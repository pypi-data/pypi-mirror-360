
# 📬 OpenMailer

**OpenMailer** is a free, open-source Python email delivery framework.

Send transactional or bulk email with your own SMTP server — Gmail, Outlook, AWS SES, Postfix, or any custom SMTP. No need for SendGrid, Mailgun, or other paid services.

---

## 🚀 Why OpenMailer?

| Problem             | How OpenMailer Solves It                                |
|---------------------|----------------------------------------------------------|
| 💰 Expensive APIs   | Uses your own SMTP — no vendor fees                      |
| 🔒 Vendor lock-in   | 100% self-hosted, open-source, and extensible            |
| 🤯 Complex APIs     | Developer-first design with both CLI & Python SDK        |
| 🔍 No visibility    | Transparent retry queue, terminal UI, logging, reports   |

---

## 🔧 Key Features

- ✅ HTML email templating ({{name}}, {{link}}, etc.)
- ✅ Multi-backend SMTP routing & failover
- ✅ Attachments (PDFs, ZIPs, images)
- ✅ Scheduled send (`--schedule`)
- ✅ Retry queue with live retry command (`--retry`)
- ✅ Priority queuing (`--priority`)
- ✅ Open tracking with tracking pixel
- ✅ Rate limiting & throttling
- ✅ Local testing (`--dry-run` → saves to `./outbox`)
- ✅ CLI (`opmctl`) and Python SDK
- ✅ Bulk sending with real-time terminal table
- ✅ Feedback reports for bulk send
- ✅ Health check & analytics module
- ✅ Plugin-ready architecture

---

## 🧱 Project Structure

```
openmailer/
├── client.py              # Core email client logic
├── smtp_engine.py         # Low-level SMTP sending
├── template_engine.py     # Jinja2-based rendering
├── queue_manager.py       # Handles retries & delays
├── rate_limiter.py        # Enforces send rate control
├── logger.py              # Log storage (JSON + terminal)
├── secrets.py             # Secure credential loading
├── localmode.py           # --dry-run support
├── analytics.py           # Tracks send metrics
├── config.py              # Default + override configs
├── health_monitor.py      # SMTP health & uptime logic

cli/
└── main.py                # CLI entrypoint (`opmcli`)
```

---

## 📦 Installation

```bash
git clone https://github.com/Devops-Bot-Official/OpenMailer.git
cd openmailer
python setup.py install
```

Then:

```bash
chmod +x cli/main.py
ln -s $(pwd)/cli/main.py /usr/local/bin/opmctl
```

---

## 🖥️ OpenMailer CLI

**OpenMailer CLI** (`opmcli`) is a full-featured command-line interface for managing email delivery using the OpenMailer engine.

### ⚙️ Single Send

```bash
opmctl --to user@example.com \
       --subject "Hello {{name}}" \
       --template templates/welcome.html \
       --context '{"name": "Alice"}' \
       --attachment invoice.pdf \
       --schedule "2025-07-01 09:00" \
       --priority high \
       --track-open \
       --report
```

### 📬 Bulk Email (via CSV)

```bash
opmctl bulk --csv contacts.csv --template templates/newsletter.html --report
```

**CSV Format:**

```csv
email,subject,name,link
alice@example.com,Welcome,Alice,https://example.com/welcome
bob@example.com,News,Bob,https://example.com/update
```

---

## 🧪 Testing Mode

```bash
opmctl --to test@example.com --template templates/test.html --dry-run
```

Saves the output to `./outbox/` instead of sending real email.

---

## 🪄 CLI Options

| Flag           | Description                                       |
|----------------|---------------------------------------------------|
| `--to`         | Email recipient address                           |
| `--subject`    | Subject line of the email                         |
| `--template`   | HTML file to use as email body                    |
| `--context`    | JSON dict injected into the template (`{{name}}`) |
| `--attachment` | One or more attachments (PDF, ZIP, etc.)          |
| `--schedule`   | Future datetime for scheduled send (UTC/local)    |
| `--priority`   | Email priority: high, normal, low                 |
| `--track-open` | Add tracking pixel to monitor opens               |
| `--dry-run`    | Save email as file without actually sending       |
| `--report`     | Sends delivery report to sender                   |
| `--retry`      | Retry all failed or queued emails                 |
| `bulk`         | Use for bulk email campaign via CSV               |

---

## 📊 Real-Time Table (Bulk Send)

During bulk send, the CLI displays a live table with email progress:

```
📬 Bulk Email Progress
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Recipient         ┃ Subject       ┃ Status   ┃ Error                ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ alice@example.com │ Welcome       │ ✅ Sent   │                      │
│ bob@example.com   │ Update        │ ❌ Failed │ SMTP connect timeout │
└───────────────────┴───────────────┴──────────┴──────────────────────┘
```

---

## 🧑‍💻 Python SDK (Library Usage)

```python
from openmailer import OpenMailerClient

client = OpenMailerClient()

client.send_email(
    to="user@example.com",
    subject="Hello {{name}}",
    html_body="<h1>Hello {{name}}</h1>",
    context={"name": "Bob"},
    attachments=["contract.pdf"]
)
```

### Bulk Programmatic Send

```python
report = client.send_bulk(
    recipients=["a@example.com", "b@example.com"],
    subject="Notice",
    html_body="<p>Hi {{name}}</p>",
    context_fn=lambda to: {"name": to.split("@")[0]}
)
client.feedback_to_sender("admin@example.com", report)
```

---

## 🧪 Retry

Failed deliveries are automatically stored in the retry queue.

To resend:

```bash
opmctl --retry
```

---

## 🧠 Developer Notes

- Retry queue is file-based, future versions will support Redis or DB
- Open tracking uses an invisible pixel hit
- Supports Gmail, Outlook, AWS SES, and more (with auth configs)
- Feedback system reports how many sent/failed, per recipient
- CLI uses `rich` for real-time terminal rendering
- Designed to plug into CI/CD or automation pipelines

---

## 💡 Use Cases

- Transactional messages (signup, password reset)
- System alerts and DevOps monitoring
- Custom marketing newsletters
- Embedded email engine in SaaS products
- Developer testing in local/airgapped environments

---

## 🛣 Roadmap

- ✅ Full SMTP support
- ✅ Retry and feedback system
- ✅ Bulk send and tracking
- ✅ Live table output for progress
- 🔜 REST API server mode
- 🔜 OAuth2 SMTP (Google, Outlook)
- 🔜 Admin dashboard UI
- 🔜 Docker image with SMTP + UI
- 🔜 Plugin SDK for custom auth/rules

---

## 🤝 Contributing

We welcome contributions from Pythonistas and email nerds.

```bash
git clone https://github.com/Devops-Bot-Official/OpenMailer.git
cd openmailer
python setup.py install
```

### Contributor Guidelines

- Engine logic goes in `openmailer/`
- CLI logic lives in `cli/`
- Avoid hardcoding — use config/environment
- Document new features in README
- PRs should pass basic tests and lint

---

## 📜 License

MIT License — use it freely in personal and commercial projects.

---

## ❤️ About

OpenMailer is built by and for developers who believe in freedom, transparency, and open infrastructure. No API limits. No billing traps. Just email that works.

> Made with 🐍 Python. Powered by SMTP.
