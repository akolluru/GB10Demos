# Multi-Agent Field Assistant for Disaster Response

This project implements a local, offline-capable multi-agent system for disaster response scenarios. The system consists of three specialized AI agents that work together to analyze terrain, plan responses, and communicate findings.

## Architecture

### Agents
1. **Scout Agent**: Processes visual input using  YOLO + LLava
2. **Planner Agent**: Analyzes terrain and constraints using Gemma
3. **Communicator Agent**: Generates reports using Mistral 

### Requirements
- Python 3.8+
- Ollama (for local model inference)
- CUDA-capable GPU (optional, for faster inference)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure Ollama is running with required models:
```bash
ollama pull mistral
ollama pull llava
ollama pull gemma
Download YOO weights
```

3. Run the demo:
```bash
python app.py
```

## Usage

1. Launch the Streamlit interface
2. Upload an image of the disaster area
3. The system will process the image and generate a response plan
4. View the results 

## Project Structure

```
├── agents/
│   ├── scout_agent.py
│   ├── planner_agent.py
│   └── communicator_agent.py
├── utils/
│   ├── vision_utils.py
│   └── text_utils.py
├── app.py
├── requirements.txt
└── README.md
``` 
