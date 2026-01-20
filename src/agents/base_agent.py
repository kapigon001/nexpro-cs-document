"""Base Agent class that all specialized agents inherit from"""
from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict
from rich.console import Console
from ..core.task import Task, TaskStatus
from ..core.message import Message, MessageType
import uuid


console = Console()


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.

    Each agent has a specific role and can:
    - Receive tasks from the CEO/Orchestrator
    - Process tasks according to their specialization
    - Report status and results back
    - Communicate with other agents through messages
    """

    def __init__(self, name: str, role: str, description: str):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.role = role
        self.description = description
        self.current_task: Optional[Task] = None
        self.completed_tasks: List[Task] = []
        self.inbox: List[Message] = []
        self.outbox: List[Message] = []

    def log(self, message: str, style: str = ""):
        """Log a message with agent context"""
        prefix = f"[bold blue][{self.name}][/bold blue]"
        console.print(f"{prefix} {message}", style=style)

    def receive_task(self, task: Task) -> bool:
        """Receive a task assignment"""
        if self.current_task is not None:
            self.log(f"Cannot accept task '{task.name}' - already working on '{self.current_task.name}'", "yellow")
            return False

        self.current_task = task
        task.assigned_to = self.name
        task.start()
        self.log(f"Received task: {task.name}", "green")
        return True

    def receive_message(self, message: Message):
        """Receive a message from another agent"""
        self.inbox.append(message)
        self.log(f"Received message from {message.sender}: {message.type.value}")

    def send_message(self, receiver: str, msg_type: MessageType, content: Any, metadata: dict = None) -> Message:
        """Send a message to another agent"""
        message = Message(
            id=str(uuid.uuid4())[:8],
            sender=self.name,
            receiver=receiver,
            type=msg_type,
            content=content,
            metadata=metadata,
        )
        self.outbox.append(message)
        return message

    @abstractmethod
    async def execute_task(self, task: Task) -> Any:
        """
        Execute the assigned task.
        Must be implemented by each specialized agent.
        Returns the result of the task execution.
        """
        pass

    async def run(self) -> Optional[Any]:
        """Run the current task to completion"""
        if self.current_task is None:
            self.log("No task assigned", "yellow")
            return None

        try:
            self.log(f"Starting execution of: {self.current_task.name}")
            result = await self.execute_task(self.current_task)
            self.current_task.complete(result)
            self.completed_tasks.append(self.current_task)
            self.log(f"Completed task: {self.current_task.name}", "green")

            # Clear current task
            completed_task = self.current_task
            self.current_task = None
            return result

        except Exception as e:
            error_msg = str(e)
            self.current_task.fail(error_msg)
            self.log(f"Task failed: {error_msg}", "red")
            self.current_task = None
            raise

    def get_status(self) -> Dict:
        """Get current agent status"""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "is_busy": self.current_task is not None,
            "current_task": self.current_task.name if self.current_task else None,
            "completed_count": len(self.completed_tasks),
            "inbox_count": len(self.inbox),
        }

    def __repr__(self):
        return f"<{self.__class__.__name__} name='{self.name}' role='{self.role}'>"
