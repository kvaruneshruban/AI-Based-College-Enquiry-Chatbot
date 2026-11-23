"""
Unit and Integration Tests for College Admission Application Form & Backend.
Tests:
- save_admission_application validation (Name, DOB, Gender, Email, Phone, Parent Name, Address, Marks, Dept, Category, Course)
- Reference number format (VRCE-APP-26-XXXXX)
- CSV persistence (applications.csv and leads.csv)
- SQLite database persistence (admission_applications table)
- Reset form helper
"""

import os
import sys
import pytest
import sqlite3
import pandas as pd

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from lead_manager import (
    save_admission_application,
    get_applications_df,
    get_leads_df,
    APPLICATIONS_FILE,
    DB_FILE
)
from application_form import (
    DEPARTMENTS_LIST,
    ADMISSION_CATEGORIES_LIST,
    COURSE_PREFERENCES_LIST,
    GENDER_OPTIONS,
    clean_html_for_markdown
)


def test_save_admission_application_valid():
    """Tests complete, valid admission application submission."""
    res = save_admission_application(
        student_name="Priya Varma",
        dob="2007-08-22",
        gender="Female",
        email="priya.varma@example.com",
        phone="9876543210",
        parent_name="Dr. S. K. Varma",
        address="Flat 402, Royal Residency, Indiranagar, Bengaluru - 560038",
        marks_12th="96.2% (PCM: 292/300)",
        department="Computer Science & Engineering (CSE)",
        admission_category="General Merit (State CET / Direct)",
        course_preference="B.Tech Regular (4-Year Undergraduate)"
    )

    assert res["status"] == "success"
    assert "ref_no" in res
    assert res["ref_no"].startswith("VRCE-APP-")

    # Verify applications.csv
    df_app = get_applications_df()
    assert not df_app.empty
    match = df_app[df_app["ref_no"] == res["ref_no"]]
    assert len(match) == 1
    row = match.iloc[0]
    assert row["student_name"] == "Priya Varma"
    assert row["email"] == "priya.varma@example.com"
    assert row["department"] == "Computer Science & Engineering (CSE)"

    # Verify leads.csv contains lead entry for Staff Desk
    df_leads = get_leads_df()
    assert not df_leads.empty
    lead_match = df_leads[df_leads["name"] == "Priya Varma"]
    assert len(lead_match) >= 1

    # Verify SQLite database
    with sqlite3.connect(DB_FILE, timeout=5.0) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ref_no, student_name, marks_12th FROM admission_applications WHERE ref_no = ?", (res["ref_no"],))
        db_row = cursor.fetchone()
        assert db_row is not None
        assert db_row[0] == res["ref_no"]
        assert db_row[1] == "Priya Varma"


def test_save_admission_application_invalid_name():
    """Tests validation for missing or single-character full name."""
    res = save_admission_application(
        student_name="A",
        dob="2007-08-22",
        gender="Female",
        email="test@example.com",
        phone="9876543210",
        parent_name="Parent",
        address="123 Street",
        marks_12th="90%",
        department="Computer Science & Engineering (CSE)",
        admission_category="General Merit (State CET / Direct)",
        course_preference="B.Tech Regular (4-Year Undergraduate)"
    )
    assert res["status"] == "error"
    assert "name" in res["message"].lower()


def test_save_admission_application_invalid_email():
    """Tests validation for malformed email addresses."""
    res = save_admission_application(
        student_name="Rahul Sharma",
        dob="2007-08-22",
        gender="Male",
        email="invalid-email-address",
        phone="9876543210",
        parent_name="Parent",
        address="123 Street",
        marks_12th="90%",
        department="Computer Science & Engineering (CSE)",
        admission_category="General Merit (State CET / Direct)",
        course_preference="B.Tech Regular (4-Year Undergraduate)"
    )
    assert res["status"] == "error"
    assert "email" in res["message"].lower()


def test_save_admission_application_invalid_phone():
    """Tests validation for incomplete phone numbers."""
    res = save_admission_application(
        student_name="Rahul Sharma",
        dob="2007-08-22",
        gender="Male",
        email="rahul@example.com",
        phone="9876",
        parent_name="Parent",
        address="123 Street",
        marks_12th="90%",
        department="Computer Science & Engineering (CSE)",
        admission_category="General Merit (State CET / Direct)",
        course_preference="B.Tech Regular (4-Year Undergraduate)"
    )
    assert res["status"] == "error"
    assert "mobile" in res["message"].lower() or "phone" in res["message"].lower()


def test_save_admission_application_unselected_dropdowns():
    """Tests validation when user leaves dropdowns as 'Select...'."""
    res = save_admission_application(
        student_name="Rahul Sharma",
        dob="2007-08-22",
        gender="Select Gender",
        email="rahul@example.com",
        phone="9876543210",
        parent_name="Parent",
        address="123 Street, City",
        marks_12th="90%",
        department="Select Department",
        admission_category="General Merit (State CET / Direct)",
        course_preference="B.Tech Regular (4-Year Undergraduate)"
    )
    assert res["status"] == "error"
    assert "gender" in res["message"].lower()


def test_departments_and_categories_options():
    """Verifies that all required departments and categories are supported."""
    required_depts = ["CSE", "ECE", "EEE", "Mechanical", "Civil", "IT", "AI & DS"]
    joined_depts = " ".join(DEPARTMENTS_LIST)
    for dept in required_depts:
        assert dept in joined_depts

    assert len(ADMISSION_CATEGORIES_LIST) >= 5
    assert len(COURSE_PREFERENCES_LIST) >= 5
    assert len(GENDER_OPTIONS) >= 4


def test_clean_html_for_markdown_prevents_code_blocks():
    """
    Verifies that clean_html_for_markdown strips leading spaces from all lines,
    ensuring CommonMark never triggers 4-space indented code blocks (<pre><code>).
    """
    nested_html = """
        <div style="background: green;">
            <h2>🎉 Application Submitted Successfully!</h2>
            <div class="ref-box">
                <strong>Application Reference Number:</strong>
                <span>VRCE-APP-26-12345</span>
            </div>
            <ul>
                <li>Our Admissions Counselling Officer will verify your academic details.</li>
            </ul>
        </div>
    """
    cleaned = clean_html_for_markdown(nested_html)
    assert cleaned.startswith("<div")
    assert cleaned.endswith("</div>")
    for line in cleaned.splitlines():
        # No line should have 4 or more leading spaces
        assert not line.startswith("    "), f"Line has 4+ leading spaces: {line}"
        assert not line.startswith("\t"), f"Line starts with tab: {line}"
    assert "Application Submitted Successfully!" in cleaned
    assert "Application Reference Number:" in cleaned
    assert "Our Admissions Counselling Officer will verify your academic details." in cleaned
