"""
Intent Detection and Response Routing Engine for AI-Based College Enquiry Chatbot.

Provides accurate intent classification across 14 academic and campus categories:
1. College Name
2. College Introduction
3. Courses Offered
4. Fee Structure
5. Admission Details
6. Scholarships
7. Hostel Facilities
8. Transportation
9. Placement Details
10. Faculty Information
11. College Location
12. Contact Information
13. Library Facilities
14. Academic Information

Guarantees:
- Never displays fee details unless the user specifically asks about fees or payments.
- Exactly adheres to specific responses requested (e.g., College Name).
- Works 100% locally with zero external API dependencies.
"""

import re
from typing import Dict, Any, Optional, List
from enum import Enum

COLLEGE_OFFICIAL_NAME = "VR College of Engineering"

class Intent(str, Enum):
    COLLEGE_NAME = "College Name"
    COLLEGE_INTRO = "College Introduction"
    COLLEGE_LOCATION = "College Location"
    COURSES_OFFERED = "Courses Offered"
    FEE_STRUCTURE = "Fee Structure"
    SCHOLARSHIPS = "Scholarships"
    HOSTEL_FACILITIES = "Hostel Facilities"
    TRANSPORTATION = "Transportation"
    PLACEMENT_DETAILS = "Placement Details"
    FACULTY_INFO = "Faculty Information"
    CONTACT_INFO = "Contact Information"
    LIBRARY_FACILITIES = "Library Facilities"
    ADMISSION_DETAILS = "Admission Details"
    ACADEMIC_INFO = "Academic Information"
    UNKNOWN = "Unknown"


# -------------------------------------------------------------
# 1. Regex Pattern Matching for Explicit Intents
# -------------------------------------------------------------
COLLEGE_NAME_PATTERNS = [
    r"\b(what('s|\s+is)?|tell\s+me|name\s+of)\s+(your|the|this)?\s*(college|institution|institute|engineering\s+college)\s*name\b",
    r"\b(what('s|\s+is)?|tell\s+me)\s+(your|the|this)?\s*college\b",
    r"\bwhich\s+college\s+(is\s+this|are\s+you)\b",
    r"\bwhat\s+is\s+the\s+name\s+of\s+(your|this|the)\s+(institution|college|institute|university)\b",
    r"\b(can\s+you\s+)?introduce\s+(your|the|this)?\s*college\b",
    r"^(college\s+name|what\s+is\s+your\s+college\s+name\??|name\s+of\s+college)$",
    r"\bwho\s+are\s+you\b",
    r"\bwhat\s+is\s+this\s+college\s+called\b"
]

COLLEGE_LOCATION_PATTERNS = [
    r"\bwhere\s+(is|are)\s+(your|the|this)?\s*(college|institution|campus|institute)\s*(located|situated)?\b",
    r"\b(college|campus)\s*(location|address|pincode)\b",
    r"\bhow\s+to\s+reach\s+(the|your)?\s*college\b",
    r"\bwhere\s+are\s+you\s+located\b",
    r"\bwhere\s+is\s+the\s+campus\b"
]

COLLEGE_INTRO_PATTERNS = [
    r"\b(about|overview\s+of|history\s+of)\s+(the|your|vr)\s*(college|institution)\b",
    r"\btell\s+me\s+about\s+(vr|the|your)?\s*college\b",
    r"\bintroduce\s+(vr\s+college|the\s+institution)\b"
]

COURSES_PATTERNS = [
    r"\bwhat\s+courses\s+(are\s+)?available\b",
    r"\bwhich\s+courses\s+(are\s+)?available\b",
    r"\bwhat\s+undergraduate\s+courses\s+(are\s+)?offered\b",
    r"\bwhat\s+courses\s+do\s+you\s+offer\b",
    r"\b(list\s+of|available)\s+(courses|programs|branches|degrees)\b",
    r"\bwhat\s+degrees\s+(are\s+)?offered\b",
    r"\bwhat\s+engineering\s+branches\s+(are\s+)?there\b",
    r"\bprograms\s+offered\b",
    r"\bcourses\s+offered\b"
]

SCHOLARSHIPS_PATTERNS = [
    r"\btell\s+me\s+about\s+scholarships?\b",
    r"\b(are\s+there\s+any|is\s+there\s+any)\s+scholarships?\b",
    r"\b(are\s+)?scholarships?\s+available\b",
    r"\bscholarship\s+(details|schemes?|eligibility|information)\b",
    r"\b(merit|sports)\s+scholarships?\b",
    r"\bfinancial\s+aid\b",
    r"\bfee\s+concession\b",
    r"\btuition\s+fee\s+waiver\b"
]

HOSTEL_PATTERNS = [
    r"\btell\s+me\s+about\s+hostel\s+facilities\b",
    r"\b(are\s+)?hostel\s+facilities\s+available\b",
    r"\bhostel\s+(rules|curfew|timing|mess|food|dining|rooms?|accommodation)\b",
    r"\bcurfew\s+time\s+for\s+hostel\b",
    r"\bhostel\s+for\s+(boys|girls)\b"
]

TRANSPORTATION_PATTERNS = [
    r"\bwhat\s+(are\s+the\s+)?(bus|transport|transportation)\s+facilities\b",
    r"\bwhat\s+bus\s+facilities\s+are\s+available\b",
    r"\btell\s+me\s+about\s+transport(ation)?\b",
    r"\bbus\s+routes?\b",
    r"\bcollege\s+bus\s+(service|routes?)\b",
    r"\btransport\s+service\b"
]

PLACEMENT_PATTERNS = [
    r"\bwhat\s+are\s+(the\s+)?placements?\b",
    r"\b(highest|average)\s+(salary\s+)?package\b",
    r"\bplacement\s+(statistics|records?|percentage|rate|details)\b",
    r"\bwhat\s+companies\s+visit\b",
    r"\btop\s+recruiters?\b",
    r"\bcampus\s+recruitment\b"
]

LIBRARY_PATTERNS = [
    r"\bshow\s+me\s+the\s+library\b",
    r"\btell\s+me\s+about\s+the\s+library\b",
    r"\blibrary\s+(timings?|hours?|working\s+hours?|facilities?)\b",
    r"\bhow\s+many\s+books\s+can\s+a\s+student\s+borrow\b",
    r"\bdigital\s+library\b"
]

ADMISSION_PATTERNS = [
    r"\bwhat\s+is\s+the\s+admission\s+procedure\b",
    r"\bhow\s+can\s+i\s+apply\s+for\s+admission\b",
    r"\beligibility\s+criteria\s+for\s+b\.?tech\b",
    r"\bwhen\s+does\s+(the\s+)?admission\s+process\s+start\b",
    r"\badmission\s+eligibility\b",
    r"\bhow\s+to\s+apply\b"
]

FACULTY_PATTERNS = [
    r"\btell\s+me\s+about\s+(the\s+)?faculty\b",
    r"\bwho\s+are\s+the\s+(professors?|teachers?|faculty\s+members?)\b",
    r"\bfaculty\s+(qualifications?|members?|experience)\b",
    r"\bteaching\s+staff\b"
]

CONTACT_PATTERNS = [
    r"\bhow\s+(can\s+i|to)\s+contact\s+(the\s+)?(college|admission\s+office)?\b",
    r"\b(contact|helpline|phone)\s+(number|details?|info)\b",
    r"\badmissions?\s+(phone|email|helpdesk)\b",
    r"\bemail\s+address\s+of\s+college\b"
]

ACADEMIC_PATTERNS = [
    r"\bacademics?\s+(information|calendar|system)\b",
    r"\bhow\s+are\s+semester\s+examinations\s+conducted\b",
    r"\bminimum\s+attendance\s+required\b",
    r"\bexamination\s+rules?\b"
]


def classify_intent(query: str) -> Intent:
    """
    Deterministically classifies user query into one of the 14 defined intents
    with strict priority to ensure specific questions (e.g. College Name, Location)
    are never overshadowed by general keywords or fee triggers.
    """
    q_clean = query.strip().lower()

    # Priority 1: College Name Intent
    for pat in COLLEGE_NAME_PATTERNS:
        if re.search(pat, q_clean):
            return Intent.COLLEGE_NAME

    # Priority 2: College Location Intent
    for pat in COLLEGE_LOCATION_PATTERNS:
        if re.search(pat, q_clean):
            return Intent.COLLEGE_LOCATION

    # Priority 3: College Introduction
    for pat in COLLEGE_INTRO_PATTERNS:
        if re.search(pat, q_clean):
            return Intent.COLLEGE_INTRO

    # Priority 4: Scholarships (Evaluated BEFORE fee structure so scholarship questions don't dump fee table)
    for pat in SCHOLARSHIPS_PATTERNS:
        if re.search(pat, q_clean):
            return Intent.SCHOLARSHIPS

    # Priority 5: Courses Offered (Only if not asking about course fees)
    if not any(k in q_clean for k in ["fee", "fees", "cost", "tuition", "how much"]):
        for pat in COURSES_PATTERNS:
            if re.search(pat, q_clean):
                return Intent.COURSES_OFFERED

    # Priority 6: Explicit Fee Structure (When user specifically asks about fees, costs, or how much)
    fee_indicators = [
        "fee", "fees", "tuition", "b.tech cost", "btech cost", "cost of study",
        "admission fee", "hostel fee", "transport fee", "fee structure", "fees structure"
    ]
    if any(re.search(r"\b" + re.escape(k) + r"\b", q_clean) for k in fee_indicators):
        return Intent.FEE_STRUCTURE
    if "how much" in q_clean and any(w in q_clean for w in ["cost", "pay", "fee", "hostel", "admission", "study", "b.tech", "cse", "ece", "eee", "mech", "civil", "it"]):
        return Intent.FEE_STRUCTURE
    if q_clean.strip() in ["fee details", "fee detail", "all fee details"]:
        return Intent.FEE_STRUCTURE

    # Priority 7: Hostel Facilities
    for pat in HOSTEL_PATTERNS:
        if re.search(pat, q_clean):
            return Intent.HOSTEL_FACILITIES

    # Priority 8: Transportation
    for pat in TRANSPORTATION_PATTERNS:
        if re.search(pat, q_clean):
            return Intent.TRANSPORTATION

    # Priority 9: Placements
    for pat in PLACEMENT_PATTERNS:
        if re.search(pat, q_clean):
            return Intent.PLACEMENT_DETAILS

    # Priority 10: Library Facilities
    for pat in LIBRARY_PATTERNS:
        if re.search(pat, q_clean):
            return Intent.LIBRARY_FACILITIES

    # Priority 11: Admission Details
    for pat in ADMISSION_PATTERNS:
        if re.search(pat, q_clean):
            return Intent.ADMISSION_DETAILS

    # Priority 12: Faculty Information
    for pat in FACULTY_PATTERNS:
        if re.search(pat, q_clean):
            return Intent.FACULTY_INFO

    # Priority 13: Contact Information
    for pat in CONTACT_PATTERNS:
        if re.search(pat, q_clean):
            return Intent.CONTACT_INFO

    # Priority 14: Academic Information
    for pat in ACADEMIC_PATTERNS:
        if re.search(pat, q_clean):
            return Intent.ACADEMIC_INFO

    return Intent.UNKNOWN


# -------------------------------------------------------------
# 2. Dedicated Response Generator for Specific Intents
# -------------------------------------------------------------
def get_intent_response(intent: Intent, query: str) -> Optional[Dict[str, Any]]:
    """
    Returns the exact, user-friendly, and strictly relevant response for each intent.
    Never includes unrelated fee tables or generic fallback apologies.
    """
    if intent == Intent.COLLEGE_NAME:
        text = (
            f"Our college name is **{COLLEGE_OFFICIAL_NAME}**. 😊 "
            "Welcome! I'm happy to help you with information about our college."
        )
        return {
            "answer": f"Our college name is {COLLEGE_OFFICIAL_NAME}.",
            "friendly_answer": text,
            "matched_question": "What is your college name?",
            "category": "College Name",
            "confidence": 1.0,
            "status": "matched",
            "is_fuzzy": False,
            "ai_generated": False,
            "visual": {
                "image": "campus_main.jpg",
                "caption": f"🏛️ {COLLEGE_OFFICIAL_NAME} Campus Quad"
            }
        }

    if intent == Intent.COLLEGE_LOCATION:
        text = (
            f"**{COLLEGE_OFFICIAL_NAME}** is located at:\n\n"
            "📍 **Address:** Knowledge Campus, Sector 4, Education City, Pincode: 560001, Karnataka, India.\n\n"
            "Our 50-acre green campus is conveniently connected via major city roadways, metro stations, "
            "and our daily campus bus transit fleet. You are warmly welcome to visit us! 🌿"
        )
        return {
            "answer": f"{COLLEGE_OFFICIAL_NAME} is located at Knowledge Campus, Sector 4, Education City, Pincode 560001.",
            "friendly_answer": text,
            "matched_question": "Where is your college located?",
            "category": "College Location",
            "confidence": 1.0,
            "status": "matched",
            "is_fuzzy": False,
            "ai_generated": False,
            "visual": {
                "image": "campus_aerial.jpg",
                "caption": "🌲 Campus Aerial View & Geographic Quad"
            }
        }

    if intent == Intent.COLLEGE_INTRO:
        text = (
            f"Welcome to **{COLLEGE_OFFICIAL_NAME}**! 🎓\n\n"
            "Established in 2005, we are an AICTE-approved and NAAC 'A+' accredited institution committed to "
            "academic brilliance, cutting-edge engineering research, and career transformation.\n\n"
            "**Key Campus Highlights:**\n"
            "- 🏛️ **50+ Acre Eco-Friendly Campus** with 24/7 high-speed Wi-Fi\n"
            "- 🔬 **Advanced AI & Computing Labs** with modern prototyping facilities\n"
            "- 💼 **92% Consistent Placement Track Record** with highest CTC of ₹14.0 LPA\n"
            "- 🏢 **On-Campus Hostels & Olympic-Grade Sports Arena**\n\n"
            "Feel free to ask me anything about our admissions, courses, hostels, or student life! 😊"
        )
        return {
            "answer": f"{COLLEGE_OFFICIAL_NAME} is an AICTE-approved, NAAC 'A+' accredited engineering institution.",
            "friendly_answer": text,
            "matched_question": "Can you introduce your college?",
            "category": "College Introduction",
            "confidence": 1.0,
            "status": "matched",
            "is_fuzzy": False,
            "ai_generated": False,
            "visual": {
                "image": "campus_main.jpg",
                "caption": f"🏛️ {COLLEGE_OFFICIAL_NAME} Main Entrance & Quad"
            }
        }

    if intent == Intent.COURSES_OFFERED:
        text = (
            f"**{COLLEGE_OFFICIAL_NAME}** offers the following accredited academic degree programs: 🎓\n\n"
            "#### 🎓 Undergraduate Programs (B.Tech - 4 Years / 8 Semesters):\n"
            "- 💻 **Computer Science and Engineering (CSE)**\n"
            "- 🤖 **Artificial Intelligence and Data Science (AI & DS)**\n"
            "- 📡 **Electronics and Communication Engineering (ECE)**\n"
            "- ⚡ **Electrical and Electronics Engineering (EEE)**\n"
            "- ⚙️ **Mechanical Engineering (ME)**\n"
            "- 🏗️ **Civil Engineering (CE)**\n"
            "- 🌐 **Information Technology (IT)**\n\n"
            "#### 🎓 Postgraduate Programs:\n"
            "- 🎓 **M.Tech in Computer Science & Engineering**\n"
            "- 💼 **Master of Business Administration (MBA)**\n"
            "- 🖥️ **Master of Computer Applications (MCA)**\n\n"
            "💡 *Tip: Would you like to know the eligibility criteria or admission procedure for any specific program?*"
        )
        return {
            "answer": "We offer B.Tech degrees in CSE, AI&DS, ECE, EEE, Mechanical, Civil, and IT, plus M.Tech, MBA, and MCA.",
            "friendly_answer": text,
            "matched_question": "What courses are available?",
            "category": "Courses",
            "confidence": 1.0,
            "status": "matched",
            "is_fuzzy": False,
            "ai_generated": False,
            "visual": {
                "image": "engineering_quad.jpg",
                "caption": "⚙️ Faculty of Engineering Academic Complex"
            }
        }

    if intent == Intent.SCHOLARSHIPS:
        text = (
            f"Yes! **{COLLEGE_OFFICIAL_NAME}** actively provides generous scholarships and financial concessions to encourage talent: 🎓\n\n"
            "- 🏆 **Merit Scholarships:** Up to 50% tuition waiver awarded to the top 5% rankers in entrance exams and qualifying board marks.\n"
            "- ⚽ **Sports Concessions:** 100% full tuition waiver for athletes representing state or national medal events.\n"
            "- 🏛️ **Government Welfare Schemes:** Full assistance and guidance for reserved categories and post-matric government scholarships.\n"
            "- 💳 **Semester Installment Option:** Flexible split payment facility is available upon formal request to the Accounts Department.\n\n"
            "💡 *Tip: You can submit your scholarship eligibility query through the **Apply** tab on the right!*"
        )
        return {
            "answer": "Scholarships include Merit Scholarships (up to 50% waiver), Sports Concessions (100% waiver), and Government Welfare Schemes.",
            "friendly_answer": text,
            "matched_question": "Tell me about scholarships.",
            "category": "Scholarships",
            "confidence": 1.0,
            "status": "matched",
            "is_fuzzy": False,
            "ai_generated": False,
            "visual": {
                "image": "students_hero.jpg",
                "caption": "🎓 Merit Scholarship Awardees & Academic Scholars"
            }
        }

    if intent == Intent.HOSTEL_FACILITIES:
        text = (
            f"**{COLLEGE_OFFICIAL_NAME}** provides secure, clean, and comfortable on-campus hostel facilities for both boys and girls: 🏢\n\n"
            "- 🛏️ **Room Accommodations:** Spacious single, double, and triple-sharing rooms with options for AC or Non-AC.\n"
            "- 🍽️ **Dining Mess:** Hygienic 4-meal daily dining serving nutritious vegetarian and non-vegetarian food.\n"
            "- ⚡ **Amenities:** 24/7 high-speed Wi-Fi, uninterrupted power backup, study desks, and modern laundry facilities.\n"
            "- 🛡️ **Security & Curfew:** Round-the-clock CCTV surveillance, biometric attendance, and a weekday curfew time of 8:30 PM (9:00 PM on weekends)."
        )
        return {
            "answer": "Hostel facilities are available for boys and girls with AC/Non-AC rooms, 4-meal mess, Wi-Fi, and 8:30 PM curfew.",
            "friendly_answer": text,
            "matched_question": "Tell me about hostel facilities.",
            "category": "Hostel",
            "confidence": 1.0,
            "status": "matched",
            "is_fuzzy": False,
            "ai_generated": False,
            "visual": {
                "image": "hostel.jpg",
                "caption": "🏢 Furnished Student Residence & Dining"
            }
        }

    if intent == Intent.TRANSPORTATION:
        text = (
            f"**{COLLEGE_OFFICIAL_NAME}** operates a comprehensive campus transit fleet: 🚌\n\n"
            "- 🚍 **Fleet Coverage:** Over 30 air-conditioned and GPS-enabled buses connecting all key city zones and suburban stops.\n"
            "- 🛡️ **Safety Standards:** Certified experienced drivers, speed governors, first-aid support, and live GPS route tracking for parents.\n"
            "- ⏰ **Timings:** Morning arrival at campus by 8:30 AM and evening departure at 4:45 PM."
        )
        return {
            "answer": "The college operates 30+ buses connecting all major city zones and residential suburbs.",
            "friendly_answer": text,
            "matched_question": "What bus facilities are available?",
            "category": "Transportation",
            "confidence": 1.0,
            "status": "matched",
            "is_fuzzy": False,
            "ai_generated": False,
            "visual": {
                "image": "transport_bus.jpg",
                "caption": "🚌 Air-Conditioned Campus Shuttle Fleet"
            }
        }

    if intent == Intent.PLACEMENT_DETAILS:
        text = (
            f"**{COLLEGE_OFFICIAL_NAME}** maintains a distinguished campus placement track record: 💼\n\n"
            "- 🌟 **Placement Rate:** 92% of all eligible graduating students successfully placed.\n"
            "- 🚀 **Highest CTC:** ₹14.0 LPA offered by tier-1 product and analytics corporations.\n"
            "- 📈 **Average CTC:** Approximately ₹4.8 LPA.\n"
            "- 🏢 **Top Recruiters:** TCS, Infosys, Wipro, Cognizant, Tech Mahindra, Accenture, and leading engineering startups.\n"
            "- 🎯 **Dedicated Training:** Aptitude training, mock interviews, and technical coding bootcamps starting from 3rd year."
        )
        return {
            "answer": "Placement rate is 92% with highest CTC of 14 LPA and average of 4.8 LPA from recruiters like TCS, Infosys, and Wipro.",
            "friendly_answer": text,
            "matched_question": "What are the placements?",
            "category": "Placement",
            "confidence": 1.0,
            "status": "matched",
            "is_fuzzy": False,
            "ai_generated": False,
            "visual": {
                "image": "placement_drive.jpg",
                "caption": "💼 Corporate Recruitment & Placement Drives"
            }
        }

    if intent == Intent.LIBRARY_FACILITIES:
        text = (
            f"Our Central Digital Library at **{COLLEGE_OFFICIAL_NAME}** is a state-of-the-art learning hub: 📚\n\n"
            "- 📖 **Collection:** Over 50,000 print textbooks, reference titles, and subscriptions to 120+ national and international journals.\n"
            "- 💻 **Digital Repositories:** High-speed internet stations with direct access to IEEE, Springer, ScienceDirect, and DELNET.\n"
            "- ⏰ **Working Hours:** Monday to Saturday from 8:00 AM to 8:00 PM (extended till 10:00 PM during exam weeks).\n"
            "- 📚 **Borrowing Policy:** Undergraduates can borrow up to 4 books for 14 days, and postgraduates up to 6 books."
        )
        return {
            "answer": "Central Library houses 50,000+ volumes, IEEE digital access, and operates 8 AM to 8 PM Monday to Saturday.",
            "friendly_answer": text,
            "matched_question": "Show me the library.",
            "category": "Library",
            "confidence": 1.0,
            "status": "matched",
            "is_fuzzy": False,
            "ai_generated": False,
            "visual": {
                "image": "library.jpg",
                "caption": "📚 Central Digital Library & Quiet Study Pods"
            }
        }

    if intent == Intent.ADMISSION_DETAILS:
        text = (
            f"Here are the admissions and eligibility guidelines for **{COLLEGE_OFFICIAL_NAME}**: 📝\n\n"
            "- 🎓 **B.Tech Eligibility:** Minimum 45% aggregate in 10+2 / Higher Secondary (40% for reserved categories) with Physics, Mathematics, and Chemistry/CS.\n"
            "- 📑 **Application Process:** Apply online through our official portal or submit forms directly at the Admissions Cell on campus.\n"
            "- 🗓️ **Academic Cycle:** Admissions open annually in April / May.\n"
            "- 📞 **Admissions Helpline:** +91 98765 43210 (Mon - Fri: 9:00 AM - 5:00 PM)."
        )
        return {
            "answer": "B.Tech admission requires 45% aggregate in 10+2 with PCM. Applications open in April/May.",
            "friendly_answer": text,
            "matched_question": "What is the admission procedure?",
            "category": "Admission",
            "confidence": 1.0,
            "status": "matched",
            "is_fuzzy": False,
            "ai_generated": False,
            "visual": {
                "image": "admissions_desk.jpg",
                "caption": "📝 Admissions Counseling & Information Desk"
            }
        }

    if intent == Intent.FACULTY_INFO:
        text = (
            f"**{COLLEGE_OFFICIAL_NAME}** is proud of its distinguished, student-centric academic faculty: 👨‍🏫\n\n"
            "- 🎓 **High Qualifications:** Over 65% of senior professors hold Ph.D. degrees from premier IITs, NITs, and reputed universities.\n"
            "- 🔬 **Research Excellence:** Faculty members actively lead sponsored research, patents, and publications in IEEE and Springer.\n"
            "- 🤝 **Personalized Mentorship:** A 1:15 faculty-to-student mentor ratio ensures continuous academic monitoring and guidance."
        )
        return {
            "answer": "Our faculty includes 65%+ Ph.D. professors with active research, maintaining a 1:15 mentor-to-student ratio.",
            "friendly_answer": text,
            "matched_question": "Tell me about the faculty.",
            "category": "Faculty",
            "confidence": 1.0,
            "status": "matched",
            "is_fuzzy": False,
            "ai_generated": False,
            "visual": {
                "image": "faculty_discussion.jpg",
                "caption": "👨‍🏫 Ph.D. Faculty Mentorship & Student Guidance"
            }
        }

    if intent == Intent.CONTACT_INFO:
        text = (
            f"Here are the official contact details for **{COLLEGE_OFFICIAL_NAME}**: 📞\n\n"
            "- 📞 **Helpline:** +91 98765 43210 / 0123-456789\n"
            "- ✉️ **Email:** admissions@vrcollege.edu\n"
            "- 🏛️ **Admissions Cell:** Ground Floor, Block A, Knowledge Campus, Sector 4, Education City, Pincode: 560001\n"
            "- ⏰ **Office Timings:** Mon - Fri: 9:00 AM - 5:00 PM | Sat: 9:00 AM - 1:00 PM."
        )
        return {
            "answer": "Helpline: +91 98765 43210 / 0123-456789 | Email: admissions@vrcollege.edu | Mon-Fri 9 AM - 5 PM.",
            "friendly_answer": text,
            "matched_question": "How can I contact the college admission office?",
            "category": "Contact",
            "confidence": 1.0,
            "status": "matched",
            "is_fuzzy": False,
            "ai_generated": False,
            "visual": {
                "image": "campus_main.jpg",
                "caption": "🏛️ Administrative Block & Admissions Office"
            }
        }

    return None
