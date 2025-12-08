#!/bin/bash

# Run script for K-12 AI Assistant (Ollama Version)
# This script activates the virtual environment and runs the Streamlit app

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Set virtual environment name with project name
VENV_NAME="venv_k12_ai_assistant"

# Check if virtual environment exists
if [ ! -d "$VENV_NAME" ]; then
    echo "❌ Virtual environment not found: $VENV_NAME"
    echo "Please run ./install.sh first to set up the environment."
    exit 1
fi

# Activate virtual environment
echo " Activating virtual environment: $VENV_NAME..."
source "$VENV_NAME/bin/activate"

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit is not installed!"
    echo "Please run ./install.sh to install dependencies."
    exit 1
fi

echo ""
echo " Starting K-12 AI Assistant with Ollama backend..."
echo ""
echo "⚠️  IMPORTANT: Make sure Ollama is running on your computer"
echo "   If not, start it in another terminal with: ollama serve"
echo ""

# Ensure we're using Ollama backend (unset any other backend variables)
unset USE_VLLM
unset USE_TENSORRT
unset VLLM_SERVER_URL
unset TENSORRT_SERVER_URL

echo "✅ Using Ollama backend"
echo ""

# Change to the app directory
cd "$SCRIPT_DIR/app"

# Run the Streamlit app
streamlit run main.py

