import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import traceback

from config import Config
from repo_handler import RepositoryHandler
from repo_analyzer import RepoAnalyzer
from test_generator import TestGenerator
from test_runner import TestRunner
from feedback_analyzer import FeedbackAnalyzer
from test_suite_manager import TestSuiteManager

class UnitTestGenerator:
    """Main orchestrator class for the Spring Boot unit test generation system."""
    
    def __init__(self, repo_url: Optional[str] = None, local_path: Optional[str] = None, 
                 gemini_api_key: Optional[str] = None):
        """
        Initialize the unit test generator.
        
        Args:
            repo_url: GitHub repository URL
            local_path: Local project path
            gemini_api_key: Google Gemini AI API key
        """
        
        # Validate configuration
        self.config = Config()
        if gemini_api_key:
            self.config.GEMINI_API_KEY = gemini_api_key
        
        try:
            self.config.validate()
        except ValueError as e:
            print(f"Configuration error: {e}")
            sys.exit(1)
        
        # Initialize components
        self.repo_handler = RepositoryHandler()
        self.repo_analyzer = RepoAnalyzer()
        self.test_generator = TestGenerator(self.config.GEMINI_API_KEY)
        self.test_runner = TestRunner()
        self.feedback_analyzer = FeedbackAnalyzer()
        self.test_suite_manager = TestSuiteManager()
        
        # Store input parameters
        self.repo_url = repo_url
        self.local_path = local_path
        
        # Runtime state
        self.project_path = None
        self.is_temp = False
        self.build_tool = None
        self.metadata = None
        self.generated_tests = []
        
        print("Unit Test Generator initialized successfully!")
    
    def generate_tests(self, max_iterations: int = 3, coverage_threshold: float = 80.0) -> Dict[str, Any]:
        """
        Generate comprehensive unit tests for the Spring Boot application.
        
        Args:
            max_iterations: Maximum number of improvement iterations
            coverage_threshold: Target code coverage percentage
            
        Returns:
            Dictionary containing generation results and statistics
        """
        
        print("=" * 60)
        print("Starting Spring Boot Unit Test Generation")
        print("=" * 60)
        
        try:
            # Phase 1: Repository Setup
            print("\n🔍 Phase 1: Repository Setup")
            self._setup_repository()
            
            # Phase 2: Code Analysis
            print("\n📊 Phase 2: Code Analysis")
            self._analyze_codebase()
            
            # Phase 3: Initial Test Generation
            print("\n🧪 Phase 3: Test Generation")
            self._generate_initial_tests()
            
            # Phase 4: Test Organization
            print("\n📁 Phase 4: Test Suite Organization")
            organization_info = self._organize_test_suite()
            
            # Phase 5: Iterative Improvement
            print("\n🔄 Phase 5: Iterative Improvement")
            improvement_results = self._iterative_improvement(max_iterations, coverage_threshold)
            
            # Phase 6: Final Report
            print("\n📋 Phase 6: Final Report")
            final_results = self._generate_final_report(organization_info, improvement_results)
            
            print("\n✅ Unit test generation completed successfully!")
            return final_results
            
        except Exception as e:
            print(f"\n❌ Error during test generation: {e}")
            traceback.print_exc()
            return {"success": False, "error": str(e)}
        
        finally:
            # Cleanup
            self._cleanup()
    
    def _setup_repository(self):
        """Set up the repository for analysis."""
        
        self.project_path, self.is_temp = self.repo_handler.handle_repository(
            self.repo_url, self.local_path
        )
        
        self.build_tool = self.repo_handler.get_build_tool(self.project_path)
        
        print(f"✅ Repository setup complete:")
        print(f"   - Project path: {self.project_path}")
        print(f"   - Build tool: {self.build_tool}")
        print(f"   - Temporary: {self.is_temp}")
    
    def _analyze_codebase(self):
        """Analyze the Spring Boot codebase."""
        
        self.metadata = self.repo_analyzer.analyze_repository(self.project_path)
        
        print(f"✅ Code analysis complete:")
        print(f"   - Classes found: {len(self.metadata['classes'])}")
        print(f"   - Spring components: {len(self.metadata['spring_components'])}")
        print(f"   - Test candidates: {len(self.metadata['test_candidates'])}")
        print(f"   - Packages: {len(self.metadata['packages'])}")
    
    def _generate_initial_tests(self):
        """Generate initial test cases."""
        
        self.generated_tests = self.test_generator.generate_tests(
            self.metadata, self.project_path
        )
        
        print(f"✅ Initial test generation complete:")
        print(f"   - Test classes generated: {len(self.generated_tests)}")
        
        if not self.generated_tests:
            raise RuntimeError("No tests were generated. Check if there are valid test candidates.")
    
    def _organize_test_suite(self):
        """Organize the generated tests into a proper test suite."""
        
        organization_info = self.test_suite_manager.organize_test_suite(
            self.generated_tests, self.project_path
        )
        
        # Create additional test configuration files
        self.test_suite_manager.create_test_configuration_files(self.project_path)
        
        print(f"✅ Test suite organization complete:")
        print(f"   - Test classes organized: {organization_info['total_test_classes']}")
        print(f"   - Packages: {len(organization_info['packages'])}")
        
        return organization_info
    
    def _iterative_improvement(self, max_iterations: int, coverage_threshold: float) -> Dict[str, Any]:
        """Perform iterative improvement of the test suite."""
        
        improvement_results = {
            "iterations": [],
            "final_coverage": 0.0,
            "final_success_rate": 0.0,
            "total_improvements": 0
        }
        
        for iteration in range(max_iterations):
            print(f"\n🔄 Iteration {iteration + 1}/{max_iterations}")
            
            # Run tests
            print("   Running tests...")
            test_result = self.test_runner.run_tests(self.project_path, self.build_tool)
            
            # Get coverage report
            print("   Analyzing coverage...")
            coverage_result = self.test_runner.get_coverage_report(self.project_path, self.build_tool)
            
            # Analyze feedback
            print("   Generating feedback...")
            feedback = self.feedback_analyzer.analyze_test_results(
                test_result, coverage_result, self.metadata
            )
            
            iteration_result = {
                "iteration": iteration + 1,
                "test_result": {
                    "total_tests": test_result.total_tests,
                    "passed_tests": test_result.passed_tests,
                    "failed_tests": test_result.failed_tests,
                    "success_rate": (test_result.passed_tests / max(test_result.total_tests, 1)) * 100
                },
                "coverage": {
                    "line_coverage": coverage_result.line_coverage if coverage_result else 0.0,
                    "branch_coverage": coverage_result.branch_coverage if coverage_result else 0.0
                },
                "feedback": {
                    "overall_score": feedback.overall_score,
                    "total_issues": feedback.total_issues
                },
                "improvements_made": 0
            }
            
            print(f"   Results: {test_result.passed_tests}/{test_result.total_tests} tests passed")
            if coverage_result:
                print(f"   Coverage: {coverage_result.line_coverage:.1f}% line coverage")
            print(f"   Quality Score: {feedback.overall_score:.1f}/100")
            
            # Check if we've met our goals
            current_coverage = coverage_result.line_coverage if coverage_result else 0.0
            current_success_rate = (test_result.passed_tests / max(test_result.total_tests, 1)) * 100
            
            if (current_coverage >= coverage_threshold and 
                current_success_rate >= 90 and 
                feedback.overall_score >= 80):
                print("   🎯 Quality goals achieved!")
                improvement_results["iterations"].append(iteration_result)
                break
            
            # Try to improve failing tests
            improvements_made = self._improve_failing_tests(feedback)
            iteration_result["improvements_made"] = improvements_made
            improvement_results["total_improvements"] += improvements_made
            
            improvement_results["iterations"].append(iteration_result)
            
            if improvements_made == 0:
                print("   ⚠️ No improvements could be made this iteration")
        
        # Record final results
        if improvement_results["iterations"]:
            last_iteration = improvement_results["iterations"][-1]
            improvement_results["final_coverage"] = last_iteration["coverage"]["line_coverage"]
            improvement_results["final_success_rate"] = last_iteration["test_result"]["success_rate"]
        
        return improvement_results
    
    def _improve_failing_tests(self, feedback) -> int:
        """Attempt to improve failing tests based on feedback."""
        
        improvements_made = 0
        
        # Group feedback by class
        class_feedback = {}
        for item in feedback.feedback_items:
            if item.severity in ['high', 'medium']:
                if item.class_name not in class_feedback:
                    class_feedback[item.class_name] = []
                class_feedback[item.class_name].append(item)
        
        # Try to regenerate tests for classes with issues
        for class_name, issues in class_feedback.items():
            if class_name in ['Overall', 'Build', 'Dependencies']:
                continue  # Skip non-specific issues
            
            # Find the corresponding class in metadata
            target_class = None
            for cls in self.metadata.get('test_candidates', []):
                if cls['name'] == class_name or cls['full_name'].endswith(class_name):
                    target_class = cls
                    break
            
            if target_class:
                try:
                    print(f"      Improving tests for {class_name}...")
                    
                    # Create improvement prompt
                    improvement_prompt = self.feedback_analyzer.create_improvement_prompt(
                        feedback, class_name
                    )
                    
                    # Regenerate test
                    improved_test = self.test_generator.regenerate_test(
                        target_class, self.metadata, self.project_path, improvement_prompt
                    )
                    
                    if improved_test:
                        improvements_made += 1
                        print(f"      ✅ Improved test for {class_name}")
                    
                except Exception as e:
                    print(f"      ❌ Failed to improve test for {class_name}: {e}")
        
        return improvements_made
    
    def _generate_final_report(self, organization_info: Dict[str, Any], 
                              improvement_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive final report."""
        
        # Run final test to get latest results
        final_test_result = self.test_runner.run_tests(self.project_path, self.build_tool)
        final_coverage = self.test_runner.get_coverage_report(self.project_path, self.build_tool)
        
        final_results = {
            "success": True,
            "project_info": {
                "path": str(self.project_path),
                "build_tool": self.build_tool,
                "is_temporary": self.is_temp
            },
            "analysis_results": {
                "total_classes": len(self.metadata['classes']),
                "spring_components": len(self.metadata['spring_components']),
                "test_candidates": len(self.metadata['test_candidates']),
                "packages": len(self.metadata['packages'])
            },
            "test_generation": {
                "test_classes_generated": len(self.generated_tests),
                "organization": organization_info
            },
            "final_test_results": {
                "total_tests": final_test_result.total_tests,
                "passed_tests": final_test_result.passed_tests,
                "failed_tests": final_test_result.failed_tests,
                "success_rate": (final_test_result.passed_tests / max(final_test_result.total_tests, 1)) * 100,
                "execution_time": final_test_result.execution_time
            },
            "coverage_results": {
                "line_coverage": final_coverage.line_coverage if final_coverage else 0.0,
                "branch_coverage": final_coverage.branch_coverage if final_coverage else 0.0,
                "method_coverage": final_coverage.method_coverage if final_coverage else 0.0,
                "class_coverage": final_coverage.class_coverage if final_coverage else 0.0
            },
            "improvement_process": improvement_results
        }
        
        # Print summary
        self._print_final_summary(final_results)
        
        # Generate and save report
        report_content = self.test_suite_manager.generate_test_report(
            self.generated_tests, organization_info
        )
        
        report_file = self.project_path / "TEST_GENERATION_REPORT.md"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"\n📄 Detailed report saved to: {report_file}")
        except Exception as e:
            print(f"Warning: Could not save report file: {e}")
        
        return final_results
    
    def _print_final_summary(self, results: Dict[str, Any]):
        """Print a final summary of results."""
        
        print("\n" + "=" * 60)
        print("FINAL RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"📊 Project Analysis:")
        print(f"   - Total classes analyzed: {results['analysis_results']['total_classes']}")
        print(f"   - Spring components found: {results['analysis_results']['spring_components']}")
        print(f"   - Test candidates identified: {results['analysis_results']['test_candidates']}")
        
        print(f"\n🧪 Test Generation:")
        print(f"   - Test classes generated: {results['test_generation']['test_classes_generated']}")
        print(f"   - Packages covered: {len(results['test_generation']['organization']['packages'])}")
        
        print(f"\n🎯 Test Execution:")
        print(f"   - Total tests: {results['final_test_results']['total_tests']}")
        print(f"   - Passed: {results['final_test_results']['passed_tests']}")
        print(f"   - Failed: {results['final_test_results']['failed_tests']}")
        print(f"   - Success rate: {results['final_test_results']['success_rate']:.1f}%")
        
        print(f"\n📈 Coverage:")
        print(f"   - Line coverage: {results['coverage_results']['line_coverage']:.1f}%")
        print(f"   - Branch coverage: {results['coverage_results']['branch_coverage']:.1f}%")
        print(f"   - Method coverage: {results['coverage_results']['method_coverage']:.1f}%")
        
        improvement_stats = results['improvement_process']
        print(f"\n🔄 Improvement Process:")
        print(f"   - Iterations performed: {len(improvement_stats['iterations'])}")
        print(f"   - Total improvements made: {improvement_stats['total_improvements']}")
        print(f"   - Final coverage: {improvement_stats['final_coverage']:.1f}%")
        print(f"   - Final success rate: {improvement_stats['final_success_rate']:.1f}%")
    
    def _cleanup(self):
        """Clean up temporary resources."""
        
        if self.is_temp and self.project_path:
            self.repo_handler.cleanup(self.project_path, self.is_temp)

def main():
    """Main entry point for command-line usage."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate unit tests for Spring Boot applications")
    parser.add_argument("--repo-url", help="GitHub repository URL")
    parser.add_argument("--local-path", help="Local project path")
    parser.add_argument("--api-key", help="Google Gemini AI API key")
    parser.add_argument("--max-iterations", type=int, default=3, help="Maximum improvement iterations")
    parser.add_argument("--coverage-threshold", type=float, default=80.0, help="Target coverage percentage")
    
    args = parser.parse_args()
    
    if not args.repo_url and not args.local_path:
        print("Error: Either --repo-url or --local-path must be provided")
        sys.exit(1)
    
    try:
        generator = UnitTestGenerator(
            repo_url=args.repo_url,
            local_path=args.local_path,
            gemini_api_key=args.api_key
        )
        
        results = generator.generate_tests(
            max_iterations=args.max_iterations,
            coverage_threshold=args.coverage_threshold
        )
        
        if results.get("success"):
            print("\n🎉 Test generation completed successfully!")
        else:
            print(f"\n❌ Test generation failed: {results.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
