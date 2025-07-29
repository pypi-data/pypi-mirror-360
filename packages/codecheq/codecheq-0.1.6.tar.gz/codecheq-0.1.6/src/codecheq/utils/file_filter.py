"""
File filtering utilities for the LLM Code Analyzer.

This module provides functionality to filter files for analysis,
excluding common boilerplate directories and supporting multiple
programming languages.
"""

import os
import re
from pathlib import Path
from typing import List, Set, Union


# Common directories and files to exclude
DEFAULT_EXCLUDE_DIRS = {
    # Python
    "__pycache__",
    "*.egg-info",
    "build",
    "dist",
    "develop-eggs",
    "downloads",
    "eggs",
    ".eggs",
    "lib",
    "lib64",
    "parts",
    "sdist",
    "var",
    "wheels",
    ".installed.cfg",
    
    # Virtual environments
    "venv",
    "env",
    "ENV",
    ".venv",
    ".env",
    
    # IDE and editor files
    ".idea",
    ".vscode",
    ".vs",
    "*.swp",
    "*.swo",
    "*~",
    
    # Testing and coverage
    ".coverage",
    "htmlcov",
    ".pytest_cache",
    ".tox",
    ".mypy_cache",
    
    # Version control
    ".git",
    ".svn",
    ".hg",
    
    # Node.js
    "node_modules",
    "npm-debug.log",
    "yarn-error.log",
    
    # Java
    "target",
    ".gradle",
    ".mvn",
    
    # C/C++
    "obj",
    "bin",
    "Debug",
    "Release",
    "x64",
    "x86",
    
    # Go
    "vendor",
    
    # Ruby
    "vendor/bundle",
    ".bundle",
    
    # PHP
    "vendor",
    "composer.lock",
    
    # Logs and temporary files
    "*.log",
    "*.tmp",
    "*.temp",
    ".DS_Store",
    "Thumbs.db",
    
    # Environment and config files
    ".env*",
    "*.env",
    
    # Documentation and build artifacts
    "docs/_build",
    "site",
    "_site",
    ".jekyll-cache",
}

# File extensions to include for analysis
SUPPORTED_EXTENSIONS = {
    # Python
    ".py",
    ".pyx",
    ".pxd",
    
    # JavaScript/TypeScript
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    
    # Java
    ".java",
    
    # C/C++
    ".c",
    ".cpp",
    ".cc",
    ".cxx",
    ".h",
    ".hpp",
    ".hxx",
    
    # Go
    ".go",
    
    # Rust
    ".rs",
    
    # Ruby
    ".rb",
    
    # PHP
    ".php",
    
    # C#
    ".cs",
    
    # Swift
    ".swift",
    
    # Kotlin
    ".kt",
    ".kts",
    
    # Scala
    ".scala",
    
    # Shell scripts
    ".sh",
    ".bash",
    ".zsh",
    ".fish",
    
    # PowerShell
    ".ps1",
    ".psm1",
    
    # Configuration files (security-relevant)
    ".conf",
    ".config",
    ".ini",
    ".yaml",
    ".yml",
    ".json",
    ".xml",
    ".toml",
    ".env",
    
    # Web files
    ".html",
    ".htm",
    ".css",
    ".scss",
    ".sass",
    ".less",
    
    # SQL
    ".sql",
    
    # Docker
    "Dockerfile",
    ".dockerfile",
    
    # Kubernetes
    ".yaml",
    ".yml",
    
    # Terraform
    ".tf",
    ".tfvars",
    
    # Ansible
    ".yml",
    ".yaml",
    
    # Makefiles
    "Makefile",
    "makefile",
    ".mk",
}

# Files to exclude by name pattern
EXCLUDE_FILES = {
    # Common files to skip
    "package-lock.json",
    "yarn.lock",
    "composer.lock",
    "Gemfile.lock",
    "Pipfile.lock",
    "poetry.lock",
    "requirements.txt",
    "setup.py",
    "pyproject.toml",
    "package.json",
    "tsconfig.json",
    "webpack.config.js",
    "babel.config.js",
    ".eslintrc.js",
    ".prettierrc",
    ".gitignore",
    ".gitattributes",
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "Makefile",
    "Dockerfile",
    ".dockerignore",
    ".env.example",
    ".env.template",
    "*.min.js",
    "*.min.css",
    "*.bundle.js",
    "*.bundle.css",
}


def should_skip_file(file_path: Union[str, Path]) -> bool:
    """
    Determine if a file should be skipped during analysis.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if the file should be skipped, False otherwise
    """
    file_path = Path(file_path)
    
    # Skip if file doesn't exist
    if not file_path.exists():
        return True
    
    # Skip directories
    if file_path.is_dir():
        return True
    
    # Check file extension
    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return True
    
    # Check if file name is in exclude list
    if file_path.name in EXCLUDE_FILES:
        return True
    
    # Check if file is in excluded directory
    for parent in file_path.parents:
        if parent.name in DEFAULT_EXCLUDE_DIRS:
            return True
    
    # Check for common patterns in path
    path_str = str(file_path).lower()
    for pattern in DEFAULT_EXCLUDE_DIRS:
        if pattern.startswith("*"):
            # Handle wildcard patterns
            if path_str.endswith(pattern[1:]):
                return True
        elif pattern in path_str:
            return True
    
    return False


def get_analyzeable_files(
    directory_path: Union[str, Path],
    exclude_patterns: Set[str] = None,
    include_extensions: Set[str] = None
) -> List[Path]:
    """
    Get all files in a directory that should be analyzed.
    
    Args:
        directory_path: Path to the directory to scan
        exclude_patterns: Additional patterns to exclude (optional)
        include_extensions: Additional file extensions to include (optional)
        
    Returns:
        List of file paths that should be analyzed
    """
    directory_path = Path(directory_path)
    
    if not directory_path.exists() or not directory_path.is_dir():
        raise NotADirectoryError(f"Directory not found: {directory_path}")
    
    # Combine exclude patterns
    all_exclude_patterns = DEFAULT_EXCLUDE_DIRS.copy()
    if exclude_patterns:
        all_exclude_patterns.update(exclude_patterns)
    
    # Combine include extensions
    all_extensions = SUPPORTED_EXTENSIONS.copy()
    if include_extensions:
        all_extensions.update(include_extensions)
    
    analyzeable_files = []
    
    # Walk through directory recursively
    for root, dirs, files in os.walk(directory_path):
        # Remove excluded directories from dirs list to prevent walking into them
        dirs[:] = [d for d in dirs if d not in all_exclude_patterns]
        
        for file in files:
            file_path = Path(root) / file
            
            # Skip if file should be excluded
            if should_skip_file(file_path):
                continue
            
            # Check if file extension is supported
            if file_path.suffix.lower() in all_extensions:
                analyzeable_files.append(file_path)
    
    return sorted(analyzeable_files)


def get_file_language(file_path: Union[str, Path]) -> str:
    """
    Determine the programming language of a file based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Programming language name
    """
    extension = Path(file_path).suffix.lower()
    
    language_map = {
        # Python
        ".py": "Python",
        ".pyx": "Cython",
        ".pxd": "Cython",
        
        # JavaScript/TypeScript
        ".js": "JavaScript",
        ".jsx": "React JSX",
        ".ts": "TypeScript",
        ".tsx": "React TypeScript",
        
        # Java
        ".java": "Java",
        
        # C/C++
        ".c": "C",
        ".cpp": "C++",
        ".cc": "C++",
        ".cxx": "C++",
        ".h": "C/C++ Header",
        ".hpp": "C++ Header",
        ".hxx": "C++ Header",
        
        # Go
        ".go": "Go",
        
        # Rust
        ".rs": "Rust",
        
        # Ruby
        ".rb": "Ruby",
        
        # PHP
        ".php": "PHP",
        
        # C#
        ".cs": "C#",
        
        # Swift
        ".swift": "Swift",
        
        # Kotlin
        ".kt": "Kotlin",
        ".kts": "Kotlin Script",
        
        # Scala
        ".scala": "Scala",
        
        # Shell scripts
        ".sh": "Shell",
        ".bash": "Bash",
        ".zsh": "Zsh",
        ".fish": "Fish",
        
        # PowerShell
        ".ps1": "PowerShell",
        ".psm1": "PowerShell Module",
        
        # Configuration files
        ".conf": "Configuration",
        ".config": "Configuration",
        ".ini": "INI Configuration",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".json": "JSON",
        ".xml": "XML",
        ".toml": "TOML",
        ".env": "Environment Variables",
        
        # Web files
        ".html": "HTML",
        ".htm": "HTML",
        ".css": "CSS",
        ".scss": "SCSS",
        ".sass": "Sass",
        ".less": "Less",
        
        # SQL
        ".sql": "SQL",
        
        # Docker
        "Dockerfile": "Dockerfile",
        ".dockerfile": "Dockerfile",
        
        # Terraform
        ".tf": "Terraform",
        ".tfvars": "Terraform Variables",
        
        # Ansible
        ".yml": "Ansible",
        ".yaml": "Ansible",
        
        # Makefiles
        "Makefile": "Makefile",
        "makefile": "Makefile",
        ".mk": "Makefile",
    }
    
    return language_map.get(extension, "Unknown") 