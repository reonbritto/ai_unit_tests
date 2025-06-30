import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from config import Config

@dataclass
class TestResult:
    """Represents the result of running tests."""
    success: bool
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    execution_time: float
    output: str
    error_output: str
    failed_test_details: List[Dict[str, str]]

@dataclass
class CoverageResult:
    """Represents code coverage results."""
    line_coverage: float
    branch_coverage: float
    method_coverage: float
    class_coverage: float
    covered_lines: int
    total_lines: int
    uncovered_classes: List[str]
    uncovered_methods: List[str]

class TestRunner:
    """Executes JUnit tests and captures results and coverage."""
    
    def __init__(self):
        self.config = Config()
    
    def run_tests(self, project_path: Path, build_tool: str) -> TestResult:
        """
        Run all tests in the project and capture results.
        
        Args:
            project_path: Path to the Spring Boot project
            build_tool: Build tool to use ('maven' or 'gradle')
            
        Returns:
            TestResult object with execution details
        """
        print(f"Running tests using {build_tool}...")
        
        start_time = time.time()
        
        try:
            if build_tool.lower() == 'maven':
                result = self._run_maven_tests(project_path)
            elif build_tool.lower() == 'gradle':
                result = self._run_gradle_tests(project_path)
            else:
                raise ValueError(f"Unsupported build tool: {build_tool}")
            
            execution_time = time.time() - start_time
            
            # Parse test results
            test_result = self._parse_test_results(result, execution_time, build_tool, project_path)
            
            print(f"Test execution completed in {execution_time:.2f} seconds")
            print(f"Results: {test_result.passed_tests} passed, {test_result.failed_tests} failed, {test_result.skipped_tests} skipped")
            
            return test_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"Test execution failed: {e}")
            
            return TestResult(
                success=False,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                execution_time=execution_time,
                output="",
                error_output=str(e),
                failed_test_details=[]
            )
    
    def _run_maven_tests(self, project_path: Path) -> subprocess.CompletedProcess:
        """Run tests using Maven."""
        
        # Ensure we have clean test and jacoco reports
        clean_cmd = ["mvn", "clean"]
        subprocess.run(clean_cmd, cwd=project_path, capture_output=True, text=True)
        
        # Run tests with JaCoCo coverage
        cmd = ["mvn", "test", "jacoco:report"]
        
        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=self.config.TEST_EXECUTION_TIMEOUT
        )
        
        return result
    
    def _run_gradle_tests(self, project_path: Path) -> subprocess.CompletedProcess:
        """Run tests using Gradle."""
        
        # Determine gradle wrapper or gradle command
        gradle_wrapper = project_path / "gradlew"
        if gradle_wrapper.exists():
            if gradle_wrapper.suffix == ".bat":
                cmd = ["gradlew.bat"]
            else:
                cmd = ["./gradlew"]
        else:
            cmd = ["gradle"]
        
        # Clean and run tests with coverage
        cmd.extend(["clean", "test", "jacocoTestReport"])
        
        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=self.config.TEST_EXECUTION_TIMEOUT,
            shell=True  # Needed for Windows
        )
        
        return result
    
    def _parse_test_results(self, result: subprocess.CompletedProcess, 
                          execution_time: float, build_tool: str, 
                          project_path: Path) -> TestResult:
        """Parse test execution results."""
        
        success = result.returncode == 0
        output = result.stdout
        error_output = result.stderr
        
        # Parse test counts from output
        total_tests, passed_tests, failed_tests, skipped_tests = self._extract_test_counts(output, build_tool)
        
        # Extract failed test details
        failed_test_details = self._extract_failed_test_details(output, error_output, build_tool)
        
        return TestResult(
            success=success,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            execution_time=execution_time,
            output=output,
            error_output=error_output,
            failed_test_details=failed_test_details
        )
    
    def _extract_test_counts(self, output: str, build_tool: str) -> Tuple[int, int, int, int]:
        """Extract test counts from build output."""
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        
        try:
            if build_tool.lower() == 'maven':
                # Maven output pattern: "Tests run: 10, Failures: 1, Errors: 0, Skipped: 2"
                import re
                pattern = r'Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)'
                matches = re.findall(pattern, output)
                
                if matches:
                    # Use the last match (final summary)
                    last_match = matches[-1]
                    total_tests = int(last_match[0])
                    failures = int(last_match[1])
                    errors = int(last_match[2])
                    skipped_tests = int(last_match[3])
                    failed_tests = failures + errors
                    passed_tests = total_tests - failed_tests - skipped_tests
                
            elif build_tool.lower() == 'gradle':
                # Gradle output varies, try to find test results
                import re
                
                # Look for patterns like "10 tests completed, 1 failed"
                completed_pattern = r'(\d+) tests? completed'
                failed_pattern = r'(\d+) failed'
                skipped_pattern = r'(\d+) skipped'
                
                completed_match = re.search(completed_pattern, output)
                failed_match = re.search(failed_pattern, output)
                skipped_match = re.search(skipped_pattern, output)
                
                if completed_match:
                    total_tests = int(completed_match.group(1))
                
                if failed_match:
                    failed_tests = int(failed_match.group(1))
                
                if skipped_match:
                    skipped_tests = int(skipped_match.group(1))
                
                passed_tests = total_tests - failed_tests - skipped_tests
                
        except Exception as e:
            print(f"Warning: Could not parse test counts: {e}")
        
        return total_tests, passed_tests, failed_tests, skipped_tests
    
    def _extract_failed_test_details(self, output: str, error_output: str, 
                                   build_tool: str) -> List[Dict[str, str]]:
        """Extract details about failed tests."""
        
        failed_tests = []
        
        try:
            import re
            
            if build_tool.lower() == 'maven':
                # Look for failed test patterns in Maven output
                # Pattern: "testMethodName(com.example.TestClass)  Time elapsed: 0.001 s  <<< FAILURE!"
                failure_pattern = r'(\w+)\(([^)]+)\).*?<<< (FAILURE|ERROR)!'
                
                matches = re.findall(failure_pattern, output + error_output)
                
                for match in matches:
                    test_method = match[0]
                    test_class = match[1]
                    failure_type = match[2]
                    
                    failed_tests.append({
                        'test_class': test_class,
                        'test_method': test_method,
                        'failure_type': failure_type,
                        'message': self._extract_failure_message(output, test_class, test_method)
                    })
            
            elif build_tool.lower() == 'gradle':
                # Gradle failure patterns
                failure_pattern = r'(\w+(?:\.\w+)*) > (\w+) FAILED'
                
                matches = re.findall(failure_pattern, output + error_output)
                
                for match in matches:
                    test_class = match[0]
                    test_method = match[1]
                    
                    failed_tests.append({
                        'test_class': test_class,
                        'test_method': test_method,
                        'failure_type': 'FAILED',
                        'message': self._extract_failure_message(output, test_class, test_method)
                    })
                    
        except Exception as e:
            print(f"Warning: Could not parse failed test details: {e}")
        
        return failed_tests
    
    def _extract_failure_message(self, output: str, test_class: str, test_method: str) -> str:
        """Extract failure message for a specific test."""
        try:
            # Look for error messages near the test failure
            lines = output.split('\n')
            for i, line in enumerate(lines):
                if test_class in line and test_method in line:
                    # Look for error message in next few lines
                    for j in range(i + 1, min(i + 10, len(lines))):
                        if 'Exception' in lines[j] or 'Error' in lines[j] or 'Assert' in lines[j]:
                            return lines[j].strip()
            return "No specific error message found"
        except:
            return "Could not extract error message"
    
    def get_coverage_report(self, project_path: Path, build_tool: str) -> Optional[CoverageResult]:
        """
        Extract code coverage information from JaCoCo reports.
        
        Args:
            project_path: Path to the Spring Boot project
            build_tool: Build tool used ('maven' or 'gradle')
            
        Returns:
            CoverageResult object or None if no coverage data found
        """
        
        try:
            if build_tool.lower() == 'maven':
                jacoco_file = project_path / self.config.JACOCO_REPORT_PATH
            else:  # gradle
                jacoco_file = project_path / self.config.GRADLE_JACOCO_PATH
            
            if not jacoco_file.exists():
                print(f"No JaCoCo report found at: {jacoco_file}")
                return None
            
            return self._parse_jacoco_report(jacoco_file)
            
        except Exception as e:
            print(f"Error reading coverage report: {e}")
            return None
    
    def _parse_jacoco_report(self, jacoco_file: Path) -> CoverageResult:
        """Parse JaCoCo XML report."""
        
        try:
            import xml.etree.ElementTree as ET
            
            tree = ET.parse(jacoco_file)
            root = tree.getroot()
            
            # Extract overall coverage metrics
            line_coverage = 0.0
            branch_coverage = 0.0
            method_coverage = 0.0
            class_coverage = 0.0
            
            covered_lines = 0
            total_lines = 0
            
            uncovered_classes = []
            uncovered_methods = []
            
            # Find the report counter elements
            for counter in root.findall('.//counter'):
                counter_type = counter.get('type')
                covered = int(counter.get('covered', 0))
                missed = int(counter.get('missed', 0))
                total = covered + missed
                
                if total > 0:
                    coverage_percent = (covered / total) * 100
                    
                    if counter_type == 'LINE':
                        line_coverage = coverage_percent
                        covered_lines = covered
                        total_lines = total
                    elif counter_type == 'BRANCH':
                        branch_coverage = coverage_percent
                    elif counter_type == 'METHOD':
                        method_coverage = coverage_percent
                    elif counter_type == 'CLASS':
                        class_coverage = coverage_percent
            
            # Find uncovered classes and methods
            for package in root.findall('.//package'):
                for class_elem in package.findall('class'):
                    class_name = class_elem.get('name', '').replace('/', '.')
                    
                    # Check class coverage
                    class_counters = class_elem.findall('counter[@type="LINE"]')
                    if class_counters:
                        counter = class_counters[0]
                        covered = int(counter.get('covered', 0))
                        if covered == 0:
                            uncovered_classes.append(class_name)
                    
                    # Check method coverage
                    for method in class_elem.findall('method'):
                        method_name = method.get('name', '')
                        method_counters = method.findall('counter[@type="LINE"]')
                        if method_counters:
                            counter = method_counters[0]
                            covered = int(counter.get('covered', 0))
                            if covered == 0:
                                uncovered_methods.append(f"{class_name}.{method_name}")
            
            return CoverageResult(
                line_coverage=line_coverage,
                branch_coverage=branch_coverage,
                method_coverage=method_coverage,
                class_coverage=class_coverage,
                covered_lines=covered_lines,
                total_lines=total_lines,
                uncovered_classes=uncovered_classes,
                uncovered_methods=uncovered_methods
            )
            
        except Exception as e:
            print(f"Error parsing JaCoCo report: {e}")
            return CoverageResult(0, 0, 0, 0, 0, 0, [], [])
    
    def run_single_test(self, project_path: Path, build_tool: str, 
                       test_class: str) -> TestResult:
        """
        Run a single test class.
        
        Args:
            project_path: Path to the Spring Boot project
            build_tool: Build tool to use
            test_class: Fully qualified test class name
            
        Returns:
            TestResult for the single test class
        """
        
        print(f"Running single test: {test_class}")
        
        start_time = time.time()
        
        try:
            if build_tool.lower() == 'maven':
                cmd = ["mvn", "test", f"-Dtest={test_class}"]
            else:  # gradle
                gradle_wrapper = project_path / "gradlew"
                if gradle_wrapper.exists():
                    cmd = ["./gradlew"] if not gradle_wrapper.suffix == ".bat" else ["gradlew.bat"]
                else:
                    cmd = ["gradle"]
                cmd.extend(["test", f"--tests", test_class])
            
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=self.config.TEST_EXECUTION_TIMEOUT,
                shell=(build_tool.lower() == 'gradle')
            )
            
            execution_time = time.time() - start_time
            
            return self._parse_test_results(result, execution_time, build_tool, project_path)
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                success=False,
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                skipped_tests=0,
                execution_time=execution_time,
                output="",
                error_output=str(e),
                failed_test_details=[]
            )
