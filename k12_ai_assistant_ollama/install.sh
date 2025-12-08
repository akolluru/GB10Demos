#!/bin/bash

# Install script for K-12 AI Assistant (Ollama Version)
# This script creates a Python virtual environment and installs dependencies

set -e  # Exit on error

echo "🚀 Setting up K-12 AI Assistant (Ollama Version)..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Set virtual environment name with project name
VENV_NAME="venv_k12_ai_assistant"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_NAME" ]; then
    echo "📦 Creating virtual environment: $VENV_NAME..."
    python3 -m venv "$VENV_NAME"
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists: $VENV_NAME"
fi

echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source "$VENV_NAME/bin/activate"

echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

echo ""

# Install requirements
echo "📥 Installing dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

echo ""

# Check for Ollama and models
echo "🤖 Checking Ollama and models..."
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama is not installed or not in PATH"
    echo "   Please install Ollama from: https://ollama.ai/download"
    echo ""
else
    echo "✅ Ollama found: $(ollama --version 2>/dev/null || echo 'installed')"
    
    # Check if Ollama service is running
    if ! ollama list &> /dev/null; then
        echo "⚠️  Ollama service is not running"
        echo "   Please start Ollama with: ollama serve"
        echo ""
    else
        echo "✅ Ollama service is running"
        echo ""
        
        # Function to check if a model exists
        check_and_pull_model() {
            local model=$1
            local model_display=$2
            
            echo "🔍 Checking for model: $model_display"
            
            # Check if model exists (ollama list returns model names, check if exact match exists)
            if ollama list 2>/dev/null | awk '{print $1}' | grep -q "^${model}$"; then
                echo "✅ Model '$model' already exists, skipping..."
            else
                echo "📥 Model '$model' not found, pulling..."
                if ollama pull "$model"; then
                    echo "✅ Successfully pulled '$model'"
                else
                    echo "❌ Failed to pull '$model'"
                    return 1
                fi
            fi
            echo ""
        }
        
        # Check and pull required models
        check_and_pull_model "llama3:latest" "Llama3 latest"
        check_and_pull_model "gpt-oss:120b" "GPT-OSS 120B"
    fi
fi

echo "✨ Installation complete!"
echo ""
echo "📋 Next Steps:"
echo "  1. Run the application:"
echo "     ./run.sh"
echo ""
echo "Or manually activate the virtual environment and run:"
echo "  source $VENV_NAME/bin/activate"
echo "  streamlit run app/main.py"
echo ""

