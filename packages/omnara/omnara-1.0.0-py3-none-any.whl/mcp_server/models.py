"""
MCP Server tool interface models.

This module contains all Pydantic models for MCP tool requests and responses.
Models define the interface contract between AI agents and the MCP server.
"""

from pydantic import BaseModel, Field

# ============================================================================
# Tool Request Models
# ============================================================================


# Payload when an agent wants to log its current step/progress
class LogStepRequest(BaseModel):
    """Request model for logging a step"""

    agent_instance_id: str | None = Field(
        None, description="Existing agent instance ID"
    )
    agent_type: str = Field(
        ..., description="Type of agent (e.g., 'Claude Code', 'Cursor')"
    )
    step_description: str = Field(
        ..., description="High-level description of the current step"
    )


# Payload when an agent wants to ask the user a question (non-blocking operation)
class AskQuestionRequest(BaseModel):
    """Request model for asking a question"""

    agent_instance_id: str = Field(..., description="Agent instance ID")
    question_text: str = Field(..., description="Question to ask the user")


# ============================================================================
# Tool Response Models
# ============================================================================


# Response confirming a step was logged successfully with step details
class LogStepResponse(BaseModel):
    """Response model for log step"""

    success: bool = Field(..., description="Whether the step was logged successfully")
    agent_instance_id: str = Field(
        ..., description="Agent instance ID (new or existing)"
    )
    step_number: int = Field(..., description="Sequential step number")
    user_feedback: list[str] = Field(
        default_factory=list,
        description="Any user feedback provided since the last step",
    )


# Response containing the user's answer to an agent's question
class AskQuestionResponse(BaseModel):
    """Response model for ask question"""

    answer: str = Field(..., description="User's answer to the question")
    question_id: str = Field(..., description="ID of the question that was answered")


# Response confirming a session was ended successfully
class EndSessionResponse(BaseModel):
    """Response model for end session"""

    success: bool = Field(..., description="Whether the session was ended successfully")
    agent_instance_id: str = Field(..., description="Agent instance ID that was ended")
    final_status: str = Field(
        ..., description="Final status of the session (should be 'completed')"
    )
