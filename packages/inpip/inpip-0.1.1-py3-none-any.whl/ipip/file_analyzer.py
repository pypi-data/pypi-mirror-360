"""
File analysis module for intelligent file operations.
"""

import os
import re
import mimetypes
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.console import Console

class FileCategory(Enum):
    """Categories of files for organization."""
    TEST = "test"
    SOURCE = "source"
    CONFIG = "config"
    DOCUMENTATION = "documentation"
    DATA = "data"
    BUILD = "build"
    DEPENDENCY = "dependency"
    SCRIPT = "script"
    ASSET = "asset"
    TEMPORARY = "temporary"
    UNKNOWN = "unknown"

@dataclass
class FileInfo:
    """Information about a file."""
    path: Path
    name: str
    extension: str
    size: int
    category: FileCategory
    purpose: str
    confidence: float
    related_files: List[str]

class FileAnalyzer:
    """Analyzes files to determine their purpose and category."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.console = Console()
        self.test_patterns = [
            r'test_.*\.py$',
            r'.*_test\.py$',
            r'.*\.test\.js$',
            r'test.*\.js$',
            r'.*_spec\.rb$',
            r'.*\.spec\.ts$',
            r'.*test.*',
        ]
        
        self.config_patterns = [
            r'.*\.json$',
            r'.*\.yaml$',
            r'.*\.yml$',
            r'.*\.toml$',
            r'.*\.ini$',
            r'.*\.cfg$',
            r'.*\.conf$',
            r'.*config.*',
            r'\.env.*',
            r'Dockerfile.*',
            r'docker-compose.*',
        ]
        
        self.doc_patterns = [
            r'.*\.md$',
            r'.*\.rst$',
            r'.*\.txt$',
            r'README.*',
            r'CHANGELOG.*',
            r'LICENSE.*',
            r'CONTRIBUTING.*',
            r'.*\.pdf$',
            r'docs/.*',
        ]
        
        self.build_patterns = [
            r'build/.*',
            r'dist/.*',
            r'target/.*',
            r'out/.*',
            r'.*\.o$',
            r'.*\.obj$',
            r'.*\.exe$',
            r'.*\.dll$',
            r'.*\.so$',
            r'.*\.pyc$',
            r'__pycache__/.*',
            r'node_modules/.*',
        ]
        
        self.script_patterns = [
            r'.*\.sh$',
            r'.*\.bat$',
            r'.*\.ps1$',
            r'.*\.py$',
            r'.*\.js$',
            r'.*\.ts$',
            r'scripts/.*',
            r'bin/.*',
        ]
        
        self.data_patterns = [
            r'.*\.csv$',
            r'.*\.json$',
            r'.*\.xml$',
            r'.*\.sql$',
            r'.*\.db$',
            r'.*\.sqlite$',
            r'data/.*',
            r'datasets/.*',
        ]
        
        self.asset_patterns = [
            r'.*\.png$',
            r'.*\.jpg$',
            r'.*\.jpeg$',
            r'.*\.gif$',
            r'.*\.svg$',
            r'.*\.ico$',
            r'.*\.css$',
            r'.*\.scss$',
            r'.*\.less$',
            r'assets/.*',
            r'static/.*',
            r'public/.*',
        ]
        
        self.temp_patterns = [
            r'\.tmp$',
            r'\.temp$',
            r'.*~$',
            r'\.bak$',
            r'\.backup$',
            r'temp/.*',
            r'tmp/.*',
        ]
    
    def analyze_file(self, file_path: Path) -> FileInfo:
        """Analyze a single file to determine its purpose and category."""
        name = file_path.name
        extension = file_path.suffix.lower()
        
        try:
            size = file_path.stat().st_size
        except (OSError, FileNotFoundError):
            size = 0
        
        category, purpose, confidence = self._categorize_file(file_path)
        related_files = self._find_related_files(file_path)
        
        return FileInfo(
            path=file_path,
            name=name,
            extension=extension,
            size=size,
            category=category,
            purpose=purpose,
            confidence=confidence,
            related_files=related_files
        )
    
    def analyze_directory(self, directory: Path, recursive: bool = True) -> List[FileInfo]:
        """Analyze all files in a directory, excluding system and sensitive files."""
        files = []
        
        # First pass: collect all file paths (for progress tracking)
        if self.verbose:
            self.console.print(f"[blue]📁 Scanning directory: {directory}[/blue]")
        
        all_file_paths = []
        scanned_count = 0
        
        # Show scanning progress for large directories
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TextColumn("[cyan]{task.completed}[/cyan] files found"),
            TimeElapsedColumn(),
            console=self.console,
            transient=True
        ) as scan_progress:
            
            scan_task = scan_progress.add_task("[cyan]Scanning...", total=None)
            
            if recursive:
                for file_path in directory.rglob('*'):
                    scanned_count += 1
                    if scanned_count % 100 == 0:  # Update every 100 files
                        scan_progress.update(scan_task, completed=len(all_file_paths), description=f"[cyan]Scanning... ({scanned_count} checked)")
                    
                    if file_path.is_file() and self._should_include_file(file_path):
                        all_file_paths.append(file_path)
            else:
                for file_path in directory.iterdir():
                    scanned_count += 1
                    scan_progress.update(scan_task, completed=len(all_file_paths))
                    
                    if file_path.is_file() and self._should_include_file(file_path):
                        all_file_paths.append(file_path)
            
            scan_progress.update(scan_task, completed=len(all_file_paths), description=f"[cyan]Scan complete")
        
        # Second pass: analyze files with progress bar
        if len(all_file_paths) > 10 or self.verbose:  # Show progress for 10+ files or in verbose mode
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TextColumn("files"),
                TimeElapsedColumn(),
                console=self.console,
                transient=True  # Remove progress bar when complete
            ) as progress:
                
                task = progress.add_task(
                    f"[cyan]Analyzing files...", 
                    total=len(all_file_paths)
                )
                
                for file_path in all_file_paths:
                    files.append(self.analyze_file(file_path))
                    progress.advance(task)
                    
                    # Update description with current file (for very verbose mode)
                    if self.verbose and len(all_file_paths) > 50:
                        progress.update(task, description=f"[cyan]Analyzing: {file_path.name[:30]}...")
        else:
            # For small numbers of files, just process without progress bar
            for file_path in all_file_paths:
                files.append(self.analyze_file(file_path))
        
        if self.verbose:
            self.console.print(f"[green]✅ Analyzed {len(files)} files[/green]")
        
        return files
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Check if a file should be included in analysis (excludes system/sensitive files)."""
        path_str = str(file_path).replace('\\', '/')
        path_parts = path_str.lower().split('/')
        file_name = file_path.name.lower()
        
        # CRITICAL EXCLUSIONS - Never touch these!
        
        # 1. Hidden files and directories (starting with .)
        for part in path_parts:
            if part.startswith('.') and part not in ['.', '..']:
                return False
        
        # 2. Virtual environment directories
        env_dirs = {
            'venv', '.venv', 'env', '.env', 'virtualenv', 
            'test_env', 'dev_env', 'prod_env', 'conda_env',
            'pipenv', '.pipenv', 'poetry_env', '.poetry'
        }
        for part in path_parts:
            if part in env_dirs:
                return False
        
        # 3. Version control and system directories
        system_dirs = {
            '.git', '.svn', '.hg', '.bzr',
            '__pycache__', '.pytest_cache', '.coverage',
            'node_modules', '.npm', '.yarn',
            '.cargo', 'target',  # Rust
            '.gradle', '.m2',    # Java
        }
        for part in path_parts:
            if part in system_dirs:
                return False
        
        # 4. IDE and editor directories
        ide_dirs = {
            '.vscode', '.idea', '.eclipse', '.netbeans',
            '.sublime-project', '.sublime-workspace',
            '.atom', '.brackets', '.emacs.d'
        }
        for part in path_parts:
            if part in ide_dirs:
                return False
        
        # 5. Build and distribution directories
        build_dirs = {
            'build', 'dist', 'target', 'out', 'bin', 'obj',
            '.tox', '.nox', 'htmlcov', 'coverage',
            'site-packages', 'lib64', 'include'
        }
        for part in path_parts:
            if part in build_dirs:
                return False
        
        # 6. OS-specific files
        os_files = {
            'thumbs.db', '.ds_store', 'desktop.ini',
            '.trash', '.recycle.bin', 'pagefile.sys'
        }
        if file_name in os_files:
            return False
        
        # 7. Critical project files that should never be moved
        critical_files = {
            'setup.py', 'pyproject.toml', 'setup.cfg',
            'requirements.txt', 'pipfile', 'pipfile.lock',
            'package.json', 'package-lock.json', 'yarn.lock',
            'makefile', 'dockerfile', 'docker-compose.yml',
            'cargo.toml', 'cargo.lock',
            '.gitignore', '.gitattributes',
            'license', 'license.txt', 'license.md',
            'readme.md', 'readme.txt', 'readme.rst'
        }
        if file_name in critical_files:
            return False
        
        # 8. Executable and binary files (be careful with these)
        dangerous_extensions = {
            '.exe', '.dll', '.so', '.dylib', '.bin',
            '.msi', '.pkg', '.deb', '.rpm', '.dmg'
        }
        if file_path.suffix.lower() in dangerous_extensions:
            return False
        
        # 9. Large data/media files (usually shouldn't be moved automatically)
        large_file_extensions = {
            '.iso', '.img', '.vmdk', '.vdi', '.ova',
            '.mp4', '.avi', '.mkv', '.mov', '.wmv',
            '.db', '.sqlite', '.mdb', '.accdb'
        }
        if file_path.suffix.lower() in large_file_extensions:
            return False
        
        # 10. Environment and config files that are location-specific
        env_config_files = {
            '.env', '.env.local', '.env.production',
            'config.ini', 'local_settings.py',
            'secrets.json', 'credentials.json'
        }
        if file_name in env_config_files:
            return False
        
        return True
    
    def _categorize_file(self, file_path: Path) -> Tuple[FileCategory, str, float]:
        """Categorize a file based on patterns and content."""
        file_str = str(file_path).replace('\\', '/')
        name = file_path.name.lower()
        
        # Test files
        if any(re.search(pattern, file_str, re.IGNORECASE) for pattern in self.test_patterns):
            return FileCategory.TEST, "Test file", 0.9
        
        # Configuration files
        if any(re.search(pattern, file_str, re.IGNORECASE) for pattern in self.config_patterns):
            return FileCategory.CONFIG, "Configuration file", 0.8
        
        # Documentation
        if any(re.search(pattern, file_str, re.IGNORECASE) for pattern in self.doc_patterns):
            return FileCategory.DOCUMENTATION, "Documentation file", 0.8
        
        # Build artifacts
        if any(re.search(pattern, file_str, re.IGNORECASE) for pattern in self.build_patterns):
            return FileCategory.BUILD, "Build artifact", 0.9
        
        # Scripts
        if any(re.search(pattern, file_str, re.IGNORECASE) for pattern in self.script_patterns):
            return FileCategory.SCRIPT, "Script file", 0.7
        
        # Data files
        if any(re.search(pattern, file_str, re.IGNORECASE) for pattern in self.data_patterns):
            return FileCategory.DATA, "Data file", 0.7
        
        # Assets
        if any(re.search(pattern, file_str, re.IGNORECASE) for pattern in self.asset_patterns):
            return FileCategory.ASSET, "Asset file", 0.8
        
        # Temporary files
        if any(re.search(pattern, file_str, re.IGNORECASE) for pattern in self.temp_patterns):
            return FileCategory.TEMPORARY, "Temporary file", 0.9
        
        # Specific file analysis
        if file_path.suffix.lower() == '.py':
            purpose = self._analyze_python_file(file_path)
            return FileCategory.SOURCE, purpose, 0.8
        
        if file_path.suffix.lower() in ['.js', '.ts', '.jsx', '.tsx']:
            purpose = self._analyze_javascript_file(file_path)
            return FileCategory.SOURCE, purpose, 0.8
        
        # Default to source if it's a code file
        code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.rb', '.go', '.rs'}
        if file_path.suffix.lower() in code_extensions:
            return FileCategory.SOURCE, "Source code file", 0.6
        
        return FileCategory.UNKNOWN, "Unknown file type", 0.3
    
    def _analyze_python_file(self, file_path: Path) -> str:
        """Analyze Python file content to determine purpose."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            if 'import unittest' in content or 'import pytest' in content or 'def test_' in content:
                return "Python test file"
            elif 'if __name__ == "__main__"' in content:
                return "Python script"
            elif 'class ' in content and 'def ' in content:
                return "Python module with classes"
            elif 'def ' in content:
                return "Python module with functions"
            else:
                return "Python source file"
        except Exception:
            return "Python file"
    
    def _analyze_javascript_file(self, file_path: Path) -> str:
        """Analyze JavaScript/TypeScript file content."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            if 'describe(' in content or 'it(' in content or 'test(' in content:
                return "JavaScript test file"
            elif 'export default' in content or 'module.exports' in content:
                return "JavaScript module"
            elif 'React' in content or 'jsx' in content.lower():
                return "React component"
            else:
                return "JavaScript source file"
        except Exception:
            return "JavaScript file"
    
    def _find_related_files(self, file_path: Path) -> List[str]:
        """Find files related to the given file."""
        related = []
        base_name = file_path.stem
        parent_dir = file_path.parent
        
        # Look for files with similar names
        for sibling in parent_dir.iterdir():
            if sibling.is_file() and sibling != file_path:
                if base_name in sibling.stem or sibling.stem in base_name:
                    related.append(str(sibling))
        
        return related
    
    def categorize_files_by_purpose(self, files: List[FileInfo]) -> Dict[str, List[FileInfo]]:
        """Group files by their detected purpose."""
        categories = {}
        
        for file_info in files:
            category_name = file_info.category.value
            if category_name not in categories:
                categories[category_name] = []
            categories[category_name].append(file_info)
        
        return categories
    
    def find_files_by_query(self, files: List[FileInfo], query: str) -> List[FileInfo]:
        """Find files that match a natural language query using AI."""
        if self.verbose:
            self.console.print(f"[blue]🔍 Searching for files matching: '{query}'[/blue]")
        
        # First try quick heuristic matches for common patterns
        quick_matches = self._quick_heuristic_match(files, query)
        if quick_matches:
            if self.verbose:
                self.console.print(f"[green]✅ Found {len(quick_matches)} files using quick pattern matching[/green]")
            return quick_matches
        
        # For more complex queries, use AI to analyze the file list
        if self.verbose:
            self.console.print("[yellow]🤖 Using AI analysis for complex query...[/yellow]")
        
        result = self._ai_assisted_file_matching(files, query)
        
        if self.verbose:
            self.console.print(f"[green]✅ AI analysis complete: {len(result)} files found[/green]")
        
        return result
    
    def _quick_heuristic_match(self, files: List[FileInfo], query: str) -> List[FileInfo]:
        """Quick heuristic matching for common, safe patterns."""
        query_lower = query.lower()
        
        # Exact category matches (safe and fast)
        exact_category_matches = {
            'test files': FileCategory.TEST,
            'config files': FileCategory.CONFIG, 
            'doc files': FileCategory.DOCUMENTATION,
            'documentation files': FileCategory.DOCUMENTATION,
            'temp files': FileCategory.TEMPORARY,
            'build files': FileCategory.BUILD,
        }
        
        for phrase, category in exact_category_matches.items():
            if phrase in query_lower:
                return [f for f in files if f.category == category]
        
        # File extension matches
        if 'python files' in query_lower:
            return [f for f in files if f.extension == '.py']
        if 'javascript files' in query_lower:
            return [f for f in files if f.extension in ['.js', '.ts']]
        if 'image files' in query_lower:
            return [f for f in files if f.extension in ['.png', '.jpg', '.jpeg', '.gif', '.svg']]
        
        return []  # No quick match found, let AI handle it
    
    def _ai_assisted_file_matching(self, files: List[FileInfo], query: str) -> List[FileInfo]:
        """Use AI to intelligently match files based on query."""
        from .llm_resolver import LLMResolver
        
        # Show progress for AI preparation
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as ai_progress:
            
            prep_task = ai_progress.add_task("[yellow]Preparing file data for AI analysis...")
            
            # Prepare file list for AI analysis
            file_data = []
            for file_info in files:
                file_data.append({
                    "name": file_info.name,
                    "path": str(file_info.path),
                    "extension": file_info.extension,
                    "category": file_info.category.value,
                    "purpose": file_info.purpose,
                    "size": file_info.size
                })
            
            ai_progress.update(prep_task, description=f"[yellow]Sending {len(file_data)} files to AI for analysis...")
            
            # Create a focused prompt for file matching
            prompt = f'''Analyze these files and identify which ones match the query: "{query}"

Files available:
{self._format_files_for_ai(file_data)}

Task: Return ONLY the file names that match the query "{query}".

Consider:
- Files with relevant words in their names (including suffixes like "my_installer.exe")
- File purposes and categories
- File extensions that make sense for the query
- Be inclusive but not overly broad

Respond with a JSON array of matching file names:
["filename1.ext", "filename2.ext"]'''
            
            ai_progress.update(prep_task, description="[yellow]Waiting for AI response...")
            
            try:
                # Use LLM to get file matches
                llm_resolver = LLMResolver(verbose=False)
                if llm_resolver.model == "local":
                    response = llm_resolver._resolve_with_local_llm(prompt)
                    matched_names = self._parse_ai_file_response(response)
                    
                    ai_progress.update(prep_task, description="[yellow]Processing AI response...")
                    
                    # Convert matched names back to FileInfo objects
                    matching_files = []
                    for file_info in files:
                        if file_info.name in matched_names:
                            matching_files.append(file_info)
                    
                    if matching_files:  # AI found matches
                        return matching_files
                
            except Exception as e:
                # If AI fails, fall back to basic pattern matching
                if self.verbose:
                    self.console.print(f"[yellow]AI matching failed: {e}[/yellow]")
                pass
        
        # Fallback: enhanced pattern matching
        return self._enhanced_pattern_matching(files, query)
    
    def _format_files_for_ai(self, file_data: List[dict]) -> str:
        """Format file list for AI analysis."""
        formatted = []
        for i, file_info in enumerate(file_data[:50]):  # Limit to prevent token overflow
            formatted.append(f"{i+1}. {file_info['name']} ({file_info['extension']}) - {file_info['purpose']}")
        
        if len(file_data) > 50:
            formatted.append(f"... and {len(file_data) - 50} more files")
        
        return "\n".join(formatted)
    
    def _parse_ai_file_response(self, response: List[str]) -> List[str]:
        """Parse AI response to extract file names."""
        import json
        import re
        
        if not response:
            return []
        
        response_text = ' '.join(response) if isinstance(response, list) else str(response)
        
        # Try to extract JSON array
        json_match = re.search(r'\[.*?\]', response_text, re.DOTALL)
        if json_match:
            try:
                file_names = json.loads(json_match.group())
                if isinstance(file_names, list):
                    return [name for name in file_names if isinstance(name, str)]
            except json.JSONDecodeError:
                pass
        
        # Fallback: extract quoted filenames
        quoted_files = re.findall(r'["\']([^"\']+\.[a-zA-Z0-9]+)["\']', response_text)
        return quoted_files
    
    def _enhanced_pattern_matching(self, files: List[FileInfo], query: str) -> List[FileInfo]:
        """Enhanced pattern matching as fallback."""
        query_lower = query.lower()
        matching_files = []
        
        # Extract key terms from query
        key_terms = []
        if 'install' in query_lower:
            key_terms.extend(['install', 'setup', 'installer'])
        if 'test' in query_lower:
            key_terms.extend(['test', 'spec'])
        if 'config' in query_lower:
            key_terms.extend(['config', 'configuration', 'settings'])
        if 'doc' in query_lower:
            key_terms.extend(['doc', 'readme', 'documentation'])
        if 'python' in query_lower:
            key_terms.extend(['.py'])
        if 'javascript' in query_lower:
            key_terms.extend(['.js', '.ts'])
        
        # If no specific terms found, try to extract any meaningful words
        if not key_terms:
            # Extract words from query (excluding common words)
            stop_words = {'list', 'show', 'find', 'all', 'files', 'with', 'in', 'the', 'name', 'that', 'have'}
            words = query_lower.split()
            for word in words:
                if word not in stop_words and len(word) > 2:
                    key_terms.append(word)
        
        # Match files containing any key terms
        for file_info in files:
            file_name_lower = file_info.name.lower()
            file_purpose_lower = file_info.purpose.lower()
            
            # Check if any key term appears in filename or purpose
            for term in key_terms:
                if term in file_name_lower or term in file_purpose_lower:
                    matching_files.append(file_info)
                    break
        
        # Remove duplicates
        seen = set()
        unique_files = []
        for file_info in matching_files:
            if file_info.path not in seen:
                seen.add(file_info.path)
                unique_files.append(file_info)
        
        return unique_files