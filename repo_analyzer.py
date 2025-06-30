import json
import javalang
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from config import Config

@dataclass
class MethodInfo:
    """Information about a Java method."""
    name: str
    return_type: str
    parameters: List[Dict[str, str]]
    annotations: List[str]
    modifiers: List[str]
    is_static: bool
    is_constructor: bool
    exceptions: List[str]

@dataclass
class FieldInfo:
    """Information about a Java field."""
    name: str
    type: str
    annotations: List[str]
    modifiers: List[str]
    is_static: bool

@dataclass
class ClassInfo:
    """Information about a Java class."""
    name: str
    package: str
    full_name: str
    annotations: List[str]
    modifiers: List[str]
    extends: Optional[str]
    implements: List[str]
    methods: List[MethodInfo]
    fields: List[FieldInfo]
    is_interface: bool
    is_enum: bool
    is_abstract: bool
    dependencies: List[str]
    file_path: str

class RepoAnalyzer:
    """Analyzes Spring Boot repository and extracts metadata."""
    
    def __init__(self):
        self.config = Config()
        self.metadata = {
            "project_info": {},
            "classes": [],
            "packages": set(),
            "dependencies": set(),
            "spring_components": [],
            "test_candidates": []
        }
    
    def analyze_repository(self, project_path: Path) -> Dict[str, Any]:
        """
        Analyze the Spring Boot repository and extract comprehensive metadata.
        
        Args:
            project_path: Path to the Spring Boot project
            
        Returns:
            Dictionary containing project metadata
        """
        print("Starting repository analysis...")
        
        # Analyze project structure
        self._analyze_project_info(project_path)
        
        # Find and analyze Java files
        java_files = self._find_java_files(project_path)
        print(f"Found {len(java_files)} Java files to analyze")
        
        # Parse each Java file
        for java_file in java_files:
            try:
                self._analyze_java_file(java_file, project_path)
            except Exception as e:
                print(f"Warning: Failed to analyze {java_file}: {e}")
                continue
        
        # Post-process metadata
        self._post_process_metadata()
        
        # Save metadata to file
        metadata_file = project_path / self.config.METADATA_FILE
        self._save_metadata(metadata_file)
        
        print(f"Analysis complete. Found {len(self.metadata['classes'])} classes")
        print(f"Metadata saved to: {metadata_file}")
        
        return self.metadata
    
    def _analyze_project_info(self, project_path: Path):
        """Analyze general project information."""
        self.metadata["project_info"] = {
            "name": project_path.name,
            "path": str(project_path),
            "has_maven": (project_path / "pom.xml").exists(),
            "has_gradle": (project_path / "build.gradle").exists() or (project_path / "build.gradle.kts").exists(),
            "source_dirs": [],
            "test_dirs": []
        }
        
        # Find source and test directories
        src_main_java = project_path / "src" / "main" / "java"
        src_test_java = project_path / "src" / "test" / "java"
        
        if src_main_java.exists():
            self.metadata["project_info"]["source_dirs"].append(str(src_main_java))
        
        if src_test_java.exists():
            self.metadata["project_info"]["test_dirs"].append(str(src_test_java))
    
    def _find_java_files(self, project_path: Path) -> List[Path]:
        """Find all Java files in the project."""
        java_files = []
        
        # Look in main source directory
        src_main_java = project_path / "src" / "main" / "java"
        if src_main_java.exists():
            java_files.extend(src_main_java.rglob("*.java"))
        
        return java_files
    
    def _analyze_java_file(self, java_file: Path, project_root: Path):
        """Analyze a single Java file and extract class information."""
        try:
            content = java_file.read_text(encoding='utf-8')
            
            # Parse Java content
            tree = javalang.parse.parse(content)
            
            # Extract package information
            package_name = tree.package.name if tree.package else ""
            self.metadata["packages"].add(package_name)
            
            # Extract imports
            imports = [imp.path for imp in tree.imports] if tree.imports else []
            self.metadata["dependencies"].update(imports)
            
            # Analyze each class/interface in the file
            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                class_info = self._extract_class_info(node, package_name, imports, java_file, project_root)
                self.metadata["classes"].append(class_info)
                
                # Check if it's a Spring component
                if self._is_spring_component(class_info):
                    self.metadata["spring_components"].append(class_info)
                
                # Check if it's a test candidate
                if self._is_test_candidate(class_info):
                    self.metadata["test_candidates"].append(class_info)
            
            # Analyze interfaces
            for path, node in tree.filter(javalang.tree.InterfaceDeclaration):
                class_info = self._extract_interface_info(node, package_name, imports, java_file, project_root)
                self.metadata["classes"].append(class_info)
            
        except Exception as e:
            print(f"Error parsing {java_file}: {e}")
            raise
    
    def _extract_class_info(self, node, package_name: str, imports: List[str], 
                          java_file: Path, project_root: Path) -> ClassInfo:
        """Extract information from a class declaration."""
        
        # Basic class information
        class_name = node.name
        full_name = f"{package_name}.{class_name}" if package_name else class_name
        
        # Annotations
        annotations = [self._extract_annotation_name(ann) for ann in (node.annotations or [])]
        
        # Modifiers
        modifiers = list(node.modifiers) if node.modifiers else []
        
        # Inheritance
        extends = node.extends.name if node.extends else None
        implements = [impl.name for impl in (node.implements or [])]
        
        # Methods
        methods = []
        if node.body:
            for member in node.body:
                if isinstance(member, javalang.tree.MethodDeclaration):
                    method_info = self._extract_method_info(member)
                    methods.append(method_info)
                elif isinstance(member, javalang.tree.ConstructorDeclaration):
                    constructor_info = self._extract_constructor_info(member, class_name)
                    methods.append(constructor_info)
        
        # Fields
        fields = []
        if node.body:
            for member in node.body:
                if isinstance(member, javalang.tree.FieldDeclaration):
                    field_infos = self._extract_field_info(member)
                    fields.extend(field_infos)
        
        # File path relative to project root
        relative_path = java_file.relative_to(project_root)
        
        return ClassInfo(
            name=class_name,
            package=package_name,
            full_name=full_name,
            annotations=annotations,
            modifiers=modifiers,
            extends=extends,
            implements=implements,
            methods=methods,
            fields=fields,
            is_interface=False,
            is_enum=False,
            is_abstract="abstract" in modifiers,
            dependencies=imports,
            file_path=str(relative_path)
        )
    
    def _extract_interface_info(self, node, package_name: str, imports: List[str],
                              java_file: Path, project_root: Path) -> ClassInfo:
        """Extract information from an interface declaration."""
        
        class_name = node.name
        full_name = f"{package_name}.{class_name}" if package_name else class_name
        
        annotations = [self._extract_annotation_name(ann) for ann in (node.annotations or [])]
        modifiers = list(node.modifiers) if node.modifiers else []
        extends_list = [ext.name for ext in (node.extends or [])]
        
        # Methods (interface methods)
        methods = []
        if node.body:
            for member in node.body:
                if isinstance(member, javalang.tree.MethodDeclaration):
                    method_info = self._extract_method_info(member)
                    methods.append(method_info)
        
        relative_path = java_file.relative_to(project_root)
        
        return ClassInfo(
            name=class_name,
            package=package_name,
            full_name=full_name,
            annotations=annotations,
            modifiers=modifiers,
            extends=None,
            implements=extends_list,  # For interfaces, extends becomes implements
            methods=methods,
            fields=[],
            is_interface=True,
            is_enum=False,
            is_abstract=True,
            dependencies=imports,
            file_path=str(relative_path)
        )
    
    def _extract_method_info(self, method_node) -> MethodInfo:
        """Extract information from a method declaration."""
        
        name = method_node.name
        return_type = self._get_type_name(method_node.return_type) if method_node.return_type else "void"
        
        # Parameters
        parameters = []
        if method_node.parameters:
            for param in method_node.parameters:
                param_info = {
                    "name": param.name,
                    "type": self._get_type_name(param.type)
                }
                parameters.append(param_info)
        
        # Annotations
        annotations = [self._extract_annotation_name(ann) for ann in (method_node.annotations or [])]
        
        # Modifiers
        modifiers = list(method_node.modifiers) if method_node.modifiers else []
        
        # Exceptions
        exceptions = []
        if method_node.throws:
            exceptions = [self._get_type_name(exc) for exc in method_node.throws]
        
        return MethodInfo(
            name=name,
            return_type=return_type,
            parameters=parameters,
            annotations=annotations,
            modifiers=modifiers,
            is_static="static" in modifiers,
            is_constructor=False,
            exceptions=exceptions
        )
    
    def _extract_constructor_info(self, constructor_node, class_name: str) -> MethodInfo:
        """Extract information from a constructor declaration."""
        
        # Parameters
        parameters = []
        if constructor_node.parameters:
            for param in constructor_node.parameters:
                param_info = {
                    "name": param.name,
                    "type": self._get_type_name(param.type)
                }
                parameters.append(param_info)
        
        # Annotations
        annotations = [self._extract_annotation_name(ann) for ann in (constructor_node.annotations or [])]
        
        # Modifiers
        modifiers = list(constructor_node.modifiers) if constructor_node.modifiers else []
        
        # Exceptions
        exceptions = []
        if constructor_node.throws:
            exceptions = [self._get_type_name(exc) for exc in constructor_node.throws]
        
        return MethodInfo(
            name=class_name,  # Constructor name is same as class name
            return_type=class_name,
            parameters=parameters,
            annotations=annotations,
            modifiers=modifiers,
            is_static=False,
            is_constructor=True,
            exceptions=exceptions
        )
    
    def _extract_field_info(self, field_node) -> List[FieldInfo]:
        """Extract information from field declarations."""
        fields = []
        
        field_type = self._get_type_name(field_node.type)
        annotations = [self._extract_annotation_name(ann) for ann in (field_node.annotations or [])]
        modifiers = list(field_node.modifiers) if field_node.modifiers else []
        
        # A field declaration can declare multiple fields
        for declarator in field_node.declarators:
            field_info = FieldInfo(
                name=declarator.name,
                type=field_type,
                annotations=annotations,
                modifiers=modifiers,
                is_static="static" in modifiers
            )
            fields.append(field_info)
        
        return fields
    
    def _get_type_name(self, type_node) -> str:
        """Extract type name from type node."""
        if hasattr(type_node, 'name'):
            return type_node.name
        elif hasattr(type_node, 'element_type'):
            # Array type
            return f"{self._get_type_name(type_node.element_type)}[]"
        elif hasattr(type_node, 'type'):
            # Generic type
            return self._get_type_name(type_node.type)
        else:
            return str(type_node)
    
    def _extract_annotation_name(self, annotation_node) -> str:
        """Extract annotation name."""
        if hasattr(annotation_node, 'name'):
            return annotation_node.name
        else:
            return str(annotation_node)
    
    def _is_spring_component(self, class_info: ClassInfo) -> bool:
        """Check if a class is a Spring component."""
        spring_annotations = {
            'Component', 'Service', 'Repository', 'Controller', 'RestController',
            'Configuration', 'SpringBootApplication', 'EnableAutoConfiguration'
        }
        
        class_annotations = set(class_info.annotations)
        return bool(spring_annotations.intersection(class_annotations))
    
    def _is_test_candidate(self, class_info: ClassInfo) -> bool:
        """Check if a class is a good candidate for unit testing."""
        # Skip test classes, interfaces, enums, and abstract classes
        if (class_info.is_interface or class_info.is_enum or 
            class_info.is_abstract or 'Test' in class_info.name):
            return False
        
        # Classes with business logic (have non-getter/setter methods)
        business_methods = [
            method for method in class_info.methods
            if not method.is_constructor and
               not self._is_getter_setter(method) and
               'public' in method.modifiers
        ]
        
        return len(business_methods) > 0
    
    def _is_getter_setter(self, method: MethodInfo) -> bool:
        """Check if a method is a simple getter or setter."""
        name = method.name.lower()
        return (name.startswith('get') or name.startswith('set') or 
                name.startswith('is') or name.startswith('has'))
    
    def _post_process_metadata(self):
        """Post-process metadata to convert sets to lists for JSON serialization."""
        self.metadata["packages"] = list(self.metadata["packages"])
        self.metadata["dependencies"] = list(self.metadata["dependencies"])
        
        # Convert dataclass objects to dictionaries
        self.metadata["classes"] = [asdict(cls) for cls in self.metadata["classes"]]
        self.metadata["spring_components"] = [asdict(cls) for cls in self.metadata["spring_components"]]
        self.metadata["test_candidates"] = [asdict(cls) for cls in self.metadata["test_candidates"]]
    
    def _save_metadata(self, metadata_file: Path):
        """Save metadata to JSON file."""
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise RuntimeError(f"Failed to save metadata: {e}")
    
    def load_metadata(self, metadata_file: Path) -> Dict[str, Any]:
        """Load metadata from JSON file."""
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load metadata: {e}")
