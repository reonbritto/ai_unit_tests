# Spring Boot Unit Test Generator - User Guide

A comprehensive Python-based system that automatically generates JUnit test cases for Spring Boot applications using Google Gemini AI.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [Features](#features)
6. [Architecture](#architecture)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Usage](#advanced-usage)

## Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini AI API key
- Maven or Gradle (for running tests)
- Git (for repository cloning)

### 1. Install Dependencies
```bash
# Windows
install.bat

# Linux/Mac
chmod +x install.sh
./install.sh
```

### 2. Set API Key
```bash
# Windows
set GEMINI_API_KEY=your-api-key-here

# Linux/Mac
export GEMINI_API_KEY="your-api-key-here"
```

### 3. Generate Tests
```bash
# For GitHub repository
python main.py --repo-url https://github.com/user/spring-boot-app

# For local project
python main.py --local-path /path/to/spring-boot-project
```

## Installation

### Automatic Installation
Run the provided installation script for your platform:

**Windows:**
```batch
install.bat
```

**Linux/Mac:**
```bash
chmod +x install.sh
./install.sh
```

### Manual Installation
```bash
pip install -r requirements.txt
```

### Verify Installation
```bash
python test_installation.py
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Your Google Gemini AI API key |

### Configuration Options

The system uses configuration from `config.py`. Key settings include:

```python
# Model settings
GEMINI_MODEL = "gemini-2.0-flash-exp"

# Test generation settings
MAX_ITERATIONS = 3
COVERAGE_THRESHOLD = 80.0

# Timeouts
TEST_EXECUTION_TIMEOUT = 300  # seconds
REPO_CLONE_TIMEOUT = 120      # seconds
```

## Usage

### Command Line Interface

```bash
python main.py [OPTIONS]
```

**Options:**
- `--repo-url URL`: GitHub repository URL
- `--local-path PATH`: Local project path
- `--api-key KEY`: Gemini AI API key (optional if set in environment)
- `--max-iterations N`: Maximum improvement iterations (default: 3)
- `--coverage-threshold N`: Target coverage percentage (default: 80.0)

**Examples:**

```bash
# Generate tests for Spring PetClinic
python main.py --repo-url https://github.com/spring-projects/spring-petclinic

# Generate tests for local project with custom settings
python main.py --local-path ./my-spring-app --max-iterations 5 --coverage-threshold 85

# Use custom API key
python main.py --repo-url https://github.com/user/app --api-key your-key-here
```

### Programmatic Usage

```python
from main import UnitTestGenerator

# Initialize generator
generator = UnitTestGenerator(
    repo_url="https://github.com/user/spring-boot-app",
    gemini_api_key="your-api-key"
)

# Generate tests
results = generator.generate_tests(
    max_iterations=3,
    coverage_threshold=80.0
)

# Check results
if results.get("success"):
    print(f"Generated {results['test_generation']['test_classes_generated']} test classes")
    print(f"Coverage: {results['coverage_results']['line_coverage']:.1f}%")
else:
    print(f"Failed: {results.get('error')}")
```

## Features

### 🔍 Intelligent Code Analysis
- **Package Structure Analysis**: Automatically identifies Spring Boot project structure
- **Annotation Detection**: Recognizes Spring annotations (@Service, @Controller, etc.)
- **Dependency Mapping**: Identifies dependencies for proper mocking
- **Method Signature Extraction**: Analyzes method parameters, return types, and exceptions

### 🧪 Comprehensive Test Generation
- **JUnit 5 Support**: Generates modern JUnit 5 test cases
- **Mockito Integration**: Automatically mocks dependencies using Mockito
- **Spring Boot Testing**: Uses appropriate Spring Boot test annotations
- **Edge Case Coverage**: Includes positive, negative, and edge case scenarios
- **Exception Testing**: Tests exception handling scenarios

### 🔄 Iterative Improvement
- **Test Execution**: Runs generated tests and captures results
- **Coverage Analysis**: Uses JaCoCo for detailed coverage reports
- **Failure Analysis**: Identifies and categorizes test failures
- **Automatic Refinement**: Regenerates tests based on feedback

### 📊 Quality Metrics
- **Coverage Tracking**: Line, branch, method, and class coverage
- **Success Rate Monitoring**: Tracks test pass/fail rates
- **Quality Scoring**: Overall quality score based on multiple factors
- **Detailed Reporting**: Comprehensive reports with actionable insights

## Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Repo Handler  │    │  Repo Analyzer  │    │ Test Generator  │
│                 │    │                 │    │                 │
│ • Clone repos   │────▶ • Parse Java    │────▶ • Generate     │
│ • Validate      │    │ • Extract meta  │    │   tests w/ AI   │
│ • Detect build  │    │ • Find Spring   │    │ • Use Mockito   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Test Suite Mgr  │    │  Test Runner    │    │ Feedback        │
│                 │    │                 │    │ Analyzer        │
│ • Organize      │◀───│ • Run JUnit     │◀───│ • Analyze       │
│ • Create suite  │    │ • Get coverage  │    │   failures      │
│ • Generate docs │    │ • Capture logs  │    │ • Suggest fixes │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow

1. **Input Processing**: Repository URL or local path
2. **Code Analysis**: Extract Spring Boot metadata
3. **Test Generation**: Use Gemini AI to create tests
4. **Organization**: Structure tests into proper suite
5. **Execution**: Run tests and collect metrics
6. **Analysis**: Analyze results and generate feedback
7. **Improvement**: Iterate based on feedback
8. **Reporting**: Generate final reports

## Troubleshooting

### Common Issues

#### 1. API Key Issues
```
Error: GEMINI_API_KEY environment variable is required
```
**Solution:** Set your Gemini AI API key:
```bash
# Windows
set GEMINI_API_KEY=your-api-key-here

# Linux/Mac
export GEMINI_API_KEY="your-api-key-here"
```

#### 2. Build Tool Not Found
```
Error: No Maven (pom.xml) or Gradle (build.gradle) build file found
```
**Solution:** Ensure your project has a proper build file:
- Maven: `pom.xml` in project root
- Gradle: `build.gradle` or `build.gradle.kts` in project root

#### 3. Java Parsing Errors
```
Error parsing Java file: Invalid syntax
```
**Solution:** Check that Java files are valid and use supported syntax. The parser supports Java 8+ syntax.

#### 4. Test Compilation Failures
```
Tests failed to compile
```
**Solution:** 
- Ensure all dependencies are in your build file
- Check that generated imports are correct
- Verify Spring Boot version compatibility

#### 5. Git Clone Issues
```
Git clone failed: Permission denied
```
**Solution:**
- For private repositories, use authentication
- Ensure Git is installed and in PATH
- Check repository URL is correct

### Debug Mode

Enable verbose logging by setting environment variable:
```bash
export DEBUG=1
python main.py --repo-url your-repo
```

### Log Files

The system creates logs in:
- Test execution output: Captured in test results
- Coverage reports: `target/site/jacoco/` (Maven) or `build/reports/jacoco/` (Gradle)
- Generated reports: `TEST_GENERATION_REPORT.md` in project root

## Advanced Usage

### Custom Prompts

You can customize the AI prompts by modifying `test_generator.py`:

```python
def _create_test_generation_prompt(self, class_info, metadata):
    # Customize the prompt here
    custom_prompt = f"""
    Generate comprehensive tests for {class_info['name']} with focus on:
    - Error handling
    - Performance edge cases
    - Security considerations
    """
    return custom_prompt
```

### Custom Coverage Thresholds

Set different coverage thresholds for different components:

```python
# In feedback_analyzer.py
def _analyze_coverage_issues(self, coverage_result, metadata):
    # Custom thresholds based on component type
    thresholds = {
        'Controller': 70.0,
        'Service': 85.0,
        'Repository': 60.0
    }
```

### Integration with CI/CD

Create a CI/CD pipeline script:

```yaml
# .github/workflows/test-generation.yml
name: Generate Tests
on: [push]
jobs:
  generate-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Generate tests
      env:
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
      run: python main.py --local-path . --coverage-threshold 75
```

### Custom Test Templates

Create custom test templates by modifying the Gemini prompts:

```python
# Custom template for repository tests
REPOSITORY_TEST_TEMPLATE = """
Generate comprehensive tests for Spring Data JPA repository:
- Test CRUD operations
- Test custom query methods
- Test transaction handling
- Use @DataJpaTest annotation
- Mock external dependencies
"""
```

### Batch Processing

Process multiple repositories:

```python
repositories = [
    "https://github.com/user/app1",
    "https://github.com/user/app2",
    "https://github.com/user/app3"
]

for repo_url in repositories:
    generator = UnitTestGenerator(repo_url=repo_url)
    results = generator.generate_tests()
    print(f"Processed {repo_url}: {results['success']}")
```

## Best Practices

### 1. Project Setup
- Ensure your Spring Boot project follows standard Maven/Gradle structure
- Include necessary testing dependencies (JUnit 5, Mockito, Spring Boot Test)
- Use clear, descriptive class and method names

### 2. Generated Test Review
- Always review generated tests before committing
- Customize tests for business-specific scenarios
- Add integration tests for complex workflows

### 3. Iterative Improvement
- Start with lower coverage thresholds and gradually increase
- Focus on critical business logic first
- Use feedback to improve your code structure

### 4. Maintenance
- Regenerate tests when significant code changes occur
- Keep test dependencies up to date
- Monitor test execution times and optimize as needed

## Support and Contributing

### Getting Help
- Check the troubleshooting section above
- Run `python test_installation.py` to verify setup
- Review log files for detailed error information

### Contributing
- Submit issues for bugs or feature requests
- Follow the existing code style and patterns
- Add tests for new functionality
- Update documentation for changes

## License

This project is licensed under the MIT License. See LICENSE file for details.
