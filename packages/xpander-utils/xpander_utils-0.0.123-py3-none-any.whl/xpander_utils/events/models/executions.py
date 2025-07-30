from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator
from datetime import datetime

from .memory import UserDetails

class AgentExecutionStatus(str, Enum):
    Pending = "pending"
    Executing = "executing"
    Paused = "paused"
    Error = "error"
    Completed = "completed"
    Stopped = "stopped"

class AgentExecutionInput(BaseModel):
    text: Optional[str] = ""
    files: Optional[List[str]] = []
    user: Optional[UserDetails] = None
    
    @model_validator(mode="after")
    def validate_at_least_one(cls, values):
        if not values.text and not values.files:
            raise ValueError("Agent execution input should have either 'text' or 'files'. Please provide at least one.")
        return values


class AgentBuilderOutput(BaseModel):
    agent_id: Optional[str] = None
    ai_employee_id: Optional[str] = None

class LLMTokens(BaseModel):
    completion_tokens: Optional[int] = 0
    prompt_tokens: Optional[int] = 0
    total_tokens: Optional[int] = 0

class Tokens(BaseModel):
    inner: Optional[LLMTokens] = LLMTokens()
    worker: Optional[LLMTokens] = LLMTokens()

class HumanInTheLoop(BaseModel):
    operation_id: str
    approved_by: Optional[str] = None
    rejected_by: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    content: str

class AgentExecution(BaseModel):
    id: str
    agent_id: str
    organization_id: str
    input: AgentExecutionInput
    status: Optional[AgentExecutionStatus] = AgentExecutionStatus.Pending
    last_executed_node_id: Optional[str] = None
    memory_thread_id: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    result: Optional[str] = None
    parent_execution: Optional[str] = None
    pending_sub_executions: Optional[List[str]] = []
    sub_executions: Optional[List[str]] = []
    tool_call_id: Optional[str] = None
    worker_id: Optional[str] = None
    is_manually_stopped: Optional[bool] = False
    agent_end_parser_instructions: Optional[str] = None
    llm_tokens: Optional[Tokens] = Tokens()
    payload_extension: Optional[dict] = None
    agent_builder_output: Optional[AgentBuilderOutput] = None
    hitl_request: Optional[HumanInTheLoop] = None
    source: Optional[str] = None

class AgentExecutionResult(BaseModel):
    """
    Represents the result of an agent execution.

    Attributes:
        is_success (Optional[bool]): Indicates whether the agent execution was successful.
            Defaults to True if not provided.
        result (str): The textual output or result produced by the agent execution.
            This field is required.
    """

    is_success: Optional[bool] = Field(
        default=True,
        description="Indicates whether the agent execution was successful. Defaults to True."
    )
    result: str = Field(
        ...,
        description="The textual output or result produced by the agent execution. This field is required."
    )
