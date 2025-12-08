#!/bin/bash

# AML Demo Run Script
# This script activates the virtual environment and runs the Streamlit application

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${NC}→ $1"
}

echo "========================================="
echo "AML Demo Run Script"
echo "========================================="
echo ""

# Check if virtual environment exists
VENV_DIR="venv-AML"
if [ ! -d "$VENV_DIR" ]; then
    print_error "Virtual environment not found!"
    print_info "Please run ./install.sh first to set up the environment."
    exit 1
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source "$VENV_DIR/bin/activate"
print_success "Virtual environment activated"

# Check if required Python packages are installed
print_info "Checking Python dependencies..."
if ! python3 -c "import streamlit" 2>/dev/null; then
    print_error "Streamlit is not installed!"
    print_info "Please run ./install.sh to install dependencies."
    exit 1
fi

# Check FAISS installation
if ! python3 -c "import faiss" 2>/dev/null; then
    print_warning "FAISS is not installed!"
    print_info "The app will work but vector search will be disabled."
    print_info "To install FAISS, run: pip install faiss-cpu>=1.13.0"
else
    print_success "FAISS is installed"
fi

print_success "Python dependencies are installed"

# Check if Ollama is installed
print_info "Checking if Ollama is installed..."
if ! command -v ollama &> /dev/null; then
    print_error "Ollama is not installed or not in PATH."
    print_info "Please install Ollama from https://ollama.ai"
    exit 1
fi
print_success "Ollama is installed"

# Check if Ollama service is running
print_info "Checking if Ollama service is running..."
if ! ollama list &> /dev/null; then
    print_warning "Ollama service is not running!"
    print_info "Attempting to check if Ollama can be reached..."
    
    # Try to start Ollama in the background (if possible)
    if command -v systemctl &> /dev/null && systemctl is-active --quiet ollama 2>/dev/null; then
        print_info "Ollama service is installed but not running. Starting it..."
        sudo systemctl start ollama 2>/dev/null || print_warning "Could not start Ollama service automatically"
    else
        print_warning "Please start Ollama manually:"
        print_info "  - Run 'ollama serve' in a separate terminal, OR"
        print_info "  - Start the Ollama service: sudo systemctl start ollama"
        print_info ""
        read -p "Press Enter to continue anyway (the app may not work without Ollama) or Ctrl+C to exit..."
    fi
else
    print_success "Ollama service is running"
fi

# Check for required models (optional check, won't fail if models are missing)
print_info "Checking for required Ollama models..."
MISSING_MODELS=()

# Try to list models, but don't fail if Ollama isn't running
OLLAMA_MODELS=$(ollama list 2>/dev/null || echo "")

if [ -n "$OLLAMA_MODELS" ]; then
    if echo "$OLLAMA_MODELS" | grep -q "mistral:latest"; then
        print_success "Model mistral:latest is available"
    else
        MISSING_MODELS+=("mistral:latest")
    fi
    
    if echo "$OLLAMA_MODELS" | grep -q "deepseek-r1:14b"; then
        print_success "Model deepseek-r1:14b is available"
    else
        MISSING_MODELS+=("deepseek-r1:14b")
    fi
    
    if [ ${#MISSING_MODELS[@]} -gt 0 ]; then
        print_warning "Some required models are missing: ${MISSING_MODELS[*]}"
        print_info "You can pull them with: ollama pull <model_name>"
        print_info "Or run ./install.sh again to ensure all models are available."
        print_info ""
        read -p "Press Enter to continue anyway or Ctrl+C to exit..."
    else
        print_success "Required Ollama models are available"
    fi
else
    print_warning "Could not check for models (Ollama may not be running)"
    print_info "Required models: mistral:latest, deepseek-r1:14b"
    print_info "Make sure Ollama is running and models are pulled before using the app."
fi

# Check if app.py exists
if [ ! -f "app.py" ]; then
    print_error "app.py not found!"
    exit 1
fi

# Run the Streamlit application
echo ""
echo "========================================="
print_success "Starting AML Demo Application..."
echo "========================================="
echo ""
print_info "The application will open in your default browser."
print_info "If it doesn't open automatically, navigate to the URL shown below."
print_info ""
print_info "Press Ctrl+C to stop the application."
echo ""

streamlit run app.py

