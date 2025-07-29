# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**freetracker** - A CLI application for freelancers to track working hours per client/project.

- **Language**: Python
- **Type**: Command-line interface (CLI) application
- **License**: MIT License (Copyright 2025 Jason (Janghyup) Sohn)
- **Status**: Fully functional CLI application with all core features implemented

## Development Setup

### Technology Stack
- **Package Manager**: `uv` - Fast Python package and project manager
- **CLI Framework**: `click` - Creating command-line interfaces
- **UI Library**: `rich` - Rich text and beautiful formatting in the terminal
- **Database**: `tinydb` - Lightweight document-oriented database for local storage
- **Build System**: `hatchling` - Modern Python packaging

### Project Structure
```
freetracker/
├── src/
│   └── freetracker/
│       ├── __init__.py     # Package initialization
│       ├── cli.py          # CLI entry point using Click
│       ├── models.py       # Data models for clients/projects/time entries
│       ├── storage.py      # TinyDB persistence layer
│       ├── ui.py           # Rich-based UI components
│       └── completion.py   # Tab completion functionality
├── tests/
│   └── test_*.py
├── pyproject.toml          # Project configuration and dependencies
├── uv.lock                 # Locked dependencies
└── README.md
```

### Development Commands
```bash
# Install dependencies
uv sync

# Set up development database (to avoid interfering with user data)
export FREETRACKER_DB_PATH=/tmp/freetracker_dev.json

# Run the CLI during development
uv run freetracker

# Add a new dependency
uv add <package-name>

# Run tests (when implemented)
uv run pytest

# Build the package
uv build

# Publish to PyPI (requires PyPI API token)
uv publish
```

### Development Best Practices

1. **Always use a development database**: Set `FREETRACKER_DB_PATH` to a temporary location during development to avoid interfering with actual user data.
   ```bash
   export FREETRACKER_DB_PATH=/tmp/freetracker_dev.json
   ```

2. **Test with fresh data**: Delete the development database to start fresh:
   ```bash
   rm /tmp/freetracker_dev.json
   ```

### Testing Framework
Use `pytest` for testing, as indicated by the `.gitignore` file's references to `.pytest_cache/`.

## Features Implemented

### Core Functionality
- **Client Management**: Full CRUD operations (add, list, edit, delete)
- **Project Management**: Projects with hours quoted, due dates, and client associations
- **Time Tracking**: Start/stop timers with automatic time calculation
- **Manual Time Entry**: Add hours manually for forgotten sessions
- **Tab Completion**: Auto-complete client and project names using readline
- **Progress Reporting**: Visual progress bars showing project completion
- **Data Export**: CSV export with customizable output paths

### Advanced Features
- **Environment Variables**: `FREETRACKER_DB_PATH` for custom database locations
- **Active Timer Notifications**: Shows current timer on every command
- **Rich Terminal UI**: Beautiful tables, progress bars, and formatted output
- **Name-based Operations**: Use human-readable names instead of IDs
- **Case Insensitive**: All name matching works regardless of case
- **Error Handling**: Comprehensive validation and user-friendly error messages

### Command Overview
```bash
# Client management
freetracker client add/list/edit/delete

# Project management
freetracker project add/list/edit/delete

# Time tracking
freetracker start/stop/status/add

# Reporting and logs
freetracker report [--csv] [--output file]
freetracker log [project_name]
```

## Important Notes

1. **Database Environment**: Always set `FREETRACKER_DB_PATH` during development to avoid interfering with user data.
2. **Tab Completion**: The app uses Python's readline module for interactive tab completion.
3. **Name-based Interface**: All operations use human-readable names with tab completion rather than technical IDs.
4. **Progress Tracking**: Projects track quoted hours vs. actual hours with visual progress indicators.