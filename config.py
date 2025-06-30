import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Configuration settings for the unit test generator."""
    
    # Gemini AI settings
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    GEMINI_API_KEY: Optional[str] = os.getenv('GEMINI_API_KEY')
    
    # Test generation settings
    MAX_ITERATIONS: int = 3
    COVERAGE_THRESHOLD: float = 80.0
    
    # File patterns
    JAVA_FILE_PATTERN: str = "**/*.java"
    TEST_FILE_SUFFIX: str = "Test.java"
    
    # Directories
    TEMP_DIR: str = "temp_repos"
    OUTPUT_DIR: str = "generated_tests"
    METADATA_FILE: str = "codebase_metadata.json"
    
    # Build tools
    MAVEN_TEST_CMD: str = "mvn test"
    GRADLE_TEST_CMD: str = "./gradlew test"
    
    # Coverage reports
    JACOCO_REPORT_PATH: str = "target/site/jacoco/jacoco.xml"
    GRADLE_JACOCO_PATH: str = "build/reports/jacoco/test/jacocoTestReport.xml"
    
    # Timeouts (in seconds)
    TEST_EXECUTION_TIMEOUT: int = 300
    REPO_CLONE_TIMEOUT: int = 120
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        return True
