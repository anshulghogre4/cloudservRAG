"""B-06 groundwork / FR-14: the provider client degrades instead of crashing.

T-22  test_provider_down_raises_unavailable   timeouts/5xx/no key -> ProviderUnavailable, never a bare exception
T-23  test_rate_limit_backoff                  429 -> retry with backoff, then success
plus  cache: identical prompt is served from disk without a second call (Build Spec §07)
"""
import json

import pytest

from src.llm import LLMClient, ProviderUnavailable


class FakeTransport:
    """Scripted responses: each item is (status_code, json_body) or an Exception instance."""

    def __init__(self, script):
        self.script = list(script)
        self.calls = []

    def __call__(self, url, headers, payload, timeout):
        self.calls.append(payload)
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def ok(text):
    return (200, {"choices": [{"message": {"content": text}}]})


@pytest.fixture
def client_factory(settings, tmp_path):
    def make(script, key="k", retries=3):
        s = settings
        s.api_key = key
        s.llm_max_retries = retries
        s.llm_cache_dir = tmp_path / "cache"
        transport = FakeTransport(script)
        c = LLMClient(s, transport=transport, sleep=lambda _s: None)
        return c, transport
    return make


def test_success_returns_text(client_factory):
    c, t = client_factory([ok('{"a": 1}')])
    assert c.complete("hello") == '{"a": 1}'
    assert len(t.calls) == 1
    assert t.calls[0]["model"] == c.settings.model_name
    assert t.calls[0]["temperature"] == 0


def test_no_key_raises_unavailable(client_factory):
    c, t = client_factory([ok("x")], key=None)
    with pytest.raises(ProviderUnavailable):
        c.complete("hello")
    assert t.calls == []  # never even tried


def test_provider_down_raises_unavailable(client_factory):
    c, t = client_factory([TimeoutError("t"), (503, {}), ConnectionError("down")], retries=3)
    with pytest.raises(ProviderUnavailable) as e:
        c.complete("hello")
    assert len(t.calls) == 3
    assert "unavailable" in str(e.value).lower()


def test_rate_limit_backoff(client_factory):
    c, t = client_factory([(429, {}), (429, {}), ok("fine")], retries=3)
    assert c.complete("hello") == "fine"
    assert len(t.calls) == 3


def test_auth_error_does_not_retry(client_factory):
    c, t = client_factory([(401, {"error": "bad key"})], retries=3)
    with pytest.raises(ProviderUnavailable):
        c.complete("hello")
    assert len(t.calls) == 1


def test_cache_hit_skips_call(client_factory):
    c, t = client_factory([ok("cached answer")])
    assert c.complete("same prompt") == "cached answer"
    assert c.complete("same prompt") == "cached answer"
    assert len(t.calls) == 1
    assert any(p.suffix == ".json" for p in c.settings.llm_cache_dir.rglob("*"))


def test_cache_is_per_model_and_prompt(client_factory):
    c, t = client_factory([ok("one"), ok("two")])
    assert c.complete("p1") == "one"
    assert c.complete("p2") == "two"
    assert len(t.calls) == 2
