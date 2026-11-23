"""
Unit and Integration Tests for English and Tamil Language Switching Functionality.

Verifies:
- Test 1: Select English and ask "What courses are available?" -> Answer in English.
- Test 2: Select Tamil and ask "What courses are available?" -> Answer in Tamil.
- Test 3: While chatting in Tamil, ask about hostel fees -> Answer in Tamil.
- Test 4: Switch back to English -> All new responses are in English.
- Tamil Greetings & Academic Queries.
- Welcome message language switching.
- Heading & Icon language switching.
- Application form validation error translations.
"""

import os
import sys
import pytest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from data_loader import load_faq_data
from chatbot import CollegeChatbot
from app import get_initial_messages, get_answer_heading_and_icon
from application_form import translate_error_to_tamil


@pytest.fixture(scope="module")
def bot():
    csv_path = os.path.join(PROJECT_DIR, "college_faq.csv")
    df = load_faq_data(csv_path)
    return CollegeChatbot(df)


def has_tamil(text: str) -> bool:
    """Checks whether the text contains Tamil Unicode script characters."""
    return any('\u0b80' <= c <= '\u0bff' for c in text)


def test_scenario_1_english_courses(bot):
    """Test 1: Select English and ask 'What courses are available?' -> Answer in English."""
    res = bot.get_response("What courses are available?", language="English")
    answer = res.get("friendly_answer") or res.get("answer")
    assert answer, "Response should not be empty"
    assert "offers the following" in answer or "Computer Science" in answer
    assert "VR College of Engineering" in answer
    # Ensure it is primarily English, not Tamil
    assert any(c.isascii() and c.isalpha() for c in answer)


def test_scenario_2_tamil_courses(bot):
    """Test 2: Select Tamil and ask 'What courses are available?' -> Answer in Tamil."""
    res = bot.get_response("What courses are available?", language="Tamil")
    answer = res.get("friendly_answer") or res.get("answer")
    assert answer, "Response should not be empty"
    assert has_tamil(answer), "Response must contain Tamil Unicode characters"
    assert "பாடப்பிரிவு" in answer or "பொறியியல்" in answer or "பட்டப்படிப்பு" in answer


def test_scenario_3_tamil_hostel_fees(bot):
    """Test 3: While in Tamil, ask about hostel fees -> Answer in Tamil."""
    res = bot.get_response("What is the hostel fee?", language="Tamil")
    answer = res.get("friendly_answer") or res.get("answer")
    assert answer, "Response should not be empty"
    assert has_tamil(answer), "Response must contain Tamil Unicode characters"
    assert "விடுதி" in answer or "கட்டணம்" in answer


def test_scenario_4_switch_back_to_english(bot):
    """Test 4: Switch back to English -> All new responses must be in English."""
    res = bot.get_response("What is the fee for CSE?", language="English")
    answer = res.get("friendly_answer") or res.get("answer")
    assert answer, "Response should not be empty"
    assert "Computer Science" in answer or "₹1,50,000" in answer
    # English response should not be in Tamil script
    tamil_chars = [c for c in answer if '\u0b80' <= c <= '\u0bff']
    assert len(tamil_chars) == 0, "English response should not contain Tamil script"


def test_tamil_pure_query(bot):
    """Test pure Tamil question inputs."""
    res = bot.get_response("கல்லூரியின் பெயர் என்ன?", language="Tamil")
    answer = res.get("friendly_answer") or res.get("answer")
    assert has_tamil(answer)
    assert "VR College of Engineering" in answer or "வி.ஆர்" in answer


def test_tamil_greeting(bot):
    """Test greeting in Tamil."""
    res = bot.get_response("வணக்கம்", language="Tamil")
    answer = res.get("friendly_answer") or res.get("answer")
    assert has_tamil(answer)


def test_welcome_message_language():
    """Verify welcome message switches dynamically based on selected language."""
    en_welcome = get_initial_messages(language="English")[0]["content"]
    assert "Welcome to the **VR College of Engineering" in en_welcome
    assert not has_tamil(en_welcome)

    ta_welcome = get_initial_messages(language="Tamil")[0]["content"]
    assert "வணக்கம்!" in ta_welcome
    assert has_tamil(ta_welcome)


def test_answer_heading_and_icon_language():
    """Verify answer headings render in English and Tamil."""
    en_title, en_icon = get_answer_heading_and_icon("Courses", language="English")
    assert en_title == "Academic Programs & Degree Courses"
    assert en_icon == "🎓"

    ta_title, ta_icon = get_answer_heading_and_icon("Courses", language="Tamil")
    assert ta_title == "கல்விப் பாடப்பிரிவுகள் மற்றும் பட்டங்கள்"
    assert ta_icon == "🎓"


def test_application_form_error_translation():
    """Verify application form validation errors translate accurately to Tamil."""
    en_err = "Please enter student's valid full name (at least 2 characters)."
    ta_err = translate_error_to_tamil(en_err)
    assert has_tamil(ta_err)
    assert "முழுப்" in ta_err
