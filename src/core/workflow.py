"""Workflow management for orchestrating multi-agent tasks"""
from typing import Dict, List, Optional
from .task import Task, TaskStatus
from .message import Message, MessageType
import uuid


class Workflow:
    """Manages the workflow of tasks across multiple agents"""

    def __init__(self, name: str, description: str = ""):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.description = description
        self.tasks: Dict[str, Task] = {}
        self.messages: List[Message] = []
        self.completed_task_ids: List[str] = []

    def add_task(self, task: Task) -> str:
        """Add a task to the workflow"""
        self.tasks[task.id] = task
        return task.id

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        return self.tasks.get(task_id)

    def get_ready_tasks(self) -> List[Task]:
        """Get all tasks that are ready to be executed"""
        ready = []
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING and task.is_ready(self.completed_task_ids):
                ready.append(task)
        return sorted(ready, key=lambda t: t.priority)

    def get_in_progress_tasks(self) -> List[Task]:
        """Get all tasks currently in progress"""
        return [t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS]

    def complete_task(self, task_id: str, output_data=None):
        """Mark a task as completed"""
        if task_id in self.tasks:
            self.tasks[task_id].complete(output_data)
            self.completed_task_ids.append(task_id)

    def fail_task(self, task_id: str, error_message: str):
        """Mark a task as failed"""
        if task_id in self.tasks:
            self.tasks[task_id].fail(error_message)

    def add_message(self, message: Message):
        """Log a message in the workflow"""
        self.messages.append(message)

    def is_complete(self) -> bool:
        """Check if all tasks are completed"""
        return all(
            t.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
            for t in self.tasks.values()
        )

    def has_failed(self) -> bool:
        """Check if any task has failed"""
        return any(t.status == TaskStatus.FAILED for t in self.tasks.values())

    def get_progress(self) -> dict:
        """Get workflow progress summary"""
        total = len(self.tasks)
        completed = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        in_progress = len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])
        failed = len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED])

        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "failed": failed,
            "pending": total - completed - in_progress - failed,
            "percent_complete": (completed / total * 100) if total > 0 else 0,
        }
