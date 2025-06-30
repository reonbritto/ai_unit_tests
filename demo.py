"""
Quick demonstration of the Spring Boot Unit Test Generator.

This script creates a minimal Spring Boot project and demonstrates
the test generation process step by step.
"""

import os
import shutil
from pathlib import Path
from main import UnitTestGenerator

def create_demo_project():
    """Create a minimal Spring Boot project for demonstration."""
    
    print("Creating demo Spring Boot project...")
    
    demo_dir = Path("demo_spring_project")
    
    # Clean up if exists
    if demo_dir.exists():
        shutil.rmtree(demo_dir)
    
    # Create directory structure
    (demo_dir / "src" / "main" / "java" / "com" / "demo").mkdir(parents=True)
    (demo_dir / "src" / "test" / "java" / "com" / "demo").mkdir(parents=True)
    (demo_dir / "src" / "main" / "resources").mkdir(parents=True)
    (demo_dir / "src" / "test" / "resources").mkdir(parents=True)
    
    # Create pom.xml
    pom_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.demo</groupId>
    <artifactId>spring-boot-demo</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>
    
    <name>Spring Boot Demo</name>
    <description>Demo project for Unit Test Generator</description>
    
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.7.14</version>
        <relativePath/>
    </parent>
    
    <properties>
        <java.version>11</java.version>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>
        
        <!-- Test dependencies -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.jacoco</groupId>
                <artifactId>jacoco-maven-plugin</artifactId>
                <version>0.8.7</version>
                <executions>
                    <execution>
                        <goals>
                            <goal>prepare-agent</goal>
                        </goals>
                    </execution>
                    <execution>
                        <id>report</id>
                        <phase>test</phase>
                        <goals>
                            <goal>report</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>'''
    
    with open(demo_dir / "pom.xml", 'w') as f:
        f.write(pom_content)
    
    # Create User entity
    user_entity = '''package com.demo.entity;

import javax.persistence.*;

@Entity
@Table(name = "users")
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String name;
    
    @Column(unique = true, nullable = false)
    private String email;
    
    private Integer age;
    
    // Constructors
    public User() {}
    
    public User(String name, String email, Integer age) {
        this.name = name;
        this.email = email;
        this.age = age;
    }
    
    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    
    public Integer getAge() { return age; }
    public void setAge(Integer age) { this.age = age; }
}'''
    
    (demo_dir / "src" / "main" / "java" / "com" / "demo" / "entity").mkdir(parents=True)
    with open(demo_dir / "src" / "main" / "java" / "com" / "demo" / "entity" / "User.java", 'w') as f:
        f.write(user_entity)
    
    # Create UserRepository
    user_repository = '''package com.demo.repository;

import com.demo.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    Optional<User> findByEmail(String email);
    
    List<User> findByAgeGreaterThan(Integer age);
    
    @Query("SELECT u FROM User u WHERE u.name LIKE %:name%")
    List<User> findByNameContaining(@Param("name") String name);
    
    boolean existsByEmail(String email);
}'''
    
    (demo_dir / "src" / "main" / "java" / "com" / "demo" / "repository").mkdir(parents=True)
    with open(demo_dir / "src" / "main" / "java" / "com" / "demo" / "repository" / "UserRepository.java", 'w') as f:
        f.write(user_repository)
    
    # Create UserService
    user_service = '''package com.demo.service;

import com.demo.entity.User;
import com.demo.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    public User createUser(User user) {
        if (user == null) {
            throw new IllegalArgumentException("User cannot be null");
        }
        
        if (userRepository.existsByEmail(user.getEmail())) {
            throw new RuntimeException("User with email already exists: " + user.getEmail());
        }
        
        return userRepository.save(user);
    }
    
    public Optional<User> findById(Long id) {
        if (id == null) {
            throw new IllegalArgumentException("ID cannot be null");
        }
        return userRepository.findById(id);
    }
    
    public Optional<User> findByEmail(String email) {
        if (email == null || email.trim().isEmpty()) {
            throw new IllegalArgumentException("Email cannot be null or empty");
        }
        return userRepository.findByEmail(email);
    }
    
    public List<User> findAll() {
        return userRepository.findAll();
    }
    
    public List<User> findAdults() {
        return userRepository.findByAgeGreaterThan(17);
    }
    
    public User updateUser(Long id, User userDetails) {
        Optional<User> optionalUser = userRepository.findById(id);
        if (!optionalUser.isPresent()) {
            throw new RuntimeException("User not found with id: " + id);
        }
        
        User user = optionalUser.get();
        user.setName(userDetails.getName());
        user.setEmail(userDetails.getEmail());
        user.setAge(userDetails.getAge());
        
        return userRepository.save(user);
    }
    
    public void deleteUser(Long id) {
        if (!userRepository.existsById(id)) {
            throw new RuntimeException("User not found with id: " + id);
        }
        userRepository.deleteById(id);
    }
    
    public List<User> searchByName(String name) {
        if (name == null) {
            throw new IllegalArgumentException("Name cannot be null");
        }
        return userRepository.findByNameContaining(name);
    }
}'''
    
    (demo_dir / "src" / "main" / "java" / "com" / "demo" / "service").mkdir(parents=True)
    with open(demo_dir / "src" / "main" / "java" / "com" / "demo" / "service" / "UserService.java", 'w') as f:
        f.write(user_service)
    
    # Create UserController
    user_controller = '''package com.demo.controller;

import com.demo.entity.User;
import com.demo.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody User user) {
        try {
            User createdUser = userService.createUser(user);
            return new ResponseEntity<>(createdUser, HttpStatus.CREATED);
        } catch (Exception e) {
            return new ResponseEntity<>(null, HttpStatus.BAD_REQUEST);
        }
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<User> getUserById(@PathVariable Long id) {
        Optional<User> user = userService.findById(id);
        return user.map(u -> ResponseEntity.ok(u))
                  .orElse(ResponseEntity.notFound().build());
    }
    
    @GetMapping
    public ResponseEntity<List<User>> getAllUsers() {
        List<User> users = userService.findAll();
        return ResponseEntity.ok(users);
    }
    
    @GetMapping("/adults")
    public ResponseEntity<List<User>> getAdults() {
        List<User> adults = userService.findAdults();
        return ResponseEntity.ok(adults);
    }
    
    @GetMapping("/search")
    public ResponseEntity<List<User>> searchUsers(@RequestParam String name) {
        try {
            List<User> users = userService.searchByName(name);
            return ResponseEntity.ok(users);
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }
    
    @PutMapping("/{id}")
    public ResponseEntity<User> updateUser(@PathVariable Long id, @RequestBody User userDetails) {
        try {
            User updatedUser = userService.updateUser(id, userDetails);
            return ResponseEntity.ok(updatedUser);
        } catch (Exception e) {
            return ResponseEntity.notFound().build();
        }
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        try {
            userService.deleteUser(id);
            return ResponseEntity.noContent().build();
        } catch (Exception e) {
            return ResponseEntity.notFound().build();
        }
    }
}'''
    
    (demo_dir / "src" / "main" / "java" / "com" / "demo" / "controller").mkdir(parents=True)
    with open(demo_dir / "src" / "main" / "java" / "com" / "demo" / "controller" / "UserController.java", 'w') as f:
        f.write(user_controller)
    
    # Create Main Application class
    main_app = '''package com.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class DemoApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}'''
    
    with open(demo_dir / "src" / "main" / "java" / "com" / "demo" / "DemoApplication.java", 'w') as f:
        f.write(main_app)
    
    # Create application.properties
    app_properties = '''# Demo Application Configuration
spring.application.name=Spring Boot Demo

# H2 Database Configuration
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driver-class-name=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=

# JPA Configuration
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.show-sql=true

# H2 Console (for development)
spring.h2.console.enabled=true'''
    
    with open(demo_dir / "src" / "main" / "resources" / "application.properties", 'w') as f:
        f.write(app_properties)
    
    print(f"✅ Demo project created at: {demo_dir.absolute()}")
    return demo_dir.absolute()

def run_demonstration():
    """Run the complete demonstration."""
    
    print("=" * 60)
    print("SPRING BOOT UNIT TEST GENERATOR DEMONSTRATION")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable is required")
        print("Please set it with: set GEMINI_API_KEY=your-api-key-here")
        return
    
    try:
        # Step 1: Create demo project
        print("\n🚀 Step 1: Creating Demo Spring Boot Project")
        print("-" * 40)
        demo_path = create_demo_project()
        
        # Step 2: Initialize generator
        print("\n🔧 Step 2: Initializing Test Generator")
        print("-" * 40)
        generator = UnitTestGenerator(
            local_path=str(demo_path),
            gemini_api_key=api_key
        )
        print("✅ Generator initialized successfully")
        
        # Step 3: Generate tests
        print("\n🧪 Step 3: Generating Unit Tests")
        print("-" * 40)
        print("This may take a few minutes...")
        
        results = generator.generate_tests(
            max_iterations=2,
            coverage_threshold=75.0
        )
        
        # Step 4: Display results
        print("\n📊 Step 4: Results Summary")
        print("-" * 40)
        
        if results.get("success"):
            print("✅ Test generation completed successfully!")
            
            # Display key metrics
            analysis = results['analysis_results']
            generation = results['test_generation']
            test_results = results['final_test_results']
            coverage = results['coverage_results']
            
            print(f"\n📋 Project Analysis:")
            print(f"   • Classes analyzed: {analysis['total_classes']}")
            print(f"   • Spring components: {analysis['spring_components']}")
            print(f"   • Test candidates: {analysis['test_candidates']}")
            
            print(f"\n🧪 Test Generation:")
            print(f"   • Test classes generated: {generation['test_classes_generated']}")
            print(f"   • Packages covered: {len(generation['organization']['packages'])}")
            
            print(f"\n🎯 Test Execution:")
            print(f"   • Total tests: {test_results['total_tests']}")
            print(f"   • Passed: {test_results['passed_tests']}")
            print(f"   • Failed: {test_results['failed_tests']}")
            print(f"   • Success rate: {test_results['success_rate']:.1f}%")
            
            print(f"\n📈 Coverage:")
            print(f"   • Line coverage: {coverage['line_coverage']:.1f}%")
            print(f"   • Branch coverage: {coverage['branch_coverage']:.1f}%")
            
            # Show generated files
            print(f"\n📁 Generated Files:")
            test_dir = demo_path / "src" / "test" / "java"
            if test_dir.exists():
                for test_file in test_dir.rglob("*.java"):
                    relative_path = test_file.relative_to(demo_path)
                    print(f"   • {relative_path}")
            
            print(f"\n🎉 Demo completed successfully!")
            print(f"📍 Project location: {demo_path}")
            print(f"📄 Detailed report: {demo_path}/TEST_GENERATION_REPORT.md")
            
            # Offer to run tests
            print(f"\n💡 You can now run the tests manually:")
            print(f"   cd {demo_path}")
            print(f"   mvn test")
            
        else:
            print(f"❌ Test generation failed: {results.get('error', 'Unknown error')}")
    
    except KeyboardInterrupt:
        print("\n⚠️ Demonstration interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main entry point."""
    
    print("Welcome to the Spring Boot Unit Test Generator Demonstration!")
    print("\nThis demo will:")
    print("1. Create a sample Spring Boot project with entities, services, and controllers")
    print("2. Analyze the code structure and identify test candidates")
    print("3. Generate comprehensive JUnit test cases using Gemini AI")
    print("4. Run the tests and provide coverage analysis")
    print("5. Show you the results and generated files")
    
    try:
        response = input("\nProceed with demonstration? (y/n): ")
        if response.lower().startswith('y'):
            run_demonstration()
        else:
            print("Demonstration cancelled.")
    except KeyboardInterrupt:
        print("\nGoodbye!")

if __name__ == "__main__":
    main()
