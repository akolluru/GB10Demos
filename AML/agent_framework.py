"""
Agent-to-Agent (A2A) Communication Framework
Enables agents to communicate and collaborate on AML screening tasks.
"""
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
import uuid
from datetime import datetime

class MessageType(Enum):
    """Types of messages agents can send."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"

@dataclass
class AgentMessage:
    """Message structure for A2A communication."""
    message_id: str
    sender_id: str
    receiver_id: str
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: str
    correlation_id: Optional[str] = None  # For request-response matching
    
    def to_dict(self) -> Dict:
        """Convert message to dictionary."""
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "message_type": self.message_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id
        }

class AgentRegistry:
    """Registry for managing agents and routing messages."""
    def __init__(self):
        self.agents: Dict[str, 'BaseAgent'] = {}
        self.message_history: List[AgentMessage] = []
    
    def register(self, agent: 'BaseAgent'):
        """Register an agent."""
        self.agents[agent.agent_id] = agent
        agent.registry = self
    
    def send_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Send a message to an agent and get response."""
        self.message_history.append(message)
        
        if message.receiver_id not in self.agents:
            error_msg = AgentMessage(
                message_id=str(uuid.uuid4()),
                sender_id="registry",
                receiver_id=message.sender_id,
                message_type=MessageType.ERROR,
                payload={"error": f"Agent {message.receiver_id} not found"},
                timestamp=datetime.now().isoformat(),
                correlation_id=message.message_id
            )
            return error_msg
        
        receiver = self.agents[message.receiver_id]
        response = receiver.handle_message(message)
        return response
    
    def broadcast(self, message: AgentMessage, exclude_sender: bool = True):
        """Broadcast a message to all agents."""
        responses = []
        for agent_id, agent in self.agents.items():
            if exclude_sender and agent_id == message.sender_id:
                continue
            response = agent.handle_message(message)
            if response:
                responses.append(response)
        return responses

class BaseAgent:
    """Base class for all AML agents."""
    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.registry: Optional[AgentRegistry] = None
        self.message_queue: List[AgentMessage] = []
    
    def send_to_agent(self, receiver_id: str, payload: Dict[str, Any], 
                     message_type: MessageType = MessageType.REQUEST,
                     correlation_id: Optional[str] = None) -> Optional[AgentMessage]:
        """Send a message to another agent."""
        if not self.registry:
            raise RuntimeError("Agent not registered with AgentRegistry")
        
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            payload=payload,
            timestamp=datetime.now().isoformat(),
            correlation_id=correlation_id
        )
        
        return self.registry.send_message(message)
    
    def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle incoming messages. Override in subclasses."""
        self.message_queue.append(message)
        return None
    
    def process_queue(self):
        """Process queued messages."""
        while self.message_queue:
            message = self.message_queue.pop(0)
            self.handle_message(message)

