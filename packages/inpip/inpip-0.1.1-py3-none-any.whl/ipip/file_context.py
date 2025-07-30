"""
File context system for ipip - remembers active files for conversational operations.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from rich.console import Console
from rich.table import Table

console = Console()

@dataclass
class FileContext:
    """Represents the current file context."""
    active_files: List[str]
    last_operation: str
    timestamp: str
    operation_type: str  # list, create, move, etc.
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FileContext':
        return cls(**data)

class FileContextManager:
    """Manages file context for conversational operations."""
    
    def __init__(self):
        self.context_file = Path.home() / ".ipip_file_context.json"
        self.current_context: Optional[FileContext] = None
        self.load_context()
    
    def load_context(self):
        """Load the current file context from disk."""
        try:
            if self.context_file.exists():
                with open(self.context_file, 'r') as f:
                    data = json.load(f)
                    self.current_context = FileContext.from_dict(data)
        except Exception:
            self.current_context = None
    
    def save_context(self):
        """Save the current file context to disk."""
        try:
            if self.current_context:
                with open(self.context_file, 'w') as f:
                    json.dump(self.current_context.to_dict(), f, indent=2)
        except Exception:
            pass  # Fail silently for context saving
    
    def set_active_files(self, files: List[Path], operation: str, operation_type: str):
        """Set the currently active files."""
        file_paths = [str(f) for f in files]
        self.current_context = FileContext(
            active_files=file_paths,
            last_operation=operation,
            timestamp=datetime.now().isoformat(),
            operation_type=operation_type
        )
        self.save_context()
    
    def get_active_files(self) -> List[Path]:
        """Get the currently active files as Path objects."""
        if not self.current_context:
            return []
        
        # Filter to only existing files
        existing_files = []
        for file_str in self.current_context.active_files:
            file_path = Path(file_str)
            if file_path.exists():
                existing_files.append(file_path)
        
        return existing_files
    
    def add_file_to_context(self, file_path: Path, operation: str):
        """Add a single file to the current context."""
        if not self.current_context:
            self.set_active_files([file_path], operation, "create")
        else:
            # Add to existing context
            if str(file_path) not in self.current_context.active_files:
                self.current_context.active_files.append(str(file_path))
                self.current_context.last_operation = operation
                self.current_context.timestamp = datetime.now().isoformat()
                self.save_context()
    
    def clear_context(self):
        """Clear the current file context."""
        self.current_context = None
        if self.context_file.exists():
            self.context_file.unlink()
    
    def has_active_files(self) -> bool:
        """Check if there are any active files in context."""
        return bool(self.get_active_files())
    
    def show_context(self, verbose: bool = False):
        """Display the current file context."""
        active_files = self.get_active_files()
        
        if not active_files:
            console.print("[dim]No active file context[/dim]")
            return
        
        console.print(f"[blue]📁 Active file context ({len(active_files)} files):[/blue]")
        
        if verbose and self.current_context:
            console.print(f"[dim]Last operation: {self.current_context.last_operation}[/dim]")
            console.print(f"[dim]Operation type: {self.current_context.operation_type}[/dim]")
            console.print(f"[dim]Timestamp: {self.current_context.timestamp}[/dim]")
            console.print()
        
        # Show files in a table
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Icon", style="blue")
        table.add_column("File", style="white")
        table.add_column("Status", style="green")
        
        for file_path in active_files:
            if file_path.is_file():
                icon = "📄"
                status = "exists"
            elif file_path.is_dir():
                icon = "📁"
                status = "directory"
            else:
                icon = "❓"
                status = "missing"
            
            table.add_row(icon, str(file_path.name), status)
        
        console.print(table)
        console.print()
    
    def get_context_summary(self) -> str:
        """Get a summary of the current context for LLM prompts."""
        if not self.current_context:
            return "No active file context."
        
        active_files = self.get_active_files()
        if not active_files:
            return "No active files in context."
        
        file_names = [f.name for f in active_files]
        return f"Active files: {', '.join(file_names)} (from {self.current_context.operation_type}: {self.current_context.last_operation})"

# Global context manager
file_context = FileContextManager()

def get_context_for_query(query: str) -> List[Path]:
    """Get contextual files for a query that doesn't specify files."""
    # Check for context-dependent commands
    context_commands = [
        "move files", "copy files", "delete files",
        "move them", "copy them", "delete them",
        "organize files", "these files", "those files",
        "the files", "current files", "active files"
    ]
    
    query_lower = query.lower()
    if any(cmd in query_lower for cmd in context_commands):
        return file_context.get_active_files()
    
    return []

def update_context_after_operation(files: List[Path], operation: str, operation_type: str):
    """Update context after a file operation."""
    if files:
        file_context.set_active_files(files, operation, operation_type)

def clear_context_if_new_operation(query: str) -> bool:
    """Clear context if this is a new type of operation."""
    # Commands that start fresh context
    fresh_commands = [
        "list", "find", "show", "search",
        "create file", "create folder", "create directory"
    ]
    
    query_lower = query.lower()
    for cmd in fresh_commands:
        if cmd in query_lower:
            return True
    
    return False