# Quick Start Guide

## Installation on a New Machine

### Step 1: Copy the Folder
Copy the entire `k12_ai_assistant_ollama` folder to the new machine.

### Step 2: Install
Open a terminal in the folder and run:
```bash
./install.sh
```

This will:
- ✅ Create a Python virtual environment
- ✅ Install all dependencies
- ✅ Set up everything needed

### Step 3: Install Ollama
Make sure Ollama is installed:
- Visit https://ollama.ai/download
- Follow installation instructions for your OS
- Verify: `ollama --version`

### Step 4: Download a Model
```bash
ollama pull phi:latest
```

### Step 5: Start Ollama Server
In a separate terminal:
```bash
ollama serve
```

### Step 6: Run the App
```bash
./run.sh
```

The app will open in your browser automatically!

## That's It!

You're ready to use the K-12 AI Assistant. Just remember:
- Keep `ollama serve` running in one terminal
- Run `./run.sh` in another terminal or after closing the app

## Troubleshooting

**"Permission denied" on scripts:**
```bash
chmod +x install.sh run.sh
```

**"Python not found":**
- Install Python 3.8 or higher
- Make sure `python3` is in your PATH

**"Ollama connection error":**
- Make sure `ollama serve` is running
- Check if Ollama is installed correctly

**"Model not found":**
- Download the model: `ollama pull <model-name>`
- List available models: `ollama list`

