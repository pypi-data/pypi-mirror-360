"""
File operations module for intelligent file management.
"""

import os
import shutil
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm, Prompt
from rich.panel import Panel

from .file_analyzer import FileAnalyzer, FileInfo, FileCategory
from .llm_resolver import LLMResolver
from .emergency_undo import file_logger
from .file_context import file_context, get_context_for_query, update_context_after_operation, clear_context_if_new_operation

console = Console()

@dataclass
class FileOperation:
    """Represents a file operation to be performed."""
    operation: str  # create, move, copy, delete, organize
    source_path: Optional[Path]
    target_path: Optional[Path]
    content: Optional[str] = None
    reason: str = ""
    confidence: float = 0.0

@dataclass
class OperationResult:
    """Result of a file operation."""
    success: bool
    operation: FileOperation
    message: str
    files_affected: List[Path]

class FileOperationManager:
    """Manages intelligent file operations using AI."""
    
    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.analyzer = FileAnalyzer(verbose=verbose)
        self.llm_resolver = LLMResolver(verbose=verbose)
        self.current_directory = Path.cwd()
    
    def execute_file_command(self, command: str) -> List[OperationResult]:
        """Execute a natural language file operation command."""
        if self.verbose:
            console.print(f"[blue]Processing file command: {command}[/blue]")
        
        # Check if this is a listing command
        if self._is_list_command(command):
            return self._handle_list_command(command)
        
        # Check if we should clear context for new operations
        if clear_context_if_new_operation(command):
            if self.verbose:
                console.print("[dim]Starting fresh file context[/dim]")
        
        # Parse the command intent
        operations = self._parse_file_command(command)
        
        if not operations:
            console.print("[yellow]Could not understand the file operation request[/yellow]")
            return []
        
        results = []
        
        # Show current context if relevant
        if file_context.has_active_files() and self.verbose:
            file_context.show_context(verbose=False)
        
        # Show preview of operations
        if operations:
            self._show_operation_preview(operations)
            
            # Confirm dangerous operations
            if not self.dry_run and self._has_dangerous_operations(operations):
                if not Confirm.ask("[red]Some operations are potentially destructive. Continue?"):
                    console.print("[yellow]Operations cancelled by user[/yellow]")
                    return []
        
        # Execute operations
        files_affected = []
        for operation in operations:
            result = self._execute_operation(operation)
            results.append(result)
            
            if result.success:
                files_affected.extend(result.files_affected)
            
            if self.verbose:
                status = "✅" if result.success else "❌"
                console.print(f"{status} {result.message}")
        
        # Update context with affected files
        if files_affected:
            operation_type = operations[0].operation if operations else "unknown"
            update_context_after_operation(files_affected, command, operation_type)
        
        return results
    
    def _is_list_command(self, command: str) -> bool:
        """Check if this is a file listing command."""
        list_keywords = ["list", "show", "find", "display", "print"]
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in list_keywords)
    
    def _handle_list_command(self, command: str) -> List[OperationResult]:
        """Handle file listing commands."""
        # Analyze current directory
        files = self.analyzer.analyze_directory(self.current_directory)
        
        # Find matching files
        if "context" in command.lower() or "active" in command.lower():
            # Show current context
            file_context.show_context(verbose=self.verbose)
            return []
        
        # Find files based on query
        matching_files = self.analyzer.find_files_by_query(files, command)
        
        if not matching_files:
            if self.verbose:
                console.print(f"[blue]Analyzed {len(files)} files for query: {command}[/blue]")
                # Show a few example files for debugging
                if files:
                    console.print("[dim]Sample files analyzed:[/dim]")
                    for i, f in enumerate(files[:5]):
                        console.print(f"[dim]  {f.name} - {f.purpose}[/dim]")
                    if len(files) > 5:
                        console.print(f"[dim]  ... and {len(files) - 5} more[/dim]")
            console.print(f"[yellow]No files found matching: {command}[/yellow]")
            return []
        
        # Display the files
        self._display_file_list(matching_files, command)
        
        # Update context with listed files
        file_paths = [f.path for f in matching_files]
        update_context_after_operation(file_paths, command, "list")
        
        # Return success result
        return [OperationResult(
            success=True,
            operation=FileOperation("list", None, None, reason=f"Listed {len(matching_files)} files"),
            message=f"Found {len(matching_files)} files",
            files_affected=file_paths
        )]
    
    def _display_file_list(self, files: List[FileInfo], query: str):
        """Display a list of files in a nice format."""
        console.print(f"[blue]📁 Files matching '{query}' ({len(files)} found):[/blue]")
        console.print()
        
        # Group files by category for better display
        by_category = {}
        for file_info in files:
            category = file_info.category.value
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(file_info)
        
        # Display each category
        for category, category_files in by_category.items():
            if len(by_category) > 1:  # Only show category headers if multiple categories
                console.print(f"[dim]{category.title()} files:[/dim]")
            
            table = Table(show_header=False, box=None, padding=(0, 1))
            table.add_column("Icon", style="blue", width=3)
            table.add_column("Name", style="white")
            table.add_column("Purpose", style="dim")
            table.add_column("Size", style="green", justify="right")
            
            for file_info in category_files:
                # Choose icon based on file type
                if file_info.extension == '.py':
                    icon = "🐍"
                elif file_info.extension in ['.js', '.ts']:
                    icon = "📜"
                elif file_info.extension in ['.md', '.txt']:
                    icon = "📄"
                elif file_info.extension in ['.json', '.yaml', '.yml']:
                    icon = "⚙️"
                elif file_info.extension in ['.bat', '.sh']:
                    icon = "🔧"
                elif file_info.category == FileCategory.TEST:
                    icon = "🧪"
                else:
                    icon = "📄"
                
                # Format file size
                if file_info.size < 1024:
                    size_str = f"{file_info.size}B"
                elif file_info.size < 1024 * 1024:
                    size_str = f"{file_info.size // 1024}KB"
                else:
                    size_str = f"{file_info.size // (1024 * 1024)}MB"
                
                table.add_row(
                    icon,
                    file_info.name,
                    file_info.purpose,
                    size_str
                )
            
            console.print(table)
            if len(by_category) > 1:
                console.print()
        
        console.print(f"[dim]💡 These files are now in your active context. Use commands like 'move files to folder' to work with them.[/dim]")
        console.print()
    
    def _parse_file_command(self, command: str) -> List[FileOperation]:
        """Parse natural language command into file operations."""
        command_lower = command.lower()
        operations = []
        
        # Check if command references contextual files
        context_files = get_context_for_query(command)
        
        if context_files:
            if self.verbose:
                console.print(f"[blue]Using {len(context_files)} files from context[/blue]")
            # Convert Path objects to FileInfo objects
            files = [self.analyzer.analyze_file(f) for f in context_files if f.exists()]
        else:
            # Analyze current directory
            files = self.analyzer.analyze_directory(self.current_directory)
        
        # Create operations
        if "create" in command_lower and "folder" in command_lower:
            operations.extend(self._parse_create_folder_command(command, files))
        elif "create" in command_lower and "file" in command_lower:
            operations.extend(self._parse_create_file_command(command, files))
        elif "move" in command_lower or "organize" in command_lower:
            operations.extend(self._parse_move_command(command, files))
        elif "delete" in command_lower or "remove" in command_lower:
            operations.extend(self._parse_delete_command(command, files))
        elif "copy" in command_lower:
            operations.extend(self._parse_copy_command(command, files))
        else:
            # Use LLM for complex commands
            operations.extend(self._parse_with_llm(command, files))
        
        return operations
    
    def _parse_create_folder_command(self, command: str, files: List[FileInfo]) -> List[FileOperation]:
        """Parse folder creation commands."""
        operations = []
        
        # Extract folder names from command
        words = command.split()
        folder_names = []
        
        # Look for quoted folder names
        import re
        quoted_names = re.findall(r'["\']([^"\']+)["\']', command)
        folder_names.extend(quoted_names)
        
        # Look for common folder patterns
        common_folders = {
            'test': 'tests',
            'testing': 'tests', 
            'doc': 'docs',
            'documentation': 'docs',
            'script': 'scripts',
            'config': 'config',
            'data': 'data',
            'asset': 'assets',
            'image': 'images',
            'source': 'src',
            'build': 'build',
            'temp': 'temp',
        }
        
        for word in words:
            word_lower = word.lower().strip('.,!?')
            if word_lower in common_folders and common_folders[word_lower] not in folder_names:
                folder_names.append(common_folders[word_lower])
        
        # Create operations
        for folder_name in folder_names:
            target_path = self.current_directory / folder_name
            operations.append(FileOperation(
                operation="create",
                source_path=None,
                target_path=target_path,
                reason=f"Create {folder_name} folder as requested",
                confidence=0.8
            ))
        
        return operations
    
    def _parse_create_file_command(self, command: str, files: List[FileInfo]) -> List[FileOperation]:
        """Parse file creation commands."""
        operations = []
        
        # Extract file names and content from command
        import re
        
        # Look for file names in quotes
        file_names = re.findall(r'["\']([^"\']+\.[a-zA-Z0-9]+)["\']', command)
        
        # Look for content after "with content" or similar
        content_match = re.search(r'(?:with content|containing|content:)[\s]*["\']([^"\']+)["\']', command, re.IGNORECASE)
        content = content_match.group(1) if content_match else ""
        
        # Create operations
        for file_name in file_names:
            target_path = self.current_directory / file_name
            operations.append(FileOperation(
                operation="create",
                source_path=None,
                target_path=target_path,
                content=content,
                reason=f"Create {file_name} as requested",
                confidence=0.8
            ))
        
        return operations
    
    def _parse_move_command(self, command: str, files: List[FileInfo]) -> List[FileOperation]:
        """Parse move/organize commands."""
        operations = []
        
        # Find files to move based on command
        target_files = self.analyzer.find_files_by_query(files, command)
        
        if not target_files:
            return operations
        
        # Determine target directory
        target_dir = self._determine_target_directory(command, target_files)
        
        if not target_dir:
            return operations
        
        # Create target directory if needed
        if not target_dir.exists():
            operations.append(FileOperation(
                operation="create",
                source_path=None,
                target_path=target_dir,
                reason=f"Create target directory {target_dir.name}",
                confidence=0.9
            ))
        
        # Create move operations
        for file_info in target_files:
            target_path = target_dir / file_info.name
            operations.append(FileOperation(
                operation="move",
                source_path=file_info.path,
                target_path=target_path,
                reason=f"Move {file_info.purpose.lower()} to {target_dir.name} folder",
                confidence=file_info.confidence
            ))
        
        return operations
    
    def _parse_delete_command(self, command: str, files: List[FileInfo]) -> List[FileOperation]:
        """Parse delete/remove commands."""
        operations = []
        
        # Find files to delete
        target_files = self.analyzer.find_files_by_query(files, command)
        
        # Only allow deletion of safe file types by default
        safe_to_delete = [FileCategory.TEMPORARY, FileCategory.BUILD]
        
        for file_info in target_files:
            if file_info.category in safe_to_delete or "temp" in command.lower() or "build" in command.lower():
                operations.append(FileOperation(
                    operation="delete",
                    source_path=file_info.path,
                    target_path=None,
                    reason=f"Delete {file_info.purpose.lower()}",
                    confidence=file_info.confidence
                ))
        
        return operations
    
    def _parse_copy_command(self, command: str, files: List[FileInfo]) -> List[FileOperation]:
        """Parse copy commands."""
        operations = []
        
        # Find files to copy
        target_files = self.analyzer.find_files_by_query(files, command)
        
        # Determine target directory
        target_dir = self._determine_target_directory(command, target_files)
        
        if not target_dir:
            return operations
        
        # Create copy operations
        for file_info in target_files:
            target_path = target_dir / file_info.name
            operations.append(FileOperation(
                operation="copy",
                source_path=file_info.path,
                target_path=target_path,
                reason=f"Copy {file_info.purpose.lower()} to {target_dir.name}",
                confidence=file_info.confidence
            ))
        
        return operations
    
    def _parse_with_llm(self, command: str, files: List[FileInfo]) -> List[FileOperation]:
        """Use LLM to parse complex file operation commands."""
        # Prepare context for LLM
        file_list = []
        for file_info in files:
            file_list.append({
                "name": file_info.name,
                "path": str(file_info.path),
                "category": file_info.category.value,
                "purpose": file_info.purpose
            })
        
        prompt = f"""You are a file management assistant. Analyze this command and the current files to suggest file operations.

Command: "{command}"

Current files:
{json.dumps(file_list[:20], indent=2)}

Respond with JSON containing an array of operations:
{{
  "operations": [
    {{
      "operation": "move|copy|delete|create",
      "source_path": "path/to/source/file" or null,
      "target_path": "path/to/target/location",
      "content": "file content" or null,
      "reason": "explanation of why this operation is needed",
      "confidence": 0.9
    }}
  ]
}}

Only suggest safe operations. For destructive operations like delete, only suggest removing temporary or build files."""
        
        try:
            # Use LLM to get operations
            if self.llm_resolver.model == "local":
                response = self.llm_resolver._resolve_with_local_llm(prompt)
                # Parse LLM response to extract operations
                return self._parse_llm_operations_response(response, files)
            else:
                # Fallback to heuristic parsing
                return []
        except Exception as e:
            if self.verbose:
                console.print(f"[yellow]LLM parsing failed: {e}[/yellow]")
            return []
    
    def _parse_llm_operations_response(self, response: List[str], files: List[FileInfo]) -> List[FileOperation]:
        """Parse LLM response into file operations."""
        operations = []
        
        # Try to extract JSON from response
        if response:
            response_text = ' '.join(response) if isinstance(response, list) else str(response)
            
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    if "operations" in data:
                        for op_data in data["operations"]:
                            source_path = Path(op_data["source_path"]) if op_data.get("source_path") else None
                            target_path = Path(op_data["target_path"]) if op_data.get("target_path") else None
                            
                            operations.append(FileOperation(
                                operation=op_data["operation"],
                                source_path=source_path,
                                target_path=target_path,
                                content=op_data.get("content"),
                                reason=op_data.get("reason", ""),
                                confidence=op_data.get("confidence", 0.5)
                            ))
                except json.JSONDecodeError:
                    pass
        
        return operations
    
    def _determine_target_directory(self, command: str, files: List[FileInfo]) -> Optional[Path]:
        """Determine target directory from command and file types."""
        command_lower = command.lower()
        
        # Extract directory names from command
        import re
        quoted_dirs = re.findall(r'["\']([^"\']+)["\']', command)
        
        # Common directory mappings
        dir_mappings = {
            'test': 'tests',
            'testing': 'tests',
            'doc': 'docs', 
            'documentation': 'docs',
            'script': 'scripts',
            'config': 'config',
            'configuration': 'config',
            'data': 'data',
            'asset': 'assets',
            'image': 'images',
            'temp': 'temp',
            'temporary': 'temp',
            'build': 'build',
        }
        
        # Check for explicit directory in command
        for quoted_dir in quoted_dirs:
            return self.current_directory / quoted_dir
        
        # Infer directory from file types
        if files:
            primary_category = files[0].category
            
            if primary_category == FileCategory.TEST:
                return self.current_directory / "tests"
            elif primary_category == FileCategory.DOCUMENTATION:
                return self.current_directory / "docs"
            elif primary_category == FileCategory.CONFIG:
                return self.current_directory / "config"
            elif primary_category == FileCategory.SCRIPT:
                return self.current_directory / "scripts"
            elif primary_category == FileCategory.DATA:
                return self.current_directory / "data"
            elif primary_category == FileCategory.ASSET:
                return self.current_directory / "assets"
            elif primary_category == FileCategory.TEMPORARY:
                return self.current_directory / "temp"
        
        # Check command for directory hints
        for keyword, directory in dir_mappings.items():
            if keyword in command_lower:
                return self.current_directory / directory
        
        return None
    
    def _execute_operation(self, operation: FileOperation) -> OperationResult:
        """Execute a single file operation."""
        try:
            if self.dry_run:
                return OperationResult(
                    success=True,
                    operation=operation,
                    message=f"[DRY RUN] Would {operation.operation}: {operation.reason}",
                    files_affected=[operation.source_path] if operation.source_path else [operation.target_path]
                )
            
            if operation.operation == "create":
                return self._create_operation(operation)
            elif operation.operation == "move":
                return self._move_operation(operation)
            elif operation.operation == "copy":
                return self._copy_operation(operation)
            elif operation.operation == "delete":
                return self._delete_operation(operation)
            else:
                return OperationResult(
                    success=False,
                    operation=operation,
                    message=f"Unknown operation: {operation.operation}",
                    files_affected=[]
                )
        
        except Exception as e:
            return OperationResult(
                success=False,
                operation=operation,
                message=f"Error: {str(e)}",
                files_affected=[]
            )
    
    def _create_operation(self, operation: FileOperation) -> OperationResult:
        """Execute create operation."""
        target_path = operation.target_path
        
        if target_path.exists():
            return OperationResult(
                success=False,
                operation=operation,
                message=f"Path already exists: {target_path}",
                files_affected=[]
            )
        
        if target_path.suffix:  # It's a file
            target_path.parent.mkdir(parents=True, exist_ok=True)
            content = operation.content or ""
            target_path.write_text(content, encoding='utf-8')
            message = f"Created file: {target_path}"
            
            # For file creation, immediately update context to this single file
            file_context.set_active_files([target_path], f"Created {target_path.name}", "create")
            
        else:  # It's a directory
            target_path.mkdir(parents=True, exist_ok=True)
            message = f"Created directory: {target_path}"
        
        return OperationResult(
            success=True,
            operation=operation,
            message=message,
            files_affected=[target_path]
        )
    
    def _move_operation(self, operation: FileOperation) -> OperationResult:
        """Execute move operation."""
        source_path = operation.source_path
        target_path = operation.target_path
        
        if not source_path.exists():
            return OperationResult(
                success=False,
                operation=operation,
                message=f"Source does not exist: {source_path}",
                files_affected=[]
            )
        
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Log the operation BEFORE executing
        file_logger.log_operation("move", str(source_path), str(target_path))
        
        shutil.move(str(source_path), str(target_path))
        
        return OperationResult(
            success=True,
            operation=operation,
            message=f"Moved {source_path.name} to {target_path.parent.name}/",
            files_affected=[source_path, target_path]
        )
    
    def _copy_operation(self, operation: FileOperation) -> OperationResult:
        """Execute copy operation."""
        source_path = operation.source_path
        target_path = operation.target_path
        
        if not source_path.exists():
            return OperationResult(
                success=False,
                operation=operation,
                message=f"Source does not exist: {source_path}",
                files_affected=[]
            )
        
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        if source_path.is_file():
            shutil.copy2(str(source_path), str(target_path))
        else:
            shutil.copytree(str(source_path), str(target_path))
        
        return OperationResult(
            success=True,
            operation=operation,
            message=f"Copied {source_path.name} to {target_path.parent.name}/",
            files_affected=[source_path, target_path]
        )
    
    def _delete_operation(self, operation: FileOperation) -> OperationResult:
        """Execute delete operation."""
        source_path = operation.source_path
        
        if not source_path.exists():
            return OperationResult(
                success=False,
                operation=operation,
                message=f"File does not exist: {source_path}",
                files_affected=[]
            )
        
        if source_path.is_file():
            source_path.unlink()
            message = f"Deleted file: {source_path.name}"
        else:
            shutil.rmtree(str(source_path))
            message = f"Deleted directory: {source_path.name}"
        
        return OperationResult(
            success=True,
            operation=operation,
            message=message,
            files_affected=[source_path]
        )
    
    def _show_operation_preview(self, operations: List[FileOperation]):
        """Show preview of operations to be performed."""
        if not operations:
            return
        
        # Show safety info
        console.print("[blue]🛡️  Safety: Automatically excluding system files, environments, and critical project files[/blue]")
        
        table = Table(title="📋 Planned File Operations")
        table.add_column("Operation", style="cyan")
        table.add_column("Source", style="yellow")
        table.add_column("Target", style="green")
        table.add_column("Reason", style="white")
        table.add_column("Confidence", style="blue")
        
        for operation in operations:
            source = str(operation.source_path.name) if operation.source_path else "—"
            target = str(operation.target_path.name) if operation.target_path else "—"
            confidence = f"{operation.confidence:.1%}"
            
            table.add_row(
                operation.operation.upper(),
                source,
                target,
                operation.reason,
                confidence
            )
        
        console.print(table)
        console.print()
        
        # Show what's being excluded if verbose
        if self.verbose:
            excluded_count = self._count_excluded_files()
            if excluded_count > 0:
                console.print(f"[dim]ℹ️  {excluded_count} files excluded for safety (environments, system files, etc.)[/dim]")
                console.print()
    
    def _count_excluded_files(self) -> int:
        """Count how many files are excluded for safety."""
        try:
            all_files = 0
            excluded_files = 0
            
            for file_path in self.current_directory.rglob('*'):
                if file_path.is_file():
                    all_files += 1
                    if not self.analyzer._should_include_file(file_path):
                        excluded_files += 1
            
            return excluded_files
        except Exception:
            return 0
    
    def _has_dangerous_operations(self, operations: List[FileOperation]) -> bool:
        """Check if operations contain potentially dangerous actions."""
        dangerous_ops = {"delete"}
        return any(op.operation in dangerous_ops for op in operations)