"""
End-to-end integration tests for the ChatGPT-Style Sidebar & SQLite Persistence
for VR College of Engineering Chatbot.

Verifies:
1. New questions automatically appear in Recent Searches.
2. Previous conversations can be reopened and restored with full message history and metadata.
3. Conversation history survives database re-opening (persists across application restarts).
4. New Chat creates a separate conversation without deleting previous chats.
5. Search Conversations finds previous chats by title and message contents.
6. Delete functionality removes individual conversations cleanly.
"""

import os
import tempfile
import pytest
import chat_history_manager as chm


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    chm.init_db(path)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_sidebar_recent_searches_flow(temp_db):
    # 1. Verify default recent searches are seeded
    initial_searches = chm.get_recent_searches(limit=10, db_path=temp_db)
    assert len(initial_searches) == 8
    assert "Available Engineering Courses" in initial_searches
    assert "College Fee Structure" in initial_searches

    # 2. Add a new query and check that it appears at the very top of Recent Searches
    new_query = "What is the B.Tech CSE cutoff for 2026?"
    chm.add_recent_search(new_query, db_path=temp_db)
    updated_searches = chm.get_recent_searches(limit=10, db_path=temp_db)
    assert updated_searches[0] == "What is the B.Tech CSE cutoff for 2026"


def test_sidebar_conversation_lifecycle(temp_db):
    # 1. Create first conversation
    conv1_id = "conv_test_001"
    q1 = "What are the hostel fee details?"
    chm.create_conversation(conv1_id, title="New Chat", db_path=temp_db)
    chm.save_message(conv1_id, "user", q1, None, db_path=temp_db)
    ans1 = "The annual hostel fee at VR College of Engineering is Rs. 65,000 including mess."
    meta1 = {"status": "matched", "category": "Hostel", "confidence": 0.95}
    chm.save_message(conv1_id, "assistant", ans1, meta1, db_path=temp_db)

    # Check conversation title auto-updated
    conv1 = chm.get_conversation(conv1_id, db_path=temp_db)
    assert conv1 is not None
    assert "Hostel Fee Details" in conv1["title"]

    # 2. Simulate "➕ New Chat": creates a second conversation
    import time
    time.sleep(0.02)
    conv2_id = "conv_test_002"
    q2 = "What companies visit for placements?"
    chm.create_conversation(conv2_id, title="New Chat", db_path=temp_db)
    chm.save_message(conv2_id, "user", q2, None, db_path=temp_db)
    ans2 = "Top recruiters include TCS, Infosys, Wipro, and Cognizant with highest package 14 LPA."
    chm.save_message(conv2_id, "assistant", ans2, {"status": "matched", "category": "Placements"}, db_path=temp_db)

    # 3. Verify both conversations exist in Previous Conversations
    all_convs = chm.list_conversations(db_path=temp_db)
    assert len(all_convs) == 2
    # Latest conversation appears first
    assert all_convs[0]["id"] == conv2_id
    assert all_convs[1]["id"] == conv1_id

    # 4. Reopen conversation 1 and verify full restoration of messages & metadata
    msgs1 = chm.get_conversation_messages(conv1_id, db_path=temp_db)
    assert len(msgs1) == 2
    assert msgs1[0]["role"] == "user"
    assert msgs1[0]["content"] == q1
    assert msgs1[1]["role"] == "assistant"
    assert msgs1[1]["content"] == ans1
    assert msgs1[1]["meta"]["category"] == "Hostel"
    assert msgs1[1]["meta"]["confidence"] == 0.95

    # 5. Test Search Conversations filter
    # Search by title/query
    search_hostel = chm.list_conversations(search_query="Hostel", db_path=temp_db)
    assert len(search_hostel) == 1
    assert search_hostel[0]["id"] == conv1_id

    search_recruiter = chm.list_conversations(search_query="recruiter", db_path=temp_db)
    assert len(search_recruiter) == 1
    assert search_recruiter[0]["id"] == conv2_id

    # 6. Delete conversation 1 and verify conversation 2 remains intact
    chm.delete_conversation(conv1_id, db_path=temp_db)
    remaining_convs = chm.list_conversations(db_path=temp_db)
    assert len(remaining_convs) == 1
    assert remaining_convs[0]["id"] == conv2_id
    assert chm.get_conversation(conv1_id, db_path=temp_db) is None
    assert len(chm.get_conversation_messages(conv1_id, db_path=temp_db)) == 0


def test_persistence_across_sessions(temp_db):
    conv_id = "session_persist_123"
    chm.create_conversation(conv_id, title="Campus Tour", db_path=temp_db)
    chm.save_message(conv_id, "user", "Tell me about the campus", None, db_path=temp_db)
    chm.save_message(conv_id, "assistant", "VR College has a 50-acre green campus.", None, db_path=temp_db)

    # Simulate app close and restart by re-initializing connection on same db file
    chm.init_db(temp_db)
    convs = chm.list_conversations(db_path=temp_db)
    assert any(c["id"] == conv_id for c in convs)

    msgs = chm.get_conversation_messages(conv_id, db_path=temp_db)
    assert len(msgs) == 2
    assert msgs[0]["content"] == "Tell me about the campus"
    assert msgs[1]["content"] == "VR College has a 50-acre green campus."
