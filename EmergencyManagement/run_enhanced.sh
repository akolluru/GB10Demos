#!/bin/bash

# Emergency Management System Run Script (Enhanced UI)
# This script activates the virtual environment and runs the enhanced Streamlit demo

set -e  # Exit on any error

echo "========================================="
echo "Emergency Management System - Enhanced UI"
echo "========================================="
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run ./install.sh first to set up the environment."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "Virtual environment activated!"
echo ""

# Check if Ollama service is running
echo "Checking Ollama service..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✓ Ollama service is running"
else
    echo "✗ Ollama service is NOT running"
    echo ""
    echo "Please start Ollama service in another terminal:"
    echo "  ollama serve"
    echo ""
    echo "Or run it in the background:"
    echo "  ollama serve &"
    echo ""
    read -p "Press Enter after starting Ollama, or Ctrl+C to exit..."
    
    # Check again
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "Error: Ollama service is still not running. Exiting."
        exit 1
    fi
fi
echo ""

# Verify required models are available
echo "Verifying required models..."
REQUIRED_MODELS=("llava:latest" "phi:latest" "mixtral:latest")
MISSING_MODELS=()

for model in "${REQUIRED_MODELS[@]}"; do
    if ollama list | grep -q "$model"; then
        echo "✓ $model is available"
    else
        echo "✗ $model is NOT available"
        MISSING_MODELS+=("$model")
    fi
done

if [ ${#MISSING_MODELS[@]} -gt 0 ]; then
    echo ""
    echo "Error: Some required models are missing!"
    echo "Please run ./install.sh to download the required models."
    echo "Or manually pull them using:"
    for model in "${MISSING_MODELS[@]}"; do
        echo "  ollama pull $model"
    done
    exit 1
fi
echo ""

# Check if Streamlit is installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "Error: Streamlit is not installed!"
    echo "Please run ./install.sh to install dependencies."
    exit 1
fi

# Display system information
echo "System Information:"
echo "  Python: $(python --version)"
if python -c "import torch; print('  PyTorch:', torch.__version__)" 2>/dev/null; then
    python -c "import torch; print('  PyTorch:', torch.__version__)"
    if python -c "import torch; print('  CUDA Available:', torch.cuda.is_available())" 2>/dev/null; then
        python -c "import torch; print('  CUDA Available:', torch.cuda.is_available())"
        if python -c "import torch; torch.cuda.is_available() and print('  CUDA Device:', torch.cuda.get_device_name(0))" 2>/dev/null; then
            python -c "import torch; torch.cuda.is_available() and print('  CUDA Device:', torch.cuda.get_device_name(0))"
        fi
    fi
fi
echo ""

# Run the enhanced Streamlit app
echo "========================================="
echo "Starting Enhanced Streamlit application..."
echo "========================================="
echo ""
echo "The application will open in your default web browser."
echo "If it doesn't open automatically, navigate to the URL shown below."
echo ""
echo "Press Ctrl+C to stop the application."
echo ""

streamlit run app_streamlit_enhanced.py

