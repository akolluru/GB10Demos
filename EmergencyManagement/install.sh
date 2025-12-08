#!/bin/bash

# Emergency Management System Installation Script
# This script sets up the virtual environment, installs dependencies, and downloads required models

set -e  # Exit on any error

echo "========================================="
echo "Emergency Management System Installation"
echo "========================================="
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python 3.8 or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi
echo "Python version: $PYTHON_VERSION - OK"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "Virtual environment created successfully!"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "Virtual environment activated!"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
echo ""

# Install requirements
echo "Installing Python dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    # Check if requirements.txt has encoding issues (UTF-16, BOM, or Windows paths)
    NEEDS_CLEANUP=false
    if file requirements.txt | grep -q "UTF-16"; then
        NEEDS_CLEANUP=true
    fi
    if grep -q "@ file://" requirements.txt 2>/dev/null; then
        NEEDS_CLEANUP=true
    fi
    # Check for BOM (UTF-8 BOM is EF BB BF)
    if head -c 3 requirements.txt | od -An -tx1 | grep -q "ef bb bf"; then
        NEEDS_CLEANUP=true
    fi
    
    if [ "$NEEDS_CLEANUP" = true ]; then
        echo "Detected encoding issues in requirements.txt. Cleaning it up..."
        python3 << 'CLEANUP_EOF'
import codecs
import sys

# Try to read with different encodings
content = None
for encoding in ['utf-8-sig', 'utf-8', 'utf-16-le', 'utf-16-be', 'latin-1']:
    try:
        with codecs.open('requirements.txt', 'r', encoding=encoding) as f:
            content = f.read()
        break
    except:
        continue

if content is None:
    print("Error: Could not read requirements.txt")
    sys.exit(1)

# Remove BOM if present (from anywhere in the content)
content = content.replace('\ufeff', '')

# Clean up Windows-specific packages and file:// references
windows_packages = {'comtypes', 'pypiwin32', 'pywin32', 'pywinpty', 'win_inet_pton'}
cleaned_lines = []
seen_packages = set()
has_faiss_cpu = False

# First pass: collect all packages
for line in content.split('\n'):
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    
    # Extract package name
    parts = line.split('@')[0].split('==')[0].split('>=')[0].split('<=')[0].strip()
    package_name = parts.split()[0] if parts else ''
    
    # Skip Windows-specific packages
    if package_name.lower() in windows_packages:
        continue
    
    # Check for faiss-cpu
    if package_name.lower() == 'faiss-cpu':
        has_faiss_cpu = True
    
    # Skip duplicates
    if package_name.lower() in seen_packages:
        continue
    
    # Remove file:// references
    if '@ file://' in line:
        cleaned_line = package_name
    else:
        cleaned_line = line.split('@')[0].strip()
    
    if cleaned_line:
        cleaned_lines.append(cleaned_line)
        seen_packages.add(package_name.lower())

# Second pass: if faiss-cpu exists, remove faiss (GPU version) to avoid conflicts
if has_faiss_cpu:
    cleaned_lines = [line for line in cleaned_lines if not (line == 'faiss' or (line.startswith('faiss==') and 'faiss-cpu' not in line))]

# Write cleaned requirements (without BOM)
with open('requirements.txt', 'w', encoding='utf-8') as f:
    for line in sorted(cleaned_lines):
        f.write(line + '\n')

print(f"Cleaned requirements.txt: {len(cleaned_lines)} packages")
CLEANUP_EOF
        echo "Requirements.txt cleaned successfully!"
    else
        # Still check and remove BOM if present (from anywhere in the file)
        python3 << 'BOM_EOF'
import codecs
try:
    # Read file and remove all BOM characters
    with open('requirements.txt', 'rb') as f:
        content_bytes = f.read()
    
    # Remove BOM sequence from anywhere
    content_bytes = content_bytes.replace(b'\xef\xbb\xbf', b'')
    
    # Also check text content
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        text_content = f.read()
        text_cleaned = text_content.replace('\ufeff', '')
    
    # Write back without BOM
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(text_cleaned)
except Exception as e:
    print(f"Warning: Could not clean BOM: {e}")
BOM_EOF
    fi
    
    # Try to install requirements
    if pip install -r requirements.txt; then
        echo "Dependencies installed successfully!"
    else
        echo "Warning: Some packages failed to install with exact versions."
        echo "Attempting to install with flexible version constraints..."
        # Create a temporary requirements file with flexible versions for problematic packages
        python3 << 'FLEXIBLE_EOF'
import re

# Known packages that may have version compatibility issues
problematic_packages = {
    'vtk': '>=9.5.0',  # vtk 9.3.1 not available for Python 3.12+
    'click': '>=8.1.8,<8.2',  # typer 0.15.4 requires click<8.2, but other packages need >=8.1.8
}

# Packages to remove if they conflict (not used in codebase)
conflicting_packages = {
    'pyvista': '0.44.2',  # Conflicts with vtk>=9.5.0, not used in codebase
}

with open('requirements.txt', 'r') as f:
    lines = f.readlines()

flexible_lines = []
for line in lines:
    line = line.strip()
    if not line:
        continue
    
    # Check if this is a conflicting package (remove it)
    package_match = re.match(r'^([a-zA-Z0-9_-]+)(==|>=|<=|>|<|~=)(.+)$', line)
    if package_match:
        pkg_name = package_match.group(1)
        # Remove conflicting packages
        if pkg_name in conflicting_packages and conflicting_packages[pkg_name] in line:
            continue  # Skip this package
        # Handle problematic packages with version updates
        if pkg_name in problematic_packages:
            flexible_lines.append(f"{pkg_name}{problematic_packages[pkg_name]}")
            continue
    
    flexible_lines.append(line)

# Write flexible requirements
with open('requirements_flexible.txt', 'w') as f:
    f.write('\n'.join(flexible_lines))

print("Created requirements_flexible.txt with compatible versions")
FLEXIBLE_EOF
        
        # Try installing with flexible versions
        if [ -f "requirements_flexible.txt" ]; then
            echo "Installing with flexible version constraints..."
            pip install -r requirements_flexible.txt || echo "Some packages may still need manual installation"
            rm -f requirements_flexible.txt
        fi
    fi
    
    # Try to install PyAudio if it failed (requires system libraries)
    if ! python -c "import pyaudio" 2>/dev/null; then
        echo ""
        echo "Note: PyAudio installation may have failed (requires system libraries)."
        echo "PyAudio is optional and not used in the core application."
        echo "To install it later, run:"
        echo "  sudo apt-get install portaudio19-dev"
        echo "  pip install PyAudio"
        echo ""
    fi
    
    # Check for CUDA and install PyTorch with CUDA support if available
    echo "Checking for CUDA support..."
    if command -v nvidia-smi &> /dev/null; then
        CUDA_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1)
        if [ -n "$CUDA_VERSION" ]; then
            echo "NVIDIA GPU detected. Checking PyTorch CUDA support..."
            if ! python -c "import torch; assert torch.cuda.is_available()" 2>/dev/null; then
                echo "PyTorch installed without CUDA support. Installing PyTorch with CUDA..."
                pip uninstall -y torch torchvision torchaudio 2>/dev/null
                # Try CUDA 13.0 first, fall back to CUDA 12.1 if not available
                if pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu130 2>/dev/null; then
                    echo "✓ PyTorch with CUDA 13.0 installed successfully"
                elif pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121 2>/dev/null; then
                    echo "✓ PyTorch with CUDA 12.1 installed successfully"
                else
                    echo "Warning: Could not install PyTorch with CUDA. Falling back to CPU version."
                    pip install torch torchvision torchaudio
                fi
                
                # Verify CUDA is now available
                if python -c "import torch; print('CUDA available:', torch.cuda.is_available())" 2>/dev/null | grep -q "True"; then
                    echo "✓ CUDA is now available in PyTorch"
                fi
            else
                echo "✓ PyTorch already has CUDA support"
            fi
        fi
    else
        echo "No NVIDIA GPU detected. PyTorch will use CPU."
    fi
    echo ""
else
    echo "Warning: requirements.txt not found. Installing basic dependencies..."
    pip install streamlit torch torchvision ultralytics ollama opencv-python pillow requests
fi
echo ""

# Check if Ollama is installed
echo "Checking for Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "Ollama is already installed."
    OLLAMA_VERSION=$(ollama --version 2>&1 || echo "unknown")
    echo "Ollama version: $OLLAMA_VERSION"
else
    echo "Ollama is not installed. Installing Ollama..."
    echo "Please visit https://ollama.ai/download to install Ollama for your system."
    echo "Or run the following command:"
    echo "  curl -fsSL https://ollama.ai/install.sh | sh"
    echo ""
    read -p "Press Enter after installing Ollama, or Ctrl+C to exit..."
fi
echo ""

# Start Ollama service (if not running)
echo "Checking if Ollama service is running..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Ollama service is already running."
else
    echo "Starting Ollama service in the background..."
    # Try to start Ollama (this may fail if Ollama is not in PATH or needs different setup)
    ollama serve > /dev/null 2>&1 &
    OLLAMA_PID=$!
    sleep 3
    
    # Check if it started successfully
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "Ollama service started successfully (PID: $OLLAMA_PID)"
    else
        echo "Warning: Could not start Ollama service automatically."
        echo "Please start Ollama manually by running: ollama serve"
        echo "Then run this script again or continue with model downloads."
        read -p "Press Enter to continue or Ctrl+C to exit..."
    fi
fi
echo ""

# Download required Ollama models
echo "Downloading required Ollama models..."
echo "This may take a while depending on your internet connection..."
echo ""

MODELS=("llava:latest" "phi:latest" "mixtral:latest")

for model in "${MODELS[@]}"; do
    echo "Pulling model: $model"
    if ollama pull "$model"; then
        echo "Successfully pulled $model"
    else
        echo "Error: Failed to pull $model"
        echo "Please check your internet connection and try again."
        exit 1
    fi
    echo ""
done

# Verify models are available
echo "Verifying models are available..."
for model in "${MODELS[@]}"; do
    if ollama list | grep -q "$model"; then
        echo "✓ $model is available"
    else
        echo "✗ $model is NOT available"
    fi
done
echo ""

# Note about YOLOv8
echo "Note: YOLOv8 model (yolov8x.pt) will be automatically downloaded"
echo "      on first use by the ultralytics library."
echo ""

# Create a .env file if it doesn't exist (for future use)
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    # Detect CUDA availability
    CUDA_AVAILABLE="false"
    if python -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
        CUDA_AVAILABLE="true"
    fi
    cat > .env << EOF
# Emergency Management System Configuration
OLLAMA_BASE_URL=http://localhost:11434
CUDA_AVAILABLE=$CUDA_AVAILABLE
EOF
    echo ".env file created with CUDA_AVAILABLE=$CUDA_AVAILABLE"
fi
echo ""

# Summary
echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""
echo "Summary:"
echo "  ✓ Virtual environment created and activated"
echo "  ✓ Python dependencies installed"
echo "  ✓ Ollama models downloaded:"
for model in "${MODELS[@]}"; do
    echo "    - $model"
done
echo ""
echo "Next steps:"
echo "  1. Make sure Ollama service is running: ollama serve"
echo "  2. Run the demo using: ./run.sh"
echo "  3. Or manually: source venv/bin/activate && streamlit run app_streamlit.py"
echo ""
echo "To activate the virtual environment manually:"
echo "  source venv/bin/activate"
echo ""

