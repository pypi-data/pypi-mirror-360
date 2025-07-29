"""Command-line interface for freetracker."""

import click
import csv
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.prompt import Prompt, IntPrompt, Confirm
from rich import box

from .storage import Storage
from .models import Client, Project, TimeEntry
from .ui import (
    display_clients_table, display_projects_table, display_time_entries_table,
    display_success, display_error, display_info, display_active_timer,
    prompt_date, format_hours, format_date
)
from .completion import prompt_client_name, prompt_project_name

console = Console()
storage = Storage()


@click.group()
@click.version_option(prog_name="freetracker")
@click.pass_context
def main(ctx):
    """freetracker - Track your freelance working hours."""
    # Check for active timer on every command
    ctx.ensure_object(dict)
    active = storage.get_active_timer()
    if active and ctx.invoked_subcommand != 'stop':
        project_id, entry = active
        project = storage.get_project(project_id)
        if project:
            display_active_timer(project.name, entry.start_time)


# Client commands
@main.group()
def client():
    """Manage clients."""
    pass


@client.command('add')
def add_client():
    """Add a new client."""
    name = Prompt.ask("Client name")
    if not name:
        display_error("Client name cannot be empty")
        return
    
    client = storage.create_client(name)
    display_success(f"Added client '{client.name}' with ID {client.id[:8]}")


@client.command('list')
def list_clients():
    """List all clients."""
    clients = storage.get_all_clients()
    if not clients:
        display_info("No clients found. Add one with 'freetracker client add'")
        return
    
    display_clients_table(clients)


@client.command('edit')
def edit_client():
    """Edit a client."""
    clients = storage.get_all_clients()
    if not clients:
        display_info("No clients found. Add one with 'freetracker client add'")
        return
    
    display_clients_table(clients)
    
    # Get client names for tab completion
    client_names = [client.name for client in clients]
    client_name = prompt_client_name(client_names, "\nEnter client name")
    
    # Find client by name
    client = storage.find_client_by_name(client_name)
    if not client:
        display_error(f"Client '{client_name}' not found")
        return
    new_name = Prompt.ask("New name", default=client.name)
    
    if storage.update_client(client.id, new_name):
        display_success(f"Updated client '{new_name}'")
    else:
        display_error("Failed to update client")


@client.command('delete')
def delete_client():
    """Delete a client."""
    clients = storage.get_all_clients()
    if not clients:
        display_info("No clients found")
        return
    
    display_clients_table(clients)
    
    # Get client names for tab completion
    client_names = [client.name for client in clients]
    client_name = prompt_client_name(client_names, "\nEnter client name")
    
    # Find client by name
    client = storage.find_client_by_name(client_name)
    if not client:
        display_error(f"Client '{client_name}' not found")
        return
    if Confirm.ask(f"Delete client '{client.name}' and all its projects?"):
        if storage.delete_client(client.id):
            display_success(f"Deleted client '{client.name}'")
        else:
            display_error("Failed to delete client")


# Project commands
@main.group()
def project():
    """Manage projects."""
    pass


@project.command('add')
def add_project():
    """Add a new project."""
    clients = storage.get_all_clients()
    if not clients:
        display_info("No clients found. Add one with 'freetracker client add'")
        return
    
    display_clients_table(clients)
    
    # Get client names for tab completion
    client_names = [client.name for client in clients]
    client_name = prompt_client_name(client_names, "\nEnter client name")
    
    # Find client by name
    client = storage.find_client_by_name(client_name)
    if not client:
        display_error(f"Client '{client_name}' not found")
        return
    
    name = Prompt.ask("Project name")
    if not name:
        display_error("Project name cannot be empty")
        return
    
    hours_quoted = IntPrompt.ask("Hours quoted", default=0)
    due_date = prompt_date("Due date (YYYY-MM-DD)", date.today() + timedelta(days=30))
    
    project = storage.create_project(client.id, name, hours_quoted, due_date)
    if project:
        display_success(f"Added project '{project.name}' for client '{client.name}'")
    else:
        display_error("Failed to create project")


@project.command('list')
@click.option('--client', '-c', help='Filter by client ID')
def list_projects(client):
    """List all projects."""
    if client:
        # Find client by partial ID
        clients = storage.get_all_clients()
        matching_clients = [c for c in clients if c.id.startswith(client)]
        if not matching_clients:
            display_error("Client not found")
            return
        if len(matching_clients) > 1:
            display_error("Multiple clients match that ID. Please be more specific.")
            return
        
        projects = storage.get_projects_for_client(matching_clients[0].id)
        if not projects:
            display_info(f"No projects found for client '{matching_clients[0].name}'")
            return
    else:
        # Get all projects
        clients = storage.get_all_clients()
        projects = []
        for c in clients:
            projects.extend(c.projects)
        
        if not projects:
            display_info("No projects found. Add one with 'freetracker project add'")
            return
    
    display_projects_table(projects, show_client=not client, storage=storage)


@project.command('edit')
def edit_project():
    """Edit a project."""
    clients = storage.get_all_clients()
    projects = []
    for c in clients:
        projects.extend(c.projects)
    
    if not projects:
        display_info("No projects found. Add one with 'freetracker project add'")
        return
    
    display_projects_table(projects, show_client=True, storage=storage)
    
    # Get project names for tab completion
    project_names = [project.name for project in projects]
    project_name = prompt_project_name(project_names, "\nEnter project name")
    
    # Find project by name
    project = storage.find_project_by_name(project_name)
    if not project:
        display_error(f"Project '{project_name}' not found")
        return
    
    new_name = Prompt.ask("New name", default=project.name)
    new_hours = IntPrompt.ask("Hours quoted", default=project.hours_quoted)
    new_due_date = prompt_date("Due date (YYYY-MM-DD)", project.due_date)
    
    if storage.update_project(project.id, new_name, new_hours, new_due_date):
        display_success(f"Updated project '{new_name}'")
    else:
        display_error("Failed to update project")


@project.command('delete')
def delete_project():
    """Delete a project."""
    clients = storage.get_all_clients()
    projects = []
    for c in clients:
        projects.extend(c.projects)
    
    if not projects:
        display_info("No projects found")
        return
    
    display_projects_table(projects, show_client=True, storage=storage)
    
    # Get project names for tab completion
    project_names = [project.name for project in projects]
    project_name = prompt_project_name(project_names, "\nEnter project name")
    
    # Find project by name
    project = storage.find_project_by_name(project_name)
    if not project:
        display_error(f"Project '{project_name}' not found")
        return
    
    if Confirm.ask(f"Delete project '{project.name}' and all its time entries?"):
        if storage.delete_project(project.id):
            display_success(f"Deleted project '{project.name}'")
        else:
            display_error("Failed to delete project")


# Time tracking commands
@main.command()
def start():
    """Start tracking time for a project."""
    # Check for active timer
    active = storage.get_active_timer()
    if active:
        display_error("A timer is already running. Stop it first with 'freetracker stop'")
        return
    
    clients = storage.get_all_clients()
    projects = []
    for c in clients:
        projects.extend(c.projects)
    
    if not projects:
        display_info("No projects found. Add one with 'freetracker project add'")
        return
    
    display_projects_table(projects, show_client=True, storage=storage)
    
    # Get project names for tab completion
    project_names = [project.name for project in projects]
    project_name = prompt_project_name(project_names, "\nEnter project name")
    
    # Find project by name
    project = storage.find_project_by_name(project_name)
    if not project:
        display_error(f"Project '{project_name}' not found")
        return
    
    # Create time entry with no end time
    entry = storage.create_time_entry(project.id, datetime.now(), None)
    if entry:
        display_success(f"Started timer for project '{project.name}'")
        console.print(f"[dim]Started at {entry.start_time.strftime('%H:%M')}[/dim]")
    else:
        display_error("Failed to start timer")


@main.command()
def stop():
    """Stop the active timer."""
    entry = storage.stop_active_timer()
    if entry:
        project = storage.get_project(entry.project_id)
        display_success(f"Stopped timer for project '{project.name if project else 'Unknown'}'")
        console.print(f"[dim]Duration: {format_hours(entry.hours)}[/dim]")
    else:
        display_info("No active timer found")


@main.command()
def cancel():
    """Cancel the active timer without logging it."""
    # Get active timer info before cancelling
    active_timer = storage.get_active_timer()
    if not active_timer:
        display_info("No active timer found")
        return
    
    project_name, timer_entry = active_timer
    
    # Calculate duration for display
    duration = datetime.now() - timer_entry.start_time
    hours = duration.total_seconds() / 3600
    
    # Show timer info and confirm
    console.print(f"\n[bold yellow]Active Timer:[/bold yellow]")
    console.print(f"Project: [cyan]{project_name}[/cyan]")
    console.print(f"Started: [green]{timer_entry.start_time.strftime('%H:%M')}[/green]")
    console.print(f"Duration: [yellow]{format_hours(hours)}[/yellow]")
    
    if Confirm.ask("\n[bold red]Cancel this timer without logging?[/bold red]"):
        if storage.cancel_active_timer():
            display_success("Timer cancelled. No time was logged.")
        else:
            display_error("Failed to cancel timer")
    else:
        display_info("Cancelled. Timer remains active.")


@main.command()
def add():
    """Manually add hours to a project."""
    clients = storage.get_all_clients()
    projects = []
    for c in clients:
        projects.extend(c.projects)
    
    if not projects:
        display_info("No projects found. Add one with 'freetracker project add'")
        return
    
    display_projects_table(projects, show_client=True, storage=storage)
    
    # Get project names for tab completion
    project_names = [project.name for project in projects]
    project_name = prompt_project_name(project_names, "\nEnter project name")
    
    # Find project by name
    project = storage.find_project_by_name(project_name)
    if not project:
        display_error(f"Project '{project_name}' not found")
        return
    
    # Prompt for time details
    console.print("\n[bold]Add manual time entry[/bold]")
    
    # Ask for date
    entry_date = prompt_date("Date (YYYY-MM-DD)", date.today())
    
    # Ask for hours
    hours = Prompt.ask("Hours worked", default="1.0")
    try:
        hours_float = float(hours)
        if hours_float <= 0:
            display_error("Hours must be greater than 0")
            return
    except ValueError:
        display_error("Invalid hours format. Please enter a number (e.g., 2.5)")
        return
    
    # Ask for optional description
    description = Prompt.ask("Description (optional)", default="Manual time entry")
    
    # Calculate start and end times based on hours (for compatibility with existing system)
    # Default to a reasonable work time (9 AM start)
    default_start_time = datetime.combine(entry_date, datetime.strptime("09:00", "%H:%M").time())
    hours_delta = timedelta(hours=hours_float)
    end_time = default_start_time + hours_delta
    start_time = default_start_time
    
    # Create the time entry
    entry = storage.create_time_entry(project.id, start_time, end_time)
    if entry:
        display_success(f"Added {hours_float} hours to project '{project.name}'")
        console.print(f"[dim]Date: {entry_date.strftime('%Y-%m-%d')}[/dim]")
        console.print(f"[dim]Description: {description}[/dim]")
    else:
        display_error("Failed to add time entry")


@main.command()
def status():
    """Show current timer status."""
    active = storage.get_active_timer()
    if active:
        project_id, entry = active
        project = storage.get_project(project_id)
        if project:
            display_active_timer(project.name, entry.start_time)
    else:
        display_info("No active timer")
    
    # Show database location
    console.print(f"\n[dim]Database: {storage.db_path}[/dim]")


# Reporting commands
@main.command()
@click.option('--csv', 'output_csv', is_flag=True, help='Export as CSV')
@click.option('--output', '-o', type=click.Path(), help='Output file path for CSV')
def report(output_csv, output):
    """Generate time tracking report with progress bars."""
    clients = storage.get_all_clients()
    if not clients:
        display_info("No data to report")
        return
    
    if output_csv:
        # CSV export
        output_path = Path(output) if output else Path("freetracker_report.csv")
        
        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Client', 'Project', 'Hours Quoted', 'Hours Worked', 
                           'Hours Remaining', 'Progress %', 'Due Date'])
            
            for client in clients:
                for project in client.projects:
                    writer.writerow([
                        client.name,
                        project.name,
                        project.hours_quoted,
                        f"{project.hours_worked:.2f}",
                        f"{project.hours_remaining:.2f}",
                        f"{project.progress_percentage:.1f}",
                        project.due_date.isoformat()
                    ])
        
        display_success(f"Report exported to {output_path}")
    else:
        # Terminal display with progress bars
        console.print("\n[bold]Time Tracking Report[/bold]\n")
        
        total_hours_all_clients = sum(c.total_hours_worked for c in clients)
        
        for client in clients:
            if not client.projects:
                continue
            
            # Client header
            console.print(f"\n[bold cyan]{client.name}[/bold cyan]")
            console.print(f"[dim]Total hours: {format_hours(client.total_hours_worked)}[/dim]\n")
            
            # Projects with progress bars
            with Progress(
                TextColumn("[bold blue]{task.fields[name]}[/bold blue]"),
                BarColumn(bar_width=30),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("{task.fields[hours]}"),
                console=console
            ) as progress:
                
                for project in client.projects:
                    task = progress.add_task(
                        "",
                        total=project.hours_quoted if project.hours_quoted > 0 else 1,
                        completed=min(project.hours_worked, project.hours_quoted),
                        name=project.name,
                        hours=f"{format_hours(project.hours_worked)}/{project.hours_quoted}h"
                    )
        
        # Summary
        console.print(f"\n[bold]Total Hours Tracked:[/bold] {format_hours(total_hours_all_clients)}")


@main.command()
@click.argument('project_name', required=False)
def log(project_name):
    """View time entry log for a project. Use project name as argument."""
    if project_name:
        # Find project by name
        project = storage.find_project_by_name(project_name)
        if not project:
            display_error(f"Project '{project_name}' not found")
            return
        entries = project.time_entries
        
        if not entries:
            display_info(f"No time entries for project '{project.name}'")
            return
        
        console.print(f"\n[bold]Time Entries for '{project.name}'[/bold]\n")
        display_time_entries_table(entries)
        console.print(f"\n[bold]Total:[/bold] {format_hours(project.hours_worked)}")
    else:
        # Show recent entries across all projects
        clients = storage.get_all_clients()
        all_entries = []
        
        for client in clients:
            for project in client.projects:
                for entry in project.time_entries:
                    all_entries.append((client.name, project.name, entry))
        
        if not all_entries:
            display_info("No time entries found")
            return
        
        # Sort by start time, most recent first
        all_entries.sort(key=lambda x: x[2].start_time, reverse=True)
        
        # Display table
        table = Table(title="Recent Time Entries", box=box.ROUNDED)
        table.add_column("Date", style="cyan")
        table.add_column("Client", style="green")
        table.add_column("Project", style="yellow")
        table.add_column("Start", style="white")
        table.add_column("End", style="white")
        table.add_column("Duration", justify="right", style="magenta")
        
        # Show last 20 entries
        for client_name, project_name, entry in all_entries[:20]:
            table.add_row(
                entry.start_time.strftime("%Y-%m-%d"),
                client_name,
                project_name,
                entry.start_time.strftime("%H:%M"),
                entry.end_time.strftime("%H:%M") if entry.end_time else "Active",
                format_hours(entry.hours)
            )
        
        console.print(table)


if __name__ == "__main__":
    main()