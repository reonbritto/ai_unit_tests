import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import google.generativeai as genai
from config import Config

@dataclass
class TestCase:
    """Represents a generated test case."""
    class_name: str
    method_name: str
    test_code: str
    description: str
    test_type: str  # unit, integration, etc.

@dataclass
class TestClass:
    """Represents a complete test class."""
    original_class: str
    test_class_name: str
    package: str
    imports: List[str]
    test_cases: List[TestCase]
    setup_code: str
    teardown_code: str
    full_code: str

class TestGenerator:
    """Generates JUnit test cases using Google Gemini AI."""
    
    def __init__(self, api_key: str):
        self.config = Config()
        self.api_key = api_key
        self._initialize_gemini()
        self.generated_tests = []
    
    def _initialize_gemini(self):
        """Initialize Gemini AI client."""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.config.GEMINI_MODEL)
            print(f"Initialized Gemini AI with model: {self.config.GEMINI_MODEL}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini AI: {e}")
    
    def generate_tests(self, metadata: Dict[str, Any], project_path: Path) -> List[TestClass]:
        """
        Generate JUnit test cases for all test candidates in the metadata.
        
        Args:
            metadata: Project metadata from RepoAnalyzer
            project_path: Path to the Spring Boot project
            
        Returns:
            List of generated test classes
        """
        print("Starting test generation...")
        
        test_candidates = metadata.get("test_candidates", [])
        if not test_candidates:
            print("No test candidates found in metadata")
            return []
        
        print(f"Generating tests for {len(test_candidates)} classes")
        
        self.generated_tests = []
        
        for class_info in test_candidates:
            try:
                test_class = self._generate_test_for_class(class_info, metadata, project_path)
                if test_class:
                    self.generated_tests.append(test_class)
                    print(f"Generated test for: {class_info['full_name']}")
            except Exception as e:
                print(f"Failed to generate test for {class_info['full_name']}: {e}")
                continue
        
        print(f"Generated {len(self.generated_tests)} test classes")
        return self.generated_tests
    
    def _generate_test_for_class(self, class_info: Dict[str, Any], 
                                metadata: Dict[str, Any], project_path: Path) -> Optional[TestClass]:
        """Generate a test class for a specific class."""
        
        # Create prompt for Gemini
        prompt = self._create_test_generation_prompt(class_info, metadata)
        
        try:
            # Generate test code using Gemini
            response = self.model.generate_content(prompt)
            test_code = response.text
            
            # Parse and structure the generated test
            test_class = self._parse_generated_test(test_code, class_info)
            
            # Save test file
            self._save_test_file(test_class, project_path)
            
            return test_class
            
        except Exception as e:
            print(f"Error generating test for {class_info['full_name']}: {e}")
            return None
    
    def _create_test_generation_prompt(self, class_info: Dict[str, Any], 
                                     metadata: Dict[str, Any]) -> str:
        """Create a detailed prompt for Gemini to generate test cases."""
        
        # Extract relevant information
        class_name = class_info['name']
        package = class_info['package']
        methods = class_info['methods']
        fields = class_info['fields']
        annotations = class_info['annotations']
        
        # Find dependencies for mocking
        dependencies = self._find_class_dependencies(class_info, metadata)
        
        prompt = f"""
You are an expert Java developer specializing in Spring Boot testing. Generate comprehensive JUnit 5 test cases for the following Spring Boot class.

## Class to Test:
**Class Name:** {class_name}
**Package:** {package}
**Annotations:** {', '.join(annotations)}

## Class Structure:
### Fields:
{self._format_fields_for_prompt(fields)}

### Methods:
{self._format_methods_for_prompt(methods)}

## Dependencies (for mocking):
{self._format_dependencies_for_prompt(dependencies)}

## Requirements:
1. Use JUnit 5 (@Test, @BeforeEach, @AfterEach, etc.)
2. Use Mockito for mocking dependencies (@Mock, @InjectMocks, @MockitoExtension)
3. Use Spring Boot testing annotations where appropriate (@SpringBootTest, @WebMvcTest, @DataJpaTest, etc.)
4. Test all public methods
5. Include positive test cases, negative test cases, and edge cases
6. Test exception scenarios where applicable
7. Use proper assertions (assertEquals, assertThrows, assertNotNull, etc.)
8. Follow Spring Boot testing best practices
9. Include setup and teardown methods if needed
10. Use descriptive test method names (should_ReturnResult_When_Condition format)

## Test Class Structure:
- Package declaration
- All necessary imports
- Class-level annotations
- Field declarations with @Mock and @InjectMocks
- @BeforeEach setup method
- Test methods for each scenario
- @AfterEach teardown method if needed

## Special Considerations:
- If it's a @RestController, use @WebMvcTest and MockMvc
- If it's a @Service, focus on business logic testing
- If it's a @Repository, use @DataJpaTest
- Mock all external dependencies
- Test both success and failure scenarios
- Include parameterized tests where appropriate

Generate a complete, compilable test class with comprehensive test coverage.
"""
        
        return prompt
    
    def _format_fields_for_prompt(self, fields: List[Dict[str, Any]]) -> str:
        """Format fields information for the prompt."""
        if not fields:
            return "No fields"
        
        formatted = []
        for field in fields:
            annotations_str = f"@{', @'.join(field['annotations'])}" if field['annotations'] else ""
            modifiers_str = ' '.join(field['modifiers'])
            formatted.append(f"- {annotations_str} {modifiers_str} {field['type']} {field['name']}")
        
        return '\n'.join(formatted)
    
    def _format_methods_for_prompt(self, methods: List[Dict[str, Any]]) -> str:
        """Format methods information for the prompt."""
        if not methods:
            return "No methods"
        
        formatted = []
        for method in methods:
            if method['is_constructor']:
                continue  # Skip constructors in method list
            
            annotations_str = f"@{', @'.join(method['annotations'])}" if method['annotations'] else ""
            modifiers_str = ' '.join(method['modifiers'])
            params_str = ', '.join([f"{p['type']} {p['name']}" for p in method['parameters']])
            exceptions_str = f" throws {', '.join(method['exceptions'])}" if method['exceptions'] else ""
            
            formatted.append(
                f"- {annotations_str} {modifiers_str} {method['return_type']} "
                f"{method['name']}({params_str}){exceptions_str}"
            )
        
        return '\n'.join(formatted)
    
    def _format_dependencies_for_prompt(self, dependencies: List[str]) -> str:
        """Format dependencies information for the prompt."""
        if not dependencies:
            return "No external dependencies to mock"
        
        return '\n'.join([f"- {dep}" for dep in dependencies])
    
    def _find_class_dependencies(self, class_info: Dict[str, Any], 
                               metadata: Dict[str, Any]) -> List[str]:
        """Find dependencies that should be mocked in tests."""
        dependencies = []
        
        # Look for @Autowired fields
        for field in class_info['fields']:
            if 'Autowired' in field['annotations']:
                dependencies.append(field['type'])
        
        # Look for constructor injection
        for method in class_info['methods']:
            if method['is_constructor'] and method['parameters']:
                # Assume constructor parameters are dependencies for Spring components
                if any(ann in class_info['annotations'] for ann in ['Service', 'Component', 'Controller', 'RestController']):
                    dependencies.extend([param['type'] for param in method['parameters']])
        
        # Look for method parameters that might be other services
        project_classes = {cls['name'] for cls in metadata.get('classes', [])}
        for method in class_info['methods']:
            for param in method['parameters']:
                if param['type'] in project_classes:
                    dependencies.append(param['type'])
        
        return list(set(dependencies))  # Remove duplicates
    
    def _parse_generated_test(self, test_code: str, class_info: Dict[str, Any]) -> TestClass:
        """Parse the generated test code and create a TestClass object."""
        
        # Clean up the generated code
        test_code = self._clean_generated_code(test_code)
        
        # Extract components
        package = self._extract_package(test_code) or class_info['package']
        imports = self._extract_imports(test_code)
        test_class_name = f"{class_info['name']}Test"
        
        # Create test cases (for now, treat the whole class as one test case)
        test_cases = [
            TestCase(
                class_name=class_info['name'],
                method_name="comprehensive_test",
                test_code=test_code,
                description=f"Comprehensive test for {class_info['name']}",
                test_type="unit"
            )
        ]
        
        return TestClass(
            original_class=class_info['name'],
            test_class_name=test_class_name,
            package=package,
            imports=imports,
            test_cases=test_cases,
            setup_code="",
            teardown_code="",
            full_code=test_code
        )
    
    def _clean_generated_code(self, code: str) -> str:
        """Clean and format the generated test code."""
        # Remove markdown code blocks if present
        code = re.sub(r'```java\n?', '', code)
        code = re.sub(r'```\n?', '', code)
        
        # Remove any leading/trailing whitespace
        code = code.strip()
        
        # Ensure proper line endings
        code = code.replace('\r\n', '\n')
        
        return code
    
    def _extract_package(self, code: str) -> Optional[str]:
        """Extract package declaration from generated code."""
        match = re.search(r'package\s+([\w.]+);', code)
        return match.group(1) if match else None
    
    def _extract_imports(self, code: str) -> List[str]:
        """Extract import statements from generated code."""
        imports = []
        import_pattern = r'import\s+(static\s+)?([\w.]+(?:\.\*)?);'
        
        for match in re.finditer(import_pattern, code):
            imports.append(match.group(2))
        
        return imports
    
    def _save_test_file(self, test_class: TestClass, project_path: Path):
        """Save the generated test class to a file."""
        # Determine test directory
        test_dir = project_path / "src" / "test" / "java"
        
        # Create package directory structure
        if test_class.package:
            package_path = test_dir / test_class.package.replace('.', os.sep)
        else:
            package_path = test_dir
        
        package_path.mkdir(parents=True, exist_ok=True)
        
        # Create test file
        test_file = package_path / f"{test_class.test_class_name}.java"
        
        try:
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_class.full_code)
            
            print(f"Saved test file: {test_file}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to save test file {test_file}: {e}")
    
    def regenerate_test(self, class_info: Dict[str, Any], metadata: Dict[str, Any],
                       project_path: Path, feedback: str) -> Optional[TestClass]:
        """Regenerate a test class based on feedback."""
        
        # Create improved prompt with feedback
        original_prompt = self._create_test_generation_prompt(class_info, metadata)
        
        feedback_prompt = f"""
{original_prompt}

## Previous Test Issues:
{feedback}

## Additional Requirements:
Please address the issues mentioned above and generate an improved version of the test class.
Focus on fixing the specific problems while maintaining comprehensive test coverage.
"""
        
        try:
            response = self.model.generate_content(feedback_prompt)
            test_code = response.text
            
            test_class = self._parse_generated_test(test_code, class_info)
            self._save_test_file(test_class, project_path)
            
            print(f"Regenerated test for: {class_info['full_name']}")
            return test_class
            
        except Exception as e:
            print(f"Error regenerating test for {class_info['full_name']}: {e}")
            return None
    
    def get_generated_tests(self) -> List[TestClass]:
        """Get all generated test classes."""
        return self.generated_tests
