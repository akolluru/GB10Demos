import streamlit as st
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path
app_path = Path(__file__).parent
sys.path.append(str(app_path))

# Import components
from components.sidebar import render_sidebar
from components.homework_helper import render_homework_helper
from components.writing_assistant import render_writing_assistant
from components.research_assistant import render_research_assistant
from components.learning_games import render_learning_games
from components.teacher_tools import render_teacher_tools
from utils.ollama_utils import get_ai_response, get_available_models

# Load custom CSS
def load_css():
    css_file = app_path / "static" / "style.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def check_ollama_status():
    """Check if Ollama is running and models are available."""
    try:
        models = get_available_models()
        if models:
            return True, models
        else:
            return False, "No models found"
    except Exception as e:
        return False, str(e)

# Set page configuration
st.set_page_config(
    page_title="K-12 AI Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add CSS for tab styling, radio buttons, and dropdowns
st.markdown(
    """
    <style>
    /* Tab text - White for all */
    button[data-baseweb="tab"] > div,
    button[data-baseweb="tab"] span,
    button[data-baseweb="tab"] p {
        color: white !important;
    }
    
    /* Active tab underline - Blue */
    button[data-baseweb="tab"][aria-selected="true"],
    div[data-testid="stTabs"] button[aria-selected="true"] {
        border-bottom: 3px solid #1f77b4 !important;
        border-bottom-color: #1f77b4 !important;
        border-top: none !important;
        border-left: none !important;
        border-right: none !important;
    }
    
    /* Radio buttons - Blue color - Maximum override */
    input[type="radio"],
    [data-baseweb="radio"] input {
        accent-color: #1f77b4 !important;
        -webkit-appearance: none !important;
        -moz-appearance: none !important;
        appearance: none !important;
        border-color: #1f77b4 !important;
    }
    
    /* Radio button BaseWeb component - All elements */
    [data-baseweb="radio"],
    [data-baseweb="radio"] * {
        color: #1f77b4 !important;
        border-color: #1f77b4 !important;
    }
    
    /* Radio button circle/dot container */
    [data-baseweb="radio"] > div,
    [data-baseweb="radio"] > span {
        background-color: transparent !important;
        border-color: #1f77b4 !important;
        color: #1f77b4 !important;
    }
    
    /* Radio button selected state - Multiple selectors */
    [data-baseweb="radio"] input[type="radio"]:checked + span,
    [data-baseweb="radio"] input[type="radio"]:checked + div,
    [data-baseweb="radio"] input[type="radio"]:checked,
    input[type="radio"]:checked,
    [data-baseweb="radio"][aria-checked="true"] {
        background-color: #1f77b4 !important;
        border-color: #1f77b4 !important;
    }
    
    /* Radio button inner dot - All pseudo-elements */
    [data-baseweb="radio"] input[type="radio"]:checked::before,
    input[type="radio"]:checked::before,
    [data-baseweb="radio"] input[type="radio"]:checked::after,
    input[type="radio"]:checked::after {
        background-color: #1f77b4 !important;
        border-color: #1f77b4 !important;
    }
    
    /* Radio button SVG/icons - Blue - All shapes */
    [data-baseweb="radio"] svg,
    [data-baseweb="radio"] path,
    [data-baseweb="radio"] circle,
    [data-baseweb="radio"] rect {
        fill: #1f77b4 !important;
        color: #1f77b4 !important;
        stroke: #1f77b4 !important;
    }
    
    /* Override inline styles */
    [data-baseweb="radio"][style*="color"],
    [data-baseweb="radio"][style*="fill"],
    [data-baseweb="radio"][style*="stroke"],
    [data-baseweb="radio"] *[style*="color"],
    [data-baseweb="radio"] *[style*="fill"],
    [data-baseweb="radio"] *[style*="stroke"] {
        color: #1f77b4 !important;
        fill: #1f77b4 !important;
        stroke: #1f77b4 !important;
    }
    
    /* Dropdown/Selectbox - Dark theme with Blue border */
    [data-baseweb="select"] {
        border: 2px solid #1f77b4 !important;
        border-radius: 4px !important;
        background-color: #262730 !important;
        color: #fafafa !important;
    }
    
    [data-baseweb="select"]:focus,
    [data-baseweb="select"]:focus-within,
    [data-baseweb="select"]:hover {
        border-color: #1f77b4 !important;
        box-shadow: 0 0 0 3px rgba(31, 119, 180, 0.2) !important;
        outline: none !important;
        background-color: #262730 !important;
    }
    
    /* Dropdown arrow/icon - Blue */
    [data-baseweb="select"] svg,
    [data-baseweb="select"] path {
        fill: #1f77b4 !important;
        color: #1f77b4 !important;
    }
    
    /* Selected value in dropdown - Blue */
    [data-baseweb="select"] > div > div,
    [data-baseweb="select"] span,
    [data-baseweb="select"] p {
        color: #1f77b4 !important;
    }
    
    /* Dropdown popover/menu - Dark theme with Blue border */
    [data-baseweb="popover"],
    [data-baseweb="menu"] {
        border: 1px solid #1f77b4 !important;
        border-radius: 4px !important;
        background-color: #262730 !important;
    }
    
    [data-baseweb="popover"] *,
    [data-baseweb="menu"] * {
        background-color: #262730 !important;
        color: #fafafa !important;
    }
    
    /* Dropdown options hover - Blue highlight on dark */
    [data-baseweb="popover"] [role="option"]:hover,
    [data-baseweb="menu"] [role="option"]:hover,
    [data-baseweb="popover"] li:hover,
    [data-baseweb="menu"] li:hover {
        background-color: rgba(31, 119, 180, 0.3) !important;
        color: #1f77b4 !important;
    }
    
    /* Selected dropdown option - Blue background on dark */
    [data-baseweb="popover"] [role="option"][aria-selected="true"],
    [data-baseweb="menu"] [role="option"][aria-selected="true"],
    [data-baseweb="popover"] li[aria-selected="true"],
    [data-baseweb="menu"] li[aria-selected="true"],
    [data-baseweb="option"][aria-selected="true"],
    [data-baseweb="option"][data-highlighted="true"] {
        background-color: rgba(31, 119, 180, 0.4) !important;
        color: #1f77b4 !important;
    }
    </style>
    <script>
    // Force radio buttons to be blue - runs after page load
    function forceBlueRadios() {
        // Find all radio button SVG elements and force blue color
        const radios = document.querySelectorAll('[data-baseweb="radio"]');
        radios.forEach(radio => {
            // Force blue on all SVG elements
            const svgs = radio.querySelectorAll('svg');
            svgs.forEach(svg => {
                svg.style.color = '#1f77b4';
                svg.style.fill = '#1f77b4';
                svg.style.stroke = '#1f77b4';
                // Force blue on all paths and circles inside
                const paths = svg.querySelectorAll('path, circle, rect');
                paths.forEach(path => {
                    path.style.fill = '#1f77b4';
                    path.style.stroke = '#1f77b4';
                    path.setAttribute('fill', '#1f77b4');
                    path.setAttribute('stroke', '#1f77b4');
                });
            });
            // Force blue on checked radios
            const inputs = radio.querySelectorAll('input[type="radio"]');
            inputs.forEach(input => {
                input.style.accentColor = '#1f77b4';
                if (input.checked) {
                    radio.style.color = '#1f77b4';
                    radio.style.borderColor = '#1f77b4';
                }
            });
        });
    }
    
    // Run immediately and also on DOM changes
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', forceBlueRadios);
    } else {
        forceBlueRadios();
    }
    
    // Use MutationObserver to catch dynamically added radios
    const observer = new MutationObserver(forceBlueRadios);
    observer.observe(document.body, { childList: true, subtree: true });
    
    // Also run periodically to catch any missed updates
    setInterval(forceBlueRadios, 500);
    </script>
    """,
    unsafe_allow_html=True
)

# Load custom CSS
load_css()

# App title and description with custom styling
st.markdown('<div class="main-header"><h1>K-12 AI Assistant</h1></div>', unsafe_allow_html=True)

# Check Ollama status
ollama_status, status_message = check_ollama_status()

if not ollama_status:
    st.error(f"⚠️ Cannot connect to Ollama: {status_message}")
    st.info("""
    Please make sure Ollama is running on your computer. 
    
    To start Ollama:
    1. Open a command prompt or terminal
    2. Type `ollama serve` and press Enter
    3. Wait for Ollama to start
    4. Refresh this page
    """)
else:
    # Initialize session state for storing the current tool
    if "current_tool" not in st.session_state:
        st.session_state.current_tool = "Homework Helper"

    # Initialize session state for storing the selected model
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "llama3:latest"  # Default model

    # Render sidebar with tool selection
    render_sidebar()

    # Render the selected tool based on session state
    if st.session_state.current_tool == "Homework Helper":
        render_homework_helper()
    elif st.session_state.current_tool == "Writing Assistant":
        render_writing_assistant()
    elif st.session_state.current_tool == "Research Assistant":
        render_research_assistant()
    elif st.session_state.current_tool == "Learning Games":
        render_learning_games()
    elif st.session_state.current_tool == "Teacher Tools":
        render_teacher_tools()

    # Footer with custom styling
    st.markdown('<div class="footer">Powered by Ollama and Streamlit | K-12 AI Assistant</div>', unsafe_allow_html=True)
    
    # Help section
    with st.expander("Help & Tips"):
        st.markdown("""
        ### Tips for Using K-12 AI Assistant
        
        - **Select the appropriate grade level** to ensure content is age-appropriate
        - **Choose a specific topic** for more focused and relevant content
        - **Try different AI models** to see which works best for your needs
        - **Download generated content** to save and use offline
        - **Customize the content** by adjusting difficulty levels and content types
        
        ### Troubleshooting
        
        - If you encounter errors, make sure Ollama is running on your computer
        - For best performance, use the recommended models for your hardware
        - Large content generation may take longer, especially with larger models
        """)
