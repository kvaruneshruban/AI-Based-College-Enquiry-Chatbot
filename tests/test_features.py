"""
Comprehensive Unit Tests for New Features:
- Lead Capture & Storage
- Feedback Logger
- Unanswered Query Tracker
- Knowledge Base CRUD (Add / Delete FAQ)
- Typo Tolerance & Fuzzy Matching
"""

import os
import sys
import pytest
import pandas as pd

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from data_loader import load_faq_data, add_faq_entry, delete_faq_entry, DataLoaderError
from chatbot import CollegeChatbot, preprocess_text
from lead_manager import (
    save_admission_lead,
    get_leads_df,
    update_lead_status,
    log_feedback,
    get_feedback_df,
    log_unanswered_query,
    get_unanswered_df,
    resolve_unanswered_query,
    get_analytics_summary
)

CSV_PATH = os.path.join(PROJECT_DIR, "college_faq.csv")


# -------------------------------------------------------------
# 1. Test Lead Capture Management
# -------------------------------------------------------------
def test_valid_admission_lead_saving():
    res = save_admission_lead(
        name="Karthik Raj",
        email="karthik@example.com",
        phone="9876543210",
        course="B.Tech Computer Science",
        cutoff="185.5",
        message="Interested in merit scholarship details."
    )
    assert res["status"] == "success"
    assert "ref_no" in res
    assert res["ref_no"].startswith("APEX-")

    df = get_leads_df()
    assert not df.empty
    saved = df[df["ref_no"] == res["ref_no"]]
    assert not saved.empty
    assert saved.iloc[0]["name"] == "Karthik Raj"
    assert saved.iloc[0]["status"] == "Pending"

    # Test updating status
    updated = update_lead_status(res["ref_no"], "Contacted")
    assert updated is True
    df_after = get_leads_df()
    assert df_after[df_after["ref_no"] == res["ref_no"]].iloc[0]["status"] == "Contacted"


def test_invalid_admission_lead():
    # Empty name
    res1 = save_admission_lead(name="", email="test@test.com", phone="9876543210", course="B.Tech")
    assert res1["status"] == "error"

    # Invalid phone (less than 10 digits)
    res2 = save_admission_lead(name="Rahul", email="rahul@test.com", phone="12345", course="B.Tech")
    assert res2["status"] == "error"


# -------------------------------------------------------------
# 2. Test Feedback & Analytics
# -------------------------------------------------------------
def test_feedback_logging_and_analytics():
    log_feedback(query="Hostel fee enquiry", answer="Hostel fee is Rs. 60,000", rating="positive", comment="Clear answer")
    log_feedback(query="B.Tech cutoff", answer="Cutoff varies", rating="negative", comment="Need more details")

    fb_df = get_feedback_df()
    assert not fb_df.empty
    assert len(fb_df) >= 2

    analytics = get_analytics_summary()
    assert analytics["total_leads"] >= 1
    assert analytics["total_feedback"] >= 2
    assert 0.0 <= analytics["satisfaction_rate"] <= 100.0


# -------------------------------------------------------------
# 3. Test Unanswered Query Logger
# -------------------------------------------------------------
def test_unanswered_query_logging():
    test_q = f"What is the policy for autonomous drone club 2026?"
    log_unanswered_query(test_q, attempted_score=0.12, suggested_category="General enquiries")

    df = get_unanswered_df()
    assert not df.empty
    match = df[df["query"] == test_q]
    assert not match.empty
    assert match.iloc[0]["status"] == "Unresolved"

    resolve_unanswered_query(test_q)
    df_resolved = get_unanswered_df()
    assert df_resolved[df_resolved["query"] == test_q].iloc[0]["status"] == "Resolved"


# -------------------------------------------------------------
# 4. Test FAQ CRUD Operations
# -------------------------------------------------------------
def test_faq_crud_operations(tmp_path):
    # Create a temporary copy of FAQ CSV for isolated testing
    temp_csv = tmp_path / "temp_faq.csv"
    orig_df = load_faq_data(CSV_PATH)
    orig_df.to_csv(temp_csv, index=False)

    initial_count = len(orig_df)
    test_cat = "Special Programs"
    test_q = "Does the college offer Aerospace Engineering?"
    test_a = "Aerospace Engineering will be introduced in the 2027 academic session."

    # Test Add
    updated_df = add_faq_entry(str(temp_csv), test_cat, test_q, test_a)
    assert len(updated_df) == initial_count + 1
    assert (updated_df["question"] == test_q).any()

    # Test Duplicate Add Error
    with pytest.raises(DataLoaderError):
        add_faq_entry(str(temp_csv), test_cat, test_q, test_a)

    # Test Delete
    deleted_df = delete_faq_entry(str(temp_csv), test_q)
    assert len(deleted_df) == initial_count
    assert not (deleted_df["question"] == test_q).any()


# -------------------------------------------------------------
# 5. Test Typo Tolerance & Fuzzy Matching in Chatbot
# -------------------------------------------------------------
def test_typo_resilience():
    df = load_faq_data(CSV_PATH)
    bot = CollegeChatbot(df, similarity_threshold=0.25)

    # Test typos that should still be matched correctly
    typo_queries = [
        ("What is the admision procedure?", "Admission"),
        ("Are scolorships available for students?", "Fees"),
        ("What is the hostal fee structure?", "Hostel"),
        ("What are the central librari timings?", "Library")
    ]

    for query, expected_cat in typo_queries:
        res = bot.get_response(query)
        assert res["status"] == "matched", f"Failed to match typo query: '{query}'"
        assert res["category"] == expected_cat, f"Wrong category for query '{query}': got {res['category']}, expected {expected_cat}"
