"""
Data Loader Module for AI-Based College Enquiry Chatbot.

Handles loading, validating, and preprocessing FAQ data from CSV,
as well as dynamic CRUD additions and deletions for knowledge base management.
"""

import os
from typing import List, Tuple, Optional
import pandas as pd

REQUIRED_COLUMNS = ["category", "question", "answer"]


class DataLoaderError(Exception):
    """Custom exception for data loading and validation errors."""
    pass


def load_faq_data(filepath: str) -> pd.DataFrame:
    """
    Loads and validates the college FAQ dataset from a CSV file.

    Parameters:
        filepath (str): Path to the FAQ CSV file.

    Returns:
        pd.DataFrame: Cleaned DataFrame with category, question, and answer columns.

    Raises:
        DataLoaderError: If file is missing, empty, or missing required columns.
    """
    if not os.path.exists(filepath):
        raise DataLoaderError(f"Dataset file not found at path: '{filepath}'. Please check the file path.")

    try:
        # Read CSV file
        df = pd.read_csv(filepath)
    except Exception as e:
        raise DataLoaderError(f"Error reading CSV file '{filepath}': {str(e)}")

    if df.empty:
        raise DataLoaderError(f"Dataset '{filepath}' is empty. At least one FAQ entry is required.")

    # Validate columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise DataLoaderError(
            f"Dataset '{filepath}' is missing required column(s): {', '.join(missing_cols)}. "
            f"Expected columns: {', '.join(REQUIRED_COLUMNS)}"
        )

    # Clean data: drop rows with null or whitespace-only questions or answers
    df = df.dropna(subset=["question", "answer"]).copy()

    # Convert to string and strip surrounding whitespace
    for col in REQUIRED_COLUMNS:
        df[col] = df[col].astype(str).str.strip()

    # Filter out empty strings
    df = df[(df["question"] != "") & (df["answer"] != "")].copy()

    if df.empty:
        raise DataLoaderError("No valid FAQ entries found after cleaning empty rows.")

    # Reset index for consistent integer indexing
    df = df.reset_index(drop=True)
    return df


def get_categories(df: pd.DataFrame) -> List[str]:
    """
    Returns a sorted list of unique categories in the dataset.
    """
    if "category" not in df.columns:
        return []
    cats = sorted([c for c in df["category"].dropna().unique().tolist() if c])
    return cats


def get_questions_by_category(df: pd.DataFrame, category: Optional[str] = None) -> List[str]:
    """
    Returns FAQ questions, optionally filtered by a specific category.
    """
    if df.empty or "question" not in df.columns:
        return []
    if category and category != "All Categories":
        filtered = df[df["category"].str.lower() == category.lower()]
        return filtered["question"].tolist()
    return df["question"].tolist()


def add_faq_entry(filepath: str, category: str, question: str, answer: str) -> pd.DataFrame:
    """
    Adds a new FAQ entry to the dataset CSV file and returns the refreshed DataFrame.
    """
    clean_cat = (category or "").strip()
    clean_q = (question or "").strip()
    clean_a = (answer or "").strip()

    if not clean_cat or not clean_q or not clean_a:
        raise DataLoaderError("Category, question, and answer cannot be empty.")

    # Ensure demo data tag for consistency
    if not clean_a.startswith("[DEMO DATA]"):
        clean_a = f"[DEMO DATA] {clean_a}"

    df = load_faq_data(filepath)

    # Check for duplicate questions
    if (df["question"].str.lower() == clean_q.lower()).any():
        raise DataLoaderError(f"An FAQ entry with the question '{clean_q}' already exists.")

    new_row = pd.DataFrame([{
        "category": clean_cat,
        "question": clean_q,
        "answer": clean_a
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(filepath, index=False)
    return df


def delete_faq_entry(filepath: str, question_to_delete: str) -> pd.DataFrame:
    """
    Deletes an FAQ entry from the dataset CSV file by exact question string.
    """
    clean_q = (question_to_delete or "").strip()
    df = load_faq_data(filepath)

    mask = df["question"].str.strip().str.lower() == clean_q.lower()
    if not mask.any():
        raise DataLoaderError(f"Question '{clean_q}' not found in knowledge base.")

    df = df[~mask].reset_index(drop=True)
    if df.empty:
        raise DataLoaderError("Cannot delete the last remaining FAQ in the knowledge base.")

    df.to_csv(filepath, index=False)
    return df
