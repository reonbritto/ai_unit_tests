"""
Test script to verify the Spring Boot Unit Test Generator installation
and demonstrate basic functionality.
"""

import os
import sys
import traceback
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    
    print("Testing imports...")
    
    try:
        import google.generativeai as genai
        print("  ✅ google-generativeai")
    except ImportError as e:
        print(f"  ❌ google-generativeai: {e}")
        return False
    
    try:
        import git
        print("  ✅ gitpython")
    except ImportError as e:
        print(f"  ❌ gitpython: {e}")
        return False
    
    try:
        import javalang
        print("  ✅ javalang")
    except ImportError as e:
        print(f"  ❌ javalang: {e}")
        return False
    
    try:
        from config import Config
        print("  ✅ config module")
    except ImportError as e:
        print(f"  ❌ config module: {e}")
        return False
    
    try:
        from repo_handler import RepositoryHandler
        print("  ✅ repo_handler module")
    except ImportError as e:
        print(f"  ❌ repo_handler module: {e}")
        return False
    
    try:
        from repo_analyzer import RepoAnalyzer
        print("  ✅ repo_analyzer module")
    except ImportError as e:
        print(f"  ❌ repo_analyzer module: {e}")
        return False
    
    try:
        from test_generator import TestGenerator
        print("  ✅ test_generator module")
    except ImportError as e:
        print(f"  ❌ test_generator module: {e}")
        return False
    
    try:
        from test_runner import TestRunner
        print("  ✅ test_runner module")
    except ImportError as e:
        print(f"  ❌ test_runner module: {e}")
        return False
    
    try:
        from feedback_analyzer import FeedbackAnalyzer
        print("  ✅ feedback_analyzer module")
    except ImportError as e:
        print(f"  ❌ feedback_analyzer module: {e}")
        return False
    
    try:
        from test_suite_manager import TestSuiteManager
        print("  ✅ test_suite_manager module")
    except ImportError as e:
        print(f"  ❌ test_suite_manager module: {e}")
        return False
    
    try:
        from main import UnitTestGenerator
        print("  ✅ main module")
    except ImportError as e:
        print(f"  ❌ main module: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration and API key setup."""
    
    print("\nTesting configuration...")
    
    try:
        from config import Config
        config = Config()
        
        if config.GEMINI_API_KEY:
            print("  ✅ GEMINI_API_KEY is set")
            
            # Test Gemini API connection
            try:
                import google.generativeai as genai
                genai.configure(api_key=config.GEMINI_API_KEY)
                model = genai.GenerativeModel(config.GEMINI_MODEL)
                print("  ✅ Gemini AI connection successful")
                return True
            except Exception as e:
                print(f"  ❌ Gemini AI connection failed: {e}")
                return False
        else:
            print("  ❌ GEMINI_API_KEY is not set")
            print("     Please set the environment variable: set GEMINI_API_KEY=your-api-key")
            return False
            
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False

def test_build_tools():
    """Test availability of build tools."""
    
    print("\nTesting build tools...")
    
    import subprocess
    
    # Test Maven
    try:
        result = subprocess.run(["mvn", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("  ✅ Maven is available")
        else:
            print("  ❌ Maven is not working properly")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("  ❌ Maven is not installed or not in PATH")
    
    # Test Gradle
    try:
        result = subprocess.run(["gradle", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("  ✅ Gradle is available")
        else:
            print("  ❌ Gradle is not working properly")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("  ❌ Gradle is not installed or not in PATH")
    
    # Test Git
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("  ✅ Git is available")
            return True
        else:
            print("  ❌ Git is not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("  ❌ Git is not installed or not in PATH")
        return False

def test_sample_java_parsing():
    """Test Java code parsing functionality."""
    
    print("\nTesting Java parsing...")
    
    try:
        import javalang
        
        # Sample Java code
        sample_code = '''
package com.example.demo;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;

@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    public User findById(Long id) {
        return userRepository.findById(id).orElse(null);
    }
    
    public User save(User user) {
        return userRepository.save(user);
    }
}
'''
        
        # Parse the code
        tree = javalang.parse.parse(sample_code)
        
        # Extract basic information
        package_name = tree.package.name if tree.package else ""
        imports = [imp.path for imp in tree.imports] if tree.imports else []
        
        # Find classes
        classes = list(tree.filter(javalang.tree.ClassDeclaration))
        
        if classes and package_name and imports:
            print("  ✅ Java parsing is working correctly")
            print(f"     Package: {package_name}")
            print(f"     Imports: {len(imports)}")
            print(f"     Classes: {len(classes)}")
            return True
        else:
            print("  ❌ Java parsing failed to extract expected information")
            return False
            
    except Exception as e:
        print(f"  ❌ Java parsing test failed: {e}")
        return False

def test_unit_test_generator_initialization():
    """Test UnitTestGenerator initialization."""
    
    print("\nTesting UnitTestGenerator initialization...")
    
    try:
        from main import UnitTestGenerator
        
        # Test with API key from environment
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("  ⚠️ Skipping initialization test - no API key available")
            return True
        
        generator = UnitTestGenerator(
            local_path=".",  # Current directory
            gemini_api_key=api_key
        )
        
        print("  ✅ UnitTestGenerator initialized successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ UnitTestGenerator initialization failed: {e}")
        return False

def create_sample_spring_boot_project():
    """Create a minimal sample Spring Boot project for testing."""
    
    print("\nCreating sample Spring Boot project...")
    
    sample_dir = Path("sample_spring_project")
    
    try:
        # Create directory structure
        (sample_dir / "src" / "main" / "java" / "com" / "example").mkdir(parents=True, exist_ok=True)
        (sample_dir / "src" / "test" / "java" / "com" / "example").mkdir(parents=True, exist_ok=True)
        
        # Create pom.xml
        pom_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>demo</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>
    
    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter</artifactId>
            <version>2.7.0</version>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <version>2.7.0</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>'''
        
        with open(sample_dir / "pom.xml", 'w') as f:
            f.write(pom_content)
        
        # Create sample Java class
        java_content = '''package com.example;

import org.springframework.stereotype.Service;

@Service
public class CalculatorService {
    
    public int add(int a, int b) {
        return a + b;
    }
    
    public int subtract(int a, int b) {
        return a - b;
    }
    
    public int multiply(int a, int b) {
        return a * b;
    }
    
    public double divide(int a, int b) {
        if (b == 0) {
            throw new IllegalArgumentException("Division by zero");
        }
        return (double) a / b;
    }
}'''
        
        with open(sample_dir / "src" / "main" / "java" / "com" / "example" / "CalculatorService.java", 'w') as f:
            f.write(java_content)
        
        print(f"  ✅ Sample project created at: {sample_dir.absolute()}")
        return sample_dir.absolute()
        
    except Exception as e:
        print(f"  ❌ Failed to create sample project: {e}")
        return None

def run_tests():
    """Run all tests."""
    
    print("Spring Boot Unit Test Generator - Installation Test")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Build Tools Test", test_build_tools),
        ("Java Parsing Test", test_sample_java_parsing),
        ("Generator Initialization Test", test_unit_test_generator_initialization)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<8} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The system is ready to use.")
        
        # Offer to create sample project
        try:
            response = input("\nWould you like to create a sample Spring Boot project for testing? (y/n): ")
            if response.lower().startswith('y'):
                sample_path = create_sample_spring_boot_project()
                if sample_path:
                    print(f"\nYou can now test the generator with:")
                    print(f"python main.py --local-path \"{sample_path}\"")
        except KeyboardInterrupt:
            pass
            
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check the installation.")
        print("\nCommon issues:")
        print("- Missing API key: Set GEMINI_API_KEY environment variable")
        print("- Missing dependencies: Run 'pip install -r requirements.txt'")
        print("- Missing build tools: Install Maven, Gradle, or Git")

def main():
    """Main entry point."""
    
    try:
        run_tests()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error during testing: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
