#!/bin/bash

# AML Demo Installation Script
# This script sets up the environment, installs dependencies, and ensures Ollama models are available

set -e  # Exit on error

echo "========================================="
echo "AML Demo Installation Script"
echo "========================================="
echo ""

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

# Check Python version
print_info "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

print_success "Python $PYTHON_VERSION found"

# Check if venv module is available
print_info "Checking for venv module..."
if ! python3 -m venv --help &> /dev/null; then
    print_error "venv module is not available. Please install python3-venv."
    exit 1
fi

# Create virtual environment
VENV_DIR="venv-AML"
if [ -d "$VENV_DIR" ]; then
    print_warning "Virtual environment already exists. Removing old one..."
    rm -rf "$VENV_DIR"
fi

print_info "Creating virtual environment..."
python3 -m venv "$VENV_DIR"
print_success "Virtual environment created"

# Activate virtual environment
print_info "Activating virtual environment..."
source "$VENV_DIR/bin/activate"
print_success "Virtual environment activated"

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip --quiet
print_success "pip upgraded"

# Install system dependencies (Graphviz)
print_info "Checking for Graphviz system package..."
if command -v dot &> /dev/null; then
    print_success "Graphviz is already installed"
else
    print_warning "Graphviz not found. Attempting to install..."
    if command -v apt-get &> /dev/null; then
        print_info "Installing Graphviz using apt-get..."
        sudo apt-get update -qq && sudo apt-get install -y graphviz
        print_success "Graphviz installed via apt-get"
    elif command -v yum &> /dev/null; then
        print_info "Installing Graphviz using yum..."
        sudo yum install -y graphviz
        print_success "Graphviz installed via yum"
    elif command -v dnf &> /dev/null; then
        print_info "Installing Graphviz using dnf..."
        sudo dnf install -y graphviz
        print_success "Graphviz installed via dnf"
    elif command -v brew &> /dev/null; then
        print_info "Installing Graphviz using Homebrew..."
        brew install graphviz
        print_success "Graphviz installed via Homebrew"
    else
        print_warning "Could not automatically install Graphviz."
        print_info "Please install Graphviz manually:"
        print_info "  - Debian/Ubuntu: sudo apt-get install graphviz"
        print_info "  - RHEL/CentOS: sudo yum install graphviz"
        print_info "  - Fedora: sudo dnf install graphviz"
        print_info "  - macOS: brew install graphviz"
        print_warning "Continuing without Graphviz (architecture diagrams may not work)..."
    fi
fi

# Install Python dependencies
print_info "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Python dependencies installed"
    
    # Verify FAISS installation
    print_info "Verifying FAISS installation..."
    if python3 -c "import faiss; print('FAISS version:', faiss.__version__)" 2>/dev/null; then
        print_success "FAISS is installed and working"
    else
        print_warning "FAISS installation verification failed"
        print_info "Attempting to reinstall FAISS..."
        pip install --upgrade faiss-cpu>=1.13.0
        if python3 -c "import faiss" 2>/dev/null; then
            print_success "FAISS reinstalled successfully"
        else
            print_warning "FAISS installation failed. The app will use text-based search instead."
            print_info "You can manually install FAISS later with: pip install faiss-cpu"
        fi
    fi
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Check if Ollama is installed
print_info "Checking if Ollama is installed..."
if ! command -v ollama &> /dev/null; then
    print_warning "Ollama is not installed or not in PATH."
    print_info "Please install Ollama from https://ollama.ai"
    print_info "After installing Ollama, run this script again to pull the required models."
    exit 1
fi

print_success "Ollama is installed"

# Check if Ollama service is running
print_info "Checking if Ollama service is running..."
if ! ollama list &> /dev/null; then
    print_warning "Ollama service is not running. Attempting to start..."
    print_info "Please make sure Ollama is running. You may need to start it manually."
    print_info "On Linux: systemctl start ollama (or run 'ollama serve' in a separate terminal)"
    print_warning "Continuing with model checks anyway..."
fi

# Function to check and pull Ollama model
check_and_pull_model() {
    local model=$1
    print_info "Checking for Ollama model: $model"
    
    if ollama list 2>/dev/null | grep -q "^$model"; then
        print_success "Model $model is already available"
    else
        print_warning "Model $model not found. Pulling..."
        if ollama pull "$model"; then
            print_success "Model $model pulled successfully"
        else
            print_error "Failed to pull model $model"
            return 1
        fi
    fi
}

# Check and pull required models
print_info "Checking required Ollama models..."
MODELS=("mistral:latest" "deepseek-r1:14b")

for model in "${MODELS[@]}"; do
    if ! check_and_pull_model "$model"; then
        print_warning "Failed to ensure model $model is available"
        print_info "You can manually pull it later with: ollama pull $model"
    fi
done

# Verify RAG data directory exists
print_info "Checking RAG data directory..."
if [ -d "rag_data" ]; then
    print_success "RAG data directory found"
    if [ -f "rag_data/aml_regulations.json" ] && [ -f "rag_data/aml_typologies.json" ] && [ -f "rag_data/high_risk_countries.json" ]; then
        print_success "RAG data files found"
    else
        print_warning "Some RAG data files may be missing"
    fi
else
    print_warning "RAG data directory not found. The app may not work correctly."
fi

# Verify lib directory exists (for frontend assets)
print_info "Checking frontend assets..."
if [ -d "lib" ]; then
    print_success "Frontend assets directory found"
else
    print_warning "lib directory not found. Some visualizations may not work."
fi

echo ""
echo "========================================="
print_success "Installation completed successfully!"
echo "========================================="
echo ""
print_info "To run the application, use:"
echo "  ./run.sh"
echo ""
print_info "Or manually:echo "  source venv-AML/bin/activate"
echo "  streamlit run app.py"
echo ""

