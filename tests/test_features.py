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
    assert res["ref_no"].startswith("VRCE-")

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
import uuid

def test_unanswered_query_logging():
    test_q = f"What is the policy for autonomous drone club {uuid.uuid4()}?"
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


# -------------------------------------------------------------
# 6. Test Multi-Turn Context & Follow-Up Resolution
# -------------------------------------------------------------
def test_multiturn_followup_context():
    df = load_faq_data(CSV_PATH)
    bot = CollegeChatbot(df, similarity_threshold=0.25)

    history = []
    # Turn 1
    q1 = "What undergraduate courses are offered?"
    r1 = bot.get_response(q1, conversation_history=history)
    assert r1["status"] == "matched"
    assert "B.Tech" in r1["answer"]
    history.append({"role": "user", "content": q1})
    history.append({"role": "assistant", "content": r1.get("friendly_answer") or r1.get("answer")})

    # Turn 2: Follow-up question referring to previous turn
    q2 = "Explain the first one"
    r2 = bot.get_response(q2, conversation_history=history)
    assert r2["status"] == "matched"
    assert "B.Tech" in r2["answer"]
    friendly = r2.get("friendly_answer") or r2.get("answer")
    assert "B.Tech" in friendly
    assert "🎓" in friendly or "**" in friendly


# -------------------------------------------------------------
# 7. Test 'ok explain more' Elaboration & Visual 1:3 Mapping
# -------------------------------------------------------------
def test_ok_explain_more_and_visual_mapping():
    df = load_faq_data(CSV_PATH)
    bot = CollegeChatbot(df, similarity_threshold=0.25)

    history = []
    # Turn 1: Discuss courses
    q1 = "What courses do you offer?"
    r1 = bot.get_response(q1, conversation_history=history)
    history.append({"role": "user", "content": q1})
    history.append({"role": "assistant", "content": r1.get("friendly_answer") or r1.get("answer"), "meta": r1})

    # Turn 2: User says 'ok explain more'
    q2 = "ok explain more"
    r2 = bot.get_response(q2, conversation_history=history)
    assert r2["status"] == "matched"
    assert "Courses" in r2["category"]
    assert "visual" in r2
    assert "image" in r2["visual"]
    assert r2["visual"]["image"] in ["engineering_quad.jpg", "courses_seminar.jpg", "computer_lab.jpg", "campus_main.jpg"]
    assert "Key Details" in (r2.get("friendly_answer") or "")


# -------------------------------------------------------------
# 8. Test Smart College Fee Enquiry System
# -------------------------------------------------------------
def test_smart_college_fee_enquiry_system():
    df = load_faq_data(CSV_PATH)
    bot = CollegeChatbot(df, similarity_threshold=0.25)

    # 1. Test ECE Department Fee Query
    r_ece = bot.get_response("What is the ECE department fee?")
    ans_ece = r_ece.get("friendly_answer") or r_ece.get("answer")
    assert "1,25,000" in ans_ece
    assert "Electronics and Communication" in ans_ece
    assert "Complete College Fee Structure" in ans_ece
    # Confirm specific answer appears BEFORE the complete table
    idx_ece_specific = ans_ece.find("1,25,000")
    idx_ece_table = ans_ece.find("Complete College Fee Structure")
    assert idx_ece_specific < idx_ece_table

    # 2. Test Hostel Fee Query
    r_hostel = bot.get_response("How much is the hostel fee?")
    ans_hostel = r_hostel.get("friendly_answer") or r_hostel.get("answer")
    assert "Hostel Fee" in ans_hostel
    assert "Complete College Fee Structure" in ans_hostel
    idx_hostel_specific = ans_hostel.find("80,000")
    idx_hostel_table = ans_hostel.find("Complete College Fee Structure")
    assert idx_hostel_specific < idx_hostel_table

    # 3. Test Admission Fee Query
    r_adm = bot.get_response("What is the admission fee?")
    ans_adm = r_adm.get("friendly_answer") or r_adm.get("answer")
    assert r_adm["status"] == "matched"
    assert "5,000" in ans_adm
    assert "Complete College Fee Structure" in ans_adm
    idx_adm_specific = ans_adm.find("5,000")
    idx_adm_table = ans_adm.find("Complete College Fee Structure")
    assert idx_adm_specific < idx_adm_table

    # 4. Mandatory Question 1: What is the ECE fee?
    r_q1 = bot.get_response("What is the ECE fee?")
    assert r_q1["status"] == "matched"
    assert "1,25,000" in r_q1["friendly_answer"]
    assert "Complete College Fee Structure" in r_q1["friendly_answer"]
    assert r_q1["friendly_answer"].find("1,25,000") < r_q1["friendly_answer"].find("Complete College Fee Structure")

    # 5. Mandatory Question 2: What is the CSE fee?
    r_q2 = bot.get_response("What is the CSE fee?")
    assert r_q2["status"] == "matched"
    assert "1,50,000" in r_q2["friendly_answer"]
    assert "Computer Science and Engineering" in r_q2["friendly_answer"]
    assert "Complete College Fee Structure" in r_q2["friendly_answer"]
    assert r_q2["friendly_answer"].find("1,50,000") < r_q2["friendly_answer"].find("Complete College Fee Structure")

    # 6. Mandatory Question 3: How much is hostel accommodation?
    r_q3 = bot.get_response("How much is hostel accommodation?")
    assert r_q3["status"] == "matched"
    assert "80,000" in r_q3["friendly_answer"]
    assert "Complete College Fee Structure" in r_q3["friendly_answer"]
    assert r_q3["friendly_answer"].find("80,000") < r_q3["friendly_answer"].find("Complete College Fee Structure")

    # 7. Mandatory Question 4: What is the admission fee?
    r_q4 = bot.get_response("What is the admission fee?")
    assert r_q4["status"] == "matched"
    assert "5,000" in r_q4["friendly_answer"]
    assert "Complete College Fee Structure" in r_q4["friendly_answer"]
    assert r_q4["friendly_answer"].find("5,000") < r_q4["friendly_answer"].find("Complete College Fee Structure")

    # 8. Mandatory Question 5: Give me the complete fee structure.
    r_q5 = bot.get_response("Give me the complete fee structure.")
    assert r_q5["status"] == "matched"
    assert "overview of our college fees" in r_q5["friendly_answer"]
    assert "Complete College Fee Structure" in r_q5["friendly_answer"]
    assert r_q5["friendly_answer"].find("overview of our college fees") < r_q5["friendly_answer"].find("Complete College Fee Structure")

    # 9. Mandatory Question 6: What is the transport fee?
    r_q6 = bot.get_response("What is the transport fee?")
    assert r_q6["status"] == "matched"
    assert "20,000" in r_q6["friendly_answer"]
    assert "Complete College Fee Structure" in r_q6["friendly_answer"]
    assert r_q6["friendly_answer"].find("20,000") < r_q6["friendly_answer"].find("Complete College Fee Structure")

    # 10. Test 'fee details' query returns complete fee structure instead of fallback
    r_more = bot.get_response("fee details")
    assert r_more["status"] == "matched"
    assert "Course & Annual Tuition Fees" in r_more["friendly_answer"] or "Complete College Fee Structure" in r_more["friendly_answer"]
    assert "2. Other Fees" in r_more["friendly_answer"] or "Other College Fees" in r_more["friendly_answer"]
    assert "Computer Science Engineering" in r_more["friendly_answer"]
    assert "Hostel Fee" in r_more["friendly_answer"]


# -------------------------------------------------------------
# 9. Test Dynamic Image Manager & Interactive Cards
# -------------------------------------------------------------
def test_dynamic_image_manager_and_interactive_cards():
    import image_manager

    # 1. Verify all 15 categories are present
    catalog = image_manager.TOPIC_IMAGE_CATALOG
    assert len(catalog) == 15

    expected_categories = [
        "campus", "admissions", "courses", "cse", "ece", "laboratories",
        "library", "hostel", "transportation", "sports", "cultural",
        "symposiums", "placements", "scholarships", "faculty"
    ]
    for cat_id in expected_categories:
        assert cat_id in catalog
        # Verify each category has at least 2 image candidates
        assert len(catalog[cat_id]["images"]) >= 2

    # 2. Test Smart Image Selection on prompt examples
    test_cases = [
        ("Tell me about hostel facilities", "Hostel Facilities & Dining"),
        ("What is the fee structure?", "Scholarships & Financial Aid"),
        ("Show me the library", "Central Digital Library"),
        ("What are the placements?", "Corporate Placements & Career Cell"),
        ("Which courses are available?", "Engineering Courses"),
        ("Tell me about college events", "Cultural Events & Arts"),
        ("Tell me about the computer science department", "Computer Science Department"),
        ("What bus facilities are available?", "Campus Transportation Fleet"),
        ("What sports facilities are on campus?", "Sports & Athletic Arena")
    ]
    for q, expected_cat in test_cases:
        v = image_manager.get_dynamic_visual(q)
        assert v["category"] == expected_cat
        assert os.path.exists(os.path.join(image_manager.ASSETS_DIR, v["image"]))

    # 3. Test Anti-Repetition: consecutive calls avoid repeating immediately previous image
    last_img = None
    for _ in range(6):
        v = image_manager.get_dynamic_visual("Tell me about hostel facilities", last_image=last_img)
        if last_img is not None:
            assert v["image"] != last_img
        last_img = v["image"]

    # 4. Verify Interactive Cards
    cards = image_manager.get_all_interactive_cards()
    assert len(cards) == 15
    for c in cards:
        assert c["id"] and c["title"] and c["description"] and c["quick_prompt"]
        assert os.path.exists(os.path.join(image_manager.ASSETS_DIR, c["image"]))

    # 5. Verify Contextual Suggestion Chips
    chips = image_manager.get_contextual_chips("What is the fee structure?", "scholarships")
    assert len(chips) == 3
    for label, query in chips:
        assert label and query


# -------------------------------------------------------------
# 10. Test College Name Recognition & Strict Intent Priority
# -------------------------------------------------------------
def test_college_name_and_intent_recognition():
    df = load_faq_data(CSV_PATH)
    bot = CollegeChatbot(df, similarity_threshold=0.25)

    # 1. Test all variations of College Name
    name_queries = [
        "What is your college name?",
        "Tell me your college name.",
        "Which college is this?",
        "What is the name of your institution?",
        "Can you introduce your college?"
    ]
    expected_response_substr = "Our college name is **VR College of Engineering**. 😊 Welcome! I'm happy to help you with information about our college."

    for q in name_queries:
        res = bot.get_response(q)
        assert res["status"] == "matched"
        assert res["category"] == "College Name"
        assert "VR College of Engineering" in res["friendly_answer"]
        assert "Welcome! I'm happy to help you with information about our college." in res["friendly_answer"]
        # Strictly verify that NO fee structure table is returned
        assert "Complete College Fee Structure" not in res["friendly_answer"]
        assert "Annual Tuition Fees" not in res["friendly_answer"]

    # 2. Test 'What courses are available?' does NOT show fee table
    res_courses = bot.get_response("What courses are available?")
    assert res_courses["status"] == "matched"
    assert "Computer Science and Engineering" in res_courses["friendly_answer"]
    assert "Complete College Fee Structure" not in res_courses["friendly_answer"]

    # 3. Test 'Where is your college located?' does NOT show fee table
    res_loc = bot.get_response("Where is your college located?")
    assert res_loc["status"] == "matched"
    assert "Sector 4, Education City" in res_loc["friendly_answer"]
    assert "Complete College Fee Structure" not in res_loc["friendly_answer"]

    # 4. Test 'Tell me about scholarships.' does NOT show fee table
    res_schol = bot.get_response("Tell me about scholarships.")
    assert res_schol["status"] == "matched"
    assert "Merit Scholarships" in res_schol["friendly_answer"]
    assert "Complete College Fee Structure" not in res_schol["friendly_answer"]

    # 5. Test specific fee queries DO show fee details
    res_fee = bot.get_response("What is the fee for CSE?")
    assert res_fee["status"] == "matched"
    assert "1,50,000" in res_fee["friendly_answer"]
    assert "Complete College Fee Structure" in res_fee["friendly_answer"]
