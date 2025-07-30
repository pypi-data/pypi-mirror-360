from email.message import EmailMessage
from openmailer.localmode import handle_local_send

def test_local_send_returns_mock_result():
    msg = EmailMessage()
    msg.set_content("Test content")
    msg["From"] = "test@example.com"
    msg["To"] = "receiver@example.com"
    msg["Subject"] = "Test"

    result = handle_local_send(msg, "receiver@example.com")

    assert result["status"] == "saved"
    assert "receiver@example.com" in result["file"]
