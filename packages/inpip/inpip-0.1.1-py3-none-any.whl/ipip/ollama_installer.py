"""
Automatic Ollama installation and setup for ipip.
"""

import os
import sys
import subprocess
import platform
import urllib.request
import tempfile
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
import time

console = Console()

class OllamaInstaller:
    """Handles automatic Ollama installation and model setup."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.system = platform.system().lower()
        self.machine = platform.machine().lower()
    
    def ensure_ollama_ready(self) -> bool:
        """Ensure Ollama is installed and a model is available."""
        if self.verbose:
            console.print("[blue]🤖 Checking Ollama setup...[/blue]")
        
        # Check if Ollama is installed
        if not self._is_ollama_installed():
            console.print("[yellow]📥 Ollama not found. Installing Ollama for AI features...[/yellow]")
            if not self._install_ollama():
                console.print("[red]❌ Failed to install Ollama. AI features will be limited.[/red]")
                return False
        
        # Start Ollama service if needed
        if not self._is_ollama_running():
            if not self._start_ollama():
                console.print("[yellow]⚠️  Could not start Ollama service. AI features may be limited.[/yellow]")
                return False
        
        # Check if we have a good model
        if not self._has_suitable_model():
            console.print("[blue]📦 Installing AI model for intelligent package resolution...[/blue]")
            if not self._install_default_model():
                console.print("[yellow]⚠️  Could not install AI model. Using heuristic resolution.[/yellow]")
                return False
        
        if self.verbose:
            console.print("[green]✅ Ollama setup complete![/green]")
        return True
    
    def _is_ollama_installed(self) -> bool:
        """Check if Ollama is installed."""
        try:
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    
    def _is_ollama_running(self) -> bool:
        """Check if Ollama service is running."""
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    
    def _has_suitable_model(self) -> bool:
        """Check if we have a suitable model installed."""
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                models = result.stdout.lower()
                # Prefer these models in order
                preferred_models = ['llama3.2', 'llama3.1', 'llama3', 'mistral', 'phi3']
                for model in preferred_models:
                    if model in models:
                        return True
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    
    def _install_ollama(self) -> bool:
        """Install Ollama automatically."""
        try:
            if self.system == 'windows':
                return self._install_ollama_windows()
            elif self.system == 'darwin':  # macOS
                return self._install_ollama_macos()
            elif self.system == 'linux':
                return self._install_ollama_linux()
            else:
                console.print(f"[red]Unsupported platform: {self.system}[/red]")
                return False
        except Exception as e:
            if self.verbose:
                console.print(f"[red]Ollama installation failed: {e}[/red]")
            return False
    
    def _install_ollama_windows(self) -> bool:
        """Install Ollama on Windows."""
        console.print("[blue]📥 Downloading Ollama for Windows...[/blue]")
        
        # Download Ollama installer
        installer_url = "https://ollama.ai/download/OllamaSetup.exe"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            installer_path = Path(temp_dir) / "OllamaSetup.exe"
            
            try:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("Downloading Ollama...", total=None)
                    urllib.request.urlretrieve(installer_url, installer_path)
                    progress.update(task, completed=True)
                
                console.print("[blue]🔧 Running Ollama installer...[/blue]")
                console.print("[yellow]💡 Please follow the installer prompts[/yellow]")
                
                # Run installer
                result = subprocess.run([str(installer_path)], timeout=300)
                
                if result.returncode == 0:
                    console.print("[green]✅ Ollama installed successfully![/green]")
                    # Wait a moment for installation to complete
                    time.sleep(3)
                    return True
                else:
                    console.print("[red]❌ Ollama installation failed[/red]")
                    return False
                    
            except Exception as e:
                console.print(f"[red]Download failed: {e}[/red]")
                return False
    
    def _install_ollama_macos(self) -> bool:
        """Install Ollama on macOS."""
        console.print("[blue]📥 Installing Ollama on macOS...[/blue]")
        
        try:
            # Try Homebrew first
            result = subprocess.run(['brew', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                console.print("[blue]🍺 Installing via Homebrew...[/blue]")
                result = subprocess.run(['brew', 'install', 'ollama'], timeout=300)
                return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Fallback to manual installation
        console.print("[blue]📥 Downloading Ollama installer...[/blue]")
        install_script = "curl -fsSL https://ollama.ai/install.sh | sh"
        result = subprocess.run(install_script, shell=True, timeout=300)
        return result.returncode == 0
    
    def _install_ollama_linux(self) -> bool:
        """Install Ollama on Linux."""
        console.print("[blue]📥 Installing Ollama on Linux...[/blue]")
        
        install_script = "curl -fsSL https://ollama.ai/install.sh | sh"
        result = subprocess.run(install_script, shell=True, timeout=300)
        return result.returncode == 0
    
    def _start_ollama(self) -> bool:
        """Start Ollama service."""
        try:
            if self.system == 'windows':
                # On Windows, Ollama should start automatically
                time.sleep(2)
                return self._is_ollama_running()
            else:
                # On Unix systems, start in background
                subprocess.Popen(['ollama', 'serve'], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                time.sleep(3)
                return self._is_ollama_running()
        except Exception:
            return False
    
    def _install_default_model(self) -> bool:
        """Install a good default model for ipip."""
        models_to_try = [
            ('llama3.2', 'Llama 3.2 (recommended)'),
            ('llama3.1', 'Llama 3.1'),
            ('mistral', 'Mistral (smaller, faster)'),
            ('phi3', 'Phi-3 (compact)')
        ]
        
        for model_name, description in models_to_try:
            console.print(f"[blue]📦 Installing {description}...[/blue]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"Downloading {model_name}...", total=None)
                
                try:
                    result = subprocess.run(
                        ['ollama', 'pull', model_name],
                        capture_output=True,
                        text=True,
                        timeout=600  # 10 minutes timeout
                    )
                    
                    progress.update(task, completed=True)
                    
                    if result.returncode == 0:
                        console.print(f"[green]✅ {description} installed successfully![/green]")
                        return True
                    else:
                        console.print(f"[yellow]⚠️  Failed to install {model_name}, trying next...[/yellow]")
                        
                except subprocess.TimeoutExpired:
                    console.print(f"[yellow]⏱️  {model_name} download timed out, trying next...[/yellow]")
                except Exception as e:
                    if self.verbose:
                        console.print(f"[yellow]Error installing {model_name}: {e}[/yellow]")
        
        console.print("[red]❌ Could not install any AI models[/red]")
        return False
    
    def get_setup_info(self) -> dict:
        """Get information about current Ollama setup."""
        info = {
            'ollama_installed': self._is_ollama_installed(),
            'ollama_running': self._is_ollama_running(),
            'has_model': self._has_suitable_model(),
            'available_models': []
        }
        
        if info['ollama_running']:
            try:
                result = subprocess.run(['ollama', 'list'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    for line in lines:
                        if line.strip():
                            model_name = line.split()[0]
                            info['available_models'].append(model_name)
            except Exception:
                pass
        
        return info
    
    def interactive_setup(self) -> bool:
        """Run interactive setup for first-time users."""
        console.print("\n[bold blue]🚀 Welcome to ipip![/bold blue]")
        console.print("Let's set up AI-powered package resolution for you.\n")
        
        setup_info = self.get_setup_info()
        
        if setup_info['ollama_installed'] and setup_info['has_model']:
            console.print("[green]✅ AI features are already set up and ready![/green]")
            return True
        
        if not setup_info['ollama_installed']:
            console.print("[blue]📥 Ollama (local AI) is not installed.[/blue]")
            console.print("Ollama enables intelligent package name resolution.")
            console.print("Example: 'ipip build a chatbot' → suggests transformers, torch, flask\n")
            
            if Confirm.ask("Install Ollama for AI features?", default=True):
                if not self.ensure_ollama_ready():
                    console.print("\n[yellow]⚠️  AI setup incomplete. ipip will use smart heuristics instead.[/yellow]")
                    return False
            else:
                console.print("\n[blue]💡 You can install Ollama later from https://ollama.ai/[/blue]")
                return False
        
        return True