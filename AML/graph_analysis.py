import networkx as nx
import pandas as pd
from typing import List, Dict, Tuple
from pyvis.network import Network
import streamlit as st
import tempfile
import os

class TransactionGraph:
    def __init__(self):
        self.G = nx.Graph()
        self.transaction_nodes = set()
        self.entity_nodes = set()
        
    def build_graph(self, transactions: pd.DataFrame, force_rebuild: bool = False):
        """Build a graph from transaction data."""
        # Skip if already built and not forcing rebuild
        if not force_rebuild and len(self.G.nodes()) > 0:
            return
        
        self.G.clear()
        self.transaction_nodes.clear()
        self.entity_nodes.clear()
        
        # Add nodes and edges
        for _, tx in transactions.iterrows():
            # Add transaction node
            tx_id = f"TX_{tx['transaction_id']}"
            self.G.add_node(tx_id, 
                          type='transaction',
                          amount=tx['amount'],
                          currency=tx['currency'],
                          timestamp=tx['timestamp'],
                          risk_score=tx['risk_score'])
            self.transaction_nodes.add(tx_id)
            
            # Add sender node
            sender_id = f"SENDER_{tx['sender_account']}"
            if sender_id not in self.entity_nodes:
                self.G.add_node(sender_id,
                              type='entity',
                              name=tx['sender_name'],
                              account=tx['sender_account'])
                self.entity_nodes.add(sender_id)
            
            # Add receiver node
            receiver_id = f"RECEIVER_{tx['receiver_account']}"
            if receiver_id not in self.entity_nodes:
                self.G.add_node(receiver_id,
                              type='entity',
                              name=tx['receiver_name'],
                              account=tx['receiver_account'])
                self.entity_nodes.add(receiver_id)
            
            # Add edges
            self.G.add_edge(sender_id, tx_id, type='sent')
            self.G.add_edge(tx_id, receiver_id, type='received')
        
        # Only print if building for first time
        if not force_rebuild:
            print(f"Graph built with {len(self.G.nodes())} nodes and {len(self.G.edges())} edges")
            print(f"Transaction nodes: {len(self.transaction_nodes)}")
            print(f"Entity nodes: {len(self.entity_nodes)}")
    
    def get_related_transactions(self, transaction_id: str, max_depth: int = 2) -> List[str]:
        """Get related transactions within max_depth hops."""
        tx_node = f"TX_{transaction_id}"
        if tx_node not in self.G:
            return []
        
        related = set()
        for node in nx.single_source_shortest_path_length(self.G, tx_node, max_depth).keys():
            if node.startswith('TX_'):
                related.add(node[3:])  # Remove 'TX_' prefix
        return list(related)
    
    def get_entity_network(self, entity_id: str, max_depth: int = 2) -> Dict:
        """Get the network of entities connected to a given entity."""
        entity_node = f"SENDER_{entity_id}" if entity_id.startswith('SENDER_') else f"RECEIVER_{entity_id}"
        if entity_node not in self.G:
            return {}
        
        subgraph = nx.ego_graph(self.G, entity_node, radius=max_depth)
        return {
            'nodes': list(subgraph.nodes()),
            'edges': list(subgraph.edges())
        }
    
    def get_risk_clusters(self) -> List[List[str]]:
        """Identify clusters of high-risk transactions."""
        # Get all transaction nodes
        tx_nodes = [n for n in self.G.nodes() if n.startswith('TX_')]
        
        # Calculate risk scores for each transaction
        risk_scores = {n: self.G.nodes[n]['risk_score'] for n in tx_nodes}
        
        # Find connected components
        components = list(nx.connected_components(self.G))
        
        # Filter high-risk clusters
        high_risk_clusters = []
        for component in components:
            tx_in_component = [n for n in component if n.startswith('TX_')]
            if tx_in_component:
                avg_risk = sum(risk_scores[tx] for tx in tx_in_component) / len(tx_in_component)
                if avg_risk > 70:  # High-risk threshold
                    high_risk_clusters.append([tx[3:] for tx in tx_in_component])  # Remove 'TX_' prefix
        
        return high_risk_clusters
    
    def visualize_network(self, transaction_id: str = None, max_depth: int = 1) -> str:
        """Create an interactive visualization of the transaction network with up to 1 hop (direct connections)."""
        try:
            # Check if graph has any nodes
            if len(self.G.nodes()) == 0:
                # Create a simple message HTML file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as tmp:
                    message_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>No Graph Data</title>
                        <style>
                            body {{
                                background-color: #000000;
                                color: #ffffff;
                                font-family: Arial, sans-serif;
                                padding: 20px;
                            }}
                            h2 {{
                                color: #ffffff;
                            }}
                            ul {{
                                color: #ffffff;
                            }}
                        </style>
                    </head>
                    <body>
                        <h2>No Graph Data Available</h2>
                        <p>The transaction graph is empty. This might be because:</p>
                        <ul>
                            <li>No transactions have been loaded</li>
                            <li>The graph hasn't been built yet</li>
                            <li>There are no connections in the data</li>
                        </ul>
                    </body>
                    </html>
                    """
                    tmp.write(message_html)
                    return tmp.name
            
            net = Network(height="800px", width="100%", bgcolor="#000000", font_color="white")
            
            # If transaction_id is provided, show its neighborhood
            if transaction_id:
                tx_node = f"TX_{transaction_id}"
                if tx_node in self.G:
                    subgraph = nx.ego_graph(self.G, tx_node, radius=max_depth)
                else:
                    subgraph = self.G
            else:
                subgraph = self.G
            
            # Add nodes with dark theme colors
            for node in subgraph.nodes():
                if node.startswith('TX_'):
                    # Transaction node - use lighter blue for visibility on black
                    net.add_node(node,
                               label=f"TX {node[3:]}",
                               title=f"Amount: {self.G.nodes[node]['amount']} {self.G.nodes[node]['currency']}<br>Risk: {self.G.nodes[node]['risk_score']}",
                               color='#4a9eff',
                               font={'color': 'white', 'size': 14})
                else:
                    # Entity node - use orange/amber for visibility on black
                    net.add_node(node,
                               label=self.G.nodes[node]['name'],
                               title=f"Account: {self.G.nodes[node]['account']}",
                               color='#ffa500',
                               font={'color': 'white', 'size': 14})
            
            # Add edges with white color for visibility
            for edge in subgraph.edges():
                net.add_edge(edge[0], edge[1], 
                           title=self.G.edges[edge]['type'],
                           color='#ffffff')
            
            # Set dark theme options
            net.set_options("""
            {
              "nodes": {
                "font": {
                  "color": "white",
                  "size": 14
                },
                "borderWidth": 0
              },
              "edges": {
                "color": {
                  "color": "#ffffff",
                  "highlight": "#4a9eff"
                },
                "font": {
                  "color": "white",
                  "size": 12
                }
              },
              "physics": {
                "enabled": true,
                "stabilization": {
                  "enabled": true,
                  "iterations": 100
                }
              }
            }
            """)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as tmp:
                net.save_graph(tmp.name)
                
                # Read the generated HTML and modify it to remove borders
                with open(tmp.name, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Add CSS to remove all borders and spacing
                css_override = """
                <style>
                    * {
                        margin: 0 !important;
                        padding: 0 !important;
                        border: none !important;
                        box-sizing: border-box !important;
                    }
                    html, body {
                        margin: 0 !important;
                        padding: 0 !important;
                        border: none !important;
                        width: 100% !important;
                        height: 100% !important;
                        overflow: hidden !important;
                        background-color: #000000 !important;
                    }
                    #mynetworkid {
                        margin: 0 !important;
                        padding: 0 !important;
                        border: none !important;
                        outline: none !important;
                        width: 100% !important;
                        height: 100% !important;
                        background-color: #000000 !important;
                    }
                    iframe {
                        margin: 0 !important;
                        padding: 0 !important;
                        border: none !important;
                        outline: none !important;
                        display: block !important;
                    }
                    div {
                        margin: 0 !important;
                        padding: 0 !important;
                    }
                </style>
                """
                
                # Insert CSS before </head> or at the beginning of <body>
                if '</head>' in html_content:
                    html_content = html_content.replace('</head>', css_override + '</head>')
                elif '<body>' in html_content:
                    html_content = html_content.replace('<body>', '<body>' + css_override)
                else:
                    # If no head/body, add at the beginning
                    html_content = css_override + html_content
                
                # Write back the modified HTML
                with open(tmp.name, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                return tmp.name
        except Exception as e:
            # Create a simple error HTML file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as tmp:
                error_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Graph Visualization Error</title>
                    <style>
                        body {{
                            background-color: #000000;
                            color: #ffffff;
                            font-family: Arial, sans-serif;
                            padding: 20px;
                        }}
                        h2 {{
                            color: #ffffff;
                        }}
                    </style>
                </head>
                <body>
                    <h2>Graph Visualization Error</h2>
                    <p>Error creating graph visualization: {str(e)}</p>
                    <p>This might be due to insufficient data or network issues.</p>
                </body>
                </html>
                """
                tmp.write(error_html)
                return tmp.name
    
    def get_risk_metrics(self) -> Dict:
        """Calculate risk metrics for the transaction network."""
        metrics = {
            'total_transactions': len(self.transaction_nodes),
            'total_entities': len(self.entity_nodes),
            'avg_risk_score': sum(self.G.nodes[n]['risk_score'] for n in self.transaction_nodes) / len(self.transaction_nodes),
            'high_risk_transactions': sum(1 for n in self.transaction_nodes if self.G.nodes[n]['risk_score'] > 70),
            'connected_components': nx.number_connected_components(self.G),
            'avg_clustering': nx.average_clustering(self.G),
            'density': nx.density(self.G)
        }
        return metrics 