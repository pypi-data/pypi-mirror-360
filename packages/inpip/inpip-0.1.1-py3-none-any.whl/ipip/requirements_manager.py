"""
Requirements.txt generation and management for ipip.
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from rich.console import Console
from rich.table import Table

console = Console()


class RequirementsManager:
    """Manages requirements.txt files and project dependencies."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.project_root = self._find_project_root()
    
    def _find_project_root(self) -> Path:
        """Find the project root directory."""
        current = Path.cwd()
        
        # Look for common project indicators
        indicators = [
            "pyproject.toml",
            "setup.py",
            "requirements.txt",
            ".git",
            "Pipfile",
            "poetry.lock",
        ]
        
        while current != current.parent:
            if any((current / indicator).exists() for indicator in indicators):
                return current
            current = current.parent
        
        # If no indicators found, use current directory
        return Path.cwd()
    
    def create_requirements(self, output_file: str = "requirements.txt") -> bool:
        """Create a requirements.txt file from the current environment."""
        try:
            console.print("[blue]Analyzing current environment...[/blue]")
            
            # Get currently installed packages
            installed_packages = self._get_installed_packages()
            
            # Filter out system packages and identify project-specific ones
            project_packages = self._filter_project_packages(installed_packages)
            
            # Detect imports in the project
            project_imports = self._scan_project_imports()
            
            # Match imports to packages
            required_packages = self._match_imports_to_packages(project_imports, installed_packages)
            
            # Merge with explicitly installed packages
            all_packages = self._merge_package_lists(project_packages, required_packages)
            
            # Write requirements file
            output_path = self.project_root / output_file
            self._write_requirements_file(output_path, all_packages)
            
            console.print(f"[green]✓ Requirements file created: {output_path}[/green]")
            console.print(f"[blue]Found {len(all_packages)} dependencies[/blue]")
            
            if self.verbose:
                self._display_packages_table(all_packages)
            
            return True
            
        except Exception as e:
            console.print(f"[red]Error creating requirements: {e}[/red]")
            return False
    
    def update_requirements(self, requirements_file: str = "requirements.txt") -> bool:
        """Update an existing requirements.txt file."""
        req_path = self.project_root / requirements_file
        
        if not req_path.exists():
            console.print(f"[yellow]Requirements file not found: {req_path}[/yellow]")
            console.print("[blue]Creating new requirements file...[/blue]")
            return self.create_requirements(requirements_file)
        
        try:
            # Read existing requirements
            existing_packages = self._read_requirements_file(req_path)
            
            # Get current environment packages
            current_packages = self._get_installed_packages()
            
            # Update versions for existing packages
            updated_packages = {}
            for pkg_name in existing_packages:
                if pkg_name in current_packages:
                    updated_packages[pkg_name] = current_packages[pkg_name]
                else:
                    # Package no longer installed
                    if self.verbose:
                        console.print(f"[yellow]Package {pkg_name} no longer installed[/yellow]")
            
            # Write updated requirements
            self._write_requirements_file(req_path, updated_packages)
            
            console.print(f"[green]✓ Requirements file updated: {req_path}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Error updating requirements: {e}[/red]")
            return False
    
    def _get_installed_packages(self) -> Dict[str, str]:
        """Get all installed packages and their versions."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "freeze"],
                capture_output=True,
                text=True,
                check=True
            )
            
            packages = {}
            for line in result.stdout.strip().split('\n'):
                if line and '==' in line:
                    name, version = line.split('==', 1)
                    packages[name] = version
            
            return packages
            
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error getting installed packages: {e}[/red]")
            return {}
    
    def _filter_project_packages(self, installed_packages: Dict[str, str]) -> Dict[str, str]:
        """Filter out system packages to identify project-specific ones."""
        # Common system/base packages to exclude
        system_packages = {
            "pip", "setuptools", "wheel", "distlib", "virtualenv",
            "pip-tools", "pipenv", "poetry", "twine", "build",
        }
        
        return {
            name: version for name, version in installed_packages.items()
            if name.lower() not in system_packages
        }
    
    def _scan_project_imports(self) -> Set[str]:
        """Scan Python files in the project for import statements."""
        imports = set()
        python_files = list(self.project_root.rglob("*.py"))
        
        # Exclude common directories
        exclude_dirs = {".git", "__pycache__", ".pytest_cache", "venv", ".venv", "env"}
        
        for py_file in python_files:
            # Skip files in excluded directories
            if any(part in exclude_dirs for part in py_file.parts):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    imports.update(self._extract_imports(content))
            except (UnicodeDecodeError, FileNotFoundError):
                continue
        
        return imports
    
    def _extract_imports(self, content: str) -> Set[str]:
        """Extract import statements from Python code."""
        imports = set()
        
        # Patterns for different import styles
        patterns = [
            r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'^from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import',
        ]
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('#'):
                continue
                
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    module = match.group(1)
                    # Get top-level module name
                    top_module = module.split('.')[0]
                    imports.add(top_module)
        
        return imports
    
    def _match_imports_to_packages(self, imports: Set[str], installed_packages: Dict[str, str]) -> Dict[str, str]:
        """Match import names to installed package names."""
        matched = {}
        
        # Common import name to package name mappings
        import_mappings = {
            "cv2": "opencv-python",
            "PIL": "pillow",
            "bs4": "beautifulsoup4",
            "yaml": "PyYAML",
            "dateutil": "python-dateutil",
            "jwt": "PyJWT",
            "crypto": "cryptography",
            "dotenv": "python-dotenv",
            "sklearn": "scikit-learn",
        }
        
        for import_name in imports:
            # Direct match
            if import_name in installed_packages:
                matched[import_name] = installed_packages[import_name]
            # Check mappings
            elif import_name in import_mappings:
                pkg_name = import_mappings[import_name]
                if pkg_name in installed_packages:
                    matched[pkg_name] = installed_packages[pkg_name]
            # Fuzzy matching (convert underscores/hyphens)
            else:
                variants = [
                    import_name.replace('_', '-'),
                    import_name.replace('-', '_'),
                    import_name.lower(),
                ]
                
                for variant in variants:
                    if variant in installed_packages:
                        matched[variant] = installed_packages[variant]
                        break
        
        return matched
    
    def _merge_package_lists(self, *package_lists: Dict[str, str]) -> Dict[str, str]:
        """Merge multiple package dictionaries, preferring later versions."""
        merged = {}
        
        for package_dict in package_lists:
            merged.update(package_dict)
        
        return merged
    
    def _write_requirements_file(self, file_path: Path, packages: Dict[str, str]) -> None:
        """Write packages to a requirements.txt file."""
        sorted_packages = sorted(packages.items())
        
        with open(file_path, 'w') as f:
            f.write("# Generated by ipip\n")
            f.write("# This file lists the Python dependencies for this project\n\n")
            
            for package, version in sorted_packages:
                f.write(f"{package}=={version}\n")
    
    def _read_requirements_file(self, file_path: Path) -> Dict[str, str]:
        """Read an existing requirements.txt file."""
        packages = {}
        
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '==' in line:
                    name, version = line.split('==', 1)
                    packages[name] = version
        
        return packages
    
    def _display_packages_table(self, packages: Dict[str, str]) -> None:
        """Display packages in a formatted table."""
        table = Table(title="Project Dependencies")
        table.add_column("Package", style="cyan", no_wrap=True)
        table.add_column("Version", style="magenta")
        
        for package, version in sorted(packages.items()):
            table.add_row(package, version)
        
        console.print(table)