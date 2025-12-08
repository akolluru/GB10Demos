"""
MCP Server for Context Management
Model Context Protocol server for managing agent context and state
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import threading


class MCPServer:
    """
    Model Context Protocol Server for managing context across agents
    Handles context storage, retrieval, and agent-to-agent handoff
    """
    
    def __init__(self):
        self.contexts: Dict[str, Dict[str, Any]] = {}
        self.application_states: Dict[str, Dict[str, Any]] = {}
        self.agent_history: Dict[str, List[Dict[str, Any]]] = {}
        self.lock = threading.Lock()
        
    def create_context(self, application_id: str, initial_data: Dict[str, Any]) -> str:
        """Create a new context for an application"""
        with self.lock:
            self.contexts[application_id] = {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "data": initial_data,
                "current_agent": None,
                "status": "initiated"
            }
            self.application_states[application_id] = {
                "stage": "intake",
                "decisions": [],
                "flags": [],
                "documents": []
            }
            self.agent_history[application_id] = []
            return application_id
    
    def set_application_state(self, application_id: str, stage: str, 
                            status: str, agent: str) -> bool:
        """Update application state and current agent"""
        with self.lock:
            if application_id in self.contexts:
                self.contexts[application_id]["status"] = status
                self.contexts[application_id]["current_agent"] = agent
                self.application_states[application_id]["stage"] = stage
                self.application_states[application_id]["updated_at"] = datetime.now().isoformat()
                return True
            return False
    
    def a2a_handoff(self, application_id: str, from_agent: str, 
                   to_agent: str, context_update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Agent-to-Agent (A2A) handoff with context transfer
        Transfers context and control from one agent to another
        """
        with self.lock:
            if application_id not in self.contexts:
                return {"success": False, "error": "Application not found"}
            
            # Record handoff in history
            handoff_record = {
                "timestamp": datetime.now().isoformat(),
                "from_agent": from_agent,
                "to_agent": to_agent,
                "context_update": context_update,
                "status": "completed"
            }
            
            self.agent_history[application_id].append(handoff_record)
            
            # Update context
            self.contexts[application_id]["data"].update(context_update)
            self.contexts[application_id]["current_agent"] = to_agent
            self.contexts[application_id]["updated_at"] = datetime.now().isoformat()
            
            # Return context for new agent
            return {
                "success": True,
                "application_id": application_id,
                "context": self.contexts[application_id]["data"],
                "state": self.application_states[application_id],
                "history": self.agent_history[application_id]
            }
    
    def add_decision(self, application_id: str, agent: str, 
                    decision: str, rationale: str) -> bool:
        """Add a decision made by an agent"""
        with self.lock:
            if application_id in self.application_states:
                self.application_states[application_id]["decisions"].append({
                    "timestamp": datetime.now().isoformat(),
                    "agent": agent,
                    "decision": decision,
                    "rationale": rationale
                })
                return True
            return False
    
    def add_flag(self, application_id: str, flag_type: str, 
                description: str, severity: str = "medium") -> bool:
        """Add a compliance or review flag"""
        with self.lock:
            if application_id in self.application_states:
                self.application_states[application_id]["flags"].append({
                    "timestamp": datetime.now().isoformat(),
                    "type": flag_type,
                    "description": description,
                    "severity": severity,
                    "resolved": False
                })
                return True
            return False
    
    def get_application_history(self, application_id: str) -> List[Dict[str, Any]]:
        """Get complete history of agent interactions"""
        return self.agent_history.get(application_id, [])
    
    def get_application_state(self, application_id: str) -> Optional[Dict[str, Any]]:
        """Get current application state"""
        return self.application_states.get(application_id)


# Global MCP Server instance
mcp_server = MCPServer()

