import re
import os
import time
from jinja2 import meta, Environment

from openmailer.smtp_engine import send_email_smtp
from openmailer.message_builder import build_email_message
from openmailer.template_engine import render_template
from openmailer.localmode import handle_local_send
from openmailer.queue_manager import QueueManager
from openmailer.logger import log_event
from openmailer.rate_limiter import RateLimiter
from openmailer.secrets import get_smtp_config
from openmailer.health_monitor import HealthMonitor
from openmailer.analytics import Analytics

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
MAX_ATTACHMENT_MB = 10

##  main
class OpenMailerClient:
    def __init__(self, config=None, dry_run=False):
        self.dry_run = dry_run
        self.queue = QueueManager()
        self.health = HealthMonitor()
        self.analytics = Analytics()

        if config is None:
            config = get_smtp_config()

        if isinstance(config, dict):
            self.backends = [config]
        elif isinstance(config, list):
            self.backends = config
        else:
            raise ValueError("Invalid config format")

        self.limiters = {
            b["host"]: RateLimiter(b.get("rate_limit", 20))
            for b in self.backends
        }

    def _validate_email(self, email: str):
        if not re.match(EMAIL_REGEX, email):
            raise ValueError(f"Invalid email address: {email}")

    def _validate_attachments(self, attachments):
        for file in attachments or []:
            if not os.path.isfile(file):
                raise FileNotFoundError(f"Attachment not found: {file}")
            if os.path.getsize(file) > MAX_ATTACHMENT_MB * 1024 * 1024:
                raise ValueError(f"Attachment too large: {file} exceeds {MAX_ATTACHMENT_MB}MB")

    def _validate_template_vars(self, template_str, context):
        env = Environment()
        parsed = env.parse(template_str)
        required_vars = meta.find_undeclared_variables(parsed)
        missing = required_vars - set(context or {})
        if missing:
            print(f"⚠️ Warning: Missing template variables: {', '.join(missing)}")

    def send_email(
        self,
        to,
        subject,
        html_body,
        context=None,
        attachments=None,
        report_mode=False,
        schedule=None,
        priority="normal",
        track_open=False
    ):
        self._validate_email(to)
        self._validate_attachments(attachments)
        self._validate_template_vars(html_body, context)

        body = render_template(html_body, context or {})

        if track_open:
            tracking_pixel = f'<img src="https://yourdomain.com/track/open/{to}" width="1" height="1" style="display:none">'
            body += tracking_pixel

        if schedule:
            self.queue.add({
                "to": to,
                "subject": subject,
                "template": html_body,
                "context": context,
                "attachments": attachments,
                "priority": priority,
                "track_open": track_open
            }, delay=schedule)
            log_event(to, "scheduled")
            return {"status": "scheduled", "to": to}

        message = build_email_message(
            from_email=self.backends[0]["username"],
            to_email=to,
            subject=subject,
            html_body=body,
            attachments=attachments
        )

        for backend in self.backends:
            try:
                if self.dry_run:
                    log_event(to, "dry-run", backend["host"])
                    if report_mode:
                        return {"success": [{"to": to}], "failed": []}
                    return handle_local_send(message, to)

                self.limiters[backend["host"]].wait()

                result = send_email_smtp(
                    smtp_host=backend["host"],
                    smtp_port=backend["port"],
                    username=backend["username"],
                    password=backend["password"],
                    use_tls=backend["use_tls"],
                    message=message
                )

                self.health.record_success(backend["host"])
                self.analytics.record("sent", backend["host"])
                log_event(to, "sent", backend["host"])

                if report_mode:
                    return {"success": [{"to": to}], "failed": []}
                return result

            except Exception as e:
                self.health.record_failure(backend["host"], e)
                self.analytics.record("failed", backend["host"])
                log_event(to, "failed", f"{backend['host']}: {str(e)}")
                last_error = str(e)

        self.queue.add({
            "to": to,
            "subject": subject,
            "template": html_body,
            "context": context,
            "attachments": attachments,
            "priority": priority,
            "track_open": track_open
        })

        if report_mode:
            return {"success": [], "failed": [{"to": to, "error": last_error}]}
        raise Exception(f"❌ All backends failed to send email to {to}: {last_error}")

    def send_bulk(self, recipients, subject, html_body, context_fn=None, attachments=None):
        report = {
            "status": "pending",
            "success": [],
            "failed": []
        }

        for to in recipients:
            try:
                context = context_fn(to) if context_fn else {}
                result = self.send_email(
                    to=to,
                    subject=subject,
                    html_body=html_body,
                    context=context,
                    attachments=attachments,
                    report_mode=True
                )
                report["success"].extend(result["success"])
                report["failed"].extend(result["failed"])
            except Exception as e:
                report["failed"].append({"to": to, "error": str(e)})

        if report["success"] and not report["failed"]:
            report["status"] = "success"
        elif report["failed"] and not report["success"]:
            report["status"] = "failed"
        else:
            report["status"] = "partial"

        return report

    def feedback_to_sender(self, sender_email, report, subject="OpenMailer Delivery Report"):
        success_count = len(report["success"])
        failed_count = len(report["failed"])
        error_list = "".join(
            f"<li>{item['to']}: {item.get('error', 'Unknown error')}</li>"
            for item in report["failed"]
        )

        html = f"""
        <html>
        <body>
          <h2>Delivery Report: {report['status'].upper()}</h2>
          <p><strong>Success:</strong> {success_count}</p>
          <p><strong>Failed:</strong> {failed_count}</p>
          <ul>{error_list}</ul>
        </body>
        </html>
        """

        self.send_email(
            to=sender_email,
            subject=subject,
            html_body=html
        )

    def retry_all(self):
        while True:
            job = self.queue.pop()
            if not job:
                break
            try:
                self.send_email(
                    to=job["to"],
                    subject=job["subject"],
                    html_body=job["template"],
                    context=job.get("context"),
                    attachments=job.get("attachments"),
                    track_open=job.get("track_open", False)
                )
                self.analytics.record("retry", self.backends[0]["host"])
            except Exception as e:
                log_event(job["to"], "retry-failed", str(e))
                self.analytics.record("retry-failed", self.backends[0]["host"])

    def get_health_status(self):
        return self.health.get_health()

    def get_analytics(self):
        return self.analytics.get_metrics()




