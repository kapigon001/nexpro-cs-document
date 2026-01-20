"""Message types for inter-agent communication"""
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel
from datetime import datetime


class MessageType(str, Enum):
    """Types of messages exchanged between agents"""
    REQUEST = "request"
    RESPONSE = "response"
    STATUS_UPDATE = "status_update"
    ERROR = "error"
    APPROVAL = "approval"
    REJECTION = "rejection"


class Message(BaseModel):
    """Message object for agent communication"""
    id: str
    sender: str
    receiver: str
    type: MessageType
    content: Any
    metadata: Optional[dict] = None
    timestamp: datetime = None

    def __init__(self, **data):
        if data.get("timestamp") is None:
            data["timestamp"] = datetime.now()
        super().__init__(**data)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "type": self.type.value,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }
