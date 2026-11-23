"""
Chatbot Module for AI-Based College Enquiry Chatbot.

Implements TF-IDF vectorization, Cosine Similarity matching, conversational intent handling,
gratitude detection, fallback responses, fuzzy typo-tolerance, multi-turn conversation memory,
and ChatGPT-like AI conversational responses via Google Gemini with local friendly fallbacks.
"""

import re
import difflib
import datetime
from typing import Dict, Any, Optional, List
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from lead_manager import log_unanswered_query
from fee_manager import is_fee_enquiry, generate_smart_fee_response
from intent_detector import classify_intent, get_intent_response, Intent
from ai_agent import (
    resolve_followup_query,
    is_ai_available,
    generate_llm_response,
    generate_local_friendly_response,
    get_topic_visual
)

# Standard patterns for conversational intents (English and Tamil)
GREETING_PATTERNS = [
    r"^(hi|hello|hey|heya|howdy)\b",
    r"^good\s+(morning|afternoon|evening|day)\b",
    r"^(greetings|namaste|welcome|vanakkam)\b",
    r"\b(வணக்கம்|நமஸ்காரம்|காலை\s+வணக்கம்|மாலை\s+வணக்கம்|ஹலோ)\b"
]

GRATITUDE_PATTERNS = [
    r"\b(thank\s+you|thanks|thank\s+u|thx|much\s+appreciated|appreciate\s+it|nandri)\b",
    r"\b(நன்றி|மிக்க\s+நன்றி|ரொம்ப\s+நன்றி)\b"
]

FAREWELL_PATTERNS = [
    r"\b(bye|goodbye|see\s+you|have\s+a\s+good\s+day|cya)\b",
    r"\b(விடைபெறுகிறேன்|போய்\s+வருகிறேன்|நன்றி\s+வணக்கம்|பை)\b"
]

DEFAULT_FALLBACK_MESSAGE = (
    "I am sorry, but I couldn't find verified information regarding your enquiry in the college database. "
    "Please try rephrasing your question or contact the VR College of Engineering Admissions / Administrative Desk at "
    "+91 98765 43210 or email admissions@vrcollege.edu. [DEMO DATA]"
)

DEFAULT_FALLBACK_MESSAGE_TAMIL = (
    "மன்னிக்கவும், தங்களின் கேள்விக்கான சரிபார்க்கப்பட்ட தகவல் கல்லூரி தரவுத்தளத்தில் கிடைக்கவில்லை. "
    "தயவுசெய்து கேள்வியை வேறு விதமாக கேட்கவும் அல்லது வி.ஆர் பொறியியல் கல்லூரி சேர்க்கை உதவி மையத்தைத் தொடர்பு கொள்ளவும்: "
    "+91 98765 43210 அல்லது மின்னஞ்சல் admissions@vrcollege.edu."
)


def preprocess_text(text: str) -> str:
    """
    Lightweight NLP preprocessing and token normalization.
    Converts to lowercase and normalizes common academic query plurals, typos,
    abbreviations, and inflections to ensure high recall between questions
    and student queries without heavy external libraries.
    """
    text = text.lower().strip()

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

    # Tamil academic keyword mapping to English tokens for high-recall TF-IDF matching
    tamil_to_english = [
        (r"பாடப்பிரிவு(கள்)?|படிப்புகள்|துறைகள்|பாடங்கள்|பாடப்பிரிவுகள்", "course undergraduate b.tech programs degree"),
        (r"கட்டணம்|கட்டணங்கள்|கல்விக்கட்டணம்|செலவு|பணம்|பீஸ்", "fee tuition fees structure installment"),
        (r"விடுதி|ஹாஸ்டல்|தங்குமிடம்|உணவுக்கூடம்", "hostel accommodation rooms mess boys girls"),
        (r"சேர்க்கை|அட்மிஷன்|விண்ணப்பம்|விண்ணப்பிக்க", "admission eligibility apply criteria documents"),
        (r"தகுதி|மதிப்பெண்|கட்-ஆஃப்|கட்ஆஃப்", "eligibility cutoff marks criteria"),
        (r"வேலைவாய்ப்பு|வேலை|பிளேஸ்மென்ட்|சம்பளம்", "placement recruitment companies package ctc highest"),
        (r"நூலகம்|லைப்ரரி|புத்தகங்கள்", "library books timings hours central"),
        (r"உதவித்தொகை|ஸ்காலர்ஷிப்|சலுகை", "scholarship financial concession merit aid"),
        (r"பேருந்து|போக்குவரத்து|பஸ்", "transport bus route connectivity"),
        (r"ஆய்வகம்|லேப்", "laboratory practical lab modern"),
        (r"விளையாட்டு|மைதானம்", "sports games facilities indoor outdoor"),
        (r"தொடர்பு|முகவரி|தொலைபேசி|எண்", "contact phone address email office desk"),
        (r"கல்லூரி\s*பெயர்|பெயர்\s*என்ன", "what is your college name institution")
    ]
    for pat, rep in tamil_to_english:
        if re.search(pat, text):
            text += " " + rep

    return text


class CollegeChatbot:
    """
    Intelligent College Enquiry Chatbot powered by TF-IDF & Cosine Similarity,
    augmented with Fuzzy Sequence Matching and ChatGPT-like LLM generation.
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

    def get_response(
        self,
        user_query: str,
        category_filter: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        api_key: Optional[str] = None,
        language: str = "English"
    ) -> Dict[str, Any]:
        """
        Processes a student's natural language enquiry, supports multi-turn context
        and follow-ups, and returns the response in English or Tamil.

        Returns:
            dict: {
                "answer": str,
                "friendly_answer": str,
                "matched_question": Optional[str],
                "category": Optional[str],
                "confidence": float,
                "status": "greeting" | "gratitude" | "farewell" | "matched" | "fallback" | "invalid",
                "is_fuzzy": bool,
                "ai_generated": bool
            }
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history = conversation_history or []
        is_tamil = (language == "Tamil")

        # Extract last image displayed from history to strictly prevent repetition
        last_image = None
        for msg in reversed(history):
            if msg.get("role") == "assistant":
                meta = msg.get("meta") or {}
                vis = meta.get("visual") or {}
                if vis.get("image"):
                    last_image = vis["image"]
                    break

        # 1. Validate empty/invalid input
        if not user_query or not user_query.strip():
            msg = "தயவுசெய்து சரியான கேள்வி அல்லது விசாரணையை உள்ளிடவும்." if is_tamil else "Please enter a valid question or enquiry so I can assist you."
            friendly = generate_local_friendly_response(user_query, msg, None, None, "invalid", history, language=language)
            response = {
                "answer": msg,
                "friendly_answer": friendly,
                "matched_question": None,
                "category": None,
                "confidence": 0.0,
                "status": "invalid",
                "is_fuzzy": False,
                "ai_generated": False,
                "visual": get_topic_visual("General", msg, last_image=last_image)
            }
            self._log_interaction(timestamp, "INVALID_INPUT", 0.0, "None", "invalid")
            return response

        cleaned_query = user_query.strip()

        # 2. Check for Greetings
        if self._is_greeting(cleaned_query):
            if is_tamil:
                ans = (
                    "வணக்கம்! வி.ஆர் பொறியியல் கல்லூரி (VR College of Engineering) AI உதவி மையத்திற்கு அன்புடன் வரவேற்கிறோம். "
                    "இன்று உங்களுக்கு எவ்வாறு உதவ வேண்டும்? பாடப்பிரிவுகள், சேர்க்கை, கட்டணம், விடுதி மற்றும் வேலைவாய்ப்பு பற்றி என்னிடம் கேட்கலாம்!"
                )
            else:
                ans = (
                    "Hello! Welcome to the VR College of Engineering AI Enquiry Assistant. "
                    "How can I help you today? You can ask me about courses, admissions, fees, "
                    "hostel facilities, placements, and more!"
                )
            friendly = generate_local_friendly_response(cleaned_query, ans, "Greeting", None, "greeting", history, language=language)
            response = {
                "answer": ans,
                "friendly_answer": friendly,
                "matched_question": None,
                "category": "Greeting",
                "confidence": 1.0,
                "status": "greeting",
                "is_fuzzy": False,
                "ai_generated": False,
                "visual": get_topic_visual("Greeting", ans, last_image=last_image)
            }
            self._log_interaction(timestamp, "GREETING", 1.0, "Greeting", "greeting")
            return response

        # 3. Check for Gratitude / Thank you
        if self._is_gratitude(cleaned_query):
            if is_tamil:
                ans = (
                    "மிக்க மகிழ்ச்சி! வி.ஆர் பொறியியல் கல்லூரி குறித்து மேலும் கேள்விகள் இருந்தால் தயங்காமல் கேளுங்கள். "
                    "உங்கள் கல்விப் பயணம் சிறக்க எனது மனமார்ந்த வாழ்த்துகள்!"
                )
            else:
                ans = (
                    "You're very welcome! Feel free to ask if you have any more questions about VR College of Engineering. "
                    "Best of luck with your academic journey!"
                )
            friendly = generate_local_friendly_response(cleaned_query, ans, "Gratitude", None, "gratitude", history, language=language)
            response = {
                "answer": ans,
                "friendly_answer": friendly,
                "matched_question": None,
                "category": "Gratitude",
                "confidence": 1.0,
                "status": "gratitude",
                "is_fuzzy": False,
                "ai_generated": False,
                "visual": get_topic_visual("Gratitude", ans, last_image=last_image)
            }
            self._log_interaction(timestamp, "GRATITUDE", 1.0, "Gratitude", "gratitude")
            return response

        # 4. Check for Farewell
        if self._is_farewell(cleaned_query):
            if is_tamil:
                ans = "நன்றி மற்றும் விடைபெறுகிறேன்! இனிய நாளாக அமையட்டும். கூடுதல் தகவல்கள் தேவைப்படும் போது எப்போதும் தொடர்பு கொள்ளலாம்."
            else:
                ans = "Goodbye! Have a wonderful day ahead. Reach out anytime if you need more information."
            friendly = generate_local_friendly_response(cleaned_query, ans, "Farewell", None, "farewell", history, language=language)
            response = {
                "answer": ans,
                "friendly_answer": friendly,
                "matched_question": None,
                "category": "Farewell",
                "confidence": 1.0,
                "status": "farewell",
                "is_fuzzy": False,
                "ai_generated": False,
                "visual": get_topic_visual("Farewell", ans, last_image=last_image)
            }
            self._log_interaction(timestamp, "FAREWELL", 1.0, "Farewell", "farewell")
            return response

        # 5. Multi-turn Follow-up Resolution
        resolved_query = resolve_followup_query(cleaned_query, history)

        # Check if user is asking to elaborate on prior turn (e.g. "ok explain more", "tell me more", "more details")
        is_elaboration = bool(
            re.search(r"^(ok\s+)?(explain\s+more|tell\s+me\s+more|elaborate|explain\s+further|more\s+details?|details?\s+please|can\s+you\s+explain\s+more|give\s+more\s+details?|in\s+detail)\b", cleaned_query.lower())
            or cleaned_query.lower() in ["more details", "more detail", "details", "explain more", "ok explain more", "tell me more", "explain", "more"]
        )

        # 6. Explicit Intent Detection Engine (Top Priority)
        # Accurately routes dedicated intents (College Name, Location, Courses, Scholarships, etc.)
        # so general queries never accidentally trigger the fee structure.
        detected_intent = classify_intent(cleaned_query)
        if detected_intent == Intent.UNKNOWN and resolved_query != cleaned_query and not is_elaboration:
            detected_intent = classify_intent(resolved_query)

        if detected_intent != Intent.UNKNOWN and detected_intent != Intent.FEE_STRUCTURE:
            intent_res = get_intent_response(detected_intent, cleaned_query, language=language)
            if intent_res:
                intent_res["visual"] = get_topic_visual(intent_res["category"], intent_res["friendly_answer"], last_image=last_image)
                self._log_interaction(
                    timestamp,
                    f"Len: {len(cleaned_query)} chars",
                    1.0,
                    intent_res["category"],
                    "matched"
                )
                return intent_res

        # 7. Smart College Fee Enquiry Priority Check
        # Triggered ONLY when user specifically asks about fees, tuition, or when detected_intent is FEE_STRUCTURE
        is_fee = (detected_intent == Intent.FEE_STRUCTURE) or is_fee_enquiry(cleaned_query) or is_fee_enquiry(resolved_query) or (category_filter and category_filter.lower() == "fees")
        if category_filter and category_filter not in ["All Categories", "Fees", "Hostel"]:
            is_fee = False

        if is_fee:
            fee_target_query = resolved_query if is_fee_enquiry(resolved_query) else cleaned_query
            fee_res = generate_smart_fee_response(fee_target_query, category_filter=category_filter, last_image=last_image, language=language)
            self._log_interaction(
                timestamp,
                f"Len: {len(cleaned_query)} chars",
                1.0,
                fee_res["category"],
                "matched"
            )
            return fee_res

        # 8. Apply category filter if specified
        target_df = self.faq_df
        target_indices = None
        if category_filter and category_filter != "All Categories":
            mask = target_df["category"].str.lower() == category_filter.lower()
            if mask.any():
                target_indices = target_df[mask].index.tolist()

        # 8. TF-IDF vectorization & Cosine Similarity calculation
        norm_query = preprocess_text(resolved_query)
        query_vector = self.vectorizer.transform([norm_query])
        similarities = cosine_similarity(query_vector, self.question_vectors).flatten()

        if target_indices is not None:
            masked_sims = similarities.copy()
            for idx in range(len(masked_sims)):
                if idx not in target_indices:
                    masked_sims[idx] = -1.0
            best_idx = int(masked_sims.argmax())
            best_score = float(masked_sims[best_idx])
        else:
            best_idx = int(similarities.argmax())
            best_score = float(similarities[best_idx])

        # 8. Fuzzy Typo Matching Fallback
        is_fuzzy = False
        valid_indices = target_indices if target_indices is not None else list(range(len(self.processed_questions)))

        if best_score < self.similarity_threshold and valid_indices:
            best_fuzzy_idx = best_idx
            best_fuzzy_score = 0.0

            q_words = set(norm_query.split())
            for idx in valid_indices:
                faq_norm = self.processed_questions[idx]
                seq_ratio = difflib.SequenceMatcher(None, norm_query, faq_norm).ratio()
                faq_words = set(faq_norm.split())
                overlap = len(q_words & faq_words) / max(1, len(q_words))
                combined_fuzzy = max(seq_ratio, overlap * 0.85)

                if combined_fuzzy > best_fuzzy_score:
                    best_fuzzy_score = combined_fuzzy
                    best_fuzzy_idx = idx

            if best_fuzzy_score >= 0.50:
                boosted_score = round(max(best_score, best_fuzzy_score * 0.75), 4)
                if boosted_score >= self.similarity_threshold:
                    best_idx = best_fuzzy_idx
                    best_score = boosted_score
                    is_fuzzy = True

        # 9. Response Composition & Optional LLM Generation
        if best_score >= self.similarity_threshold:
            matched_row = self.faq_df.iloc[best_idx]
            raw_answer = matched_row["answer"]
            cat = matched_row["category"]
            matched_q = matched_row["question"]

            # Grounded facts collection for LLM
            grounded_facts = [{
                "category": cat,
                "question": matched_q,
                "answer": raw_answer
            }]

            ai_generated = False
            friendly_answer = ""

            # Check if Gemini AI can generate response
            if is_ai_available(api_key):
                llm_res = generate_llm_response(
                    user_query=cleaned_query,
                    grounded_facts=grounded_facts,
                    history=history,
                    api_key=api_key,
                    language=language
                )
                if llm_res:
                    friendly_answer = llm_res
                    ai_generated = True

            if not friendly_answer:
                friendly_answer = generate_local_friendly_response(
                    user_query=cleaned_query,
                    raw_answer=raw_answer,
                    category=cat,
                    matched_question=matched_q,
                    status="matched",
                    history=history,
                    language=language
                )

            response = {
                "answer": raw_answer,
                "friendly_answer": friendly_answer,
                "matched_question": matched_q,
                "category": cat,
                "confidence": round(best_score, 4),
                "status": "matched",
                "is_fuzzy": is_fuzzy,
                "ai_generated": ai_generated,
                "visual": get_topic_visual(cat, raw_answer, last_image=last_image)
            }
            self._log_interaction(
                timestamp,
                f"Len: {len(cleaned_query)} chars",
                round(best_score, 4),
                cat,
                "matched"
            )
        else:
            # Query not resolved: log into unanswered queries
            log_unanswered_query(cleaned_query, best_score, category_filter)

            fallback_msg = DEFAULT_FALLBACK_MESSAGE_TAMIL if is_tamil else DEFAULT_FALLBACK_MESSAGE
            friendly_fallback = generate_local_friendly_response(
                user_query=cleaned_query,
                raw_answer=fallback_msg,
                category=None,
                matched_question=None,
                status="fallback",
                history=history,
                language=language
            )

            response = {
                "answer": fallback_msg,
                "friendly_answer": friendly_fallback,
                "matched_question": None,
                "category": None,
                "confidence": round(best_score, 4),
                "status": "fallback",
                "is_fuzzy": False,
                "ai_generated": False,
                "visual": get_topic_visual("Admissions", DEFAULT_FALLBACK_MESSAGE, last_image=last_image)
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
        """Safely logs interaction metadata without storing raw sensitive personal details."""
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

        chat_history = []
        while True:
            try:
                user_q = input("Student: ")
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye!")
                break

            if user_q.strip().lower() in ["exit", "quit"]:
                print("Bot: Goodbye! Have a wonderful day.")
                break

            resp = bot.get_response(user_q, conversation_history=chat_history)
            disp = resp.get("friendly_answer") or resp.get("answer")
            print(f"\nBot: {disp}\n")

            chat_history.append({"role": "user", "content": user_q})
            chat_history.append({"role": "assistant", "content": disp})

            if resp.get("status") == "matched":
                fuzzy_tag = " [Fuzzy Matched]" if resp.get("is_fuzzy") else ""
                ai_tag = " [Gemini AI]" if resp.get("ai_generated") else " [Local Agent]"
                print(f"   [Category: {resp['category']} | Confidence: {resp['confidence']:.2f}{fuzzy_tag}{ai_tag}]\n")
            elif resp.get("status") == "fallback":
                print(f"   [Fallback Triggered | Score: {resp['confidence']:.2f}]\n")
    except Exception as e:
        print(f"Error starting chatbot: {e}")
