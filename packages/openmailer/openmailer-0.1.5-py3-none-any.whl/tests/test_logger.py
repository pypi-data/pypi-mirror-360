
from rich.console import Console
from io import StringIO
from openmailer.logger import log_event

def test_log_event_prints():
    output = StringIO()
    test_console = Console(file=output, force_terminal=True)
    log_event("test@example.com", "sent", "smtp.example.com", console_override=test_console)

    contents = output.getvalue()
    assert "sent" in contents
    assert "smtp.example.com" in contents

