"""
Package installation functionality for ipip.
"""

import subprocess
import sys
from typing import List, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class PackageInstaller:
    """Handles pip package installation."""
    
    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
    
    def install_packages(self, packages: List[str]) -> bool:
        """Install the specified packages using pip."""
        if not packages:
            console.print("[yellow]No packages to install.[/yellow]")
            return True
        
        if self.dry_run:
            console.print("[yellow]Dry run - would install:[/yellow]")
            for package in packages:
                console.print(f"  - {package}")
            return True
        
        console.print(f"[blue]Installing packages: {', '.join(packages)}[/blue]")
        
        success = True
        for package in packages:
            if not self._install_single_package(package):
                success = False
        
        return success
    
    def _install_single_package(self, package: str) -> bool:
        """Install a single package."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn(f"Installing {package}..."),
                console=console,
                transient=True
            ) as progress:
                progress.add_task("install", total=None)
                
                # Build pip command
                cmd = [sys.executable, "-m", "pip", "install", package]
                
                if not self.verbose:
                    cmd.append("--quiet")
                
                # Run pip install
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=False
                )
            
            if result.returncode == 0:
                console.print(f"[green]✓ Successfully installed {package}[/green]")
                return True
            else:
                console.print(f"[red]✗ Failed to install {package}[/red]")
                if self.verbose:
                    console.print(f"[red]Error: {result.stderr}[/red]")
                else:
                    console.print("[dim]Use --verbose to see error details[/dim]")
                return False
                
        except Exception as e:
            console.print(f"[red]✗ Error installing {package}: {e}[/red]")
            return False
    
    def check_package_exists(self, package: str) -> bool:
        """Check if a package exists on PyPI."""
        try:
            cmd = [sys.executable, "-m", "pip", "index", "versions", package]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return result.returncode == 0
        except Exception:
            return False
    
    def is_package_installed(self, package: str) -> bool:
        """Check if a package is already installed."""
        try:
            cmd = [sys.executable, "-m", "pip", "show", package]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return result.returncode == 0
        except Exception:
            return False
    
    def get_installed_version(self, package: str) -> Optional[str]:
        """Get the installed version of a package."""
        try:
            cmd = [sys.executable, "-m", "pip", "show", package]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        return line.split(':', 1)[1].strip()
            return None
        except Exception:
            return None
    
    def upgrade_package(self, package: str) -> bool:
        """Upgrade a package to the latest version."""
        try:
            console.print(f"[blue]Upgrading {package}...[/blue]")
            
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", package]
            if not self.verbose:
                cmd.append("--quiet")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                console.print(f"[green]✓ Successfully upgraded {package}[/green]")
                return True
            else:
                console.print(f"[red]✗ Failed to upgrade {package}[/red]")
                if self.verbose:
                    console.print(f"[red]Error: {result.stderr}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]✗ Error upgrading {package}: {e}[/red]")
            return False
    
    def uninstall_package(self, package: str) -> bool:
        """Uninstall a package."""
        try:
            console.print(f"[blue]Uninstalling {package}...[/blue]")
            
            cmd = [sys.executable, "-m", "pip", "uninstall", "-y", package]
            if not self.verbose:
                cmd.append("--quiet")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                console.print(f"[green]✓ Successfully uninstalled {package}[/green]")
                return True
            else:
                console.print(f"[red]✗ Failed to uninstall {package}[/red]")
                if self.verbose:
                    console.print(f"[red]Error: {result.stderr}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]✗ Error uninstalling {package}: {e}[/red]")
            return False