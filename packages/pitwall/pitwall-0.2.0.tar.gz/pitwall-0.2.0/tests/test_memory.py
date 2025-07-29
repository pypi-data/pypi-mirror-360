"""
Tests for Pitwall memory management functionality.
"""

import json
import tempfile
from pathlib import Path

from pitwall.memory import ConversationMemory


class TestConversationMemory:
    """Test conversation memory functionality."""

    def setup_method(self):
        """Set up test with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.memory = ConversationMemory(memory_dir=Path(self.temp_dir))

    def test_create_session(self):
        """Test creating a new session."""
        session_id = self.memory.create_session("test-model")

        assert session_id is not None
        assert self.memory.has_active_session()
        assert self.memory.current_session_id == session_id

        # Check that session files are created
        session_file = self.memory._get_session_file(session_id)
        metadata_file = self.memory._get_session_metadata_file(session_id)

        assert session_file.exists()
        assert metadata_file.exists()

    def test_session_metadata(self):
        """Test session metadata is stored correctly."""
        test_metadata = {"test_key": "test_value"}
        session_id = self.memory.create_session("test-model", metadata=test_metadata)

        summary = self.memory.get_session_summary()

        assert summary is not None
        assert summary["session_id"] == session_id
        assert summary["model"] == "test-model"
        assert summary["metadata"]["test_key"] == "test_value"
        assert "created_at" in summary
        assert "updated_at" in summary

    def test_load_session(self):
        """Test loading an existing session."""
        # Create and save a session
        session_id = self.memory.create_session("test-model")
        original_id = self.memory.current_session_id

        # Clear memory and load the session
        self.memory.clear_session()
        assert not self.memory.has_active_session()

        # Load the session
        loaded = self.memory.load_session(session_id)

        assert loaded is True
        assert self.memory.has_active_session()
        assert self.memory.current_session_id == original_id

    def test_load_nonexistent_session(self):
        """Test loading a session that doesn't exist."""
        loaded = self.memory.load_session("nonexistent-id")
        assert loaded is False
        assert not self.memory.has_active_session()

    def test_list_sessions(self):
        """Test listing all sessions."""
        # Start with no sessions
        sessions = self.memory.list_sessions()
        assert len(sessions) == 0

        # Create a few sessions
        session1 = self.memory.create_session("model1", metadata={"name": "test1"})
        session2 = self.memory.create_session("model2", metadata={"name": "test2"})

        sessions = self.memory.list_sessions()
        assert len(sessions) == 2

        # Should be sorted by updated_at descending (newest first)
        assert sessions[0]["session_id"] == session2  # Most recent
        assert sessions[1]["session_id"] == session1

    def test_delete_session(self):
        """Test deleting a session."""
        session_id = self.memory.create_session("test-model")

        # Verify session exists
        assert self.memory.has_active_session()
        sessions = self.memory.list_sessions()
        assert len(sessions) == 1

        # Delete the session
        deleted = self.memory.delete_session(session_id)

        assert deleted is True
        assert not self.memory.has_active_session()

        sessions = self.memory.list_sessions()
        assert len(sessions) == 0

    def test_delete_nonexistent_session(self):
        """Test deleting a session that doesn't exist."""
        deleted = self.memory.delete_session("nonexistent-id")
        assert deleted is False

    def test_clear_all_sessions(self):
        """Test clearing all sessions."""
        # Create multiple sessions
        self.memory.create_session("model1")
        self.memory.create_session("model2")
        self.memory.create_session("model3")

        sessions = self.memory.list_sessions()
        assert len(sessions) == 3

        # Clear all sessions
        self.memory.clear_all_sessions()

        sessions = self.memory.list_sessions()
        assert len(sessions) == 0
        assert not self.memory.has_active_session()

    def test_export_session(self):
        """Test exporting a session."""
        session_id = self.memory.create_session("test-model", metadata={"test": "data"})

        # Export to temporary file
        export_path = Path(self.temp_dir) / "export.json"
        exported = self.memory.export_session(session_id, export_path)

        assert exported is True
        assert export_path.exists()

        # Verify export content
        with open(export_path, "r") as f:
            export_data = json.load(f)

        assert "metadata" in export_data
        assert "messages" in export_data
        assert export_data["metadata"]["session_id"] == session_id
        assert export_data["metadata"]["model"] == "test-model"

    def test_export_nonexistent_session(self):
        """Test exporting a session that doesn't exist."""
        export_path = Path(self.temp_dir) / "export.json"
        exported = self.memory.export_session("nonexistent-id", export_path)

        assert exported is False
        assert not export_path.exists()

    def test_get_context_summary(self):
        """Test getting conversation context summary."""
        self.memory.create_session("test-model")

        # Test with no messages
        summary = self.memory.get_context_summary()
        assert "No conversation history" in summary

        # Add some mock messages (this would normally come from PydanticAI)
        # For testing, we'll create simple mock objects with the required attributes
        class MockUserMessage:
            role = "user"
            content = "Hello"

        class MockAssistantMessage:
            role = "assistant"
            content = "Hi there!"

        self.memory.current_messages = [MockUserMessage(), MockAssistantMessage()]

        summary = self.memory.get_context_summary()
        assert "Last 2 messages" in summary
        assert "Human: Hello" in summary
        assert "Assistant: Hi there!" in summary
