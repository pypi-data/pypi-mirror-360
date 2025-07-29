# CodeCheq

A powerful library for analyzing code security using Large Language Models (LLMs). This tool helps identify potential security vulnerabilities, code smells, and best practice violations in your codebase.

## Features

- 🔍 Evidence-based code analysis using LLMs
- 🛡️ Security vulnerability detection
- 🔧 **Automatic vulnerability patching** (NEW!)
- 🔐 **API Key Authentication** (NEW!)
- 📊 Detailed analysis reports
- 🔄 Support for multiple LLM providers (OpenAI, Anthropic)
- 📝 Customizable analysis prompts
- 🎯 Multiple output formats (JSON, HTML, Text)
- 🚀 Easy-to-use CLI interface
- 🔒 HIPAA and healthcare compliance analysis

## Installation

### From PyPI

```bash
pip install codecheq
```

### From Source

```bash
# Clone the repository
git clone https://github.com/CalBearKen/aioniq_codecheq.git
cd codecheq

# Install in editable mode
pip install -e .
```

## Quick Start

### Using the Library

```python
from codecheq import CodeAnalyzer, VulnerabilityPatcher

# Initialize the analyzer
analyzer = CodeAnalyzer(provider="openai", model="gpt-4")

# Analyze a file
results = analyzer.analyze_file("path/to/your/file.py")

# Print results
for issue in results.issues:
    print(f"Severity: {issue.severity}")
    print(f"Message: {issue.message}")
    print(f"Location: {issue.location}")
    print(f"Description: {issue.description}")
    print(f"Recommendation: {issue.recommendation}")
    print("---")

# Automatically patch vulnerabilities
patcher = VulnerabilityPatcher(provider="openai", model="gpt-4")
patch_result = patcher.patch_file("path/to/your/file.py", results)

if patch_result["success"]:
    print(f"Patched file saved to: {patch_result['output_file']}")
    print(f"Fixed {len(patch_result['issues_fixed'])} vulnerabilities")
```

### Using the CLI

#### After Installation

If you've installed the package (either from PyPI or in editable mode), you can use the CLI directly:

```bash
# Analyze a single file
codecheq file.py

# Analyze a directory
codecheq directory/

# Generate HTML report
codecheq file.py --format html --output report.html

# Use specific model
codecheq file.py --model gpt-4

# Analyze and automatically patch vulnerabilities
codecheq patch file.py

# Patch vulnerabilities in a directory
codecheq patch directory/ --output-dir patched_code
```

#### Without Installation

If you haven't installed the package, you can use the provided scripts:

```bash
# Using the Python script
python codecheq.py file.py

# Using the batch file (Windows)
codecheq.bat file.py

# Using the run script
python run_codecheq.py file.py
```

## Configuration

The library can be configured using environment variables or a configuration file:

```bash
# Environment variables
export OPENAI_API_KEY="your-api-key"
export ANTHROPIC_API_KEY="your-api-key"
export CODECHEQ_MODEL="gpt-4"
export CODECHEQ_API_TOKEN="sk-your-token-here"
export CODECHEQ_TOKEN_PORTAL_URL="http://localhost:5000"
```

Or create a `.env` file:

```env
OPENAI_API_KEY=your-api-key
ANTHROPIC_API_KEY=your-api-key
CODECHEQ_MODEL=gpt-4
CODECHEQ_API_TOKEN=sk-your-token-here
CODECHEQ_TOKEN_PORTAL_URL=http://localhost:5000
```

## Advanced Usage

### Custom Analysis Prompts

```python
from codecheq import CodeAnalyzer, PromptTemplate

# Create custom prompt
custom_prompt = PromptTemplate(
    template="""Analyze the following code for {analysis_type}:
    {code}
    
    Focus on:
    {focus_areas}
    """,
    variables=["analysis_type", "code", "focus_areas"]
)

# Use custom prompt
analyzer = CodeAnalyzer(prompt=custom_prompt)
```

### Batch Analysis

```python
from codecheq import BatchAnalyzer

# Initialize batch analyzer
batch = BatchAnalyzer()

# Add files to analyze
batch.add_file("file1.py")
batch.add_file("file2.py")
batch.add_directory("src/")

# Run analysis
results = batch.analyze()

# Export results
results.export_html("report.html")
```

### API Key Authentication

CodeCheq now supports API key authentication for enhanced security. This feature integrates with the API Token Portal to verify users before allowing patch operations.

#### Setup Authentication

1. **Start the Token Portal:**
   ```bash
   cd APITokenPortal
   npm install
   npm run dev
   ```

2. **Create an API Token:**
   - Visit http://localhost:5000 in your browser
   - Sign in with your account
   - Go to the API Tokens section
   - Create a new token
   - Copy the token (starts with 'sk-')

3. **Configure CodeCheq:**
   ```bash
   # Set environment variable
   export CODECHEQ_API_TOKEN="sk-your-token-here"
   
   # Or use command line parameter
   codecheq patch --api-token "sk-your-token-here" file.py
   ```

#### Using Authentication

```python
from codecheq import VulnerabilityPatcher, TokenVerifier

# Verify token before using
verifier = TokenVerifier(base_url="http://localhost:5000")
result = verifier.verify_token("sk-your-token-here")
print(f"Authenticated as: {result['user']['email']}")

# Use patcher with authentication
patcher = VulnerabilityPatcher(
    provider="openai",
    model="gpt-4",
    api_token="sk-your-token-here",
    require_auth=True,  # This requires authentication
    output_dir="patched_code"
)

# Patch with authentication
patch_result = patcher.patch_file("vulnerable_file.py", analysis_result)
```

#### CLI Authentication

```bash
# Verify your token
codecheq verify-token sk-your-token-here

# Patch with authentication
codecheq patch --require-auth --api-token sk-your-token-here file.py

# Analyze with optional authentication
codecheq analyze --require-auth --api-token sk-your-token-here directory/
```

**Authentication Features:**
- 🔐 Secure token verification with the Token Portal
- ⚡ Token caching for performance
- 🛡️ Required authentication for patch operations
- 🔄 Optional authentication for analysis
- 📊 User information and token status display

### Automatic Vulnerability Patching

The patcher automatically fixes security vulnerabilities found by CodeCheq:

```python
from codecheq import VulnerabilityPatcher

# Initialize patcher
patcher = VulnerabilityPatcher(
    provider="openai",
    model="gpt-4",
    output_dir="patched_code"
)

# Patch a single file
patch_result = patcher.patch_file("vulnerable_file.py", analysis_result)

# Patch multiple files
patch_results = patcher.patch_directory("src/", analysis_results_dict)

# Generate patch report
report = patcher.create_patch_report(patch_results)
print(report)
```

**Key Features:**
- 🔧 Automatically fixes SQL injection, command injection, and other vulnerabilities
- 🛡️ Preserves code functionality while improving security
- 📁 Saves patched files to a separate directory
- 📊 Generates detailed patching reports
- ⚠️ Skips fixes that require broader codebase context
- 🔐 **Now with optional API key authentication**

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/codecheq.git
cd codecheq

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

This project is licensed under the Apache License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all the contributors who have helped shape this project
- Inspired by various code analysis tools and security best practices 