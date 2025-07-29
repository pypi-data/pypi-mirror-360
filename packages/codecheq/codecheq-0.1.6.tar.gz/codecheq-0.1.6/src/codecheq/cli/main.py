"""
LLM Code Analyzer CLI

This module provides the command-line interface for the LLM Code Analyzer.
"""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..analyzer import CodeAnalyzer
from ..models.analysis_result import Severity
from ..utils.file_filter import get_analyzeable_files, get_file_language, SUPPORTED_EXTENSIONS

app = typer.Typer(help="LLM Code Analyzer CLI")
console = Console()


@app.command()
def analyze(
    path: Path = typer.Argument(..., help="Path to file or directory to analyze"),
    provider: str = typer.Option("openai", help="LLM provider (openai or anthropic)"),
    model: str = typer.Option("gpt-4", help="Model to use for analysis"),
    output: Optional[Path] = typer.Option(None, help="Output file path"),
    format: str = typer.Option("text", help="Output format (text, json, or html)"),
    api_key: Optional[str] = typer.Option(None, help="API key for the provider"),
):
    """Analyze code for security vulnerabilities using LLMs."""
    try:
        # Initialize analyzer
        analyzer = CodeAnalyzer(
            provider=provider,
            model=model,
            api_key=api_key,
        )

        # Analyze file or directory
        if path.is_file():
            language = get_file_language(path)
            console.print(f"Analyzing file: {path} ({language})")
            result = analyzer.analyze_file(path)
        else:
            console.print(f"Analyzing directory: {path}")
            # Show what files will be analyzed
            analyzeable_files = get_analyzeable_files(path)
            if analyzeable_files:
                console.print(f"Found {len(analyzeable_files)} files to analyze:")
                for file_path in analyzeable_files[:5]:  # Show first 5 files
                    language = get_file_language(file_path)
                    console.print(f"  - {file_path} ({language})")
                if len(analyzeable_files) > 5:
                    console.print(f"  ... and {len(analyzeable_files) - 5} more files")
            result = analyzer.analyze_directory(path)

        # Output results
        if output:
            if format == "json":
                output.write_text(result.to_json())
            elif format == "html":
                output.write_text(result.to_html())
            else:
                output.write_text(str(result))
        else:
            # Display results in console
            if format == "json":
                console.print_json(result.to_json())
            elif format == "html":
                console.print(result.to_html())
            else:
                display_results(result)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def list_files(
    path: Path = typer.Argument(..., help="Path to directory to list analyzeable files"),
    show_all: bool = typer.Option(False, "--all", "-a", help="Show all files instead of just first 10"),
):
    """List all files that would be analyzed in a directory."""
    try:
        if not path.is_dir():
            console.print(f"[red]Error:[/red] {path} is not a directory")
            raise typer.Exit(1)
            
        analyzeable_files = get_analyzeable_files(path)
        
        if not analyzeable_files:
            console.print(f"No analyzeable files found in {path}")
            return
            
        console.print(f"Found {len(analyzeable_files)} analyzeable files in {path}:")
        console.print()
        
        # Group files by language
        files_by_language = {}
        for file_path in analyzeable_files:
            language = get_file_language(file_path)
            if language not in files_by_language:
                files_by_language[language] = []
            files_by_language[language].append(file_path)
        
        # Display files grouped by language
        for language, files in sorted(files_by_language.items()):
            console.print(f"[bold blue]{language}[/bold blue] ({len(files)} files):")
            display_count = len(files) if show_all else min(10, len(files))
            for file_path in files[:display_count]:
                console.print(f"  {file_path}")
            if not show_all and len(files) > 10:
                console.print(f"  ... and {len(files) - 10} more files")
            console.print()
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def supported_types():
    """List all supported file types and extensions."""
    console.print("[bold blue]Supported File Types:[/bold blue]")
    console.print()
    
    # Group extensions by category
    categories = {
        "Python": [ext for ext in SUPPORTED_EXTENSIONS if ext in [".py", ".pyx", ".pxd"]],
        "JavaScript/TypeScript": [ext for ext in SUPPORTED_EXTENSIONS if ext in [".js", ".jsx", ".ts", ".tsx"]],
        "Java": [ext for ext in SUPPORTED_EXTENSIONS if ext in [".java"]],
        "C/C++": [ext for ext in SUPPORTED_EXTENSIONS if ext in [".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx"]],
        "Go": [ext for ext in SUPPORTED_EXTENSIONS if ext in [".go"]],
        "Rust": [ext for ext in SUPPORTED_EXTENSIONS if ext in [".rs"]],
        "Ruby": [ext for ext in SUPPORTED_EXTENSIONS if ext in [".rb"]],
        "PHP": [ext for ext in SUPPORTED_EXTENSIONS if ext in [".php"]],
        "C#": [ext for ext in SUPPORTED_EXTENSIONS if ext in [".cs"]],
        "Swift": [ext for ext in SUPPORTED_EXTENSIONS if ext in [".swift"]],
        "Kotlin": [ext for ext in SUPPORTED_EXTENSIONS if ext in [".kt", ".kts"]],
        "Scala": [ext for ext in SUPPORTED_EXTENSIONS if ext in [".scala"]],
        "Shell Scripts": [ext for ext in SUPPORTED_EXTENSIONS if ext in [".sh", ".bash", ".zsh", ".fish"]],
        "PowerShell": [ext for ext in SUPPORTED_EXTENSIONS if ext in [".ps1", ".psm1"]],
        "Configuration": [ext for ext in SUPPORTED_EXTENSIONS if ext in [".conf", ".config", ".ini", ".yaml", ".yml", ".json", ".xml", ".toml", ".env"]],
        "Web": [ext for ext in SUPPORTED_EXTENSIONS if ext in [".html", ".htm", ".css", ".scss", ".sass", ".less"]],
        "SQL": [ext for ext in SUPPORTED_EXTENSIONS if ext in [".sql"]],
        "Docker": [ext for ext in SUPPORTED_EXTENSIONS if ext in ["Dockerfile", ".dockerfile"]],
        "Terraform": [ext for ext in SUPPORTED_EXTENSIONS if ext in [".tf", ".tfvars"]],
        "Ansible": [ext for ext in SUPPORTED_EXTENSIONS if ext in [".yml", ".yaml"]],
        "Makefiles": [ext for ext in SUPPORTED_EXTENSIONS if ext in ["Makefile", "makefile", ".mk"]],
    }
    
    for category, extensions in categories.items():
        if extensions:
            console.print(f"[bold]{category}:[/bold] {', '.join(extensions)}")
    
    console.print()
    console.print(f"Total supported extensions: {len(SUPPORTED_EXTENSIONS)}")


def display_results(result):
    """Display analysis results in a formatted table."""
    # Create table
    table = Table(title="Code Analysis Results")
    table.add_column("Severity", style="bold")
    table.add_column("Location")
    table.add_column("Message")
    table.add_column("Description")

    # Add issues to table
    for issue in result.issues:
        severity_color = {
            Severity.ERROR: "red",
            Severity.WARNING: "yellow",
            Severity.INFO: "blue",
        }[issue.severity]

        table.add_row(
            f"[{severity_color}]{issue.severity}[/{severity_color}]",
            f"{issue.location.path}:{issue.location.start_line}",
            issue.message,
            issue.description,
        )

    # Display table
    console.print(table)

    # Display summary
    console.print("\n[bold]Summary:[/bold]")
    console.print(f"Total issues: {len(result.issues)}")
    for severity in Severity:
        count = len(result.get_issues_by_severity(severity))
        console.print(f"{severity.value}: {count}")


if __name__ == "__main__":
    app() 