import asyncio
import time
from datetime import datetime, timezone
from uuid import UUID

from shared.database import (
    AgentInstance,
    AgentQuestion,
    AgentStatus,
    AgentStep,
    AgentType,
    AgentUserFeedback,
)
from sqlalchemy import func
from sqlalchemy.orm import Session


def create_or_get_agent_type(db: Session, name: str) -> AgentType:
    """Create or get an agent type by name"""
    # Normalize name to lowercase for consistent storage
    normalized_name = name.lower()

    agent_type = db.query(AgentType).filter(AgentType.name == normalized_name).first()
    if not agent_type:
        agent_type = AgentType(name=normalized_name)
        db.add(agent_type)
        db.commit()
        db.refresh(agent_type)
    return agent_type


def create_agent_instance(
    db: Session, agent_type_id: UUID, user_id: str
) -> AgentInstance:
    """Create a new agent instance"""
    instance = AgentInstance(
        agent_type_id=agent_type_id, user_id=UUID(user_id), status=AgentStatus.ACTIVE
    )
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


def get_agent_instance(db: Session, instance_id: str) -> AgentInstance | None:
    """Get an agent instance by ID"""
    return db.query(AgentInstance).filter(AgentInstance.id == instance_id).first()


def log_step(db: Session, instance_id: UUID, description: str) -> AgentStep:
    """Log a new step for an agent instance"""
    # Get the next step number
    max_step = (
        db.query(func.max(AgentStep.step_number))
        .filter(AgentStep.agent_instance_id == instance_id)
        .scalar()
    )
    next_step_number = (max_step or 0) + 1

    # Create the step
    step = AgentStep(
        agent_instance_id=instance_id,
        step_number=next_step_number,
        description=description,
    )
    db.add(step)
    db.commit()
    db.refresh(step)
    return step


def create_question(
    db: Session, instance_id: UUID, question_text: str
) -> AgentQuestion:
    """Create a new question for an agent instance"""
    # Mark any existing active questions as inactive
    db.query(AgentQuestion).filter(
        AgentQuestion.agent_instance_id == instance_id, AgentQuestion.is_active
    ).update({"is_active": False})

    # Create new question
    question = AgentQuestion(
        agent_instance_id=instance_id, question_text=question_text, is_active=True
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


async def wait_for_answer(
    db: Session, question_id: UUID, timeout: int = 86400
) -> str | None:
    """
    Wait for an answer to a question (async non-blocking)

    Args:
        db: Database session
        question_id: Question ID to wait for
        timeout: Maximum time to wait in seconds (default 24 hours)

    Returns:
        Answer text if received, None if timeout
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        # Check for answer
        db.commit()  # Ensure we see latest data
        question = (
            db.query(AgentQuestion).filter(AgentQuestion.id == question_id).first()
        )

        if question and question.answer_text is not None:
            return question.answer_text

        await asyncio.sleep(1)

    # Timeout - mark question as inactive
    db.query(AgentQuestion).filter(AgentQuestion.id == question_id).update(
        {"is_active": False}
    )
    db.commit()

    return None


def get_and_mark_unretrieved_feedback(
    db: Session, instance_id: UUID, since_time: datetime | None = None
) -> list[str]:
    """Get unretrieved user feedback for an agent instance and mark as retrieved"""

    query = db.query(AgentUserFeedback).filter(
        AgentUserFeedback.agent_instance_id == instance_id,
        AgentUserFeedback.retrieved_at.is_(None),
    )

    if since_time:
        query = query.filter(AgentUserFeedback.created_at > since_time)

    feedback_list = query.order_by(AgentUserFeedback.created_at).all()

    # Mark all feedback as retrieved
    for feedback in feedback_list:
        feedback.retrieved_at = datetime.now(timezone.utc)
    db.commit()

    return [feedback.feedback_text for feedback in feedback_list]


def end_session(db: Session, instance_id: UUID) -> AgentInstance:
    """End an agent session by marking it as completed"""
    instance = db.query(AgentInstance).filter(AgentInstance.id == instance_id).first()

    if not instance:
        raise ValueError(f"Agent instance {instance_id} not found")

    # Update status to completed
    instance.status = AgentStatus.COMPLETED
    instance.ended_at = datetime.now(timezone.utc)

    # Mark any active questions as inactive
    db.query(AgentQuestion).filter(
        AgentQuestion.agent_instance_id == instance_id, AgentQuestion.is_active
    ).update({"is_active": False})

    db.commit()
    db.refresh(instance)
    return instance
