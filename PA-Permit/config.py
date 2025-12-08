"""
Configuration module for PA Permit Automation System
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Ollama Settings
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:latest")  # Using smaller model for better performance
    
    # Application Settings
    APP_TITLE = os.getenv("APP_TITLE", "PA Permit Automation System")
    APP_PORT = int(os.getenv("APP_PORT", "8501"))
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
    
    # MCP Server Settings
    MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "localhost")
    MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "5000"))
    
    # Permit Types
    PERMIT_TYPES = [
        "Environmental Permit - Air Quality",
        "Environmental Permit - Water Quality",
        "Environmental Permit - Land Use",
        "Storage Tank Permit",
        "Residual Waste Permit",
        "Pesticide Usage Permit",
        "Agricultural Permit - Hemp Cultivation",
        "Agricultural Permit - Hemp Processing",
    ]
    
    # Agent Roles
    AGENT_ROLES = {
        "intake": "Permit Intake Specialist",
        "review": "Technical Review Officer",
        "compliance": "Compliance Verification Agent",
        "decision": "Permit Decision Authority"
    }

