"""
Code Vulnerability Patcher Module

This module provides functionality to automatically patch security vulnerabilities
found by CodeCheq analysis using LLM-based code correction.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import openai
from dotenv import load_dotenv

from .models.analysis_result import AnalysisResult, Issue, Severity
from .prompt import PromptTemplate
from .auth import TokenVerifier, TokenVerificationError, InvalidTokenError
from .auth.config import AuthConfig


class VulnerabilityPatcher:
    """Main class for patching security vulnerabilities in code."""

    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4.1",
        api_key: Optional[str] = None,
        output_dir: str = "patched_code",
        api_token: Optional[str] = None,
        token_portal_url: Optional[str] = None,
        require_auth: bool = True,
    ):
        """Initialize the vulnerability patcher.

        Args:
            provider: The LLM provider to use ("openai" or "anthropic")
            model: The model to use for patching
            api_key: API key for the provider (optional)
            output_dir: Directory to save patched files
            api_token: API token for authentication with Token Portal
            token_portal_url: URL of the Token Portal
            require_auth: Whether authentication is required for patching
        """
        load_dotenv()

        self.provider = provider.lower()
        self.model = model
        self.output_dir = Path(output_dir)
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)

        # Set up API client
        if self.provider == "openai":
            self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        # Initialize authentication
        self.auth_config = AuthConfig(
            api_token=api_token,
            token_portal_url=token_portal_url,
            require_auth=require_auth
        )
        
        if self.auth_config.has_token():
            self.token_verifier = TokenVerifier(
                base_url=self.auth_config.token_portal_url,
                cache_duration=self.auth_config.cache_duration
            )
        else:
            self.token_verifier = None

        # Initialize prompt template
        self.patch_prompt = self._get_patch_prompt()

    def _verify_authentication(self) -> None:
        """Verify authentication before allowing patch operations.
        
        Raises:
            TokenVerificationError: If authentication fails
            InvalidTokenError: If token is invalid
        """
        if not self.auth_config.require_auth:
            return
            
        if not self.auth_config.has_token():
            raise InvalidTokenError(
                "Authentication is required but no API token is provided. "
                "Please set CODECHEQ_API_TOKEN environment variable or pass api_token parameter."
            )
            
        if not self.token_verifier:
            raise TokenVerificationError("Token verifier not initialized")
            
        try:
            self.token_verifier.verify_token(self.auth_config.api_token)
        except TokenVerificationError as e:
            raise TokenVerificationError(
                f"Authentication failed: {str(e)}. "
                "Please check your API token and ensure the Token Portal is accessible."
            )

    def _get_patch_prompt(self) -> PromptTemplate:
        """Get the prompt template for vulnerability patching."""
        template = """You are a security-focused code patcher. Your task is to fix security vulnerabilities in the provided code.

CRITICAL REQUIREMENTS:
1. ONLY fix the specific vulnerabilities identified in the analysis results
2. Do NOT make any other changes to the code
3. If a fix requires understanding the broader codebase context (imports, dependencies, class definitions, etc.), return an error
4. Keep the original code structure and functionality intact
5. Use secure coding practices and industry standards
6. PRESERVE ALL INDENTATION EXACTLY as shown in the original code

ANALYSIS RESULTS:
{analysis_results}

ORIGINAL CODE (with line numbers):
{original_code}

INSTRUCTIONS:
- Fix ONLY the vulnerabilities listed in the analysis results
- If you cannot fix a vulnerability without broader context, mark it as "REQUIRES_CONTEXT"
- Preserve all comments, formatting, and non-vulnerable code
- Ensure the patched code is functionally equivalent to the original
- Use secure alternatives for vulnerable patterns
- CRITICAL: Maintain exact indentation levels - each indented line should have the same number of spaces as the original

RESPONSE FORMAT:
Return the complete patched code inside a markdown code block like this:

```python
# Your patched code here with all indentation preserved
```

CRITICAL: 
- Use the exact markdown code block format above
- Preserve all indentation exactly as it appears in the original code
- If any vulnerabilities cannot be fixed due to context requirements, include a note explaining why
"""
        return PromptTemplate(template=template, variables=["analysis_results", "original_code"])

    def patch_file(
        self, 
        file_path: Union[str, Path], 
        analysis_result: AnalysisResult
    ) -> Dict[str, Union[str, List[str], bool]]:
        """Patch vulnerabilities in a single file.

        Args:
            file_path: Path to the file to patch
            analysis_result: AnalysisResult containing vulnerabilities to fix

        Returns:
            Dictionary containing patching results
        """
        # Verify authentication before proceeding
        try:
            self._verify_authentication()
        except (TokenVerificationError, InvalidTokenError) as e:
            return {
                "success": False,
                "message": f"Authentication failed: {str(e)}",
                "patched_code": "",
                "issues_fixed": [],
                "issues_skipped": [],
                "auth_error": True
            }
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read original code
        with open(file_path, "r", encoding="utf-8") as f:
            original_code = f.read()

        # Filter issues by severity (focus on ERROR and WARNING)
        critical_issues = [
            issue for issue in analysis_result.issues 
            if issue.severity in [Severity.ERROR, Severity.WARNING]
        ]

        if not critical_issues:
            return {
                "success": True,
                "message": "No critical vulnerabilities found to patch",
                "patched_code": original_code,
                "issues_fixed": [],
                "issues_skipped": []
            }

        # Format analysis results for the prompt
        analysis_text = self._format_analysis_results(critical_issues)

        # Generate patch prompt with original code (no line numbers needed for markdown blocks)
        prompt = self.patch_prompt.format(
            analysis_results=analysis_text,
            original_code=original_code
        )

        try:
            # Get patched code from LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=4000,
            )
            patched_code = response.choices[0].message.content

            # Extract the patched code from the response
            patched_code = self._extract_patched_code(patched_code, original_code)

            # Validate that the patched code has proper indentation
            if not self._validate_code_structure(patched_code):
                return {
                    "success": False,
                    "message": "Failed to extract properly formatted code - indentation may be corrupted",
                    "patched_code": original_code,
                    "issues_fixed": [],
                    "issues_skipped": [issue.check_id for issue in critical_issues]
                }

            # Save patched file
            output_file = self.output_dir / file_path.name
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(patched_code)

            return {
                "success": True,
                "message": f"Successfully patched {len(critical_issues)} vulnerabilities",
                "patched_code": patched_code,
                "output_file": str(output_file),
                "issues_fixed": [issue.check_id for issue in critical_issues],
                "issues_skipped": []
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error patching file: {str(e)}",
                "patched_code": original_code,
                "issues_fixed": [],
                "issues_skipped": [issue.check_id for issue in critical_issues]
            }

    def _format_analysis_results(self, issues: List[Issue]) -> str:
        """Format analysis results for the prompt."""
        formatted_results = []
        
        for i, issue in enumerate(issues, 1):
            formatted_results.append(f"""
VULNERABILITY {i}:
- Check ID: {issue.check_id}
- Severity: {issue.severity.value}
- Location: Line {issue.location.start_line}
- Message: {issue.message}
- Description: {issue.description}
- Recommendation: {issue.recommendation}
- Code Snippet: {issue.code_snippet}
""")
        
        return "\n".join(formatted_results)

    def _extract_patched_code(self, response: str, original_code: str) -> str:
        """Extract the patched code from the LLM response."""
        # First, try to extract from markdown code blocks
        code_block_pattern = r'```(?:python)?\s*\n(.*?)\n```'
        code_block_match = re.search(code_block_pattern, response, re.DOTALL)
        
        if code_block_match:
            # Extract code from the markdown code block
            patched_code = code_block_match.group(1).strip()
            return patched_code
        
        # Fallback: Look for the patched code section (old format)
        if "PATCHED CODE:" in response:
            # Extract everything after "PATCHED CODE:"
            patched_section = response.split("PATCHED CODE:")[-1].strip()
            
            # Remove line numbers and return clean code
            lines = patched_section.split('\n')
            clean_lines = []
            
            for line in lines:
                # Remove line number prefix (e.g., "  1: ")
                if re.match(r'^\s*\d+:\s*', line):
                    # Extract the code part after the line number, preserving indentation
                    code_part = re.sub(r'^\s*\d+:\s*', '', line)
                    clean_lines.append(code_part)
                else:
                    # Keep lines that don't have line numbers
                    clean_lines.append(line)
            
            return '\n'.join(clean_lines)
        
        # If no clear section marker, try to extract code from the response
        # This is a fallback for cases where the LLM doesn't follow the exact format
        lines = response.split('\n')
        code_lines = []
        in_code_block = False
        
        for line in lines:
            # Skip lines that are clearly not code (prompts, explanations, etc.)
            if any(skip in line.lower() for skip in [
                "patch", "vulnerability", "analysis", "result", "instruction", 
                "requirement", "format", "response", "note", "explanation"
            ]):
                continue
            
            # If line has a line number prefix, extract the code
            if re.match(r'^\s*\d+:\s*', line):
                code_part = re.sub(r'^\s*\d+:\s*', '', line)
                code_lines.append(code_part)
                in_code_block = True
            elif in_code_block and line.strip() and not line.startswith('#'):
                # Include non-empty lines that aren't comments, preserving indentation
                code_lines.append(line)
            elif in_code_block and not line.strip():
                # Include empty lines within code blocks to preserve structure
                code_lines.append(line)
        
        # If we couldn't extract code properly, fall back to original
        if not code_lines:
            return original_code
        
        # Check if the extracted code has proper indentation
        extracted_code = '\n'.join(code_lines)
        if not self._has_proper_indentation(extracted_code):
            # Fall back to original code if indentation is corrupted
            return original_code
        
        return extracted_code

    def _validate_code_structure(self, code: str) -> bool:
        """Validate that the extracted code has proper Python structure."""
        lines = code.split('\n')
        
        # Check for basic Python syntax indicators
        has_def = any('def ' in line for line in lines)
        has_import = any('import ' in line for line in lines)
        has_indentation = any(line.startswith('    ') or line.startswith('\t') for line in lines if line.strip())
        
        # If it's a Python file, it should have some of these characteristics
        if has_def or has_import:
            # Check that indentation is consistent
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('#'):
                    # Check for proper indentation after colons
                    if i > 0 and ':' in lines[i-1] and not lines[i-1].strip().endswith(':'):
                        continue
                    if ':' in lines[i-1] and lines[i-1].strip().endswith(':'):
                        # Next line should be indented
                        if i < len(lines) and lines[i].strip() and not lines[i].startswith((' ', '\t')):
                            return False
        
        return True

    def _has_proper_indentation(self, code: str) -> bool:
        """Check if the code has proper indentation structure."""
        lines = code.split('\n')
        
        # Check if there are any indented lines
        has_indentation = False
        for line in lines:
            if line.strip() and line.startswith(('    ', '\t')):
                has_indentation = True
                break
        
        # If no indentation at all, it's probably corrupted
        if not has_indentation:
            return False
        
        # Check for basic Python structure indicators
        has_def = any('def ' in line for line in lines)
        has_class = any('class ' in line for line in lines)
        has_if = any('if ' in line for line in lines)
        has_for = any('for ' in line for line in lines)
        has_while = any('while ' in line for line in lines)
        
        # If it has Python constructs, it should have indentation
        if any([has_def, has_class, has_if, has_for, has_while]):
            return has_indentation
        
        return True

    def patch_directory(
        self, 
        directory_path: Union[str, Path], 
        analysis_results: Dict[str, AnalysisResult]
    ) -> Dict[str, Dict]:
        """Patch vulnerabilities in multiple files.

        Args:
            directory_path: Path to the directory containing files
            analysis_results: Dictionary mapping file paths to AnalysisResult objects

        Returns:
            Dictionary containing patching results for each file
        """
        # Verify authentication before proceeding
        try:
            self._verify_authentication()
        except (TokenVerificationError, InvalidTokenError) as e:
            return {
                "auth_error": {
                    "success": False,
                    "message": f"Authentication failed: {str(e)}",
                    "issues_fixed": [],
                    "issues_skipped": [],
                    "auth_error": True
                }
            }
        
        directory_path = Path(directory_path)
        results = {}

        for file_path, analysis_result in analysis_results.items():
            file_path = Path(file_path)
            
            # Skip if file doesn't exist
            if not file_path.exists():
                results[str(file_path)] = {
                    "success": False,
                    "message": "File not found",
                    "issues_fixed": [],
                    "issues_skipped": []
                }
                continue

            # Patch the file
            result = self.patch_file(file_path, analysis_result)
            results[str(file_path)] = result

        return results

    def create_patch_report(self, results: Dict[str, Dict]) -> str:
        """Create a summary report of the patching results.

        Args:
            results: Results from patch_directory or patch_file

        Returns:
            Formatted report string
        """
        report_lines = [
            "CodeCheq Vulnerability Patching Report",
            "=" * 40,
            ""
        ]

        total_files = len(results)
        successful_patches = sum(1 for r in results.values() if r.get("success", False))
        total_issues_fixed = sum(len(r.get("issues_fixed", [])) for r in results.values())
        total_issues_skipped = sum(len(r.get("issues_skipped", [])) for r in results.values())

        report_lines.extend([
            f"Summary:",
            f"- Total files processed: {total_files}",
            f"- Successfully patched: {successful_patches}",
            f"- Total vulnerabilities fixed: {total_issues_fixed}",
            f"- Total vulnerabilities skipped: {total_issues_skipped}",
            ""
        ])

        for file_path, result in results.items():
            report_lines.extend([
                f"File: {file_path}",
                f"Status: {'✓ Success' if result.get('success') else '✗ Failed'}",
                f"Message: {result.get('message', 'N/A')}",
            ])
            
            if result.get("output_file"):
                report_lines.append(f"Patched file: {result['output_file']}")
            
            if result.get("issues_fixed"):
                report_lines.append(f"Fixed issues: {', '.join(result['issues_fixed'])}")
            
            if result.get("issues_skipped"):
                report_lines.append(f"Skipped issues: {', '.join(result['issues_skipped'])}")
            
            report_lines.append("")

        return "\n".join(report_lines) 