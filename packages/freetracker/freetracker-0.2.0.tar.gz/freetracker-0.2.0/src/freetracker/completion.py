"""Tab completion functionality for freetracker."""

import readline
from typing import List, Optional, Callable
from rich.prompt import Prompt
from rich.console import Console

console = Console()


class TabCompleter:
    """A generic tab completer for names."""
    
    def __init__(self, choices: List[str]):
        """Initialize with a list of choices for completion."""
        self.choices = [choice.lower() for choice in choices]
        self.original_choices = choices  # Keep original case
        self.matches = []
    
    def complete(self, text: str, state: int) -> Optional[str]:
        """Complete function for readline."""
        if state == 0:
            # Generate matches
            if text:
                self.matches = [
                    original for choice, original in zip(self.choices, self.original_choices)
                    if choice.startswith(text.lower())
                ]
            else:
                self.matches = self.original_choices[:]
        
        try:
            return self.matches[state]
        except IndexError:
            return None


def prompt_with_completion(prompt_text: str, choices: List[str], default: str = "") -> str:
    """Prompt for input with tab completion and index selection."""
    if not choices:
        # Fall back to regular prompt if no choices
        return Prompt.ask(prompt_text, default=default)
    
    # Set up tab completion
    completer = TabCompleter(choices)
    readline.set_completer(completer.complete)
    readline.parse_and_bind("tab: complete")
    
    # Display available choices with indices
    if len(choices) <= 10:  # Only show if not too many
        choices_str = ", ".join(f"[cyan]{i+1}. {choice}[/cyan]" for i, choice in enumerate(choices))
        console.print(f"[dim]Available: {choices_str}[/dim]")
    else:
        console.print(f"[dim]Available choices: {len(choices)} items (use tab to complete or enter a number)[/dim]")
    
    console.print(f"[dim]Enter a name or index (1-{len(choices)})[/dim]")
    
    try:
        # Get input with readline (enables tab completion)
        if default:
            result = input(f"{prompt_text} [{default}]: ").strip()
            result = result if result else default
        else:
            result = input(f"{prompt_text}: ").strip()
        
        # Check if input is a number (index)
        try:
            index = int(result)
            if 1 <= index <= len(choices):
                return choices[index - 1]
            else:
                console.print(f"[red]Invalid index. Please enter a number between 1 and {len(choices)}[/red]")
                return prompt_with_completion(prompt_text, choices, default)
        except ValueError:
            # Not a number, treat as name
            return result
            
    except (EOFError, KeyboardInterrupt):
        console.print("\n[red]Cancelled[/red]")
        raise
    finally:
        # Clean up readline
        readline.set_completer(None)


def prompt_client_name(clients: List[str], prompt_text: str = "Client name") -> str:
    """Prompt for client name with tab completion."""
    return prompt_with_completion(prompt_text, clients)


def prompt_project_name(projects: List[str], prompt_text: str = "Project name") -> str:
    """Prompt for project name with tab completion."""
    return prompt_with_completion(prompt_text, projects)