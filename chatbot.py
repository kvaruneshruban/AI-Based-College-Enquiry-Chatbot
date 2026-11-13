"""
Chatbot Module for AI-Based College Enquiry Chatbot.

Implements TF-IDF vectorization, Cosine Similarity matching, greeting handling,
gratitude detection, fallback responses, fuzzy typo-tolerance, and interaction logging.
"""

import re
import difflib
import datetime
from typing import Dict, Any, Optional, List
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from lead_manager import log_unanswered_query

# Standard patterns for conversational intents
GREETING_PATTERNS = [
    r"^(hi|hello|hey|heya|howdy)\b",
    r"^good\s+(morning|afternoon|evening|day)\b",
    r"^(greetings|namaste|welcome|vanakkam)\b"
]

GRATITUDE_PATTERNS = [
    r"\b(thank\s+you|thanks|thank\s+u|thx|much\s+appreciated|appreciate\s+it|nandri)\b"
]

FAREWELL_PATTERNS = [
    r"\b(bye|goodbye|see\s+you|have\s+a\s+good\s+day|cya)\b"
]

DEFAULT_FALLBACK_MESSAGE = (
    "I am sorry, but I couldn't find verified information regarding your enquiry in the college database. "
    "Please try rephrasing your question or contact the College Admissions / Administrative Desk at "
    "+91 98765 43210 or email admissions@demo-college.edu. [DEMO DATA]"
)


def preprocess_text(text: str) -> str:
    """
    Lightweight NLP preprocessing and token normalization.
    Converts to lowercase and normalizes common academic query plurals, typos,
    abbreviations, and inflections to ensure high recall between questions
    and student queries without heavy external libraries.
    """
    text = text.lower().strip()
    
    # Common academic typos and abbreviations
    typo_replacements = {
        r"\badmision\b": "admission",
        r"\badmisn\b": "admission",
        r"\badmissoin\b": "admission",
        r"\bscolorship\b": "scholarship",
        r"\bscholorship\b": "scholarship",
        r"\bscolorships\b": "scholarship",
        r"\bhostal\b": "hostel",
        r"\bhostle\b": "hostel",
        r"\belgibility\b": "eligibility",
        r"\belegibility\b": "eligibility",
        r"\beligiblity\b": "eligibility",
        r"\blibrari\b": "library",
        r"\blibary\b": "library",
        r"\blibrery\b": "library",
        r"\bplcmnt\b": "placement",
        r"\bplacmnt\b": "placement",
        r"\bplacemnts\b": "placement",
        r"\btranspot\b": "transport",
        r"\btransprot\b": "transport",
        r"\bcolg\b": "college",
        r"\bclg\b": "college",
        r"\bclge\b": "college",
        r"\bdept\b": "department",
        r"\bdepts\b": "department",
        r"\bfees\b": "fee",
        r"\bfeee\b": "fee",
        r"\bcourses\b": "course",
        r"\bcources\b": "course",
        r"\bhostels\b": "hostel",
        r"\blibraries\b": "library",
        r"\bdepartments\b": "department",
        r"\btimings\b": "timing",
        r"\bhours\b": "hour",
        r"\bfacilities\b": "facility",
        r"\badmissions\b": "admission",
        r"\bexams\b": "examination",
        r"\bexaminations\b": "examination",
        r"\bplacements\b": "placement",
        r"\bcontacts\b": "contact",
        r"\bdetails\b": "detail",
        r"\bbranches\b": "department",
        r"\bprograms\b": "course"
    }
    for pat, rep in typo_replacements.items():
        text = re.sub(pat, rep, text)
    return text


class CollegeChatbot:
    """
    Intelligent College Enquiry Chatbot powered by TF-IDF & Cosine Similarity,
    augmented with Fuzzy Sequence Matching for typo resilience.
    """

    def __init__(self, faq_df: pd.DataFrame, similarity_threshold: float = 0.25):
        """
        Initializes the chatbot with an FAQ DataFrame and trains the TF-IDF Vectorizer.

        Parameters:
            faq_df (pd.DataFrame): DataFrame containing columns ['category', 'question', 'answer'].
            similarity_threshold (float): Minimum cosine similarity required to return an answer.
        """
        self.faq_df = faq_df.copy().reset_index(drop=True)
        self.similarity_threshold = similarity_threshold
        self.logs: List[Dict[str, Any]] = []

        # Initialize TF-IDF Vectorizer with unigrams and bigrams
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2)
        )

        # Preprocess FAQ questions for higher matching accuracy
        self.processed_questions = self.faq_df["question"].apply(preprocess_text).tolist()
        self.question_vectors = self.vectorizer.fit_transform(self.processed_questions)

    def set_threshold(self, new_threshold: float) -> None:
        """Updates the similarity threshold."""
        self.similarity_threshold = max(0.0, min(1.0, float(new_threshold)))

    def _is_greeting(self, text: str) -> bool:
        """Checks if the user query is a greeting."""
        clean = text.lower().strip()
        return any(re.search(pat, clean) for pat in GREETING_PATTERNS)

    def _is_gratitude(self, text: str) -> bool:
        """Checks if the user query is expressing gratitude."""
        clean = text.lower().strip()
        return any(re.search(pat, clean) for pat in GRATITUDE_PATTERNS)

    def _is_farewell(self, text: str) -> bool:
        """Checks if the user query is a farewell."""
        clean = text.lower().strip()
        return any(re.search(pat, clean) for pat in FAREWELL_PATTERNS)

    def get_response(self, user_query: str, category_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Processes a student's natural language enquiry and returns the best matching answer.

        Parameters:
            user_query (str): The natural language query from the student.
            category_filter (str, optional): Category name to restrict search, or None for all.

        Returns:
            dict: {
                "answer": str,
                "matched_question": Optional[str],
                "category": Optional[str],
                "confidence": float,
                "status": "greeting" | "gratitude" | "farewell" | "matched" | "fallback" | "invalid",
                "is_fuzzy": bool
            }
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Validate empty/invalid input
        if not user_query or not user_query.strip():
            response = {
                "answer": "Please enter a valid question or enquiry so I can assist you.",
                "matched_question": None,
                "category": None,
                "confidence": 0.0,
                "status": "invalid",
                "is_fuzzy": False
            }
            self._log_interaction(timestamp, "INVALID_INPUT", 0.0, "None", "invalid")
            return response

        cleaned_query = user_query.strip()

        # 2. Check for Greetings
        if self._is_greeting(cleaned_query):
            response = {
                "answer": (
                    "Hello! Welcome to the AI College Enquiry Assistant. "
                    "How can I help you today? You can ask me about courses, admissions, fees, "
                    "hostel facilities, placements, and more!"
                ),
                "matched_question": None,
                "category": "Greeting",
                "confidence": 1.0,
                "status": "greeting",
                "is_fuzzy": False
            }
            self._log_interaction(timestamp, "GREETING", 1.0, "Greeting", "greeting")
            return response

        # 3. Check for Gratitude / Thank you
        if self._is_gratitude(cleaned_query):
            response = {
                "answer": (
                    "You're very welcome! Feel free to ask if you have any more questions about the college. "
                    "Best of luck with your academic journey!"
                ),
                "matched_question": None,
                "category": "Gratitude",
                "confidence": 1.0,
                "status": "gratitude",
                "is_fuzzy": False
            }
            self._log_interaction(timestamp, "GRATITUDE", 1.0, "Gratitude", "gratitude")
            return response

        # 4. Check for Farewell
        if self._is_farewell(cleaned_query):
            response = {
                "answer": "Goodbye! Have a wonderful day ahead. Reach out anytime if you need more information.",
                "matched_question": None,
                "category": "Farewell",
                "confidence": 1.0,
                "status": "farewell",
                "is_fuzzy": False
            }
            self._log_interaction(timestamp, "FAREWELL", 1.0, "Farewell", "farewell")
            return response

        # 5. Apply category filter if specified
        target_df = self.faq_df
        target_indices = None
        if category_filter and category_filter != "All Categories":
            mask = target_df["category"].str.lower() == category_filter.lower()
            if mask.any():
                target_indices = target_df[mask].index.tolist()

        # 6. TF-IDF vectorization & Cosine Similarity calculation
        norm_query = preprocess_text(cleaned_query)
        query_vector = self.vectorizer.transform([norm_query])
        similarities = cosine_similarity(query_vector, self.question_vectors).flatten()

        if target_indices is not None:
            # Mask out non-selected categories by setting their similarity to -1
            masked_sims = similarities.copy()
            for idx in range(len(masked_sims)):
                if idx not in target_indices:
                    masked_sims[idx] = -1.0
            best_idx = int(masked_sims.argmax())
            best_score = float(masked_sims[best_idx])
        else:
            best_idx = int(similarities.argmax())
            best_score = float(similarities[best_idx])

        # 7. Fuzzy Typo Matching Fallback (if TF-IDF score is borderline or low)
        is_fuzzy = False
        valid_indices = target_indices if target_indices is not None else list(range(len(self.processed_questions)))

        if best_score < self.similarity_threshold and valid_indices:
            best_fuzzy_idx = best_idx
            best_fuzzy_score = 0.0

            q_words = set(norm_query.split())
            for idx in valid_indices:
                faq_norm = self.processed_questions[idx]
                seq_ratio = difflib.SequenceMatcher(None, norm_query, faq_norm).ratio()
                
                # Check token overlap
                faq_words = set(faq_norm.split())
                overlap = len(q_words & faq_words) / max(1, len(q_words))
                combined_fuzzy = max(seq_ratio, overlap * 0.85)

                if combined_fuzzy > best_fuzzy_score:
                    best_fuzzy_score = combined_fuzzy
                    best_fuzzy_idx = idx

            # If fuzzy similarity is convincing, promote it
            if best_fuzzy_score >= 0.50:
                boosted_score = round(max(best_score, best_fuzzy_score * 0.75), 4)
                if boosted_score >= self.similarity_threshold:
                    best_idx = best_fuzzy_idx
                    best_score = boosted_score
                    is_fuzzy = True

        # 8. Threshold Evaluation
        if best_score >= self.similarity_threshold:
            matched_row = self.faq_df.iloc[best_idx]
            response = {
                "answer": matched_row["answer"],
                "matched_question": matched_row["question"],
                "category": matched_row["category"],
                "confidence": round(best_score, 4),
                "status": "matched",
                "is_fuzzy": is_fuzzy
            }
            self._log_interaction(
                timestamp,
                f"Len: {len(cleaned_query)} chars",
                round(best_score, 4),
                matched_row["category"],
                "matched"
            )
        else:
            # Query not resolved: log into unanswered queries for administrative review
            log_unanswered_query(cleaned_query, best_score, category_filter)

            response = {
                "answer": DEFAULT_FALLBACK_MESSAGE,
                "matched_question": None,
                "category": None,
                "confidence": round(best_score, 4),
                "status": "fallback",
                "is_fuzzy": False
            }
            self._log_interaction(
                timestamp,
                f"Len: {len(cleaned_query)} chars",
                round(best_score, 4),
                "None",
                "fallback"
            )

        return response

    def _log_interaction(self, timestamp: str, query_meta: str, score: float, category: str, status: str) -> None:
        """
        Safely logs interaction metadata without storing raw sensitive personal details.
        """
        self.logs.append({
            "timestamp": timestamp,
            "query_meta": query_meta,
            "similarity_score": score,
            "category": category,
            "status": status
        })

    def get_logs_df(self) -> pd.DataFrame:
        """Returns the interaction logs as a pandas DataFrame."""
        if not self.logs:
            return pd.DataFrame(columns=["timestamp", "query_meta", "similarity_score", "category", "status"])
        return pd.DataFrame(self.logs)


if __name__ == "__main__":
    import os
    from data_loader import load_faq_data

    csv_path = os.path.join(os.path.dirname(__file__), "college_faq.csv")
    print("==================================================")
    print("   🎓 AI-Based College Enquiry Chatbot (CLI Mode)")
    print("==================================================")
    print("Loading dataset from:", csv_path)

    try:
        faq_df = load_faq_data(csv_path)
        bot = CollegeChatbot(faq_df, similarity_threshold=0.25)
        print(f"Loaded {len(faq_df)} FAQs successfully! Ready for queries.")
        print("Type 'exit' or 'quit' to stop.\n")

        while True:
            try:
                user_q = input("Student: ")
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye!")
                break

            if user_q.strip().lower() in ["exit", "quit"]:
                print("Bot: Goodbye! Have a wonderful day.")
                break

            resp = bot.get_response(user_q)
            print(f"Bot: {resp['answer']}")
            if resp.get("status") == "matched":
                fuzzy_tag = " [Fuzzy Matched]" if resp.get("is_fuzzy") else ""
                print(f"   [Category: {resp['category']} | Confidence: {resp['confidence']:.2f}{fuzzy_tag}]")
            elif resp.get("status") == "fallback":
                print(f"   [Fallback Triggered | Score: {resp['confidence']:.2f}]")
            print()
    except Exception as e:
        print(f"Error starting chatbot: {e}")
