"""
Lead and Analytics Manager for AI-Based College Enquiry Chatbot.

Handles:
- Prospective student admission leads (CRUD, CSV storage, reference number generation)
- Unanswered fallback queries tracking (for knowledge base gap identification)
- Student satisfaction feedback logging (Thumbs Up / Thumbs Down ratings)
"""

import os
import re
import datetime
import sqlite3
import pandas as pd
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEADS_FILE = os.path.join(BASE_DIR, "leads.csv")
APPLICATIONS_FILE = os.path.join(BASE_DIR, "applications.csv")
UNANSWERED_FILE = os.path.join(BASE_DIR, "unanswered_queries.csv")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback_logs.csv")
DB_FILE = os.path.join(BASE_DIR, "chat_history.db")


# -------------------------------------------------------------
# 1. Admission Leads Management
# -------------------------------------------------------------
def get_leads_df() -> pd.DataFrame:
    """Reads leads.csv or returns an empty structured DataFrame."""
    cols = ["timestamp", "ref_no", "name", "email", "phone", "course", "cutoff", "message", "status"]
    if not os.path.exists(LEADS_FILE):
        return pd.DataFrame(columns=cols)
    try:
        df = pd.read_csv(LEADS_FILE)
        for col in cols:
            if col not in df.columns:
                df[col] = ""
        return df
    except Exception:
        return pd.DataFrame(columns=cols)


def save_admission_lead(
    name: str,
    email: str,
    phone: str,
    course: str,
    cutoff: str = "",
    message: str = ""
) -> Dict[str, Any]:
    """
    Validates and stores a new student admission enquiry lead.
    Returns dict with status ('success' | 'error'), message, and reference number.
    """
    clean_name = (name or "").strip()
    clean_email = (email or "").strip().lower()
    clean_phone = re.sub(r"[^\d+]", "", (phone or "").strip())

    if not clean_name or len(clean_name) < 2:
        return {"status": "error", "message": "Please enter a valid full name."}

    if not clean_phone or len(clean_phone) < 10:
        return {"status": "error", "message": "Please enter a valid 10-digit mobile number."}

    if clean_email and ("@" not in clean_email or "." not in clean_email):
        return {"status": "error", "message": "Please enter a valid email address."}

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ref_seed = int(datetime.datetime.now().timestamp() % 100000)
    ref_no = f"VRCE-{datetime.datetime.now().strftime('%y')}-{ref_seed:05d}"

    new_lead = {
        "timestamp": timestamp,
        "ref_no": ref_no,
        "name": clean_name,
        "email": clean_email if clean_email else "N/A",
        "phone": clean_phone,
        "course": course if course else "General Engineering",
        "cutoff": (cutoff or "").strip() if cutoff else "N/A",
        "message": (message or "").strip() if message else "Campus enquiry via AI chatbot",
        "status": "Pending"
    }

    df = get_leads_df()
    df = pd.concat([df, pd.DataFrame([new_lead])], ignore_index=True)
    df.to_csv(LEADS_FILE, index=False)

    return {
        "status": "success",
        "message": "Enquiry registered successfully! Our admissions counselor will contact you shortly.",
        "ref_no": ref_no
    }


def update_lead_status(ref_no: str, new_status: str) -> bool:
    """Updates the processing status of a lead (e.g. 'Pending' -> 'Contacted')."""
    df = get_leads_df()
    if df.empty or "ref_no" not in df.columns:
        return False
    mask = df["ref_no"] == ref_no
    if mask.any():
        df.loc[mask, "status"] = new_status
        df.to_csv(LEADS_FILE, index=False)
        return True
    return False


# -------------------------------------------------------------
# 1B. Formal Admission Applications Management
# -------------------------------------------------------------
def init_applications_table(db_path: Optional[str] = None) -> None:
    """Initializes the admission_applications SQLite table if not exists."""
    path = db_path or DB_FILE
    try:
        with sqlite3.connect(path, timeout=5.0) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS admission_applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ref_no TEXT UNIQUE NOT NULL,
                    timestamp TEXT NOT NULL,
                    student_name TEXT NOT NULL,
                    dob TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    parent_name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    marks_12th TEXT NOT NULL,
                    department TEXT NOT NULL,
                    admission_category TEXT NOT NULL,
                    course_preference TEXT NOT NULL,
                    status TEXT DEFAULT 'Submitted'
                );
            """)
    except Exception:
        pass


def get_applications_df() -> pd.DataFrame:
    """Reads applications.csv or returns an empty structured DataFrame."""
    cols = [
        "timestamp", "ref_no", "student_name", "dob", "gender", "email",
        "phone", "parent_name", "address", "marks_12th", "department",
        "admission_category", "course_preference", "status"
    ]
    if not os.path.exists(APPLICATIONS_FILE):
        return pd.DataFrame(columns=cols)
    try:
        df = pd.read_csv(APPLICATIONS_FILE)
        for col in cols:
            if col not in df.columns:
                df[col] = ""
        return df
    except Exception:
        return pd.DataFrame(columns=cols)


def save_admission_application(
    student_name: str,
    dob: str,
    gender: str,
    email: str,
    phone: str,
    parent_name: str,
    address: str,
    marks_12th: str,
    department: str,
    admission_category: str,
    course_preference: str,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validates and persists a formal college admission application.
    Saves to:
    1. applications.csv (comprehensive fields)
    2. leads.csv (for Staff Desk compatibility)
    3. chat_history.db (SQLite database)
    Returns:
    dict: {"status": "success" | "error", "message": str, "ref_no": str, "data": dict}
    """
    clean_name = (student_name or "").strip()
    clean_dob = (str(dob) or "").strip()
    clean_gender = (gender or "").strip()
    clean_email = (email or "").strip().lower()
    clean_phone = re.sub(r"[^\d+]", "", (phone or "").strip())
    clean_parent = (parent_name or "").strip()
    clean_address = (address or "").strip()
    clean_marks = (marks_12th or "").strip()
    clean_dept = (department or "").strip()
    clean_category = (admission_category or "").strip()
    clean_course = (course_preference or "").strip()

    # 1. Full Name Validation
    if not clean_name or len(clean_name) < 2:
        return {"status": "error", "message": "Please enter student's valid full name (at least 2 characters)."}

    # 2. Date of Birth Validation
    if not clean_dob:
        return {"status": "error", "message": "Please enter or select a valid Date of Birth."}

    # 3. Gender Validation
    if not clean_gender or clean_gender in ["Select Gender", "Select"]:
        return {"status": "error", "message": "Please select student's gender."}

    # 4. Email Validation
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not clean_email or not re.match(email_pattern, clean_email):
        return {"status": "error", "message": "Please enter a valid email address (e.g., student@example.com)."}

    # 5. Mobile Number Validation
    digits_phone = re.sub(r"\D", "", clean_phone)
    if len(digits_phone) < 10:
        return {"status": "error", "message": "Please enter a valid 10-digit mobile number."}

    # 6. Parent / Guardian Name Validation
    if not clean_parent or len(clean_parent) < 2:
        return {"status": "error", "message": "Please enter Parent / Guardian Name (at least 2 characters)."}

    # 7. Residential Address Validation
    if not clean_address or len(clean_address) < 5:
        return {"status": "error", "message": "Please enter complete residential address."}

    # 8. Marks Validation
    if not clean_marks:
        return {"status": "error", "message": "Please enter 12th Standard / Diploma marks or percentage."}

    # 9. Department Validation
    if not clean_dept or clean_dept in ["Select Department", "Select"]:
        return {"status": "error", "message": "Please select a preferred department."}

    # 10. Admission Category Validation
    if not clean_category or clean_category in ["Select Category", "Select"]:
        return {"status": "error", "message": "Please select an admission category."}

    # 11. Course Preference Validation
    if not clean_course or clean_course in ["Select Course Preference", "Select"]:
        return {"status": "error", "message": "Please select a course preference."}

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ref_seed = int(datetime.datetime.now().timestamp() * 1000 % 100000)
    ref_no = f"VRCE-APP-{datetime.datetime.now().strftime('%y')}-{ref_seed:05d}"

    new_record = {
        "timestamp": timestamp,
        "ref_no": ref_no,
        "student_name": clean_name,
        "dob": clean_dob,
        "gender": clean_gender,
        "email": clean_email,
        "phone": clean_phone,
        "parent_name": clean_parent,
        "address": clean_address,
        "marks_12th": clean_marks,
        "department": clean_dept,
        "admission_category": clean_category,
        "course_preference": clean_course,
        "status": "Submitted"
    }

    # A. Save to applications.csv
    try:
        df_app = get_applications_df()
        df_app = pd.concat([df_app, pd.DataFrame([new_record])], ignore_index=True)
        df_app.to_csv(APPLICATIONS_FILE, index=False)
    except Exception:
        pass

    # B. Save into leads.csv for compatibility with Staff Desk
    lead_msg = (
        f"Formal Application [{ref_no}] | DOB: {clean_dob} | Gender: {clean_gender} | "
        f"Parent: {clean_parent} | Cat: {clean_category} | Addr: {clean_address}"
    )
    save_admission_lead(
        name=clean_name,
        email=clean_email,
        phone=clean_phone,
        course=f"{clean_dept} ({clean_course})",
        cutoff=clean_marks,
        message=lead_msg
    )

    # C. Save into SQLite database
    path = db_path or DB_FILE
    try:
        init_applications_table(path)
        with sqlite3.connect(path, timeout=5.0) as conn:
            conn.execute("""
                INSERT INTO admission_applications (
                    ref_no, timestamp, student_name, dob, gender, email, phone,
                    parent_name, address, marks_12th, department, admission_category,
                    course_preference, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ref_no, timestamp, clean_name, clean_dob, clean_gender, clean_email, clean_phone,
                clean_parent, clean_address, clean_marks, clean_dept, clean_category, clean_course, "Submitted"
            ))
    except Exception:
        pass

    return {
        "status": "success",
        "message": "College Admission Application Submitted Successfully!",
        "ref_no": ref_no,
        "data": new_record
    }


# -------------------------------------------------------------
# 2. Unanswered Fallback Queries Logger
# -------------------------------------------------------------
def get_unanswered_df() -> pd.DataFrame:
    """Reads unanswered_queries.csv or returns an empty DataFrame."""
    cols = ["timestamp", "query", "attempted_score", "suggested_category", "status"]
    if not os.path.exists(UNANSWERED_FILE):
        return pd.DataFrame(columns=cols)
    try:
        return pd.read_csv(UNANSWERED_FILE)
    except Exception:
        return pd.DataFrame(columns=cols)


def log_unanswered_query(query: str, attempted_score: float, suggested_category: Optional[str] = None) -> None:
    """Logs questions that did not meet the similarity threshold for admin review."""
    clean_q = (query or "").strip()
    if not clean_q or len(clean_q) < 3:
        return

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "timestamp": timestamp,
        "query": clean_q,
        "attempted_score": round(attempted_score, 4),
        "suggested_category": suggested_category if suggested_category else "General enquiries",
        "status": "Unresolved"
    }

    df = get_unanswered_df()
    if not df.empty and (df["query"].str.lower() == clean_q.lower()).any():
        # Update existing record back to Unresolved if re-queried
        mask = df["query"].str.lower() == clean_q.lower()
        df.loc[mask, "timestamp"] = timestamp
        df.loc[mask, "attempted_score"] = round(attempted_score, 4)
        df.loc[mask, "status"] = "Unresolved"
        df.to_csv(UNANSWERED_FILE, index=False)
        return

    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    df.to_csv(UNANSWERED_FILE, index=False)


def resolve_unanswered_query(query_text: str) -> None:
    """Marks an unanswered query as Resolved after adding to FAQ."""
    df = get_unanswered_df()
    if df.empty or "query" not in df.columns:
        return
    mask = df["query"].str.lower() == query_text.strip().lower()
    if mask.any():
        df.loc[mask, "status"] = "Resolved"
        df.to_csv(UNANSWERED_FILE, index=False)


# -------------------------------------------------------------
# 3. Student Satisfaction Feedback Logger
# -------------------------------------------------------------
def get_feedback_df() -> pd.DataFrame:
    """Reads feedback_logs.csv or returns an empty DataFrame."""
    cols = ["timestamp", "query", "answer_preview", "rating", "comment"]
    if not os.path.exists(FEEDBACK_FILE):
        return pd.DataFrame(columns=cols)
    try:
        return pd.read_csv(FEEDBACK_FILE)
    except Exception:
        return pd.DataFrame(columns=cols)


def log_feedback(query: str, answer: str, rating: str, comment: str = "") -> None:
    """
    Logs student satisfaction ratings (thumbs_up / thumbs_down) for chatbot answers.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "timestamp": timestamp,
        "query": (query or "")[:120],
        "answer_preview": (answer or "")[:120],
        "rating": rating,
        "comment": (comment or "").strip()
    }
    df = get_feedback_df()
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    df.to_csv(FEEDBACK_FILE, index=False)


def get_analytics_summary() -> Dict[str, Any]:
    """Computes summary metrics for the Admin Dashboard."""
    leads_df = get_leads_df()
    unanswered_df = get_unanswered_df()
    feedback_df = get_feedback_df()

    total_leads = len(leads_df)
    pending_leads = len(leads_df[leads_df["status"] == "Pending"]) if total_leads > 0 else 0
    unresolved_queries = len(unanswered_df[unanswered_df["status"] == "Unresolved"]) if not unanswered_df.empty else 0

    total_ratings = len(feedback_df)
    positive_ratings = len(feedback_df[feedback_df["rating"] == "positive"]) if total_ratings > 0 else 0
    satisfaction_rate = round((positive_ratings / total_ratings * 100), 1) if total_ratings > 0 else 100.0

    return {
        "total_leads": total_leads,
        "pending_leads": pending_leads,
        "unresolved_queries": unresolved_queries,
        "total_feedback": total_ratings,
        "satisfaction_rate": satisfaction_rate
    }
