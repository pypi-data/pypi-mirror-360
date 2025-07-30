import os
import pytest

@pytest.fixture(scope="session", autouse=True)
def setup_env():
    os.environ["SMTP_HOST"] = "smtp.example.com"
    os.environ["SMTP_PORT"] = "587"
    os.environ["SMTP_USERNAME"] = "test@example.com"
    os.environ["SMTP_PASSWORD"] = "dummy-password"
    os.environ["SMTP_USE_TLS"] = "true"
    os.environ["SMTP_RATE_LIMIT"] = "10"
