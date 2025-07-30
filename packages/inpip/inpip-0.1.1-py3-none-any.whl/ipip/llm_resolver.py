"""
LLM-based package name resolution for ipip.
"""

import json
import subprocess
import re
import sys
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from rich.console import Console

console = Console()


@dataclass
class Intent:
    """Represents the parsed intent from user query."""
    action: str  # install, search, requirements
    target: str  # the target package or query
    confidence: float = 0.0


@dataclass
class PackageMapping:
    """Represents a package name mapping."""
    query: str
    actual_package: str
    confidence: float
    description: str = ""


class LLMResolver:
    """Resolves package names using local or remote LLM."""
    
    def __init__(self, model: str = "local", verbose: bool = False):
        self.model = model
        self.verbose = verbose
        self.package_mappings = self._load_common_mappings()
    
    def _load_common_mappings(self) -> Dict[str, str]:
        """Load common package name mappings."""
        return {
            "blender": "bpy",
            "pil": "pillow", 
            "PIL": "pillow",
            "opencv": "opencv-python",
            "cv2": "opencv-python",
            "sklearn": "scikit-learn",
            "torch": "torch",
            "pytorch": "torch",
            "tensorflow": "tensorflow",
            "tf": "tensorflow",
            "numpy": "numpy",
            "np": "numpy",
            "pandas": "pandas",
            "pd": "pandas",
            "matplotlib": "matplotlib",
            "plt": "matplotlib",
            "seaborn": "seaborn",
            "sns": "seaborn",
            "requests": "requests",
            "beautifulsoup": "beautifulsoup4",
            "bs4": "beautifulsoup4",
            "selenium": "selenium",
            "flask": "flask",
            "django": "django",
            "fastapi": "fastapi",
            "sqlalchemy": "SQLAlchemy",
            "psycopg": "psycopg2-binary",
            "mysql": "mysql-connector-python",
            "redis": "redis",
            "celery": "celery",
            "jwt": "PyJWT",
            "yaml": "PyYAML",
            "toml": "toml",
            "dotenv": "python-dotenv",
            "crypto": "cryptography",
            "lxml": "lxml",
            "arrow": "arrow",
            "dateutil": "python-dateutil",
            "pytz": "pytz",
            "click": "click",
            "typer": "typer",
            "rich": "rich",
            "colorama": "colorama",
            "tqdm": "tqdm",
            "joblib": "joblib",
            "dask": "dask",
            "multiprocessing": "multiprocess",
            "asyncio": "asyncio",
            "aiohttp": "aiohttp",
            "websockets": "websockets",
        }
    
    def parse_intent(self, query: str) -> Intent:
        """Parse user intent from natural language query."""
        query_lower = query.lower()
        
        # Check for file operation keywords
        file_keywords = ["move", "copy", "delete", "remove", "create", "organize", "folder", "directory", "list", "show", "find"]
        if any(keyword in query_lower for keyword in file_keywords):
            return Intent(action="file", target=query)
        
        # Check for requirements-related actions
        requirements_keywords = ["requirements", "requirement", "req", "freeze"]
        create_keywords = ["create", "generate", "make", "build"]
        update_keywords = ["update", "refresh", "sync"]
        
        if any(keyword in query_lower for keyword in requirements_keywords):
            if any(keyword in query_lower for keyword in create_keywords):
                return Intent(action="requirements", target="create requirements")
            elif any(keyword in query_lower for keyword in update_keywords):
                return Intent(action="requirements", target="update requirements")
            else:
                return Intent(action="requirements", target="create requirements")
        
        # Check for search-related actions
        search_keywords = ["search", "find", "look", "discover", "list", "show", "available"]
        if any(keyword in query_lower for keyword in search_keywords):
            # Extract the search target
            target = query
            for keyword in search_keywords:
                target = target.replace(keyword, "").strip()
            return Intent(action="search", target=target or query)
        
        # Default to install action
        return Intent(action="install", target=query)
    
    def resolve_packages(self, query: str) -> List[str]:
        """Resolve package names from user query."""
        # First try direct mapping
        query_clean = query.strip().lower()
        
        if query_clean in self.package_mappings:
            if self.verbose:
                console.print(f"[green]Direct mapping found: {query_clean} -> {self.package_mappings[query_clean]}[/green]")
            return [self.package_mappings[query_clean]]
        
        # Try LLM resolution
        if self.model == "local":
            llm_result = self._resolve_with_local_llm(query)
            if llm_result:
                if self.verbose:
                    console.print(f"[green]LLM resolved: {llm_result}[/green]")
                return llm_result
            else:
                if self.verbose:
                    console.print(f"[yellow]LLM failed, using heuristics[/yellow]")
                return self._resolve_heuristic(query)
        else:
            # For now, fallback to heuristic resolution
            return self._resolve_heuristic(query)
    
    def _resolve_with_local_llm(self, query: str) -> List[str]:
        """Resolve using local LLM (like ollama)."""
        try:
            # Get the correct ollama command for this platform
            ollama_cmd = self._get_ollama_command()
            
            if not ollama_cmd:
                if self.verbose:
                    console.print("[yellow]Ollama not found or not responding, falling back to heuristic resolution[/yellow]")
                return self._resolve_heuristic(query)
            
            # Get available models and pick the best one
            model_to_use = self._get_best_ollama_model()
            
            # Prepare a simple, focused prompt
            prompt = f"""Task: Suggest Python packages for "{query}"

Examples:
- "openai image generator" -> ["openai", "pillow", "requests"]
- "web scraping" -> ["requests", "beautifulsoup4", "selenium"]
- "machine learning" -> ["scikit-learn", "pandas", "numpy"]
- "chatbot" -> ["transformers", "torch", "openai"]

Respond with ONLY a JSON object:
{{"packages": ["package1", "package2", "package3"]}}"""
            
            if self.verbose:
                console.print(f"[blue]Using Ollama model: {model_to_use}[/blue]")
            
            # Call ollama with the correct command and progress indicator
            if self.verbose:
                console.print("[blue]🤖 Querying Ollama LLM... (this may take 5-15 seconds)[/blue]")
            
            # Add progress indicator
            with console.status("[bold blue]Thinking with AI...", spinner="dots") as status:
                try:
                    result = subprocess.run(
                        [ollama_cmd, "run", model_to_use, prompt],
                        capture_output=True,
                        text=True,
                        timeout=45,
                        shell=(sys.platform == "win32"),
                        encoding='utf-8',
                        errors='replace'  # Handle Unicode errors gracefully
                    )
                except UnicodeDecodeError:
                    # Fallback with different encoding
                    result = subprocess.run(
                        [ollama_cmd, "run", model_to_use, prompt],
                        capture_output=True,
                        timeout=45,
                        shell=(sys.platform == "win32"),
                        encoding='latin1',
                        errors='replace'
                    )
                    # Convert to string if bytes
                    if hasattr(result.stdout, 'decode'):
                        result.stdout = result.stdout.decode('utf-8', errors='replace')
                    if hasattr(result.stderr, 'decode'):
                        result.stderr = result.stderr.decode('utf-8', errors='replace')
            
            if result.returncode == 0:
                response = result.stdout.strip()
                if self.verbose:
                    console.print(f"[blue]Raw LLM response ({len(response)} chars):[/blue]")
                    console.print(f"[dim]{response}[/dim]")  # Show full response for debugging
                return self._parse_llm_response(response, query)
            else:
                if self.verbose:
                    console.print(f"[yellow]Ollama error (exit code {result.returncode}):[/yellow]")
                    console.print(f"[yellow]STDERR: {result.stderr}[/yellow]")
                    console.print(f"[yellow]STDOUT: {result.stdout}[/yellow]")
                return self._resolve_heuristic(query)
                
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            if self.verbose:
                console.print(f"[yellow]LLM resolution failed: {e}[/yellow]")
            return self._resolve_heuristic(query)
    
    def _get_ollama_command(self) -> Optional[str]:
        """Get the correct ollama command for this platform."""
        # Possible ollama commands to try
        candidates = ["ollama"]
        
        # On Windows, also try .exe version
        if sys.platform == "win32":
            candidates = ["ollama.exe", "ollama"]
        
        for cmd in candidates:
            try:
                # Test if command exists and works
                result = subprocess.run(
                    [cmd, "--version"], 
                    capture_output=True, 
                    text=True, 
                    timeout=5,
                    shell=(sys.platform == "win32")
                )
                if result.returncode == 0:
                    if self.verbose:
                        console.print(f"[blue]Found Ollama command: {cmd}[/blue]")
                    return cmd
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue
        
        # Try finding ollama in common Windows locations
        if sys.platform == "win32":
            common_paths = [
                "C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Ollama\\ollama.exe",
                "C:\\Program Files\\Ollama\\ollama.exe",
                "C:\\Program Files (x86)\\Ollama\\ollama.exe",
            ]
            
            for path in common_paths:
                expanded_path = os.path.expandvars(path)
                if os.path.exists(expanded_path):
                    try:
                        result = subprocess.run(
                            [expanded_path, "--version"], 
                            capture_output=True, 
                            text=True, 
                            timeout=5,
                            shell=True
                        )
                        if result.returncode == 0:
                            if self.verbose:
                                console.print(f"[blue]Found Ollama at: {expanded_path}[/blue]")
                            return expanded_path
                    except:
                        continue
        
        return None
    
    def _get_best_ollama_model(self) -> str:
        """Get the best available Ollama model."""
        try:
            ollama_cmd = self._get_ollama_command()
            if not ollama_cmd:
                return "llama3.2"
            
            # Get list of available models
            result = subprocess.run(
                [ollama_cmd, "list"], 
                capture_output=True, 
                text=True, 
                timeout=10,
                shell=(sys.platform == "win32")
            )
            
            if result.returncode == 0:
                available_models = []
                for line in result.stdout.split('\n')[1:]:  # Skip header
                    if line.strip():
                        model_name = line.split()[0]
                        available_models.append(model_name)
                
                if self.verbose:
                    console.print(f"[blue]Available models: {available_models}[/blue]")
                
                # Preference order (best for package resolution)
                preferred = ["llama3.2", "llama3.1", "llama3", "mistral", "phi3"]
                
                for pref in preferred:
                    for available in available_models:
                        if pref in available.lower():
                            return available
                
                # Use first available if none preferred
                return available_models[0] if available_models else "llama3.2"
            
            return "llama3.2"
            
        except Exception as e:
            if self.verbose:
                console.print(f"[yellow]Model detection failed: {e}[/yellow]")
            return "llama3.2"
    
    def _parse_llm_response(self, response: str, original_query: str) -> List[str]:
        """Parse LLM response with multiple fallback methods."""
        if not response or not response.strip():
            if self.verbose:
                console.print("[yellow]Empty response from LLM[/yellow]")
            return []
        
        try:
            # Method 1: Look for JSON with packages array
            json_patterns = [
                r'\{"packages":\s*\[.*?\]\}',
                r'\{[^}]*"packages"[^}]*\}',
                r'\{.*?\}',
            ]
            
            for pattern in json_patterns:
                json_match = re.search(pattern, response, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    if self.verbose:
                        console.print(f"[blue]Found JSON: {json_str}[/blue]")
                    
                    try:
                        data = json.loads(json_str)
                        packages = data.get("packages", [])
                        if packages and isinstance(packages, list):
                            # Clean package names
                            clean_packages = [pkg.strip() for pkg in packages if pkg.strip()]
                            if self.verbose:
                                console.print(f"[green]Parsed packages: {clean_packages}[/green]")
                            return clean_packages
                    except json.JSONDecodeError:
                        continue
            
            # Method 2: Extract package names from text
            if self.verbose:
                console.print("[blue]No valid JSON found, extracting from text...[/blue]")
            
            found_packages = []
            
            # Look for quoted package names
            quoted_patterns = [
                r'"([a-zA-Z0-9_-]+)"',
                r"'([a-zA-Z0-9_-]+)'", 
                r"`([a-zA-Z0-9_-]+)`",
            ]
            
            for pattern in quoted_patterns:
                matches = re.findall(pattern, response)
                found_packages.extend(matches)
            
            # Look for common package names
            common_packages = [
                "openai", "requests", "pillow", "transformers", "torch", 
                "tensorflow", "scikit-learn", "pandas", "numpy", "flask",
                "fastapi", "django", "beautifulsoup4", "selenium", "opencv-python"
            ]
            
            for package in common_packages:
                if package in response.lower():
                    found_packages.append(package)
            
            if found_packages:
                unique_packages = list(dict.fromkeys(found_packages))  # Remove duplicates, preserve order
                if self.verbose:
                    console.print(f"[blue]Extracted packages: {unique_packages}[/blue]")
                return unique_packages
            
            # Method 3: If LLM mentioned specific query terms, use heuristics
            if "openai" in response.lower():
                return ["openai", "requests"]
            
            if self.verbose:
                console.print("[yellow]Could not extract packages from LLM response[/yellow]")
            return []
                
        except Exception as e:
            if self.verbose:
                console.print(f"[red]Error parsing LLM response: {e}[/red]")
            return []
    
    def _resolve_heuristic(self, query: str) -> List[str]:
        """Fallback heuristic resolution."""
        words = query.lower().split()
        
        # Try to find known packages in the query
        found_packages = []
        for word in words:
            if word in self.package_mappings:
                found_packages.append(self.package_mappings[word])
        
        if found_packages:
            return found_packages
        
        # If no direct match, try common patterns
        if "openai" in query.lower():
            if "image" in query.lower() or "dall" in query.lower() or "generate" in query.lower():
                return ["openai", "pillow", "requests"]
            else:
                return ["openai", "requests"]
        elif "vision" in query.lower() and "recognition" in query.lower():
            return ["opencv-python", "pillow", "scikit-image"]
        elif "image" in query.lower() and ("generate" in query.lower() or "generation" in query.lower()):
            return ["openai", "pillow", "requests", "diffusers"]
        elif "machine learning" in query.lower() or "ml" in query.lower():
            return ["scikit-learn", "pandas", "numpy"]
        elif "deep learning" in query.lower() or "neural" in query.lower():
            return ["tensorflow", "torch", "keras"]
        elif "web scraping" in query.lower() or "scraping" in query.lower():
            return ["requests", "beautifulsoup4", "selenium"]
        elif "api" in query.lower() and "web" in query.lower():
            return ["fastapi", "flask", "requests"]
        elif "database" in query.lower() or "db" in query.lower():
            return ["sqlalchemy", "psycopg2-binary"]
        elif "chatbot" in query.lower() or "chat bot" in query.lower():
            return ["transformers", "torch", "flask", "openai"]
        elif "nlp" in query.lower() or "natural language" in query.lower():
            return ["transformers", "nltk", "spacy", "torch"]
        elif "sentiment" in query.lower() and "analysis" in query.lower():
            return ["transformers", "textblob", "vader-sentiment", "pandas"]
        
        # Last resort: assume the query is the package name
        if len(words) == 1:
            return [words[0]]
        
        return []