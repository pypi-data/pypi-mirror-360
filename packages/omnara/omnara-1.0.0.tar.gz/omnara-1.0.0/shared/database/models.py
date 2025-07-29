from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import (
    DeclarativeBase,  # type: ignore[attr-defined]
    Mapped,  # type: ignore[attr-defined]
    mapped_column,  # type: ignore[attr-defined]
    relationship,
)

from .enums import AgentStatus


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True
    )  # Matches Supabase auth.users.id
    email: Mapped[str] = mapped_column(String(255), unique=True)
    display_name: Mapped[str | None] = mapped_column(String(255), default=None)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    agent_instances: Mapped[list["AgentInstance"]] = relationship(
        "AgentInstance", back_populates="user"
    )
    answered_questions: Mapped[list["AgentQuestion"]] = relationship(
        "AgentQuestion", back_populates="answered_by_user"
    )
    feedback: Mapped[list["AgentUserFeedback"]] = relationship(
        "AgentUserFeedback", back_populates="created_by_user"
    )
    api_keys: Mapped[list["APIKey"]] = relationship("APIKey", back_populates="user")


class AgentType(Base):
    __tablename__ = "agent_types"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    instances: Mapped[list["AgentInstance"]] = relationship(
        "AgentInstance", back_populates="agent_type"
    )


class AgentInstance(Base):
    __tablename__ = "agent_instances"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    agent_type_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_types.id"), type_=PostgresUUID(as_uuid=True)
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), type_=PostgresUUID(as_uuid=True)
    )
    status: Mapped[AgentStatus] = mapped_column(default=AgentStatus.ACTIVE)
    started_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(default=None)

    # Relationships
    agent_type: Mapped["AgentType"] = relationship(
        "AgentType", back_populates="instances"
    )
    user: Mapped["User"] = relationship("User", back_populates="agent_instances")
    steps: Mapped[list["AgentStep"]] = relationship(
        "AgentStep", back_populates="instance", order_by="AgentStep.created_at"
    )
    questions: Mapped[list["AgentQuestion"]] = relationship(
        "AgentQuestion", back_populates="instance", order_by="AgentQuestion.asked_at"
    )
    user_feedback: Mapped[list["AgentUserFeedback"]] = relationship(
        "AgentUserFeedback",
        back_populates="instance",
        order_by="AgentUserFeedback.created_at",
    )


class AgentStep(Base):
    __tablename__ = "agent_steps"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    agent_instance_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_instances.id"), type_=PostgresUUID(as_uuid=True)
    )
    step_number: Mapped[int] = mapped_column()
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    instance: Mapped["AgentInstance"] = relationship(
        "AgentInstance", back_populates="steps"
    )


class AgentQuestion(Base):
    __tablename__ = "agent_questions"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    agent_instance_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_instances.id"), type_=PostgresUUID(as_uuid=True)
    )
    question_text: Mapped[str] = mapped_column(Text)
    answer_text: Mapped[str | None] = mapped_column(Text, default=None)
    answered_by_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id"), type_=PostgresUUID(as_uuid=True), default=None
    )
    asked_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    answered_at: Mapped[datetime | None] = mapped_column(default=None)
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    instance: Mapped["AgentInstance"] = relationship(
        "AgentInstance", back_populates="questions"
    )
    answered_by_user: Mapped["User | None"] = relationship(
        "User", back_populates="answered_questions"
    )


class AgentUserFeedback(Base):
    __tablename__ = "agent_user_feedback"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    agent_instance_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_instances.id"), type_=PostgresUUID(as_uuid=True)
    )
    created_by_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), type_=PostgresUUID(as_uuid=True)
    )
    feedback_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    retrieved_at: Mapped[datetime | None] = mapped_column(default=None)

    # Relationships
    instance: Mapped["AgentInstance"] = relationship(
        "AgentInstance", back_populates="user_feedback"
    )
    created_by_user: Mapped["User"] = relationship("User", back_populates="feedback")


class APIKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), type_=PostgresUUID(as_uuid=True)
    )
    name: Mapped[str] = mapped_column(String(255))
    api_key_hash: Mapped[str] = mapped_column(String(128))
    api_key: Mapped[str] = mapped_column(
        Text
    )  # Store the actual JWT for user viewing, not good for security
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(default=None)
    last_used_at: Mapped[datetime | None] = mapped_column(default=None)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="api_keys")
