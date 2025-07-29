"""
Memory management for Pitwall, the agentic AI companion to MultiViewer,
using PydanticAI's built-in message history.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from uuid import uuid4

from pydantic_core import to_jsonable_python
from pydantic_ai.messages import ModelMessagesTypeAdapter, ModelMessage


class ConversationMemory:
    """Manages conversation memory using PydanticAI's native message history."""

    def __init__(self, memory_dir: Optional[Path] = None):
        """Initialize memory manager."""
        if memory_dir is None:
            memory_dir = Path.home() / ".pitwall" / "memory"

        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.current_session_id: Optional[str] = None
        self.current_messages: List[ModelMessage] = []

    def _get_session_file(self, session_id: str) -> Path:
        """Get the file path for a session."""
        return self.memory_dir / f"{session_id}.json"

    def _get_session_metadata_file(self, session_id: str) -> Path:
        """Get the metadata file path for a session."""
        return self.memory_dir / f"{session_id}_meta.json"

    def create_session(
        self, model: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new conversation session and return session ID."""
        session_id = str(uuid4())
        now = datetime.now().isoformat()

        # Store session metadata
        session_metadata = {
            "session_id": session_id,
            "created_at": now,
            "updated_at": now,
            "model": model,
            "metadata": metadata or {},
        }

        # Save metadata
        metadata_file = self._get_session_metadata_file(session_id)
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(session_metadata, f, indent=2, ensure_ascii=False)

        # Initialize empty message history
        self.current_session_id = session_id
        self.current_messages = []
        self._save_messages()

        return session_id

    def load_session(self, session_id: str) -> bool:
        """Load an existing session. Returns True if successful."""
        session_file = self._get_session_file(session_id)
        metadata_file = self._get_session_metadata_file(session_id)

        if not session_file.exists() or not metadata_file.exists():
            return False

        try:
            # Load messages using PydanticAI's ModelMessagesTypeAdapter
            with open(session_file, "r", encoding="utf-8") as f:
                messages_data = json.load(f)

            if messages_data:
                self.current_messages = ModelMessagesTypeAdapter.validate_python(
                    messages_data
                )
            else:
                self.current_messages = []

            self.current_session_id = session_id
            return True

        except (json.JSONDecodeError, Exception):
            return False

    def _save_messages(self):
        """Save current messages to disk using PydanticAI serialization."""
        if self.current_session_id is None:
            return

        session_file = self._get_session_file(self.current_session_id)

        # Convert messages to JSON-serializable format using PydanticAI
        messages_data = to_jsonable_python(self.current_messages)

        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(messages_data, f, indent=2, ensure_ascii=False)

        # Update metadata timestamp
        self._update_session_metadata()

    def _update_session_metadata(self):
        """Update session metadata with current timestamp."""
        if self.current_session_id is None:
            return

        metadata_file = self._get_session_metadata_file(self.current_session_id)

        if metadata_file.exists():
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)

                metadata["updated_at"] = datetime.now().isoformat()
                metadata["message_count"] = len(self.current_messages)

                with open(metadata_file, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)

            except (json.JSONDecodeError, Exception):
                pass

    def update_from_run_result(self, run_result):
        """Update memory with messages from a PydanticAI run result."""
        if self.current_session_id is None:
            raise ValueError("No active session. Create or load a session first.")

        # Get all messages from the run result
        self.current_messages = run_result.all_messages()
        self._save_messages()

    def get_message_history(self) -> List[ModelMessage]:
        """Get the current message history for passing to agent.run()."""
        return self.current_messages.copy()

    def clear_session(self):
        """Clear the current session in memory (but keep it saved)."""
        self.current_session_id = None
        self.current_messages = []

    def get_session_summary(self) -> Optional[Dict[str, Any]]:
        """Get summary of current session."""
        if self.current_session_id is None:
            return None

        metadata_file = self._get_session_metadata_file(self.current_session_id)

        if not metadata_file.exists():
            return None

        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            return {
                "session_id": self.current_session_id,
                "message_count": len(self.current_messages),
                **metadata,
            }
        except (json.JSONDecodeError, Exception):
            return None

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all available sessions."""
        sessions = []

        for metadata_file in self.memory_dir.glob("*_meta.json"):
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)

                sessions.append(metadata)

            except (json.JSONDecodeError, Exception):
                continue

        # Sort by updated_at descending
        sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        session_file = self._get_session_file(session_id)
        metadata_file = self._get_session_metadata_file(session_id)

        deleted = False

        if session_file.exists():
            session_file.unlink()
            deleted = True

        if metadata_file.exists():
            metadata_file.unlink()
            deleted = True

        if self.current_session_id == session_id:
            self.clear_session()

        return deleted

    def clear_all_sessions(self):
        """Clear all sessions."""
        for session_file in self.memory_dir.glob("*.json"):
            session_file.unlink()

        self.clear_session()

    def export_session(self, session_id: str, export_path: Path) -> bool:
        """Export a session to a file."""
        session_file = self._get_session_file(session_id)
        metadata_file = self._get_session_metadata_file(session_id)

        if not session_file.exists() or not metadata_file.exists():
            return False

        try:
            # Load both files
            with open(session_file, "r", encoding="utf-8") as f:
                messages_data = json.load(f)

            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            # Combine into export format
            export_data = {"metadata": metadata, "messages": messages_data}

            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception:
            return False

    def has_active_session(self) -> bool:
        """Check if there's an active session."""
        return self.current_session_id is not None

    def get_context_summary(self, max_messages: int = 10) -> str:
        """Get a human-readable summary of recent conversation context."""
        if not self.current_messages:
            return "No conversation history."

        recent_messages = self.current_messages[-max_messages:]

        summary_parts = []
        summary_parts.append(f"Last {len(recent_messages)} messages:")

        for msg in recent_messages:
            if hasattr(msg, "role") and hasattr(msg, "content"):
                role = "Human" if msg.role == "user" else "Assistant"
                content = (
                    str(msg.content)[:100] + "..."
                    if len(str(msg.content)) > 100
                    else str(msg.content)
                )
                summary_parts.append(f"  {role}: {content}")

        return "\n".join(summary_parts)
