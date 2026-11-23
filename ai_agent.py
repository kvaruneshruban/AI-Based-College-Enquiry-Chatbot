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
    Supports both English and Tamil fee keywords.
    """
    clean = (query or "").lower()
    cat = (category or "").lower()
    if cat == "fees":
        return True
    fee_keywords = [
        "fee", "fees", "feee", "tuition", "cost", "charge", "charges",
        "pricing", "expense", "hostel fee", "ece fee", "cse fee", "admission fee",
        "கட்டணம்", "கட்டணங்கள்", "கல்விக்கட்டணம்", "செலவு", "பணம்", "விடுதி கட்டணம்", "பீஸ்"
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


COMPLETE_FEE_TABLE_TAMIL = """### முழுமையான கல்லூரி கட்டண விவரங்கள் (Complete Fee Structure)

#### 🎓 இளங்கலை பட்டப்படிப்பு ஆண்டு கட்டணம் (Course Tuition Fees)
| பாடப்பிரிவு (Course) | ஆண்டு கல்விக் கட்டணம் |
| :--- | :---:|
| கணினி அறிவியல் பொறியியல் (CSE) | ₹1,50,000 |
| மின்னணு & தகவல் தொடர்பு (ECE) | ₹1,25,000 |
| மின் மற்றும் மின்னணு பொறியியல் (EEE) | ₹1,10,000 |
| மெக்கானிக்கல் இன்ஜினியரிங் (Mechanical) | ₹1,00,000 |
| சிவில் இன்ஜினியரிங் (Civil) | ₹95,000 |
| தகவல் தொழில்நுட்பம் (IT) | ₹1,40,000 |
| செயற்கை நுண்ணறிவு மற்றும் தரவு அறிவியல் (AI & DS) | ₹1,50,000 |

#### 🏢 2. பிற கல்லூரி கட்டணங்கள் (Other Fees)
| கட்டண விவரம் | தொகை |
| :--- | :---:|
| சேர்க்கை கட்டணம் (Admission Fee) | ₹5,000 |
| பதிவு கட்டணம் (Registration Fee) | ₹2,000 |
| ஆய்வக கட்டணம் (Laboratory Fee) | ₹8,000 |
| நூலக கட்டணம் (Library Fee) | ₹3,000 |
| வளாக வளர்ச்சி கட்டணம் (Development Fee) | ₹5,000 |
| தேர்வு கட்டணம் (Exam Fee) | ₹2,500 (செமஸ்டருக்கு) |
| பேருந்து கட்டணம் (Transport Fee) | ₹20,000–₹40,000 |
| விடுதி கட்டணம் (Hostel Fee) | ₹80,000–₹1,20,000 |

### 🎓 கல்வி உதவித்தொகை & நிதி உதவி (Scholarships & Financial Aid)
- 🏆 **தகுதி உதவித்தொகை (Merit Scholarships):** சிறந்த மதிப்பெண் பெற்ற மாணவர்களுக்கு 50% வரை கல்விக் கட்டண தள்ளுபடி.
- ⚽ **விளையாட்டுச் சலுகை (Sports Quota):** மாநில மற்றும் தேசிய அளவிலான வீரர்களுக்கு 100% முழுக் கல்விக் கட்டண சலுகை.
- 🏛️ **அரசு திட்டங்கள் (Government Schemes):** இடஒதுக்கீட்டுப் பிரிவு மாணவர்களுக்கான 100% அரசு உதவித்தொகை வழிகாட்டல்.
- 💳 **தவணை முறை (Installments):** மாணவர்களின் கோரிக்கையின் பேரில் செமஸ்டர் வாரியான கட்டண தவணை வசதி உண்டு.

*(குறிப்பு: மேற்கண்ட கட்டணங்கள் ஒப்புதல் அளிக்கப்பட்ட மாதிரி விவரங்கள் ஆகும்).*"""


def get_smart_fee_response(user_query: str, raw_answer: str, language: str = "English") -> str:
    """
    Generates a structured, friendly response for fee enquiries:
    1. First gives the specific requested fee details.
    2. At the END, automatically appends the Complete College Fee Structure.
    Supports both English and Tamil dynamically.
    """
    clean_q = user_query.strip().lower()
    is_tamil = (language == "Tamil")

    # Case A: ECE Department
    if any(k in clean_q for k in ["ece", "electronics and comm", "electronics & comm", "மின்னணு"]):
        if is_tamil:
            specific_part = (
                "நிச்சயமாக! 😊 **மின்னணு மற்றும் தகவல் தொடர்பு பொறியியல் (ECE)** கட்டண விவரங்கள் கீழே கொடுக்கப்பட்டுள்ளன:\n\n"
                "**B.Tech Electronics & Communication Engineering (ECE)**\n\n"
                "- 💰 **ஆண்டு கல்விக் கட்டணம் (Annual Tuition Fee):** ₹1,25,000\n"
                "- 📝 **சேர்க்கை கட்டணம் (Admission Fee):** ₹5,000 (ஒரு முறை மட்டும்)\n"
                "- 🔬 **ஆய்வக கட்டணம் (Laboratory Fee):** ₹8,000\n"
                "- 📚 **நூலக கட்டணம் (Library Fee):** ₹3,000\n\n"
                "*மேற்கண்ட கட்டணங்கள் மாதிரி விவரங்கள் ஆகும். சேர்க்கை ஒதுக்கீட்டிற்கு ஏற்ப மாறுபடலாம்.*"
            )
        else:
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
    elif any(k in clean_q for k in ["cse", "computer science", "கணினி"]):
        if is_tamil:
            specific_part = (
                "நிச்சயமாக! 😊 **கணினி அறிவியல் மற்றும் பொறியியல் (CSE)** கட்டண விவரங்கள் கீழே உள்ளன:\n\n"
                "**B.Tech Computer Science & Engineering (CSE)**\n\n"
                "- 💰 **ஆண்டு கல்விக் கட்டணம் (Annual Tuition Fee):** ₹1,50,000\n"
                "- 📝 **சேர்க்கை கட்டணம் (Admission Fee):** ₹5,000 (ஒரு முறை மட்டும்)\n"
                "- 🔬 **ஆய்வக கட்டணம் (Laboratory Fee):** ₹8,000\n"
                "- 📚 **நூலக கட்டணம் (Library Fee):** ₹3,000\n\n"
                "*மேற்கண்ட கட்டணங்கள் மாதிரி விவரங்கள் ஆகும். சேர்க்கை ஒதுக்கீட்டிற்கு ஏற்ப மாறுபடலாம்.*"
            )
        else:
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
    elif any(k in clean_q for k in ["eee", "electrical", "மின்"]):
        if is_tamil:
            specific_part = (
                "நிச்சயமாக! 😊 **மின் மற்றும் மின்னணு பொறியியல் (EEE)** கட்டண விவரங்கள் கீழே உள்ளன:\n\n"
                "**B.Tech Electrical & Electronics Engineering (EEE)**\n\n"
                "- 💰 **ஆண்டு கல்விக் கட்டணம் (Annual Tuition Fee):** ₹1,10,000\n"
                "- 📝 **சேர்க்கை கட்டணம் (Admission Fee):** ₹5,000\n"
                "- 🔬 **ஆய்வக கட்டணம் (Laboratory Fee):** ₹8,000\n"
                "- 📚 **நூலக கட்டணம் (Library Fee):** ₹3,000"
            )
        else:
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
    elif any(k in clean_q for k in ["mech", "mechanical", "மெக்கானிக்கல்"]):
        if is_tamil:
            specific_part = (
                "நிச்சயமாக! 😊 **மெக்கானிக்கல் இன்ஜினியரிங் (Mechanical Engineering)** கட்டண விவரங்கள் கீழே உள்ளன:\n\n"
                "**B.Tech Mechanical Engineering**\n\n"
                "- 💰 **ஆண்டு கல்விக் கட்டணம் (Annual Tuition Fee):** ₹1,00,000\n"
                "- 📝 **சேர்க்கை கட்டணம் (Admission Fee):** ₹5,000\n"
                "- 🔬 **ஆய்வக கட்டணம் (Laboratory Fee):** ₹8,000\n"
                "- 📚 **நூலக கட்டணம் (Library Fee):** ₹3,000"
            )
        else:
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
    elif any(k in clean_q for k in ["civil", "சிவில்"]):
        if is_tamil:
            specific_part = (
                "நிச்சயமாக! 😊 **சிவில் இன்ஜினியரிங் (Civil Engineering)** கட்டண விவரங்கள் கீழே உள்ளன:\n\n"
                "**B.Tech Civil Engineering**\n\n"
                "- 💰 **ஆண்டு கல்விக் கட்டணம் (Annual Tuition Fee):** ₹95,000\n"
                "- 📝 **சேர்க்கை கட்டணம் (Admission Fee):** ₹5,000\n"
                "- 🔬 **ஆய்வக கட்டணம் (Laboratory Fee):** ₹8,000\n"
                "- 📚 **நூலக கட்டணம் (Library Fee):** ₹3,000"
            )
        else:
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
    elif any(k in clean_q for k in ["hostel", "mess", "boarding", "room", "விடுதி", "உணவு"]):
        if is_tamil:
            specific_part = (
                "🏢 **வி.ஆர் பொறியியல் கல்லூரி விடுதி கட்டண விவரங்கள் (Hostel Fees):**\n\n"
                "- 🛏️ **ஆண்டு விடுதி கட்டணம்:** ஆண்டிற்கு **₹80,000 முதல் ₹1,20,000** வரை (அறை வகை சார்ந்தது).\n"
                "- 🍽️ **உணவு முறை (Mess):** இதில் 4 வேளை சுகாதாரமான மற்றும் சுவையான சைவ/அசைவ உணவு மற்றும் தங்குமிடம் அடங்கும்.\n"
                "- 💡 **வசதிகள்:** அதிவேக வைஃபை, படிக்கும் மேஜை, 24/7 மின்சாரம் மற்றும் பாதுகாப்பு வசதிகள் உண்டு."
            )
        else:
            specific_part = (
                "Of course! 😊 Here are the hostel fee details.\n\n"
                "- **Hostel Fee:** ₹80,000 – ₹1,20,000 per year.\n\n"
                "The actual amount may depend on the room type and facilities."
            )

    # Case G: Admission Fee
    elif any(k in clean_q for k in ["admission fee", "registration fee", "admission charge", "சேர்க்கை கட்டணம்"]):
        if is_tamil:
            specific_part = (
                "📝 **சேர்க்கை மற்றும் பதிவு கட்டண விவரங்கள்:**\n\n"
                "- **சேர்க்கை கட்டணம் (Admission Fee):** ₹5,000 (சேர்க்கையின் போது ஒரு முறை மட்டும் செலுத்த வேண்டும்).\n"
                "- **பதிவு கட்டணம் (Registration Fee):** ₹2,000 (ஒரு முறை மட்டும்)."
            )
        else:
            specific_part = (
                "The sample admission fee is **₹5,000**.\n\n"
                "This is a one-time enrollment and registration fee paid at the time of admission confirmation."
            )

    # Case H: Transport fee
    elif any(k in clean_q for k in ["transport", "bus", "பேருந்து", "போக்குவரத்து"]):
        if is_tamil:
            specific_part = (
                "🚌 **வளாக பேருந்து கட்டண விவரங்கள் (Transport Fees):**\n\n"
                "- **ஆண்டு பேருந்து கட்டணம்:** பயண தூரத்தைப் பொறுத்து ஆண்டிற்கு **₹20,000 முதல் ₹40,000** வரை.\n"
                "- **வழித்தடங்கள்:** சென்னை மற்றும் புறநகரின் 40+ முக்கிய வழித்தடங்களை இணைக்கும் பேருந்து வசதி உள்ளது."
            )
        else:
            specific_part = (
                "🚌 **Campus Transport & Bus Fees:**\n\n"
                "- **Annual Transport Fee:** ₹20,000 – ₹40,000 per year depending on the boarding stop distance.\n"
                "- **Routes:** 40+ college buses connect all major transit hubs across the city."
            )

    # Case I: MBA
    elif any(k in clean_q for k in ["mba"]):
        if is_tamil:
            specific_part = (
                "நிச்சயமாக! 😊 **முதுகலை வணிக மேலாண்மை (MBA)** கட்டண விவரங்கள்:\n\n"
                "**Master of Business Administration (MBA)**\n\n"
                "- 💰 **ஆண்டு கல்விக் கட்டணம்:** ₹1,20,000\n"
                "- 📝 **சேர்க்கை கட்டணம்:** ₹5,000\n"
                "- 📚 **நூலக வள கட்டணம்:** ₹3,000"
            )
        else:
            specific_part = (
                "Sure! 😊 Here are the MBA program fee details.\n\n"
                "**Master of Business Administration (MBA)**\n\n"
                "- **Annual Tuition Fee:** ₹1,20,000\n"
                "- **Admission Fee:** ₹5,000\n"
                "- **Library & Resource Fee:** ₹3,000\n\n"
                "The above amounts are sample values for demonstration."
            )

    # Case J: MCA
    elif any(k in clean_q for k in ["mca"]):
        if is_tamil:
            specific_part = (
                "நிச்சயமாக! 😊 **முதுகலை கணினி பயன்பாட்டியல் (MCA)** கட்டண விவரங்கள்:\n\n"
                "**Master of Computer Applications (MCA)**\n\n"
                "- 💰 **ஆண்டு கல்விக் கட்டணம்:** ₹85,000\n"
                "- 📝 **சேர்க்கை கட்டணம்:** ₹5,000\n"
                "- 🔬 **ஆய்வக கட்டணம்:** ₹8,000"
            )
        else:
            specific_part = (
                "Sure! 😊 Here are the MCA program fee details.\n\n"
                "**Master of Computer Applications (MCA)**\n\n"
                "- **Annual Tuition Fee:** ₹85,000\n"
                "- **Admission Fee:** ₹5,000\n"
                "- **Laboratory Fee:** ₹8,000\n\n"
                "The above amounts are sample values for demonstration."
            )

    # Case K: General tuition / B.Tech fee
    else:
        if is_tamil:
            specific_part = (
                "நிச்சயமாக! 😊 **வி.ஆர் பொறியியல் கல்லூரியின் கட்டண விவரங்கள் கீழே கொடுக்கப்பட்டுள்ளன:**\n\n"
                "- 🎓 **ஆண்டு கல்விக் கட்டணம்:** பாடப்பிரிவைப் பொறுத்து ஆண்டிற்கு சுமார் ₹75,000 முதல் ₹1,50,000 வரை.\n"
                "- 💳 **தவணை வசதி:** மாணவர்களின் கோரிக்கையின் பேரில் செமஸ்டர் வாரியாக தவணை முறையில் கட்டணம் செலுத்தலாம்."
            )
        else:
            clean_raw = raw_answer.replace("[DEMO DATA]", "").strip()
            specific_part = (
                "Sure! 😊 Let me help you with the college fee details.\n\n"
                f"{clean_raw}\n\n"
                "- **Annual Tuition Fee:** Approximately ₹75,000 – ₹1,50,000 per year depending on the branch.\n"
                "- **Installment Facility:** Semester-wise split payments are available upon formal request to the Accounts Department."
            )

    if is_tamil:
        return f"{specific_part}\n\n---\n\n{COMPLETE_FEE_TABLE_TAMIL}"
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
        if any(p in clean_q for p in [
            "explain more", "tell me more", "more details", "in detail", "explain further",
            "i want the list", "the list", "give the list", "show list", "give full details", "details"
        ]):
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

    # Case 0: Elaboration / Continuation ("ok explain more", "tell me more", "explain in detail", "elaborate", "more details", "i want the list")
    is_elaboration = bool(
        re.search(r"^(ok\s+)?(explain\s+more|tell\s+me\s+more|elaborate|more\s+details?|details?\s+please|explain\s+further|continue|what\s+else|tell\s+me\s+everything|can\s+you\s+explain\s+more|give\s+more\s+details?|give\s+full\s+details?|in\s+detail|i\s+want\s+(the\s+)?list|give\s+(me\s+)?(the\s+)?list|show\s+(me\s+)?(the\s+)?list|the\s+list)\b", clean_q)
        or clean_q in ["explain more", "ok explain more", "tell me more", "more details", "more detail", "details", "explain", "more", "explain further", "i want the list", "the list", "give list", "show list", "full details"]
    )
    if is_elaboration:
        # Check specific topics based on last category or last user query first
        user_lower = last_user_msg.lower()
        cat_lower = last_cat.lower()
        combined = (last_cat + " " + last_q + " " + last_user_msg + " " + last_bot_msg).lower()

        if any(k in clean_q for k in ["list", "fee", "fees"]) and ("fee" in combined or "cost" in combined or "tuition" in combined):
            return "What is the annual tuition fee for B.Tech?"
        elif "college name" in cat_lower or any(k in user_lower for k in ["college name", "your college name", "name of your", "which college", "introduce"]):
            return "Can you introduce your college?"
        elif any(k in user_lower for k in ["course", "b.tech", "degree", "m.tech", "branch"]) or "courses" in cat_lower or "course" in cat_lower:
            return "What undergraduate courses are offered?"
        elif any(k in user_lower for k in ["fee", "tuition", "cost", "scholarship"]) or "fee" in cat_lower:
            return "What is the annual tuition fee for B.Tech?"
        elif any(k in user_lower for k in ["hostel", "mess", "room"]) or "hostel" in cat_lower:
            return "Are hostel facilities available for boys and girls?"
        elif any(k in user_lower for k in ["placement", "package", "salary", "recruit"]) or "placement" in cat_lower:
            return "What was the highest and average salary package in recent placements?"
        elif any(k in user_lower for k in ["admission", "apply", "eligib"]) or "admission" in cat_lower:
            return "What is the eligibility criteria for B.Tech admission?"
        elif any(k in user_lower for k in ["library", "book"]) or "library" in cat_lower:
            return "What are the library timings and working hours?"
        elif any(k in user_lower for k in ["transport", "bus"]) or "transport" in cat_lower:
            return "What bus facilities are available?"
        elif any(k in user_lower for k in ["location", "address", "where"]) or "location" in cat_lower:
            return "Where is your college located?"
        elif "course" in combined or "b.tech" in combined or "degree" in combined:
            return "What undergraduate courses are offered?"
        elif "admission" in combined or "eligibility" in combined:
            return "What is the eligibility criteria for B.Tech admission?"
        elif "fee" in combined or "scholarship" in combined:
            return "What is the annual tuition fee for B.Tech?"
        elif "hostel" in combined:
            return "Are hostel facilities available for boys and girls?"
        elif "placement" in combined:
            return "What was the highest and average salary package in recent placements?"
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


def translate_text_to_tamil(text: str, category: Optional[str] = None, matched_question: Optional[str] = None) -> str:
    """
    Translates verified college FAQ facts and statements into natural, fluent, and clear Tamil.
    Preserves numbers, fees, and standard academic terms (e.g. B.Tech, CSE, ECE, TNEA).
    """
    clean = text.replace("[DEMO DATA]", "").strip()
    low_text = clean.lower()
    low_q = (matched_question or "").lower()

    # 1. Courses
    if category == "Courses" or "course" in low_q or "undergraduate" in low_q or "postgraduate" in low_q:
        if "postgraduate" in low_q or "pg" in low_q or "m.tech" in low_text or "mba" in low_text:
            return (
                "எங்கள் கல்லூரியில் பின்வரும் முதுகலை பட்டப்படிப்புகள் (PG Programs) வழங்கப்படுகின்றன:\n"
                "- 💻 **M.Tech கணினி அறிவியல் மற்றும் பொறியியல் (Computer Science & Engineering)** (2 ஆண்டுகள்)\n"
                "- 📊 **MBA (நிதி, மனிதவளம், சந்தைப்படுத்தல்)** (2 ஆண்டுகள்)\n"
                "- 🖥️ **MCA (கணினி பயன்பாட்டியல் முதுகலை)** (2 ஆண்டுகள்)\n"
                "அனைத்து முதுகலை படிப்புகளும் AICTE அங்கீகாரம் மற்றும் அண்ணா பல்கலைக்கழக இணைவு பெற்றவை."
            )
        elif "diploma" in low_q or "certificate" in low_q:
            return (
                "எங்கள் கல்லூரி வழக்கமான பட்டப்படிப்புகளுடன் இணைந்து செயற்கை நுண்ணறிவு (AI), கிளவுட் கம்ப்யூட்டிங், "
                "ஐஓடி (IoT) மற்றும் டேட்டா சயின்ஸ் ஆகிய தொழில்துறை சார்ந்த சிறப்பு சான்றிதழ் பயிற்சிகளை வழங்குகிறது."
            )
        elif "duration" in low_q:
            return (
                "B.Tech இளங்கலை பொறியியல் படிப்பு **4 ஆண்டுகள் (8 செமஸ்டர்கள்)** கால அளவு கொண்டது. "
                "டிப்ளமோ முடித்து நேரடி இரண்டாம் ஆண்டில் சேரும் மாணவர்களுக்கு (Lateral Entry) 3 ஆண்டுகள் ஆகும். "
                "MBA மற்றும் MCA படிப்புகள் 2 ஆண்டுகள் (4 செமஸ்டர்கள்) கால அளவு கொண்டவை."
            )
        else:
            return (
                "வி.ஆர் பொறியியல் கல்லூரியில் (VR College of Engineering) AICTE அங்கீகாரம் பெற்ற பின்வரும் இளங்கலை பட்டப்படிப்புகள் (B.Tech) வழங்கப்படுகின்றன:\n\n"
                "- 💻 **B.Tech கணினி அறிவியல் மற்றும் பொறியியல் (Computer Science & Engineering - CSE)** (180 இடங்கள்)\n"
                "- 🤖 **B.Tech செயற்கை நுண்ணறிவு மற்றும் தரவு அறிவியல் (AI & Data Science)** (60 இடங்கள்)\n"
                "- 📡 **B.Tech தகவல் தொழில்நுட்பம் (Information Technology - IT)** (120 இடங்கள்)\n"
                "- ⚡ **B.Tech மின்னணு மற்றும் தகவல் தொடர்பு பொறியியல் (ECE)** (120 இடங்கள்)\n"
                "- ⚙️ **B.Tech மெக்கானிக்கல் இன்ஜினியரிங் (Mechanical Engineering)** (60 இடங்கள்)\n"
                "- 🏗️ **B.Tech சிவில் இன்ஜினியரிங் (Civil Engineering)** (60 இடங்கள்)\n\n"
                "அனைத்து பாடப்பிரிவுகளும் NAAC 'A+' தரம் மற்றும் நவீன ஆய்வுக்கூட வசதிகளுடன் கற்பிக்கப்படுகின்றன."
            )

    # 2. Admission
    if category == "Admission" or "admission" in low_q or "apply" in low_q or "eligibility" in low_q:
        if "eligibility" in low_q or "criteria" in low_q:
            return (
                "**B.Tech பொறியியல் சேர்க்கைக்கான தகுதி வரம்புகள்:**\n"
                "- 10+2 / மேல்நிலை (+2) தேர்வில் கணிதம், இயற்பியல், வேதியியல் பாடங்களில் பொதுப் பிரிவினர் குறைந்தபட்சம் 50% மதிப்பெண்களும் (இடஒதுக்கீட்டுப் பிரிவினர் 45%) பெற்றிருக்க வேண்டும்.\n"
                "- AICTE மற்றும் தமிழ்நாடு அரசு விதிகளின்படி தகுதி நிர்ணயிக்கப்படுகிறது."
            )
        elif "document" in low_q:
            return (
                "**சேர்க்கையின் போது சமர்ப்பிக்க வேண்டிய முக்கிய ஆவணங்கள்:**\n"
                "1. 10 மற்றும் 12-ஆம் வகுப்பு அசல் மதிப்பெண் சான்றிதழ்கள்\n"
                "2. மாற்றுச் சான்றிதழ் (TC) மற்றும் நடத்தைச் சான்றிதழ்\n"
                "3. சாதிச் சான்றிதழ் (Community Certificate)\n"
                "4. TNEA கலந்தாய்வு ஒதுக்கீட்டுக் கடிதம் (Allotment Order)\n"
                "5. ஆதார் அட்டை நகல் & 5 பாஸ்போர்ட் அளவு புகைப்படங்கள்"
            )
        elif "lateral" in low_q:
            return (
                "ஆம், AICTE விதிகளின்படி அரசு அங்கீகாரம் பெற்ற 3 ஆண்டு பாலிடெக்னிக் டிப்ளமோ (Diploma) அல்லது "
                "B.Sc கணிதம் முடித்த மாணவர்கள் B.Tech நேரடி 2-ஆம் ஆண்டில் (3-ஆம் செமஸ்டர்) சேரலாம்."
            )
        elif "when" in low_q or "start" in low_q:
            return (
                "சேர்க்கை விண்ணப்பப் பதிவு ஆண்டுதோறும் **ஏப்ரல் மாதத்தில்** தொடங்குகிறது. "
                "TNEA ஒற்றைச் சாளர கலந்தாய்வு தேதிகளுக்கு ஏற்ப சேர்க்கை நடைபெறும். ஆன்லைன் விண்ணப்பம் தற்போது திறக்கப்பட்டுள்ளது."
            )
        else:
            return (
                "**வி.ஆர் பொறியியல் கல்லூரி சேர்க்கை முறை (Admissions):**\n"
                "1. **TNEA அரசு ஒதுக்கீடு:** தமிழ்நாடு பொறியியல் சேர்க்கை கலந்தாய்வு மூலம் விண்ணப்பிக்கலாம் (கல்லூரி குறியீடு: VRCE).\n"
                "2. **நிர்வாக ஒதுக்கீடு (Management Quota):** எங்கள் கல்லூரி சேர்க்கை அலுவலகத்தில் நேரடியாகவோ அல்லது ஆன்லைன் விண்ணப்பம் மூலமாகவோ பதிவு செய்யலாம்.\n"
                "3. உதவி மையம்: +91 98765 43210 அல்லது admissions@vrcollege.edu."
            )

    # 3. Hostel
    if category == "Hostel" or "hostel" in low_q:
        if "amenities" in low_q or "room" in low_q:
            return (
                "விடுதி அறைகளில் 24 மணி நேர வைஃபை (Wi-Fi), தனித்தனி படிக்கும் மேஜை, அலமாரி, சுடுநீர் வசதி, "
                "மின்சார பேக்கப், உடற்பயிற்சி கூடம் (Gym) மற்றும் பொழுதுபோக்கு அறை வசதிகள் செய்யப்பட்டுள்ளன."
            )
        elif "mess" in low_q or "dining" in low_q or "food" in low_q:
            return (
                "விடுதி மெஸ் உணவு நேரங்கள்:\n"
                "- காலை உணவு: 7:30 AM – 9:00 AM\n"
                "- மதிய உணவு: 12:30 PM – 2:00 PM\n"
                "- மாலை சிற்றுண்டி: 4:30 PM – 5:30 PM\n"
                "- இரவு உணவு: 7:30 PM – 9:00 PM\n"
                "சுகாதாரமான மற்றும் சத்தான சைவ மற்றும் அசைவ உணவு வகைகள் பரிமாறப்படுகின்றன."
            )
        elif "curfew" in low_q or "time" in low_q:
            return (
                "மாணவர்களின் பாதுகாப்பிற்காக இரவு **7:30 மணி** நேரக் கட்டுப்பாடாக (Curfew Time) நிர்ணயிக்கப்பட்டுள்ளது. "
                "பெற்றோரின் முறையான முன் அனுமதியுடன் மட்டுமே விடுதியை விட்டு வெளியே செல்ல முடியும்."
            )
        else:
            return (
                "கல்லூரி வளாகத்திற்குள் மாணவ, மாணவியருக்கு தனித்தனியாக 24/7 சிசிடிவி பாதுகாப்புடன் கூடிய நவீன விடுதி வசதிகள் உள்ளன. "
                "ஆண்டு விடுதி கட்டணம் உணவு மற்றும் தங்குமிடம் சேர்த்து ஆண்டிற்கு **₹80,000 முதல் ₹1,20,000** வரை ஆகும்."
            )

    # 4. Placement
    if category == "Placement" or "placement" in low_q or "package" in low_q or "recruitment" in low_q:
        if "highest" in low_q or "average" in low_q or "salary" in low_q:
            return (
                "சமீபத்திய வளாக வேலைவாய்ப்பில் பதிவு செய்யப்பட்ட சம்பள விவரங்கள்:\n"
                "- 🌟 **அதிகபட்ச சம்பளம் (Highest CTC):** **₹14.0 LPA**\n"
                "- 📊 **சராசரி சம்பளம் (Average Package):** **₹4.5 LPA**\n"
                "- 🎯 **வேலைவாய்ப்பு சதவீதம்:** 85%+ தகுதி பெற்ற மாணவர்களுக்கு வேலைவாய்ப்பு உறுதி செய்யப்பட்டுள்ளது."
            )
        elif "companies" in low_q or "recruit" in low_q:
            return (
                "எங்கள் வளாகத்திற்கு வரும் முன்னணி நிறுவனங்கள்: **TCS, Infosys, Wipro, Cognizant, Tech Mahindra, "
                "Zoho, HCL, Accenture, L&T Infotech** உள்ளிட்ட 80-க்கும் மேற்பட்ட புகழ்பெற்ற நிறுவனங்கள் ஆகும்."
            )
        elif "training" in low_q:
            return (
                "எங்கள் பயிற்சி மற்றும் வேலைவாய்ப்பு மையம் 2-ஆம் ஆண்டு முதல் சிறப்பு ஆப்டிட்யூட், சாப்ட் ஸ்கில்ஸ், "
                "கோடிங் பயிற்சிகள் மற்றும் மாதிரி நேர்காணல்களை (Mock Interviews) தொடர்ந்து நடத்துகிறது."
            )
        else:
            return (
                "வி.ஆர் பொறியியல் கல்லூரியின் பயிற்சி மற்றும் வேலைவாய்ப்பு மையம் மாணவர்களுக்கு 85%+ வேலைவாய்ப்பை உறுதி செய்கிறது. "
                "அதிகபட்ச சம்பளம் ₹14.0 LPA; முன்னணி பன்னாட்டு நிறுவனங்கள் ஆண்டுதோறும் வளாக நேர்காணல் நடத்துகின்றன."
            )

    # 5. Library
    if category == "Library" or "library" in low_q:
        if "timings" in low_q or "hour" in low_q:
            return (
                "மத்திய டிஜிட்டல் நூலகம் **திங்கள் முதல் சனிக்கிழமை வரை, காலை 8:00 மணி முதல் இரவு 8:00 மணி வரை** இயங்கும். "
                "செமஸ்டர் தேர்வு காலங்களில் இரவு 10:00 மணி வரை செயல்படும்."
            )
        elif "book" in low_q or "borrow" in low_q:
            return (
                "இளங்கலை மாணவர்கள் **4 புத்தகங்களை 14 நாட்களுக்கும்**, முதுகலை மாணவர்கள் **6 புத்தகங்களை 21 நாட்களுக்கும்** எடுத்துச் செல்லலாம்."
            )
        else:
            return (
                "மத்திய நூலகத்தில் 50,000+ புத்தகங்கள், 500+ சர்வதேச மற்றும் தேசிய ஆய்விதழ்கள் (IEEE, Springer) மற்றும் "
                "60 கணினிகள் கொண்ட நவீன டிஜிட்டல் ஆய்வுப் பிரிவு உள்ளது."
            )

    # 6. Departments
    if category == "Departments" or "department" in low_q:
        return (
            "எங்கள் கல்லூரியில் கணினி அறிவியல், தகவல் தொழில்நுட்பம், மின்னணுவியல் (ECE), எலக்ட்ரிக்கல் (EEE), "
            "மெக்கானிக்கல், சிவில் மற்றும் அறிவியல் & மானுடவியல் ஆகிய துறைகள் செயல்படுகின்றன. "
            "கணினி அறிவியல் துறை பிளாக் B-யின் 2-வது தளத்தில் இயங்குகிறது. துறைத் தலைவர்: முனைவர் கே. ராமனாதன் (Dr. K. Ramanathan, Ph.D)."
        )

    # 7. Examination
    if category == "Examination" or "exam" in low_q:
        return (
            "செமஸ்டர் தேர்வுகள் அண்ணா பல்கலைக்கழக அட்டவணைப்படி ஆண்டுக்கு இருமுறை (நவம்பர்-டிசம்பர் மற்றும் ஏப்ரல்-மே) நடத்தப்படுகின்றன. "
            "தேர்வு எழுத குறைந்தபட்சம் **75% வருகைப் பதிவு (Attendance)** கட்டாயமாகும்."
        )

    # 8. Contact & General
    if category == "Contact" or "contact" in low_q or "phone" in low_q or "address" in low_q:
        return (
            "**சேர்க்கை மற்றும் நிர்வாக அலுவலக தொடர்புகள்:**\n"
            "- 📞 தொலைபேசி: +91 98765 43210 / 0123-456789\n"
            "- ✉️ மின்னஞ்சல்: admissions@vrcollege.edu\n"
            "- 🏛️ முகவரி: வி.ஆர் பொறியியல் கல்லூரி, நாலெட்ஜ் கேம்பஸ், செக்டார் 4, எஜுகேஷன் சிட்டி - 600100.\n"
            "- ⏰ அலுவலக நேரம்: திங்கள் முதல் சனிக்கிழமை வரை, காலை 9:00 மணி முதல் மாலை 5:00 மணி வரை."
        )

    if "bus" in low_q or "transport" in low_q:
        return (
            "சென்னையின் அனைத்து முக்கிய பகுதிகளையும் இணைக்கும் **40+ கல்லூரி பேருந்துகள்** இயக்கப்படுகின்றன. "
            "பயண தூரத்தைப் பொறுத்து ஆண்டிற்கு ₹20,000 முதல் ₹40,000 வரை கட்டணம் நிர்ணயிக்கப்பட்டுள்ளது."
        )

    if "sports" in low_q:
        return (
            "எங்கள் வளாகத்தில் கிரிக்கெட் மைதானம், கால்பந்து திடல், கூடைப்பந்து மைதானம், இறகுப்பந்து உள்விளையாட்டரங்கம் மற்றும் "
            "நவீன உடற்பயிற்சி கூடம் (Gym) உள்ளிட்ட சிறப்பான விளையாட்டு வசதிகள் உள்ளன."
        )

    if "ragging" in low_q:
        return (
            "வி.ஆர் பொறியியல் கல்லூரி வளாகம் **முற்றிலும் பகிடிவதையற்ற (Ragging-Free) பாதுகாப்பான வளாகமாகும்**. "
            "24 மணி நேர ஆன்டி-ரேக்கிங் குழு மற்றும் இலவச உதவி எண் (1800-180-5522) செயல்படுகிறது."
        )

    if "name" in low_q or "college" in low_q:
        return (
            "எங்கள் நிறுவனத்தின் பெயர் **வி.ஆர் பொறியியல் கல்லூரி (VR College of Engineering)** ஆகும். "
            "இது 2005-ஆம் ஆண்டு நிறுவப்பட்டு, AICTE அங்கீகாரம், NAAC 'A+' தரம் பெற்று சிறந்து விளங்குகிறது."
        )

    # General translation fallback with key term mapping
    replacements = [
        ("VR College of Engineering", "வி.ஆர் பொறியியல் கல்லூரி"),
        ("Computer Science and Engineering", "கணினி அறிவியல் மற்றும் பொறியியல் (CSE)"),
        ("Electronics and Communication Engineering", "மின்னணு மற்றும் தகவல் தொடர்பு பொறியியல் (ECE)"),
        ("Mechanical Engineering", "மெக்கானிக்கல் இன்ஜினியரிங்"),
        ("Civil Engineering", "சிவில் இன்ஜினியரிங்"),
        ("Information Technology", "தகவல் தொழில்நுட்பம் (IT)"),
        ("Artificial Intelligence", "செயற்கை நுண்ணறிவு"),
        ("tuition fee", "கல்விக் கட்டணம்"),
        ("hostel", "விடுதி"),
        ("admission", "சேர்க்கை"),
        ("eligibility", "தகுதி"),
        ("placement", "வேலைவாய்ப்பு"),
        ("scholarship", "உதவித்தொகை"),
        ("library", "நூலகம்")
    ]
    res_text = clean
    for eng, tam in replacements:
        res_text = re.sub(re.escape(eng), tam, res_text, flags=re.IGNORECASE)

    return res_text


def generate_llm_response(
    user_query: str,
    grounded_facts: List[Dict[str, str]],
    history: List[Dict[str, Any]],
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
    language: str = "English"
) -> Optional[str]:
    """
    Generates a natural, friendly ChatGPT-style conversational response using Google Gemini API,
    grounded on verified college facts and conversation history.
    Dynamically adheres to the requested consultation language (English or Tamil).
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
            if language == "Tamil":
                facts_text = "குறிப்பிட்ட தகவல் தரவுத்தளத்தில் இல்லை. சேர்க்கை உதவி மையத்தைத் தொடர்பு கொள்ளுமாறு மாணவருக்கு வழிகாட்டவும் (+91 98765 43210 / admissions@vrcollege.edu)."
            else:
                facts_text = "No direct FAQ matched. Please politely state that this specific detail is not in the database and offer the Admissions Desk helpline (+91 98765 43210 / admissions@vrcollege.edu)."

        conversation_context = ""
        for msg in history[-6:]:
            role_label = "Student" if msg["role"] == "user" else "VRBot"
            content = msg.get("content", "").replace("[DEMO DATA]", "").strip()
            conversation_context += f"{role_label}: {content}\n"

        if language == "Tamil":
            lang_instruction = (
                "CRITICAL LANGUAGE DIRECTIVE:\n"
                "The student has selected Tamil (தமிழ்). You MUST respond ENTIRELY in natural, conversational, fluent Tamil. "
                "Use simple and polite Tamil that students and parents can easily understand. "
                "Translate all college facts, courses, fees, procedures, and guidance into natural Tamil script. "
                "Do NOT respond in English even if previous conversation turns were in English, unless the user explicitly asks for English.\n\n"
            )
            fee_table_to_attach = COMPLETE_FEE_TABLE_TAMIL
            fee_table_marker = "முழுமையான கல்லூரி கட்டண விவரங்கள்"
        else:
            lang_instruction = (
                "LANGUAGE DIRECTIVE:\n"
                "Respond entirely in clear, friendly English.\n\n"
            )
            fee_table_to_attach = COMPLETE_FEE_TABLE
            fee_table_marker = "Complete College Fee Structure"

        prompt = f"""{lang_instruction}
VERIFIED COLLEGE FACTS:
{facts_text}

RECENT CONVERSATION HISTORY:
{conversation_context}

STUDENT'S LANGUAGE PREFERENCE: {language}
STUDENT'S LATEST MESSAGE:
Student: {user_query}

Respond as VRBot to the student's latest message entirely in {language} in a warm, friendly, and structured manner:"""

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=lang_instruction + SYSTEM_PROMPT,
                temperature=0.3,
            )
        )

        if response and response.text:
            text = response.text.strip()
            # Ensure complete fee structure table is attached if missing from LLM response for fee query
            if is_fee_query(user_query) and fee_table_marker not in text:
                text = f"{text}\n\n---\n\n{fee_table_to_attach}"
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
    history: List[Dict[str, Any]],
    language: str = "English"
) -> str:
    """
    Generates a natural, warm, and structured ChatGPT-like response locally without requiring an API key.
    Transforms raw dataset strings into helpful, readable, and friendly advice in English or Tamil.
    """
    clean_answer = raw_answer.replace("[DEMO DATA]", "").strip()
    clean_q = user_query.strip().lower()
    is_tamil = (language == "Tamil")

    # 1. Greetings
    if status == "greeting":
        if is_tamil:
            return (
                "வணக்கம்! 👋 **வி.ஆர் பொறியியல் கல்லூரிக்கு (VR College of Engineering)** தங்களை அன்புடன் வரவேற்கிறோம்!\n\n"
                "நான் **VRBot**, உங்கள் கல்லூரி AI ஆலோசகர். பின்வரும் தகவல்களில் உங்களுக்கு உதவ நான் தயாராக உள்ளேன்:\n"
                "- 🎓 **சேர்க்கை & தகுதி விவரங்கள்** (B.Tech, M.Tech, MBA & MCA)\n"
                "- 💰 **கட்டண அட்டவணை, தவணை முறைகள் & உதவித்தொகை**\n"
                "- 🏢 **வளாக விடுதிகள், உணவு & வசதிகள்**\n"
                "- 💼 **வளாக வேலைவாய்ப்பு (Placements) & அதிகபட்ச சம்பளம் (₹14 LPA)**\n"
                "- 📚 **மத்திய டிஜிட்டல் நூலகம் & ஆய்வகங்கள்**\n\n"
                "இன்று நீங்கள் என்ன தகவல்களை அறிய விரும்புகிறீர்கள்? தயங்காமல் கேளுங்கள்! 😊"
            )
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
        if is_tamil:
            return (
                "மிக்க மகிழ்ச்சி! 😊 உங்களுக்கு உதவ முடிந்ததில் எனக்கு பெரும் மகிழ்ச்சி.\n\n"
                "பாடப்பிரிவுகள், கல்லூரி வாழ்க்கை அல்லது சேர்க்கை நடைமுறைகள் குறித்து ஏதேனும் கூடுதல் கேள்விகள் இருந்தால், "
                "எப்போதும் என்னிடம் கேட்கலாம். உங்கள் கல்விப் பயணம் சிறக்க எனது மனமார்ந்த வாழ்த்துகள்! 🌟🎓"
            )
        return (
            "You are very welcome! 😊 Glad I could help you with that.\n\n"
            "If you have any more questions about courses, campus life, or the admissions process, "
            "I'm always right here to assist you. Wishing you great success on your academic journey! 🌟🎓"
        )

    # 3. Farewell
    if status == "farewell":
        if is_tamil:
            return (
                "நன்றி மற்றும் விடைபெறுகிறேன்! 👋 என்னுடன் உரையாடியதற்கு நன்றி.\n\n"
                "இனிய நாளாக அமையட்டும்! வி.ஆர் பொறியியல் கல்லூரி பற்றிய மேலும் தகவல்கள் தேவைப்படும் போது, "
                "எங்கள் உதவி மையம் எப்போதும் உங்களுக்காக திறந்திருக்கும். வாழ்த்துகள்! ✨"
            )
        return (
            "Goodbye! 👋 Thank you for chatting with me today.\n\n"
            "Have a wonderful day ahead! Whenever you need more information about VR College of Engineering, "
            "our campus desk is always open for you. Take care! ✨"
        )

    # 4. Invalid / Empty input
    if status == "invalid":
        if is_tamil:
            return (
                "மன்னிக்கவும், தங்களின் கேள்வி சரியாகப் புரியவில்லை! 😊 எங்கள் பாடப்பிரிவுகள், சேர்க்கை, "
                "கட்டணங்கள் அல்லது விடுதி வசதிகள் பற்றி உங்கள் கேள்வியை மீண்டும் கேளுங்கள். நான் மகிழ்ச்சியுடன் உதவுகிறேன்!"
            )
        return (
            "I didn't quite catch that! 😊 Could you please rephrase or type your question about "
            "our courses, admissions, fees, or hostel facilities? I'll be delighted to help!"
        )

    # 5. Smart Fee Enquiry Handling (Intercept all fee queries to deliver specific answer + full table at end)
    if is_fee_query(user_query, category):
        return get_smart_fee_response(user_query, raw_answer, language=language)

    # 6. Fallback (Query not found / out of domain)
    if status == "fallback":
        if is_tamil:
            if any(p in clean_q for p in ["more detail", "more details", "detail", "details", "fee", "fees", "cost", "course", "courses", "விவரம்", "கட்டணம்", "படிப்பு"]):
                return (
                    "நிச்சயமாக! 😊 எங்கள் கல்லூரியின் கல்விக் கட்டணங்கள் மற்றும் பிற நிறுவனக் கட்டணங்கள் குறித்த முழுமையான விவரங்கள்:\n\n"
                    f"{COMPLETE_FEE_TABLE_TAMIL}"
                )
            return (
                "கல்லூரி சார்ந்த கேள்விகளுக்கு உங்களுக்கு உதவ நான் தயாராக உள்ளேன்! 😊 நீங்கள் கேட்ட குறிப்பிட்ட கேள்விக்கான தகவல் "
                "எங்கள் சரிபார்க்கப்பட்ட தரவுத்தளத்தில் இல்லை என்றாலும், பின்வரும் முக்கிய பகுதிகளைப் பற்றி நீங்கள் கேட்கலாம்:\n\n"
                "- 🎓 **இளங்கலை மற்றும் முதுகலை பாடப்பிரிவுகள்** (B.Tech, MBA, MCA)\n"
                "- 💰 **கட்டண அட்டவணை & தகுதி உதவித்தொகை**\n"
                "- 🏢 **மாணவர் விடுதிகள் & வளாக வசதிகள்**\n"
                "- 💼 **வேலைவாய்ப்பு & முன்னணி நிறுவனங்கள் (அதிகபட்சம் ₹14 LPA)**\n\n"
                "நேரடி கல்லூரி ஆலோசனைக்கு, எங்கள் **சேர்க்கை உதவி மையத்தைத்** தொடர்பு கொள்ளவும்:\n"
                "- 📞 **தொலைபேசி:** +91 98765 43210 / 0123-456789\n"
                "- ✉️ **மின்னஞ்சல்:** admissions@vrcollege.edu\n"
                "- 🏛️ **வழிகாட்டுதல் மையம்:** பிளாக் A (திங்கள் - வெள்ளி: காலை 9:00 - மாலை 5:00)"
            )

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
    is_elaboration = any(p in clean_q for p in ["explain more", "tell me more", "more details", "more detail", "in detail", "elaborate", "details", "விளக்கு", "விளக்கவும்", "கூடுதல் விவரங்கள்"]) or clean_q in ["more", "details", "explain", "ok explain more", "more details", "விவரம்"]
    if is_elaboration:
        if is_tamil:
            return (
                f"**வி.ஆர் பொறியியல் கல்லூரி ({category or 'VR College of Engineering'})** பற்றிய கூடுதல் விரிவான விவரங்கள்:\n\n"
                f"📌 **முக்கிய தகவல்கள்:**\n{translate_text_to_tamil(clean_answer, category, matched_question)}\n\n"
                "✨ **கூடுதல் சிறப்பம்சங்கள்:**\n"
                "- 🏛️ **அங்கீகாரம்:** NAAC 'A+' தரம், AICTE அனுமதி, அண்ணா பல்கலைக்கழக இணைவு.\n"
                "- 🔬 **வசதிகள்:** நவீன ஆராய்ச்சி ஆய்வகங்கள், ஸ்மார்ட் வகுப்பறைகள், 50 ஏக்கர் வைஃபை வளாகம்.\n"
                "- 🤝 **நேரடி ஆலோசனை:** எங்கள் சேர்க்கை ஆலோசகரிடம் பேச வலதுபுறம் உள்ள **Apply** போர்ட்டலில் பதிவு செய்யலாம்!\n\n"
                "💡 *கட்டண தவணை முறைகள், விடுதி விதிகள் அல்லது வேலைவாய்ப்பு புள்ளிவிவரங்கள் பற்றி அறிய விரும்புகிறீர்களா?*"
            )
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
    if is_tamil:
        tamil_body = translate_text_to_tamil(clean_answer, category, matched_question)
        intro = ""
        tip = ""
        if category == "Courses":
            intro = "🎓 **தாங்கள் கோரிய பாடப்பிரிவு விவரங்கள் கீழே கொடுக்கப்பட்டுள்ளன:**\n\n"
            tip = "\n\n💡 *குறிப்பு: ஏதேனும் ஒரு குறிப்பிட்ட பாடப்பிரிவின் தகுதி வரம்புகள், கல்விக் கட்டணம் அல்லது உதவித்தொகை சலுகைகள் பற்றி அறிய விரும்பினால் கேளுங்கள்!*"
        elif category == "Admission":
            intro = "📝 **வி.ஆர் பொறியியல் கல்லூரிக்கான சரிபார்க்கப்பட்ட சேர்க்கை வழிகாட்டுதல்:**\n\n"
            tip = "\n\n💡 *குறிப்பு: எங்கள் ஆலோசகர்களிடமிருந்து நேரடி வழிகாட்டுதலைப் பெற 'Apply / Callback' படிவத்தில் உங்கள் விவரங்களை பதிவு செய்யலாம்.*"
        elif category == "Hostel":
            intro = "🏢 **வளாக விடுதி மற்றும் மாணவர் தங்குமிடம் பற்றிய விவரங்கள்:**\n\n"
            tip = "\n\n💡 *குறிப்பு: விடுதி உணவு நேரங்கள், நேரக் கட்டுப்பாடு அல்லது அறை வசதிகள் பற்றி மேலும் அறிய வேண்டுமா?*"
        elif category == "Placement":
            intro = "💼 **கல்லூரியின் சமீபத்திய வேலைவாய்ப்பு மற்றும் நிறுவன விவரங்கள்:**\n\n"
            tip = "\n\n💡 *குறிப்பு: முன்னணி நிறுவனங்களின் தேர்வு முறை அல்லது ஆப்டிட்யூட் பயிற்சி பற்றி மேலும் அறிய விரும்புகிறீர்களா?*"
        elif category == "Library":
            intro = "📚 **மத்திய டிஜிட்டல் நூலகம் பற்றிய தகவல்:**\n\n"
            tip = "\n\n💡 *குறிப்பு: நூலகத்தில் தேசிய மற்றும் சர்வதேச ஆய்விதழ்கள் (IEEE, Springer) அணுகல் வசதி உள்ளது.*"
        else:
            intro = "✨ **எங்கள் கல்லூரி தரவுத்தளத்தில் இருந்து சரிபார்க்கப்பட்ட தகவல்:**\n\n"
            tip = "\n\n💡 *குறிப்பு: உங்களுக்கு உதவ நான் எப்போதும் தயாராக உள்ளேன்!*"

        return f"{intro}{tamil_body}{tip}"

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
