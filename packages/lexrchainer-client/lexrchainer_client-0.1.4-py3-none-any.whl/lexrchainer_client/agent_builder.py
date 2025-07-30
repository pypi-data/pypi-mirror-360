"""
Client-side agent builder for LexrChainer.
"""

from typing import List, Dict, Any, Optional
from lexrchainer_client.models import (
    ChainMeta, ChainStepConfig, ChainConfig, ToolConfig,
    ChainStepType, ChainStepFlowDirection, ChainStepFlowType,
    ChainStepFlowState, ChainStepResponseTreatment,
    ModelParams, ModelConfig, Message, MessageRole, MessageContent, MessageType,
    UserCreate, CreateConversationRequest, UserType,
    ConversationMedium, ConversationTurnType, ConversationIterationEndCriteria,
    ConversationMemberRole, ConversationMember, ValidationError, ChainCreate,
    AgentCreate, AgentUpdate, ClientConversationMessageRequest
)
from .client_interface import ClientInterface, ClientConfig
from .config import get_settings
import json
from datetime import datetime

class AgentWrapper:
    """Wrapper class that manages an agent and its conversation."""
    
    def __init__(self, agent_user_id: str, conversation_id: str, client: Optional[ClientInterface] = None):
        self.agent_user_id = agent_user_id
        self.conversation_id = conversation_id
        self.client = client or ClientInterface()
    
    def send_message(self, message: str, streaming: bool = False) -> Any:
        """Send a message to the agent and get the response.
        
        Args:
            message: The message to send
            streaming: Whether to stream the response
            
        Returns:
            The agent's response
        """
        # Create message in the correct format
        messages = [Message(
            role=MessageRole.USER,
            content=message,
            entity_id=self.agent_user_id,
            conversation_id=self.conversation_id
        )]
        
        # Send the message and get response
        print(f"Sending message to agent: {self.agent_user_id}")
        response = self.client.send_message_to_agent(
            self.agent_user_id,
            ClientConversationMessageRequest(
                messages=messages,
                streaming=streaming,
                recepient_id=self.agent_user_id
            )
        )
        if streaming:
            for line in response.iter_lines():
                line = line.decode("utf-8")
                line = line.replace("data: ", "")
                if line:
                    _json = json.loads(line)
                    print(f"{datetime.now()} - Received event data: {_json}")

        return response

class MultiAgentWrapper:
    """Wrapper class that manages multiple agents in a conversation."""
    
    def __init__(self, agent_user_ids: List[str], conversation_id: str, client: Optional[ClientInterface] = None):
        self.agent_user_ids = agent_user_ids
        self.conversation_id = conversation_id
        self.client = client or ClientInterface()
    
    def send_message(self, message: str, streaming: bool = False) -> Any:
        """Send a message to the conversation and get responses from all agents.
        
        Args:
            message: The message to send
            streaming: Whether to stream the responses
            
        Returns:
            The responses from all agents
        """
        # Create message in the correct format
        messages = [Message(
            role=MessageRole.USER,
            content=message,
            entity_id=self.agent_user_ids[0],  # Use first agent as sender
            conversation_id=self.conversation_id
        )]
        
        # Send the message and get responses
        return self.client.send_message_to_agent(
            self.agent_user_ids[0],
            ClientConversationMessageRequest(
                messages=messages,
                streaming=streaming,
                recepient_id=self.agent_user_ids[0]
            )
        )

class AgentBuilder:
    """A simple yet powerful builder for creating agents."""
    
    def __init__(self, name: str, client: Optional[ClientInterface] = None):
        settings = get_settings()
        self.name = name
        self.description = ""
        self.system_prompt = settings.default_system_prompt
        self.model = settings.default_model
        self.model_params = settings.default_model_params
        self.tools: List[ToolConfig] = []
        self.models: List[ModelConfig] = []
        self.steps: List[ChainStepConfig] = []
        self.static_meta: Dict = {}
        self.client = client or ClientInterface()
        self.agent_id = None  # Store the agent ID after creation
    
    def _validate_model(self, model_name: str) -> None:
        """Validate that the model exists in the model repository.
        
        Args:
            model_name: The name of the model to validate
            
        Raises:
            ValidationError: If the model is not found in the repository
        """
        self.client.validate_model(model_name)
    
    def _validate_tool(self, tool_name: str) -> None:
        """Validate that the tool exists in the tool repository.
        
        Args:
            tool_name: The name of the tool to validate
            
        Raises:
            ValidationError: If the tool is not found in the repository
        """
        self.client.validate_tool(tool_name)
    
    def with_description(self, description: str) -> 'AgentBuilder':
        """Add a description to the agent.
        
        Args:
            description: The description of the agent
            
        Returns:
            self for method chaining
        """
        self.description = description
        return self
    
    def with_system_prompt(self, prompt: str) -> 'AgentBuilder':
        """Set the system prompt for the agent.
        
        Args:
            prompt: The system prompt to use
            
        Returns:
            self for method chaining
        """
        self.system_prompt = prompt
        return self
    
    def with_model(self, model: str, credentials: Dict=None, **model_params) -> 'AgentBuilder':
        """Set the model and its parameters for the agent.
        
        Args:
            model: The model name to use
            credentials: model credentials
            **model_params: Additional model parameters
            
        Returns:
            self for method chaining
            
        Raises:
            ValidationError: If the model is not found in the repository
        """
        # Validate the model exists
        self._validate_model(model)
        
        settings = get_settings()
        # convert **model_params to ModelParams
        try:
            model_params = ModelParams(**model_params)
        except Exception as e:
            model_params = self.model_params
        
        self.model = model
        self.model_params = model_params
        model_params.model = model
        self.models = [ModelConfig(
            name=model,
            credentials=credentials if credentials else {},
            params=model_params
        )]
        return self

    def with_tool(self, name: str, credentials: Dict[str, Any] = None) -> 'AgentBuilder':
        """Add a tool to the agent.
        
        Args:
            name: The name of the tool
            credentials: Optional credentials for the tool
            
        Returns:
            self for method chaining
            
        Raises:
            ValidationError: If the tool is not found in the repository
        """
        # Validate the tool exists
        self._validate_tool(name)
        
        self.tools.append(ToolConfig(
            name=name,
            credentials=credentials or {}
        ))
        return self
    
    def with_static_meta(self, meta: Dict) -> 'AgentBuilder':
        """Add static metadata to the agent.
        
        Args:
            meta: Dictionary of static metadata
            
        Returns:
            self for method chaining
        """
        self.static_meta = meta
        return self
    
    def add_step(self, 
                 name: str,
                 prompt: str,
                 model: str = None,
                 model_credentials: Dict[str, Any] = None,
                 model_params: Dict[str, Any] = None,
                 type: ChainStepType = ChainStepType.HIDDEN_TURN_USER,
                 flow: ChainStepFlowDirection = ChainStepFlowDirection.TO_USER,
                 flow_type: ChainStepFlowType = ChainStepFlowType.AT_ONCE,
                 flow_state: ChainStepFlowState = ChainStepFlowState.CONTINUE,
                 response_treatment: ChainStepResponseTreatment = ChainStepResponseTreatment.APPEND,
                 tool_use: bool = False,
                 **kwargs) -> 'AgentBuilder':
        """Add a step to the agent's chain.
        
        Args:
            name: Name of the step
            prompt: The prompt for this step
            model: The model to use for this step
            model_credentials: model credentials
            model_params: The parameters for the model
            type: Type of the step
            flow: Flow direction
            flow_type: Flow type
            flow_state: Flow state
            response_treatment: How to treat the response
            tool_use: Whether this step uses tools
            **kwargs: Additional step parameters
            
        Returns:
            self for method chaining
            
        Raises:
            ValidationError: If tool_use is True but no tools are configured
        """
        settings = get_settings()
        
        # Validate that tools are configured if tool_use is True
        if tool_use and not self.tools:
            raise ValidationError("Tool use is enabled but no tools are configured")
        
        # if model is set, use it, otherwise use the default model
        if model:
            if not model in [m.name for m in self.models]:
                # Add model to models list
                self.models.append(ModelConfig(
                    name=model,
                    credentials=model_credentials if model_credentials else {},
                    params=model_params
                ))
        elif self.models:
            model_params = self.models[-1].params
        else:
            model_params = self.model_params

        step = ChainStepConfig(
            name=name,
            id=f"step_{len(self.steps)}",
            description=f"Step {len(self.steps) + 1}",
            version=settings.default_chain_version,
            prompt=prompt,
            type=type or ChainStepType(settings.default_step_type),
            flow=flow or ChainStepFlowDirection(settings.default_flow_direction),
            flow_type=flow_type or ChainStepFlowType(settings.default_flow_type),
            flow_state=flow_state or ChainStepFlowState(settings.default_flow_state),
            response_treatment=response_treatment or ChainStepResponseTreatment(settings.default_response_treatment),
            tool_use=tool_use,
            model_params=model_params,
            **kwargs
        )
        self.steps.append(step)
        return self
    
    def load_agent(self, agent_id: str, conversation_id: str) -> 'AgentWrapper':
        agents = self.client.get_agents()
        # Find the agent with matching ID
        agent_info = None
        for agent in agents:
            if agent['id'] == agent_id:
                agent_info = agent
                break
                
        if not agent_info:
            raise ValidationError(f"Agent with ID {agent_id} not found")

        # Create and return an AgentWrapper instance
        return AgentWrapper(agent_id, conversation_id, self.client)
    

    def build(self) -> ChainConfig:
        """Build the agent configuration.
        
        Returns:
            A ChainConfig object that can be used to create an agent
            
        Raises:
            ValidationError: If required components are not properly configured
        """
        settings = get_settings()
        
        # Validate that a model is configured
        if not self.model:
            raise ValidationError("No model configured for the agent")
            
        # Validate that tools are configured if any step uses tools
        if any(step.tool_use for step in self.steps) and not self.tools:
            raise ValidationError("Some steps use tools but no tools are configured")
        
        # Create the chain meta
        chain_meta = ChainMeta(
            id=f"chain_{self.name.lower().replace(' ', '_')}",
            name=self.name,
            description=self.description,
            version=settings.default_chain_version,
            default_system_prompt=self.system_prompt,
            static_meta=self.static_meta,
            tools=self.tools,
            models=self.models,
            default_model_params=self.model_params
        )
        
        # If no steps were added, add a default step
        if not self.steps:
            self.add_step(
                name="Default Step",
                prompt=self.system_prompt,
                type=ChainStepType(settings.default_step_type),
                flow=ChainStepFlowDirection(settings.default_flow_direction)
            )
        
        # Create the chain config
        return ChainConfig(
            chain=chain_meta,
            steps=self.steps
        )
    
    def get_agents(self) -> List[Dict[str, Any]]:
        """Get all available agents.
        
        Returns:
            List of agent information dictionaries
        """
        return self.client.get_agents()

    def update_agent(self, agent_id: str) -> dict:
        """
        Update an existing agent with the current configuration.
        Args:
            agent_id: The ID of the agent to update
        Returns:
            Updated agent information
        Raises:
            ValidationError: If the agent configuration is invalid
        """
        # Build the chain config
        chain_config = self.build()
        agent_update_payload = AgentUpdate(
            agent_name=self.name,
            config=chain_config.chain
        )
        # Update the agent
        return self.client.update_agent(agent_id, agent_update_payload)

    def get_agent_conversations(self, medium: ConversationMedium) -> List[str]:
        """Get all conversations for this agent with a specific medium.
        
        Args:
            medium: The conversation medium to filter by
            
        Returns:
            List of conversation IDs
            
        Raises:
            ValidationError: If the agent ID is not set
        """
        if not self.agent_id:
            raise ValidationError("Agent ID not set. Create the agent first.")
            
        return self.client.get_agent_conversations(self.agent_id, medium)

    def create_agent(self, medium: ConversationMedium = None) -> AgentWrapper:
        """
        Create an agent user and start a conversation with it using the agent API endpoint.
        Args:
            medium: The conversation medium to use (ignored, as the API creates the gateway conversation)
        Returns:
            An AgentWrapper instance that manages the agent and conversation
        Raises:
            ValidationError: If the agent configuration is invalid
        """
        try:
            # Build the chain config
            chain_config = self.build()
            # Call the agent API endpoint via client_interface
            agent_create_payload = AgentCreate(
                agent_name=self.name,
                config=chain_config.chain
            )
            agent_user = self.client.create_agent(agent_create_payload)
            # Store the agent ID
            self.agent_id = agent_user["id"]
            # Use the gateway_conversation_id from the API response
            gateway_conversation_id = agent_user.get("gateway_conversation_id")
            if not gateway_conversation_id:
                raise ValidationError("No gateway_conversation_id returned from agent API.")
            return AgentWrapper(agent_user["id"], gateway_conversation_id, self.client)
        except Exception as e:
            raise ValidationError(f"Failed to create agent: {str(e)}")

class MultiAgentBuilder:
    """Builder for creating multiple agents and managing their conversation."""
    
    def __init__(self, client: Optional[ClientInterface] = None):
        self.agents: List[AgentBuilder] = []
        self.client = client or ClientInterface()
    
    def add_agent(self, name: str) -> AgentBuilder:
        """Add an agent to the multi-agent system.
        
        Args:
            name: The name of the agent
            
        Returns:
            The AgentBuilder instance for configuring the agent
        """
        agent = AgentBuilder(name, self.client)
        self.agents.append(agent)
        return agent
    
    def create_agents(self, medium: ConversationMedium = None) -> MultiAgentWrapper:
        """Create all agents using the agent API endpoint and manage their conversation.
        
        Args:
            medium: The conversation medium to use (ignored, as the API creates the gateway conversation)
        
        Returns:
            A MultiAgentWrapper instance that manages all agents and the conversation
        
        Raises:
            ValidationError: If any agent configuration is invalid
        """
        if not self.agents:
            raise ValidationError("No agents configured")
        agent_user_ids = []
        gateway_conversation_ids = []
        for agent in self.agents:
            try:
                chain_config = agent.build()
                agent_create_payload = {
                    "agent_name": agent.name,
                    "config": chain_config.chain
                }
                agent_user = self.client.create_agent(agent_create_payload)
                agent_user_ids.append(agent_user["id"])
                gateway_conversation_id = agent_user.get("gateway_conversation_id")
                if gateway_conversation_id:
                    gateway_conversation_ids.append(gateway_conversation_id)
            except Exception as e:
                raise ValidationError(f"Failed to create agent '{agent.name}': {str(e)}")
        # For multi-agent, use the first agent's gateway conversation as the shared conversation
        if not gateway_conversation_ids:
            raise ValidationError("No gateway conversations returned from agent API.")
        conversation_id = gateway_conversation_ids[0]
        return MultiAgentWrapper(agent_user_ids, conversation_id, self.client)

# Example usage:
"""
# Configure client mode via environment variables
# LEXRCHAINER_API_KEY=your_api_key  # or LEXRCHAINER_JWT_TOKEN=your_jwt_token
# LEXRCHAINER_API_URL=http://your-api-url

# Create a single agent
agent = (AgentBuilder("Simple Assistant")
    .with_model("gpt-4")
    .with_system_prompt("You are a helpful assistant")
    .create_agent())

# Send a message to the agent
response = agent.send_message("Hello, how are you?")

# Create multiple agents
multi_agent = MultiAgentBuilder()
assistant = multi_agent.add_agent("Assistant")
assistant.with_model("gpt-4").with_system_prompt("You are a helpful assistant")

expert = multi_agent.add_agent("Expert")
expert.with_model("gpt-4").with_system_prompt("You are an expert in your field")

# Create all agents and start conversation
agents = multi_agent.create_agents()

# Send a message to all agents
responses = agents.send_message("Hello everyone!")
""" 