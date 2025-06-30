"""
Simple example showing how to use the Spring Boot Unit Test Generator.
Run this script to see basic usage without needing an API key for demonstration.
"""

def show_usage_examples():
    """Show usage examples for the Spring Boot Unit Test Generator."""
    
    print("=" * 60)
    print("SPRING BOOT UNIT TEST GENERATOR - USAGE GUIDE")
    print("=" * 60)
    
    print("\n🚀 QUICK START:")
    print("-" * 30)
    print("1. Set your API key:")
    print("   $env:GEMINI_API_KEY='your-gemini-api-key-here'")
    print("")
    print("2. Run for GitHub repository:")
    print("   py main.py --repo-url https://github.com/spring-projects/spring-petclinic")
    print("")
    print("3. Run for local project:")
    print("   py main.py --local-path 'C:\\path\\to\\your\\spring-boot-project'")
    
    print("\n🛠️ COMMAND LINE OPTIONS:")
    print("-" * 30)
    print("--repo-url URL          GitHub repository URL")
    print("--local-path PATH       Local Spring Boot project path") 
    print("--api-key KEY           Gemini AI API key (optional if set in env)")
    print("--max-iterations N      Maximum improvement iterations (default: 3)")
    print("--coverage-threshold N  Target coverage percentage (default: 80)")
    print("--help                  Show help message")
    
    print("\n📝 EXAMPLES:")
    print("-" * 30)
    print("# Basic usage with GitHub repo")
    print("py main.py --repo-url https://github.com/spring-projects/spring-petclinic")
    print("")
    print("# Local project with custom settings")
    print("py main.py --local-path 'C:\\MyProject' --max-iterations 5 --coverage-threshold 85")
    print("")
    print("# With explicit API key")
    print("py main.py --repo-url https://github.com/user/repo --api-key 'your-key-here'")
    
    print("\n🧪 WHAT THE SYSTEM DOES:")
    print("-" * 30)
    print("1. 📊 Analyzes your Spring Boot codebase")
    print("2. 🤖 Uses AI to generate comprehensive JUnit tests")
    print("3. 🏃 Runs the tests and measures coverage")
    print("4. 🔄 Iteratively improves test quality")
    print("5. 📋 Provides detailed reports")
    
    print("\n📁 OUTPUT:")
    print("-" * 30)
    print("- Generated test files in src/test/java/")
    print("- JUnit test suite configuration") 
    print("- Coverage reports (JaCoCo)")
    print("- Detailed generation report (TEST_GENERATION_REPORT.md)")
    
    print("\n⚙️ REQUIREMENTS:")
    print("-" * 30)
    print("✅ Python 3.8+")
    print("✅ Google Gemini AI API key")
    print("⚠️  Maven or Gradle (for running tests)")
    print("⚠️  Git (for cloning repositories)")
    print("✅ Dependencies installed (py -m pip install -r requirements.txt)")
    
    print("\n🆘 GETTING HELP:")
    print("-" * 30)
    print("- Check installation: py test_installation.py")
    print("- View help: py main.py --help")
    print("- Read documentation: USER_GUIDE.md")
    
    print("\n🔑 GET GEMINI API KEY:")
    print("-" * 30)
    print("1. Visit: https://makersuite.google.com/app/apikey")
    print("2. Create/login to Google account")
    print("3. Generate new API key")
    print("4. Set environment variable:")
    print("   $env:GEMINI_API_KEY='your-api-key-here'")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    show_usage_examples()
    
    print("\nReady to proceed? Here's what you need to do:")
    print("1. Get your Gemini AI API key from Google AI Studio")
    print("2. Set it: $env:GEMINI_API_KEY='your-key'")
    print("3. Run: py main.py --repo-url https://github.com/your-repo")
    print("\nFor testing, you can also run: py demo.py (after setting API key)")
