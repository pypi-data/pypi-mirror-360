import pytest
from datetime import datetime
from isek.memory.memory import Memory, UserMemory, SessionSummary


@pytest.fixture
def memory():
    return Memory(debug_mode=True)


@pytest.fixture
def sample_user_memory():
    return UserMemory(
        memory="This is a test memory",
        topics=["test", "example"],
        last_updated=datetime.now(),
    )


@pytest.fixture
def sample_session_summary():
    return SessionSummary(
        summary="This is a test session summary",
        topics=["test", "session"],
        last_updated=datetime.now(),
    )


def test_add_user_memory(memory, sample_user_memory):
    """Test adding and retrieving user memories"""
    # Add memory
    memory_id = memory.add_user_memory(sample_user_memory, user_id="test_user")
    assert memory_id is not None

    # Retrieve memory
    retrieved_memory = memory.get_user_memory(memory_id, user_id="test_user")
    assert retrieved_memory is not None
    assert retrieved_memory.memory == "This is a test memory"
    assert "test" in retrieved_memory.topics


def test_get_user_memories(memory, sample_user_memory):
    """Test getting all memories for a user"""
    # Add multiple memories
    memory.add_user_memory(sample_user_memory, user_id="test_user")

    second_memory = UserMemory(memory="Another test memory", topics=["another", "test"])
    memory.add_user_memory(second_memory, user_id="test_user")

    # Get all memories
    memories = memory.get_user_memories(user_id="test_user")
    assert len(memories) == 2
    assert any(m.memory == "This is a test memory" for m in memories)
    assert any(m.memory == "Another test memory" for m in memories)


def test_delete_user_memory(memory, sample_user_memory):
    """Test deleting user memories"""
    # Add memory
    memory_id = memory.add_user_memory(sample_user_memory, user_id="test_user")

    # Verify it exists
    assert memory.get_user_memory(memory_id, user_id="test_user") is not None

    # Delete memory
    result = memory.delete_user_memory(memory_id, user_id="test_user")
    assert result is True

    # Verify it's deleted
    assert memory.get_user_memory(memory_id, user_id="test_user") is None


def test_session_summaries(memory, sample_session_summary):
    """Test session summary operations"""
    # Add session summary
    session_id = memory.add_session_summary(
        session_id="test_session", summary=sample_session_summary, user_id="test_user"
    )
    assert session_id == "test_session"

    # Retrieve session summary
    retrieved_summary = memory.get_session_summary("test_session", user_id="test_user")
    assert retrieved_summary is not None
    assert retrieved_summary.summary == "This is a test session summary"
    assert "test" in retrieved_summary.topics


def test_runs(memory):
    """Test run operations"""
    session_id = "test_session"

    # Add runs
    memory.add_run(session_id, {"action": "test_action", "result": "success"})
    memory.add_run(session_id, {"action": "another_action", "result": "success"})

    # Get runs
    runs = memory.get_runs(session_id)
    assert len(runs) == 2
    assert runs[0]["action"] == "test_action"
    assert runs[1]["action"] == "another_action"


def test_clear_memory(memory, sample_user_memory, sample_session_summary):
    """Test clearing all memory"""
    # Add some data
    memory.add_user_memory(sample_user_memory, user_id="test_user")
    memory.add_session_summary(
        "test_session", sample_session_summary, user_id="test_user"
    )
    memory.add_run("test_session", {"action": "test"})

    # Verify data exists
    assert len(memory.get_user_memories(user_id="test_user")) > 0
    assert memory.get_session_summary("test_session", user_id="test_user") is not None
    assert len(memory.get_runs("test_session")) > 0

    # Clear memory
    memory.clear()

    # Verify data is cleared
    assert len(memory.get_user_memories(user_id="test_user")) == 0
    assert memory.get_session_summary("test_session", user_id="test_user") is None
    assert len(memory.get_runs("test_session")) == 0


def test_memory_to_dict(memory, sample_user_memory, sample_session_summary):
    """Test converting memory to dictionary"""
    # Add some data
    memory.add_user_memory(sample_user_memory, user_id="test_user")
    memory.add_session_summary(
        "test_session", sample_session_summary, user_id="test_user"
    )
    memory.add_run("test_session", {"action": "test"})

    # Convert to dict
    memory_dict = memory.to_dict()

    # Verify structure
    assert "memories" in memory_dict
    assert "summaries" in memory_dict
    assert "runs" in memory_dict
    assert "test_user" in memory_dict["memories"]
    assert "test_user" in memory_dict["summaries"]
    assert "test_session" in memory_dict["runs"]


def test_user_memory_to_dict(sample_user_memory):
    """Test UserMemory to_dict method"""
    memory_dict = sample_user_memory.to_dict()

    assert "memory" in memory_dict
    assert "topics" in memory_dict
    assert "last_updated" in memory_dict
    assert memory_dict["memory"] == "This is a test memory"
    assert "test" in memory_dict["topics"]


def test_session_summary_to_dict(sample_session_summary):
    """Test SessionSummary to_dict method"""
    summary_dict = sample_session_summary.to_dict()

    assert "session_id" in summary_dict
    assert "summary" in summary_dict
    assert "topics" in summary_dict
    assert "last_updated" in summary_dict
    assert summary_dict["summary"] == "This is a test session summary"
    assert "test" in summary_dict["topics"]


def test_memory_repr(memory):
    """Test memory string representation"""
    repr_str = repr(memory)
    assert "Memory" in repr_str
    assert "users=0" in repr_str
    assert "sessions=0" in repr_str
    assert "runs=0" in repr_str


def test_multiple_users(memory, sample_user_memory):
    """Test memory isolation between users"""
    # Add memory for user1
    memory.add_user_memory(sample_user_memory, user_id="user1")

    # Add different memory for user2
    user2_memory = UserMemory(memory="User 2 memory", topics=["user2", "test"])
    memory.add_user_memory(user2_memory, user_id="user2")

    # Verify isolation
    user1_memories = memory.get_user_memories(user_id="user1")
    user2_memories = memory.get_user_memories(user_id="user2")

    assert len(user1_memories) == 1
    assert len(user2_memories) == 1
    assert user1_memories[0].memory == "This is a test memory"
    assert user2_memories[0].memory == "User 2 memory"
