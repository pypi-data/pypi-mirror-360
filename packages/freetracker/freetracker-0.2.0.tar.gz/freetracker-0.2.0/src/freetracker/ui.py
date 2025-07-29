"""UI components and helpers using Rich."""

from datetime import datetime, date
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.text import Text
from rich import box

from .models import Client, Project, TimeEntry

console = Console()


def format_hours(hours: float) -> str:
    """Format hours as HH:MM."""
    h = int(hours)
    m = int((hours - h) * 60)
    return f"{h:02d}:{m:02d}"


def format_date(d: date) -> str:
    """Format date for display."""
    return d.strftime("%Y-%m-%d")


def prompt_date(prompt_text: str, default: Optional[date] = None) -> date:
    """Prompt for a date input."""
    default_str = default.isoformat() if default else date.today().isoformat()
    while True:
        date_str = Prompt.ask(prompt_text, default=default_str)
        try:
            return date.fromisoformat(date_str)
        except ValueError:
            console.print("[red]Invalid date format. Please use YYYY-MM-DD[/red]")


def display_clients_table(clients: List[Client]) -> None:
    """Display a table of clients."""
    table = Table(title="Clients", box=box.ROUNDED)
    table.add_column("#", style="bold magenta", width=3)
    table.add_column("ID", style="dim", width=8)
    table.add_column("Name", style="cyan")
    table.add_column("Projects", justify="right", style="green")
    table.add_column("Total Hours", justify="right", style="yellow")
    
    for i, client in enumerate(clients, 1):
        table.add_row(
            str(i),
            client.id[:8],
            client.name,
            str(len(client.projects)),
            format_hours(client.total_hours_worked)
        )
    
    console.print(table)


def display_projects_table(projects: List[Project], show_client: bool = False, storage=None) -> None:
    """Display a table of projects."""
    table = Table(title="Projects", box=box.ROUNDED)
    table.add_column("#", style="bold magenta", width=3)
    table.add_column("ID", style="dim", width=8)
    if show_client:
        table.add_column("Client", style="cyan")
    table.add_column("Name", style="cyan")
    table.add_column("Quoted", justify="right", style="green")
    table.add_column("Worked", justify="right", style="yellow")
    table.add_column("Remaining", justify="right", style="red")
    table.add_column("Due Date", style="magenta")
    table.add_column("Progress", justify="right")
    
    for i, project in enumerate(projects, 1):
        row = [
            str(i),
            project.id[:8],
            project.name,
            str(project.hours_quoted),
            format_hours(project.hours_worked),
            format_hours(project.hours_remaining),
            format_date(project.due_date),
            f"{project.progress_percentage:.0f}%"
        ]
        if show_client and storage:
            client = storage.get_client(project.client_id)
            client_name = client.name if client else "Unknown"
            row.insert(2, client_name)
        elif show_client:
            row.insert(2, "")  # Fallback if no storage provided
        table.add_row(*row)
    
    console.print(table)


def display_time_entries_table(entries: List[TimeEntry]) -> None:
    """Display a table of time entries."""
    table = Table(title="Time Entries", box=box.ROUNDED)
    table.add_column("Date", style="cyan")
    table.add_column("Start Time", style="green")
    table.add_column("End Time", style="red")
    table.add_column("Duration", justify="right", style="yellow")
    
    for entry in entries:
        table.add_row(
            entry.start_time.strftime("%Y-%m-%d"),
            entry.start_time.strftime("%H:%M"),
            entry.end_time.strftime("%H:%M") if entry.end_time else "Active",
            format_hours(entry.hours)
        )
    
    console.print(table)


def display_success(message: str) -> None:
    """Display a success message."""
    console.print(f"[bold green]✓[/bold green] {message}")


def display_error(message: str) -> None:
    """Display an error message."""
    console.print(f"[bold red]✗[/bold red] {message}")


def display_info(message: str) -> None:
    """Display an info message."""
    console.print(f"[bold blue]ℹ[/bold blue] {message}")


def display_active_timer(project_name: str, start_time: datetime) -> None:
    """Display active timer info."""
    duration = datetime.now() - start_time
    hours = duration.total_seconds() / 3600
    
    panel = Panel(
        f"[bold yellow]Timer Active[/bold yellow]\n\n"
        f"Project: [cyan]{project_name}[/cyan]\n"
        f"Started: {start_time.strftime('%H:%M')}\n"
        f"Duration: [green]{format_hours(hours)}[/green]",
        title="[bold]Active Timer[/bold]",
        border_style="yellow"
    )
    console.print(panel)