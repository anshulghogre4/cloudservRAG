"""Settings loaded from the environment (B-01).

Every behavioural number the system uses (thresholds, top-k, kill switch) is read
here and nowhere else, so nothing is hard-coded and the kill switch needs no deploy.
The API key is held but excluded from repr() so it can never reach a log.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]

_TRUE = {"1", "true", "yes", "on"}


def _bool(value: Optional[str], default: bool) -> bool:
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in _TRUE


def _float(value: Optional[str], default: float) -> float:
    try:
        return float(value) if value not in (None, "") else default
    except ValueError:
        return default


def _int(value: Optional[str], default: int) -> int:
    try:
        return int(value) if value not in (None, "") else default
    except ValueError:
        return default


@dataclass
class Settings:
    api_key: Optional[str] = field(default=None, repr=False)
    base_url: str = "https://openrouter.ai/api/v1"
    model_name: str = "meta-llama/llama-3.1-8b-instruct"
    embedding_model: str = "all-MiniLM-L6-v2"
    chroma_path: Path = ROOT / "storage" / "chroma"
    database_url: str = f"sqlite:///{(ROOT / 'storage' / 'decisions.db').as_posix()}"
    log_level: str = "INFO"
    confidence_threshold: float = 0.80   # illustrative until derived from dev data (FR-05)
    retrieval_threshold: float = 0.40    # cosine floor, derived from dev data 16 Sep 2026: keeps 97.8% answerable, cuts 100% unclear_request (FR-04)
    retrieval_top_k: int = 5
    llm_timeout_seconds: float = 30.0
    llm_max_retries: int = 3
    llm_cache_dir: Path = ROOT / "storage" / "llm_cache"
    kill_switch: bool = False            # True forces every ticket to escalate (Governance §5)
    # Both optional routing rules were measured on the development set (evaluation/route_check.py,
    # 16 Sep 2026) and lowered routing accuracy, so both are off; they stay available for the report.
    answerable_floor: float = 0.0        # escalate when neighbours say P(answerable from docs) is below this; 0 disables
    plan_rule: bool = False              # escalate when the cited article's plan excludes the customer's tier
    metrics_port: int = 8001

    @property
    def sqlite_path(self) -> Path:
        prefix = "sqlite:///"
        if self.database_url.startswith(prefix):
            return Path(self.database_url[len(prefix):])
        raise ValueError("Only sqlite:/// DATABASE_URL values are supported")


def load_settings(env_file: Optional[str | os.PathLike] = ".env") -> Settings:
    """Load settings. env_file=None skips .env entirely (used by tests and CI)."""
    if env_file is not None:
        path = Path(env_file)
        if not path.is_absolute():
            path = ROOT / path
        if path.exists():
            load_dotenv(path, override=False)

    env = os.environ
    key = env.get("OPENROUTER_API_KEY")
    if key is not None:
        key = key.strip() or None
    defaults = Settings()
    return Settings(
        api_key=key,
        base_url=env.get("OPENROUTER_BASE_URL", defaults.base_url),
        model_name=env.get("MODEL_NAME", defaults.model_name),
        embedding_model=env.get("EMBEDDING_MODEL", defaults.embedding_model),
        chroma_path=Path(env.get("CHROMA_PATH", str(defaults.chroma_path))),
        database_url=env.get("DATABASE_URL", defaults.database_url),
        log_level=env.get("LOG_LEVEL", defaults.log_level),
        confidence_threshold=_float(env.get("CONFIDENCE_THRESHOLD"), defaults.confidence_threshold),
        retrieval_threshold=_float(env.get("RETRIEVAL_THRESHOLD"), defaults.retrieval_threshold),
        retrieval_top_k=_int(env.get("RETRIEVAL_TOP_K"), defaults.retrieval_top_k),
        llm_timeout_seconds=_float(env.get("LLM_TIMEOUT_SECONDS"), defaults.llm_timeout_seconds),
        llm_max_retries=_int(env.get("LLM_MAX_RETRIES"), defaults.llm_max_retries),
        llm_cache_dir=Path(env.get("LLM_CACHE_DIR", str(defaults.llm_cache_dir))),
        kill_switch=_bool(env.get("KILL_SWITCH"), defaults.kill_switch),
        answerable_floor=_float(env.get("ANSWERABLE_FLOOR"), defaults.answerable_floor),
        plan_rule=_bool(env.get("PLAN_RULE"), defaults.plan_rule),
        metrics_port=_int(env.get("METRICS_PORT"), defaults.metrics_port),
    )
