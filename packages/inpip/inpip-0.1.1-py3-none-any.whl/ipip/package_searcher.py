"""
Package search and discovery functionality for ipip.
"""

import requests
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from rich.console import Console

console = Console()


@dataclass
class PackageInfo:
    """Information about a PyPI package."""
    name: str
    description: str
    version: str
    author: str = ""
    homepage: str = ""
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


class PackageSearcher:
    """Searches for packages on PyPI and provides recommendations."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ipip/0.1.0 (Intelligent pip installer)'
        })
    
    def search_packages(self, query: str, limit: int = 10) -> List[PackageInfo]:
        """Search for packages related to the query."""
        # PyPI doesn't have a search API anymore, so we'll use alternative approaches
        packages = []
        
        # Try different search strategies
        packages.extend(self._search_by_keywords(query, limit))
        packages.extend(self._search_by_category(query, limit))
        packages.extend(self._get_popular_packages_for_domain(query, limit))
        
        # Remove duplicates and sort by relevance
        seen = set()
        unique_packages = []
        for pkg in packages:
            if pkg.name not in seen:
                seen.add(pkg.name)
                unique_packages.append(pkg)
        
        return unique_packages[:limit]
    
    def _search_by_keywords(self, query: str, limit: int) -> List[PackageInfo]:
        """Search packages by keywords using known mappings."""
        packages = []
        query_lower = query.lower()
        
        # Domain-specific package collections
        domain_packages = {
            "computer vision": [
                ("opencv-python", "Computer vision library"),
                ("pillow", "Python Imaging Library fork"),
                ("scikit-image", "Image processing library"),
                ("imageio", "Library for reading and writing image data"),
                ("face-recognition", "Face recognition library"),
            ],
            "vision": [
                ("opencv-python", "Computer vision library"),
                ("pillow", "Python Imaging Library fork"),
                ("scikit-image", "Image processing library"),
                ("dlib", "Machine learning library with face recognition"),
            ],
            "machine learning": [
                ("scikit-learn", "Machine learning library"),
                ("tensorflow", "Deep learning framework"),
                ("torch", "PyTorch deep learning framework"),
                ("keras", "High-level neural networks API"),
                ("xgboost", "Gradient boosting framework"),
                ("lightgbm", "Gradient boosting framework"),
            ],
            "deep learning": [
                ("tensorflow", "Deep learning framework"),
                ("torch", "PyTorch deep learning framework"),
                ("keras", "High-level neural networks API"),
                ("pytorch-lightning", "PyTorch wrapper"),
            ],
            "web scraping": [
                ("requests", "HTTP library"),
                ("beautifulsoup4", "HTML/XML parser"),
                ("selenium", "Web browser automation"),
                ("scrapy", "Web crawling framework"),
                ("httpx", "Async HTTP client"),
            ],
            "data science": [
                ("pandas", "Data manipulation library"),
                ("numpy", "Numerical computing library"),
                ("matplotlib", "Plotting library"),
                ("seaborn", "Statistical visualization"),
                ("jupyter", "Interactive computing"),
            ],
            "web development": [
                ("flask", "Micro web framework"),
                ("django", "Full-featured web framework"),
                ("fastapi", "Modern API framework"),
                ("starlette", "ASGI framework"),
                ("bottle", "Micro web framework"),
            ],
            "api": [
                ("fastapi", "Modern API framework"),
                ("flask", "Micro web framework"),
                ("django-rest-framework", "REST API for Django"),
                ("connexion", "OpenAPI-first framework"),
            ],
            "database": [
                ("sqlalchemy", "SQL toolkit"),
                ("psycopg2-binary", "PostgreSQL adapter"),
                ("mysql-connector-python", "MySQL driver"),
                ("pymongo", "MongoDB driver"),
                ("redis", "Redis client"),
            ],
            "testing": [
                ("pytest", "Testing framework"),
                ("unittest2", "Enhanced unittest"),
                ("nose2", "Testing framework"),
                ("mock", "Mock object library"),
                ("factory-boy", "Test fixtures"),
            ],
            "gui": [
                ("tkinter", "GUI toolkit (built-in)"),
                ("PyQt5", "Cross-platform GUI toolkit"),
                ("kivy", "Multi-platform GUI framework"),
                ("wxpython", "Native GUI toolkit"),
            ],
        }
        
        # Check for domain matches
        for domain, pkg_list in domain_packages.items():
            if any(word in query_lower for word in domain.split()):
                for pkg_name, description in pkg_list:
                    packages.append(self._get_package_info(pkg_name, description))
        
        return packages[:limit]
    
    def _search_by_category(self, query: str, limit: int) -> List[PackageInfo]:
        """Search by package categories."""
        # This would ideally use a package database or API
        # For now, return empty list
        return []
    
    def _get_popular_packages_for_domain(self, query: str, limit: int) -> List[PackageInfo]:
        """Get popular packages for specific domains."""
        query_lower = query.lower()
        
        if "vision" in query_lower or "image" in query_lower:
            return [
                self._get_package_info("opencv-python", "Computer vision library"),
                self._get_package_info("pillow", "Python Imaging Library"),
                self._get_package_info("scikit-image", "Image processing"),
            ]
        elif "ml" in query_lower or "machine" in query_lower:
            return [
                self._get_package_info("scikit-learn", "Machine learning library"),
                self._get_package_info("pandas", "Data manipulation"),
                self._get_package_info("numpy", "Numerical computing"),
            ]
        elif "web" in query_lower:
            return [
                self._get_package_info("requests", "HTTP library"),
                self._get_package_info("flask", "Web framework"),
                self._get_package_info("beautifulsoup4", "HTML parser"),
            ]
        
        return []
    
    def _get_package_info(self, package_name: str, description: str = "") -> PackageInfo:
        """Get detailed package information from PyPI."""
        try:
            url = f"https://pypi.org/pypi/{package_name}/json"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                info = data.get("info", {})
                
                return PackageInfo(
                    name=package_name,
                    description=description or info.get("summary", ""),
                    version=info.get("version", "unknown"),
                    author=info.get("author", ""),
                    homepage=info.get("home_page", ""),
                    keywords=info.get("keywords", "").split(",") if info.get("keywords") else []
                )
            else:
                # Fallback for when API is unavailable
                return PackageInfo(
                    name=package_name,
                    description=description,
                    version="latest",
                    author="",
                    homepage="",
                    keywords=[]
                )
                
        except Exception as e:
            if self.verbose:
                console.print(f"[yellow]Warning: Could not fetch info for {package_name}: {e}[/yellow]")
            
            return PackageInfo(
                name=package_name,
                description=description,
                version="unknown",
                author="",
                homepage="",
                keywords=[]
            )
    
    def get_package_details(self, package_name: str) -> Optional[PackageInfo]:
        """Get detailed information about a specific package."""
        return self._get_package_info(package_name)
    
    def get_similar_packages(self, package_name: str, limit: int = 5) -> List[PackageInfo]:
        """Find packages similar to the given package."""
        # This would ideally use package similarity algorithms
        # For now, return empty list
        return []
    
    def validate_package_exists(self, package_name: str) -> bool:
        """Check if a package exists on PyPI."""
        try:
            url = f"https://pypi.org/pypi/{package_name}/json"
            response = self.session.get(url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False