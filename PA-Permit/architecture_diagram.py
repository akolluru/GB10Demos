"""
Architecture Diagram Generator using Graphviz
Creates visual representation of the PA Permit Automation System
"""
import graphviz


def generate_architecture_diagram():
    """
    Generate comprehensive architecture diagram showing all system components
    and their interactions
    """
    
    # Create directed graph with Streamlit dark theme background color
    dot = graphviz.Digraph(comment='PA Permit Automation System Architecture')
    dot.attr(rankdir='TB', splines='ortho', nodesep='1.0', ranksep='1.5', size='18,14', bgcolor='#0E1117')
    dot.attr('node', shape='box', style='filled', fontname='Arial', fontsize='11', fontcolor='white')
    dot.attr('edge', fontcolor='white')
    
    # UI Layer
    with dot.subgraph(name='cluster_ui') as c:
        c.attr(label='User Interface Layer (Streamlit)', style='filled', color='#1E3A5F', fontcolor='white', bgcolor='#1A2332')
        c.node('streamlit', 'Streamlit UI\n(Web Interface)', 
               fillcolor='#2D4A6B', shape='box3d', fontsize='12', fontcolor='white')
        c.node('forms', 'Application\nForms', fillcolor='#2D4A6B', fontsize='10', fontcolor='white')
        c.node('status', 'Results\nDashboard', fillcolor='#2D4A6B', fontsize='10', fontcolor='white')
    
    # Agent Layer - True Horizontal Bar
    with dot.subgraph(name='cluster_agents') as c:
        c.attr(label='AI Agent Layer (CrewAI) - Sequential Processing', 
               style='filled', color='#2D5F3F', fontcolor='white', bgcolor='#1A2E1F')
        
        # Force all agents to be on the same horizontal rank
        c.attr(rank='same')
        
        # Define agents with consistent sizing
        c.node('agent1', 'Intake Agent', fillcolor='#2D5F3F', shape='box', 
               style='filled', width='2.0', height='1.0', fontsize='10', fontcolor='white')
        c.node('agent2', 'Review Agent', fillcolor='#2D5F3F', shape='box', 
               style='filled', width='2.0', height='1.0', fontsize='10', fontcolor='white')
        c.node('agent3', 'Compliance Agent', fillcolor='#2D5F3F', shape='box', 
               style='filled', width='2.0', height='1.0', fontsize='10', fontcolor='white')
        c.node('agent4', 'Decision Agent', fillcolor='#2D5F3F', shape='box', 
               style='filled', width='2.0', height='1.0', fontsize='10', fontcolor='white')
        
        # Force strict horizontal order
        c.edge('agent1', 'agent2', style='invis', minlen='0')
        c.edge('agent2', 'agent3', style='invis', minlen='0')
        c.edge('agent3', 'agent4', style='invis', minlen='0')
        
        # Visible A2A connections
        c.edge('agent1', 'agent2', label='A2A', color='#4ade80', fontsize='9', 
               style='bold', constraint='false', fontcolor='white')
        c.edge('agent2', 'agent3', label='A2A', color='#4ade80', fontsize='9', 
               style='bold', constraint='false', fontcolor='white')
        c.edge('agent3', 'agent4', label='A2A', color='#4ade80', fontsize='9', 
               style='bold', constraint='false', fontcolor='white')
    
    # Support Systems
    with dot.subgraph(name='cluster_support') as c:
        c.attr(label='Support Systems', style='filled', color='#8B6914', fontcolor='white', bgcolor='#2E2417')
        c.node('mcp', 'MCP Server\n(Context & A2A)', fillcolor='#8B6914', 
               shape='diamond', fontsize='10', fontcolor='white')
        c.node('ollama', 'Ollama\n(Mistral LLM)', fillcolor='#8B2E2E', 
               shape='doubleoctagon', fontsize='10', fontcolor='white')
    
    # Shared Resources
    with dot.subgraph(name='cluster_shared_resources') as c:
        c.attr(label='Shared Resources', style='filled', color='#4A4A6A', fontcolor='white', bgcolor='#1E1E2E')
        c.node('context_store', 'Context\nStore', fillcolor='#4A4A6A', 
               shape='cylinder', fontsize='10', fontcolor='white')
        c.node('vector_db', 'Vector\nDatabase', fillcolor='#4A4A6A', 
               shape='cylinder', fontsize='10', fontcolor='white')
        c.node('storage', 'Application\nDatabase', fillcolor='#4A4A6A', 
               shape='cylinder', fontsize='10', fontcolor='white')
        c.node('pa_gov', 'PA.gov\nRegulations', fillcolor='#6A6A4A', 
               shape='folder', fontsize='9', fontcolor='white')
        c.node('dep', 'PA DEP\nGuidelines', fillcolor='#6A6A4A', 
               shape='folder', fontsize='9', fontcolor='white')
    
    # Main Flow Connections
    dot.edge('forms', 'agent1', label='Submit Application', color='#60a5fa', 
             fontsize='12', style='bold', fontcolor='white')
    dot.edge('agent4', 'status', label='Final Result', color='#60a5fa', 
             fontsize='12', style='bold', fontcolor='white')
    
    # Agent to Support System Connections
    dot.edge('agent1', 'mcp', color='#f59e0b', style='solid', label='Context', fontsize='8', fontcolor='white')
    dot.edge('agent2', 'mcp', color='#f59e0b', style='solid', label='Context', fontsize='8', fontcolor='white')
    dot.edge('agent3', 'mcp', color='#f59e0b', style='solid', label='Context', fontsize='8', fontcolor='white')
    dot.edge('agent4', 'mcp', color='#f59e0b', style='solid', label='Context', fontsize='8', fontcolor='white')
    
    dot.edge('agent1', 'ollama', color='#ef4444', style='solid', label='LLM', fontsize='8', fontcolor='white')
    dot.edge('agent2', 'ollama', color='#ef4444', style='solid', label='LLM', fontsize='8', fontcolor='white')
    dot.edge('agent3', 'ollama', color='#ef4444', style='solid', label='LLM', fontsize='8', fontcolor='white')
    dot.edge('agent4', 'ollama', color='#ef4444', style='solid', label='LLM', fontsize='8', fontcolor='white')
    
    # MCP to Shared Resources Connections
    dot.edge('mcp', 'context_store', color='#3b82f6', style='bold', label='Store/Retrieve', fontsize='8', fontcolor='white')
    dot.edge('mcp', 'vector_db', color='#3b82f6', style='bold', label='Embeddings', fontsize='8', fontcolor='white')
    dot.edge('mcp', 'storage', color='#3b82f6', style='bold', label='Persist', fontsize='8', fontcolor='white')
    dot.edge('mcp', 'pa_gov', color='#3b82f6', style='bold', label='Query', fontsize='8', fontcolor='white')
    dot.edge('mcp', 'dep', color='#3b82f6', style='bold', label='Query', fontsize='8', fontcolor='white')
    
    # Add comprehensive legend
    with dot.subgraph(name='cluster_legend') as c:
        c.attr(label='Legend', style='filled', color='#262730', fontcolor='white', bgcolor='#1A1A24')
        c.node('leg1', 'A2A Flow', fillcolor='transparent', shape='plaintext', fontsize='9', fontcolor='white')
        c.node('leg2', 'Agent-MCP', fillcolor='transparent', shape='plaintext', fontsize='9', fontcolor='white')
        c.node('leg3', 'Agent-LLM', fillcolor='transparent', shape='plaintext', fontsize='9', fontcolor='white')
        c.node('leg4', 'MCP-Resources', fillcolor='transparent', shape='plaintext', fontsize='9', fontcolor='white')
        
        c.edge('leg1', 'leg2', color='#4ade80', style='bold', label='', constraint='false')
        c.edge('leg2', 'leg3', color='#f59e0b', style='solid', label='', constraint='false')
        c.edge('leg3', 'leg4', color='#ef4444', style='solid', label='', constraint='false')
        c.edge('leg4', 'leg1', color='#3b82f6', style='bold', label='', constraint='false')
    
    return dot


def generate_workflow_diagram():
    """Generate simplified workflow diagram"""
    
    dot = graphviz.Digraph(comment='Permit Processing Workflow')
    dot.attr(rankdir='LR', size='12,6', nodesep='1.0', ranksep='1.5', bgcolor='#0E1117')
    dot.attr('node', shape='box', style='filled', fontname='Arial', fontsize='12', fontcolor='white')
    dot.attr('edge', fontcolor='white')
    
    # Define nodes with better styling for dark background
    dot.node('start', 'Application\nSubmitted', shape='ellipse', fillcolor='#2D5F3F', style='filled', fontsize='14', fontcolor='white')
    dot.node('intake', 'Intake\nAgent', shape='box', fillcolor='#2D4A6B', style='filled', fontsize='12', fontcolor='white')
    dot.node('review', 'Review\nAgent', shape='box', fillcolor='#2D4A6B', style='filled', fontsize='12', fontcolor='white')
    dot.node('compliance', 'Compliance\nAgent', shape='box', fillcolor='#2D4A6B', style='filled', fontsize='12', fontcolor='white')
    dot.node('decision', 'Decision\nAgent', shape='box', fillcolor='#2D4A6B', style='filled', fontsize='12', fontcolor='white')
    dot.node('end', 'Final\nResult', shape='ellipse', fillcolor='#8B2E2E', style='filled', fontsize='14', fontcolor='white')
    
    # Define edges with A2A labels
    dot.edge('start', 'intake', label='Submit', fontsize='10', color='#60a5fa', fontcolor='white')
    dot.edge('intake', 'review', label='A2A Handoff', color='#4ade80', style='bold', fontsize='10', fontcolor='white')
    dot.edge('review', 'compliance', label='A2A Handoff', color='#4ade80', style='bold', fontsize='10', fontcolor='white')
    dot.edge('compliance', 'decision', label='A2A Handoff', color='#4ade80', style='bold', fontsize='10', fontcolor='white')
    dot.edge('decision', 'end', label='Complete', fontsize='10', color='#ef4444', fontcolor='white')
    
    return dot

