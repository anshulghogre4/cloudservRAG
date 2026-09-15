"""B-01: configuration loads from .env.example defaults and never leaks the key.

T-00a  .env.example carries every variable the system reads.
T-00b  Settings load without a .env file present (CI has none) and defaults are sane.
T-00c  The API key is read from the environment, not hard-coded, and is not in repr().
"""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_VARS = [
    "OPENROUTER_API_KEY",
    "MODEL_NAME",
    "EMBEDDING_MODEL",
    "CHROMA_PATH",
    "DATABASE_URL",
    "LOG_LEVEL",
    "CONFIDENCE_THRESHOLD",
    "RETRIEVAL_TOP_K",
]


def test_env_example_lists_every_variable():
    text = (ROOT / ".env.example").read_text(encoding="utf-8")
    missing = [v for v in REQUIRED_VARS if f"{v}=" not in text]
    assert not missing, f".env.example is missing {missing}"


def test_settings_load_without_env_file(monkeypatch):
    for v in REQUIRED_VARS:
        monkeypatch.delenv(v, raising=False)
    from src.config import load_settings

    s = load_settings(env_file=None)
    assert s.model_name == "meta-llama/llama-3.1-8b-instruct"
    assert s.embedding_model == "all-MiniLM-L6-v2"
    assert 0.0 <= s.confidence_threshold <= 1.0
    assert s.retrieval_top_k >= 1
    assert s.api_key is None  # absent key is allowed; the LLM client degrades (FR-14)
    assert s.kill_switch is False  # default: auto-respond enabled


def test_settings_read_from_environment(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-123")
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "0.65")
    monkeypatch.setenv("KILL_SWITCH", "true")
    from src.config import load_settings

    s = load_settings(env_file=None)
    assert s.api_key == "test-key-123"
    assert s.confidence_threshold == pytest.approx(0.65)
    assert s.kill_switch is True
    assert "test-key-123" not in repr(s)  # never leak the key into logs
