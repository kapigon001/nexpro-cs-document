"""Task management for agent workflows"""
from enum import Enum
from typing import Any, Optional, List
from pydantic import BaseModel
from datetime import datetime


class TaskStatus(str, Enum):
    """Status of a task"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(BaseModel):
    """Task object representing work to be done by an agent"""
    id: str
    name: str
    description: str
    assigned_to: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 1  # 1 = highest priority
    dependencies: List[str] = []  # List of task IDs that must complete first
    input_data: Optional[Any] = None
    output_data: Optional[Any] = None
    error_message: Optional[str] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __init__(self, **data):
        if data.get("created_at") is None:
            data["created_at"] = datetime.now()
        super().__init__(**data)

    def start(self):
        """Mark task as started"""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()

    def complete(self, output_data: Any = None):
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        if output_data is not None:
            self.output_data = output_data

    def fail(self, error_message: str):
        """Mark task as failed"""
        self.status = TaskStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.now()

    def is_ready(self, completed_tasks: List[str]) -> bool:
        """Check if all dependencies are satisfied"""
        return all(dep in completed_tasks for dep in self.dependencies)
