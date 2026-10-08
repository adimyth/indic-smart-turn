import os
from dataclasses import dataclass
from typing import List, Dict, Union

import numpy as np
import onnx
import torch
import wandb
from onnxruntime.quantization import quantize_static, CalibrationDataReader, QuantType, quant_pre_process, \
    QuantFormat, CalibrationMethod
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from torch import nn
from torch.nn.functional import softmax
from torch.utils.data import Dataset
from transformers import WhisperFeatureExtractor, WhisperPreTrainedModel, WhisperConfig
# noinspection PyProtectedMember
from transformers.models.whisper.modeling_whisper import WhisperEncoder
# noinspection PyProtectedMember
from transformers.trainer import Trainer
from transformers.trainer_callback import TrainerCallback
from transformers.trainer_utils import IntervalStrategy
from transformers.training_args import TrainingArguments

from audio_utils import truncate_audio_to_last_n_seconds
from benchmark import benchmark
from datasets import load_dataset, concatenate_datasets, load_from_disk
from logger import log, log_model_structure, log_dataset_statistics, log_dependencies, log_device_info, ProgressLoggerCallback

DATA_ROOT = os.environ.get("INDIC_TURN_DATA", "./data")
INDIC_LANGS = ["hin", "mar", "tam", "kan", "mal", "guj", "pan", "tel", "asm", "ori", "ben"]
V32_LANGS = ["eng", "hin", "mar", "ben"]

CONFIG = {
    "base_model_name": os.environ.get("BASE_MODEL", "openai/whisper-base"),

    # local parquet files produced by indic_turn.build (have a `split` column)
    "indic_parquets": [f"{DATA_ROOT}/built/{l}.parquet" for l in INDIC_LANGS],
    # upstream data, filtered to V32_LANGS; english capped to keep the mix Indic-heavy
    "v32_train": "pipecat-ai/smart-turn-data-v3.2-train",
    "v32_test": "pipecat-ai/smart-turn-data-v3.2-test",
    "v32_eng_cap": int(os.environ.get("V32_ENG_CAP", "40000")),
    "tamil_eot": "santhosh-005/tamil-eot",
    "indic_repeat": int(os.environ.get("INDIC_REPEAT", "2")),  # oversample real Indic data

    "learning_rate": float(os.environ.get("LR", "5e-5")),
    "num_epochs": float(os.environ.get("EPOCHS", "4")),
    "train_batch_size": int(os.environ.get("BATCH", "128")),
    "eval_batch_size": 128,
    "warmup_ratio": 0.2,
    "weight_decay": 0.01,

    "eval_steps": int(os.environ.get("EVAL_STEPS", "1000")),
    "save_steps": int(os.environ.get("EVAL_STEPS", "1000")),
    "logging_steps": 100,

    "onnx_opset_version": 18,
    "calibration_dataset_size": 1024,
}


def ensure_torchcodec_available():
    """
    HF `datasets` audio decoding for this project requires `torchcodec` at runtime.
    Fail fast with a helpful error message if it's missing.
    """
    try:
        import torchcodec  # type: ignore  # noqa: F401
    except Exception as e:
        raise RuntimeError("Missing required dependency 'torchcodec'") from e


class SmartTurnV3Model(WhisperPreTrainedModel):
    def __init__(self, config: WhisperConfig):
        super().__init__(config)

        config.max_source_positions = 400
        self.encoder = WhisperEncoder(config)

        # Use the encoder's hidden size
        hidden_size = config.d_model

        self.pool_attention = nn.Sequential(
            nn.Linear(hidden_size, 256),
            nn.Tanh(),
            nn.Linear(256, 1)
        )

        self.classifier = nn.Sequential(
            nn.Linear(hidden_size, 256),
            nn.LayerNorm(256),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(256, 64),
            nn.GELU(),
            nn.Linear(64, 1)
        )

        # Initialize classifier weights
        for module in self.classifier:
            if isinstance(module, nn.Linear):
                module.weight.data.normal_(mean=0.0, std=0.1)
                if module.bias is not None:
                    module.bias.data.zero_()

        # Initialize attention pooling weights
        for module in self.pool_attention:
            if isinstance(module, nn.Linear):
                module.weight.data.normal_(mean=0.0, std=0.1)
                if module.bias is not None:
                    module.bias.data.zero_()

    def forward(self, input_features, labels=None):
        """
        Forward pass using Whisper encoder only

        Args:
            input_features: Log-mel spectrogram features [batch_size, n_mels, n_frames] - now (batch_size, 80, 800)
            labels: Binary labels for endpointing (1 = complete, 0 = incomplete)
        """
        # Use only the encoder part of Whisper
        encoder_outputs = self.encoder(input_features=input_features)

        hidden_states = encoder_outputs.last_hidden_state

        attention_weights = self.pool_attention(hidden_states)
        attention_weights = softmax(attention_weights, dim=1)
        pooled = torch.sum(hidden_states * attention_weights, dim=1)

        logits = self.classifier(pooled)

        if labels is not None:
            # Calculate positive sample weight based on batch statistics
            pos_weight = ((labels == 0).sum() / (labels == 1).sum()).clamp(min=0.1, max=10.0)
            loss_fct = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
            labels = labels.float()
            loss = loss_fct(logits.view(-1), labels.view(-1))

            probs = torch.sigmoid(logits.detach())
            return {"loss": loss, "logits": probs}

        probs = torch.sigmoid(logits)
        return {"logits": probs}


class CalibrationDataset:
    """Calibration dataset for ONNX quantization with stratified sampling (early-stop)."""

    def __init__(self, dataset, feature_extractor, max_samples):

        log.info("Building calibration dataset...")

        self.feature_extractor = feature_extractor

        ds = dataset.dataset.shuffle(seed=42)
        n = min(max_samples, len(ds))
        subset = ds.select(range(n))
        self.dataset = subset

        label_view = subset.select_columns(["endpoint_bool"])
        labels = label_view["endpoint_bool"]
        pos = sum(1 for v in labels if v)
        neg = len(labels) - pos

        log.info(f"Calibration dataset: {n} samples (positives={pos}, negatives={neg})")

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        sample = self.dataset[idx]

        audio_array = sample["audio"]["array"]
        audio_array = truncate_audio_to_last_n_seconds(audio_array, n_seconds=8)

        inputs = self.feature_extractor(
            audio_array,
            sampling_rate=16000,
            return_tensors="pt",
            padding="max_length",
            max_length=8 * 16000,
            truncation=True,
            do_normalize=True,
        )
        return inputs.input_features.squeeze(0).numpy()


class ONNXCalibrationDataReader(CalibrationDataReader):
    def __init__(self, calibration_dataset):
        self.calibration_dataset = calibration_dataset
        self.iterator = iter(range(len(calibration_dataset)))

    def get_next(self):
        try:
            idx = next(self.iterator)
            input_data = self.calibration_dataset[idx]  # shape (80, 800)
            input_data = np.expand_dims(input_data, axis=0)  # shape (1, 80, 800)
            input_data = input_data.astype(np.float32, copy=False)
            return {"input_features": input_data}
        except StopIteration:
            return None


def export_to_onnx_fp32(model, output_path, config):
    """Export model to ONNX FP32 format"""
    try:
        log.info("Exporting model to ONNX FP32...")

        class ONNXExportWrapper(torch.nn.Module):
            def __init__(self, inner):
                super().__init__()
                self.inner = inner

            def forward(self, input_features):
                out = self.inner(input_features)
                logits = out["logits"] if isinstance(out, dict) else out
                # Output (batch_size, 1) shape (2D) - standard format for single-output models
                batch_size = logits.shape[0]
                return logits.reshape(batch_size, 1)

        export_model = ONNXExportWrapper(model).eval().cpu()

        example_input_b1 = torch.randn(1, 80, 800)
        example_input_b2 = torch.randn(2, 80, 800)

        # Test with both batch size 1 and 2 to ensure consistent output shapes
        with torch.no_grad():
            test_output_1 = export_model(example_input_b1)
            test_output_2 = export_model(example_input_b2)
            assert test_output_1.shape == (1, 1), f"Expected (1, 1), got {test_output_1.shape}"
            assert test_output_2.shape == (2, 1), f"Expected (2, 1), got {test_output_2.shape}"

        dynamic_axes = {
            "input_features": {0: "batch_size"},
            "logits": {0: "batch_size"},
        }

        torch.onnx.export(
            model=export_model,
            args=(example_input_b2,),
            f=output_path,
            export_params=True,
            opset_version=config["onnx_opset_version"],
            do_constant_folding=False,
            input_names=['input_features'],
            output_names=['logits'],
            dynamic_axes=dynamic_axes,
            dynamo=False,
            verbose=False,
            external_data=False,
        )

        onnx_model = onnx.load(output_path)
        onnx.checker.check_model(onnx_model)
        log.info(f"FP32 ONNX model saved to {output_path}")

        # Verify the exported model works with batch sizes 1 and 2 and outputs consistent shapes
        import onnxruntime as ort
        session = ort.InferenceSession(output_path)

        example_input_1_np = example_input_b1.numpy().astype(np.float32)
        outputs_1 = session.run(None, {'input_features': example_input_1_np})
        assert outputs_1[0].shape == (1, 1), f"Expected (1, 1), got {outputs_1[0].shape}"

        example_input_2_np = example_input_b2.numpy().astype(np.float32)
        outputs_2 = session.run(None, {'input_features': example_input_2_np})
        assert outputs_2[0].shape == (2, 1), f"Expected (2, 1), got {outputs_2[0].shape}"

        log.info("ONNX model verification successful - consistent output shapes for both batch sizes")

        return output_path

    except Exception:
        log.exception("Failed to export to ONNX")
        return None


def quantize_onnx_model(
        onnx_fp32_path: str,
        training_dataset,
        feature_extractor,
        exports_path,
        calibration_dataset_size: int):
    """Quantize ONNX model using static quantization"""

    log.info("Invoking quant_pre_process...")

    pre_path = os.path.join(exports_path, "model_pre.onnx")
    quant_pre_process(
        onnx_fp32_path,
        pre_path,
        skip_optimization=False,  # let it fold/clean
        skip_symbolic_shape=True,
        verbose=1
    )

    log.info(f"Invoking quantize_static for calibration dataset size: {calibration_dataset_size} ...")

    output_path = os.path.join(exports_path, f"model_int8_static_calib{calibration_dataset_size}.onnx")

    log.info("Building calibration dataset...")

    calibration_dataset = CalibrationDataset(
        training_dataset,
        feature_extractor,
        max_samples=calibration_dataset_size,
    )

    log.info("Invoking quantize_static...")

    quantize_static(
        model_input=pre_path,
        model_output=output_path,
        calibration_data_reader=ONNXCalibrationDataReader(calibration_dataset),
        quant_format=QuantFormat.QDQ,
        activation_type=QuantType.QUInt8,
        weight_type=QuantType.QInt8,
        per_channel=True,
        calibrate_method=CalibrationMethod.Entropy,
        op_types_to_quantize=["Conv", "MatMul", "Gemm"],
    )

    log.info(f"Quantized ONNX models saved to {output_path}")

    return output_path


def load_dataset_at(path: str):
    if path.startswith('/'):
        return load_from_disk(path)["train"]
    else:
        return load_dataset(path)["train"]


class OnDemandSmartTurnDataset(Dataset):
    def __init__(self, hf_dataset, feature_extractor):
        self.dataset = hf_dataset
        self.feature_extractor = feature_extractor

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        sample = self.dataset[idx]

        audio_array = sample["audio"]["array"]

        audio_array = truncate_audio_to_last_n_seconds(audio_array, n_seconds=8)

        label = 1 if sample["endpoint_bool"] else 0

        inputs = self.feature_extractor(
            audio_array,
            sampling_rate=16000,
            return_tensors="pt",
            padding="max_length",
            max_length=8 * 16000,
            truncation=True,
            do_normalize=True,
        )

        return {
            "input_features": inputs.input_features.squeeze(0),
            "labels": torch.tensor(label, dtype=torch.long),
            "language": sample.get("language", "eng"),
            "dataset": sample.get("dataset", "unknown"),
            "midfiller": sample.get("midfiller", None),
            "endfiller": sample.get("endfiller", None),
        }


@dataclass
class SmartTurnDataCollator:
    def __call__(self, features: List[Dict[str, Union[torch.Tensor, str, None]]]) -> Dict[str, torch.Tensor]:
        input_features = torch.stack([f["input_features"] for f in features])
        labels = torch.stack([f["labels"] for f in features])

        batch = {
            "input_features": input_features,
            "labels": labels,
        }

        if "language" in features[0]:
            batch["language"] = [f["language"] for f in features]
        if "midfiller" in features[0]:
            batch["midfiller"] = [f["midfiller"] for f in features]
        if "endfiller" in features[0]:
            batch["endfiller"] = [f["endfiller"] for f in features]

        return batch


AUDIO_COLS = ["audio", "endpoint_bool", "language", "dataset", "midfiller", "endfiller"]

def _std(ds):
    """Keep the common columns, cast audio to 16 kHz."""
    from datasets import Audio
    keep = [c for c in AUDIO_COLS if c in ds.column_names]
    ds = ds.select_columns(keep)
    return ds.cast_column("audio", Audio(sampling_rate=16000))

def load_indic(config):
    from datasets import load_dataset
    train, dev, test = [], [], {}
    for p in config["indic_parquets"]:
        if not os.path.exists(p):
            log.warning(f"missing {p}, skipping"); continue
        ds = load_dataset("parquet", data_files=p)["train"]
        lang = ds[0]["language"]
        for name, sub in [("train", train), ("dev", dev)]:
            part = ds.filter(lambda r, n=name: r["split"] == n, num_proc=4)
            sub.append(_std(part))
        test[f"indic_{lang}"] = _std(ds.filter(lambda r: r["split"] == "test", num_proc=4))
        log.info(f"indic {lang}: train={len(train[-1])} dev={len(dev[-1])} test={len(test[f'indic_{lang}'])}")
    return train, dev, test

def load_tamil_eot(config):
    from datasets import load_dataset
    d = load_dataset(config["tamil_eot"])
    return _std(d["train"]), _std(d["dev"]), _std(d["test"])

def load_v32(config):
    from datasets import load_dataset
    tr = load_dataset(config["v32_train"])["train"]
    tr = tr.filter(lambda language: language in V32_LANGS, input_columns="language", num_proc=8)
    eng = tr.filter(lambda language: language == "eng", input_columns="language", num_proc=8).shuffle(seed=42)
    eng = eng.select(range(min(config["v32_eng_cap"], len(eng))))
    rest = tr.filter(lambda language: language != "eng", input_columns="language", num_proc=8)
    te = load_dataset(config["v32_test"])["train"].filter(lambda language: language in V32_LANGS, input_columns="language", num_proc=8)
    te = te.shuffle(seed=42).select(range(min(3000, len(te))))
    log.info(f"v3.2: eng={len(eng)} hin/mar={len(rest)} test={len(te)}")
    return _std(concatenate_datasets([eng, rest])), _std(te)

def prepare_datasets_ondemand(feature_extractor, config):
    log.info("Preparing datasets...")
    ensure_torchcodec_available()

    ind_train, ind_dev, test_splits = load_indic(config)
    ta_train, ta_dev, ta_test = load_tamil_eot(config)
    test_splits["tamil_eot"] = ta_test
    v32_train, v32_test = load_v32(config)
    test_splits["v32_eng_hin_mar"] = v32_test

    indic_all = concatenate_datasets(ind_train + [ta_train])
    v32_split = v32_train.train_test_split(test_size=0.05, seed=42)
    training = concatenate_datasets([indic_all] * config["indic_repeat"] + [v32_split["train"]]).shuffle(seed=42)
    evaluation = concatenate_datasets(ind_dev + [ta_dev, v32_split["test"].select(range(min(3000, len(v32_split["test"]))))])
    log.info(f"training={len(training)} (indic {len(indic_all)} x{config['indic_repeat']}, v3.2 {len(v32_split['train'])}); eval={len(evaluation)}")

    wrapped_test_splits = {name: OnDemandSmartTurnDataset(ds, feature_extractor) for name, ds in test_splits.items()}
    merged_test = concatenate_datasets(list(test_splits.values()))
    return {
        "training": OnDemandSmartTurnDataset(training, feature_extractor),
        "eval": OnDemandSmartTurnDataset(evaluation, feature_extractor),
        "test": wrapped_test_splits,
        "test_merged": OnDemandSmartTurnDataset(merged_test, feature_extractor),
        "raw_datasets": {"training": training, "eval": evaluation, "test": test_splits},
    }


def process_predictions(logits):
    """
    Converts raw logits into squeezed probability predictions and binary predictions.
    """
    if np.isnan(logits).any() or not np.isfinite(logits).all():
        raise ValueError("Non-finite or NaN values detected in logits during processing")

    probs = logits.squeeze()
    preds = (probs > 0.5).astype(int)

    return probs, preds


def get_predictions_and_labels(trainer, dataset, metric_key_prefix=None):
    """
    Returns tuple:
        - predictions: Raw prediction output from trainer
        - labels: Ground truth labels
        - probs: Squeezed probability predictions
        - preds: Binary predictions (probs > 0.5)
    """
    predictions = trainer.predict(dataset, metric_key_prefix=metric_key_prefix)

    probs, preds = process_predictions(predictions.predictions)
    labels = predictions.label_ids

    return predictions, labels, probs, preds


class ExternalEvaluationCallback(TrainerCallback):

    def __init__(self, test_datasets, trainer):
        super().__init__()
        self.test_datasets = test_datasets
        self.trainer = trainer

    def on_evaluate(self, args, state, control, **kwargs):
        accuracies = {}
        language_metrics = {}
        midfiller_metrics = {}

        for dataset_name, dataset in self.test_datasets.items():
            predictions, labels, probs, preds = get_predictions_and_labels(
                self.trainer, dataset, f"exttest/{dataset_name}"
            )

            metrics = compute_metrics((probs, labels))

            external_metrics = {
                f"exttest/{dataset_name}_{k}": v
                for k, v in metrics.items()
            }

            external_metrics[f"exttest/{dataset_name}_prob_dist"] = wandb.Histogram(probs)

            external_metrics[f"train/global_step"] = state.global_step

            accuracies[dataset_name] = metrics["accuracy"]

            wandb.log(external_metrics)

            self._process_category_metrics(dataset, probs, labels, preds, language_metrics,
                                           column_name='language', default_value='unknown-error')
            self._process_category_metrics(dataset, probs, labels, preds, midfiller_metrics,
                                           column_name='midfiller', default_value='unknown')

        self._log_category_metrics(language_metrics, 'lang', state.global_step)
        self._log_category_metrics(midfiller_metrics, 'midfiller', state.global_step)

        if accuracies:
            lowest_accuracy = min(accuracies.values())
            lowest_accuracy_dataset = min(accuracies.keys(), key=lambda k: accuracies[k])

            accuracy_values = list(accuracies.values())
            mean_accuracy = sum(accuracy_values) / len(accuracy_values)

            wandb.log({
                "exttest/lowest_accuracy": lowest_accuracy,
                "exttest/lowest_accuracy_dataset": lowest_accuracy_dataset,
                "exttest/mean_accuracy": mean_accuracy,
                "exttest/accuracy_variance": np.var(accuracy_values),
                "train/global_step": state.global_step
            })

            log.info(f"Overall accuracy metrics:")
            log.info(f"  Lowest accuracy across all test datasets: {lowest_accuracy:.4f} ({lowest_accuracy_dataset})")
            log.info(f"  Mean accuracy: {mean_accuracy:.4f}")
            log.info(f"  Accuracy variance: {np.var(accuracy_values):.4f}")

    def _process_category_metrics(self, dataset, probs, labels, preds, category_metrics,
                                  column_name, default_value):
        if hasattr(dataset, 'dataset'):
            underlying_dataset = dataset.dataset
        else:
            underlying_dataset = dataset

        if hasattr(underlying_dataset, 'column_names') and column_name in underlying_dataset.column_names:
            categories = underlying_dataset[column_name]
        else:
            categories = [default_value] * len(dataset)

        for i, category in enumerate(categories):
            category_key = str(category).lower() if category is not None else default_value

            if category_key not in category_metrics:
                category_metrics[category_key] = {
                    'probs': [],
                    'labels': [],
                    'preds': []
                }

            category_metrics[category_key]['probs'].append(probs[i])
            category_metrics[category_key]['labels'].append(labels[i])
            category_metrics[category_key]['preds'].append(preds[i])

    def _log_category_metrics(self, category_metrics, metric_prefix, global_step):
        category_accuracies = {}

        for category, data in category_metrics.items():
            if len(data['labels']) == 0:
                continue

            cat_probs = np.array(data['probs'])
            cat_labels = np.array(data['labels'])

            metrics = compute_metrics((cat_probs, cat_labels))

            category_specific_metrics = {
                f"exttest/{metric_prefix}_{category}_{k}": v
                for k, v in metrics.items()
            }

            category_specific_metrics[f"exttest/{metric_prefix}_{category}_prob_dist"] = wandb.Histogram(cat_probs)
            category_specific_metrics[f"exttest/{metric_prefix}_{category}_sample_count"] = len(cat_labels)
            category_specific_metrics["train/global_step"] = global_step

            category_accuracies[category] = metrics["accuracy"]

            wandb.log(category_specific_metrics)

            log.info(f"{metric_prefix.capitalize()} {category} metrics: accuracy={metrics['accuracy']:.4f}, "
                     f"precision={metrics['precision']:.4f}, recall={metrics['recall']:.4f}, "
                     f"f1={metrics['f1']:.4f}, samples={len(cat_labels)}")

        if category_accuracies:
            min_accuracy = min(category_accuracies.values())
            max_accuracy = max(category_accuracies.values())
            mean_accuracy = sum(category_accuracies.values()) / len(category_accuracies)

            best_category = max(category_accuracies.keys(), key=lambda k: category_accuracies[k])
            worst_category = min(category_accuracies.keys(), key=lambda k: category_accuracies[k])

            summary_metrics = {
                f"exttest/{metric_prefix}_min_accuracy": min_accuracy,
                f"exttest/{metric_prefix}_max_accuracy": max_accuracy,
                f"exttest/{metric_prefix}_mean_accuracy": mean_accuracy,
                f"exttest/{metric_prefix}_accuracy_range": max_accuracy - min_accuracy,
                f"exttest/best_performing_{metric_prefix}": best_category,
                f"exttest/worst_performing_{metric_prefix}": worst_category,
                f"exttest/{metric_prefix}_categories_evaluated": len(category_accuracies),
                "train/global_step": global_step
            }

            if len(category_accuracies) > 1:
                summary_metrics[f"exttest/{metric_prefix}_accuracy_std"] = np.std(list(category_accuracies.values()))

            wandb.log(summary_metrics)

            category_type = metric_prefix.replace('_', ' ')
            log.info(f"{category_type.capitalize()} performance summary:")
            log.info(f"  Best performing {category_type}: {best_category} ({category_accuracies[best_category]:.4f})")
            log.info(
                f"  Worst performing {category_type}: {worst_category} ({category_accuracies[worst_category]:.4f})")
            log.info(f"  Mean accuracy across {category_type}s: {mean_accuracy:.4f}")
            log.info(f"  Accuracy range: {max_accuracy - min_accuracy:.4f}")

        if category_metrics:
            total_samples = sum(len(data['labels']) for data in category_metrics.values())
            distribution_metrics = {
                f"exttest/{metric_prefix}_{category}_percentage": (len(
                    category_metrics[category]['labels']) / total_samples) * 100
                for category in category_metrics.keys()
            }
            distribution_metrics["train/global_step"] = global_step
            wandb.log(distribution_metrics)


def compute_metrics(eval_pred):
    logits, labels = eval_pred

    probs, preds = process_predictions(logits)

    tn, fp, fn, tp = confusion_matrix(labels, preds).ravel()

    return {
        "accuracy": accuracy_score(labels, preds),
        "precision": precision_score(labels, preds, zero_division="warn"),
        "recall": recall_score(labels, preds, zero_division="warn"),
        "f1": f1_score(labels, preds, zero_division="warn"),
        "pred_positives": tp + fp,
        "pred_negatives": tn + fn,
        "true_positives": tp,
        "false_positives": fp,
        "true_negatives": tn,
        "false_negatives": fn,
    }


def final_evaluate(trainer, dataset, split_name):
    log.info(f"Evaluating on {split_name} set...")
    metrics = trainer.evaluate(eval_dataset=dataset)

    predictions, labels, probs, preds = get_predictions_and_labels(trainer, dataset)

    wandb_metrics = {
        f"final/{split_name}_accuracy": metrics["eval_accuracy"],
        f"final/{split_name}_precision": metrics["eval_precision"],
        f"final/{split_name}_recall": metrics["eval_recall"],
        f"final/{split_name}_f1": metrics["eval_f1"],
    }

    wandb.log(wandb_metrics)

    return metrics, predictions


def do_training_run(run_name: str, output_dir: str = "./output"):
    log_dependencies()
    log_device_info()

    log.info(f"Starting training run: {run_name}")
    log.info(f"Output directory: {output_dir}")

    wandb_run = wandb.init(
        project="indic-smart-turn",
        name=run_name,
        config=CONFIG,
        mode="online" if os.environ.get("WANDB_API_KEY") else "disabled",
    )

    wandb_run.define_metric(name="exttest/*", step_metric="train/global_step")

    model = SmartTurnV3Model.from_pretrained(CONFIG["base_model_name"], num_labels=1, ignore_mismatched_sizes=True)
    feature_extractor = WhisperFeatureExtractor(chunk_length=8) # 8 seconds

    log_model_structure(model, CONFIG)

    datasets = prepare_datasets_ondemand(feature_extractor, CONFIG)

    training_args = TrainingArguments(
        output_dir=f"{output_dir}/{run_name}",
        per_device_train_batch_size=CONFIG["train_batch_size"],
        per_device_eval_batch_size=CONFIG["eval_batch_size"],
        num_train_epochs=CONFIG["num_epochs"],
        eval_strategy=IntervalStrategy.STEPS,
        gradient_accumulation_steps=1,
        eval_steps=CONFIG["eval_steps"],
        save_steps=CONFIG["save_steps"],
        logging_steps=CONFIG["logging_steps"],
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        learning_rate=CONFIG["learning_rate"],
        warmup_ratio=CONFIG["warmup_ratio"],
        weight_decay=CONFIG["weight_decay"],
        lr_scheduler_type="cosine",
        report_to=["wandb"] if os.environ.get("WANDB_API_KEY") else [],
        bf16=torch.cuda.is_available(),
        save_total_limit=2,
        dataloader_num_workers=int(os.environ.get("NUM_WORKERS", "8")),
        dataloader_prefetch_factor=4,
        dataloader_pin_memory=True,
        tf32=False,
        disable_tqdm=True,
    )

    os.makedirs(training_args.output_dir, exist_ok=True)

    log_dataset_statistics("training", datasets["training"])
    log_dataset_statistics("eval", datasets["eval"])

    for dataset_name, dataset in datasets["test"].items():
        log_dataset_statistics("test_" + dataset_name, dataset)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=datasets["training"],
        eval_dataset=datasets["eval"],
        compute_metrics=compute_metrics,
        data_collator=SmartTurnDataCollator(),
        callbacks=[
            ProgressLoggerCallback(log_interval=CONFIG["logging_steps"])
        ]
    )

    trainer.add_callback(ExternalEvaluationCallback(
        test_datasets=datasets["test"],
        trainer=trainer
    ))

    log.info("Starting training...")
    trainer.train()

    final_save_path = f"{trainer.args.output_dir}/final_model"
    os.makedirs(final_save_path, exist_ok=True)

    feature_extractor.save_pretrained(final_save_path)
    trainer.save_model(final_save_path)

    export_path = os.path.join(final_save_path, "exports")
    os.makedirs(export_path, exist_ok=True)

    onnx_fp32_path = os.path.join(export_path, "model_fp32.onnx")

    trainer.model.eval().cpu()

    onnx_fp32_model_path = export_to_onnx_fp32(trainer.model, onnx_fp32_path, CONFIG)

    log.info(f"Training and export completed. Models saved to: {final_save_path}")

    wandb.finish()

    return onnx_fp32_model_path


def do_quantization_run(fp32_model_path: str):
    calibration_dataset_size = CONFIG["calibration_dataset_size"]

    log.info(f"Starting quantization run on {fp32_model_path} (calib dataset size {calibration_dataset_size})")

    feature_extractor = WhisperFeatureExtractor(chunk_length=8)  # 8 seconds

    datasets = prepare_datasets_ondemand(feature_extractor, CONFIG)

    parent_dir = os.path.dirname(fp32_model_path)

    quantized_onnx_path = quantize_onnx_model(
        onnx_fp32_path=fp32_model_path,
        training_dataset=datasets["training"],
        feature_extractor=feature_extractor,
        exports_path=parent_dir,
        calibration_dataset_size=calibration_dataset_size
    )

    return quantized_onnx_path


def do_benchmark_run(model_paths: List[str]):
    log.info(f"Benchmarking models: {model_paths}")

    feature_extractor = WhisperFeatureExtractor(chunk_length=8)  # 8 seconds

    dataset = prepare_datasets_ondemand(feature_extractor, CONFIG)["test_merged"]

    for model_path in model_paths:
        model_name = os.path.basename(model_path).replace(".onnx", "")
        benchmark_path = os.path.join(os.path.dirname(model_path), "benchmarks")
        os.makedirs(benchmark_path, exist_ok=True)

        benchmark(
            onnx_path=model_path,
            run_description=model_name,
            dataset=dataset,
            limit=None,
            markdown_output=f"{benchmark_path}/{model_name}.md",
            batch_size=256
        )
