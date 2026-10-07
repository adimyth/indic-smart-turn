#!/usr/bin/env python3
"""Fine-tune a released Indic Smart Turn checkpoint on local private-call parquet files.

The script never uploads private audio. It mixes private train samples 1:1 with public Indic and English examples, exports an fp32 ONNX model, and creates a static-int8 ONNX model unless `--skip-quantize` is selected.
"""
from __future__ import annotations

import argparse
import io
import os
import random
import sys
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "train"))
sys.path.insert(0, str(ROOT))
from indic_turn.common import SR

smart_turn_train = None


def decode_audio(audio: dict) -> np.ndarray:
    wav, rate = sf.read(io.BytesIO(audio["bytes"]), dtype="float32", always_2d=False)
    if wav.ndim > 1:
        wav = wav.mean(axis=1)
    if rate != SR:
        import librosa
        wav = librosa.resample(wav, orig_sr=rate, target_sr=SR)
    return wav.astype(np.float32)


def parquet_rows(paths: list[Path], split: str) -> list[dict]:
    rows: list[dict] = []
    for path in paths:
        data = pq.read_table(path).to_pylist()
        rows.extend(row for row in data if row.get("split") == split)
    return rows


def english_rows(size: int) -> list[dict]:
    from datasets import Audio, load_dataset
    dataset = load_dataset("pipecat-ai/smart-turn-data-v3.2-train", split="train").cast_column("audio", Audio(decode=False))
    english = dataset.filter(lambda row: row["language"] == "eng", num_proc=4).shuffle(seed=42)
    return [english[index] for index in range(min(size, len(english)))]


def public_rows(paths: list[Path], english_size: int) -> list[dict]:
    rows = parquet_rows(paths, "train")
    rows.extend(english_rows(english_size))
    if not rows:
        raise RuntimeError("No public training rows were found")
    return rows


def equal_public_mix(private: list[dict], public: list[dict], seed: int) -> list[dict]:
    if not private:
        raise RuntimeError("No private train rows were found")
    rng = random.Random(seed)
    if len(public) >= len(private):
        selected = rng.sample(public, len(private))
    else:
        selected = [public[index % len(public)] for index in range(len(private))]
        rng.shuffle(selected)
    mixed = [*private, *selected]
    rng.shuffle(mixed)
    return mixed


class BytesDataset:
    def __init__(self, rows: list[dict], feature_extractor):
        import torch
        self.rows = rows
        self.feature_extractor = feature_extractor
        self.torch = torch

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> dict:
        row = self.rows[index]
        audio = smart_turn_train.truncate_audio_to_last_n_seconds(decode_audio(row["audio"]), n_seconds=8)
        inputs = self.feature_extractor(audio, sampling_rate=SR, return_tensors="pt", padding="max_length", max_length=8 * SR, truncation=True, do_normalize=True)
        return {
            "input_features": inputs.input_features.squeeze(0),
            "labels": self.torch.tensor(int(bool(row["endpoint_bool"])), dtype=self.torch.long),
            "language": row.get("language", "eng"),
            "dataset": row.get("dataset", "unknown"),
            "midfiller": row.get("midfiller", False),
            "endfiller": row.get("endfiller", False),
        }


def quantize(fp32_path: Path, dataset: BytesDataset, output_dir: Path, size: int) -> Path:
    from onnxruntime.quantization import CalibrationDataReader, CalibrationMethod, QuantFormat, QuantType, quant_pre_process, quantize_static

    class Reader(CalibrationDataReader):
        def __init__(self):
            self.index = 0

        def get_next(self):
            if self.index >= min(size, len(dataset)):
                return None
            features = dataset[self.index]["input_features"].numpy()[None, :].astype(np.float32, copy=False)
            self.index += 1
            return {"input_features": features}

    prepared = output_dir / "model_pre.onnx"
    destination = output_dir / f"model_int8_static_calib{min(size, len(dataset))}.onnx"
    quant_pre_process(str(fp32_path), str(prepared), skip_optimization=False, skip_symbolic_shape=True)
    quantize_static(str(prepared), str(destination), Reader(), quant_format=QuantFormat.QDQ, activation_type=QuantType.QUInt8, weight_type=QuantType.QInt8, per_channel=True, calibrate_method=CalibrationMethod.Entropy, op_types_to_quantize=["Conv", "MatMul", "Gemm"])
    return destination


def main() -> None:
    global smart_turn_train
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--checkpoint", required=True, type=Path, help="Stage 5 output/<run>/final_model checkpoint")
    ap.add_argument("--private-dir", type=Path, default=ROOT / "data" / "private")
    ap.add_argument("--public-glob", default=str(ROOT / "data" / "built" / "*.parquet"))
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--english-size", type=int, default=5_000)
    ap.add_argument("--epochs", type=float, default=1.0)
    ap.add_argument("--learning-rate", type=float, default=1e-5)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--calibration-size", type=int, default=1_024)
    ap.add_argument("--skip-quantize", action="store_true")
    args = ap.parse_args()
    try:
        import train as smart_turn_train_module
    except ImportError as exc:
        raise SystemExit("Local fine-tuning needs the project's [train] dependencies; install them with `uv sync --extra train`") from exc
    smart_turn_train = smart_turn_train_module
    if not args.checkpoint.is_dir():
        raise SystemExit(f"Missing Stage 5 checkpoint: {args.checkpoint}")
    private_paths = sorted(args.private_dir.glob("*.parquet"))
    public_paths = sorted(Path().glob(args.public_glob)) if not Path(args.public_glob).is_absolute() else sorted(Path(args.public_glob).parent.glob(Path(args.public_glob).name))
    private_train = parquet_rows(private_paths, "train")
    private_test = parquet_rows(private_paths, "test")
    if not private_test:
        raise SystemExit("No private test rows were found; extraction must produce a 70/30 call-disjoint split")
    public = public_rows(public_paths, args.english_size)
    training_rows = equal_public_mix(private_train, public, args.seed)
    from transformers import Trainer, TrainingArguments, WhisperFeatureExtractor
    feature_extractor = WhisperFeatureExtractor.from_pretrained(args.checkpoint)
    model = smart_turn_train.SmartTurnV3Model.from_pretrained(args.checkpoint, num_labels=1, ignore_mismatched_sizes=False)
    train_dataset = BytesDataset(training_rows, feature_extractor)
    test_dataset = BytesDataset(private_test, feature_extractor)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    training_args = TrainingArguments(
        output_dir=str(args.output_dir), per_device_train_batch_size=args.batch_size, per_device_eval_batch_size=args.batch_size,
        num_train_epochs=args.epochs, learning_rate=args.learning_rate, warmup_ratio=0.2, weight_decay=0.01,
        lr_scheduler_type="cosine", eval_strategy="epoch", save_strategy="epoch", load_best_model_at_end=True,
        metric_for_best_model="f1", greater_is_better=True, report_to=[], bf16=__import__("torch").cuda.is_available(),
        dataloader_num_workers=0, dataloader_pin_memory=False,
    )
    trainer = Trainer(model=model, args=training_args, train_dataset=train_dataset, eval_dataset=test_dataset, compute_metrics=smart_turn_train.compute_metrics, data_collator=smart_turn_train.SmartTurnDataCollator())
    trainer.train()
    final_model = args.output_dir / "final_model"
    final_model.mkdir(exist_ok=True)
    trainer.save_model(final_model)
    feature_extractor.save_pretrained(final_model)
    exports = final_model / "exports"
    exports.mkdir(exist_ok=True)
    fp32 = exports / "model_fp32.onnx"
    trainer.model.eval().cpu()
    if not smart_turn_train.export_to_onnx_fp32(trainer.model, str(fp32), smart_turn_train.CONFIG):
        raise SystemExit("FP32 ONNX export failed")
    print(f"private train={len(private_train)} test={len(private_test)} public={len(public)} mixed train={len(training_rows)}")
    print(f"fp32 ONNX: {fp32}")
    if not args.skip_quantize:
        int8 = quantize(fp32, train_dataset, exports, args.calibration_size)
        print(f"int8 ONNX: {int8}")


if __name__ == "__main__":
    main()
