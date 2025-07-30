"""
Default configuration management for LexrChainer client.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from lexrchainer_client.models import ChainStepType, ChainStepFlowDirection, ChainStepFlowType, ChainStepFlowState, ChainStepResponseTreatment, ModelParams, ConversationTurnType, ConversationIterationEndCriteria

class ClientSettings(BaseModel):
    """Default settings for the LexrChainer client."""
    # Model defaults
    default_model: str = "azure/gpt-4o"
    default_system_prompt: str = "You are a helpful AI assistant."
    default_model_params: ModelParams = ModelParams(
        model=default_model,
        max_tokens=2048,
        temperature=0.7,
        top_p=1.0,
        top_k=40
    )
    
    # API defaults
    default_api_url: str = "http://localhost:8000"
    default_medium: str = "WHATSAPP"
    
    # Conversation defaults
    default_turn_type: str = ConversationTurnType.SEQUENTIAL
    default_iteration_end_criteria: str = ConversationIterationEndCriteria.PERPETUAL
    
    # Chain defaults
    default_chain_version: str = "0.0"
    default_step_type: str = ChainStepType.HIDDEN_TURN_USER
    default_flow_direction: str = ChainStepFlowDirection.TO_USER
    default_flow_type: str = ChainStepFlowType.AT_ONCE
    default_flow_state: str = ChainStepFlowState.CONTINUE
    default_response_treatment: str = ChainStepResponseTreatment.APPEND

    available_models: List[str] = ["lexr/gpt-4o", "lexr/o3-mini", "lexr/gpt-o4-mini"]
    available_tools: List[str] = ["SerpTool", "ScraperTool", "SequentialThinking", "TaskManagerTool", "LexrIndex", "AgentConversationTool"]

# Global settings instance
_settings = ClientSettings()

def get_settings() -> ClientSettings:
    """Get the current settings."""
    return _settings

def set_settings(settings: Dict[str, Any]) -> None:
    """Update the settings with new values.
    
    Args:
        settings: Dictionary of settings values to update
    """
    global _settings
    _settings = ClientSettings(**{**_settings.model_dump(), **settings})

def reset_settings() -> None:
    """Reset the settings to default values."""
    global _settings
    _settings = ClientSettings()

# Example usage:
"""
from lexrchainer.client.config import get_settings, set_settings

# Get current settings
settings = get_settings()

# Update specific values
set_settings({
    "default_model": "gpt-3.5-turbo",
    "default_system_prompt": "You are a specialized assistant.",
    "default_model_params": {
        "max_tokens": 1024,
        "temperature": 0.5
    }
})

# Reset to defaults
reset_settings()
""" 