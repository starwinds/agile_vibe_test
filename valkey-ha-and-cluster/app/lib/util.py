import time
from rich.console import Console
from rich.table import Table

console = Console()

def print_title(title):
    """Prints a formatted title."""
    console.print(f"\n[bold cyan]===== {title} =====[/bold cyan]\n")

def print_step(message):
    """Prints a step message."""
    console.print(f"[yellow]▶ {message}...[/yellow]")

def print_ok(message):
    """Prints a success message."""
    console.print(f"[green]✅ {message}[/green]")

def print_fail(message):
    """Prints a failure message."""
    console.print(f"[bold red]❌ {message}[/bold red]")

def print_info(message):
    """Prints an info message."""
    console.print(f"[blue]ℹ️ {message}[/blue]")

def print_table(title, rows, columns):
    """Prints a formatted table."""
    table = Table(title=title)
    for col in columns:
        table.add_column(col, justify="left", style="magenta")
    
    for row in rows:
        table.add_row(*[str(item) for item in row])
    
    console.print(table)

def sleep_with_message(seconds, message="Waiting"):
    """Waits for a specified number of seconds while printing a message."""
    with console.status(f"[bold green]{message} for {seconds} seconds...") as status:
        time.sleep(seconds)
