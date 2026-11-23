"""
Dedicated Fee Manager and Knowledge Base for AI-Based College Enquiry Chatbot.

Provides a robust, local, deterministic Smart College Fee Enquiry System that:
1. Detects all fee-related student queries (departments, tuition, hostel, admission, transport, scholarships).
2. Extracts and displays the exact specific requested fee details FIRST.
3. Appends the Complete College Fee Structure (Undergraduate + Other Fees + Scholarship info) LAST.
4. Operates 100% locally with zero external API dependencies.
"""

import re
from typing import Dict, Any, Optional

# -------------------------------------------------------------
# 1. Local Structured Fee Knowledge Base
# -------------------------------------------------------------
UNDERGRADUATE_FEES = {
    "cse": {
        "code": "CSE",
        "name": "Computer Science and Engineering (CSE)",
        "tuition": "₹1,50,000 per year",
        "aliases": ["cse", "computer science", "computer science engineering", "comp sci", "cs engineering", "b.tech cse", "btech cse"]
    },
    "ece": {
        "code": "ECE",
        "name": "Electronics and Communication Engineering (ECE)",
        "tuition": "₹1,25,000 per year",
        "aliases": ["ece", "electronics", "electronics and communication", "electronics & communication", "electronics and communication engineering", "b.tech ece", "btech ece"]
    },
    "eee": {
        "code": "EEE",
        "name": "Electrical and Electronics Engineering (EEE)",
        "tuition": "₹1,10,000 per year",
        "aliases": ["eee", "electrical", "electrical and electronics", "electrical & electronics", "electrical engineering", "b.tech eee", "btech eee"]
    },
    "mech": {
        "code": "ME",
        "name": "Mechanical Engineering",
        "tuition": "₹1,00,000 per year",
        "aliases": ["mechanical", "mechanical engineering", "mech", "mech engineering", "b.tech mech", "b.tech mechanical", "btech mech"]
    },
    "civil": {
        "code": "CE",
        "name": "Civil Engineering",
        "tuition": "₹95,000 per year",
        "aliases": ["civil", "civil engineering", "b.tech civil", "btech civil"]
    },
    "it": {
        "code": "IT",
        "name": "Information Technology (IT)",
        "tuition": "₹1,40,000 per year",
        "aliases": ["information technology", "infotech", "it department", "it dept", "it branch", "b.tech it", "btech it"]
    },
    "aids": {
        "code": "AI & DS",
        "name": "Artificial Intelligence and Data Science",
        "tuition": "₹1,50,000 per year",
        "aliases": ["ai and data science", "ai & data science", "artificial intelligence", "data science", "aids", "ai & ds", "ai ds", "b.tech aids", "btech aids"]
    }
}

OTHER_FEES = {
    "admission": {
        "name": "Admission Fee",
        "amount": "₹5,000",
        "terms": "One-time registration fee payable at enrollment confirmation",
        "aliases": ["admission fee", "admission charges", "registration fee", "admission cost", "enrollment fee"]
    },
    "registration": {
        "name": "Registration Fee",
        "amount": "₹2,000",
        "terms": "One-time registration fee",
        "aliases": ["registration fee", "registration charges"]
    },
    "lab": {
        "name": "Laboratory Fee",
        "amount": "₹8,000",
        "terms": "Annual fee covering specialized AI, networking, computing, and robotics laboratories",
        "aliases": ["lab fee", "laboratory fee", "lab charges", "practical fee"]
    },
    "library": {
        "name": "Library Fee",
        "amount": "₹3,000",
        "terms": "Annual fee providing full access to IEEE, Springer digital repositories and textbook lending",
        "aliases": ["library fee", "library charges", "book fee"]
    },
    "development": {
        "name": "Development Fee",
        "amount": "₹5,000",
        "terms": "Annual campus infrastructure and digital facility maintenance",
        "aliases": ["development fee", "infrastructure fee"]
    },
    "exam": {
        "name": "Examination Fee",
        "amount": "₹2,500 per semester",
        "terms": "Semester university and continuous assessment fee",
        "aliases": ["exam fee", "examination fee", "semester exam fee"]
    },
    "transport": {
        "name": "Transport Fee",
        "amount": "₹20,000 – ₹40,000 per year",
        "terms": "Annual fee depending on designated bus route distance across city and suburbs",
        "aliases": ["transport fee", "transport charges", "bus fee", "bus charges", "bus transport", "transportation charges", "transportation fee"]
    },
    "hostel": {
        "name": "Hostel Fee",
        "amount": "₹80,000 – ₹1,20,000 per year",
        "terms": "Includes accommodation, 4-meal daily dining mess, 24/7 Wi-Fi, power backup, and security (varies by room occupancy and AC/Non-AC)",
        "aliases": ["hostel fee", "hostel charges", "hostel accommodation", "room fee", "mess fee", "hostel cost", "hostel expenses"]
    }
}

SCHOLARSHIP_INFO = (
    "### 🎓 Scholarships & Financial Aid\n\n"
    "- 🏆 **Merit Scholarships:** Up to 50% tuition waiver awarded for top 5% rankers in entrance exams.\n"
    "- ⚽ **Sports Scholarships:** 100% full tuition concession for state and national level sports medalists.\n"
    "- 🏛️ **Government Scholarships:** Complete assistance for post-matric and government category welfare schemes.\n"
    "- 💳 **Semester Installments:** Flexible semester split payment facility is available upon formal request to the Accounts Department.\n\n"
    "*(Note: The above amounts are approved sample fees for demonstration purposes. Official quotes vary by category and quota).* "
    "[DEMO DATA]"
)

# -------------------------------------------------------------
# 2. Complete Fee Structure Markdown Table
# -------------------------------------------------------------
COMPLETE_FEE_STRUCTURE_MARKDOWN = f"""### Complete College Fee Structure

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

{SCHOLARSHIP_INFO}"""


# -------------------------------------------------------------
# 3. Dedicated Fee Query Detection Function
# -------------------------------------------------------------
FEE_TRIGGER_WORDS = [
    "fee", "fees", "feee", "feees", "tuition", "b.tech cost", "btech cost",
    "cost of study", "installment", "installments", "admission fee", "registration fee",
    "hostel fee", "transport fee", "lab fee", "library fee", "exam fee",
    "fee structure", "fees structure", "fee details", "fee detail",
    "course fee", "college fee", "annual fee", "semester fee",
    "கட்டணம்", "கல்விக்கட்டணம்", "செலவு", "பணம்", "ரூபாய்", "பீஸ்"
]


def is_fee_enquiry(query: str) -> bool:
    """
    Robustly identifies whether a student's question is asking for fee, tuition,
    or payment structure details.
    Guarantees that general questions (college name, location, courses, scholarships)
    are NEVER misclassified as fee enquiries.
    """
    if not query or not query.strip():
        return False

    q_lower = query.strip().lower()

    # Tamil fee detection
    if any(k in q_lower for k in ["கட்டணம்", "கல்விக்கட்டணம்", "பீஸ்"]):
        return True

    # Exclude questions that are explicitly asking about college name, location, or general identity
    if any(k in q_lower for k in ["college name", "name of college", "which college", "where is", "located", "address"]):
        return False

    # 1. Direct keywords
    if any(re.search(r"\b" + re.escape(word) + r"\b", q_lower) for word in FEE_TRIGGER_WORDS):
        return True

    # 2. Specific questions like "How much does B.Tech cost?" or "how much is hostel accommodation"
    if "how much" in q_lower and any(w in q_lower for w in ["cost", "pay", "fee", "b.tech", "btech", "hostel", "admission", "study", "cse", "ece", "eee", "mech", "civil", "it"]):
        return True

    # 3. Complete fee structure inquiry
    if "fee structure" in q_lower or "complete fee" in q_lower or "all fees" in q_lower or "fee list" in q_lower:
        return True

    # 4. Detail inquiries specifically asking about fee schedules
    if q_lower.strip() in ["fee details", "fee detail", "all fee details", "fee structure details", "tuition details"]:
        return True

    return False


def matches_alias(query: str, aliases: list) -> bool:
    """Checks whether any alias appears in the query using regex word boundaries."""
    for alias in aliases:
        pattern = r"\b" + re.escape(alias) + r"\b"
        if re.search(pattern, query, re.IGNORECASE):
            return True
    return False


# -------------------------------------------------------------
# 4. Extract Specific Requested Fee & Generate Structured Answer
# -------------------------------------------------------------
def generate_smart_fee_response(
    query: str,
    category_filter: Optional[str] = None,
    last_image: Optional[str] = None,
    language: str = "English"
) -> Dict[str, Any]:
    """
    Generates the fee response strictly following the mandatory priority and format:
    1. Understands the specific fee requested.
    2. Displays the specific requested fee details FIRST.
    3. Displays the Complete College Fee Structure LAST.
    4. Dynamically selects relevant campus imagery with anti-repetition protection.
    Supports English and Tamil dynamically.
    """
    from image_manager import get_dynamic_visual

    q_lower = query.strip().lower()

    is_hostel = (category_filter and category_filter.lower() == "hostel") or any(k in q_lower for k in ["hostel", "hostal", "hostle", "விடுதி"])

    if language == "Tamil":
        from ai_agent import get_smart_fee_response
        full_friendly_response = get_smart_fee_response(query, "", language="Tamil")
        if is_hostel:
            raw_matched_answer = "வி.ஆர் பொறியியல் கல்லூரி விடுதி கட்டணம் ஆண்டிற்கு ₹80,000 முதல் ₹1,20,000 வரை (உணவு மற்றும் அறை உட்பட)."
            assigned_cat = "Hostel"
            matched_q = "விடுதி கட்டண விவரங்கள் என்ன?"
        else:
            raw_matched_answer = "வி.ஆர் பொறியியல் கல்லூரி கட்டண விவரங்கள்: இளங்கலை பொறியியல் (₹95,000 முதல் ₹1,50,000 வரை), சேர்க்கை கட்டணம் ₹5,000, விடுதி கட்டணம் ₹80,000–₹1,20,000."
            assigned_cat = "Fees"
            matched_q = "முழுமையான கல்லூரி கட்டண விவரங்கள் என்ன?"

        visual_data = get_dynamic_visual(
            query=query,
            answer=full_friendly_response,
            category_hint=assigned_cat,
            last_image=last_image
        )
        return {
            "answer": raw_matched_answer,
            "friendly_answer": full_friendly_response,
            "matched_question": matched_q,
            "category": assigned_cat,
            "confidence": 1.0,
            "status": "matched",
            "is_fuzzy": False,
            "ai_generated": False,
            "visual": {
                "image": visual_data["image"],
                "caption": visual_data["caption"]
            }
        }

    # Priority Check 1: Hostel (or Hostel Category Filter)
    if is_hostel:
        specific_answer = (
            "Of course! 😊 Here are the hostel fee details.\n\n"
            "- **Hostel Fee:** ₹80,000 – ₹1,20,000 per year.\n\n"
            "The actual amount may depend on the room type and facilities (single, double, or triple sharing, AC/Non-AC). "
            "It includes 4-meal hygienic dining mess, 24/7 power backup, Wi-Fi, and security.\n\n"
            "These are sample fees for demonstration purposes."
        )

    # Priority Check 2: Explicit Complete Fee Structure or All Department Fees
    elif bool(
        re.search(r"\b(complete|full|entire|whole|all)\s+(fee|fees|fee structure|structure)\b", q_lower)
        or re.search(r"\b(fee structure|all department fees?|all courses? fees?|all branches? fees?)\b", q_lower)
        or any(k in q_lower for k in ["fee details", "fee detail", "all fee details"])
        or q_lower.strip() in ["fee structure", "fees structure", "give me fee structure", "give me the complete fee structure", "fees", "fee", "college fees", "fee details"]
    ):
        specific_answer = (
            "Hello! 😊 Sure, here is the overview of our college fees and tuition schedules.\n\n"
            "- **B.Tech Undergraduate Tuition Fees:** ₹95,000 to ₹1,50,000 per year depending on your engineering branch.\n"
            "- **Hostel & Dining:** ₹80,000 – ₹1,20,000 per year.\n"
            "- **Installment Facility:** Semester-wise split payments are available upon request.\n\n"
            "These are sample fees for demonstration purposes."
        )

    # Priority Check 2: Specific Undergraduate Departments
    elif matches_alias(q_lower, UNDERGRADUATE_FEES["ece"]["aliases"]):
        specific_answer = (
            "Hello! 😊 Sure, I'll help you with the ECE fee details.\n\n"
            "**Electronics and Communication Engineering (ECE)**\n\n"
            "- **Annual Tuition Fee:** ₹1,25,000\n"
            "- **Admission Fee:** ₹5,000 (one-time)\n"
            "- **Laboratory Fee:** ₹8,000 per year\n"
            "- **Library Fee:** ₹3,000 per year\n\n"
            "These are sample fees for demonstration purposes."
        )

    elif matches_alias(q_lower, UNDERGRADUATE_FEES["cse"]["aliases"]):
        specific_answer = (
            "Hello! 😊 Sure, I'll help you with the CSE fee details.\n\n"
            "**Computer Science and Engineering (CSE)**\n\n"
            "- **Annual Tuition Fee:** ₹1,50,000\n"
            "- **Admission Fee:** ₹5,000 (one-time)\n"
            "- **Laboratory Fee:** ₹8,000 per year\n"
            "- **Library Fee:** ₹3,000 per year\n\n"
            "These are sample fees for demonstration purposes."
        )

    elif matches_alias(q_lower, UNDERGRADUATE_FEES["eee"]["aliases"]):
        specific_answer = (
            "Hello! 😊 Sure, I'll help you with the EEE fee details.\n\n"
            "**Electrical and Electronics Engineering (EEE)**\n\n"
            "- **Annual Tuition Fee:** ₹1,10,000\n"
            "- **Admission Fee:** ₹5,000 (one-time)\n"
            "- **Laboratory Fee:** ₹8,000 per year\n"
            "- **Library Fee:** ₹3,000 per year\n\n"
            "These are sample fees for demonstration purposes."
        )

    elif matches_alias(q_lower, UNDERGRADUATE_FEES["mech"]["aliases"]):
        specific_answer = (
            "Hello! 😊 Sure, I'll help you with the Mechanical Engineering fee details.\n\n"
            "**Mechanical Engineering**\n\n"
            "- **Annual Tuition Fee:** ₹1,00,000\n"
            "- **Admission Fee:** ₹5,000 (one-time)\n"
            "- **Laboratory Fee:** ₹8,000 per year\n"
            "- **Library Fee:** ₹3,000 per year\n\n"
            "These are sample fees for demonstration purposes."
        )

    elif matches_alias(q_lower, UNDERGRADUATE_FEES["civil"]["aliases"]):
        specific_answer = (
            "Hello! 😊 Sure, I'll help you with the Civil Engineering fee details.\n\n"
            "**Civil Engineering**\n\n"
            "- **Annual Tuition Fee:** ₹95,000\n"
            "- **Admission Fee:** ₹5,000 (one-time)\n"
            "- **Laboratory Fee:** ₹8,000 per year\n"
            "- **Library Fee:** ₹3,000 per year\n\n"
            "These are sample fees for demonstration purposes."
        )

    elif matches_alias(q_lower, UNDERGRADUATE_FEES["it"]["aliases"]):
        specific_answer = (
            "Hello! 😊 Sure, I'll help you with the IT department fee details.\n\n"
            "**Information Technology (IT)**\n\n"
            "- **Annual Tuition Fee:** ₹1,40,000\n"
            "- **Admission Fee:** ₹5,000 (one-time)\n"
            "- **Laboratory Fee:** ₹8,000 per year\n"
            "- **Library Fee:** ₹3,000 per year\n\n"
            "These are sample fees for demonstration purposes."
        )

    elif matches_alias(q_lower, UNDERGRADUATE_FEES["aids"]["aliases"]):
        specific_answer = (
            "Hello! 😊 Sure, I'll help you with the AI & Data Science fee details.\n\n"
            "**Artificial Intelligence and Data Science**\n\n"
            "- **Annual Tuition Fee:** ₹1,50,000\n"
            "- **Admission Fee:** ₹5,000 (one-time)\n"
            "- **Laboratory Fee:** ₹8,000 per year\n"
            "- **Library Fee:** ₹3,000 per year\n\n"
            "These are sample fees for demonstration purposes."
        )

    # Priority Check 3: Hostel
    elif matches_alias(q_lower, OTHER_FEES["hostel"]["aliases"]) or "hostel" in q_lower:
        visual_img = "hostel.jpg"
        visual_caption = "🏢 On-Campus Student Residence & Dining"
        specific_answer = (
            "Of course! 😊 Here are the hostel fee details.\n\n"
            "- **Hostel Fee:** ₹80,000 – ₹1,20,000 per year.\n\n"
            "The actual amount may depend on the room type and facilities (single, double, or triple sharing, AC/Non-AC). "
            "It includes 4-meal hygienic dining mess, 24/7 power backup, Wi-Fi, and security.\n\n"
            "These are sample fees for demonstration purposes."
        )

    # Priority Check 4: Admission / Registration
    elif matches_alias(q_lower, OTHER_FEES["admission"]["aliases"]) or "admission fee" in q_lower or "registration fee" in q_lower:
        specific_answer = (
            "Hello! 😊 Here are the admission fee details.\n\n"
            "The sample admission fee is **₹5,000** (one-time at enrollment) and the registration fee is **₹2,000**.\n\n"
            "These are sample fees for demonstration purposes."
        )

    # Priority Check 5: Transport / Bus
    elif matches_alias(q_lower, OTHER_FEES["transport"]["aliases"]) or "transport" in q_lower or "bus fee" in q_lower:
        specific_answer = (
            "Hello! 😊 Here are the college transportation and bus charges.\n\n"
            "- **Transport Fee:** ₹20,000 – ₹40,000 per year.\n\n"
            "The exact fee depends on the designated route distance connecting various city stops and suburbs.\n\n"
            "These are sample fees for demonstration purposes."
        )

    # Priority Check 6: Lab
    elif matches_alias(q_lower, OTHER_FEES["lab"]["aliases"]) or "lab fee" in q_lower or "laboratory fee" in q_lower:
        specific_answer = (
            "Hello! 😊 Here are the laboratory fee details.\n\n"
            "- **Laboratory Fee:** ₹8,000 per year.\n\n"
            "Covers specialized computing, AI, and electronics lab equipment.\n\n"
            "These are sample fees for demonstration purposes."
        )

    # Priority Check 7: Library
    elif matches_alias(q_lower, OTHER_FEES["library"]["aliases"]) or "library fee" in q_lower:
        specific_answer = (
            "Hello! 😊 Here are the library fee details.\n\n"
            "- **Library Fee:** ₹3,000 per year.\n\n"
            "Provides full access to central library books, IEEE, and digital e-journals.\n\n"
            "These are sample fees for demonstration purposes."
        )

    # Priority Check 8: Scholarships
    elif any(k in q_lower for k in ["scholarship", "scholarships", "scolorship", "financial aid", "concession"]):
        specific_answer = (
            "Hello! 😊 Yes, scholarships and financial aid are actively available for eligible students:\n\n"
            "- 🏆 **Merit Scholarships:** Up to 50% tuition waiver for top rankers.\n"
            "- ⚽ **Sports Concessions:** 100% tuition waiver for state and national medalists.\n"
            "- 🏛️ **Government Assistance:** 100% scheme support for reserved categories.\n"
            "- 💳 **Semester Installments:** Flexible split payments are available upon request.\n\n"
            "These are sample policies for demonstration purposes."
        )

    # Fallback within Fee System: General Fee Overview
    else:
        specific_answer = (
            "Hello! 😊 Here is the overview of our college fees and tuition schedules.\n\n"
            "- **B.Tech Undergraduate Tuition Fees:** ₹95,000 to ₹1,50,000 per year depending on your engineering branch.\n"
            "- **Hostel & Dining:** ₹80,000 – ₹1,20,000 per year.\n"
            "- **Installment Facility:** Semester-wise split payments are available upon request.\n\n"
            "These are sample fees for demonstration purposes."
        )

    # Form the complete answer: Specific Answer FIRST + Complete Fee Structure LAST
    full_friendly_response = f"{specific_answer}\n\n---\n\n{COMPLETE_FEE_STRUCTURE_MARKDOWN}"

    if is_hostel:
        raw_matched_answer = (
            "[DEMO DATA] The hostel accommodation fee is approximately Rs. 80,000 to Rs. 1,20,000 per year, "
            "inclusive of mess dining charges and room facilities."
        )
        assigned_cat = "Hostel"
        matched_q = "What is the hostel fee structure?"
    else:
        raw_matched_answer = (
            "[DEMO DATA] The college fee structure covers undergraduate B.Tech "
            "(CSE ₹1,50,000, ECE ₹1,25,000, EEE ₹1,10,000, Mech ₹1,00,000, Civil ₹95,000, "
            "IT ₹1,40,000, AI & DS ₹1,50,000), admission fee ₹5,000, and hostel fee ₹80,000–₹1,20,000."
        )
        assigned_cat = "Fees"
        matched_q = "What is the complete college fee structure?"

    visual_data = get_dynamic_visual(
        query=query,
        answer=full_friendly_response,
        category_hint=assigned_cat,
        last_image=last_image
    )

    return {
        "answer": raw_matched_answer,
        "friendly_answer": full_friendly_response,
        "matched_question": matched_q,
        "category": assigned_cat,
        "confidence": 1.0,
        "status": "matched",
        "is_fuzzy": False,
        "ai_generated": False,
        "visual": {
            "image": visual_data["image"],
            "caption": visual_data["caption"]
        }
    }
