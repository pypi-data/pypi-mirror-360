"""
Configuration management for ipip.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from rich.console import Console

console = Console()


@dataclass
class LLMConfig:
    """Configuration for LLM settings."""
    model: str = "local"
    api_key: str = ""
    api_url: str = ""
    timeout: int = 30
    max_retries: int = 3
    temperature: float = 0.1


@dataclass
class IpipConfig:
    """Main configuration for ipip."""
    llm: LLMConfig
    verbose: bool = False
    dry_run_default: bool = False
    auto_confirm: bool = False
    requirements_filename: str = "requirements.txt"
    exclude_system_packages: bool = True
    package_search_limit: int = 10


class ConfigManager:
    """Manages ipip configuration files."""
    
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_config_dir(self) -> Path:
        """Get the configuration directory."""
        # Use XDG_CONFIG_HOME if available, otherwise ~/.config
        if os.name == 'nt':  # Windows
            config_home = os.environ.get('APPDATA', str(Path.home() / 'AppData' / 'Roaming'))
            return Path(config_home) / 'ipip'
        else:  # Unix-like
            config_home = os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config'))
            return Path(config_home) / 'ipip'
    
    def load_config(self) -> IpipConfig:
        """Load configuration from file."""
        if not self.config_file.exists():
            return self._create_default_config()
        
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            # Convert to config objects
            llm_config = LLMConfig(**data.get('llm', {}))
            config = IpipConfig(
                llm=llm_config,
                verbose=data.get('verbose', False),
                dry_run_default=data.get('dry_run_default', False),
                auto_confirm=data.get('auto_confirm', False),
                requirements_filename=data.get('requirements_filename', 'requirements.txt'),
                exclude_system_packages=data.get('exclude_system_packages', True),
                package_search_limit=data.get('package_search_limit', 10)
            )
            
            return config
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            console.print(f"[yellow]Warning: Invalid config file, using defaults: {e}[/yellow]")
            return self._create_default_config()
    
    def save_config(self, config: IpipConfig) -> bool:
        """Save configuration to file."""
        try:
            data = {
                'llm': asdict(config.llm),
                'verbose': config.verbose,
                'dry_run_default': config.dry_run_default,
                'auto_confirm': config.auto_confirm,
                'requirements_filename': config.requirements_filename,
                'exclude_system_packages': config.exclude_system_packages,
                'package_search_limit': config.package_search_limit
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
            
        except Exception as e:
            console.print(f"[red]Error saving config: {e}[/red]")
            return False
    
    def _create_default_config(self) -> IpipConfig:
        """Create and save default configuration."""
        config = IpipConfig(
            llm=LLMConfig(),
            verbose=False,
            dry_run_default=False,
            auto_confirm=False,
            requirements_filename="requirements.txt",
            exclude_system_packages=True,
            package_search_limit=10
        )
        
        self.save_config(config)
        return config
    
    def get_llm_config(self) -> LLMConfig:
        """Get LLM configuration with environment variable overrides."""
        config = self.load_config()
        llm_config = config.llm
        
        # Override with environment variables if present
        if api_key := os.environ.get('IPIP_API_KEY'):
            llm_config.api_key = api_key
        
        if api_url := os.environ.get('IPIP_API_URL'):
            llm_config.api_url = api_url
        
        if model := os.environ.get('IPIP_MODEL'):
            llm_config.model = model
        
        if timeout := os.environ.get('IPIP_TIMEOUT'):
            try:
                llm_config.timeout = int(timeout)
            except ValueError:
                pass
        
        return llm_config
    
    def update_llm_model(self, model: str) -> bool:
        """Update the LLM model setting."""
        config = self.load_config()
        config.llm.model = model
        return self.save_config(config)
    
    def update_api_key(self, api_key: str) -> bool:
        """Update the API key setting."""
        config = self.load_config()
        config.llm.api_key = api_key
        return self.save_config(config)
    
    def reset_config(self) -> bool:
        """Reset configuration to defaults."""
        if self.config_file.exists():
            self.config_file.unlink()
        
        self._create_default_config()
        console.print("[green]Configuration reset to defaults[/green]")
        return True
    
    def show_config(self) -> None:
        """Display current configuration."""
        config = self.load_config()
        
        console.print("[bold blue]Current ipip configuration:[/bold blue]")
        console.print(f"Config file: {self.config_file}")
        console.print()
        
        console.print("[bold]LLM Settings:[/bold]")
        console.print(f"  Model: {config.llm.model}")
        console.print(f"  API URL: {config.llm.api_url or 'Not set'}")
        console.print(f"  API Key: {'***' if config.llm.api_key else 'Not set'}")
        console.print(f"  Timeout: {config.llm.timeout}s")
        console.print(f"  Max Retries: {config.llm.max_retries}")
        console.print(f"  Temperature: {config.llm.temperature}")
        console.print()
        
        console.print("[bold]General Settings:[/bold]")
        console.print(f"  Verbose: {config.verbose}")
        console.print(f"  Dry run default: {config.dry_run_default}")
        console.print(f"  Auto confirm: {config.auto_confirm}")
        console.print(f"  Requirements filename: {config.requirements_filename}")
        console.print(f"  Exclude system packages: {config.exclude_system_packages}")
        console.print(f"  Package search limit: {config.package_search_limit}")
        console.print()
        
        console.print("[dim]Environment variable overrides:[/dim]")
        console.print(f"  IPIP_MODEL: {os.environ.get('IPIP_MODEL', 'Not set')}")
        console.print(f"  IPIP_API_KEY: {'Set' if os.environ.get('IPIP_API_KEY') else 'Not set'}")
        console.print(f"  IPIP_API_URL: {os.environ.get('IPIP_API_URL', 'Not set')}")
        console.print(f"  IPIP_TIMEOUT: {os.environ.get('IPIP_TIMEOUT', 'Not set')}")