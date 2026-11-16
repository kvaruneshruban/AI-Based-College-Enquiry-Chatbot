"""
Unit Tests for Response Display Design & Helper Utilities:
- Heading and icon generation for different categories & queries
- Writing block structure verification
- Action bar components
"""

import os
import sys
import pytest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from app import get_answer_heading_and_icon


def test_get_answer_heading_and_icon_known_categories():
    heading, icon = get_answer_heading_and_icon("Courses", None, "B.Tech degrees offered")
    assert heading == "Academic Programs & Degree Courses"
    assert icon == "🎓"

    heading, icon = get_answer_heading_and_icon("Admission", None, "How to apply")
    assert heading == "Admissions Procedure & Eligibility Criteria"
    assert icon == "📝"

    heading, icon = get_answer_heading_and_icon("Fee", None, "Annual tuition fee")
    assert heading == "Tuition Fees & Complete Payment Schedule"
    assert icon == "💰"

    heading, icon = get_answer_heading_and_icon("Hostel", None, "Hostel rules")
    assert heading == "Campus Hostels & Residential Facilities"
    assert icon == "🏢"

    heading, icon = get_answer_heading_and_icon("Placement", None, "Top recruiters")
    assert heading == "Campus Placements & Recruiter Records"
    assert icon == "💼"


def test_get_answer_heading_and_icon_content_heuristics():
    heading, icon = get_answer_heading_and_icon(None, None, "The annual tuition fee is 1,50,000")
    assert "Fee" in heading
    assert icon == "💰"

    heading, icon = get_answer_heading_and_icon(None, None, "Hostel accommodation with wifi and mess")
    assert "Hostel" in heading
    assert icon == "🏢"


def test_get_answer_heading_and_icon_matched_question():
    heading, icon = get_answer_heading_and_icon(None, "What sports facilities exist on campus?", "Sports quad and courts")
    assert "What sports facilities exist on campus" in heading
    assert icon == "📘"


def test_get_answer_heading_and_icon_fallback():
    heading, icon = get_answer_heading_and_icon(None, None, "Random generic sentence")
    assert heading == "VR College Official Advisory"
    assert icon == "✨"
