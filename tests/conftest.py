"""Shared fixtures. No network, no API key: every test must pass in CI (A12)."""
import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "Docs" / "Capstone_Project" / "05_Datasets"


@pytest.fixture(scope="session")
def sample_tickets():
    """One real development ticket per channel: email, chat, docs_comment, forum."""
    return json.loads((FIXTURES / "sample_tickets.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def edge_tickets():
    """Synthetic malformed tickets: empty body, missing fields, odd characters, unknown channel."""
    return json.loads((FIXTURES / "edge_tickets.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def documentation():
    return json.loads((DATASETS / "documentation.json").read_text(encoding="utf-8"))


@pytest.fixture
def settings(monkeypatch):
    """Settings with no .env and no key, so nothing can reach the network."""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    from src.config import load_settings
    return load_settings(env_file=None)
