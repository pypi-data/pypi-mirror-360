
# openmailer/logger.py
from rich.console import Console
console = Console()

def log_event(to, status, smtp, console_override=None):
    c = console_override or console
    c.print(f"[green]Email to {to}[/green] → [blue]{smtp}[/blue] → Status: [bold]{status}[/bold]")
