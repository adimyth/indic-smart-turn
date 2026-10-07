from __future__ import annotations
import os, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get("INDIC_TURN_DATA", ROOT / "data"))

# IndicVoices config name -> ISO-639-3 code used by smart-turn's `language` column
LANGS = {
    "hindi": "hin", "marathi": "mar", "tamil": "tam", "kannada": "kan",
    "malayalam": "mal", "gujarati": "guj", "punjabi": "pan", "telugu": "tel",
    "assamese": "asm", "odia": "ori", "bengali": "ben",
}
LANG_NAMES = {
    "hin": "Hindi", "mar": "Marathi", "tam": "Tamil", "kan": "Kannada", "mal": "Malayalam",
    "guj": "Gujarati", "pan": "Punjabi", "tel": "Telugu", "eng": "English",
    "asm": "Assamese", "ori": "Odia", "ben": "Bengali",
}
HF_DATASET = "ai4bharat/IndicVoices"
SR = 16000

_PATH_RE = re.compile(r"^(?P<session>[0-9a-f-]{36})_(?P<part>\d+)_chunk_(?P<chunk>\d+)\.flac$")

def parse_path(p: str):
    """'<uuid>_0_chunk_12.flac' -> (session_id, part, chunk_idx) or None."""
    m = _PATH_RE.match(p or "")
    if not m:
        return None
    return m["session"] + "_" + m["part"], int(m["part"]), int(m["chunk"])

def hf_token() -> str:
    tok = os.environ.get("HF_TOKEN")
    if not tok:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
        tok = os.environ.get("HF_TOKEN")
    if not tok:
        raise SystemExit("HF_TOKEN not set")
    return tok
