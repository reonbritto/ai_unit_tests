from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from test_runner import TestResult, CoverageResult

@dataclass
class FeedbackItem:
    """Represents a specific feedback item for test improvement."""
    issue_type: str  # 'compilation_error', 'test_failure', 'low_coverage', 'missing_test'
    class_name: str
    method_name: Optional[str]
    description: str
    suggestion: str
    severity: str  # 'high', 'medium', 'low'

@dataclass
class AnalysisFeedback:
    """Comprehensive feedback analysis for test improvement."""
    overall_score: float  # 0-100
    total_issues: int
    feedback_items: List[FeedbackItem]
    summary: str
    recommendations: List[str]

class FeedbackAnalyzer:
    """Analyzes test results and coverage to provide improvement feedback."""
    
    def __init__(self):
        self.coverage_threshold = 80.0
        self.acceptable_failure_rate = 0.1  # 10%
    
    def analyze_test_results(self, test_result: TestResult, 
                           coverage_result: Optional[CoverageResult],
                           metadata: Dict[str, Any]) -> AnalysisFeedback:
        """
        Analyze test execution results and provide comprehensive feedback.
        
        Args:
            test_result: Results from test execution
            coverage_result: Coverage analysis results
            metadata: Project metadata from repo analyzer
            
        Returns:
            AnalysisFeedback with detailed improvement suggestions
        """
        
        print("Analyzing test results and generating feedback...")
        
        feedback_items = []
        
        # Analyze test failures
        failure_feedback = self._analyze_test_failures(test_result)
        feedback_items.extend(failure_feedback)
        
        # Analyze coverage issues
        if coverage_result:
            coverage_feedback = self._analyze_coverage_issues(coverage_result, metadata)
            feedback_items.extend(coverage_feedback)
        
        # Analyze missing tests
        missing_test_feedback = self._analyze_missing_tests(test_result, metadata)
        feedback_items.extend(missing_test_feedback)
        
        # Analyze compilation issues
        compilation_feedback = self._analyze_compilation_issues(test_result)
        feedback_items.extend(compilation_feedback)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(test_result, coverage_result, feedback_items)
        
        # Generate summary and recommendations
        summary = self._generate_summary(test_result, coverage_result, feedback_items)
        recommendations = self._generate_recommendations(feedback_items)
        
        feedback = AnalysisFeedback(
            overall_score=overall_score,
            total_issues=len(feedback_items),
            feedback_items=feedback_items,
            summary=summary,
            recommendations=recommendations
        )
        
        print(f"Analysis complete. Overall score: {overall_score:.1f}/100, Issues found: {len(feedback_items)}")
        
        return feedback
    
    def _analyze_test_failures(self, test_result: TestResult) -> List[FeedbackItem]:
        """Analyze test failures and create feedback items."""
        
        feedback_items = []
        
        for failed_test in test_result.failed_test_details:
            test_class = failed_test.get('test_class', 'Unknown')
            test_method = failed_test.get('test_method', 'Unknown')
            failure_type = failed_test.get('failure_type', 'FAILURE')
            message = failed_test.get('message', 'No message')
            
            # Categorize the failure
            issue_type, suggestion = self._categorize_test_failure(failure_type, message)
            
            feedback_item = FeedbackItem(
                issue_type=issue_type,
                class_name=test_class,
                method_name=test_method,
                description=f"Test {test_method} in {test_class} failed: {message}",
                suggestion=suggestion,
                severity='high'
            )
            
            feedback_items.append(feedback_item)
        
        return feedback_items
    
    def _categorize_test_failure(self, failure_type: str, message: str) -> tuple:
        """Categorize test failure and provide specific suggestions."""
        
        message_lower = message.lower()
        
        # Check for common failure patterns
        if 'nullpointerexception' in message_lower:
            return 'test_failure', "Add null checks or mock missing dependencies properly"
        
        elif 'assertionerror' in message_lower or 'assertion' in message_lower:
            return 'test_failure', "Review test assertions and expected vs actual values"
        
        elif 'classnotfound' in message_lower or 'noclassdeffounderror' in message_lower:
            return 'compilation_error', "Add missing dependencies or imports to test class"
        
        elif 'autowired' in message_lower or 'dependency' in message_lower:
            return 'test_failure', "Properly mock or configure Spring dependencies in test"
        
        elif 'mockito' in message_lower:
            return 'test_failure', "Check Mockito mock setup and stubbing"
        
        elif 'timeout' in message_lower:
            return 'test_failure', "Increase test timeout or optimize test performance"
        
        elif 'security' in message_lower:
            return 'test_failure', "Configure test security context or disable security for test"
        
        elif 'database' in message_lower or 'sql' in message_lower:
            return 'test_failure', "Use @DataJpaTest or configure test database properly"
        
        elif 'web' in message_lower or 'http' in message_lower:
            return 'test_failure', "Use @WebMvcTest and configure MockMvc properly"
        
        else:
            return 'test_failure', "Review test logic and mock setup"
    
    def _analyze_coverage_issues(self, coverage_result: CoverageResult, 
                               metadata: Dict[str, Any]) -> List[FeedbackItem]:
        """Analyze code coverage and identify areas needing more tests."""
        
        feedback_items = []
        
        # Overall coverage feedback
        if coverage_result.line_coverage < self.coverage_threshold:
            feedback_item = FeedbackItem(
                issue_type='low_coverage',
                class_name='Overall',
                method_name=None,
                description=f"Line coverage is {coverage_result.line_coverage:.1f}%, below threshold of {self.coverage_threshold}%",
                suggestion=f"Add tests to increase coverage to at least {self.coverage_threshold}%",
                severity='medium'
            )
            feedback_items.append(feedback_item)
        
        # Uncovered classes
        for uncovered_class in coverage_result.uncovered_classes[:5]:  # Limit to first 5
            feedback_item = FeedbackItem(
                issue_type='low_coverage',
                class_name=uncovered_class,
                method_name=None,
                description=f"Class {uncovered_class} has no test coverage",
                suggestion=f"Create comprehensive unit tests for {uncovered_class}",
                severity='high'
            )
            feedback_items.append(feedback_item)
        
        # Uncovered methods
        for uncovered_method in coverage_result.uncovered_methods[:10]:  # Limit to first 10
            if '.' in uncovered_method:
                class_name, method_name = uncovered_method.rsplit('.', 1)
            else:
                class_name, method_name = uncovered_method, 'unknown'
            
            feedback_item = FeedbackItem(
                issue_type='low_coverage',
                class_name=class_name,
                method_name=method_name,
                description=f"Method {method_name} in {class_name} is not covered by tests",
                suggestion=f"Add test cases for method {method_name}",
                severity='medium'
            )
            feedback_items.append(feedback_item)
        
        return feedback_items
    
    def _analyze_missing_tests(self, test_result: TestResult, 
                             metadata: Dict[str, Any]) -> List[FeedbackItem]:
        """Identify classes that should have tests but don't."""
        
        feedback_items = []
        
        # Get test candidates from metadata
        test_candidates = metadata.get('test_candidates', [])
        
        # Check if we have very few tests compared to candidates
        if test_result.total_tests < len(test_candidates) * 0.5:  # Less than 50% of candidates have tests
            feedback_item = FeedbackItem(
                issue_type='missing_test',
                class_name='Overall',
                method_name=None,
                description=f"Only {test_result.total_tests} tests found for {len(test_candidates)} test candidates",
                suggestion="Generate tests for more classes, especially Spring components",
                severity='medium'
            )
            feedback_items.append(feedback_item)
        
        return feedback_items
    
    def _analyze_compilation_issues(self, test_result: TestResult) -> List[FeedbackItem]:
        """Analyze compilation and build issues."""
        
        feedback_items = []
        
        if not test_result.success and test_result.total_tests == 0:
            # Likely a compilation issue
            error_output = test_result.error_output.lower()
            
            if 'compilation' in error_output or 'compile' in error_output:
                feedback_item = FeedbackItem(
                    issue_type='compilation_error',
                    class_name='Build',
                    method_name=None,
                    description="Tests failed to compile",
                    suggestion="Fix compilation errors in test classes - check imports, syntax, and dependencies",
                    severity='high'
                )
                feedback_items.append(feedback_item)
            
            elif 'dependency' in error_output or 'resolution' in error_output:
                feedback_item = FeedbackItem(
                    issue_type='compilation_error',
                    class_name='Dependencies',
                    method_name=None,
                    description="Dependency resolution failed",
                    suggestion="Add missing test dependencies to pom.xml or build.gradle",
                    severity='high'
                )
                feedback_items.append(feedback_item)
        
        return feedback_items
    
    def _calculate_overall_score(self, test_result: TestResult, 
                               coverage_result: Optional[CoverageResult],
                               feedback_items: List[FeedbackItem]) -> float:
        """Calculate an overall quality score for the test suite."""
        
        score = 100.0
        
        # Deduct for test failures
        if test_result.total_tests > 0:
            failure_rate = test_result.failed_tests / test_result.total_tests
            if failure_rate > self.acceptable_failure_rate:
                score -= (failure_rate - self.acceptable_failure_rate) * 200  # Heavy penalty for failures
        
        # Deduct for low coverage
        if coverage_result:
            if coverage_result.line_coverage < self.coverage_threshold:
                coverage_deficit = self.coverage_threshold - coverage_result.line_coverage
                score -= coverage_deficit * 0.5  # 0.5 points per percentage point below threshold
        
        # Deduct for high severity issues
        high_severity_count = sum(1 for item in feedback_items if item.severity == 'high')
        medium_severity_count = sum(1 for item in feedback_items if item.severity == 'medium')
        
        score -= high_severity_count * 10  # 10 points per high severity issue
        score -= medium_severity_count * 5   # 5 points per medium severity issue
        
        # Ensure score is not negative
        return max(0.0, min(100.0, score))
    
    def _generate_summary(self, test_result: TestResult, 
                         coverage_result: Optional[CoverageResult],
                         feedback_items: List[FeedbackItem]) -> str:
        """Generate a summary of the test analysis."""
        
        summary_parts = []
        
        # Test execution summary
        if test_result.total_tests > 0:
            success_rate = (test_result.passed_tests / test_result.total_tests) * 100
            summary_parts.append(f"Test execution: {test_result.passed_tests}/{test_result.total_tests} passed ({success_rate:.1f}% success rate)")
        else:
            summary_parts.append("No tests were executed successfully")
        
        # Coverage summary
        if coverage_result:
            summary_parts.append(f"Line coverage: {coverage_result.line_coverage:.1f}%")
            if coverage_result.line_coverage < self.coverage_threshold:
                summary_parts.append("Coverage is below the recommended threshold")
        else:
            summary_parts.append("No coverage data available")
        
        # Issues summary
        high_issues = sum(1 for item in feedback_items if item.severity == 'high')
        medium_issues = sum(1 for item in feedback_items if item.severity == 'medium')
        
        if high_issues > 0 or medium_issues > 0:
            summary_parts.append(f"Found {high_issues} high priority and {medium_issues} medium priority issues")
        else:
            summary_parts.append("No significant issues found")
        
        return ". ".join(summary_parts) + "."
    
    def _generate_recommendations(self, feedback_items: List[FeedbackItem]) -> List[str]:
        """Generate prioritized recommendations for improvement."""
        
        recommendations = []
        
        # Group feedback by issue type
        issue_types = {}
        for item in feedback_items:
            if item.issue_type not in issue_types:
                issue_types[item.issue_type] = []
            issue_types[item.issue_type].append(item)
        
        # Generate recommendations based on issue types
        if 'compilation_error' in issue_types:
            recommendations.append("Fix compilation errors first - tests cannot run without compiling successfully")
        
        if 'test_failure' in issue_types:
            failure_count = len(issue_types['test_failure'])
            recommendations.append(f"Address {failure_count} test failures by reviewing mock setup and assertions")
        
        if 'low_coverage' in issue_types:
            coverage_issues = len(issue_types['low_coverage'])
            recommendations.append(f"Improve test coverage by adding tests for {coverage_issues} uncovered areas")
        
        if 'missing_test' in issue_types:
            recommendations.append("Generate tests for classes that don't have any test coverage")
        
        # General recommendations
        if len(feedback_items) > 10:
            recommendations.append("Consider focusing on high-severity issues first for maximum impact")
        
        if not recommendations:
            recommendations.append("Test suite is in good shape - consider adding edge case tests")
        
        return recommendations
    
    def create_improvement_prompt(self, feedback: AnalysisFeedback, 
                                class_name: str) -> str:
        """Create a focused improvement prompt for a specific class."""
        
        # Find feedback items for this class
        class_feedback = [
            item for item in feedback.feedback_items 
            if item.class_name == class_name or class_name in item.class_name
        ]
        
        if not class_feedback:
            return "No specific issues found for this class. Consider adding more comprehensive test cases."
        
        prompt_parts = [
            f"The following issues were found with tests for class {class_name}:",
            ""
        ]
        
        for item in class_feedback:
            prompt_parts.append(f"- {item.description}")
            prompt_parts.append(f"  Suggestion: {item.suggestion}")
            prompt_parts.append("")
        
        prompt_parts.extend([
            "Please regenerate the test class addressing these specific issues.",
            "Focus on the suggestions provided and ensure the tests are robust and comprehensive."
        ])
        
        return "\n".join(prompt_parts)
