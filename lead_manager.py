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
import pandas as pd
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEADS_FILE = os.path.join(BASE_DIR, "leads.csv")
UNANSWERED_FILE = os.path.join(BASE_DIR, "unanswered_queries.csv")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback_logs.csv")


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
    ref_no = f"APEX-{datetime.datetime.now().strftime('%y')}-{ref_seed:05d}"

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
