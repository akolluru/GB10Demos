# Comprehensive AML Screening Demo Application

This is a comprehensive Anti-Money Laundering (AML) screening application with full agentic AI capabilities, including Agent-to-Agent (A2A) communication, Pydantic structured outputs, Model Context Protocol (MCP), and FAISS vector search.

## Features

### Agentic AI Features
- **A2A Communication**: Agent-to-Agent message passing framework
- **Pydantic + A2A Orchestration**: Role-based AI agents (L1, L2, RAG specialists) with structured outputs
- **MCP Integration**: Model Context Protocol for external document retrieval
- **FAISS Vector Search**: Semantic similarity search for knowledge retrieval

### Core AML Features
- **Level 1 Screening**: Basic transaction monitoring and risk scoring with Pydantic agents
- **Level 2 Screening**: Enhanced due diligence with detailed analysis
- **RAG-Enhanced Analysis**: Context-aware analysis with MCP and vector search
- **Watchlist Screening**: Sanctions, PEP, and Adverse Media screening
- **Alert Management**: Complete alert workflow system
- **Case Management**: Investigation case tracking
- **Pattern Detection**: Advanced ML pattern recognition (structuring, layering, etc.)
- **SAR Generation**: Suspicious Activity Report creation
- **Customer Risk Profiling**: KYC/CDD with automated risk scoring
- **Configurable Rules Engine**: Custom AML rules with auto-execution
- **Graph Analysis**: Network visualization of transaction relationships
- **Interactive Dashboard**: Real-time monitoring with dark theme UI

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running locally
- Graphviz (for architecture diagrams)
- FAISS (automatically installed via requirements.txt)
- NVIDIA GPU (recommended for better performance)

## Installation

### Automated Installation (Recommended)

1. Clone this repository
2. Run the installation script:
```bash
chmod +x install.sh
./install.sh
```

The script will:
- Create a virtual environment (`venv-AML`)
- Install all Python dependencies (including FAISS)
- Check and install Graphviz
- Verify Ollama installation
- Pull required Ollama models (mistral:latest, deepseek-r1:14b)
- Verify FAISS installation

### Manual Installation

1. Create virtual environment:
```bash
python3 -m venv venv-AML
source venv-AML/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Graphviz (system package):
```bash
# Ubuntu/Debian
sudo apt-get install graphviz

# RHEL/CentOS
sudo yum install graphviz

# macOS
brew install graphviz
```

4. Install and configure Ollama:
- Download from https://ollama.ai
- Pull required models:
```bash
ollama pull mistral:latest
ollama pull deepseek-r1:14b
```

5. Verify FAISS installation:
```bash
python3 -c "import faiss; print('FAISS version:', faiss.__version__)"
```

## Running the Application

### Using the Run Script (Recommended)

```bash
chmod +x run.sh
./run.sh
```

The script will:
- Activate the virtual environment
- Check for required dependencies
- Verify Ollama is running
- Check for required models
- Start the Streamlit application

### Manual Run

1. Activate virtual environment:
```bash
source venv-AML/bin/activate
```

2. Start the application:
```bash
streamlit run app.py
```

3. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

## Usage

1. **Dashboard Tab**: View transactions, run L1/L2 screening, RAG analysis, and graph visualization
2. **Agentic AI Tab**: Monitor agent status, run collaborative screening with all agents
3. **Watchlist Screening**: Screen transactions against sanctions, PEP, and adverse media lists
4. **Alerts**: Manage alerts generated from screening and pattern detection
5. **Cases**: Create and manage investigation cases
6. **Pattern Detection**: Detect money laundering patterns (structuring, layering, etc.)
7. **SAR Generation**: Create and export Suspicious Activity Reports
8. **Customer Risk**: View customer risk profiles and KYC/CDD information
9. **Rules Engine**: Create and manage custom AML rules
10. **Architecture**: View system architecture diagrams and documentation

## Project Structure

### Core Application Files
- `app.py`: Main Streamlit application with comprehensive AML features
- `data_generator.py`: Transaction data simulation
- `screening.py`: Basic AML screening logic
- `graph_analysis.py`: Network graph analysis and visualization

### Agentic AI Components
- `agent_framework.py`: A2A communication framework
- `pydantic_agents.py`: Pydantic-based agent orchestration with A2A
- `mcp_client.py`: Model Context Protocol client
- `rag_agent.py`: RAG agent with FAISS vector search

### AML Feature Modules
- `watchlist_screening.py`: Watchlist screening (Sanctions, PEP, Adverse Media)
- `alert_management.py`: Alert management system
- `case_management.py`: Case management and investigation tracking
- `pattern_detection.py`: Pattern detection engine
- `sar_generation.py`: SAR generation module
- `customer_risk_profiling.py`: Customer risk profiling (KYC/CDD)
- `rules_engine.py`: Configurable rules engine

### Data & Configuration
- `rag_data/`: Knowledge base JSON files (regulations, typologies, countries)
- `watchlist_data/`: Watchlist data files
- `requirements.txt`: Python dependencies (including FAISS)
- `install.sh`: Automated installation script
- `run.sh`: Application launcher script

## Dependencies

Key dependencies include:
- **Streamlit**: Web framework
- **FAISS**: Vector similarity search (version 1.10.0)
- **Pydantic**: Structured output validation
- **A2A Framework**: Agent-to-Agent communication
- **Ollama**: Local LLM inference
- **NetworkX**: Graph analysis
- **Plotly**: Interactive visualizations
- **Graphviz**: Architecture diagrams

See `requirements.txt` for complete list.

## Troubleshooting

### FAISS Installation Issues
If FAISS fails to install:
```bash
pip install --upgrade faiss-cpu==1.10.0
python3 -c "import faiss; print('FAISS installed')"
```

### Ollama Connection Issues
Ensure Ollama is running:
```bash
ollama serve
# Or
sudo systemctl start ollama
```

### Graphviz Not Found
Install system package:
```bash
sudo apt-get install graphviz  # Ubuntu/Debian
sudo yum install graphviz      # RHEL/CentOS
brew install graphviz          # macOS
``` 