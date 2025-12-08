import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from graphviz import Digraph
from data_generator import generate_transaction_data, generate_risk_scores
from screening import AMLScreener
from graph_analysis import TransactionGraph
from pydantic_agents import ScreeningAgents
from mcp_client import MCPClient

# Page config
st.set_page_config(
    page_title="AML Screening Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Tab styling CSS
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
    </style>
    """,
    unsafe_allow_html=True
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #000000;
        color: #ffffff;
    }
    .stApp {
        width: 100%;
        max-width: none;
        margin: 0;
        background-color: #000000;
        color: #ffffff;
    }
    [data-testid="stAppViewContainer"] {
        background-color: #000000;
    }
    [data-testid="stHeader"] {
        background-color: #1a1a1a;
    }
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, div {
        color: #ffffff !important;
    }
    .card {
        background-color: #1a1a1a;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
        color: #ffffff;
    }
    .metric-card {
        background-color: #1a1a1a;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(255, 255, 255, 0.1);
        text-align: center;
        color: #ffffff;
    }
    .metric-card h3, .metric-card h2 {
        color: #ffffff;
    }
    .risk-high {
        color: #ff4b4b;
        font-weight: bold;
    }
    .risk-medium {
        color: #ffa500;
        font-weight: bold;
    }
    .risk-low {
        color: #00cc00;
        font-weight: bold;
    }
    /* Streamlit widget styling */
    .stSlider, .stDateInput, .stCheckbox, .stButton, .stSelectbox {
        color: #ffffff;
    }
    /* Table and dataframe styling */
    .stDataFrame, table {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    .streamlit-expanderContent {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    /* Remove borders from iframes and HTML components */
    iframe {
        border: none !important;
        outline: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    [data-testid="stIFrame"] {
        border: none !important;
        outline: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    /* Remove spacing in column 4 (graph column) */
    [data-testid="column"]:nth-child(4) {
        margin: 0 !important;
        padding: 0 !important;
    }
    [data-testid="column"]:nth-child(4) > div {
        margin: 0 !important;
        padding: 0 !important;
    }
    /* Remove spacing between button row and result row in column 4 */
    .streamlit-expanderContent > div:has([data-testid="column"]:nth-child(4):has(button)) {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    .streamlit-expanderContent > div:has([data-testid="column"]:nth-child(4):has([data-testid="stHtml"])) {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    /* Remove spacing from graph button and result in column 4 */
    [data-testid="column"]:nth-child(4) .stButton {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    [data-testid="column"]:nth-child(4) [data-testid="stHtml"] {
        margin-top: 0 !important;
        padding-top: 0 !important;
        background-color: #000000 !important;
    }
    [data-testid="column"]:nth-child(4) [data-testid="stHtml"] iframe {
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = generate_risk_scores(generate_transaction_data(1000))
if 'screener' not in st.session_state:
    st.session_state.screener = AMLScreener()
if 'rag' not in st.session_state:
    try:
        from rag_agent import RAGAgent
        mcp_client = MCPClient()
        # Use lazy_init=True to defer expensive vector index building
        st.session_state.rag = RAGAgent(mcp_client=mcp_client, lazy_init=True)
    except Exception as e:
        print(f"RAG Agent initialization error: {e}")
        st.session_state.rag = None
if 'graph' not in st.session_state:
    st.session_state.graph = TransactionGraph()
    # Only build graph once, skip if already has nodes
    if len(st.session_state.graph.G.nodes()) == 0:
        st.session_state.graph.build_graph(st.session_state.transactions)
if 'crew_agents' not in st.session_state:
    try:
        mcp_client = MCPClient()
        st.session_state.crew_agents = ScreeningAgents(mcp_client=mcp_client)
    except:
        st.session_state.crew_agents = None

# Main content
st.markdown("<h1 style='text-align: center;'> AML Screening Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

# Create tabs - only Dashboard and Architecture
tab1, tab2 = st.tabs([
    " Dashboard", 
    " Architecture"
])

with tab1:
    # Screening Parameters Row
    param1, param2, param3 = st.columns([2, 3, 2])
    with param1:
        risk_threshold = st.slider("Risk Threshold", 0, 100, 70)
    with param2:
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now())
        )
    with param3:
        show_high_risk_only = st.checkbox("Show only high-risk transactions", value=False)

    # Filter transactions
    filtered_tx = st.session_state.transactions[
        (st.session_state.transactions['timestamp'].dt.date >= date_range[0]) &
        (st.session_state.transactions['timestamp'].dt.date <= date_range[1])
    ]

    if show_high_risk_only:
        filtered_tx = filtered_tx[filtered_tx['risk_score'] > risk_threshold]
        # Show only the top 8 high-risk transactions
        filtered_tx = filtered_tx.sort_values(by='risk_score', ascending=False).head(8)

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
            <div class="metric-card">
                <h3>Total Transactions</h3>
                <h2>{}</h2>
            </div>
        """.format(len(st.session_state.transactions)), unsafe_allow_html=True)

    with col2:
        if show_high_risk_only:
            high_risk = len(filtered_tx)
        else:
            high_risk = len(st.session_state.transactions[st.session_state.transactions['risk_score'] > risk_threshold])
        st.markdown("""
            <div class="metric-card">
                <h3>High Risk Transactions</h3>
                <h2>{}</h2>
            </div>
        """.format(high_risk), unsafe_allow_html=True)

    with col3:
        avg_risk = st.session_state.transactions['risk_score'].mean()
        st.markdown("""
            <div class="metric-card">
                <h3>Average Risk Score</h3>
                <h2>{:.1f}</h2>
            </div>
        """.format(avg_risk), unsafe_allow_html=True)

    with col4:
        total_amount = st.session_state.transactions['amount'].sum()
        st.markdown("""
            <div class="metric-card">
                <h3>Total Amount</h3>
                <h2>${:,.2f}</h2>
            </div>
        """.format(total_amount), unsafe_allow_html=True)

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Risk Score Distribution")
        fig = px.histogram(
            st.session_state.transactions,
            x='risk_score',
            nbins=20,
            color_discrete_sequence=['#1f77b4']
        )
        fig.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Transactions by Type")
        fig = px.pie(
            st.session_state.transactions,
            names='transaction_type',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(
            showlegend=True,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

    # Transaction List
    if show_high_risk_only:
        st.markdown("### High Risk Transaction Details")
    else:
        st.markdown("### Recent Transactions")
    st.markdown("---")

    # Initialize all session_state keys upfront to avoid dictionary modification during iteration
    keys_to_init = []
    for _, tx in filtered_tx.iterrows():
        tx_id = tx['transaction_id']
        keys_to_init.extend([
            f'l1_result_{tx_id}',
            f'l2_result_{tx_id}',
            f'rag_result_{tx_id}',
            f'graph_result_{tx_id}'
        ])
    
    # Initialize all keys at once
    for key in keys_to_init:
        if key not in st.session_state:
            st.session_state[key] = None

    # Display transactions
    for _, tx in filtered_tx.iterrows():
        with st.expander(f"Transaction {tx['transaction_id']} - {tx['amount']} {tx['currency']}"):
            # Transaction details (full width)
            st.markdown(f"""
                **Sender:** {tx['sender_name']}  
                **Receiver:** {tx['receiver_name']}  
                **Type:** {tx['transaction_type']}  
                **Country:** {tx['country']}  
                **Purpose:** {tx['purpose']}
            """)

            # Button row (full width, left-aligned)
            b1, b2, b3, b4 = st.columns(4)
            tx_id = tx['transaction_id']
            l1_result_key = f'l1_result_{tx_id}'
            l2_result_key = f'l2_result_{tx_id}'
            rag_result_key = f'rag_result_{tx_id}'
            graph_result_key = f'graph_result_{tx_id}'
            l1_btn_key = f'l1_btn_{tx_id}'
            l2_btn_key = f'l2_btn_{tx_id}'
            rag_btn_key = f'rag_btn_{tx_id}'
            graph_btn_key = f'graph_btn_{tx_id}'
            with b1:
                if st.button("L1 Screening", key=l1_btn_key):
                    model_name = "mistral:latest"
                    if st.session_state.crew_agents:
                        model_name = st.session_state.crew_agents.model_name_l1
                    with st.spinner(f"Performing Level 1 screening ({model_name})..."):
                        if st.session_state.crew_agents:
                            try:
                                score, explanation = st.session_state.crew_agents.level1_screening(tx)
                            except:
                                # Fallback to original screener
                                score, explanation = st.session_state.screener.level1_screening(tx)
                        else:
                            score, explanation = st.session_state.screener.level1_screening(tx)
                        st.session_state[l1_result_key] = (score, explanation)
            with b2:
                if st.button("L2 Screening", key=l2_btn_key):
                    model_name = "deepseek-r1:14b"
                    if st.session_state.crew_agents:
                        model_name = st.session_state.crew_agents.model_name_l2
                    with st.spinner(f"Performing Level 2 screening ({model_name})..."):
                        related = st.session_state.screener.find_related_transactions(tx, st.session_state.transactions)
                        if st.session_state.crew_agents:
                            try:
                                result = st.session_state.crew_agents.level2_screening(tx, related)
                            except:
                                result = st.session_state.screener.level2_screening(tx, related)
                        else:
                            result = st.session_state.screener.level2_screening(tx, related)
                        st.session_state[l2_result_key] = result
            with b3:
                if st.button("RAG (MCP)", key=rag_btn_key):
                    with st.spinner("Performing RAG-enhanced analysis with MCP (Mistral)..."):
                        if st.session_state.crew_agents:
                            try:
                                result = st.session_state.crew_agents.rag_analysis(tx.to_dict())
                            except:
                                result = st.session_state.rag.analyze_transaction(tx.to_dict())
                        else:
                            result = st.session_state.rag.analyze_transaction(tx.to_dict())
                        st.session_state[rag_result_key] = result
            with b4:
                if st.button("Graph", key=graph_btn_key):
                    with st.spinner("Performing graph analysis..."):
                        viz_file = st.session_state.graph.visualize_network(tx_id, max_depth=3)
                        st.session_state[graph_result_key] = viz_file

            # Results row: 4 columns for L1, L2, RAG, Graph
            r1, r2, r3, r4 = st.columns(4)
            with r1:
                if st.session_state[l1_result_key]:
                    score, explanation = st.session_state[l1_result_key]
                    st.markdown(f"""
                        **Risk Score (L1):** {score:.1f}  
                        **Analysis (L1):** {explanation}
                    """)
            with r2:
                if st.session_state[l2_result_key]:
                    result = st.session_state[l2_result_key]
                    st.markdown(f"""
                        **Risk Score (L2):** {result['score']:.1f}  
                        **Risk Level (L2):** {result['risk_level']}  
                        **Risk Factors (L2):** {result['risk_factors']}  
                        **Recommendations (L2):** {result['recommendations']}  
                        **Explanation (L2):** {result['explanation']}
                    """)
            with r3:
                if st.session_state[rag_result_key]:
                    result = st.session_state[rag_result_key]
                    st.markdown(f"""
                        **RAG Analysis:**  
                        Risk Score: {result['score']}  
                        Risk Level: {result['risk_level']}  
                        Regulations: {result['regulations']}  
                        Typologies: {result['typologies']}  
                        Risk Factors: {result['risk_factors']}  
                        Recommendations: {result['recommendations']}  
                        **Explanation (RAG):** {result['explanation']}
                    """)
            with r4:
                if st.session_state[graph_result_key]:
                    viz_file = st.session_state[graph_result_key]
                    try:
                        with open(viz_file, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                            if html_content.strip():
                                # Add additional CSS to remove iframe borders and spacing
                                border_removal_css = """
                                <style>
                                    body {
                                        margin: 0 !important;
                                        padding: 0 !important;
                                    }
                                    iframe {
                                        border: none !important;
                                        outline: none !important;
                                        margin: 0 !important;
                                        padding: 0 !important;
                                        display: block !important;
                                    }
                                    * {
                                        margin: 0 !important;
                                        padding: 0 !important;
                                    }
                                </style>
                                """
                                # Inject CSS if not already present
                                if 'border: none' not in html_content:
                                    if '</head>' in html_content:
                                        html_content = html_content.replace('</head>', border_removal_css + '</head>')
                                    elif '<body>' in html_content:
                                        html_content = html_content.replace('<body>', '<body>' + border_removal_css)
                                
                                # Render with no spacing
                                st.components.v1.html(html_content, height=800, scrolling=False)
                            else:
                                st.error("Graph visualization file is empty")
                    except FileNotFoundError:
                        st.error(f"Graph visualization file not found: {viz_file}")
                    except Exception as e:
                        st.error(f"Error displaying graph: {str(e)}")
                        st.info(f"Debug info - File path: {viz_file}")

    # Download buttons
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Download Transaction Data"):
            csv = filtered_tx.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="transactions.csv",
                mime="text/csv"
            )

    with col2:
        if st.button("Download Risk Report"):
            report = {
                "total_transactions": len(filtered_tx),
                "high_risk_transactions": high_risk,
                "average_risk_score": avg_risk,
                "total_amount": total_amount,
                "risk_threshold": risk_threshold,
                "date_range": [str(d) for d in date_range]
            }
            st.download_button(
                label="Download JSON",
                data=json.dumps(report, indent=2),
                file_name="risk_report.json",
                mime="application/json"
            )

# Architecture Tab
with tab2:
    st.markdown("<h1 style='text-align: center;'> Application Architecture</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("Overview")
    st.markdown("""
    This AML (Anti-Money Laundering) Screening Dashboard is a comprehensive transaction monitoring 
    and risk assessment application that leverages Large Language Models (LLMs) and graph analytics 
    to identify potential money laundering activities.
    """)
    
    st.subheader("Architecture Components")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Frontend Layer
        - **Streamlit**: Web-based dashboard framework
        - **Plotly**: Interactive data visualizations
        - **Pyvis/Vis.js**: Network graph visualizations
        - **Custom CSS**: Dark theme styling
        """)
        
        st.markdown("""
        ### LLM Integration
        - **Ollama**: Local LLM inference server
        - **Models Used**:
          - `mistral:latest` - Level 1 screening & RAG
          - `deepseek-r1:14b` - Level 2 enhanced screening
        - **Pydantic**: Structured output validation
        - **A2A**: Agent-to-Agent communication framework
        - **MCP Protocol**: Model Context Protocol for RAG operations
        """)
    
    with col2:
        st.markdown("""
        ### Data Processing Layer
        - **Pandas**: Transaction data manipulation
        - **Faker**: Synthetic transaction generation
        - **NetworkX**: Graph construction and analysis
        - **Scipy**: Statistical computations
        """)
        
        st.markdown("""
        ### RAG (Retrieval-Augmented Generation)
        - **Knowledge Base**: Local JSON files + External documents
          - AML Regulations
          - AML Typologies
          - High-Risk Countries
        - **FAISS Vector Search**: Semantic similarity search
        - **MCP Integration**: External document retrieval via MCP
        - **Context Injection**: Retrieved context injected into LLM prompts
        """)
    
    st.markdown("---")
    st.subheader("Data Flow")
    
    # Create Data Flow Diagram
    try:
        flow_dot = Digraph(comment='AML Data Flow', format='png')
        flow_dot.attr(rankdir='LR', size='14,8', bgcolor='#000000', fontcolor='#ffffff')
        flow_dot.attr('node', shape='box', style='rounded,filled', fillcolor='#1a1a1a', fontcolor='#ffffff', color='#4a9eff')
        flow_dot.attr('edge', color='#ffffff', fontcolor='#ffffff')
        
        # Data Flow Steps
        flow_dot.node('GEN', '1. Data Generation\n(Synthetic Transactions)', fillcolor='#2d4a7c')
        flow_dot.node('SCORE', '2. Risk Scoring\n(Amount, Country, Type)', fillcolor='#3d5a7c')
        flow_dot.node('L1_FLOW', '3. Level 1 Screening\n(mistral:latest)', fillcolor='#4d6a8c')
        flow_dot.node('L2_FLOW', '4. Level 2 Screening\n(deepseek-r1:14b)', fillcolor='#4d6a8c')
        flow_dot.node('RAG_FLOW', '5. RAG Analysis\n(Knowledge Base)', fillcolor='#4d6a8c')
        flow_dot.node('GRAPH_FLOW', '6. Graph Analysis\n(NetworkX)', fillcolor='#3d5a7c')
        flow_dot.node('OUTPUT', '7. Results & Visualization\n(Dashboard)', fillcolor='#2d4a7c', shape='ellipse')
        
        # Flow connections
        flow_dot.edge('GEN', 'SCORE', label='Transaction Data')
        flow_dot.edge('SCORE', 'L1_FLOW', label='Scored Data')
        flow_dot.edge('SCORE', 'L2_FLOW', label='Scored Data')
        flow_dot.edge('SCORE', 'RAG_FLOW', label='Scored Data')
        flow_dot.edge('SCORE', 'GRAPH_FLOW', label='Scored Data')
        flow_dot.edge('L1_FLOW', 'OUTPUT', label='Risk Score', style='dashed')
        flow_dot.edge('L2_FLOW', 'OUTPUT', label='Risk Score', style='dashed')
        flow_dot.edge('RAG_FLOW', 'OUTPUT', label='Risk Score', style='dashed')
        flow_dot.edge('GRAPH_FLOW', 'OUTPUT', label='Network Graph', style='dashed')
        
        # Render the flow graph
        flow_dot.render('data_flow', format='png', cleanup=True)
        
        # Display the image
        st.image('data_flow.png')
        
    except Exception as e:
        st.warning(f"Could not generate data flow diagram: {str(e)}")
    
    st.markdown("""
    ### Transaction Processing Pipeline
    
    1. **Data Generation**: Synthetic transaction data generated with risk clusters
    2. **Risk Scoring**: Initial risk scores calculated based on:
       - Transaction amount
       - Country risk
       - Transaction type
    3. **Level 1 Screening**: Basic rule-based + LLM analysis using `mistral:latest`
    4. **Level 2 Screening**: Enhanced due diligence with:
       - Related transaction analysis
       - Pattern detection
       - LLM analysis using `deepseek-r1:14b`
    5. **RAG Analysis**: Context-aware analysis using:
       - AML regulations knowledge base
       - Typology patterns
       - Country risk data
    6. **Graph Analysis**: Network visualization showing:
       - Transaction relationships
       - Entity connections
       - Risk clusters
    7. **Results & Visualization**: All results displayed in the dashboard
    """)
    
    st.markdown("---")
    st.subheader("System Architecture Diagram")
    
    # Create Graphviz diagram with layered structure
    try:
        dot = Digraph(comment='AML Screening Architecture', format='png')
        dot.attr(rankdir='TB', size='14,10', bgcolor='#000000', fontcolor='#ffffff')
        dot.attr('node', shape='box', style='rounded,filled', fontcolor='#ffffff', color='#4a9eff')
        dot.attr('edge', color='#ffffff', fontcolor='#ffffff')
        
        # Create subgraphs for layers
        with dot.subgraph(name='cluster_ui') as ui_layer:
            ui_layer.attr(label='Presentation Layer', style='filled', fillcolor='#1a1a1a', color='#4a9eff', fontcolor='#ffffff')
            ui_layer.node('UI', 'Streamlit Dashboard\n(Web Interface)', fillcolor='#2d4a7c')
        
        with dot.subgraph(name='cluster_agents') as agent_layer:
            agent_layer.attr(label='Agent Layer (A2A Communication)', style='filled', fillcolor='#1a1a1a', color='#4a9eff', fontcolor='#ffffff')
            agent_layer.node('L1', 'L1 Screening Agent\n(Pydantic + mistral)', fillcolor='#3d5a7c')
            agent_layer.node('L2', 'L2 Screening Agent\n(Pydantic + deepseek)', fillcolor='#3d5a7c')
            agent_layer.node('RAG', 'RAG Analysis Agent\n(Pydantic + mistral + MCP + FAISS)', fillcolor='#3d5a7c')
            agent_layer.node('A2A', 'A2A Framework\n(Agent Registry)', fillcolor='#5a7c9e', shape='diamond')
        
        with dot.subgraph(name='cluster_llm') as llm_layer:
            llm_layer.attr(label='LLM Layer', style='filled', fillcolor='#1a1a1a', color='#4a9eff', fontcolor='#ffffff')
            llm_layer.node('OLLAMA', 'Ollama API\n(Local LLM Server)', shape='ellipse', fillcolor='#4a7c9e')
            llm_layer.node('MISTRAL', 'mistral:latest', fillcolor='#5a7c9e')
            llm_layer.node('DEEPSEEK', 'deepseek-r1:14b', fillcolor='#5a7c9e')
        
        with dot.subgraph(name='cluster_data') as data_layer:
            data_layer.attr(label='Data & Knowledge Layer', style='filled', fillcolor='#1a1a1a', color='#4a9eff', fontcolor='#ffffff')
            data_layer.node('KB', 'Knowledge Base\n(JSON Files)', fillcolor='#5a7c9e')
            data_layer.node('MCP', 'MCP Client\n(External Docs)', fillcolor='#6a8cae', shape='ellipse')
            data_layer.node('DATA', 'Data Processing\n(Pandas, NetworkX)', fillcolor='#3d5a7c')
        
        with dot.subgraph(name='cluster_analysis') as analysis_layer:
            analysis_layer.attr(label='Analysis Layer', style='filled', fillcolor='#1a1a1a', color='#4a9eff', fontcolor='#ffffff')
            analysis_layer.node('GRAPH', 'Graph Analysis\n(NetworkX + Pyvis)', fillcolor='#2d4a7c')
        
        # Connections from UI to Agents
        dot.edge('UI', 'L1', label='Transaction Data', color='#4a9eff')
        dot.edge('UI', 'L2', label='Transaction Data', color='#4a9eff')
        dot.edge('UI', 'RAG', label='Transaction Data', color='#4a9eff')
        dot.edge('UI', 'GRAPH', label='Transaction Data', color='#4a9eff')
        
        # A2A Communication (bidirectional between agents)
        dot.edge('L1', 'A2A', label='A2A', color='#00ff00', style='bold')
        dot.edge('A2A', 'L1', label='A2A', color='#00ff00', style='bold')
        dot.edge('L2', 'A2A', label='A2A', color='#00ff00', style='bold')
        dot.edge('A2A', 'L2', label='A2A', color='#00ff00', style='bold')
        dot.edge('RAG', 'A2A', label='A2A', color='#00ff00', style='bold')
        dot.edge('A2A', 'RAG', label='A2A', color='#00ff00', style='bold')
        
        # Direct agent-to-agent communication (optional, shown as lighter lines)
        dot.edge('L1', 'L2', label='Collaborate', color='#00ff88', style='dashed', constraint='false')
        dot.edge('L2', 'RAG', label='Request Context', color='#00ff88', style='dashed', constraint='false')
        dot.edge('RAG', 'L1', label='Provide Context', color='#00ff88', style='dashed', constraint='false')
        
        # Agent to LLM connections
        dot.edge('L1', 'OLLAMA', label='LLM Request', color='#ffaa00')
        dot.edge('L2', 'OLLAMA', label='LLM Request', color='#ffaa00')
        dot.edge('RAG', 'OLLAMA', label='LLM Request\n(mistral)', color='#ffaa00')
        
        # Ollama to models - show which agent uses which model
        dot.edge('OLLAMA', 'MISTRAL', label='L1 & RAG', color='#ffaa00')
        dot.edge('OLLAMA', 'DEEPSEEK', label='L2', color='#ffaa00')
        
        # RAG specific connections
        dot.edge('RAG', 'MCP', label='Document Retrieval', color='#ff00ff')
        dot.edge('RAG', 'KB', label='FAISS Vector Search', color='#ff00ff')
        
        # Data flow
        dot.edge('DATA', 'UI', label='Processed Data', color='#00ffff', style='dashed')
        dot.edge('DATA', 'GRAPH', label='Graph Construction', color='#00ffff')
        
        # Results back to UI
        dot.edge('L1', 'UI', label='Risk Score', color='#ffff00', style='dashed')
        dot.edge('L2', 'UI', label='Risk Score', color='#ffff00', style='dashed')
        dot.edge('RAG', 'UI', label='Risk Score', color='#ffff00', style='dashed')
        dot.edge('GRAPH', 'UI', label='Network Viz', color='#ffff00', style='dashed')
        
        # Render the graph
        dot.render('architecture', format='png', cleanup=True)
        
        # Display the image
        st.image('architecture.png')
        
    except Exception as e:
        st.warning(f"Could not generate Graphviz diagram: {str(e)}")
        st.info("Make sure Graphviz is installed: sudo apt-get install graphviz (or equivalent)")
        # Fallback to text diagram
        st.markdown("""
        ```
        ┌─────────────────────────────────────────────────────────────┐
        │                    User Interface Layer                     │
        │                    (Streamlit Dashboard)                     │
        └───────────────────────┬─────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐
        │   Level 1    │ │   Level 2   │ │    RAG     │
        │  Screening   │ │  Screening  │ │  Analysis  │
        └───────┬──────┘ └──────┬──────┘ └─────┬──────┘
                │               │               │
                └───────────────┼───────────────┘
                                │
                        ┌───────▼───────┐
                        │  Ollama API   │
                        │  (Local LLM)  │
                        └───────┬───────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐
        │  mistral:    │ │ deepseek-  │ │ Knowledge  │
        │   latest     │ │ r1:14b      │ │   Base     │
        └──────────────┘ └─────────────┘ └────────────┘
        
        ┌─────────────────────────────────────────────────────────────┐
        │                    Graph Analysis Layer                      │
        │              (NetworkX + Pyvis Visualization)                │
        └─────────────────────────────────────────────────────────────┘
        ```
        """)
    
    st.markdown("---")
    st.subheader("Protocols & Communication")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### ✅ Using MCP (Model Context Protocol)
        - **Implementation**: MCP client for RAG operations
        - **Purpose**: External document retrieval and validation
        - **Features**:
          - Document context retrieval
          - External document validation
          - Fallback to local mode if MCP server unavailable
        - **Integration**: RAG agent uses MCP for enhanced context
        """)
    
    with col2:
        st.markdown("""
        ### ✅ Using A2A (Agent-to-Agent)
        - **Implementation**: Agent framework with message passing
        - **Agents**: L1, L2, RAG agents communicate via A2A protocol
        - **Features**:
          - Agent registry for routing
          - Request-response messaging
          - Agent collaboration
        - **Orchestration**: A2A framework manages agent workflows with Pydantic validation
        """)
    
    st.markdown("---")
    st.subheader("Technology Stack")
    
    tech_stack = {
        "Frontend": ["Streamlit", "Plotly", "Pyvis", "HTML/CSS", "Graphviz"],
        "Backend": ["Python 3.8+", "Pandas", "NetworkX", "Scipy"],
        "LLM & AI": ["Ollama", "mistral:latest", "deepseek-r1:14b", "Pydantic"],
        "Agentic AI": ["A2A Framework", "Pydantic Validation", "MCP Protocol"],
        "RAG & Search": ["FAISS", "Vector Embeddings", "Semantic Search", "MCP Client"],
        "Data": ["JSON (Knowledge Base)", "CSV (Transactions)", "In-Memory Graph", "FAISS Index"],
        "Visualization": ["Plotly Charts", "Network Graphs", "Interactive Dashboards", "Graphviz Diagrams"]
    }
    
    for category, technologies in tech_stack.items():
        with st.expander(f"**{category}**"):
            for tech in technologies:
                st.markdown(f"- {tech}")
    
    st.markdown("---")
    st.subheader("Key Features")
    
    features = [
        "✅ Real-time transaction monitoring",
        "✅ Multi-level risk screening (L1 & L2) with Pydantic + A2A",
        "✅ RAG-enhanced analysis with MCP and FAISS vector search",
        "✅ Agent-to-Agent (A2A) communication",
        "✅ Graph-based relationship analysis",
        "✅ Interactive visualizations",
        "✅ Dark theme UI",
        "✅ Local LLM inference (privacy-preserving)"
    ]
    
    for feature in features:
        st.markdown(feature)
    
    st.markdown("---")
    st.subheader("Deployment Architecture")
    
    st.markdown("""
    ### Current Setup
    - **Environment**: Local development with virtual environment
    - **LLM Server**: Ollama running locally
    - **Web Server**: Streamlit development server
    - **Storage**: File-based (JSON knowledge base, temporary HTML visualizations)
    
    ### Scalability Considerations
    - **Horizontal Scaling**: Could deploy multiple Streamlit instances behind a load balancer
    - **LLM Scaling**: Ollama supports multiple concurrent requests
    - **Graph Storage**: Currently in-memory; could migrate to graph database (Neo4j, ArangoDB)
    - **Knowledge Base**: Could migrate to vector database (FAISS, Pinecone) for semantic search
    """)
