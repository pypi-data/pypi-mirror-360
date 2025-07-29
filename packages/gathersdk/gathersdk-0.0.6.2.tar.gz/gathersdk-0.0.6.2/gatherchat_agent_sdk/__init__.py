"""
GatherChat Agent SDK

A Python SDK for building agents that integrate with GatherChat.
"""

from .agent import (
    BaseAgent,
    AgentContext,
    UserContext,
    ChatContext,
    MessageContext,
    AgentResponse,
    AgentError
)
from .client import AgentClient, run_agent
from .auth import SimpleAuth
from .router import MessageRouter
from .crypto import AgentCrypto

__version__ = "0.0.1"

__all__ = [
    # Simple interface (pydantic-ai style)
    "MessageRouter",
    
    # Core classes
    "BaseAgent",
    "AgentClient",
    "SimpleAuth",
    "AgentCrypto",
    
    # Context models
    "AgentContext",
    "UserContext", 
    "ChatContext",
    "MessageContext",
    
    # Helper classes
    "AgentResponse",
    "AgentError",
    
    # Convenience functions
    "run_agent"
]