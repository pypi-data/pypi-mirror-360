"""DeepSentinel SDK data types and models.

This module contains all Pydantic models used for request/response validation,
configuration, and internal data structures throughout the DeepSentinel SDK.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class MessageRole(str, Enum):
    """Enumeration of possible message roles in a conversation."""
    
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"


class ComplianceAction(str, Enum):
    """Enumeration of possible compliance actions."""
    
    ALLOW = "allow"
    BLOCK = "block"
    REDACT = "redact"
    WARN = "warn"
    AUDIT = "audit"


class SeverityLevel(str, Enum):
    """Enumeration of severity levels for violations and alerts."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProviderType(str, Enum):
    """Enumeration of supported LLM providers."""
    
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    CUSTOM = "custom"


class Message(BaseModel):
    """Represents a single message in a conversation.
    
    Attributes:
        role: The role of the message sender
        content: The message content
        name: Optional name of the sender
        function_call: Optional function call data
        tool_calls: Optional list of tool calls
        tool_call_id: Optional tool call identifier
    """
    
    role: MessageRole
    content: Optional[str] = None
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    
    @validator("content")
    def validate_content(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Optional[str]:
        """Validate that content is provided for most message types."""
        role = values.get("role")
        if role in [MessageRole.USER, MessageRole.ASSISTANT] and not v:
            raise ValueError(f"Content is required for {role} messages")
        return v


class ChatRequest(BaseModel):
    """Request model for chat completions.
    
    Attributes:
        messages: List of conversation messages
        model: Model identifier
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        top_p: Nucleus sampling parameter
        frequency_penalty: Frequency penalty parameter
        presence_penalty: Presence penalty parameter
        stop: Stop sequences
        stream: Whether to stream the response
        user: Optional user identifier
        functions: Optional function definitions
        function_call: Optional function call preference
        tools: Optional tool definitions
        tool_choice: Optional tool choice preference
    """
    
    messages: List[Message]
    model: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    stop: Optional[Union[str, List[str]]] = None
    stream: bool = False
    user: Optional[str] = None
    functions: Optional[List[Dict[str, Any]]] = None
    function_call: Optional[Union[str, Dict[str, Any]]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None


class Usage(BaseModel):
    """Token usage information.
    
    Attributes:
        prompt_tokens: Tokens used in the prompt
        completion_tokens: Tokens used in the completion
        total_tokens: Total tokens used
    """
    
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class Choice(BaseModel):
    """Represents a single completion choice.
    
    Attributes:
        index: Choice index
        message: The response message
        finish_reason: Reason the completion finished
        logprobs: Optional log probabilities
    """
    
    index: int
    message: Message
    finish_reason: Optional[str] = None
    logprobs: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Response model for chat completions.
    
    Attributes:
        id: Response identifier
        object: Object type
        created: Creation timestamp
        model: Model used
        choices: List of completion choices
        usage: Token usage information
        system_fingerprint: Optional system fingerprint
    """
    
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]
    usage: Optional[Usage] = None
    system_fingerprint: Optional[str] = None


class CompletionRequest(BaseModel):
    """Request model for text completions.
    
    Attributes:
        model: Model identifier
        prompt: Text prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        top_p: Nucleus sampling parameter
        n: Number of completions to generate
        stream: Whether to stream the response
        logprobs: Number of log probabilities to return
        echo: Whether to echo the prompt
        stop: Stop sequences
        presence_penalty: Presence penalty parameter
        frequency_penalty: Frequency penalty parameter
        best_of: Number of completions to generate server-side
        logit_bias: Logit bias adjustments
        user: Optional user identifier
        suffix: Optional suffix for completion
    """
    
    model: str
    prompt: Union[str, List[str]]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    n: Optional[int] = Field(1, ge=1)
    stream: bool = False
    logprobs: Optional[int] = Field(None, ge=0, le=5)
    echo: bool = False
    stop: Optional[Union[str, List[str]]] = None
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    best_of: Optional[int] = Field(None, ge=1)
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None
    suffix: Optional[str] = None


class CompletionChoice(BaseModel):
    """Represents a single completion choice.
    
    Attributes:
        text: Generated text
        index: Choice index
        logprobs: Optional log probabilities
        finish_reason: Reason the completion finished
    """
    
    text: str
    index: int
    logprobs: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None


class CompletionResponse(BaseModel):
    """Response model for text completions.
    
    Attributes:
        id: Response identifier
        object: Object type
        created: Creation timestamp
        model: Model used
        choices: List of completion choices
        usage: Token usage information
        system_fingerprint: Optional system fingerprint
    """
    
    id: str
    object: str
    created: int
    model: str
    choices: List[CompletionChoice]
    usage: Optional[Usage] = None
    system_fingerprint: Optional[str] = None


class EmbeddingRequest(BaseModel):
    """Request model for embeddings.
    
    Attributes:
        input: Text to embed
        model: Model identifier
        encoding_format: Encoding format for embeddings
        dimensions: Number of dimensions for embeddings
        user: Optional user identifier
    """
    
    input: Union[str, List[str]]
    model: str
    encoding_format: Optional[str] = "float"
    dimensions: Optional[int] = None
    user: Optional[str] = None


class Embedding(BaseModel):
    """Represents a single embedding.
    
    Attributes:
        object: Object type
        embedding: The embedding vector
        index: Embedding index
    """
    
    object: str
    embedding: List[float]
    index: int


class EmbeddingResponse(BaseModel):
    """Response model for embeddings.
    
    Attributes:
        object: Object type
        data: List of embeddings
        model: Model used
        usage: Token usage information
    """
    
    object: str
    data: List[Embedding]
    model: str
    usage: Optional[Usage] = None


class ComplianceCheck(BaseModel):
    """Represents a compliance check result.
    
    Attributes:
        policy_name: Name of the policy that was checked
        passed: Whether the check passed
        action: Action to take if check failed
        severity: Severity level of any violation
        message: Human-readable message about the check
        details: Additional details about the check
        timestamp: When the check was performed
    """
    
    policy_name: str
    passed: bool
    action: ComplianceAction
    severity: SeverityLevel
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AuditEntry(BaseModel):
    """Represents an audit log entry.
    
    Attributes:
        id: Unique identifier for the entry
        timestamp: When the event occurred
        user_id: Identifier of the user
        session_id: Session identifier
        operation: The operation that was performed
        provider: The LLM provider used
        model: The model used
        request_data: Summary of the request
        response_data: Summary of the response
        compliance_checks: List of compliance checks performed
        metadata: Additional metadata
        cost: Optional cost information
        duration_ms: Duration of the operation in milliseconds
    """
    
    id: str
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    operation: str
    provider: str
    model: str
    request_data: Dict[str, Any] = Field(default_factory=dict)
    response_data: Dict[str, Any] = Field(default_factory=dict)
    compliance_checks: List[ComplianceCheck] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    cost: Optional[float] = None
    duration_ms: Optional[int] = None


class ProviderConfig(BaseModel):
    """Configuration for a specific provider.
    
    Attributes:
        provider_type: Type of the provider
        api_key: API key for authentication
        base_url: Base URL for the provider's API
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries
        retry_delay: Delay between retries in seconds
        rate_limit: Rate limit configuration
        headers: Additional headers to send
        extra_config: Provider-specific configuration
    """
    
    provider_type: ProviderType
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit: Optional[Dict[str, Any]] = None
    headers: Dict[str, str] = Field(default_factory=dict)
    extra_config: Dict[str, Any] = Field(default_factory=dict)


class StreamChunk(BaseModel):
    """Represents a chunk of streamed response data.
    
    Attributes:
        id: Chunk identifier
        object: Object type
        created: Creation timestamp
        model: Model used
        choices: List of choice deltas
        usage: Optional usage information (usually only in final chunk)
    """
    
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Optional[Usage] = None


class MCPToolCall(BaseModel):
    """Represents an MCP tool call.
    
    Attributes:
        server_name: Name of the MCP server
        tool_name: Name of the tool to call
        arguments: Arguments to pass to the tool
        call_id: Unique identifier for the call
    """
    
    server_name: str
    tool_name: str
    arguments: Dict[str, Any]
    call_id: str


class MCPToolResult(BaseModel):
    """Represents the result of an MCP tool call.
    
    Attributes:
        call_id: Identifier of the original call
        success: Whether the call was successful
        result: The result data
        error: Error information if the call failed
        metadata: Additional metadata
    """
    
    call_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)