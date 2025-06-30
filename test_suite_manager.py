import os
from pathlib import Path
from typing import List, Dict, Any
from config import Config
from test_generator import TestClass

class TestSuiteManager:
    """Manages the organization and structure of generated test suites."""
    
    def __init__(self):
        self.config = Config()
    
    def organize_test_suite(self, test_classes: List[TestClass], project_path: Path) -> Dict[str, Any]:
        """
        Organize generated test classes into a proper test suite structure.
        
        Args:
            test_classes: List of generated test classes
            project_path: Path to the Spring Boot project
            
        Returns:
            Dictionary with test suite organization information
        """
        
        print("Organizing test suite...")
        
        # Ensure test directory structure exists
        self._create_test_directory_structure(project_path)
        
        # Organize tests by package
        package_organization = self._organize_by_package(test_classes)
        
        # Create test suite class
        suite_class_path = self._create_test_suite_class(test_classes, project_path)
        
        # Create Maven/Gradle test configuration if needed
        self._configure_test_execution(project_path)
        
        organization_info = {
            "total_test_classes": len(test_classes),
            "packages": list(package_organization.keys()),
            "test_suite_class": str(suite_class_path) if suite_class_path else None,
            "test_directory": str(project_path / "src" / "test" / "java"),
            "package_organization": package_organization
        }
        
        print(f"Test suite organized: {len(test_classes)} test classes in {len(package_organization)} packages")
        
        return organization_info
    
    def _create_test_directory_structure(self, project_path: Path):
        """Create the standard test directory structure."""
        
        test_base = project_path / "src" / "test"
        
        # Create main test directories
        directories = [
            test_base / "java",
            test_base / "resources"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"Created test directory: {directory}")
    
    def _organize_by_package(self, test_classes: List[TestClass]) -> Dict[str, List[str]]:
        """Organize test classes by package."""
        
        package_organization = {}
        
        for test_class in test_classes:
            package = test_class.package or "default"
            
            if package not in package_organization:
                package_organization[package] = []
            
            package_organization[package].append(test_class.test_class_name)
        
        return package_organization
    
    def _create_test_suite_class(self, test_classes: List[TestClass], project_path: Path) -> Path:
        """Create a JUnit test suite class that includes all generated tests."""
        
        if not test_classes:
            return None
        
        # Determine the base package for the test suite
        base_package = self._determine_base_package(test_classes)
        
        # Generate test suite class content
        suite_content = self._generate_test_suite_content(test_classes, base_package)
        
        # Determine file path
        if base_package:
            package_path = project_path / "src" / "test" / "java" / base_package.replace('.', os.sep)
        else:
            package_path = project_path / "src" / "test" / "java"
        
        package_path.mkdir(parents=True, exist_ok=True)
        
        suite_file = package_path / "AllGeneratedTestsSuite.java"
        
        try:
            with open(suite_file, 'w', encoding='utf-8') as f:
                f.write(suite_content)
            
            print(f"Created test suite class: {suite_file}")
            return suite_file
            
        except Exception as e:
            print(f"Failed to create test suite class: {e}")
            return None
    
    def _determine_base_package(self, test_classes: List[TestClass]) -> str:
        """Determine the common base package for the test suite."""
        
        packages = [test_class.package for test_class in test_classes if test_class.package]
        
        if not packages:
            return ""
        
        # Find common package prefix
        if len(packages) == 1:
            return packages[0]
        
        # Find longest common prefix
        common_prefix = packages[0]
        for package in packages[1:]:
            while not package.startswith(common_prefix):
                if '.' in common_prefix:
                    common_prefix = common_prefix.rsplit('.', 1)[0]
                else:
                    common_prefix = ""
                    break
        
        return common_prefix
    
    def _generate_test_suite_content(self, test_classes: List[TestClass], base_package: str) -> str:
        """Generate the content for the test suite class."""
        
        # Prepare class names for the suite
        test_class_names = []
        imports = set()
        
        for test_class in test_classes:
            if test_class.package:
                full_class_name = f"{test_class.package}.{test_class.test_class_name}"
                imports.add(f"import {full_class_name};")
            
            test_class_names.append(f"{test_class.test_class_name}.class")
        
        # Sort imports
        sorted_imports = sorted(imports)
        
        # Generate suite content
        content_parts = []
        
        # Package declaration
        if base_package:
            content_parts.append(f"package {base_package};")
            content_parts.append("")
        
        # Imports
        content_parts.extend([
            "import org.junit.platform.suite.api.SelectClasses;",
            "import org.junit.platform.suite.api.Suite;",
            ""
        ])
        
        # Add test class imports
        content_parts.extend(sorted_imports)
        content_parts.append("")
        
        # Class declaration
        content_parts.extend([
            "/**",
            " * Test suite containing all generated unit tests.",
            " * This class was automatically generated.",
            " */",
            "@Suite",
            "@SelectClasses({"
        ])
        
        # Add test classes
        for i, class_name in enumerate(test_class_names):
            comma = "," if i < len(test_class_names) - 1 else ""
            content_parts.append(f"    {class_name}{comma}")
        
        content_parts.extend([
            "})",
            "public class AllGeneratedTestsSuite {",
            "    // This class serves as a test suite runner",
            "    // Individual test classes are listed in the @SelectClasses annotation",
            "}"
        ])
        
        return "\n".join(content_parts)
    
    def _configure_test_execution(self, project_path: Path):
        """Configure Maven or Gradle for optimal test execution."""
        
        # Configure Maven if present
        pom_file = project_path / "pom.xml"
        if pom_file.exists():
            self._configure_maven_testing(pom_file)
        
        # Configure Gradle if present
        gradle_file = project_path / "build.gradle"
        gradle_kts_file = project_path / "build.gradle.kts"
        
        if gradle_file.exists():
            self._configure_gradle_testing(gradle_file)
        elif gradle_kts_file.exists():
            self._configure_gradle_testing(gradle_kts_file)
    
    def _configure_maven_testing(self, pom_file: Path):
        """Ensure Maven has proper test configuration."""
        
        try:
            # Read current pom.xml
            content = pom_file.read_text(encoding='utf-8')
            
            # Check if JaCoCo plugin is present
            if 'jacoco-maven-plugin' not in content:
                print("Note: Consider adding JaCoCo plugin to pom.xml for coverage reports")
            
            # Check if JUnit 5 dependencies are present
            if 'junit-jupiter' not in content:
                print("Note: Consider adding JUnit 5 dependencies to pom.xml")
            
            # Check if Mockito is present
            if 'mockito' not in content:
                print("Note: Consider adding Mockito dependencies to pom.xml for mocking")
                
        except Exception as e:
            print(f"Could not read pom.xml: {e}")
    
    def _configure_gradle_testing(self, gradle_file: Path):
        """Ensure Gradle has proper test configuration."""
        
        try:
            # Read current build.gradle
            content = gradle_file.read_text(encoding='utf-8')
            
            # Check if JaCoCo plugin is present
            if 'jacoco' not in content:
                print("Note: Consider adding JaCoCo plugin to build.gradle for coverage reports")
            
            # Check if JUnit 5 is configured
            if 'useJUnitPlatform()' not in content:
                print("Note: Consider adding useJUnitPlatform() to test block in build.gradle")
                
        except Exception as e:
            print(f"Could not read build.gradle: {e}")
    
    def create_test_configuration_files(self, project_path: Path):
        """Create additional test configuration files."""
        
        # Create application-test.properties for Spring Boot tests
        self._create_test_properties(project_path)
        
        # Create logback-test.xml for test logging
        self._create_test_logging_config(project_path)
    
    def _create_test_properties(self, project_path: Path):
        """Create application-test.properties file."""
        
        test_resources = project_path / "src" / "test" / "resources"
        test_resources.mkdir(parents=True, exist_ok=True)
        
        properties_file = test_resources / "application-test.properties"
        
        if not properties_file.exists():
            properties_content = [
                "# Test configuration for Spring Boot",
                "# This file is used when running tests",
                "",
                "# Use in-memory database for tests",
                "spring.datasource.url=jdbc:h2:mem:testdb",
                "spring.datasource.driver-class-name=org.h2.Driver",
                "spring.jpa.hibernate.ddl-auto=create-drop",
                "",
                "# Disable unnecessary features in tests",
                "spring.jpa.show-sql=false",
                "logging.level.org.springframework.web=WARN",
                "logging.level.org.hibernate=WARN",
                "",
                "# Test-specific settings",
                "spring.test.database.replace=none"
            ]
            
            try:
                with open(properties_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(properties_content))
                
                print(f"Created test properties file: {properties_file}")
                
            except Exception as e:
                print(f"Failed to create test properties file: {e}")
    
    def _create_test_logging_config(self, project_path: Path):
        """Create logback-test.xml for test logging configuration."""
        
        test_resources = project_path / "src" / "test" / "resources"
        test_resources.mkdir(parents=True, exist_ok=True)
        
        logback_file = test_resources / "logback-test.xml"
        
        if not logback_file.exists():
            logback_content = '''<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <!-- Test logging configuration -->
    
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>
    
    <!-- Reduce logging for common Spring components during tests -->
    <logger name="org.springframework" level="WARN"/>
    <logger name="org.hibernate" level="WARN"/>
    <logger name="com.zaxxer.hikari" level="WARN"/>
    <logger name="org.apache.catalina" level="WARN"/>
    
    <!-- Application logging -->
    <logger name="com.unitgen" level="DEBUG"/>
    
    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
    </root>
</configuration>'''
            
            try:
                with open(logback_file, 'w', encoding='utf-8') as f:
                    f.write(logback_content)
                
                print(f"Created test logging config: {logback_file}")
                
            except Exception as e:
                print(f"Failed to create test logging config: {e}")
    
    def generate_test_report(self, test_classes: List[TestClass], 
                           organization_info: Dict[str, Any]) -> str:
        """Generate a summary report of the test suite."""
        
        report_parts = [
            "# Generated Test Suite Report",
            "",
            f"**Total Test Classes Generated:** {organization_info['total_test_classes']}",
            f"**Packages Covered:** {len(organization_info['packages'])}",
            "",
            "## Package Organization",
            ""
        ]
        
        for package, classes in organization_info['package_organization'].items():
            report_parts.append(f"### Package: {package}")
            for class_name in classes:
                report_parts.append(f"- {class_name}")
            report_parts.append("")
        
        report_parts.extend([
            "## Test Suite Structure",
            "",
            f"- Test Directory: `{organization_info['test_directory']}`"
        ])
        
        if organization_info['test_suite_class']:
            report_parts.append(f"- Test Suite Class: `{organization_info['test_suite_class']}`")
        
        report_parts.extend([
            "",
            "## Next Steps",
            "",
            "1. Run the test suite using your build tool:",
            "   - Maven: `mvn test`",
            "   - Gradle: `./gradlew test`",
            "",
            "2. Review test results and coverage reports",
            "",
            "3. Iterate on failed tests to improve coverage",
            "",
            "4. Customize tests as needed for your specific use cases"
        ])
        
        return "\n".join(report_parts)
