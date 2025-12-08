#!/bin/bash

# PA Permit Automation System - Run Script
# This script activates the virtual environment and runs the application

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

# Check if virtual environment exists
if [ ! -d "$VENV_NAME" ]; then
    echo -e "${RED}Error: Virtual environment not found!${NC}"
    echo -e "${YELLOW}Please run ./install.sh first${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source "$VENV_NAME/bin/activate"

# Check if activation was successful
if [ "$VIRTUAL_ENV" = "" ]; then
    echo -e "${RED}Error: Failed to activate virtual environment${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Run the application
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Starting PA Permit Automation System...${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if run.py exists, otherwise use streamlit directly
if [ -f "run.py" ]; then
    python run.py
else
    echo -e "${YELLOW}run.py not found, running streamlit directly...${NC}"
    streamlit run app.py --server.headless=false
fi

