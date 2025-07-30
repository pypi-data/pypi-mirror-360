from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

print("✅ Loaded message_builder.py")

try:
    EmailMessage
except NameError:
    from email.message import EmailMessage

def build_email_message(from_email, to_email, subject, html_body, attachments=None, headers=None):
    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content("This is a MIME formatted email. Please view in an HTML compatible client.")
    msg.add_alternative(html_body, subtype='html')

    for file in attachments or []:
        with open(file, "rb") as f:
            file_data = f.read()
            filename = os.path.basename(file)
            msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=filename)

    # ✅ Add custom headers
    if headers:
        for key, value in headers.items():
            msg[key] = str(value)

    return msg
