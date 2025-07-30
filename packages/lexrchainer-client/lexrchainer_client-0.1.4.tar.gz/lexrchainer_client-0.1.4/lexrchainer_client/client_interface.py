"""
Client interface for interacting with the LexrChainer API.
"""

import os
import requests
from enum import Enum
from typing import List, Dict, Any, Optional
from lexrchainer_client.models import (
    ModelInfo, FunctionDefinition, ValidationError, ConversationMedium, UserCreate, ClientConversationMessageRequest, WorkflowCreateRequest, WorkflowRunCreateRequest, RunWorkflowRequest, SendMessageRequest,
    TaskCreateRequest, TaskUpdateRequest, TaskListCreateRequest, TaskListTemplateCreateRequest, Task, TaskList, TaskListTemplate, AgentCreate, AgentUpdate, ToolCredentialsCreate, ToolCredentialsUpdate, Message
)
from lexrchainer_client.config import get_settings

class ClientMode(Enum):
    """Enum for client mode configuration."""
    SERVER = "server"  # Direct method calls
    CLIENT = "client"  # API calls

class ClientConfig:
    """Configuration for the client interface."""
    
    def __init__(self):
        self.mode = os.getenv("LEXRCHAINER_MODE", ClientMode.CLIENT.value)
        self.api_key = os.getenv("LEXRCHAINER_API_KEY")
        self.jwt_token = os.getenv("LEXRCHAINER_JWT_TOKEN")
        self.base_url = os.getenv("LEXRCHAINER_API_URL")
        
    @property
    def headers(self) -> Dict[str, str]:
        """Get the headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        elif self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"
        return headers

class ClientInterface:
    """Interface for making API calls to the LexrChainer API."""
    
    def __init__(self, config: Optional[ClientConfig] = None):
        self.config = config or ClientConfig()
        self._available_tools = None
        self._available_models = None
    
    def _get_available_tools(self) -> List[FunctionDefinition]:
        """Get available tools from the server."""
        if self._available_tools is None:
            response = requests.get(
                f"{self.config.base_url}/agent/tools",
                headers=self.config.headers
            )
            response.raise_for_status()
            self._available_tools = response.json()
        return self._available_tools
    
    def _get_available_models(self) -> List[ModelInfo]:
        """Get available models from the server."""
        if self._available_models is None:
            response = requests.get(
                f"{self.config.base_url}/agent/models",
                headers=self.config.headers
            )
            response.raise_for_status()
            self._available_models = response.json()
        return self._available_models
    
    def validate_model(self, model_name: str) -> None:
        """Validate that the model exists in the model repository.
        
        Args:
            model_name: The name of the model to validate
            
        Raises:
            ValidationError: If the model is not found in the repository
        """
        if "lexr/" in model_name:
            available_models = get_settings().available_models
            if not any(model == model_name for model in available_models):
                raise ValidationError(f"Model '{model_name}' not found in model repository")
    
    def validate_tool(self, tool_name: str) -> None:
        """Validate that the tool exists in the tool repository.
        
        Args:
            tool_name: The name of the tool to validate
            
        Raises:
            ValidationError: If the tool is not found in the repository
        """
        available_tools = get_settings().available_tools
        if not any(tool == tool_name for tool in available_tools):
            raise ValidationError(f"Tool '{tool_name}' not found in tool repository")
    
    def send_message(self, conversation_id: str, messages: List[Any], recepient_id: str = None, streaming: bool = False) -> Any:
        """Send a message to a conversation.
        
        Args:
            conversation_id: The ID of the conversation
            messages: The messages to send
            streaming: Whether to stream the response. If True, returns a response object
                     that can be iterated over for SSE events. If False, returns JSON response.
            
        Returns:
            If streaming=False: The JSON response from the conversation
            If streaming=True: The raw response object that can be iterated over for SSE events
        """
        client_conversation_message_request = ClientConversationMessageRequest(
            sender_id="",
            messages=messages,
            streaming=streaming,
            recepient_id=recepient_id
        )
        response = requests.post(
            f"{self.config.base_url}/conversation/{conversation_id}/send_message",
            headers=self.config.headers,
            json=client_conversation_message_request.model_dump(),
            stream=streaming  # Enable streaming for SSE
        )
        response.raise_for_status()
        
        if not streaming:
            return response.json()
        return response  # Return raw response for SSE streaming
    
    def create_conversation(self, request: Any) -> Dict[str, Any]:
        """Create a new conversation.
        
        Args:
            request: The conversation creation request
            
        Returns:
            The created conversation details
        """
        response = requests.post(
            f"{self.config.base_url}/conversation/",
            headers=self.config.headers,
            json=request.dict()
        )
        response.raise_for_status()
        return response.json()
    
    def create_user(self, request: UserCreate) -> Any:
        """Create a new user.
        
        Args:
            request: The user creation request
            
        Returns:
            The created user details
        """
        #print(f"create_user: {request.model_dump()}")
        response = requests.post(
            f"{self.config.base_url}/user/",
            headers=self.config.headers,
            json=request.model_dump()
        )
        response.raise_for_status()
        return response.json()

    # User API endpoints
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get a user by ID."""
        response = requests.get(
            f"{self.config.base_url}/user/id/{user_id}",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a user."""
        response = requests.put(
            f"{self.config.base_url}/user/id/{user_id}",
            headers=self.config.headers,
            json=user_data
        )
        response.raise_for_status()
        return response.json()

    def delete_user(self, user_id: str) -> None:
        """Delete a user."""
        response = requests.delete(
            f"{self.config.base_url}/user/id/{user_id}",
            headers=self.config.headers
        )
        response.raise_for_status()

    def list_users(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List users."""
        response = requests.get(
            f"{self.config.base_url}/user?skip={skip}&limit={limit}",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def get_current_user(self) -> Dict[str, Any]:
        """Get the current user."""
        response = requests.get(
            f"{self.config.base_url}/user/self",
            headers=self.config.headers
        )
        print(response.headers)
        print(response.text)
        response.raise_for_status()
        return response.json()

    # Organization API endpoints
    def create_organization(self, org_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new organization."""
        response = requests.post(
            f"{self.config.base_url}/organization",
            headers=self.config.headers,
            json=org_data
        )
        response.raise_for_status()
        return response.json()

    def update_organization(self, org_id: str, org_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an organization."""
        response = requests.put(
            f"{self.config.base_url}/organization/{org_id}",
            headers=self.config.headers,
            json=org_data
        )
        response.raise_for_status()
        return response.json()

    # Workspace API endpoints
    def create_workspace(self, workspace_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workspace."""
        response = requests.post(
            f"{self.config.base_url}/workspace",
            headers=self.config.headers,
            json=workspace_data
        )
        response.raise_for_status()
        return response.json()

    def get_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """Get a workspace by ID."""
        response = requests.get(
            f"{self.config.base_url}/workspace/{workspace_id}",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def update_workspace(self, workspace_id: str, workspace_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a workspace."""
        response = requests.put(
            f"{self.config.base_url}/workspace/{workspace_id}",
            headers=self.config.headers,
            json=workspace_data
        )
        response.raise_for_status()
        return response.json()

    def delete_workspace(self, workspace_id: str) -> None:
        """Delete a workspace."""
        response = requests.delete(
            f"{self.config.base_url}/workspace/{workspace_id}",
            headers=self.config.headers
        )
        response.raise_for_status()

    def list_workspaces(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List workspaces."""
        response = requests.get(
            f"{self.config.base_url}/workspace?skip={skip}&limit={limit}",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def list_workspace_members(self, workspace_id: str) -> List[Dict[str, Any]]:
        """List members of a workspace."""
        response = requests.get(
            f"{self.config.base_url}/workspace/{workspace_id}/members",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def add_workspace_member(self, workspace_id: str, member_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a member to a workspace."""
        response = requests.post(
            f"{self.config.base_url}/workspace/{workspace_id}/members",
            headers=self.config.headers,
            json=member_data
        )
        response.raise_for_status()
        return response.json()

    def remove_workspace_member(self, workspace_id: str, user_id: str) -> None:
        """Remove a member from a workspace."""
        response = requests.delete(
            f"{self.config.base_url}/workspace/{workspace_id}/members/{user_id}",
            headers=self.config.headers
        )
        response.raise_for_status()

    # Chain API endpoints
    def create_chain(self, chain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new chain."""
        response = requests.post(
            f"{self.config.base_url}/chain",
            headers=self.config.headers,
            json=chain_data
        )
        response.raise_for_status()
        return response.json()

    def get_chain(self, chain_id: str) -> Dict[str, Any]:
        """Get a chain by ID."""
        response = requests.get(
            f"{self.config.base_url}/chain/{chain_id}",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def update_chain(self, chain_id: str, chain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a chain."""
        response = requests.put(
            f"{self.config.base_url}/chain/{chain_id}",
            headers=self.config.headers,
            json=chain_data
        )
        response.raise_for_status()
        return response.json()

    def delete_chain(self, chain_id: str) -> None:
        """Delete a chain."""
        response = requests.delete(
            f"{self.config.base_url}/chain/{chain_id}",
            headers=self.config.headers
        )
        response.raise_for_status()

    def list_chains(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List chains."""
        response = requests.get(
            f"{self.config.base_url}/chain?skip={skip}&limit={limit}",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def trigger_chain(self, chain_id: str, trigger_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger a chain execution."""
        response = requests.post(
            f"{self.config.base_url}/chain/{chain_id}/trigger",
            headers=self.config.headers,
            json=trigger_data
        )
        response.raise_for_status()
        return response.json()

    def schedule_chain(self, chain_id: str, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a chain execution."""
        response = requests.post(
            f"{self.config.base_url}/chain/{chain_id}/schedule",
            headers=self.config.headers,
            json=schedule_data
        )
        response.raise_for_status()
        return response.json()

    # Conversation API endpoints
    def add_conversation_member(self, conversation_id: str, user_id: str, role: str) -> Dict[str, Any]:
        """Add a member to a conversation."""
        response = requests.post(
            f"{self.config.base_url}/conversation/{conversation_id}/add_member",
            headers=self.config.headers,
            json={"user_id": user_id, "role": role}
        )
        response.raise_for_status()
        return response.json()

    def remove_conversation_member(self, conversation_id: str, user_id: str) -> Dict[str, Any]:
        """Remove a member from a conversation."""
        response = requests.post(
            f"{self.config.base_url}/conversation/{conversation_id}/remove_member",
            headers=self.config.headers,
            json={"user_id": user_id}
        )
        response.raise_for_status()
        return response.json()

    def get_conversation_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get messages from a conversation."""
        response = requests.post(
            f"{self.config.base_url}/conversation/{conversation_id}/get_messages",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def send_message_to_agent(self, agent_id: str, message_data: ClientConversationMessageRequest, streaming: bool = False) -> Any:
        """Send a message to a specific agent.
        
        Args:
            agent_id: The id of the agent to send the message to
            message_data: The message data to send
            streaming: Whether to stream the response. If True, returns a response object
                     that can be iterated over for SSE events. If False, returns JSON response.
            
        Returns:
            If streaming=False: The JSON response from the agent
            If streaming=True: The raw response object that can be iterated over for SSE events
        """
        response = requests.post(
            f"{self.config.base_url}/conversation/{agent_id}/message",
            headers=self.config.headers,
            json=message_data.model_dump(),
            stream=streaming  # Enable streaming for SSE
        )
        response.raise_for_status()
        
        if not streaming:
            return response.json()
        return response  # Return raw response for SSE streaming

    def send_public_agent_message(self, agent_name: str, message_data: Dict[str, Any], streaming: bool = False) -> Any:
        """Send a message to a public agent.
        
        Args:
            agent_name: The name of the public agent to send the message to
            message_data: The message data to send
            streaming: Whether to stream the response. If True, returns a response object
                     that can be iterated over for SSE events. If False, returns JSON response.
            
        Returns:
            If streaming=False: The JSON response from the public agent
            If streaming=True: The raw response object that can be iterated over for SSE events
        """
        response = requests.post(
            f"{self.config.base_url}/conversation/public/{agent_name}/message",
            headers=self.config.headers,
            json=message_data,
            stream=streaming  # Enable streaming for SSE
        )
        response.raise_for_status()
        
        if not streaming:
            return response.json()
        return response  # Return raw response for SSE streaming

    def get_agents(self) -> List[Dict[str, Any]]:
        """Get all available agents.
        
        Returns:
            List of agent information dictionaries
        """
        response = requests.get(
            f"{self.config.base_url}/agent",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def update_agent(self, agent_id: str, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing agent.
        
        Args:
            agent_id: The ID of the agent to update
            agent_data: The updated agent data
            
        Returns:
            Updated agent information
        """
        response = requests.patch(
            f"{self.config.base_url}/agent/{agent_id}",
            headers=self.config.headers,
            json=agent_data
        )
        response.raise_for_status()
        return response.json()

    def get_agent_conversations(self, agent_id: str, medium: ConversationMedium) -> List[str]:
        """Get all conversations for an agent with a specific medium.
        
        Args:
            agent_id: The ID of the agent
            medium: The conversation medium to filter by
            
        Returns:
            List of conversation IDs
        """
        response = requests.post(
            f"{self.config.base_url}/{agent_id}/conversations",
            headers=self.config.headers,
            params={"medium": medium.value}
        )
        response.raise_for_status()
        return response.json()

    # --- Agent API Endpoints ---
    def create_agent(self, request: 'AgentCreate') -> dict:
        """
        Create a new agent.
        Args:
            request: AgentCreate model instance
        Returns:
            The created agent user details (UserResponse)
        """
        response = requests.post(
            f"{self.config.base_url}/agent/",
            headers=self.config.headers,
            json=request.model_dump()
        )
        response.raise_for_status()
        return response.json()

    def update_agent(self, agent_id: str, request: 'AgentUpdate') -> dict:
        """
        Update an existing agent.
        Args:
            agent_id: The ID of the agent to update
            request: AgentUpdate model instance
        Returns:
            Updated agent user details (UserResponse)
        """
        response = requests.patch(
            f"{self.config.base_url}/agent/{agent_id}",
            headers=self.config.headers,
            json=request.model_dump()
        )
        response.raise_for_status()
        return response.json()

    def delete_agent(self, agent_id: str) -> None:
        """
        Delete an agent.
        Args:
            agent_id: The ID of the agent to delete
        """
        response = requests.delete(
            f"{self.config.base_url}/agent/{agent_id}",
            headers=self.config.headers
        )
        response.raise_for_status()

    def get_agents(self) -> list:
        """
        Get all available agents.
        Returns:
            List of agent user details (UserResponse)
        """
        response = requests.get(
            f"{self.config.base_url}/agent/",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def get_available_tools(self) -> list:
        """
        Get all available tools from the tool repository.
        Returns:
            List of FunctionDefinition dicts
        """
        response = requests.get(
            f"{self.config.base_url}/agent/tools",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def get_available_models(self) -> list:
        """
        Get all available models from the model repository.
        Returns:
            List of ModelInfo dicts
        """
        response = requests.get(
            f"{self.config.base_url}/agent/models",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def create_tool_credentials(self, request: 'ToolCredentialsCreate') -> dict:
        """
        Create tool credentials for an agent tool.
        Args:
            request: ToolCredentialsCreate model instance
        Returns:
            ToolCredentialsResponse dict
        """
        response = requests.post(
            f"{self.config.base_url}/agent/tool-credentials",
            headers=self.config.headers,
            json=request.model_dump()
        )
        response.raise_for_status()
        return response.json()

    def get_tool_credentials(self, tool_id: str) -> dict:
        """
        Get tool credentials for a specific tool.
        Args:
            tool_id: The ID of the tool
        Returns:
            ToolCredentialsResponse dict
        """
        response = requests.get(
            f"{self.config.base_url}/agent/tool-credentials/{tool_id}",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def list_tool_credentials(self) -> list:
        """
        List all tool credentials for the organization.
        Returns:
            List of ToolCredentialsResponse dicts
        """
        response = requests.get(
            f"{self.config.base_url}/agent/tool-credentials",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def update_tool_credentials(self, tool_id: str, request: 'ToolCredentialsUpdate') -> dict:
        """
        Update tool credentials for a specific tool.
        Args:
            tool_id: The ID of the tool
            request: ToolCredentialsUpdate model instance
        Returns:
            ToolCredentialsResponse dict
        """
        response = requests.patch(
            f"{self.config.base_url}/agent/tool-credentials/{tool_id}",
            headers=self.config.headers,
            json=request.model_dump()
        )
        response.raise_for_status()
        return response.json()

    def delete_tool_credentials(self, tool_id: str) -> None:
        """
        Delete tool credentials for a specific tool.
        Args:
            tool_id: The ID of the tool
        """
        response = requests.delete(
            f"{self.config.base_url}/agent/tool-credentials/{tool_id}",
            headers=self.config.headers
        )
        response.raise_for_status()

    # --- Conversation API: All Endpoints ---
    def add_conversation_member(self, conversation_id: str, user_id: str, role: str) -> dict:
        response = requests.post(
            f"{self.config.base_url}/conversation/{conversation_id}/add_member",
            headers=self.config.headers,
            json={"user_id": user_id, "role": role}
        )
        response.raise_for_status()
        return response.json()

    def remove_conversation_member(self, conversation_id: str, user_id: str) -> dict:
        response = requests.post(
            f"{self.config.base_url}/conversation/{conversation_id}/remove_member",
            headers=self.config.headers,
            json={"user_id": user_id}
        )
        response.raise_for_status()
        return response.json()

    def receive_conversation_message(self, conversation_id: str, message_request: dict) -> dict:
        response = requests.post(
            f"{self.config.base_url}/conversation/{conversation_id}/receive_message",
            headers=self.config.headers,
            json=message_request
        )
        response.raise_for_status()
        return response.json()

    def submit_conversation_message(self, conversation_id: str, message_request: dict) -> dict:
        response = requests.post(
            f"{self.config.base_url}/conversation/{conversation_id}/submit_message",
            headers=self.config.headers,
            json=message_request
        )
        response.raise_for_status()
        return response.json()

    def send_conversation_message(self, conversation_id: str, message_request: dict, streaming: bool = False) -> any:
        response = requests.post(
            f"{self.config.base_url}/conversation/{conversation_id}/send_message",
            headers=self.config.headers,
            json=message_request,
            stream=streaming
        )
        response.raise_for_status()
        if not streaming:
            return response.json()
        return response

    def get_conversation_messages(self, conversation_id: str) -> list:
        response = requests.post(
            f"{self.config.base_url}/conversation/{conversation_id}/get_messages",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def get_conversation_messages_v2(self, conversation_id: str, limit: int = 10, offset: int = 0) -> list:
        response = requests.get(
            f"{self.config.base_url}/conversation/{conversation_id}/messages?limit={limit}&offset={offset}",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def get_public_conversation_messages(self, conversation_id: str, limit: int = 10, offset: int = 0) -> list:
        response = requests.get(
            f"{self.config.base_url}/conversation/public/{conversation_id}/messages?limit={limit}&offset={offset}",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def send_public_agent_message(self, agent_name: str, message_request: dict, streaming: bool = False) -> any:
        response = requests.post(
            f"{self.config.base_url}/conversation/public/{agent_name}/message",
            headers=self.config.headers,
            json=message_request,
            stream=streaming
        )
        response.raise_for_status()
        if not streaming:
            return response.json()
        return response

    def get_agent_conversations(self, agent_id: str, medium: str) -> list:
        response = requests.get(
            f"{self.config.base_url}/conversation/{agent_id}/conversations?medium={medium}",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    # --- Knowledgebase API ---
    def create_knowledgebase(self, request: dict) -> dict:
        response = requests.post(
            f"{self.config.base_url}/knowledgebase/",
            headers=self.config.headers,
            json=request
        )
        response.raise_for_status()
        return response.json()

    def update_knowledgebase(self, kb_id: str, request: dict) -> dict:
        response = requests.put(
            f"{self.config.base_url}/knowledgebase/{kb_id}",
            headers=self.config.headers,
            json=request
        )
        response.raise_for_status()
        return response.json()

    def mark_knowledgebase_public(self, kb_id: str, is_public: bool) -> dict:
        response = requests.patch(
            f"{self.config.base_url}/knowledgebase/{kb_id}/public",
            headers=self.config.headers,
            json={"is_public": is_public}
        )
        response.raise_for_status()
        return response.json()

    def mark_knowledgebase_open(self, kb_id: str, is_open: bool) -> dict:
        response = requests.patch(
            f"{self.config.base_url}/knowledgebase/{kb_id}/open",
            headers=self.config.headers,
            json={"is_open": is_open}
        )
        response.raise_for_status()
        return response.json()

    def create_corpus(self, request: dict) -> dict:
        response = requests.post(
            f"{self.config.base_url}/knowledgebase/corpus",
            headers=self.config.headers,
            json=request
        )
        response.raise_for_status()
        return response.json()

    def update_corpus(self, corpus_id: str, request: dict) -> dict:
        response = requests.put(
            f"{self.config.base_url}/knowledgebase/corpus/{corpus_id}",
            headers=self.config.headers,
            json=request
        )
        response.raise_for_status()
        return response.json()

    def upload_document_to_corpus(self, corpus_id: str, request: dict) -> dict:
        response = requests.post(
            f"{self.config.base_url}/knowledgebase/corpus/{corpus_id}/upload",
            headers=self.config.headers,
            json=request
        )
        response.raise_for_status()
        return response.json()

    def search_knowledgebase(self, kb_id: str, request: dict) -> dict:
        response = requests.post(
            f"{self.config.base_url}/knowledgebase/{kb_id}/search",
            headers=self.config.headers,
            json=request
        )
        response.raise_for_status()
        return response.json()

    def search_corpus(self, corpus_id: str, request: dict) -> dict:
        response = requests.post(
            f"{self.config.base_url}/knowledgebase/corpus/{corpus_id}/search",
            headers=self.config.headers,
            json=request
        )
        response.raise_for_status()
        return response.json()

    def get_document_segments(self, kb_id: str, document_id: str) -> dict:
        response = requests.get(
            f"{self.config.base_url}/knowledgebase/{kb_id}/documents/{document_id}/segments",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def delete_document(self, kb_id: str, document_id: str) -> dict:
        response = requests.delete(
            f"{self.config.base_url}/knowledgebase/{kb_id}/documents/{document_id}",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    # --- Org API ---
    def create_organization(self, org_data: dict) -> dict:
        response = requests.post(
            f"{self.config.base_url}/org/",
            headers=self.config.headers,
            json=org_data
        )
        response.raise_for_status()
        return response.json()

    def update_organization(self, org_id: str, org_data: dict) -> dict:
        response = requests.put(
            f"{self.config.base_url}/org/{org_id}",
            headers=self.config.headers,
            json=org_data
        )
        response.raise_for_status()
        return response.json()

    # --- Webhooks API ---
    def create_webhook(self, request: dict) -> dict:
        response = requests.post(
            f"{self.config.base_url}/webhooks/",
            headers=self.config.headers,
            json=request
        )
        response.raise_for_status()
        return response.json()

    def list_webhooks(self) -> list:
        response = requests.get(
            f"{self.config.base_url}/webhooks/",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def get_webhook(self, webhook_id: str) -> dict:
        response = requests.get(
            f"{self.config.base_url}/webhooks/{webhook_id}",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def update_webhook(self, webhook_id: str, request: dict) -> dict:
        response = requests.put(
            f"{self.config.base_url}/webhooks/{webhook_id}",
            headers=self.config.headers,
            json=request
        )
        response.raise_for_status()
        return response.json()

    def delete_webhook(self, webhook_id: str) -> dict:
        response = requests.delete(
            f"{self.config.base_url}/webhooks/{webhook_id}",
            headers=self.config.headers
        )
        response.raise_for_status()

    def regenerate_webhook_token(self, webhook_id: str) -> dict:
        response = requests.post(
            f"{self.config.base_url}/webhooks/{webhook_id}/regenerate-token",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    # --- Workflow API ---
    def create_workflow(self, request: WorkflowCreateRequest) -> dict:
        """
        Create a workflow. Only accepts WorkflowCreateRequest (Pydantic model).
        """
        if not isinstance(request, WorkflowCreateRequest):
            raise TypeError("request must be a WorkflowCreateRequest instance")
        response = requests.post(
            f"{self.config.base_url}/workflow/",
            headers=self.config.headers,
            json=request.model_dump()
        )
        response.raise_for_status()
        return response.json()

    def create_workflow_run(self, request: WorkflowRunCreateRequest) -> dict:
        """
        Create a workflow run. Only accepts WorkflowRunCreateRequest (Pydantic model).
        """
        if not isinstance(request, WorkflowRunCreateRequest):
            raise TypeError("request must be a WorkflowRunCreateRequest instance")
        response = requests.post(
            f"{self.config.base_url}/workflow/run",
            headers=self.config.headers,
            json=request.model_dump()
        )
        response.raise_for_status()
        return response.json()

    def trigger_workflow(self, request: RunWorkflowRequest) -> dict:
        """
        Trigger a workflow. Only accepts RunWorkflowRequest (Pydantic model).
        """
        if not isinstance(request, RunWorkflowRequest):
            raise TypeError("request must be a RunWorkflowRequest instance")
        response = requests.post(
            f"{self.config.base_url}/workflow/trigger",
            headers=self.config.headers,
            json=request.model_dump()
        )
        response.raise_for_status()
        return response.json()

    def send_message_to_default_conversation(self, request: SendMessageRequest) -> dict:
        """
        Send a message to the default workflow conversation. Only accepts SendMessageRequest (Pydantic model).
        """
        if not isinstance(request, SendMessageRequest):
            raise TypeError("request must be a SendMessageRequest instance")
        response = requests.post(
            f"{self.config.base_url}/workflow/send_message",
            headers=self.config.headers,
            json=request.model_dump()
        )
        response.raise_for_status()
        return response.json()

    # --- Task API endpoints ---
    def create_tasklist(self, request: TaskListCreateRequest) -> TaskList:
        response = requests.post(
            f"{self.config.base_url}/task/tasklist",
            headers=self.config.headers,
            json=request.model_dump(mode="json")
        )
        response.raise_for_status()
        return TaskList(**response.json())

    def get_tasklist(self, tasklist_id: str) -> TaskList:
        response = requests.get(
            f"{self.config.base_url}/task/tasklist/{tasklist_id}",
            headers=self.config.headers
        )
        response.raise_for_status()
        return TaskList(**response.json())

    def get_all_tasks(self, tasklist_id: str) -> list[Task]:
        response = requests.get(
            f"{self.config.base_url}/task/tasklist/{tasklist_id}/tasks",
            headers=self.config.headers
        )
        response.raise_for_status()
        return [Task(**t) for t in response.json()]

    def create_task(self, request: TaskCreateRequest) -> Task:
        response = requests.post(
            f"{self.config.base_url}/task/task",
            headers=self.config.headers,
            json=request.model_dump(mode="json")
        )
        response.raise_for_status()
        return Task(**response.json())

    def get_task(self, task_id: str) -> Task:
        response = requests.get(
            f"{self.config.base_url}/task/task/{task_id}",
            headers=self.config.headers
        )
        response.raise_for_status()
        return Task(**response.json())

    def update_task(self, task_id: str, request: TaskUpdateRequest) -> Task:
        response = requests.patch(
            f"{self.config.base_url}/task/task/{task_id}",
            headers=self.config.headers,
            json=request.model_dump(exclude_unset=True, mode="json")
        )
        response.raise_for_status()
        return Task(**response.json())

    def delete_task(self, task_id: str) -> None:
        response = requests.delete(
            f"{self.config.base_url}/task/task/{task_id}",
            headers=self.config.headers
        )
        response.raise_for_status()

    def create_tasklist_template(self, request: TaskListTemplateCreateRequest) -> TaskListTemplate:
        response = requests.post(
            f"{self.config.base_url}/task/tasklist/template",
            headers=self.config.headers,
            json=request.model_dump()
        )
        response.raise_for_status()
        return TaskListTemplate(**response.json())

    def search_tasklist_templates(self, search_term: str) -> list[TaskListTemplate]:
        response = requests.get(
            f"{self.config.base_url}/task/tasklist/template/search",
            headers=self.config.headers,
            params={"search_term": search_term}
        )
        response.raise_for_status()
        return [TaskListTemplate(**tpl) for tpl in response.json()]