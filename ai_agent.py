"""
AI Conversational Agent Module for AI-Based College Enquiry Chatbot.

Provides ChatGPT-like conversational intelligence using Google Gemini API (via google-genai),
with dynamic multi-turn conversation memory, context resolution (e.g. 'explain more', 'the first one'),
strict knowledge grounding from verified college FAQs, visual asset mapping (1:3 ratio),
a Smart College Fee Enquiry System with complete automatic fee schedules,
and an intelligent local conversational fallback for offline/zero-cost operation.
"""

import os
import re
import datetime
from typing import List, Dict, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def get_api_key() -> Optional[str]:
    """Retrieves the Gemini API key from environment variables or .env file."""
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def is_ai_available(api_key: Optional[str] = None) -> bool:
    """Checks whether the Gemini AI client can be initialized."""
    key = api_key or get_api_key()
    return bool(GENAI_AVAILABLE and key and key.strip())


def is_fee_query(query: str, category: Optional[str] = None) -> bool:
    """
    Checks if a student enquiry is related to college fees, tuition, departments fees, or hostel fees.
    """
    clean = (query or "").lower()
    cat = (category or "").lower()
    if cat == "fees":
        return True
    fee_keywords = [
        "fee", "fees", "feee", "tuition", "cost", "charge", "charges",
        "pricing", "expense", "hostel fee", "ece fee", "cse fee", "admission fee"
    ]
    return any(k in clean for k in fee_keywords)


COMPLETE_FEE_TABLE = """### Complete College Fee Structure

#### 🎓 Course & Annual Tuition Fees
| Course | Annual Tuition Fees |
| :--- | :---:|
| Computer Science Engineering | ₹1,50,000 |
| Electronics and Communication Engineering | ₹1,25,000 |
| Electrical and Electronics Engineering | ₹1,10,000 |
| Mechanical Engineering | ₹1,00,000 |
| Civil Engineering | ₹95,000 |
| Information Technology | ₹1,40,000 |
| Artificial Intelligence and Data Science | ₹1,50,000 |

#### 🏢 2. Other Fees
| Fee Category | Amount |
| :--- | :---:|
| Admission Fee | ₹5,000 |
| Registration Fee | ₹2,000 |
| Laboratory Fee | ₹8,000 |
| Library Fee | ₹3,000 |
| Development Fee | ₹5,000 |
| Exam Fee | ₹2,500 per semester |
| Transport Fee | ₹20,000–₹40,000 |
| Hostel Fee | ₹80,000–₹1,20,000 |

### 🎓 Scholarships & Financial Aid
- 🏆 **Merit Scholarships:** Up to 50% tuition waiver for top rankers.
- ⚽ **Sports Concessions:** 100% full tuition waiver for state and national medalists.
- 🏛️ **Government Assistance:** 100% scheme support for reserved categories.
- 💳 **Semester Installments:** Flexible semester split payments are available upon request.

*(Note: The above amounts are approved sample fees for demonstration purposes. Official quotes vary by category and quota).* [DEMO DATA]"""


def get_smart_fee_response(user_query: str, raw_answer: str) -> str:
    """
    Generates a structured, friendly response for fee enquiries:
    1. First gives the specific requested fee details.
    2. At the END, automatically appends the Complete College Fee Structure.
    """
    clean_q = user_query.strip().lower()

    # Case A: ECE Department
    if any(k in clean_q for k in ["ece", "electronics and comm", "electronics & comm"]):
        specific_part = (
            "Sure! 😊 Let me help you with the ECE fee details.\n\n"
            "**Electronics and Communication Engineering (ECE)**\n\n"
            "- **Annual Tuition Fee:** ₹1,25,000\n"
            "- **Admission Fee:** ₹5,000\n"
            "- **Laboratory Fee:** ₹8,000\n"
            "- **Library Fee:** ₹3,000\n\n"
            "The above amounts are sample values for demonstration."
        )

    # Case B: CSE Department
    elif any(k in clean_q for k in ["cse", "computer science"]):
        specific_part = (
            "Sure! 😊 Here are the Computer Science & Engineering (CSE) fee details.\n\n"
            "**Computer Science & Engineering (CSE)**\n\n"
            "- **Annual Tuition Fee:** ₹1,50,000\n"
            "- **Admission Fee:** ₹5,000\n"
            "- **Laboratory Fee:** ₹8,000\n"
            "- **Library Fee:** ₹3,000\n\n"
            "The above amounts are sample values for demonstration."
        )

    # Case C: EEE Department
    elif any(k in clean_q for k in ["eee", "electrical"]):
        specific_part = (
            "Sure! 😊 Here are the Electrical and Electronics Engineering (EEE) fee details.\n\n"
            "**Electrical and Electronics Engineering (EEE)**\n\n"
            "- **Annual Tuition Fee:** ₹1,10,000\n"
            "- **Admission Fee:** ₹5,000\n"
            "- **Laboratory Fee:** ₹8,000\n"
            "- **Library Fee:** ₹3,000\n\n"
            "The above amounts are sample values for demonstration."
        )

    # Case D: Mechanical Engineering
    elif any(k in clean_q for k in ["mech", "mechanical"]):
        specific_part = (
            "Sure! 😊 Here are the Mechanical Engineering (ME) fee details.\n\n"
            "**Mechanical Engineering (ME)**\n\n"
            "- **Annual Tuition Fee:** ₹1,00,000\n"
            "- **Admission Fee:** ₹5,000\n"
            "- **Laboratory Fee:** ₹8,000\n"
            "- **Library Fee:** ₹3,000\n\n"
            "The above amounts are sample values for demonstration."
        )

    # Case E: Civil Engineering
    elif any(k in clean_q for k in ["civil"]):
        specific_part = (
            "Sure! 😊 Here are the Civil Engineering (CE) fee details.\n\n"
            "**Civil Engineering (CE)**\n\n"
            "- **Annual Tuition Fee:** ₹95,000\n"
            "- **Admission Fee:** ₹5,000\n"
            "- **Laboratory Fee:** ₹8,000\n"
            "- **Library Fee:** ₹3,000\n\n"
            "The above amounts are sample values for demonstration."
        )

    # Case F: Hostel Fee
    elif any(k in clean_q for k in ["hostel"]):
        specific_part = (
            "Of course! 😊 Here are the hostel fee details.\n\n"
            "- **Hostel Fee:** ₹80,000 – ₹1,20,000 per year.\n\n"
            "The actual amount may depend on the room type and facilities."
        )

    # Case G: Admission Fee
    elif any(k in clean_q for k in ["admission fee", "registration fee", "admission charge"]):
        specific_part = (
            "The sample admission fee is **₹5,000**.\n\n"
            "This is a one-time enrollment and registration fee paid at the time of admission confirmation."
        )

    # Case H: MBA
    elif any(k in clean_q for k in ["mba"]):
        specific_part = (
            "Sure! 😊 Here are the MBA program fee details.\n\n"
            "**Master of Business Administration (MBA)**\n\n"
            "- **Annual Tuition Fee:** ₹1,20,000\n"
            "- **Admission Fee:** ₹5,000\n"
            "- **Library & Resource Fee:** ₹3,000\n\n"
            "The above amounts are sample values for demonstration."
        )

    # Case I: MCA
    elif any(k in clean_q for k in ["mca"]):
        specific_part = (
            "Sure! 😊 Here are the MCA program fee details.\n\n"
            "**Master of Computer Applications (MCA)**\n\n"
            "- **Annual Tuition Fee:** ₹85,000\n"
            "- **Admission Fee:** ₹5,000\n"
            "- **Laboratory Fee:** ₹8,000\n\n"
            "The above amounts are sample values for demonstration."
        )

    # Case J: General tuition / B.Tech fee
    else:
        clean_raw = raw_answer.replace("[DEMO DATA]", "").strip()
        specific_part = (
            "Sure! 😊 Let me help you with the college fee details.\n\n"
            f"{clean_raw}\n\n"
            "- **Annual Tuition Fee:** Approximately ₹75,000 – ₹1,50,000 per year depending on the branch.\n"
            "- **Installment Facility:** Semester-wise split payments are available upon formal request to the Accounts Department."
        )

    return f"{specific_part}\n\n---\n\n{COMPLETE_FEE_TABLE}"


def get_topic_visual(category: Optional[str], text: str = "", last_image: Optional[str] = None) -> Dict[str, str]:
    """
    Returns the most relevant campus visual asset filename and caption for the query/answer
    using dynamic anti-repetition image selection across 15 campus categories.
    """
    from image_manager import get_dynamic_visual
    return get_dynamic_visual(query=text, answer=text, category_hint=category, last_image=last_image)


def resolve_followup_query(query: str, history: List[Dict[str, Any]]) -> str:
    """
    Intelligently resolves conversational follow-ups and pronouns (e.g. 'ok explain more', 'explain the first one',
    'how much is the fee for it?', 'where is that?') using multi-turn conversation history.
    """
    clean_q = query.strip().lower()

    if not history:
        if any(p in clean_q for p in ["explain more", "tell me more", "more details", "in detail"]):
            return "What undergraduate courses are offered?"
        return query

    # Find the most recent assistant and user messages
    last_bot_msg = ""
    last_user_msg = ""
    last_cat = ""
    last_q = ""
    for msg in reversed(history):
        if msg.get("role") == "assistant" and not last_bot_msg:
            last_bot_msg = msg.get("content", "")
            meta = msg.get("meta") or {}
            last_cat = meta.get("category", "")
            last_q = meta.get("matched_question", "")
        elif msg.get("role") == "user" and not last_user_msg:
            # Skip current query if it has already been appended into history by caller
            if msg.get("content", "").strip().lower() == clean_q:
                continue
            last_user_msg = msg.get("content", "")
        if last_bot_msg and last_user_msg:
            break

    # Case 0: Elaboration / Continuation ("ok explain more", "tell me more", "explain in detail", "elaborate", "more details")
    is_elaboration = bool(
        re.search(r"^(ok\s+)?(explain\s+more|tell\s+me\s+more|elaborate|more\s+details?|details?\s+please|explain\s+further|continue|what\s+else|tell\s+me\s+everything|can\s+you\s+explain\s+more|give\s+more\s+details?|in\s+detail)\b", clean_q)
        or clean_q in ["explain more", "ok explain more", "tell me more", "more details", "more detail", "details", "explain", "more"]
    )
    if is_elaboration:
        combined = (last_cat + " " + last_q + " " + last_user_msg + " " + last_bot_msg).lower()
        if any(k in combined for k in ["college name", "institution", "who are you", "introduce", "about college", "vr college of engineering"]):
            return "Can you introduce your college?"
        elif any(k in combined for k in ["course", "b.tech", "degree", "m.tech", "program", "department", "cse", "ece", "mech", "civil", "eee", "it"]):
            return "What undergraduate courses are offered?"
        elif any(k in combined for k in ["admission", "apply", "eligibility", "cutoff"]):
            return "What is the eligibility criteria for B.Tech admission?"
        elif any(k in combined for k in ["fee", "tuition", "scholarship", "cost"]):
            return "What is the annual tuition fee for B.Tech?"
        elif any(k in combined for k in ["hostel", "mess", "curfew", "room"]):
            return "Are hostel facilities available for boys and girls?"
        elif any(k in combined for k in ["placement", "package", "recruitment", "salary", "company"]):
            return "What was the highest and average salary package in recent placements?"
        elif any(k in combined for k in ["library", "book"]):
            return "What are the library timings and working hours?"
        elif any(k in combined for k in ["transport", "bus"]):
            return "What bus facilities are available?"
        elif any(k in combined for k in ["location", "address", "where"]):
            return "Where is your college located?"
        else:
            return "What undergraduate courses are offered?"

    # Case 1: Ordinal follow-ups: "the first one", "first option", "the second one", etc.
    if re.search(r"\b(first|1st)\s+(one|option|course|program|dept|department)\b", clean_q) or clean_q in ["the first one", "first one", "explain the first one", "tell me about the first one"]:
        if "b.tech" in last_bot_msg.lower() or "bachelor of technology" in last_bot_msg.lower():
            return "Explain B.Tech undergraduate degree program details and courses"
        if "computer science" in last_bot_msg.lower():
            return "Explain Computer Science and Engineering department details"

    if re.search(r"\b(second|2nd)\s+(one|option|course|program)\b", clean_q) or clean_q in ["the second one", "second one", "explain the second one"]:
        if "m.tech" in last_bot_msg.lower():
            return "Explain M.Tech postgraduate program details"
        if "information technology" in last_bot_msg.lower():
            return "Explain Information Technology department details"

    if re.search(r"\b(third|3rd)\s+(one|option|course|program)\b", clean_q):
        if "mba" in last_bot_msg.lower():
            return "Explain MBA Master of Business Administration program details"

    # Case 2: Pronoun follow-ups: "what is the fee for that?", "how much does it cost?", "what is its fee?"
    if re.search(r"\b(fee|cost|tuition|charge)\b", clean_q) and ("that" in clean_q or "it" in clean_q or "this" in clean_q):
        if "hostel" in last_user_msg.lower() or "hostel" in last_bot_msg.lower():
            return "What is the hostel fee structure?"
        if "b.tech" in last_user_msg.lower() or "b.tech" in last_bot_msg.lower():
            return "What is the annual tuition fee for B.Tech?"
        if "ece" in last_user_msg.lower() or "ece" in last_bot_msg.lower():
            return "What is the ECE department fee?"
        if "cse" in last_user_msg.lower() or "cse" in last_bot_msg.lower():
            return "What is the CSE department fee?"
        if "mba" in last_user_msg.lower() or "mba" in last_bot_msg.lower():
            return "What is the fee for MBA program?"

    # Case 3: Eligibility follow-ups: "what is the eligibility for it?", "eligibility criteria for that?"
    if "eligibility" in clean_q and ("that" in clean_q or "it" in clean_q or "this" in clean_q):
        if "b.tech" in last_user_msg.lower() or "b.tech" in last_bot_msg.lower():
            return "What is the eligibility criteria for B.Tech admission?"

    # Case 4: Location follow-ups: "where is it located?", "where is that?"
    if "where" in clean_q and ("located" in clean_q or "it" in clean_q or "that" in clean_q):
        if "computer science" in last_user_msg.lower() or "cse" in last_user_msg.lower():
            return "Where is the Computer Science Department located?"

    return query


SYSTEM_PROMPT = """You are 'VRBot', an intelligent, warm, and friendly AI Campus Counselor for VR College of Engineering.
Your goal is to communicate with students, applicants, and parents naturally, supportively, and informatively—just like ChatGPT, but specialized for VR College of Engineering.

Key Personality & Behavioral Guidelines:
1. Friendly & Warm: Greet students politely, use simple and approachable English, and include tasteful emojis (🎓, 📚, ✨, 🏢, 💡).
2. Clear & Well-Structured: Use bullet points, bold highlights, and clean markdown headings to make information easy to read.
3. Multi-Turn Context: Remember previous turns in this conversation. When the student asks follow-up questions (e.g. 'ok explain more', 'explain the first one', 'what is the fee for that?'), understand what was previously discussed and elaborate naturally.
4. Smart College Fee Enquiry System:
   Whenever a student asks ANY question related to college fees (tuition, department fees like ECE/CSE/Mechanical, hostel fees, admission fees, etc.):
   - Step 1: First, give the specific requested fee details clearly and warmly.
   - Step 2: At the END of your response, automatically display the Complete College Fee Structure table below:

   **Complete College Fee Structure**

   #### 🎓 Undergraduate Courses
   | Course | Annual Tuition Fee |
   | :--- | :---:|
   | Computer Science Engineering (CSE) | ₹1,50,000 |
   | Electronics and Communication Engineering (ECE) | ₹1,25,000 |
   | Electrical and Electronics Engineering (EEE) | ₹1,10,000 |
   | Mechanical Engineering | ₹1,00,000 |
   | Civil Engineering | ₹95,000 |
   | Information Technology (IT) | ₹1,40,000 |
   | AI and Data Science | ₹1,50,000 |

   #### 🏢 Other College Fees
   | Fee Component | Amount | Frequency / Description |
   | :--- | :---:| :--- |
   | Admission Fee | ₹5,000 | One-time at enrollment |
   | Registration Fee | ₹2,000 | One-time at registration |
   | Laboratory Fee | ₹8,000 | Annual practical lab fee |
   | Library Fee | ₹3,000 | Annual central library access |
   | Development Fee | ₹5,000 | Annual campus development |
   | Examination Fee | ₹2,500 | Per semester |
   | Transport Fee | ₹20,000 – ₹40,000 | Annual (Depends on route distance) |
   | Hostel Fee | ₹80,000 – ₹1,20,000 | Annual (Includes 4-meal mess & room) |

   NEVER display the full fee list before answering the student's actual question!

5. Strict Grounding (Zero Hallucination): You MUST ground all specific college facts, numbers, dates, timings, and fees strictly on the VERIFIED COLLEGE FACTS provided below. NEVER invent unverified college policies or prices.
6. Missing Information Guidance: If the student asks for information not present in the verified facts, be polite, honest, and helpful. Guide them to contact the Admissions Desk at +91 98765 43210 or email admissions@vrcollege.edu.
7. Clean Output: Never output internal tags like '[DEMO DATA]' in your conversational reply. Present the facts naturally as a real campus advisor.
"""


def generate_llm_response(
    user_query: str,
    grounded_facts: List[Dict[str, str]],
    history: List[Dict[str, Any]],
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash"
) -> Optional[str]:
    """
    Generates a natural, friendly ChatGPT-style conversational response using Google Gemini API,
    grounded on verified college facts and conversation history.
    """
    key = api_key or get_api_key()
    if not is_ai_available(key):
        return None

    try:
        client = genai.Client(api_key=key.strip())

        facts_text = ""
        for i, item in enumerate(grounded_facts, 1):
            q = item.get("question", "")
            a = item.get("answer", "").replace("[DEMO DATA]", "").strip()
            cat = item.get("category", "")
            facts_text += f"{i}. [{cat}] Question: {q}\n   Official Verified Info: {a}\n\n"

        if not facts_text.strip():
            facts_text = "No direct FAQ matched. Please politely state that this specific detail is not in the database and offer the Admissions Desk helpline (+91 98765 43210 / admissions@vrcollege.edu)."

        conversation_context = ""
        for msg in history[-6:]:
            role_label = "Student" if msg["role"] == "user" else "VRBot"
            content = msg.get("content", "").replace("[DEMO DATA]", "").strip()
            conversation_context += f"{role_label}: {content}\n"

        prompt = f"""VERIFIED COLLEGE FACTS:
{facts_text}

RECENT CONVERSATION HISTORY:
{conversation_context}

STUDENT'S LATEST MESSAGE:
Student: {user_query}

Respond as VRBot to the student's latest message in a warm, friendly, and structured manner:"""

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.3,
            )
        )

        if response and response.text:
            text = response.text.strip()
            # Ensure complete fee structure table is attached if missing from LLM response for fee query
            if is_fee_query(user_query) and "Complete College Fee Structure" not in text:
                text = f"{text}\n\n---\n\n{COMPLETE_FEE_TABLE}"
            return text
    except Exception as e:
        print(f"Gemini API generation exception: {e}")
        return None

    return None


def generate_local_friendly_response(
    user_query: str,
    raw_answer: str,
    category: Optional[str],
    matched_question: Optional[str],
    status: str,
    history: List[Dict[str, Any]]
) -> str:
    """
    Generates a natural, warm, and structured ChatGPT-like response locally without requiring an API key.
    Transforms raw dataset strings into helpful, readable, and friendly advice.
    """
    clean_answer = raw_answer.replace("[DEMO DATA]", "").strip()
    clean_q = user_query.strip().lower()

    # 1. Greetings
    if status == "greeting":
        return (
            "Hello there! 👋 Welcome to **VR College of Engineering**!\n\n"
            "I'm **VRBot**, your friendly campus AI advisor. I can help you with anything related to:\n"
            "- 🎓 **Admissions & Eligibility** for B.Tech, M.Tech, MBA & MCA\n"
            "- 💰 **Fee Schedules, Installments & Scholarships**\n"
            "- 🏢 **Campus Hostels, Dining & Amenities**\n"
            "- 💼 **Placements, Highest CTC & Recruiter Records**\n"
            "- 📚 **Central Digital Library & Research Labs**\n\n"
            "What would you like to explore today? Feel free to ask anytime! 😊"
        )

    # 2. Gratitude
    if status == "gratitude":
        return (
            "You are very welcome! 😊 Glad I could help you with that.\n\n"
            "If you have any more questions about courses, campus life, or the admissions process, "
            "I'm always right here to assist you. Wishing you great success on your academic journey! 🌟🎓"
        )

    # 3. Farewell
    if status == "farewell":
        return (
            "Goodbye! 👋 Thank you for chatting with me today.\n\n"
            "Have a wonderful day ahead! Whenever you need more information about VR College of Engineering, "
            "our campus desk is always open for you. Take care! ✨"
        )

    # 4. Invalid / Empty input
    if status == "invalid":
        return (
            "I didn't quite catch that! 😊 Could you please rephrase or type your question about "
            "our courses, admissions, fees, or hostel facilities? I'll be delighted to help!"
        )

    # 5. Smart Fee Enquiry Handling (Intercept all fee queries to deliver specific answer + full table at end)
    if is_fee_query(user_query, category):
        return get_smart_fee_response(user_query, raw_answer)

    # 6. Fallback (Query not found / out of domain)
    if status == "fallback":
        # If user asked for "more details", "details", "fees", or "courses", return the complete fee structure and courses instead of generic fallback!
        if any(p in clean_q for p in ["more detail", "more details", "detail", "details", "fee", "fees", "cost", "course", "courses"]):
            return (
                "Sure! 😊 Here are the complete details regarding our course tuition fees and other institutional charges:\n\n"
                f"{COMPLETE_FEE_TABLE}"
            )
        return (
            "I'm happy to help you with college-related queries! 😊 While I don't have records "
            "for that specific question in our verified database right now, here are the key areas I can guide you through:\n\n"
            "- 🎓 **Undergraduate & Postgraduate Courses** (B.Tech, MBA, MCA)\n"
            "- 💰 **Fee Schedules & Merit Scholarships**\n"
            "- 🏢 **On-Campus Hostels & Facilities**\n"
            "- 💼 **Placements & Recruiter Packages (Up to ₹14 LPA)**\n\n"
            "For direct official assistance, please reach out to our **Admissions Desk**:\n"
            "- 📞 **Helpline:** +91 98765 43210 / 0123-456789\n"
            "- ✉️ **Email:** admissions@vrcollege.edu\n"
            "- 🏛️ **Counseling Cell:** Block A (Mon - Fri: 9:00 AM - 5:00 PM)"
        )

    # 7. Elaboration Response (If user asked "ok explain more", "tell me more", etc.)
    is_elaboration = any(p in clean_q for p in ["explain more", "tell me more", "more details", "more detail", "in detail", "elaborate", "details"]) or clean_q in ["more", "details", "explain", "ok explain more", "more details"]
    if is_elaboration:
        return (
            f"Here is more detailed information regarding **{category or 'VR College of Engineering'}**:\n\n"
            f"📌 **Key Details:**\n{clean_answer}\n\n"
            "✨ **Additional Highlights:**\n"
            "- 🏛️ **Accreditation:** NAAC 'A+' Grade, AICTE approved, affiliated to State Technical University.\n"
            "- 🔬 **Facilities:** Modern research labs, smart digital classrooms, 50-acre Wi-Fi campus.\n"
            "- 🤝 **Personal Guidance:** You can request a campus visit or counselor call in the **Apply** tab on the right!\n\n"
            "💡 *Would you like to know about fee installment options, hostel rules, or placement statistics next?*"
        )

    # 8. Standard Matched Query
    intro = ""
    if category == "Courses":
        intro = "🎓 **Here are the academic program details you requested:**\n\n"
    elif category == "Admission":
        intro = "📝 **Here is the verified admissions guidance for VR College of Engineering:**\n\n"
    elif category == "Hostel":
        intro = "🏢 **Here are the details regarding on-campus student residences:**\n\n"
    elif category == "Placement":
        intro = "💼 **Here is the latest placement & recruitment overview:**\n\n"
    elif category == "Library":
        intro = "📚 **Here is the Central Digital Library information:**\n\n"
    else:
        intro = "✨ **Here is the verified information from our college database:**\n\n"

    followup_tip = ""
    if category == "Courses":
        followup_tip = "\n\n💡 *Tip: Feel free to ask about the eligibility criteria, annual fee schedule, or scholarship concessions for any of these programs!*"
    elif category == "Admission":
        followup_tip = "\n\n💡 *Tip: You can also register your enquiry directly using the 'Apply / Callback' tab on the right to receive personal guidance from our counselors.*"
    elif category == "Hostel":
        followup_tip = "\n\n💡 *Tip: Would you like to know about hostel mess timings, curfew rules, or room amenities? Just ask!*"

    return f"{intro}{clean_answer}{followup_tip}"
