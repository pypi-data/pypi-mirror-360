from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

def build_email_message(from_email, to_email, subject, html_body, attachments=None):
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    # Attach HTML
    msg.attach(MIMEText(html_body, "html"))

    # Attach files
    if attachments:
        for path in attachments:
            with open(path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(path))
                part["Content-Disposition"] = f'attachment; filename="{os.path.basename(path)}"'
                msg.attach(part)

    return msg
