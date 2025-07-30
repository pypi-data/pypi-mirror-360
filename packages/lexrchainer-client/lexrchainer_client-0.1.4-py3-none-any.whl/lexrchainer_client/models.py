"""
Client-side data models for LexrChainer.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Union, TypeAlias
from enum import Enum
from typing_extensions import Required, TypedDict
from datetime import datetime, timedelta

class MessageType(str, Enum):
    """Type of message content."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"

class MessageRole(str, Enum):
    """Role of the message sender."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class MessageContent(BaseModel):
    """Content of a message."""
    type: MessageType
    text: Optional[str] = None
    url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class Message(BaseModel):
    """A message in a conversation."""
    role: MessageRole
    content: str
    entity_id: str
    conversation_id: Optional[str] = None

class ModelParams(BaseModel):
    """Parameters for model configuration."""
    model: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    stop: Optional[List[str]] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None

class ModelConfig(BaseModel):
    """Configuration for a model."""
    name: str
    credentials: Dict[str, Any] = Field(default_factory=dict)
    params: ModelParams

class ToolConfig(BaseModel):
    """Configuration for a tool."""
    name: str
    credentials: Dict[str, Any] = Field(default_factory=dict)

class ChainStepType(str, Enum):
    """Type of chain step."""
    USER_MESSAGE_ADDENDUM = "USER_MESSAGE_ADDENDUM"
    ASSISTANT_MESSAGE_ADDENDUM = "ASSISTANT_MESSAGE_ADDENDUM"
    HIDDEN_TURN_USER = "HIDDEN_TURN_USER"
    HIDDEN_TURN_ASSISTANT = "HIDDEN_TURN_ASSISTANT"
    DIRECT_TOOL_USE = "DIRECT_TOOL_USE"
    EXECUTE_CODE = "EXECUTE_CODE"
    SET_RESULT = "SET_RESULT"
    # Used when a calculated / processed data needs to be sent to user. Example: Message extracted from XML tags.
    SEND_TO_USER = "SEND_TO_USER"

class ChainStepFlowDirection(str, Enum):
    """Direction of flow in a chain step."""
    TO_USER = "TO_USER"
    TO_ASSISTANT = "TO_ASSISTANT"

class ChainStepFlowType(str, Enum):
    """Type of flow in a chain step."""
    AT_ONCE = "AT_ONCE"
    STREAMING = "STREAMING"

class ChainStepFlowState(str, Enum):
    """State of flow in a chain step."""
    CONTINUE = "CONTINUE"
    END = "END"

class ChainStepResponseTreatment(str, Enum):
    """How to treat the response in a chain step."""
    APPEND = "APPEND"
    REPLACE = "REPLACE"
    IGNORE = "IGNORE"

class ChainStepConfig(BaseModel):
    """Configuration for a chain step."""
    name: str
    id: str
    description: str
    version: str
    prompt: str
    type: ChainStepType
    flow: ChainStepFlowDirection
    flow_type: ChainStepFlowType = ChainStepFlowType.AT_ONCE
    flow_state: ChainStepFlowState = ChainStepFlowState.CONTINUE
    response_treatment: ChainStepResponseTreatment = ChainStepResponseTreatment.APPEND
    tool_use: bool = False
    model_params: ModelParams

class ChainMeta(BaseModel):
    """Metadata for a chain."""
    id: str
    name: str
    description: str
    version: str
    default_system_prompt: str
    static_meta: Dict[str, Any] = Field(default_factory=dict)
    tools: List[ToolConfig] = Field(default_factory=list)
    models: List[ModelConfig] = Field(default_factory=list)
    default_model_params: ModelParams

class ChainCreate(BaseModel):
    json_content: Dict[str, Any]
    class Config:
        extra = 'allow'

class ChainConfig(BaseModel):
    """Configuration for a chain."""
    chain: ChainMeta
    steps: List[ChainStepConfig]

class UserType(str, Enum):
    """Type of user."""
    HUMAN = "human"
    AGENT = "agent"

class ConversationMedium(str, Enum):
    """Medium of conversation."""
    WHATSAPP = "WHATSAPP"
    WEB = "WEB"
    TELEGRAM = "TELEGRAM"
    EMAIL = "EMAIL"

class ConversationTurnType(str, Enum):
    """Type of conversation turn."""
    SEQUENTIAL = "SEQUENTIAL"
    PARALLEL = "PARALLEL"

class ConversationIterationEndCriteria(str, Enum):
    """Criteria for ending conversation iteration."""
    ALL_TURNS_DONE = "ALL_TURNS_DONE"
    PERPETUAL = "PERPETUAL"
    MAX_ITERATIONS = "MAX_ITERATIONS"

class ConversationMemberRole(str, Enum):
    """Role of a conversation member."""
    ACTIVE_PARTICIPATION = "ACTIVE_PARTICIPATION"
    OBSERVER = "OBSERVER"

class ConversationMember(BaseModel):
    """A member in a conversation."""
    id: Optional[str] = None
    role: ConversationMemberRole = ConversationMemberRole.ACTIVE_PARTICIPATION

class UserCreate(BaseModel):
    """Request to create a user."""
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    user_type: UserType
    chain_id: Optional[str] = None
    chain_config: Optional[ChainCreate] = None

class CreateConversationRequest(BaseModel):
    """Request to create a conversation."""
    medium: ConversationMedium
    members: List[ConversationMember]
    turn_type: ConversationTurnType
    iteration_end_criteria: ConversationIterationEndCriteria
    iteration_limit: Optional[int] = None
    persist: bool = True
    is_gateway: bool = False

class ClientConversationMessageRequest(BaseModel):
    """Request to send a message to a conversation."""
    sender_id: Optional[str] = None
    recepient_id: Optional[str] = None
    messages: List[Message]
    streaming: Optional[bool] = False
    conversation_id: Optional[str] = None
    async_request_id: Optional[str] = None

class ModelInfo(BaseModel):
    """Information about an available model."""
    name: str
    version: str
    description: str
    default_model_params: 'ModelParams'

class FunctionDefinition(TypedDict, total=False):
    name: Required[str]
    description: str
    parameters: Dict[str, object]
    strict: Optional[bool]

# --- Workflow API Models ---
class WorkflowCreateRequest(BaseModel):
    owner_agent_id: str
    owner_human_id: str
    goal: str
    instructions: List[str]
    workspace_id: Optional[str] = None

class WorkflowRunCreateRequest(BaseModel):
    workflow_id: str
    owner_agent_id: str
    owner_human_id: str
    goal: str
    instructions: List[str]
    workspace_id: Optional[str] = None

class RunWorkflowRequest(BaseModel):
    workflow_run_id: str

class SendMessageRequest(BaseModel):
    workflow_run_id: str
    sender_id: str
    message_content: Optional[str] = None
    output_handler_config: Optional[dict] = None  # Should be OutputHandlerConfig, but allow dict for flexibility

# --- Task API Models ---
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskActor(BaseModel):
    name: str
    description: Optional[str] = None

class Task(BaseModel):
    task_id: str
    task_name: str
    depends_on: List[str] = []
    dependents: List[str] = []
    task_description: str
    task_status: TaskStatus = TaskStatus.PENDING
    task_created_at: Optional[datetime] = None
    task_updated_at: Optional[datetime] = None
    task_completed_at: Optional[datetime] = None
    deadline: datetime
    priority: int = 1
    tags: List[str] = []
    actor: TaskActor
    actor_assignment: Optional[str] = None
    assigned_to: Optional[str] = None
    assigned_by: Optional[str] = None
    assigned_at: Optional[datetime] = None
    subtasks: List['Task'] = []

    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True

Task.model_rebuild()

class TaskListTemplate(BaseModel):
    tasklist_template_id: str
    tasklist_template_name: str
    tasklist_template_description: Optional[str] = None
    deadline_from_start: timedelta
    actors: List[TaskActor] = []
    tasks: List[Task] = []
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TaskList(BaseModel):
    tasklist_id: str
    tasklist_name: str
    deadline: datetime
    total_tasks: int = 0
    owner: str
    actors: List[TaskActor] = []
    dag_id: Optional[str] = None
    actor_assignments: Optional[dict] = None
    tasks: List[Task] = []
    template_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TaskCreateRequest(BaseModel):
    tasklist_id: str
    task_name: str
    task_description: str
    deadline: datetime
    actor: TaskActor
    priority: int = 1
    tags: Optional[List[str]] = None
    depends_on: Optional[List[str]] = None
    assigned_to: Optional[str] = None
    assigned_by: Optional[str] = None
    parent_task_id: Optional[str] = None

class TaskUpdateRequest(BaseModel):
    task_name: Optional[str] = None
    task_description: Optional[str] = None
    task_status: Optional[TaskStatus] = None
    priority: Optional[int] = None
    tags: Optional[List[str]] = None
    deadline: Optional[datetime] = None
    assigned_to: Optional[str] = None
    actor_assignment: Optional[str] = None

class TaskListCreateRequest(BaseModel):
    name: str
    deadline: datetime
    owner: str
    actors: List[TaskActor]
    tasks: List[Task]

class TaskListTemplateCreateRequest(BaseModel):
    name: str
    deadline_from_start_days: int
    actors: List[TaskActor]
    tasks: List[Task]

class AgentCreate(BaseModel):
    agent_name: str = Field(..., description="The name of the agent")
    config: ChainMeta = Field(..., description="The configuration of the agent")

class AgentUpdate(BaseModel):
    agent_name: str = Field(..., description="The name of the agent")
    config: ChainMeta = Field(..., description="The configuration of the agent")

class ValidationError(Exception):
    """Exception raised for validation errors."""
    pass

class ToolCredentialsBase(BaseModel):
    tool_id: str = Field(..., description="The ID of the tool (ForeignKey to tools.id)")
    credentials_json: Dict[str, Any] = Field(..., description="The credentials as a JSON object")

class ToolCredentialsCreate(ToolCredentialsBase):
    pass

class ToolCredentialsUpdate(BaseModel):
    credentials_json: Dict[str, Any] = Field(..., description="The credentials as a JSON object")
