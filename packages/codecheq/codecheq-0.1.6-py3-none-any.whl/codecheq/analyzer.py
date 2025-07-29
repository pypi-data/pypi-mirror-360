"""
LLM Code Analyzer Module

This module provides the main functionality for analyzing code using LLMs.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

import openai
from anthropic import Anthropic
from dotenv import load_dotenv

from .models.analysis_result import AnalysisResult, Issue, Location, Severity
from .prompt import PromptTemplate, get_default_prompt
from .utils.file_filter import get_analyzeable_files, get_file_language


class CodeAnalyzer:
    """Main class for analyzing code using LLMs."""

    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4",
        prompt: Optional[PromptTemplate] = None,
        api_key: Optional[str] = None,
    ):
        """Initialize the code analyzer.

        Args:
            provider: The LLM provider to use ("openai" or "anthropic")
            model: The model to use for analysis
            prompt: Custom prompt template (optional)
            api_key: API key for the provider (optional)
        """
        load_dotenv()

        self.provider = provider.lower()
        self.model = model
        self.prompt = prompt or get_default_prompt()

        # Set up API client
        if self.provider == "openai":
            self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        elif self.provider == "anthropic":
            self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def analyze_file(self, file_path: Union[str, Path]) -> AnalysisResult:
        """Analyze a single file.

        Args:
            file_path: Path to the file to analyze

        Returns:
            AnalysisResult containing the analysis results
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        return self.analyze_code(code, str(file_path))
        
    def analyze_directory(self, directory_path: Union[str, Path]) -> AnalysisResult:
        """Analyze all supported files in a directory recursively.

        Args:
            directory_path: Path to the directory to analyze

        Returns:
            AnalysisResult containing the analysis results for all files
        """
        directory_path = Path(directory_path)
        if not directory_path.exists() or not directory_path.is_dir():
            raise NotADirectoryError(f"Directory not found: {directory_path}")
            
        # Find all analyzeable files in the directory
        analyzeable_files = get_analyzeable_files(directory_path)
        
        if not analyzeable_files:
            print(f"No analyzeable files found in {directory_path}")
            return AnalysisResult()
            
        # Analyze each file and combine results
        combined_result = AnalysisResult()
        for file_path in analyzeable_files:
            try:
                language = get_file_language(file_path)
                print(f"Analyzing {file_path} ({language})...")
                file_result = self.analyze_file(file_path)
                combined_result.issues.extend(file_result.issues)
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
                
        return combined_result

    def analyze_code(self, code: str, file_path: str) -> AnalysisResult:
        """Analyze a code string.

        Args:
            code: The code to analyze
            file_path: Path to the file (for reference)

        Returns:
            AnalysisResult containing the analysis results
        """
        # Add line numbers to the code for better accuracy
        lines = code.split('\n')
        numbered_code = '\n'.join(f"{i+1:3d}: {line}" for i, line in enumerate(lines))
        
        # Add context about the file being analyzed
        context = f"Analyzing file: {file_path}\n\nCode to analyze (with line numbers):\n{numbered_code}"
        
        # Format the prompt
        prompt = self.prompt.format(code=context)

        # Get analysis from LLM
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            analysis_text = response.choices[0].message.content
        else:  # anthropic
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}],
            )
            analysis_text = response.content[0].text

        # Parse the response
        try:
            issues = json.loads(analysis_text)
            if not isinstance(issues, list):
                issues = [issues]
        except json.JSONDecodeError:
            # If the response is not valid JSON, try to extract JSON objects
            issues = self._extract_json_objects(analysis_text)

        # Convert to AnalysisResult
        result = AnalysisResult()
        for issue in issues:
            try:
                result.add_issue(
                    Issue(
                        check_id=issue["check_id"],
                        message=issue["extra"]["message"],
                        severity=Severity(issue["extra"]["severity"]),
                        location=Location(
                            path=issue["path"],
                            start_line=issue["start"]["line"],
                            end_line=issue["end"]["line"],
                            start_column=issue["start"].get("col"),
                            end_column=issue["end"].get("col"),
                        ),
                        description=issue["extra"]["metadata"]["description"],
                        recommendation=issue["extra"]["metadata"]["recommendation"],
                        code_snippet=issue["extra"]["lines"],
                        metadata=issue["extra"]["metadata"],
                    )
                )
            except (KeyError, ValueError) as e:
                print(f"Error parsing issue: {e}")
                continue

        return result

    def _extract_json_objects(self, text: str) -> List[Dict]:
        """Extract JSON objects from text that might contain multiple objects.

        Args:
            text: Text containing JSON objects

        Returns:
            List of parsed JSON objects
        """
        objects = []
        current_object = ""
        brace_count = 0

        for char in text:
            if char == "{":
                brace_count += 1
                current_object += char
            elif char == "}":
                brace_count -= 1
                current_object += char
                if brace_count == 0:
                    try:
                        objects.append(json.loads(current_object))
                    except json.JSONDecodeError:
                        pass
                    current_object = ""
            elif brace_count > 0:
                current_object += char

        return objects 