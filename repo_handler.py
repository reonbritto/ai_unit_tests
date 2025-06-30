import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse
import git
from config import Config

class RepositoryHandler:
    """Handles repository cloning and validation for Spring Boot projects."""
    
    def __init__(self):
        self.config = Config()
        self.temp_dir = Path(self.config.TEMP_DIR)
        self.temp_dir.mkdir(exist_ok=True)
    
    def handle_repository(self, repo_url: Optional[str] = None, 
                         local_path: Optional[str] = None) -> Tuple[Path, bool]:
        """
        Handle repository access - either clone from URL or validate local path.
        
        Args:
            repo_url: GitHub repository URL
            local_path: Local directory path
            
        Returns:
            Tuple of (project_path, is_temp) where is_temp indicates if cleanup is needed
        """
        if repo_url:
            return self._clone_repository(repo_url), True
        elif local_path:
            return self._validate_local_path(local_path), False
        else:
            raise ValueError("Either repo_url or local_path must be provided")
    
    def _clone_repository(self, repo_url: str) -> Path:
        """Clone repository from GitHub URL."""
        try:
            # Parse repository name from URL
            parsed_url = urlparse(repo_url)
            repo_name = Path(parsed_url.path).stem
            
            clone_path = self.temp_dir / repo_name
            
            # Remove existing directory if it exists
            if clone_path.exists():
                shutil.rmtree(clone_path)
            
            print(f"Cloning repository: {repo_url}")
            
            # Clone with timeout
            process = subprocess.Popen(
                ["git", "clone", repo_url, str(clone_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=self.config.REPO_CLONE_TIMEOUT)
                if process.returncode != 0:
                    raise RuntimeError(f"Git clone failed: {stderr}")
            except subprocess.TimeoutExpired:
                process.kill()
                raise RuntimeError("Repository cloning timed out")
            
            print(f"Repository cloned to: {clone_path}")
            return self._validate_spring_boot_project(clone_path)
            
        except Exception as e:
            raise RuntimeError(f"Failed to clone repository: {str(e)}")
    
    def _validate_local_path(self, local_path: str) -> Path:
        """Validate and return local project path."""
        path = Path(local_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Local path does not exist: {local_path}")
        
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {local_path}")
        
        return self._validate_spring_boot_project(path)
    
    def _validate_spring_boot_project(self, project_path: Path) -> Path:
        """Validate that the project is a Spring Boot project."""
        # Check for Maven or Gradle build files
        has_maven = (project_path / "pom.xml").exists()
        has_gradle = (project_path / "build.gradle").exists() or (project_path / "build.gradle.kts").exists()
        
        if not (has_maven or has_gradle):
            raise ValueError(f"No Maven (pom.xml) or Gradle (build.gradle) build file found in: {project_path}")
        
        # Check for Java source directory
        src_main_java = project_path / "src" / "main" / "java"
        if not src_main_java.exists():
            raise ValueError(f"No Java source directory found at: {src_main_java}")
        
        # Look for Spring Boot indicators
        spring_indicators = self._find_spring_boot_indicators(src_main_java)
        if not spring_indicators:
            print("Warning: No clear Spring Boot indicators found. Proceeding anyway...")
        else:
            print(f"Spring Boot project detected with indicators: {spring_indicators}")
        
        return project_path
    
    def _find_spring_boot_indicators(self, src_dir: Path) -> list:
        """Find indicators that this is a Spring Boot project."""
        indicators = []
        
        # Look for common Spring Boot annotations and imports
        spring_patterns = [
            "@SpringBootApplication",
            "@RestController",
            "@Service",
            "@Repository",
            "@Component",
            "@Autowired",
            "org.springframework"
        ]
        
        java_files = list(src_dir.rglob("*.java"))
        
        for java_file in java_files[:10]:  # Check first 10 files for performance
            try:
                content = java_file.read_text(encoding='utf-8')
                for pattern in spring_patterns:
                    if pattern in content and pattern not in indicators:
                        indicators.append(pattern)
            except (UnicodeDecodeError, PermissionError):
                continue
        
        return indicators
    
    def get_build_tool(self, project_path: Path) -> str:
        """Determine the build tool (Maven or Gradle) for the project."""
        if (project_path / "pom.xml").exists():
            return "maven"
        elif (project_path / "build.gradle").exists() or (project_path / "build.gradle.kts").exists():
            return "gradle"
        else:
            raise ValueError("No supported build tool found")
    
    def cleanup(self, project_path: Path, is_temp: bool):
        """Clean up temporary directories if needed."""
        if is_temp and project_path.exists() and self.temp_dir in project_path.parents:
            try:
                shutil.rmtree(project_path)
                print(f"Cleaned up temporary directory: {project_path}")
            except Exception as e:
                print(f"Warning: Failed to clean up temporary directory: {e}")
    
    def __del__(self):
        """Cleanup on destruction."""
        # Clean up entire temp directory if it's empty or on exit
        try:
            if self.temp_dir.exists() and not any(self.temp_dir.iterdir()):
                shutil.rmtree(self.temp_dir)
        except:
            pass
