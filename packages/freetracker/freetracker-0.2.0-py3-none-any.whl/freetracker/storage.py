"""TinyDB storage layer for freetracker."""

import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime, date
from tinydb import TinyDB, Query
from tinydb.table import Document

from .models import Client, Project, TimeEntry


class Storage:
    """Handles data persistence using TinyDB."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize storage with database path."""
        if db_path is None:
            # Check for environment variable first
            env_path = os.environ.get('FREETRACKER_DB_PATH')
            if env_path:
                db_path = Path(env_path)
                # Ensure the directory exists
                db_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                # Default to ~/.freetracker/db.json
                home = Path.home()
                db_dir = home / ".freetracker"
                db_dir.mkdir(exist_ok=True)
                db_path = db_dir / "db.json"
        
        self.db_path = db_path  # Store for reference
        self.db = TinyDB(db_path)
        self.clients = self.db.table('clients')
        self.projects = self.db.table('projects')
        self.time_entries = self.db.table('time_entries')
    
    # Client operations
    def create_client(self, name: str) -> Client:
        """Create a new client."""
        client = Client(name=name)
        self.clients.insert({
            'id': client.id,
            'name': client.name
        })
        return client
    
    def get_client(self, client_id: str) -> Optional[Client]:
        """Get a client by ID."""
        query = Query()
        doc = self.clients.get(query.id == client_id)
        if doc:
            client = Client(id=doc['id'], name=doc['name'])
            client.projects = self.get_projects_for_client(client_id)
            return client
        return None
    
    def get_all_clients(self) -> List[Client]:
        """Get all clients."""
        clients = []
        for doc in self.clients.all():
            client = Client(id=doc['id'], name=doc['name'])
            client.projects = self.get_projects_for_client(client.id)
            clients.append(client)
        return clients
    
    def find_client_by_name(self, name: str) -> Optional[Client]:
        """Find a client by name (case insensitive)."""
        query = Query()
        docs = self.clients.search(query.name.test(lambda x: x.lower() == name.lower()))
        if docs:
            doc = docs[0]  # Return first match
            client = Client(id=doc['id'], name=doc['name'])
            client.projects = self.get_projects_for_client(client.id)
            return client
        return None
    
    def update_client(self, client_id: str, name: str) -> bool:
        """Update a client's name."""
        query = Query()
        return len(self.clients.update({'name': name}, query.id == client_id)) > 0
    
    def delete_client(self, client_id: str) -> bool:
        """Delete a client and all associated projects."""
        query = Query()
        # Delete all projects for this client
        projects = self.get_projects_for_client(client_id)
        for project in projects:
            self.delete_project(project.id)
        # Delete the client
        return len(self.clients.remove(query.id == client_id)) > 0
    
    # Project operations
    def create_project(self, client_id: str, name: str, hours_quoted: int, due_date: date) -> Optional[Project]:
        """Create a new project for a client."""
        # Verify client exists
        if not self.get_client(client_id):
            return None
        
        project = Project(
            client_id=client_id,
            name=name,
            hours_quoted=hours_quoted,
            due_date=due_date
        )
        
        self.projects.insert({
            'id': project.id,
            'client_id': project.client_id,
            'name': project.name,
            'hours_quoted': project.hours_quoted,
            'due_date': due_date.isoformat()
        })
        return project
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID."""
        query = Query()
        doc = self.projects.get(query.id == project_id)
        if doc:
            project = Project(
                id=doc['id'],
                client_id=doc['client_id'],
                name=doc['name'],
                hours_quoted=doc['hours_quoted'],
                due_date=date.fromisoformat(doc['due_date'])
            )
            project.time_entries = self.get_time_entries_for_project(project_id)
            return project
        return None
    
    def get_projects_for_client(self, client_id: str) -> List[Project]:
        """Get all projects for a client."""
        query = Query()
        projects = []
        for doc in self.projects.search(query.client_id == client_id):
            project = Project(
                id=doc['id'],
                client_id=doc['client_id'],
                name=doc['name'],
                hours_quoted=doc['hours_quoted'],
                due_date=date.fromisoformat(doc['due_date'])
            )
            project.time_entries = self.get_time_entries_for_project(project.id)
            projects.append(project)
        return projects
    
    def find_project_by_name(self, name: str) -> Optional[Project]:
        """Find a project by name (case insensitive)."""
        query = Query()
        docs = self.projects.search(query.name.test(lambda x: x.lower() == name.lower()))
        if docs:
            doc = docs[0]  # Return first match
            project = Project(
                id=doc['id'],
                client_id=doc['client_id'],
                name=doc['name'],
                hours_quoted=doc['hours_quoted'],
                due_date=date.fromisoformat(doc['due_date'])
            )
            project.time_entries = self.get_time_entries_for_project(project.id)
            return project
        return None
    
    def update_project(self, project_id: str, name: str, hours_quoted: int, due_date: date) -> bool:
        """Update a project."""
        query = Query()
        return len(self.projects.update({
            'name': name,
            'hours_quoted': hours_quoted,
            'due_date': due_date.isoformat()
        }, query.id == project_id)) > 0
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project and all associated time entries."""
        query = Query()
        # Delete all time entries for this project
        self.time_entries.remove(query.project_id == project_id)
        # Delete the project
        return len(self.projects.remove(query.id == project_id)) > 0
    
    # Time entry operations
    def create_time_entry(self, project_id: str, start_time: datetime, end_time: Optional[datetime] = None) -> Optional[TimeEntry]:
        """Create a new time entry."""
        # Verify project exists
        if not self.get_project(project_id):
            return None
        
        # If creating an active timer (no end_time), stop any existing active timer
        if end_time is None:
            self.stop_active_timer()
        
        entry = TimeEntry(
            project_id=project_id,
            start_time=start_time,
            end_time=end_time
        )
        if end_time:
            entry.hours = entry.calculate_hours()
        else:
            entry.hours = 0
        
        self.time_entries.insert({
            'id': entry.id,
            'project_id': entry.project_id,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat() if end_time else None,
            'hours': entry.hours
        })
        return entry
    
    def get_time_entries_for_project(self, project_id: str) -> List[TimeEntry]:
        """Get all time entries for a project."""
        query = Query()
        entries = []
        for doc in self.time_entries.search(query.project_id == project_id):
            entry = TimeEntry(
                id=doc['id'],
                project_id=doc['project_id'],
                start_time=datetime.fromisoformat(doc['start_time']),
                end_time=datetime.fromisoformat(doc['end_time']) if doc['end_time'] else None,
                hours=doc['hours']
            )
            entries.append(entry)
        return entries
    
    def get_active_timer(self) -> Optional[tuple[str, TimeEntry]]:
        """Get the currently active timer if any."""
        query = Query()
        doc = self.time_entries.get(query.end_time == None)
        if doc:
            entry = TimeEntry(
                id=doc['id'],
                project_id=doc['project_id'],
                start_time=datetime.fromisoformat(doc['start_time']),
                end_time=None,
                hours=0
            )
            return doc['project_id'], entry
        return None
    
    def stop_active_timer(self) -> Optional[TimeEntry]:
        """Stop all currently active timers."""
        query = Query()
        end_time = datetime.now()
        
        # Find all active timers
        active_docs = self.time_entries.search(query.end_time == None)
        
        if not active_docs:
            return None
        
        # Update all active timers
        last_entry = None
        for doc in active_docs:
            entry = TimeEntry(
                id=doc['id'],
                project_id=doc['project_id'],
                start_time=datetime.fromisoformat(doc['start_time']),
                end_time=end_time,
                hours=0
            )
            entry.hours = entry.calculate_hours()
            
            self.time_entries.update({
                'end_time': end_time.isoformat(),
                'hours': entry.hours
            }, query.id == entry.id)
            
            last_entry = entry
        
        return last_entry
    
    def cancel_active_timer(self) -> bool:
        """Cancel (delete) the currently active timer without logging it."""
        query = Query()
        
        # Find active timer
        active_docs = self.time_entries.search(query.end_time == None)
        
        if not active_docs:
            return False
        
        # Delete all active timers
        for doc in active_docs:
            self.time_entries.remove(query.id == doc['id'])
        
        return True