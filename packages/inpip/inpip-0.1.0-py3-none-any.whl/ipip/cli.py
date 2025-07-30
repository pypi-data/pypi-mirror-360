"""
CLI interface for ipip - Intelligent pip package installer.
"""

import click
import sys
from typing import List, Optional
from .llm_resolver import LLMResolver
from .package_installer import PackageInstaller
from .requirements_manager import RequirementsManager
from .package_searcher import PackageSearcher
from .file_operations import FileOperationManager
from .ollama_installer import OllamaInstaller
from rich.console import Console
from rich.table import Table

console = Console()

# Global flag to track if we've done first-time setup
_setup_done = False


@click.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.argument('query', nargs=-1, required=False)
@click.option('--dry-run', is_flag=True, help='Show what would be installed without actually installing')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--model', default='local', help='LLM model to use for resolution (local, openai, etc.)')
@click.option('--setup', is_flag=True, help='Run first-time setup')
@click.option('--undo', is_flag=True, help='Emergency undo recent file operations')
@click.option('--context', is_flag=True, help='Show current file context')
@click.option('--clear-context', is_flag=True, help='Clear current file context')
@click.pass_context
def main(ctx, query: tuple, dry_run: bool, verbose: bool, model: str, setup: bool, undo: bool, context: bool, clear_context: bool):
    """
    ipip - Intelligent pip package installer using AI.
    
    Examples:
        ipip blender                    # Installs bpy
        ipip "build a chatbot"          # AI suggests relevant packages  
        ipip "move test files to tests" # Organizes files intelligently
        ipip create requirements        # Creates requirements.txt
    """
    global _setup_done
    
    # Handle setup command
    if setup:
        installer = OllamaInstaller(verbose=True)
        installer.interactive_setup()
        return
    
    # Handle emergency undo
    if undo:
        from .emergency_undo import emergency_undo
        emergency_undo()
        return
    
    # Handle context commands
    if context:
        from .file_context import file_context
        file_context.show_context(verbose=True)
        return
    
    if clear_context:
        from .file_context import file_context
        file_context.clear_context()
        console.print("[green]✅ File context cleared[/green]")
        return
    
    # Run auto-setup on first use (unless it's just help)
    if not _setup_done and query and not any(h in str(query) for h in ['--help', '-h']):
        installer = OllamaInstaller(verbose=verbose)
        installer.ensure_ollama_ready()
        _setup_done = True
    
    if not query:
        click.echo("Usage: ipip <query>")
        click.echo("Try 'ipip --help' for more information.")
        click.echo("Run 'ipip --setup' for first-time setup.")
        return
    
    query_str = " ".join(query)
    
    try:
        resolver = LLMResolver(model=model, verbose=verbose)
        installer = PackageInstaller(dry_run=dry_run, verbose=verbose)
        searcher = PackageSearcher(verbose=verbose)
        requirements_manager = RequirementsManager(verbose=verbose)
        file_manager = FileOperationManager(dry_run=dry_run, verbose=verbose)
        
        # Use LLM to understand the intent
        intent = resolver.parse_intent(query_str)
        
        if verbose:
            console.print(f"[blue]Parsed intent: {intent.action}[/blue]")
        
        if intent.action == "install":
            _handle_install(intent, installer, resolver, dry_run, verbose)
        elif intent.action == "search":
            _handle_search(intent, searcher, verbose)
        elif intent.action == "requirements":
            _handle_requirements(intent, requirements_manager, verbose)
        elif intent.action == "file":
            _handle_file_operations(intent, file_manager, verbose)
        else:
            console.print(f"[red]Unknown action: {intent.action}[/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


def _handle_install(intent, installer, resolver, dry_run: bool, verbose: bool):
    """Handle package installation."""
    # Show progress for package resolution
    if not verbose:
        with console.status("[bold blue]Resolving packages...", spinner="dots"):
            packages = resolver.resolve_packages(intent.target)
    else:
        packages = resolver.resolve_packages(intent.target)
    
    if not packages:
        console.print(f"[yellow]Could not resolve packages for: {intent.target}[/yellow]")
        return
    
    if verbose:
        console.print(f"[blue]Resolved packages: {packages}[/blue]")
    
    if dry_run:
        console.print("[yellow]Dry run - would install:[/yellow]")
        for pkg in packages:
            console.print(f"  - {pkg}")
    else:
        installer.install_packages(packages)


def _handle_search(intent, searcher, verbose: bool):
    """Handle package search and discovery."""
    # Show progress for package search
    if not verbose:
        with console.status("[bold blue]Searching packages...", spinner="dots"):
            results = searcher.search_packages(intent.target)
    else:
        console.print(f"[blue]Searching for packages related to: {intent.target}[/blue]")
        results = searcher.search_packages(intent.target)
    
    if not results:
        console.print(f"[yellow]No packages found for: {intent.target}[/yellow]")
        return
    
    table = Table(title=f"Packages for '{intent.target}'")
    table.add_column("Package", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")
    table.add_column("Version", style="green")
    
    for result in results:
        table.add_row(result.name, result.description, result.version)
    
    console.print(table)
    
    # Interactive selection
    if len(results) > 1:
        _interactive_package_selection(results)


def _handle_requirements(intent, requirements_manager, verbose: bool):
    """Handle requirements.txt operations."""
    if "create" in intent.target.lower() or "generate" in intent.target.lower():
        requirements_manager.create_requirements()
    elif "update" in intent.target.lower():
        requirements_manager.update_requirements()
    else:
        # Default to create
        requirements_manager.create_requirements()


def _handle_file_operations(intent, file_manager, verbose: bool):
    """Handle file operations."""
    if verbose:
        console.print(f"[blue]Executing file operation: {intent.target}[/blue]")
    
    results = file_manager.execute_file_command(intent.target)
    
    if not results:
        console.print("[yellow]No file operations were performed[/yellow]")
        return
    
    # Summary of results
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    if successful:
        console.print(f"[green]✅ {len(successful)} operation(s) completed successfully[/green]")
    
    if failed:
        console.print(f"[red]❌ {len(failed)} operation(s) failed[/red]")
        for result in failed:
            console.print(f"[red]  • {result.message}[/red]")


def _interactive_package_selection(packages):
    """Allow user to interactively select packages to install."""
    console.print("\n[blue]Select packages to install (enter numbers separated by commas, or 'all'):[/blue]")
    
    for i, pkg in enumerate(packages, 1):
        console.print(f"  {i}. {pkg.name} - {pkg.description}")
    
    try:
        selection = input("\nSelection: ").strip()
        
        if selection.lower() == 'all':
            selected_packages = [pkg.name for pkg in packages]
        else:
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            selected_packages = [packages[i].name for i in indices if 0 <= i < len(packages)]
        
        if selected_packages:
            installer = PackageInstaller(dry_run=False, verbose=True)
            installer.install_packages(selected_packages)
        else:
            console.print("[yellow]No packages selected.[/yellow]")
            
    except (ValueError, IndexError):
        console.print("[red]Invalid selection.[/red]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Selection cancelled.[/yellow]")


if __name__ == "__main__":
    main()