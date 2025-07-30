# tests/test_secrets.py
import os
import pytest
from openmailer.secrets import get_secret

def test_get_secret_from_env(monkeypatch):
    monkeypatch.setenv("MY_SECRET", "env-value")
    assert get_secret("MY_SECRET") == "env-value"

def test_get_secret_with_default(monkeypatch):
    monkeypatch.delenv("MY_MISSING_SECRET", raising=False)
    assert get_secret("MY_MISSING_SECRET", default="default-value") == "default-value"

def test_get_secret_required_raises(monkeypatch):
    monkeypatch.delenv("MUST_HAVE_SECRET", raising=False)
    with pytest.raises(ValueError) as exc:
        get_secret("MUST_HAVE_SECRET", required=True)
    assert "Missing required secret" in str(exc.value)
