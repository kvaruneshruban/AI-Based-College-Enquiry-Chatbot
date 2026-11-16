"""
Pytest Automated Test Suite for Chat History & SQLite Database Integration.
"""

import os
import tempfile
import pytest
from chat_history_manager import (
    init_db,
    create_conversation,
    get_conversation,
    update_conversation_title,
    save_message,
    get_conversation_messages,
    list_conversations,
    delete_conversation,
    add_recent_search,
    get_recent_searches,
    generate_conversation_title,
    DEFAULT_RECENT_SEARCHES
)


@pytest.fixture
def temp_db():
    """Provides a fresh temporary SQLite database for isolated test execution."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_db_initialization_and_preseeded_searches(temp_db):
    """Verifies that init_db creates tables and seeds the required 8 recent searches."""
    searches = get_recent_searches(limit=15, db_path=temp_db)
    assert len(searches) == len(DEFAULT_RECENT_SEARCHES)
    for expected in DEFAULT_RECENT_SEARCHES:
        assert expected in searches


def test_title_generation():
    """Verifies smart ChatGPT-style conversation title generation."""
    t1 = generate_conversation_title("What undergraduate courses are offered?")
    assert "Undergraduate Courses" in t1 or "Courses" in t1

    t2 = generate_conversation_title("What is the annual tuition fee for B.Tech?")
    assert "Annual Tuition Fee" in t2 or "Tuition" in t2

    t3 = generate_conversation_title("Are hostel facilities available for boys and girls?")
    assert "Hostel" in t3

    t4 = generate_conversation_title("   ")
    assert t4 == "New Chat"


def test_create_and_retrieve_conversation(temp_db):
    """Verifies creating a conversation and retrieving its metadata."""
    conv_id = "test_conv_001"
    res_id = create_conversation(conv_id, title="Admissions Enquiry", db_path=temp_db)
    assert res_id == conv_id

    meta = get_conversation(conv_id, db_path=temp_db)
    assert meta is not None
    assert meta["id"] == conv_id
    assert meta["title"] == "Admissions Enquiry"


def test_save_and_restore_messages_with_meta(temp_db):
    """Verifies saving user and assistant messages with visual/confidence metadata and restoring them."""
    conv_id = "test_conv_002"

    # User message
    save_message(
        conv_id=conv_id,
        role="user",
        content="What are the B.Tech CSE fees?",
        meta=None,
        db_path=temp_db
    )

    # Bot response with metadata
    meta_dict = {
        "confidence": 0.95,
        "category": "Fees",
        "visual": {"image": "campus_main.jpg", "caption": "VR College Campus"}
    }
    save_message(
        conv_id=conv_id,
        role="assistant",
        content="The annual fee for B.Tech CSE is Rs. 1,50,000 per year.",
        meta=meta_dict,
        db_path=temp_db
    )

    # Restore messages
    msgs = get_conversation_messages(conv_id, db_path=temp_db)
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[0]["content"] == "What are the B.Tech CSE fees?"

    assert msgs[1]["role"] == "assistant"
    assert msgs[1]["content"] == "The annual fee for B.Tech CSE is Rs. 1,50,000 per year."
    assert msgs[1]["meta"] is not None
    assert msgs[1]["meta"]["category"] == "Fees"
    assert msgs[1]["meta"]["visual"]["image"] == "campus_main.jpg"

    # Check that conversation title was auto-updated from user query
    conv = get_conversation(conv_id, db_path=temp_db)
    assert "B.Tech" in conv["title"] or "Fees" in conv["title"]


def test_list_and_search_conversations(temp_db):
    """Verifies conversation listing, order (newest first), and text search."""
    create_conversation("c1", title="Hostel Accommodation", db_path=temp_db)
    create_conversation("c2", title="Campus Placements", db_path=temp_db)
    create_conversation("c3", title="Scholarship Eligibility", db_path=temp_db)

    # List all
    all_convs = list_conversations(db_path=temp_db)
    assert len(all_convs) >= 3
    ids = [c["id"] for c in all_convs]
    assert "c3" in ids and "c2" in ids and "c1" in ids

    # Search by title
    search_res = list_conversations(search_query="Hostel", db_path=temp_db)
    assert len(search_res) == 1
    assert search_res[0]["id"] == "c1"

    # Search by content inside message
    save_message("c2", "user", "Does Google or Microsoft visit for recruitment?", None, db_path=temp_db)
    msg_search = list_conversations(search_query="Microsoft", db_path=temp_db)
    assert len(msg_search) == 1
    assert msg_search[0]["id"] == "c2"


def test_delete_conversation(temp_db):
    """Verifies that deleting a conversation also cleans up all its associated messages."""
    conv_id = "to_delete_001"
    create_conversation(conv_id, "Temporary Chat", db_path=temp_db)
    save_message(conv_id, "user", "Hello", None, db_path=temp_db)
    save_message(conv_id, "assistant", "Hi there!", None, db_path=temp_db)

    assert get_conversation(conv_id, db_path=temp_db) is not None
    assert len(get_conversation_messages(conv_id, db_path=temp_db)) == 2

    success = delete_conversation(conv_id, db_path=temp_db)
    assert success is True
    assert get_conversation(conv_id, db_path=temp_db) is None
    assert len(get_conversation_messages(conv_id, db_path=temp_db)) == 0


def test_recent_searches_addition_and_bumping(temp_db):
    """Verifies adding a user query to recent searches and ensuring it moves to the top."""
    add_recent_search("How to apply for AICTE scholarship?", db_path=temp_db)
    searches = get_recent_searches(limit=5, db_path=temp_db)
    assert searches[0] == "How to apply for AICTE scholarship"

    # Add another query
    add_recent_search("What are the hostel dining timings?", db_path=temp_db)
    updated_searches = get_recent_searches(limit=5, db_path=temp_db)
    assert updated_searches[0] == "What are the hostel dining timings"
    assert updated_searches[1] == "How to apply for AICTE scholarship"

