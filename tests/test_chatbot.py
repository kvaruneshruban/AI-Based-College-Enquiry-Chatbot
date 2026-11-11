"""
Unit and Integration Tests for AI-Based College Enquiry Chatbot.

Tests cover:
- Greetings and conversational pleasantries
- Thank-you / Gratitude responses
- Farewell handling
- Course, Admission, Fee, Hostel, Library, Placement, and Contact queries
- Fallback for out-of-scope / unknown queries
- Empty and invalid inputs
- Missing / invalid CSV dataset handling
- Category filtering
"""

import os
import sys
import pytest
import pandas as pd

# Base project path - ensure project root is on sys.path
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from data_loader import load_faq_data, DataLoaderError, get_categories
from chatbot import CollegeChatbot, DEFAULT_FALLBACK_MESSAGE
CSV_PATH = os.path.join(PROJECT_DIR, "college_faq.csv")


@pytest.fixture(scope="module")
def bot():
    """Provides an initialized CollegeChatbot instance using sample dataset."""
    df = load_faq_data(CSV_PATH)
    return CollegeChatbot(faq_df=df, similarity_threshold=0.25)


# 1. Test Greeting Responses
@pytest.mark.parametrize("greeting", [
    "Hi",
    "Hello",
    "Good morning",
    "Hey there",
    "Good afternoon"
])
def test_greeting_responses(bot, greeting):
    res = bot.get_response(greeting)
    assert res["status"] == "greeting"
    assert "Hello" in res["answer"] or "Welcome" in res["answer"]
    assert res["confidence"] == 1.0


# 2. Test Thank-You Responses
@pytest.mark.parametrize("thanks", [
    "Thank you",
    "Thanks a lot",
    "Thank you so much",
    "Much appreciated"
])
def test_gratitude_responses(bot, thanks):
    res = bot.get_response(thanks)
    assert res["status"] == "gratitude"
    assert "welcome" in res["answer"].lower()
    assert res["confidence"] == 1.0


# 3. Test Farewell Responses
@pytest.mark.parametrize("farewell", [
    "Bye",
    "Goodbye",
    "See you later"
])
def test_farewell_responses(bot, farewell):
    res = bot.get_response(farewell)
    assert res["status"] == "farewell"
    assert "goodbye" in res["answer"].lower() or "day ahead" in res["answer"].lower()


# 4. Test Course Enquiries
def test_course_enquiry(bot):
    res = bot.get_response("What undergraduate courses are offered in your college?")
    assert res["status"] == "matched"
    assert "B.Tech" in res["answer"]
    assert res["category"] == "Courses"
    assert res["confidence"] >= 0.25


# 5. Test Admission Enquiries
def test_admission_enquiry(bot):
    res = bot.get_response("What is the admission procedure and eligibility criteria?")
    assert res["status"] == "matched"
    assert "admission" in res["answer"].lower() or "eligibility" in res["answer"].lower() or "10+2" in res["answer"]
    assert res["category"] == "Admission"
    assert res["confidence"] >= 0.25


# 6. Test Fee Enquiries
def test_fee_enquiry(bot):
    res = bot.get_response("How much is the annual tuition fee for B.Tech?")
    assert res["status"] == "matched"
    assert "fee" in res["answer"].lower() or "85,000" in res["answer"]
    assert res["category"] == "Fees"
    assert res["confidence"] >= 0.25


# 7. Test Hostel Enquiries
def test_hostel_enquiry(bot):
    res = bot.get_response("Are there hostel facilities for boys and girls on campus?")
    assert res["status"] == "matched"
    assert "hostel" in res["answer"].lower()
    assert res["category"] == "Hostel"
    assert res["confidence"] >= 0.25


# 8. Test Library Enquiries
def test_library_enquiry(bot):
    res = bot.get_response("What are the library timings and working hours?")
    assert res["status"] == "matched"
    assert "library" in res["answer"].lower() or "8:00 AM" in res["answer"]
    assert res["category"] == "Library"
    assert res["confidence"] >= 0.25


# 9. Test Placement Enquiries
def test_placement_enquiry(bot):
    res = bot.get_response("Which companies visit for campus recruitment and placements?")
    assert res["status"] == "matched"
    assert "recruitment" in res["answer"].lower() or "tcs" in res["answer"].lower() or "placement" in res["answer"].lower()
    assert res["category"] == "Placement"
    assert res["confidence"] >= 0.25


# 10. Test Contact Enquiries
def test_contact_enquiry(bot):
    res = bot.get_response("How can I contact the college admission office?")
    assert res["status"] == "matched"
    assert "contact" in res["answer"].lower() or "admission" in res["answer"].lower() or "+91" in res["answer"]
    assert res["category"] == "Contact"
    assert res["confidence"] >= 0.25


# 11. Test Unknown / Out-of-Domain Question (Fallback Trigger)
def test_unknown_question_fallback(bot):
    res = bot.get_response("How do I bake a chocolate cake with strawberry frosting?")
    assert res["status"] == "fallback"
    assert res["answer"] == DEFAULT_FALLBACK_MESSAGE
    assert res["category"] is None


# 12. Test Empty and Invalid Inputs
@pytest.mark.parametrize("empty_input", ["", "   ", "\t\n"])
def test_empty_input(bot, empty_input):
    res = bot.get_response(empty_input)
    assert res["status"] == "invalid"
    assert "valid question" in res["answer"].lower()
    assert res["confidence"] == 0.0


# 13. Test Missing CSV File Handling
def test_missing_csv_file():
    with pytest.raises(DataLoaderError) as exc_info:
        load_faq_data("non_existent_file_12345.csv")
    assert "not found" in str(exc_info.value).lower()


# 14. Test Category Filtering
def test_category_filtering(bot):
    # Query with category restricted to 'Hostel'
    res = bot.get_response("What are the fees?", category_filter="Hostel")
    assert res["status"] == "matched"
    assert res["category"] == "Hostel"
    assert "hostel" in res["answer"].lower()


# 15. Test Dataset Verification & Demonstration Marking
def test_dataset_verification():
    df = load_faq_data(CSV_PATH)
    assert len(df) >= 30, f"Expected at least 30 FAQ entries, found {len(df)}"
    categories = get_categories(df)
    expected_categories = [
        "Courses", "Departments", "Admission", "Fees", "Hostel",
        "Library", "Examination", "Placement", "Contact", "General enquiries"
    ]
    for cat in expected_categories:
        assert cat in categories, f"Expected category '{cat}' missing from dataset"

    # Verify that all answers are clearly marked as DEMO DATA
    for ans in df["answer"]:
        assert "[DEMO DATA]" in ans, f"Answer missing [DEMO DATA] prefix: {ans}"
