"""
Application Launcher for PA Permit Automation System
Provides easy startup with pre-flight checks
"""
import sys
import os
import subprocess


def check_python_version():
    """Verify Python version is 3.11 or higher"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Error: Python 3.11 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def check_ollama():
    """Check if Ollama is running and model is available"""
    try:
        import ollama
        # Try to list models
        models = ollama.list()
        print("✅ Ollama is connected")
        
        # Check for mixtral model
        has_mixtral = False
        try:
            if isinstance(models, dict) and 'models' in models:
                model_list = models['models']
                for model in model_list:
                    if isinstance(model, dict):
                        # Try different key names
                        name = model.get('name', '') or model.get('model', '') or str(model)
                    else:
                        name = str(model)
                    
                    if 'mixtral' in name.lower():
                        has_mixtral = True
                        print(f"✅ Mixtral model found: {name}")
                        break
            
            if not has_mixtral:
                print("⚠️  Warning: Mixtral model not detected")
                print("   Run: ollama pull mixtral:latest")
                print("   Or use another model by creating .env file with OLLAMA_MODEL=mistral:latest")
        except Exception as parse_error:
            print(f"⚠️  Could not parse model list: {parse_error}")
            print("   This is OK - the app will still work if a model is available")
        
        return True
    except Exception as e:
        print(f"⚠️  Ollama check warning: {str(e)}")
        print("   Make sure Ollama is running, then start it and run: ollama pull mixtral:latest")
        return True  # Non-critical, allow to continue


def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        ('streamlit', 'streamlit'),
        ('crewai', 'crewai'),
        ('ollama', 'ollama'),
        ('graphviz', 'graphviz'),
        ('python-dotenv', 'dotenv')  # pip name vs import name
    ]
    
    missing = []
    for pip_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {pip_name} installed")
        except ImportError:
            missing.append(pip_name)
            print(f"❌ {pip_name} not installed")
    
    if missing:
        print("\n⚠️  Missing packages. Install with:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True


def check_graphviz():
    """Check if system Graphviz is installed"""
    try:
        result = subprocess.run(
            ['dot', '-V'], 
            capture_output=True, 
            text=True,
            timeout=5
        )
        print(f"✅ Graphviz installed: {result.stderr.strip()}")
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  Warning: System Graphviz not found")
        print("   Install with: conda install -c conda-forge graphviz")
        print("   (Application may work without it, but diagrams won't render)")
        return True  # Non-critical, allow to continue


def check_env_file():
    """Check if .env file exists"""
    if os.path.exists('.env'):
        print("✅ .env file found")
        return True
    else:
        print("⚠️  .env file not found (using defaults)")
        print("   You can create .env file for custom configuration")
        return True  # Non-critical


def print_banner():
    """Print application banner"""
    print("=" * 70)
    print("🏛️  PA PERMIT AUTOMATION SYSTEM")
    print("   Commonwealth of Pennsylvania - AI-Powered Permit Processing")
    print("=" * 70)
    print()


def print_instructions():
    """Print post-launch instructions"""
    print("\n" + "=" * 70)
    print("🚀 STARTING APPLICATION...")
    print("=" * 70)
    print("\n📋 Once the application starts:")
    print("   1. Your browser will open automatically")
    print("   2. Navigate to the 'Submit Application' tab")
    print("   3. Fill in the permit application form")
    print("   4. Click 'Submit Application' to process")
    print("   5. View results and agent workflow")
    print("\n💡 Tips:")
    print("   - Check 'System Architecture' tab for visual diagram")
    print("   - View 'Application Status' for all processed permits")
    print("   - Press Ctrl+C in this terminal to stop the server")
    print("\n" + "=" * 70)
    print()


def main():
    """Main launcher function"""
    print_banner()
    
    print("🔍 Running pre-flight checks...\n")
    
    # Run all checks
    checks_passed = True
    
    if not check_python_version():
        checks_passed = False
    
    if not check_dependencies():
        checks_passed = False
    
    check_ollama()  # Warning only
    check_graphviz()  # Warning only
    check_env_file()  # Warning only
    
    if not checks_passed:
        print("\n❌ Pre-flight checks failed. Please fix errors above.")
        sys.exit(1)
    
    print("\n✅ All critical checks passed!")
    
    print_instructions()
    
    # Launch Streamlit
    try:
        subprocess.run([
            sys.executable,
            '-m',
            'streamlit',
            'run',
            'app.py',
            '--server.headless=false'
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped. Thank you for using PA Permit Automation!")
    except Exception as e:
        print(f"\n❌ Error launching application: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

