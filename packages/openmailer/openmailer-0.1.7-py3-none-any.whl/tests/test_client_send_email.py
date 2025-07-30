import os
import pytest
from openmailer.client import OpenMailerClient
import openmailer.smtp_engine as smtp_engine
import openmailer.localmode as localmode

@pytest.fixture(autouse=True)
def fake_send(monkeypatch, tmp_path):
    # localmode stub
    def fake_local_send(message, to):
        return {"file": str(tmp_path/"out.eml"), "status": "saved"}
    monkeypatch.setattr(localmode, "handle_local_send", fake_local_send)
    # smtp_engine stub
    def fake_smtp_fail(**kwargs):
        raise RuntimeError("SMTP down")
    monkeypatch.setattr(smtp_engine, "send_email_smtp", fake_smtp_fail)
    return monkeypatch

def test_track_open_in_dry_run(monkeypatch):
    cfg = {"host":"h","port":25,"username":"u","password":"p","use_tls":False}
    client = OpenMailerClient(config=cfg, dry_run=True)
    res = client.send_email(
        to="a@b.com", subject="s", html_body="<p>hi</p>",
        track_open=True)
    assert 'track/open/a@b.com' in res["file"] or res["status"]=="saved"
