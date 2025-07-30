import os
from datetime import datetime

def handle_local_send(message, to):
    filename = f"outbox/email-{datetime.now().isoformat()}-{to}.eml".replace(":", "_")
    os.makedirs("outbox", exist_ok=True)
    with open(filename, "w") as f:
        f.write(message.as_string())
    return {"status": "saved", "file": filename}