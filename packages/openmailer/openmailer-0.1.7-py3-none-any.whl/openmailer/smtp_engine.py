import smtplib

def send_email_smtp(smtp_host, smtp_port, username, password, use_tls, message):
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        if use_tls:
            server.starttls()
        server.login(username, password)
        server.send_message(message)
    return {"status": "sent"}
