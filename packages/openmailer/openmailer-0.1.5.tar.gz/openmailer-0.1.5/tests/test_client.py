import os
import pytest
from openmailer.client import OpenMailerClient

DUMMY_EMAIL = "test@example.com"
DUMMY_SUBJECT = "Unit Test Email"
DUMMY_TEMPLATE = "<h1>Hello {{ name }}</h1>"
DUMMY_CONTEXT = {"name": "Tester"}
DUMMY_ATTACHMENT = "tests/test_attachment.txt"


@pytest.fixture(scope="module")
def client():
    return OpenMailerClient(dry_run=True)


def test_valid_email(client):
    result = client.send_email(
        to=DUMMY_EMAIL,
        subject=DUMMY_SUBJECT,
        html_body=DUMMY_TEMPLATE,
        context=DUMMY_CONTEXT
    )
    assert result is not None


def test_invalid_email(client):
    with pytest.raises(ValueError):
        client.send_email(
            to="invalid-email",
            subject=DUMMY_SUBJECT,
            html_body=DUMMY_TEMPLATE,
            context=DUMMY_CONTEXT
        )


def test_missing_template_var_warning(client, capsys):
    client.send_email(
        to=DUMMY_EMAIL,
        subject=DUMMY_SUBJECT,
        html_body="<h1>Hello {{ name }} {{ missing }}</h1>",
        context={"name": "Test"}
    )
    captured = capsys.readouterr()
    assert "⚠️ Warning" in captured.out


def test_attachment_validation(client):
    with open(DUMMY_ATTACHMENT, "w") as f:
        f.write("Sample attachment")

    result = client.send_email(
        to=DUMMY_EMAIL,
        subject=DUMMY_SUBJECT,
        html_body=DUMMY_TEMPLATE,
        context=DUMMY_CONTEXT,
        attachments=[DUMMY_ATTACHMENT]
    )
    assert result is not None

    os.remove(DUMMY_ATTACHMENT)


def test_bulk_send(client):
    report = client.send_bulk(
        recipients=["a@example.com", "b@example.com"],
        subject=DUMMY_SUBJECT,
        html_body=DUMMY_TEMPLATE,
        context_fn=lambda email: {"name": email.split("@")[0]}
    )
    assert report["status"] in {"success", "partial"}
    assert len(report["success"]) + len(report["failed"]) == 2


def test_feedback_to_sender(client):
    report = {
        "status": "partial",
        "success": [{"to": "a@example.com"}],
        "failed": [{"to": "b@example.com", "error": "FakeError"}]
    }
    result = client.feedback_to_sender("sender@example.com", report)
    assert result is None  # It's an internal send call


def test_queue_and_retry(client):
    client.queue.add({
        "to": DUMMY_EMAIL,
        "subject": DUMMY_SUBJECT,
        "template": DUMMY_TEMPLATE,
        "context": DUMMY_CONTEXT
    })

    client.retry_all()
    # Assert should pass if no exception


def test_health_check(client):
    status = client.get_health_status()
    assert isinstance(status, dict)


def test_analytics(client):
    metrics = client.get_analytics()
    assert isinstance(metrics, dict)
