import streamlit as st
import os
import tempfile
from agents.scout_agent import ScoutAgent
from agents.planner_agent import PlannerAgent
from agents.communicator_agent import CommunicatorAgent
import logging
import torch
import gc
import graphviz
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Suppress PyTorch torch.classes warning (harmless internal warning)
import warnings
warnings.filterwarnings('ignore', message='.*torch.classes.*')
# Also filter the specific PyTorch warning
logging.getLogger('torch').setLevel(logging.ERROR)

# Configure Streamlit page
st.set_page_config(
    page_title="Emergency Response Analysis",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS styling with black background
st.markdown("""
    <style>
        [data-testid="collapsedControl"] {
            display: none
        }
        #MainMenu {
            visibility: hidden;
        }
        footer {
            visibility: hidden;
        }
        .stApp {
            background-color: #000000;
        }
        .main .block-container {
            background-color: #000000;
            padding-top: 2rem;
        }
        .agent-header {
            background: #1a1a1a;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px rgba(255, 255, 255, 0.1);
            border: 1px solid #333;
        }
        .scout-header {
            border-left: 5px solid #f5576c;
        }
        .planner-header {
            border-left: 5px solid #4facfe;
        }
        .communicator-header {
            border-left: 5px solid #43e97b;
        }
        .info-card {
            background: #1a1a1a;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(255, 255, 255, 0.1);
            border: 1px solid #333;
            color: #e0e0e0;
        }
        .detection-item {
            background: #1a1a1a;
            padding: 0.75rem;
            border-radius: 6px;
            margin: 0.5rem 0;
            border-left: 3px solid #667eea;
            color: #e0e0e0;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff;
        }
        p, div, span, label {
            color: #e0e0e0;
        }
        .stMarkdown {
            color: #e0e0e0;
        }
        .stTabs [data-baseweb="tab-list"] {
            background-color: #1a1a1a;
        }
        .stTabs [data-baseweb="tab"] {
            color: #e0e0e0;
        }
        .stTabs [aria-selected="true"] {
            color: #ffffff;
            background-color: #2a2a2a;
        }
        .stExpander {
            background-color: #1a1a1a;
            border: 1px solid #333;
        }
        .stMetric {
            background-color: #1a1a1a;
            border: 1px solid #333;
            padding: 1rem;
            border-radius: 8px;
        }
        .stProgress > div > div {
            background-color: #333;
        }
        .stAlert {
            background-color: #1a1a1a;
            border: 1px solid #333;
        }
        .stInfo {
            background-color: #1a3a5a;
            border-left: 4px solid #4facfe;
        }
        .stSuccess {
            background-color: #1a3a2a;
            border-left: 4px solid #43e97b;
        }
        .stError {
            background-color: #3a1a1a;
            border-left: 4px solid #f5576c;
        }
        .stWarning {
            background-color: #3a3a1a;
            border-left: 4px solid #ffd700;
        }
        .stFileUploader {
            background-color: #1a1a1a;
            border: 1px solid #333;
        }
        .stButton > button {
            background-color: #2a2a2a;
            color: #ffffff;
            border: 1px solid #444;
        }
        .stButton > button:hover {
            background-color: #3a3a3a;
            border-color: #555;
        }
        .stDownloadButton > button {
            background-color: #2a2a2a;
            color: #ffffff;
            border: 1px solid #444;
        }
        .stExpander label {
            color: #ffffff;
        }
        .stMetric label {
            color: #b0b0b0;
        }
        .stMetric [data-testid="stMetricValue"] {
            color: #ffffff;
        }
        .stMetric [data-testid="stMetricDelta"] {
            color: #b0b0b0;
        }
    </style>
""", unsafe_allow_html=True)

def show_architecture_tab():
    st.header("System Architecture")
    st.markdown("""
    **Multi-Agent Emergency Response System**
    """)
    
    # Create Graphviz diagram
    st.subheader(" System Flow Diagram")
    
    # Create a simple, clean Graphviz diagram
    dot = graphviz.Digraph(comment='Emergency Response System Architecture')
    
    # Simple horizontal layout with default sizing
    dot.attr(rankdir='LR', bgcolor='#000000')
    dot.attr('node', shape='box', style='rounded,filled', fontname='Arial', fontsize='12')
    dot.attr('edge', fontsize='10', fontcolor='#ffffff')
    
    # Nodes with distinct colors: Agents (Blue) vs LLMs (Orange/Amber)
    # Input/Output: Dark Blue
    dot.node('input', 'Disaster Scene\nImage', fillcolor='#1E3A8A', fontcolor='white')
    dot.node('output', 'Emergency\nResponse Report', fillcolor='#1E3A8A', fontcolor='white')
    
    # Agents: Blue shades
    dot.node('scout', 'Scout Agent', fillcolor='#2563EB', fontcolor='white')
    dot.node('planner', 'Planner Agent', fillcolor='#3B82F6', fontcolor='white')
    dot.node('communicator', 'Communicator Agent', fillcolor='#60A5FA', fontcolor='white')
    
    # LLMs: Orange/Amber shades
    dot.node('yolo', 'YOLOv8', fillcolor='#F59E0B', fontcolor='white')
    dot.node('llava', 'LLaVA', fillcolor='#F97316', fontcolor='white')
    dot.node('phi', 'Phi', fillcolor='#FBBF24', fontcolor='white')
    dot.node('mixtral', 'Mixtral', fillcolor='#FCD34D', fontcolor='black')
    
    # Main flow - using agent colors for main flow, LLM colors for model connections
    dot.edge('input', 'scout', color='#2563EB')
    dot.edge('scout', 'yolo', color='#F59E0B', style='dashed')
    dot.edge('yolo', 'llava', color='#F97316', style='dashed')
    dot.edge('llava', 'planner', color='#3B82F6')
    dot.edge('planner', 'phi', color='#FBBF24', style='dashed')
    dot.edge('phi', 'communicator', color='#60A5FA')
    dot.edge('communicator', 'mixtral', color='#FCD34D', style='dashed')
    dot.edge('mixtral', 'output', color='#1E3A8A')
    
    # Display the graph
    st.graphviz_chart(dot.source)
    
    st.markdown("---")
    
    # Three columns for agent details
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader(" Scout Edge Agent")
        st.markdown("""
        - **Role:** Real-time scene analysis, hazard detection, resource assessment
        - **Models:** YOLOv8 (object detection), LLaVA (vision-language analysis)
        
        **About YOLOv8:**
        - YOLOv8 is a state-of-the-art, real-time object detection model by Ultralytics.
        - It detects and localizes objects (people, vehicles, buildings, debris, etc.) in the uploaded scene image.
        - Provides bounding boxes and confidence scores for each detected object.
        - Enables fast hazard identification and resource assessment.
        
        **About LLaVA:**
        - LLaVA (Large Language and Vision Assistant) is a vision-language model that combines image and text understanding.
        - Analyzes the scene contextually, generating detailed descriptions and assessments based on both visual and textual cues.
        - Enables deeper scene understanding and language-based analysis for emergency response.
        
        **Workflow:**
        1. Image is uploaded.
        2. YOLOv8 detects and classifies objects in the scene.
        3. Results are visualized (bounding boxes) and passed to LLaVA for deeper scene understanding and language-based analysis.
        """)
    with col2:
        st.subheader(" Planner Edge Agent")
        st.markdown("""
        - **Role:** Response strategy development, resource allocation, team deployment planning
        - **Model:** Phi (LLM for planning)
        
        **About Phi:**
        - Phi is a large language model optimized for planning and decision support.
        - It generates detailed, actionable response plans based on scene analysis and detected hazards.
        - Considers resource allocation, team assignments, and safety protocols.
        
        **Workflow:**
        1. Receives scene analysis and detected objects from Scout Agent.
        2. Generates a prioritized, step-by-step emergency response plan.
        3. Outputs specific actions, resource needs, and team assignments.
        """)
    with col3:
        st.subheader(" Communicator Edge Agent")
        st.markdown("""
        - **Role:** Report generation, emergency communication, action coordination
        - **Model:** Mixtral (LLM for reporting)
        
        **About Mixtral:**
        - Mixtral is a large language model specialized in summarization and communication.
        - Synthesizes analysis and plans into clear, actionable reports for responders and stakeholders.
        - Ensures all critical information is communicated effectively and concisely.
        
        **Workflow:**
        1. Receives the response plan and scene analysis from Planner Agent.
        2. Generates a comprehensive, structured emergency response report.
        3. Facilitates communication and coordination among teams.
        """)

def format_text_with_sections(text):
    """Format text into expandable sections based on numbered lists or headers"""
    lines = text.split('\n')
    formatted_sections = []
    current_section = []
    section_title = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line is a section header (starts with number or is a header)
        if (line and len(line) > 0 and 
            (line[0].isdigit() and ('.' in line[:5] or ':' in line[:10]) or
             line.startswith('#') or
             (line.isupper() and len(line) < 50))):
            if current_section:
                formatted_sections.append((section_title, '\n'.join(current_section)))
            section_title = line
            current_section = []
        else:
            current_section.append(line)
    
    if current_section:
        formatted_sections.append((section_title, '\n'.join(current_section)))
    
    return formatted_sections if formatted_sections else [("Full Analysis", text)]

def display_scout_results(scout_results):
    """Display Scout Agent results in a nice format"""
    with st.container():
        st.markdown('<div class="agent-header scout-header">', unsafe_allow_html=True)
        st.markdown("###  Scout Agent - Scene Analysis")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Terrain Analysis in expandable sections
        if scout_results.get("analysis"):
            with st.expander(" Detailed Terrain Analysis", expanded=True):
                sections = format_text_with_sections(scout_results["analysis"])
                for title, content in sections:
                    if title and title != "Full Analysis":
                        st.markdown(f"**{title}**")
                    st.markdown(content)
                    st.markdown("---")
        
        # Detected Objects in a nice card format
        terrain_data = scout_results.get("terrain_data", {}).get("terrain_analysis", {})
        if terrain_data:
            st.markdown("###  Detected Objects")
            
            # Count objects by category
            total_objects = sum(len(items) for items in terrain_data.values() if items)
            if total_objects > 0:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Objects", total_objects)
                with col2:
                    st.metric("People", len(terrain_data.get("people", [])))
                with col3:
                    st.metric("Vehicles", len(terrain_data.get("vehicles", [])))
                with col4:
                    st.metric("Structures", len(terrain_data.get("structures", [])))
            
            # Show detailed detections
            for category, items in terrain_data.items():
                if items:
                    with st.expander(f" {category.title()} ({len(items)} found)", expanded=False):
                        for item in items:
                            confidence = item.get('confidence', 0)
                            area = item.get('area_m2', 0)
                            
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**{item['class']}**")
                            with col2:
                                st.progress(confidence, text=f"{confidence:.0%}")
                            
                            if area > 0:
                                st.caption(f"📍 Area: {area:.2f} m²")

def display_planner_results(plan_results):
    """Display Planner Agent results in a nice format"""
    with st.container():
        st.markdown('<div class="agent-header planner-header">', unsafe_allow_html=True)
        st.markdown("###  Planner Agent - Response Plan")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if plan_results and plan_results.get("plan"):
            plan_text = plan_results["plan"]
            
            # Format plan into sections
            sections = format_text_with_sections(plan_text)
            
            for title, content in sections:
                if title and title != "Full Analysis":
                    with st.expander(f" {title}", expanded=True):
                        # Highlight key information
                        lines = content.split('\n')
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            
                            # Format bullet points nicely
                            if line.startswith('-') or line.startswith('•'):
                                st.markdown(f"  {line}")
                            elif line[0].isdigit() and ('.' in line[:3] or ')' in line[:3]):
                                st.markdown(f"**{line}**")
                            else:
                                st.markdown(line)
                else:
                    # If no clear sections, show in a nice container
                    st.markdown('<div class="info-card">', unsafe_allow_html=True)
                    st.markdown(content)
                    st.markdown('</div>', unsafe_allow_html=True)

def display_communicator_results(report_results):
    """Display Communicator Agent results in a nice format"""
    with st.container():
        st.markdown('<div class="agent-header communicator-header">', unsafe_allow_html=True)
        st.markdown("###  Communicator Agent - Final Report")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if report_results and report_results.get("report"):
            report_text = report_results["report"]
            
            # Format report into sections
            sections = format_text_with_sections(report_text)
            
            # Show summary at top
            st.info("**Executive Summary** - This comprehensive report synthesizes all analysis and planning information for emergency responders.")
            
            for title, content in sections:
                if title and title != "Full Analysis":
                    with st.expander(f"📋 {title}", expanded=False):
                        st.markdown('<div class="info-card">', unsafe_allow_html=True)
                        st.markdown(content)
                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="info-card">', unsafe_allow_html=True)
                    st.markdown(content)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Add download button for report
            st.download_button(
                label=" Download Report",
                data=report_text,
                file_name=f"emergency_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

def show_architecture_diagram_tab():
    """Display a clean, simple architecture diagram in a new tab."""
    st.header("System Architecture Diagram")
    st.markdown("""
    **Multi-Agent Emergency Response System Flow**
    """)
    
    # Create a simple, clean Graphviz diagram
    dot = graphviz.Digraph(comment='Emergency Response System Architecture')
    
    # Simple horizontal layout with default sizing
    dot.attr(rankdir='LR', bgcolor='#000000')
    dot.attr('node', shape='box', style='rounded,filled', fontname='Arial', fontsize='12')
    dot.attr('edge', fontsize='10', fontcolor='#ffffff')
    
    # Nodes with distinct colors: Agents (Blue) vs LLMs (Orange/Amber)
    # Input/Output: Dark Blue
    dot.node('input', 'Disaster Scene\nImage', fillcolor='#1E3A8A', fontcolor='white')
    dot.node('output', 'Emergency\nResponse Report', fillcolor='#1E3A8A', fontcolor='white')
    
    # Agents: Blue shades
    dot.node('scout', 'Scout Agent', fillcolor='#2563EB', fontcolor='white')
    dot.node('planner', 'Planner Agent', fillcolor='#3B82F6', fontcolor='white')
    dot.node('communicator', 'Communicator Agent', fillcolor='#60A5FA', fontcolor='white')
    
    # LLMs: Orange/Amber shades
    dot.node('yolo', 'YOLOv8', fillcolor='#F59E0B', fontcolor='white')
    dot.node('llava', 'LLaVA', fillcolor='#F97316', fontcolor='white')
    dot.node('phi', 'Phi', fillcolor='#FBBF24', fontcolor='white')
    dot.node('mixtral', 'Mixtral', fillcolor='#FCD34D', fontcolor='black')
    
    # Main flow - using agent colors for main flow, LLM colors for model connections
    dot.edge('input', 'scout', color='#2563EB')
    dot.edge('scout', 'yolo', color='#F59E0B', style='dashed')
    dot.edge('yolo', 'llava', color='#F97316', style='dashed')
    dot.edge('llava', 'planner', color='#3B82F6')
    dot.edge('planner', 'phi', color='#FBBF24', style='dashed')
    dot.edge('phi', 'communicator', color='#60A5FA')
    dot.edge('communicator', 'mixtral', color='#FCD34D', style='dashed')
    dot.edge('mixtral', 'output', color='#1E3A8A')
    
    # Display the graph
    st.graphviz_chart(dot.source)

def main():
    # Header with dark theme
    st.markdown("""
    <div style="background: #1a1a1a; 
                padding: 2rem; 
                border-radius: 10px; 
                margin-bottom: 2rem;
                text-align: center;
                border: 1px solid #333;
                box-shadow: 0 4px 6px rgba(255, 255, 255, 0.1);">
        <h1 style="color: #ffffff; margin: 0;"> Emergency Response Analysis System</h1>
        <p style="color: #e0e0e0; margin: 0.5rem 0 0 0;">AI-Powered Multi-Agent Disaster Response Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs([" Analysis", " Architecture"])
    
    with tabs[0]:
        # File uploader with better styling
        st.markdown("###  Upload Disaster Scene Image")
        uploaded_file = st.file_uploader(
            "Choose an image file", 
            type=["jpg", "jpeg", "png"],
            help="Upload an image of a disaster or emergency scene for analysis"
        )
        
        if uploaded_file is not None:
            # Show uploaded image
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_path = tmp_file.name
            
            try:
                # Create agent flow visualization
                st.markdown("## 🔄 Agent Processing Pipeline")
                
                # Single placeholder for all agent boxes (will be updated dynamically)
                agent_boxes_placeholder = st.empty()
                
                # Initial display of agent boxes
                agent_boxes_placeholder.markdown("""
                <div style="display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
                    <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #f5576c; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                        <h3 style="color: #f5576c; margin: 0 0 1rem 0;">🔍 Scout Agent</h3>
                        <p style="color: #888; font-size: 0.9rem; margin: 0;">⏳ Waiting to start...</p>
                    </div>
                    <div style="text-align: center; font-size: 2rem; color: #ffffff; padding: 0 1rem;">→</div>
                    <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #4facfe; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                        <h3 style="color: #4facfe; margin: 0 0 1rem 0;">📋 Planner Agent</h3>
                        <p style="color: #888; font-size: 0.9rem; margin: 0;">⏳ Waiting...</p>
                    </div>
                    <div style="text-align: center; font-size: 2rem; color: #ffffff; padding: 0 1rem;">→</div>
                    <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #43e97b; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                        <h3 style="color: #43e97b; margin: 0 0 1rem 0;">📢 Communicator Agent</h3>
                        <p style="color: #888; font-size: 0.9rem; margin: 0;">⏳ Waiting...</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Status messages area
                status_area = st.empty()
                
                # Scout Agent Processing
                agent_boxes_placeholder.markdown("""
                <div style="display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
                    <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #ffd700; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                        <h3 style="color: #f5576c; margin: 0 0 1rem 0;">🔍 Scout Agent</h3>
                        <p style="color: #ffd700; font-weight: bold; margin: 0.5rem 0;">🔄 Initializing...</p>
                        <p style="color: #e0e0e0; font-size: 0.9rem; margin: 0;">Loading models</p>
                    </div>
                    <div style="text-align: center; font-size: 2rem; color: #ffffff; padding: 0 1rem;">→</div>
                    <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #4facfe; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                        <h3 style="color: #4facfe; margin: 0 0 1rem 0;">📋 Planner Agent</h3>
                        <p style="color: #888; font-size: 0.9rem; margin: 0;">⏳ Waiting...</p>
                    </div>
                    <div style="text-align: center; font-size: 2rem; color: #ffffff; padding: 0 1rem;">→</div>
                    <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #43e97b; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                        <h3 style="color: #43e97b; margin: 0 0 1rem 0;">📢 Communicator Agent</h3>
                        <p style="color: #888; font-size: 0.9rem; margin: 0;">⏳ Waiting...</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                status_area.info("🔄 Initializing Scout Agent...")
                with st.spinner("Loading YOLOv8 and LLaVA models..."):
                    scout_agent = ScoutAgent()
                
                agent_boxes_placeholder.markdown("""
                <div style="display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
                    <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #ffd700; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                        <h3 style="color: #f5576c; margin: 0 0 1rem 0;">🔍 Scout Agent</h3>
                        <p style="color: #ffd700; font-weight: bold; margin: 0.5rem 0;">🔄 Processing...</p>
                        <p style="color: #e0e0e0; font-size: 0.9rem; margin: 0;">Analyzing scene</p>
                    </div>
                    <div style="text-align: center; font-size: 2rem; color: #ffffff; padding: 0 1rem;">→</div>
                    <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #4facfe; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                        <h3 style="color: #4facfe; margin: 0 0 1rem 0;">📋 Planner Agent</h3>
                        <p style="color: #888; font-size: 0.9rem; margin: 0;">⏳ Waiting...</p>
                    </div>
                    <div style="text-align: center; font-size: 2rem; color: #ffffff; padding: 0 1rem;">→</div>
                    <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #43e97b; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                        <h3 style="color: #43e97b; margin: 0 0 1rem 0;">📢 Communicator Agent</h3>
                        <p style="color: #888; font-size: 0.9rem; margin: 0;">⏳ Waiting...</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                status_area.info("🔍 Analyzing scene with YOLOv8 and LLaVA...")
                with st.spinner("Processing image and detecting objects..."):
                    scout_results = scout_agent.analyze_scene(temp_path)
                
                agent_boxes_placeholder.markdown("""
                <div style="display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
                    <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #43e97b; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                        <h3 style="color: #f5576c; margin: 0 0 1rem 0;"> Scout Agent</h3>
                        <p style="color: #43e97b; font-weight: bold; margin: 0.5rem 0;"> Complete</p>
                        <p style="color: #e0e0e0; font-size: 0.9rem; margin: 0;">Scene analyzed</p>
                    </div>
                    <div style="text-align: center; font-size: 2rem; color: #ffffff; padding: 0 1rem;">→</div>
                    <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #4facfe; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                        <h3 style="color: #4facfe; margin: 0 0 1rem 0;"> Planner Agent</h3>
                        <p style="color: #888; font-size: 0.9rem; margin: 0;">⏳ Waiting...</p>
                    </div>
                    <div style="text-align: center; font-size: 2rem; color: #ffffff; padding: 0 1rem;">→</div>
                    <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #43e97b; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                        <h3 style="color: #43e97b; margin: 0 0 1rem 0;"> Communicator Agent</h3>
                        <p style="color: #888; font-size: 0.9rem; margin: 0;">⏳ Waiting...</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                status_area.success(" Scout Agent: Analysis complete!")
                
                if scout_results:
                    # Planner Agent Processing
                    agent_boxes_placeholder.markdown("""
                    <div style="display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
                        <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #43e97b; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                            <h3 style="color: #f5576c; margin: 0 0 1rem 0;"> Scout Agent</h3>
                            <p style="color: #43e97b; font-weight: bold; margin: 0.5rem 0;"> Complete</p>
                            <p style="color: #e0e0e0; font-size: 0.9rem; margin: 0;">Scene analyzed</p>
                        </div>
                        <div style="text-align: center; font-size: 2rem; color: #ffffff; padding: 0 1rem;">→</div>
                        <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #ffd700; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                            <h3 style="color: #4facfe; margin: 0 0 1rem 0;"> Planner Agent</h3>
                            <p style="color: #ffd700; font-weight: bold; margin: 0.5rem 0;"> Initializing...</p>
                            <p style="color: #e0e0e0; font-size: 0.9rem; margin: 0;">Loading model</p>
                        </div>
                        <div style="text-align: center; font-size: 2rem; color: #ffffff; padding: 0 1rem;">→</div>
                        <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #43e97b; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                            <h3 style="color: #43e97b; margin: 0 0 1rem 0;"> Communicator Agent</h3>
                            <p style="color: #888; font-size: 0.9rem; margin: 0;">⏳ Waiting...</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    status_area.info("Initializing Planner Agent...")
                    with st.spinner("Loading Phi model..."):
                        planner_agent = PlannerAgent()
                    
                    agent_boxes_placeholder.markdown("""
                    <div style="display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
                        <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #43e97b; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                            <h3 style="color: #f5576c; margin: 0 0 1rem 0;"> Scout Agent</h3>
                            <p style="color: #43e97b; font-weight: bold; margin: 0.5rem 0;">Complete</p>
                            <p style="color: #e0e0e0; font-size: 0.9rem; margin: 0;">Scene analyzed</p>
                        </div>
                        <div style="text-align: center; font-size: 2rem; color: #ffffff; padding: 0 1rem;">→</div>
                        <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #ffd700; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                            <h3 style="color: #4facfe; margin: 0 0 1rem 0;"> Planner Agent</h3>
                            <p style="color: #ffd700; font-weight: bold; margin: 0.5rem 0;"> Processing...</p>
                            <p style="color: #e0e0e0; font-size: 0.9rem; margin: 0;">Creating plan</p>
                        </div>
                        <div style="text-align: center; font-size: 2rem; color: #ffffff; padding: 0 1rem;">→</div>
                        <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #43e97b; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                            <h3 style="color: #43e97b; margin: 0 0 1rem 0;">Communicator Agent</h3>
                            <p style="color: #888; font-size: 0.9rem; margin: 0;">⏳ Waiting...</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    status_area.info(" Creating emergency response plan with Phi...")
                    with st.spinner("Generating detailed action plan using Phi model..."):
                        plan_results = planner_agent.create_plan(scout_results)
                    
                    agent_boxes_placeholder.markdown("""
                    <div style="display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
                        <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #43e97b; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                            <h3 style="color: #f5576c; margin: 0 0 1rem 0;"> Scout Agent</h3>
                            <p style="color: #43e97b; font-weight: bold; margin: 0.5rem 0;"> Complete</p>
                            <p style="color: #e0e0e0; font-size: 0.9rem; margin: 0;">Scene analyzed</p>
                        </div>
                        <div style="text-align: center; font-size: 2rem; color: #ffffff; padding: 0 1rem;">→</div>
                        <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #43e97b; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                            <h3 style="color: #4facfe; margin: 0 0 1rem 0;">Planner Agent</h3>
                            <p style="color: #43e97b; font-weight: bold; margin: 0.5rem 0;"> Complete</p>
                            <p style="color: #e0e0e0; font-size: 0.9rem; margin: 0;">Plan generated</p>
                        </div>
                        <div style="text-align: center; font-size: 2rem; color: #ffffff; padding: 0 1rem;">→</div>
                        <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #ffd700; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                            <h3 style="color: #43e97b; margin: 0 0 1rem 0;">Communicator Agent</h3>
                            <p style="color: #ffd700; font-weight: bold; margin: 0.5rem 0;">Initializing...</p>
                            <p style="color: #e0e0e0; font-size: 0.9rem; margin: 0;">Loading model</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    status_area.success("Planner Agent: Response plan created!")
                    
                    # Communicator Agent Processing
                    status_area.info(" Initializing Communicator Agent...")
                    with st.spinner("Loading Mixtral model..."):
                        communicator_agent = CommunicatorAgent()
                    
                    agent_boxes_placeholder.markdown("""
                    <div style="display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
                        <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #43e97b; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                            <h3 style="color: #f5576c; margin: 0 0 1rem 0;"> Scout Agent</h3>
                            <p style="color: #43e97b; font-weight: bold; margin: 0.5rem 0;"> Complete</p>
                            <p style="color: #e0e0e0; font-size: 0.9rem; margin: 0;">Scene analyzed</p>
                        </div>
                        <div style="text-align: center; font-size: 2rem; color: #ffffff; padding: 0 1rem;">→</div>
                        <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #43e97b; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                            <h3 style="color: #4facfe; margin: 0 0 1rem 0;"> Planner Agent</h3>
                            <p style="color: #43e97b; font-weight: bold; margin: 0.5rem 0;"> Complete</p>
                            <p style="color: #e0e0e0; font-size: 0.9rem; margin: 0;">Plan generated</p>
                        </div>
                        <div style="text-align: center; font-size: 2rem; color: #ffffff; padding: 0 1rem;">→</div>
                        <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #ffd700; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                            <h3 style="color: #43e97b; margin: 0 0 1rem 0;"> Communicator Agent</h3>
                            <p style="color: #ffd700; font-weight: bold; margin: 0.5rem 0;"> Processing...</p>
                            <p style="color: #e0e0e0; font-size: 0.9rem; margin: 0;">Generating report</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    status_area.info("📢 Generating comprehensive report with Mixtral...")
                    with st.spinner("Synthesizing analysis and creating report using Mixtral model..."):
                        report_results = communicator_agent.generate_report(scout_results, plan_results)
                    
                    agent_boxes_placeholder.markdown("""
                    <div style="display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
                        <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #43e97b; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                            <h3 style="color: #f5576c; margin: 0 0 1rem 0;"> Scout Agent</h3>
                            <p style="color: #43e97b; font-weight: bold; margin: 0.5rem 0;"> Complete</p>
                            <p style="color: #e0e0e0; font-size: 0.9rem; margin: 0;">Scene analyzed</p>
                        </div>
                        <div style="text-align: center; font-size: 2rem; color: #ffffff; padding: 0 1rem;">→</div>
                        <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #43e97b; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                            <h3 style="color: #4facfe; margin: 0 0 1rem 0;"> Planner Agent</h3>
                            <p style="color: #43e97b; font-weight: bold; margin: 0.5rem 0;"> Complete</p>
                            <p style="color: #e0e0e0; font-size: 0.9rem; margin: 0;">Plan generated</p>
                        </div>
                        <div style="text-align: center; font-size: 2rem; color: #ffffff; padding: 0 1rem;">→</div>
                        <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; border: 2px solid #43e97b; text-align: center; min-height: 200px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                            <h3 style="color: #43e97b; margin: 0 0 1rem 0;"> Communicator Agent</h3>
                            <p style="color: #43e97b; font-weight: bold; margin: 0.5rem 0;"> Complete</p>
                            <p style="color: #e0e0e0; font-size: 0.9rem; margin: 0;">Report ready</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    status_area.success(" Communicator Agent: Final report generated!")
                    
                    # Clear status area
                    status_area.empty()
                    
                    # Add spacing
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    
                    # Display results in a nice layout with tabs
                    st.markdown("##  Analysis Results")
                    
                    # Use tabs for each agent's output
                    result_tabs = st.tabs([" Scout Analysis", " Response Plan", " Final Report"])
                    
                    with result_tabs[0]:
                        display_scout_results(scout_results)
                    
                    with result_tabs[1]:
                        display_planner_results(plan_results)
                    
                    with result_tabs[2]:
                        display_communicator_results(report_results)
                    
                    # Summary metrics at the bottom
                    st.markdown("---")
                    st.markdown("###  Analysis Summary")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        total_objects = sum(len(items) for items in scout_results.get("terrain_data", {}).get("terrain_analysis", {}).values() if items)
                        st.metric("Objects Detected", total_objects, "items")
                    
                    with col2:
                        plan_length = len(plan_results.get("plan", "")) if plan_results else 0
                        st.metric("Plan Length", f"{plan_length:,}", "characters")
                    
                    with col3:
                        report_length = len(report_results.get("report", "")) if report_results else 0
                        st.metric("Report Length", f"{report_length:,}", "characters")
                    
                    with col4:
                        cuda_status = " GPU" if torch.cuda.is_available() else "⚠️ CPU"
                        st.metric("Processing", cuda_status)
                
                # Clean up
                os.unlink(temp_path)
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                logger.error(f"Error details: {type(e).__name__}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                
                # Clean up on error
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        else:
            # Show instructions when no file is uploaded
            st.info(" **Please upload an image** to begin the emergency response analysis. The system will:")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                <div style="background: #1a1a1a; padding: 1rem; border-radius: 8px; border-left: 4px solid #f5576c;">
                <h4 style="color: #ffffff;"> Scout Agent</h4>
                <ul style="color: #e0e0e0;">
                <li>Analyze the scene</li>
                <li>Detect objects and hazards</li>
                <li>Assess terrain conditions</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div style="background: #1a1a1a; padding: 1rem; border-radius: 8px; border-left: 4px solid #4facfe;">
                <h4 style="color: #ffffff;"> Planner Agent</h4>
                <ul style="color: #e0e0e0;">
                <li>Create response plan</li>
                <li>Allocate resources</li>
                <li>Assign teams</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown("""
                <div style="background: #1a1a1a; padding: 1rem; border-radius: 8px; border-left: 4px solid #43e97b;">
                <h4 style="color: #ffffff;"> Communicator Agent</h4>
                <ul style="color: #e0e0e0;">
                <li>Generate report</li>
                <li>Coordinate actions</li>
                <li>Document findings</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
    
    with tabs[1]:
        show_architecture_tab()

if __name__ == "__main__":
    main()
