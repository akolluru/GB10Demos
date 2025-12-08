# K-12 AI Assistant (Ollama Version)

A self-contained, easy-to-install version of the K-12 AI Assistant that uses Ollama for local AI inference.

## Quick Start

### 1. Install Dependencies

```bash
./install.sh
```

This will:
- Create a Python virtual environment (`venv_k12_ai_assistant`)
- Install all required Python packages
- Set up the application

### 2. Install Ollama

Make sure Ollama is installed on your system:

- **Linux/Mac**: Visit https://ollama.ai/download and follow the instructions
- **Windows**: Download the installer from https://ollama.ai/download

After installing, verify it works:
```bash
ollama --version
```

### 3. Download a Model

Download at least one AI model (this may take a few minutes):

```bash
# Small, fast model (recommended for testing)
ollama pull phi:latest

# Or try a larger, more capable model
ollama pull llama3:latest

# Or the full Llama 3 8B model
ollama pull llama3:8b
```

### 4. Start Ollama Server

In a separate terminal, start the Ollama server:

```bash
ollama serve
```

Keep this terminal open while using the application.

### 5. Run the Application

```bash
./run.sh
```

The application will open in your web browser automatically.

## What's Included

This folder contains everything you need to run the K-12 AI Assistant:

- `app/` - The Streamlit application code
- `requirements.txt` - Python dependencies
- `install.sh` - Installation script (creates venv and installs packages)
- `run.sh` - Run script (activates venv and starts the app)
- `README.md` - This file

## Features

- **Homework Helper** - Get help with homework questions
- **Writing Assistant** - Improve writing with AI feedback
- **Research Assistant** - Explore topics and create study guides
- **Learning Games** - Interactive educational games
- **Teacher Tools** - Lesson plans, rubrics, and more

## Requirements

- Python 3.8 or higher
- Ollama installed and running
- At least one Ollama model downloaded
- Internet connection (for initial Ollama/model downloads)

## Supported Models

The application works with any Ollama model, but recommended models include:

- `phi:latest` - Small and fast (1.6GB)
- `llama3:latest` - Balanced performance (4.7GB)
- `llama3:8b` - Better quality (4.7GB)
- `mixtral:8x7b` - High quality (47B parameters)
- `gemma:7b` - Good performance (7B parameters)

## Troubleshooting

### "Virtual environment not found"
Run `./install.sh` first to create the virtual environment.

### "Streamlit is not installed"
Run `./install.sh` to install dependencies.

### "Could not connect to Ollama"
Make sure Ollama is running in a separate terminal:
```bash
ollama serve
```

### "Model not found"
Download the model first:
```bash
ollama pull <model-name>
```

### Port already in use
If port 8501 is already in use, Streamlit will automatically use the next available port. Check the terminal output for the correct URL.

## Manual Installation

If you prefer to set up manually:

```bash
# Create virtual environment
python3 -m venv venv_k12_ai_assistant

# Activate virtual environment
source venv_k12_ai_assistant/bin/activate  # Linux/Mac
# or
venv_k12_ai_assistant\Scripts\activate  # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run the app
cd app
streamlit run main.py
```

## Notes

- The virtual environment is created in the project folder (`venv_k12_ai_assistant/`)
- All dependencies are isolated to this virtual environment
- The application uses Ollama locally - no data is sent to external servers
- Models are stored in `~/.ollama/models/` (can be large, several GB each)

## Support

For issues or questions:
1. Check that Ollama is running: `ollama list`
2. Verify models are downloaded: `ollama list`
3. Check Python version: `python3 --version`
4. Review the terminal output for error messages

## License

This is a self-contained educational tool. Make sure you have proper licenses for any Ollama models you use.

