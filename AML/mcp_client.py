"""
Model Context Protocol (MCP) Client
Provides MCP integration for RAG operations with external document retrieval.
"""
import json
import requests
from typing import Dict, List, Any, Optional
from pathlib import Path
import os

class MCPClient:
    """Client for Model Context Protocol operations."""
    
    def __init__(self, mcp_server_url: Optional[str] = None):
        """
        Initialize MCP client.
        
        Args:
            mcp_server_url: URL of MCP server. If None, uses local file-based context.
        """
        self.mcp_server_url = mcp_server_url or os.getenv("MCP_SERVER_URL")
        self.use_mcp = self.mcp_server_url is not None
    
    def get_context(self, query: str, context_type: str = "rag") -> Dict[str, Any]:
        """
        Get context from MCP server or local sources.
        
        Args:
            query: Query string for context retrieval
            context_type: Type of context (rag, regulation, typology, etc.)
        
        Returns:
            Dictionary with context information
        """
        if self.use_mcp:
            return self._get_context_from_mcp(query, context_type)
        else:
            return self._get_context_local(query, context_type)
    
    def _get_context_from_mcp(self, query: str, context_type: str) -> Dict[str, Any]:
        """Get context from MCP server."""
        try:
            response = requests.post(
                f"{self.mcp_server_url}/context",
                json={
                    "query": query,
                    "context_type": context_type,
                    "model": "mistral:latest"
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"MCP server error: {e}, falling back to local context")
            return self._get_context_local(query, context_type)
    
    def _get_context_local(self, query: str, context_type: str) -> Dict[str, Any]:
        """Get context from local sources (fallback)."""
        return {
            "query": query,
            "context_type": context_type,
            "source": "local",
            "context": f"Local context for: {query}"
        }
    
    def validate_document(self, document_path: str) -> Dict[str, Any]:
        """
        Validate external document through MCP.
        
        Args:
            document_path: Path to external document
        
        Returns:
            Validation result with document metadata
        """
        if self.use_mcp:
            try:
                with open(document_path, 'rb') as f:
                    files = {'document': f}
                    response = requests.post(
                        f"{self.mcp_server_url}/validate",
                        files=files,
                        timeout=30
                    )
                    response.raise_for_status()
                    return response.json()
            except Exception as e:
                return {
                    "valid": False,
                    "error": str(e),
                    "source": "mcp_error"
                }
        else:
            # Local validation
            path = Path(document_path)
            if path.exists():
                return {
                    "valid": True,
                    "path": str(path),
                    "size": path.stat().st_size,
                    "source": "local"
                }
            return {
                "valid": False,
                "error": "File not found",
                "source": "local"
            }
    
    def retrieve_external_documents(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve external documents relevant to query.
        
        Args:
            query: Search query
            max_results: Maximum number of results
        
        Returns:
            List of relevant documents
        """
        if self.use_mcp:
            try:
                response = requests.post(
                    f"{self.mcp_server_url}/retrieve",
                    json={
                        "query": query,
                        "max_results": max_results
                    },
                    timeout=15
                )
                response.raise_for_status()
                return response.json().get("documents", [])
            except Exception as e:
                print(f"MCP retrieval error: {e}")
                return []
        else:
            # Local document retrieval (from external_docs directory)
            return self._retrieve_local_documents(query, max_results)
    
    def _retrieve_local_documents(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Retrieve documents from local external_docs directory."""
        external_docs_dir = Path("external_docs")
        if not external_docs_dir.exists():
            return []
        
        documents = []
        for doc_file in external_docs_dir.glob("*"):
            if doc_file.is_file():
                documents.append({
                    "path": str(doc_file),
                    "name": doc_file.name,
                    "type": doc_file.suffix,
                    "relevance_score": 0.5  # Placeholder
                })
        
        return documents[:max_results]

