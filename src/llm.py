"""Provider client (FR-14, B-06 groundwork): one place that talks to the model.

- OpenAI-compatible chat completions over HTTP (OpenRouter by default, Groq by changing the base URL).
- Timeout, exponential backoff on 429/5xx/network errors, capped retries.
- Raises ProviderUnavailable on a missing key, an auth error, or exhausted retries; callers degrade
  (classify falls back, route escalates) instead of crashing (A11).
- Disk cache keyed by model + prompt so development runs are reproducible and cheap
  (Build Spec section 07: caching is encouraged).
- `transport` and `sleep` are injectable so tests never touch the network.
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

import requests

from src.config import Settings

log = logging.getLogger(__name__)

Transport = Callable[[str, Dict[str, str], Dict[str, Any], float], Tuple[int, Any]]


class ProviderUnavailable(RuntimeError):
    """The model provider could not be used. The system continues without it."""


def _http_transport(url: str, headers: Dict[str, str], payload: Dict[str, Any], timeout: float) -> Tuple[int, Any]:
    r = requests.post(url, headers=headers, json=payload, timeout=timeout)
    try:
        body = r.json()
    except ValueError:
        body = {"raw": r.text[:500]}
    return r.status_code, body


class LLMClient:
    RETRY_STATUSES = {408, 409, 425, 429, 500, 502, 503, 504}
    FATAL_STATUSES = {400, 401, 402, 403, 404, 422}

    def __init__(self, settings: Settings, transport: Optional[Transport] = None,
                 sleep: Callable[[float], None] = time.sleep, use_cache: bool = True):
        self.settings = settings
        self.transport = transport or _http_transport
        self.sleep = sleep
        self.use_cache = use_cache
        self.calls = 0
        self.cache_hits = 0

    # ---- cache -------------------------------------------------------------------
    def _cache_path(self, prompt: str, system: Optional[str]) -> Path:
        key = hashlib.sha256(f"{self.settings.model_name}\n{system or ''}\n{prompt}".encode("utf-8")).hexdigest()
        return Path(self.settings.llm_cache_dir) / key[:2] / f"{key}.json"

    def _cache_get(self, path: Path) -> Optional[str]:
        if not self.use_cache or not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))["content"]
        except Exception:
            return None

    def _cache_put(self, path: Path, content: str, prompt: str) -> None:
        if not self.use_cache:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"model": self.settings.model_name, "content": content,
                                    "prompt_sha": hashlib.sha256(prompt.encode("utf-8")).hexdigest()}),
                        encoding="utf-8")

    # ---- call --------------------------------------------------------------------
    def complete(self, prompt: str, system: Optional[str] = None, json_mode: bool = False,
                 max_tokens: int = 600) -> str:
        """Return the assistant text for `prompt`. Raises ProviderUnavailable when it cannot."""
        path = self._cache_path(prompt, system)
        cached = self._cache_get(path)
        if cached is not None:
            self.cache_hits += 1
            return cached

        key = self.settings.api_key
        if not key:
            raise ProviderUnavailable("provider unavailable: no API key configured")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload: Dict[str, Any] = {"model": self.settings.model_name, "messages": messages,
                                   "temperature": 0, "max_tokens": max_tokens}
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                   "HTTP-Referer": "https://github.com/cloudservrag", "X-Title": "cloudservRAG"}
        url = f"{self.settings.base_url.rstrip('/')}/chat/completions"

        attempts = max(1, int(self.settings.llm_max_retries))
        last_error = "unknown"
        for attempt in range(1, attempts + 1):
            try:
                self.calls += 1
                status, body = self.transport(url, headers, payload, self.settings.llm_timeout_seconds)
            except Exception as exc:  # timeouts, connection errors, DNS
                last_error = f"{type(exc).__name__}: {exc}"
                log.warning("provider call failed (attempt %d/%d): %s", attempt, attempts, last_error)
                self._backoff(attempt, attempts)
                continue

            if status == 200:
                try:
                    content = body["choices"][0]["message"]["content"]
                except (KeyError, IndexError, TypeError):
                    last_error = f"malformed response: {str(body)[:200]}"
                    self._backoff(attempt, attempts)
                    continue
                if content is None:
                    content = ""
                self._cache_put(path, content, prompt)
                return content

            if status in self.FATAL_STATUSES:
                raise ProviderUnavailable(f"provider unavailable: HTTP {status} {str(body)[:200]}")

            last_error = f"HTTP {status}"
            log.warning("provider returned %s (attempt %d/%d)", status, attempt, attempts)
            self._backoff(attempt, attempts)

        raise ProviderUnavailable(f"provider unavailable after {attempts} attempts: {last_error}")

    def _backoff(self, attempt: int, attempts: int) -> None:
        if attempt < attempts:
            self.sleep(min(30.0, 1.5 * (2 ** (attempt - 1))))
