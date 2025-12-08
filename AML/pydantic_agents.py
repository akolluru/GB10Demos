"""
Pydantic-based AML Agents using A2A and MCP
Replaces CrewAI with direct Ollama calls and structured outputs.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Any, Optional
import ollama
import pandas as pd
from agent_framework import BaseAgent, AgentRegistry, MessageType
from mcp_client import MCPClient
from rag_agent import RAGAgent


# Pydantic models for structured outputs
class L1ScreeningResult(BaseModel):
    """Structured output for Level 1 screening."""
    score: float = Field(description="Risk score from 0-100", ge=0, le=100)
    explanation: str = Field(description="Brief explanation of the risk assessment")


class L2ScreeningResult(BaseModel):
    """Structured output for Level 2 screening."""
    score: float = Field(description="Risk score from 0-100", ge=0, le=100)
    risk_level: str = Field(description="Risk level: Low, Medium, or High")
    risk_factors: str = Field(description="Key risk factors identified")
    recommendations: str = Field(description="Recommended actions")
    explanation: str = Field(description="Detailed explanation and reasoning")
    
    @field_validator('risk_factors', 'recommendations', mode='before')
    @classmethod
    def convert_list_to_string(cls, v):
        """Convert lists to strings if needed."""
        if isinstance(v, list):
            # If list of dicts, extract values
            if v and isinstance(v[0], dict):
                return '; '.join([str(item.get('description', item)) for item in v])
            # If list of strings, join them
            return '; '.join(str(item) for item in v)
        return str(v) if v is not None else ""


class RAGAnalysisResult(BaseModel):
    """Structured output for RAG analysis."""
    score: float = Field(description="Risk score from 0-100", ge=0, le=100)
    risk_level: str = Field(description="Risk level: Low, Medium, or High")
    regulations: str = Field(description="Relevant regulations cited")
    typologies: str = Field(description="Money laundering typologies identified")
    risk_factors: str = Field(description="Risk factors based on knowledge base")
    recommendations: str = Field(description="Recommended actions")
    explanation: str = Field(description="Detailed explanation with context")


class L1ScreeningAgent(BaseAgent):
    """Level 1 Screening Agent using Pydantic and A2A."""
    
    def __init__(self, model_name: str = "mistral:latest", registry: Optional[AgentRegistry] = None):
        super().__init__("l1_agent", "Level 1 Screening Agent")
        self.model_name = model_name
        if registry:
            registry.register(self)
    
    def screen(self, transaction: pd.Series) -> L1ScreeningResult:
        """Perform Level 1 screening."""
        prompt = f"""
You are an AML screening expert. Analyze this transaction for potential money laundering risks.
Focus on basic red flags like:
1. High-value transactions (>$100,000)
2. Transactions to high-risk countries
3. Suspicious transaction patterns

Transaction Details:
ID: {transaction['transaction_id']}
Amount: {transaction['amount']} {transaction['currency']}
Sender: {transaction['sender_name']} ({transaction['sender_account']})
Receiver: {transaction['receiver_name']} ({transaction['receiver_account']})
Type: {transaction['transaction_type']}
Country: {transaction['country']}
Purpose: {transaction['purpose']}

Provide a risk score (0-100) and a brief explanation of any concerns.
Respond in JSON format with "score" (number) and "explanation" (string).
"""
        
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                format="json"
            )
            result_text = response['response']
            
            # Parse JSON response
            import json
            result_dict = json.loads(result_text)
            return L1ScreeningResult(**result_dict)
        except Exception as e:
            # Fallback to default values
            return L1ScreeningResult(
                score=0.0,
                explanation=f"Error in screening: {str(e)}"
            )
    
    def handle_message(self, message) -> Optional[Any]:
        """Handle A2A messages."""
        if message.message_type == MessageType.REQUEST:
            if message.payload.get("action") == "screen":
                transaction = pd.Series(message.payload.get("transaction", {}))
                result = self.screen(transaction)
                return self._create_response(message, result.dict())
        return None
    
    def _create_response(self, original_message, payload: Dict):
        """Create a response message."""
        from agent_framework import AgentMessage
        from datetime import datetime
        import uuid
        
        return AgentMessage(
            message_id=str(uuid.uuid4()),
            sender_id=self.agent_id,
            receiver_id=original_message.sender_id,
            message_type=MessageType.RESPONSE,
            payload=payload,
            timestamp=datetime.now().isoformat(),
            correlation_id=original_message.message_id
        )


class L2ScreeningAgent(BaseAgent):
    """Level 2 Screening Agent using Pydantic and A2A."""
    
    def __init__(self, model_name: str = "deepseek-r1:14b", registry: Optional[AgentRegistry] = None):
        super().__init__("l2_agent", "Level 2 Screening Agent")
        self.model_name = model_name
        if registry:
            registry.register(self)
    
    def screen(self, transaction: pd.Series, related_transactions: List[pd.Series]) -> L2ScreeningResult:
        """Perform Level 2 screening."""
        # Format related transactions
        related_tx_text = "\n".join([
            f"TX {i+1}: {tx['transaction_id']} - {tx['amount']} {tx['currency']} - {tx['country']}"
            for i, tx in enumerate(related_transactions)
        ])
        
        prompt = f"""
You are an AML expert performing enhanced due diligence. Analyze this transaction and its related transactions
for complex money laundering patterns. Consider:
1. Transaction patterns and relationships
2. Customer behavior analysis
3. Geographic risk factors
4. Transaction purpose analysis
5. Structuring or layering indicators

Main Transaction:
ID: {transaction['transaction_id']}
Amount: {transaction['amount']} {transaction['currency']}
Sender: {transaction['sender_name']} ({transaction['sender_account']})
Receiver: {transaction['receiver_name']} ({transaction['receiver_account']})
Type: {transaction['transaction_type']}
Country: {transaction['country']}
Purpose: {transaction['purpose']}

Related Transactions:
{related_tx_text}

Provide a detailed analysis with:
1. Risk Score (0-100)
2. Risk Level (Low/Medium/High)
3. Key Risk Factors
4. Recommended Actions
5. Detailed explanation and reasoning

Respond in JSON format with: "score" (number), "risk_level" (string: Low/Medium/High), "risk_factors" (string - comma or semicolon separated list), "recommendations" (string - comma or semicolon separated list), "explanation" (string).
Note: risk_factors and recommendations must be strings, not arrays. If you have multiple items, join them with semicolons.
"""
        
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                format="json"
            )
            result_text = response['response']
            
            # Parse JSON response
            import json
            result_dict = json.loads(result_text)
            
            # Convert lists to strings if needed (before Pydantic validation)
            if isinstance(result_dict.get('risk_factors'), list):
                risk_factors_list = result_dict['risk_factors']
                if risk_factors_list and isinstance(risk_factors_list[0], dict):
                    result_dict['risk_factors'] = '; '.join([str(item.get('description', item)) for item in risk_factors_list])
                else:
                    result_dict['risk_factors'] = '; '.join(str(item) for item in risk_factors_list)
            
            if isinstance(result_dict.get('recommendations'), list):
                recommendations_list = result_dict['recommendations']
                if recommendations_list and isinstance(recommendations_list[0], dict):
                    result_dict['recommendations'] = '; '.join([str(item.get('description', item)) for item in recommendations_list])
                else:
                    result_dict['recommendations'] = '; '.join(str(item) for item in recommendations_list)
            
            return L2ScreeningResult(**result_dict)
        except Exception as e:
            # Fallback to default values
            return L2ScreeningResult(
                score=0.0,
                risk_level="Unknown",
                risk_factors=f"Error: {str(e)}",
                recommendations="Please review manually",
                explanation=f"Error in screening: {str(e)}"
            )
    
    def handle_message(self, message) -> Optional[Any]:
        """Handle A2A messages."""
        if message.message_type == MessageType.REQUEST:
            if message.payload.get("action") == "screen":
                transaction = pd.Series(message.payload.get("transaction", {}))
                related = [pd.Series(tx) for tx in message.payload.get("related_transactions", [])]
                result = self.screen(transaction, related)
                return self._create_response(message, result.dict())
        return None
    
    def _create_response(self, original_message, payload: Dict):
        """Create a response message."""
        from agent_framework import AgentMessage
        from datetime import datetime
        import uuid
        
        return AgentMessage(
            message_id=str(uuid.uuid4()),
            sender_id=self.agent_id,
            receiver_id=original_message.sender_id,
            message_type=MessageType.RESPONSE,
            payload=payload,
            timestamp=datetime.now().isoformat(),
            correlation_id=original_message.message_id
        )


class RAGAnalysisAgent(BaseAgent):
    """RAG Analysis Agent using Pydantic, MCP, and A2A."""
    
    def __init__(self, model_name: str = "mistral:latest", 
                 mcp_client: Optional[MCPClient] = None,
                 registry: Optional[AgentRegistry] = None):
        super().__init__("rag_agent", "RAG Analysis Agent")
        self.model_name = model_name
        self.mcp_client = mcp_client or MCPClient()
        self.rag_agent = RAGAgent(mcp_client=self.mcp_client, lazy_init=True)
        if registry:
            registry.register(self)
    
    def analyze(self, transaction: Dict[str, Any]) -> RAGAnalysisResult:
        """Perform RAG analysis with MCP."""
        # Use existing RAG agent
        result = self.rag_agent.analyze_transaction(transaction)
        
        # Convert to Pydantic model
        return RAGAnalysisResult(
            score=result.get('score', 0.0),
            risk_level=result.get('risk_level', 'Unknown'),
            regulations=result.get('regulations', 'N/A'),
            typologies=result.get('typologies', 'N/A'),
            risk_factors=result.get('risk_factors', 'N/A'),
            recommendations=result.get('recommendations', 'N/A'),
            explanation=result.get('explanation', 'N/A')
        )
    
    def handle_message(self, message) -> Optional[Any]:
        """Handle A2A messages."""
        if message.message_type == MessageType.REQUEST:
            if message.payload.get("action") == "analyze":
                transaction = message.payload.get("transaction", {})
                result = self.analyze(transaction)
                return self._create_response(message, result.dict())
        return None
    
    def _create_response(self, original_message, payload: Dict):
        """Create a response message."""
        from agent_framework import AgentMessage
        from datetime import datetime
        import uuid
        
        return AgentMessage(
            message_id=str(uuid.uuid4()),
            sender_id=self.agent_id,
            receiver_id=original_message.sender_id,
            message_type=MessageType.RESPONSE,
            payload=payload,
            timestamp=datetime.now().isoformat(),
            correlation_id=original_message.message_id
        )


class ScreeningAgents:
    """Orchestrator for AML screening agents using A2A."""
    
    def __init__(self, model_name_l1: str = "mistral:latest",
                 model_name_l2: str = "deepseek-r1:14b",
                 mcp_client: Optional[MCPClient] = None):
        self.model_name_l1 = model_name_l1
        self.model_name_l2 = model_name_l2
        self.mcp_client = mcp_client or MCPClient()
        
        # Create agent registry
        self.registry = AgentRegistry()
        
        # Initialize agents
        self.l1_agent = L1ScreeningAgent(model_name_l1, self.registry)
        self.l2_agent = L2ScreeningAgent(model_name_l2, self.registry)
        self.rag_agent = RAGAnalysisAgent("mistral:latest", self.mcp_client, self.registry)
    
    def level1_screening(self, transaction: pd.Series) -> tuple[float, str]:
        """Perform Level 1 screening."""
        result = self.l1_agent.screen(transaction)
        return result.score, result.explanation
    
    def level2_screening(self, transaction: pd.Series, related_transactions: List[pd.Series]) -> Dict:
        """Perform Level 2 screening."""
        result = self.l2_agent.screen(transaction, related_transactions)
        return result.dict()
    
    def rag_analysis(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Perform RAG analysis."""
        result = self.rag_agent.analyze(transaction)
        return result.dict()
    
    def collaborative_screening(self, transaction: pd.Series, related_transactions: List[pd.Series]) -> Dict:
        """Perform collaborative screening using A2A."""
        tx_dict = transaction.to_dict()
        
        # L1 screening
        l1_result = self.level1_screening(transaction)
        
        # RAG analysis
        rag_result = self.rag_analysis(tx_dict)
        
        # L2 screening with context
        l2_result = self.level2_screening(transaction, related_transactions)
        
        return {
            'l1': {'score': l1_result[0], 'explanation': l1_result[1]},
            'rag': rag_result,
            'l2': l2_result,
            'final_score': max(l1_result[0], l2_result['score'], rag_result['score'])
        }

