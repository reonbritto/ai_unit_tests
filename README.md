# Spring Boot Unit Test Generator

A Python-based system that uses two agents to automatically generate JUnit test cases for Spring Boot applications using Google Gemini AI.

## Features

- **Repo Analyzer Agent**: Analyzes Spring Boot codebase and extracts metadata
- **Test Generator Agent**: Uses Gemini AI to generate comprehensive JUnit test cases
- **Iterative Improvement**: Runs tests, analyzes failures, and improves test coverage
- **Support for GitHub repositories and local projects**

## Prerequisites

- Python 3.8+
- Maven or Gradle
- Google Gemini AI API key
- Git (for repository cloning)

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your Google Gemini AI API key:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

## Usage

```python
from main import UnitTestGenerator

# For GitHub repository
generator = UnitTestGenerator(
    repo_url="https://github.com/user/spring-boot-app",
    gemini_api_key="your-api-key"
)

# For local project
generator = UnitTestGenerator(
    local_path="/path/to/spring-boot-app",
    gemini_api_key="your-api-key"
)

# Generate tests
generator.generate_tests(max_iterations=3, coverage_threshold=80)
```

## Project Structure

```
├── repo_analyzer.py      # Analyzes Spring Boot codebase
├── test_generator.py     # Generates JUnit tests using Gemini AI
├── repo_handler.py       # Handles repository cloning/access
├── test_runner.py        # Executes tests and captures results
├── feedback_analyzer.py  # Analyzes test results and coverage
├── test_suite_manager.py # Manages test suite organization
├── main.py              # Main orchestrator
└── config.py            # Configuration settings
```

## License

MIT License
