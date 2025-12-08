"""
RAG Agent with Vector Search and External Document Retrieval
Uses FAISS for vector similarity search and MCP for external document access.
"""
import json
import numpy as np
from typing import Dict, List, Any, Optional
from pathlib import Path
import ollama
from agent_framework import BaseAgent, AgentMessage, MessageType
from mcp_client import MCPClient

try:
    import faiss
    FAISS_AVAILABLE = True
except (ImportError, ModuleNotFoundError) as e:
    FAISS_AVAILABLE = False
    # Don't print warning on every import - it's handled gracefully
    if "numpy.distutils" not in str(e):
        print(f"Warning: FAISS not available: {e}")

class RAGAgent(BaseAgent):
    """RAG Agent with vector search and MCP integration."""
    
    def __init__(self, agent_id: str = "rag_agent", model_name: str = "mistral:latest",
                 mcp_client: Optional[MCPClient] = None, lazy_init: bool = True):
        super().__init__(agent_id, "RAG Agent")
        self.model_name = model_name
        self.mcp_client = mcp_client or MCPClient()
        self.knowledge_base = {}
        self.vector_index = None
        self.document_vectors = []
        self.document_metadata = []
        self._vector_index_built = False
        self._load_knowledge_base()
        if not lazy_init:
            self._build_vector_index()
    
    def _load_knowledge_base(self):
        """Load knowledge base from JSON files."""
        rag_dir = Path("rag_data")
        for file in rag_dir.glob("*.json"):
            with open(file, 'r') as f:
                self.knowledge_base[file.stem] = json.load(f)
    
    def _get_embeddings(self, text: str) -> np.ndarray:
        """Get embeddings for text using Ollama."""
        try:
            response = ollama.embeddings(model=self.model_name, prompt=text)
            return np.array(response['embedding'], dtype=np.float32)
        except Exception as e:
            print(f"Embedding error: {e}")
            # Fallback to random embedding if Ollama doesn't support embeddings
            return np.random.rand(768).astype(np.float32)
    
    def _build_vector_index(self):
        """Build FAISS index for vector similarity search."""
        if self._vector_index_built:
            return  # Already built, skip
        
        if not FAISS_AVAILABLE:
            # Don't print every time, just mark as built
            self._vector_index_built = True
            return
        
        try:
            # Get embeddings for all knowledge base chunks
            chunks = []
            metadata = []
            
            # Chunk knowledge base
            for kb_name, kb_data in self.knowledge_base.items():
                chunks.extend(self._chunk_knowledge(kb_data, kb_name))
            
            if not chunks:
                self._vector_index_built = True
                return
            
            # Get embeddings (limit to avoid slow initialization)
            embeddings = []
            max_chunks = 50  # Limit chunks for faster initialization
            for i, chunk in enumerate(chunks[:max_chunks]):
                try:
                    embedding = self._get_embeddings(chunk['text'])
                    embeddings.append(embedding)
                    metadata.append({
                        'chunk_id': i,
                        'source': chunk['source'],
                        'text': chunk['text']
                    })
                except Exception as e:
                    print(f"Error getting embedding for chunk {i}: {e}")
                    continue
            
            if not embeddings:
                self._vector_index_built = True
                return
            
            # Determine dimension
            dim = len(embeddings[0])
            
            # Create FAISS index
            self.vector_index = faiss.IndexFlatL2(dim)
            embeddings_array = np.array(embeddings).astype('float32')
            self.vector_index.add(embeddings_array)
            self.document_metadata = metadata
            
            self._vector_index_built = True
            print(f"Built FAISS index with {len(embeddings)} vectors")
        except Exception as e:
            print(f"Error building vector index: {e}")
            self._vector_index_built = True  # Mark as attempted to avoid retrying
    
    def _chunk_knowledge(self, kb_data: Dict, source: str) -> List[Dict]:
        """Chunk knowledge base data into searchable pieces."""
        chunks = []
        
        # Chunk regulations
        if "regulations" in kb_data:
            for reg in kb_data["regulations"]:
                chunk_text = f"Regulation: {reg.get('name', '')}\n"
                chunk_text += f"Requirements: {' '.join(reg.get('requirements', []))}\n"
                chunk_text += f"Risk Indicators: {' '.join(reg.get('risk_indicators', []))}"
                chunks.append({"text": chunk_text, "source": source})
        
        # Chunk typologies
        if "typologies" in kb_data:
            for typo in kb_data["typologies"]:
                chunk_text = f"Typology: {typo.get('name', '')}\n"
                chunk_text += f"Description: {typo.get('description', '')}\n"
                chunk_text += f"Indicators: {' '.join(typo.get('indicators', []))}"
                chunks.append({"text": chunk_text, "source": source})
        
        # Chunk countries
        if "high_risk_countries" in kb_data:
            for country in kb_data.get("high_risk_countries", []):
                chunk_text = f"Country: {country.get('name', '')}\n"
                chunk_text += f"Risk Level: {country.get('risk_level', '')}\n"
                chunk_text += f"Risk Factors: {' '.join(country.get('risk_factors', []))}"
                chunks.append({"text": chunk_text, "source": source})
        
        return chunks
    
    def _retrieve_relevant_chunks(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve relevant chunks using vector similarity."""
        # Lazy build vector index if not built yet
        if not self._vector_index_built:
            self._build_vector_index()
        
        if not self.vector_index or not FAISS_AVAILABLE:
            # Fallback to simple text matching
            return self._simple_text_search(query, top_k)
        
        try:
            query_embedding = self._get_embeddings(query)
            query_vector = np.array([query_embedding]).astype('float32')
            
            # Search
            distances, indices = self.vector_index.search(query_vector, top_k)
            
            results = []
            for idx, dist in zip(indices[0], distances[0]):
                if idx < len(self.document_metadata):
                    result = self.document_metadata[idx].copy()
                    result['similarity_score'] = float(1 / (1 + dist))  # Convert distance to similarity
                    results.append(result)
            
            return results
        except Exception as e:
            print(f"Vector search error: {e}")
            return self._simple_text_search(query, top_k)
    
    def _simple_text_search(self, query: str, top_k: int) -> List[Dict]:
        """Simple text-based search fallback."""
        query_lower = query.lower()
        results = []
        
        for kb_name, kb_data in self.knowledge_base.items():
            kb_str = json.dumps(kb_data).lower()
            if query_lower in kb_str:
                results.append({
                    "text": f"Match from {kb_name}",
                    "source": kb_name,
                    "similarity_score": 0.7
                })
        
        return results[:top_k]
    
    def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle incoming messages."""
        if message.message_type == MessageType.REQUEST:
            payload = message.payload
            action = payload.get("action")
            
            if action == "analyze_transaction":
                result = self.analyze_transaction(payload.get("transaction", {}))
                return AgentMessage(
                    message_id=str(uuid.uuid4()),
                    sender_id=self.agent_id,
                    receiver_id=message.sender_id,
                    message_type=MessageType.RESPONSE,
                    payload={"result": result},
                    timestamp=datetime.now().isoformat(),
                    correlation_id=message.message_id
                )
            elif action == "retrieve_context":
                context = self.retrieve_context(payload.get("query", ""))
                return AgentMessage(
                    message_id=str(uuid.uuid4()),
                    sender_id=self.agent_id,
                    receiver_id=message.sender_id,
                    message_type=MessageType.RESPONSE,
                    payload={"context": context},
                    timestamp=datetime.now().isoformat(),
                    correlation_id=message.message_id
                )
        
        return None
    
    def retrieve_context(self, query: str) -> Dict[str, Any]:
        """Retrieve context using vector search and external documents."""
        # Vector search in knowledge base
        kb_chunks = self._retrieve_relevant_chunks(query, top_k=3)
        
        # Get external documents via MCP
        external_docs = self.mcp_client.retrieve_external_documents(query, max_results=3)
        
        # Get MCP context
        mcp_context = self.mcp_client.get_context(query, context_type="rag")
        
        return {
            "knowledge_base_chunks": kb_chunks,
            "external_documents": external_docs,
            "mcp_context": mcp_context,
            "query": query
        }
    
    def analyze_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze transaction with RAG-enhanced context."""
        # Build query from transaction
        query = f"Transaction: {transaction.get('transaction_id', '')} "
        query += f"Amount: {transaction.get('amount', 0)} "
        query += f"Country: {transaction.get('country', '')} "
        query += f"Type: {transaction.get('transaction_type', '')}"
        
        # Retrieve context
        context = self.retrieve_context(query)
        
        # Format context for LLM
        context_str = self._format_context(context)
        
        # Build prompt
        tx_str = f"""
Transaction Details:
ID: {transaction.get('transaction_id', '')}
Amount: {transaction.get('amount', 0)} {transaction.get('currency', '')}
Sender: {transaction.get('sender_name', '')} ({transaction.get('sender_account', '')})
Receiver: {transaction.get('receiver_name', '')} ({transaction.get('receiver_account', '')})
Type: {transaction.get('transaction_type', '')}
Country: {transaction.get('country', '')}
Purpose: {transaction.get('purpose', '')}
"""
        
        prompt = f"""
You are an AML expert analyzing a transaction for potential money laundering risks.
Use the following retrieved context to inform your analysis:

{context_str}

Analyze this transaction:
{tx_str}

Provide a detailed analysis with:
1. Risk Score (0-100)
2. Risk Level (Low/Medium/High)
3. Applicable Regulations (cite sources from context)
4. Potential Typologies (cite sources from context)
5. Risk Factors
6. Recommended Actions
7. A detailed explanation and reasoning, including which retrieved documents or knowledge base entries contributed to your assessment.

Format your response as:
SCORE: [number]
RISK_LEVEL: [Low/Medium/High]
REGULATIONS: [list with citations]
TYPOLOGIES: [list with citations]
RISK_FACTORS: [list of factors]
RECOMMENDATIONS: [list of actions]
EXPLANATION: [detailed explanation with citations]
Please answer ONLY in the above format. Do not add any explanation or text outside this format.
"""
        
        # Get LLM response
        response = ollama.generate(model=self.model_name, prompt=prompt)
        response_text = response['response']
        
        # Parse response
        import re
        try:
            score = float(re.search(r'SCORE:\s*([0-9.]+)', response_text).group(1))
            risk_level = re.search(r'RISK_LEVEL:\s*([\w/]+)', response_text).group(1)
            regulations = re.search(r'REGULATIONS:\s*(.*?)TYPOLOGIES:', response_text, re.DOTALL).group(1).strip()
            typologies = re.search(r'TYPOLOGIES:\s*(.*?)RISK_FACTORS:', response_text, re.DOTALL).group(1).strip()
            risk_factors = re.search(r'RISK_FACTORS:\s*(.*?)RECOMMENDATIONS:', response_text, re.DOTALL).group(1).strip()
            recommendations = re.search(r'RECOMMENDATIONS:\s*(.*?)EXPLANATION:', response_text, re.DOTALL).group(1).strip()
            explanation = re.search(r'EXPLANATION:\s*(.*)', response_text, re.DOTALL).group(1).strip()
        except Exception as e:
            score = 0
            risk_level = "Unknown"
            regulations = "Error in parsing LLM response"
            typologies = "Error in parsing LLM response"
            risk_factors = "Error in parsing LLM response"
            recommendations = "Error in parsing LLM response"
            explanation = f"Error in parsing LLM response: {e}"
        
        return {
            'score': score,
            'risk_level': risk_level,
            'regulations': regulations,
            'typologies': typologies,
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'explanation': explanation,
            'context_used': {
                'kb_chunks': len(context['knowledge_base_chunks']),
                'external_docs': len(context['external_documents']),
                'mcp_enabled': self.mcp_client.use_mcp
            }
        }
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format retrieved context for LLM prompt."""
        formatted = []
        
        # Knowledge base chunks
        if context.get('knowledge_base_chunks'):
            formatted.append("=== Knowledge Base Context ===")
            for chunk in context['knowledge_base_chunks']:
                formatted.append(f"Source: {chunk.get('source', 'unknown')}")
                formatted.append(f"Content: {chunk.get('text', '')}")
                formatted.append(f"Relevance: {chunk.get('similarity_score', 0):.2f}")
                formatted.append("")
        
        # External documents
        if context.get('external_documents'):
            formatted.append("=== External Documents (via MCP) ===")
            for doc in context['external_documents']:
                formatted.append(f"Document: {doc.get('name', 'unknown')}")
                formatted.append(f"Path: {doc.get('path', 'unknown')}")
                formatted.append(f"Type: {doc.get('type', 'unknown')}")
                formatted.append("")
        
        # MCP context
        if context.get('mcp_context'):
            mcp_ctx = context['mcp_context']
            formatted.append("=== MCP Context ===")
            formatted.append(f"Source: {mcp_ctx.get('source', 'unknown')}")
            formatted.append(f"Context: {mcp_ctx.get('context', '')}")
            formatted.append("")
        
        return "\n".join(formatted)

# Import uuid and datetime for AgentMessage
import uuid
from datetime import datetime

