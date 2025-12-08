#!/bin/bash

# PA Permit Automation System - Installation Script
# This script sets up the virtual environment and installs all dependencies

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project name
PROJECT_NAME="PA-Permit"
VENV_NAME="${PROJECT_NAME}-venv"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}PA Permit Automation System${NC}"
echo -e "${BLUE}Installation Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    echo -e "${RED}Error: Python 3.11 or higher is required${NC}"
    echo -e "${RED}Current version: $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python version: $PYTHON_VERSION${NC}"
echo ""

# Remove existing virtual environment if it exists
if [ -d "$VENV_NAME" ]; then
    echo -e "${YELLOW}Removing existing virtual environment...${NC}"
    rm -rf "$VENV_NAME"
    echo -e "${GREEN}✓ Removed existing virtual environment${NC}"
    echo ""
fi

# Create new virtual environment
echo -e "${YELLOW}Creating virtual environment: $VENV_NAME...${NC}"
python3 -m venv "$VENV_NAME"
echo -e "${GREEN}✓ Virtual environment created${NC}"
echo ""

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$VENV_NAME/bin/activate"
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip --quiet
echo -e "${GREEN}✓ pip upgraded${NC}"
echo ""

# Install dependencies
echo -e "${YELLOW}Installing dependencies from requirements.txt...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}Error: requirements.txt not found${NC}"
    exit 1
fi
echo ""

# Check if Ollama is installed
echo -e "${YELLOW}Checking Ollama installation...${NC}"
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama is installed${NC}"
    OLLAMA_VERSION=$(ollama --version 2>&1 || echo "unknown")
    echo -e "${BLUE}  Version: $OLLAMA_VERSION${NC}"
    
    # Check if Ollama service is running
    if ollama list &> /dev/null; then
        echo -e "${GREEN}✓ Ollama service is running${NC}"
    else
        echo -e "${YELLOW}⚠ Warning: Ollama service is not running${NC}"
        echo -e "${YELLOW}  Please start Ollama service: ollama serve${NC}"
    fi
    echo ""
    
    # Pull required Ollama models
    echo -e "${YELLOW}Checking and pulling required Ollama models...${NC}"
    
    # Get list of available models
    AVAILABLE_MODELS=$(ollama list 2>/dev/null || echo "")
    
    # Check for mistral:latest (default from config.py)
    if echo "$AVAILABLE_MODELS" | grep -q "mistral:latest" 2>/dev/null; then
        echo -e "${GREEN}✓ mistral:latest is already available${NC}"
    else
        echo -e "${YELLOW}Pulling mistral:latest...${NC}"
        if ollama pull mistral:latest 2>/dev/null; then
            echo -e "${GREEN}✓ mistral:latest pulled successfully${NC}"
        else
            echo -e "${YELLOW}⚠ Failed to pull mistral:latest (Ollama service may not be running)${NC}"
            echo -e "${YELLOW}  You can pull it later with: ollama pull mistral:latest${NC}"
        fi
    fi
    
    # Also check for mixtral:latest (mentioned in run.py)
    if echo "$AVAILABLE_MODELS" | grep -q "mixtral:latest" 2>/dev/null; then
        echo -e "${GREEN}✓ mixtral:latest is already available${NC}"
    else
        echo -e "${YELLOW}Pulling mixtral:latest (optional, for better performance)...${NC}"
        if ollama pull mixtral:latest 2>/dev/null; then
            echo -e "${GREEN}✓ mixtral:latest pulled successfully${NC}"
        else
            echo -e "${YELLOW}⚠ Failed to pull mixtral:latest (optional model)${NC}"
            echo -e "${YELLOW}  You can pull it later with: ollama pull mixtral:latest${NC}"
        fi
    fi
    echo ""
else
    echo -e "${YELLOW}⚠ Warning: Ollama is not installed${NC}"
    echo -e "${YELLOW}  Please install Ollama from: https://ollama.ai${NC}"
    echo -e "${YELLOW}  After installation, run: ollama pull mistral:latest${NC}"
    echo ""
fi

# Check for system Graphviz (optional but recommended)
echo -e "${YELLOW}Checking for system Graphviz (optional)...${NC}"
if command -v dot &> /dev/null; then
    echo -e "${GREEN}✓ Graphviz is installed${NC}"
else
    echo -e "${YELLOW}⚠ Warning: System Graphviz not found${NC}"
    echo -e "${YELLOW}  Install with: sudo apt-get install graphviz (Ubuntu/Debian)${NC}"
    echo -e "${YELLOW}  Or: brew install graphviz (macOS)${NC}"
    echo -e "${YELLOW}  (Application will work without it, but diagrams won't render)${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Virtual environment: $VENV_NAME${NC}"
echo -e "${GREEN}Location: $SCRIPT_DIR/$VENV_NAME${NC}"
echo ""
echo -e "${YELLOW}To activate the virtual environment manually:${NC}"
echo -e "${BLUE}  source $VENV_NAME/bin/activate${NC}"
echo ""
echo -e "${YELLOW}To run the application:${NC}"
echo -e "${BLUE}  ./run.sh${NC}"
echo -e "${BLUE}  or${NC}"
echo -e "${BLUE}  source $VENV_NAME/bin/activate && python run.py${NC}"
echo ""

