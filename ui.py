from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from contextlib import contextmanager

console = Console()

def render_error_card(explanation: str, fix_command: str | None = None) -> None:
    console.print(Panel(
        Text("Error intercepted", style="bold red"),
        border_style="red",
        title="[bold]fixit[/bold]"
    ))
    console.print(Panel(
        explanation,
        title="[bold yellow]Explanation[/bold yellow]",
        border_style="yellow",
        padding=(1, 2)
    ))
    if fix_command:
        console.print(Panel(
            Text(fix_command, style="bold green"),
            title="[bold green]Suggested Fix[/bold green]",
            border_style="green"
        ))

@contextmanager
def render_spinner(message: str):
    with console.status(f"[bold cyan]{message}[/bold cyan]", spinner="dots"):
        yield

def prompt_auto_execute(command: str) -> bool:
    console.print()
    choice = console.input(
        f"[bold yellow]Run this command?[/bold yellow] "
        f"[dim]({command})[/dim] [Y/n]: "
    )
    return choice.strip().lower() in ("", "y", "yes")
