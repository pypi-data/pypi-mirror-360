"""
Emergency undo functionality for file operations.
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict
from rich.console import Console
from datetime import datetime

console = Console()

class FileOperationLogger:
    """Logs all file operations for potential undo."""
    
    def __init__(self):
        self.log_file = Path.home() / ".ipip_file_operations.json"
        self.operations = []
    
    def log_operation(self, operation: str, source: str, target: str):
        """Log a file operation."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "source": source,
            "target": target
        }
        self.operations.append(entry)
        self._save_log()
    
    def _save_log(self):
        """Save operations log to file."""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.operations, f, indent=2)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not save operation log: {e}[/yellow]")
    
    def load_recent_operations(self, hours: int = 1) -> List[Dict]:
        """Load recent operations for potential undo."""
        try:
            if not self.log_file.exists():
                return []
            
            with open(self.log_file, 'r') as f:
                all_operations = json.load(f)
            
            # Filter recent operations
            from datetime import timedelta
            cutoff = datetime.now() - timedelta(hours=hours)
            
            recent = []
            for op in all_operations:
                op_time = datetime.fromisoformat(op["timestamp"])
                if op_time > cutoff:
                    recent.append(op)
            
            return recent
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load operation log: {e}[/yellow]")
            return []
    
    def undo_last_operations(self, count: int = 10) -> bool:
        """Attempt to undo the last N operations."""
        recent_ops = self.load_recent_operations(hours=24)
        
        if not recent_ops:
            console.print("[yellow]No recent operations to undo[/yellow]")
            return False
        
        # Show what will be undone
        console.print(f"[blue]Will attempt to undo last {min(count, len(recent_ops))} operations:[/blue]")
        
        ops_to_undo = recent_ops[-count:]
        for i, op in enumerate(reversed(ops_to_undo)):
            console.print(f"  {i+1}. {op['operation']}: {op['source']} → {op['target']}")
        
        from rich.prompt import Confirm
        if not Confirm.ask("Proceed with undo?"):
            return False
        
        # Attempt to undo operations in reverse order
        success_count = 0
        for op in reversed(ops_to_undo):
            try:
                if op["operation"] == "move":
                    # Move back from target to source
                    target_path = Path(op["target"])
                    source_path = Path(op["source"])
                    if target_path.exists():
                        shutil.move(str(target_path), str(source_path))
                        console.print(f"[green]✅ Moved {target_path.name} back to {source_path.parent}/[/green]")
                        success_count += 1
                    else:
                        console.print(f"[yellow]⚠️  {target_path} not found[/yellow]")
                
                elif op["operation"] == "copy":
                    # Delete the copy
                    target_path = Path(op["target"])
                    if target_path.exists():
                        if target_path.is_file():
                            target_path.unlink()
                        else:
                            shutil.rmtree(str(target_path))
                        console.print(f"[green]✅ Removed copy: {target_path.name}[/green]")
                        success_count += 1
                
                elif op["operation"] == "create":
                    # Delete created files/folders
                    target_path = Path(op["target"])
                    if target_path.exists():
                        if target_path.is_file():
                            target_path.unlink()
                        else:
                            shutil.rmtree(str(target_path))
                        console.print(f"[green]✅ Removed created: {target_path.name}[/green]")
                        success_count += 1
                
            except Exception as e:
                console.print(f"[red]❌ Failed to undo {op['operation']}: {e}[/red]")
        
        console.print(f"\n[blue]Undo complete: {success_count}/{len(ops_to_undo)} operations reversed[/blue]")
        return success_count > 0

# Global logger instance
file_logger = FileOperationLogger()

def emergency_undo():
    """Emergency undo function that can be called directly."""
    console.print("[red]🚨 EMERGENCY UNDO MODE 🚨[/red]")
    console.print("This will attempt to reverse recent file operations.")
    
    file_logger.undo_last_operations(20)