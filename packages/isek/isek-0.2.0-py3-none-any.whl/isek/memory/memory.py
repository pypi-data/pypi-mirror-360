from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel


class UserMemory(BaseModel):
    """Simple user memory model."""

    memory_id: Optional[str] = None
    memory: str
    topics: Optional[List[str]] = None
    last_updated: Optional[datetime] = None

    def __post_init__(self):
        if self.memory_id is None:
            self.memory_id = str(uuid4())
        if self.last_updated is None:
            self.last_updated = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)


class SessionSummary(BaseModel):
    """Simple session summary model."""

    summary: str
    topics: Optional[List[str]] = None
    last_updated: Optional[datetime] = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)


@dataclass
class Memory:
    """Ultra-simplified Memory class with minimal features."""

    # Model used for memories and summaries (optional)
    model: Optional[Any] = None

    # Simple in-memory storage
    memories: Dict[str, Dict[str, UserMemory]] = field(default_factory=dict)
    summaries: Dict[str, Dict[str, SessionSummary]] = field(default_factory=dict)
    runs: Dict[str, List[Any]] = field(default_factory=dict)

    # Debug mode
    debug_mode: bool = False
    version: int = 2

    def __post_init__(self):
        """Initialize memory after creation."""
        if self.debug_mode:
            print(f"Memory initialized (version: {self.version})")

    def add_user_memory(self, memory: UserMemory, user_id: str = "default") -> str:
        """Add a user memory."""
        if memory.memory_id is None:
            memory.memory_id = str(uuid4())

        if user_id not in self.memories:
            self.memories[user_id] = {}

        self.memories[user_id][memory.memory_id] = memory

        if self.debug_mode:
            print(f"Added memory for user {user_id}: {memory.memory_id}")

        return memory.memory_id

    def get_user_memories(self, user_id: str = "default") -> List[UserMemory]:
        """Get all memories for a user."""
        if user_id not in self.memories:
            return []
        return list(self.memories[user_id].values())

    def get_user_memory(
        self, memory_id: str, user_id: str = "default"
    ) -> Optional[UserMemory]:
        """Get a specific memory by ID."""
        if user_id not in self.memories:
            return None
        return self.memories[user_id].get(memory_id)

    def delete_user_memory(self, memory_id: str, user_id: str = "default") -> bool:
        """Delete a user memory."""
        if user_id in self.memories and memory_id in self.memories[user_id]:
            del self.memories[user_id][memory_id]
            if self.debug_mode:
                print(f"Deleted memory {memory_id} for user {user_id}")
            return True
        return False

    def add_session_summary(
        self, session_id: str, summary: SessionSummary, user_id: str = "default"
    ) -> str:
        """Add a session summary."""
        if user_id not in self.summaries:
            self.summaries[user_id] = {}

        self.summaries[user_id][session_id] = summary

        if self.debug_mode:
            print(f"Added session summary for user {user_id}, session {session_id}")

        return session_id

    def get_session_summary(
        self, session_id: str, user_id: str = "default"
    ) -> Optional[SessionSummary]:
        """Get a session summary."""
        if user_id not in self.summaries:
            return None
        return self.summaries[user_id].get(session_id)

    def add_run(self, session_id: str, run: Any) -> None:
        """Add a run to memory."""
        if session_id not in self.runs:
            self.runs[session_id] = []

        self.runs[session_id].append(run)

        if self.debug_mode:
            print(f"Added run to session {session_id}")

    def get_runs(self, session_id: str) -> List[Any]:
        """Get all runs for a session."""
        return self.runs.get(session_id, [])

    def clear(self) -> None:
        """Clear all memory."""
        self.memories.clear()
        self.summaries.clear()
        self.runs.clear()

        if self.debug_mode:
            print("Memory cleared")

    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary."""
        return {
            "memories": {
                user_id: {
                    memory_id: memory.to_dict()
                    for memory_id, memory in user_memories.items()
                }
                for user_id, user_memories in self.memories.items()
            },
            "summaries": {
                user_id: {
                    session_id: summary.to_dict()
                    for session_id, summary in session_summaries.items()
                }
                for user_id, session_summaries in self.summaries.items()
            },
            "runs": {
                session_id: [str(run) for run in runs]
                for session_id, runs in self.runs.items()
            },
        }

    def __repr__(self) -> str:
        return f"Memory(users={len(self.memories)}, sessions={len(self.summaries)}, runs={len(self.runs)})"
