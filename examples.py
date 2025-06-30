"""
Example usage of the Spring Boot Unit Test Generator.

This script demonstrates how to use the UnitTestGenerator class
to generate comprehensive test suites for Spring Boot applications.
"""

import os
from main import UnitTestGenerator

def example_github_repo():
    """Example: Generate tests for a GitHub repository."""
    
    print("Example 1: Generating tests from GitHub repository")
    print("-" * 50)
    
    # Set your Gemini API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Please set GEMINI_API_KEY environment variable")
        return
    
    # Example Spring Boot repository
    repo_url = "https://github.com/spring-projects/spring-petclinic.git"
    
    try:
        generator = UnitTestGenerator(
            repo_url=repo_url,
            gemini_api_key=api_key
        )
        
        results = generator.generate_tests(
            max_iterations=3,
            coverage_threshold=75.0
        )
        
        if results.get("success"):
            print("✅ Test generation successful!")
            print(f"Generated {results['test_generation']['test_classes_generated']} test classes")
            print(f"Final coverage: {results['coverage_results']['line_coverage']:.1f}%")
        else:
            print(f"❌ Test generation failed: {results.get('error')}")
            
    except Exception as e:
        print(f"Error: {e}")

def example_local_project():
    """Example: Generate tests for a local project."""
    
    print("Example 2: Generating tests from local project")
    print("-" * 50)
    
    # Set your Gemini API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Please set GEMINI_API_KEY environment variable")
        return
    
    # Path to your local Spring Boot project
    local_path = r"C:\path\to\your\springboot\project"
    
    if not os.path.exists(local_path):
        print(f"Local path does not exist: {local_path}")
        print("Please update the path to point to your Spring Boot project")
        return
    
    try:
        generator = UnitTestGenerator(
            local_path=local_path,
            gemini_api_key=api_key
        )
        
        results = generator.generate_tests(
            max_iterations=2,
            coverage_threshold=80.0
        )
        
        if results.get("success"):
            print("✅ Test generation successful!")
            print_results_summary(results)
        else:
            print(f"❌ Test generation failed: {results.get('error')}")
            
    except Exception as e:
        print(f"Error: {e}")

def example_custom_configuration():
    """Example: Generate tests with custom configuration."""
    
    print("Example 3: Custom configuration")
    print("-" * 50)
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Please set GEMINI_API_KEY environment variable")
        return
    
    # Example with custom settings
    repo_url = "https://github.com/your-username/your-spring-boot-app.git"
    
    try:
        generator = UnitTestGenerator(
            repo_url=repo_url,
            gemini_api_key=api_key
        )
        
        # Custom generation with higher standards
        results = generator.generate_tests(
            max_iterations=5,      # More iterations for better quality
            coverage_threshold=85.0  # Higher coverage target
        )
        
        if results.get("success"):
            print("✅ Test generation successful!")
            print_detailed_results(results)
        else:
            print(f"❌ Test generation failed: {results.get('error')}")
            
    except Exception as e:
        print(f"Error: {e}")

def print_results_summary(results):
    """Print a summary of generation results."""
    
    print("\n📊 Results Summary:")
    print(f"   Classes analyzed: {results['analysis_results']['total_classes']}")
    print(f"   Test classes generated: {results['test_generation']['test_classes_generated']}")
    print(f"   Tests passed: {results['final_test_results']['passed_tests']}/{results['final_test_results']['total_tests']}")
    print(f"   Success rate: {results['final_test_results']['success_rate']:.1f}%")
    print(f"   Line coverage: {results['coverage_results']['line_coverage']:.1f}%")

def print_detailed_results(results):
    """Print detailed generation results."""
    
    print("\n📊 Detailed Results:")
    
    analysis = results['analysis_results']
    print(f"   📋 Analysis:")
    print(f"      - Total classes: {analysis['total_classes']}")
    print(f"      - Spring components: {analysis['spring_components']}")
    print(f"      - Test candidates: {analysis['test_candidates']}")
    print(f"      - Packages: {analysis['packages']}")
    
    generation = results['test_generation']
    print(f"   🧪 Test Generation:")
    print(f"      - Test classes: {generation['test_classes_generated']}")
    print(f"      - Packages covered: {len(generation['organization']['packages'])}")
    
    test_results = results['final_test_results']
    print(f"   🎯 Test Execution:")
    print(f"      - Total tests: {test_results['total_tests']}")
    print(f"      - Passed: {test_results['passed_tests']}")
    print(f"      - Failed: {test_results['failed_tests']}")
    print(f"      - Success rate: {test_results['success_rate']:.1f}%")
    print(f"      - Execution time: {test_results['execution_time']:.2f}s")
    
    coverage = results['coverage_results']
    print(f"   📈 Coverage:")
    print(f"      - Line: {coverage['line_coverage']:.1f}%")
    print(f"      - Branch: {coverage['branch_coverage']:.1f}%")
    print(f"      - Method: {coverage['method_coverage']:.1f}%")
    print(f"      - Class: {coverage['class_coverage']:.1f}%")
    
    improvement = results['improvement_process']
    print(f"   🔄 Improvement:")
    print(f"      - Iterations: {len(improvement['iterations'])}")
    print(f"      - Improvements made: {improvement['total_improvements']}")

def main():
    """Run example demonstrations."""
    
    print("Spring Boot Unit Test Generator - Examples")
    print("=" * 60)
    
    print("\nChoose an example to run:")
    print("1. Generate tests from GitHub repository")
    print("2. Generate tests from local project")
    print("3. Generate tests with custom configuration")
    print("0. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (0-3): ").strip()
            
            if choice == "0":
                print("Goodbye!")
                break
            elif choice == "1":
                example_github_repo()
            elif choice == "2":
                example_local_project()
            elif choice == "3":
                example_custom_configuration()
            else:
                print("Invalid choice. Please enter 0-3.")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
