"""Data models for freetracker."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List
import uuid


@dataclass
class TimeEntry:
    """Represents a single time tracking entry."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    hours: float = 0.0
    
    def calculate_hours(self) -> float:
        """Calculate hours from start and end time."""
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() / 3600
        return 0.0


@dataclass
class Project:
    """Represents a project for a client."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str = ""
    name: str = ""
    hours_quoted: int = 0
    due_date: date = field(default_factory=date.today)
    time_entries: List[TimeEntry] = field(default_factory=list)
    
    @property
    def hours_worked(self) -> float:
        """Calculate total hours worked on this project."""
        return sum(entry.hours for entry in self.time_entries)
    
    @property
    def hours_remaining(self) -> float:
        """Calculate hours remaining based on quote."""
        return max(0, self.hours_quoted - self.hours_worked)
    
    @property
    def progress_percentage(self) -> float:
        """Calculate project progress as percentage."""
        if self.hours_quoted == 0:
            return 0.0
        return min(100.0, (self.hours_worked / self.hours_quoted) * 100)


@dataclass
class Client:
    """Represents a client."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    projects: List[Project] = field(default_factory=list)
    
    @property
    def total_hours_worked(self) -> float:
        """Calculate total hours worked across all projects."""
        return sum(project.hours_worked for project in self.projects)
    
    @property
    def active_projects(self) -> List[Project]:
        """Get projects that haven't exceeded their quoted hours."""
        return [p for p in self.projects if p.hours_remaining > 0]