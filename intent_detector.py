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
    r"\bwhat\s+is\s+this\s+college\s+called\b",
    r"கல்லூரி.*பெயர்", r"கல்லூரியின் பெயர்", r"உங்கள் பெயர்"
]

COLLEGE_LOCATION_PATTERNS = [
    r"\bwhere\s+(is|are)\s+(your|the|this)?\s*(college|institution|campus|institute)\s*(located|situated)?\b",
    r"\b(college|campus)\s*(location|address|pincode)\b",
    r"\bhow\s+to\s+reach\s+(the|your)?\s*college\b",
    r"\bwhere\s+are\s+you\s+located\b",
    r"\bwhere\s+is\s+the\s+campus\b",
    r"எங்குள்ளது", r"அமைந்துள்ள.*இடம்", r"முகவரி"
]

COLLEGE_INTRO_PATTERNS = [
    r"\b(about|overview\s+of|history\s+of)\s+(the|your|vr)\s*(college|institution)\b",
    r"\btell\s+me\s+about\s+(vr|the|your)?\s*college\b",
    r"\bintroduce\s+(vr\s+college|the\s+institution)\b",
    r"\bwho\s+(was|is)\s+(the\s+)?founder\b",
    r"\bwho\s+founded\s+(the|your|this)?\s*(college|institution)\b",
    r"\bwhen\s+was\s+(the|your|this)?\s*(college|institution)\s*(founded|established|started)\b",
    r"\byear\s+of\s+establishment\b",
    r"\bwho\s+started\s+(the|your|this)?\s*(college|institution)\b",
    r"கல்லூரி.*பற்றி", r"அறிமுகம்"
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
    r"\bcourses\s+offered\b",
    r"பாடப்பிரிவு", r"படிப்பு", r"துறைகள்", r"courses"
]

SCHOLARSHIPS_PATTERNS = [
    r"\btell\s+me\s+about\s+scholarships?\b",
    r"\b(are\s+there\s+any|is\s+there\s+any)\s+scholarships?\b",
    r"\b(are\s+)?scholarships?\s+available\b",
    r"\bscholarship\s+(details|schemes?|eligibility|information)\b",
    r"\b(merit|sports)\s+scholarships?\b",
    r"\bfinancial\s+aid\b",
    r"\bfee\s+concession\b",
    r"\btuition\s+fee\s+waiver\b",
    r"உதவித்தொகை", r"கல்வி உதவித்தொகை", r"சலுகை"
]

HOSTEL_PATTERNS = [
    r"\btell\s+me\s+about\s+hostel\s+facilities\b",
    r"\b(are\s+)?hostel\s+facilities\s+available\b",
    r"\bhostel\s+(rules|curfew|timing|mess|food|dining|rooms?|accommodation)\b",
    r"\bcurfew\s+time\s+for\s+hostel\b",
    r"\bhostel\s+for\s+(boys|girls)\b",
    r"விடுதி", r"ஹாஸ்டல்", r"தங்கும் வசதி", r"மெஸ்"
]

TRANSPORTATION_PATTERNS = [
    r"\bwhat\s+(are\s+the\s+)?(bus|transport|transportation)\s+facilities\b",
    r"\bwhat\s+bus\s+facilities\s+are\s+available\b",
    r"\btell\s+me\s+about\s+transport(ation)?\b",
    r"\bbus\s+routes?\b",
    r"\bcollege\s+bus\s+(service|routes?)\b",
    r"\btransport\s+service\b",
    r"பேருந்து", r"போக்குவரத்து", r"பஸ்"
]

PLACEMENT_PATTERNS = [
    r"\bwhat\s+are\s+(the\s+)?placements?\b",
    r"\b(highest|average)\s+(salary\s+)?package\b",
    r"\bplacement\s+(statistics|records?|percentage|rate|details)\b",
    r"\bwhat\s+companies\s+visit\b",
    r"\btop\s+recruiters?\b",
    r"\bcampus\s+recruitment\b",
    r"வேலைவாய்ப்பு", r"கேம்பஸ் இன்டர்வியூ", r"சம்பளம்"
]

LIBRARY_PATTERNS = [
    r"\bshow\s+me\s+the\s+library\b",
    r"\btell\s+me\s+about\s+the\s+library\b",
    r"\blibrary\s+(timings?|hours?|working\s+hours?|facilities?)\b",
    r"\bhow\s+many\s+books\s+can\s+a\s+student\s+borrow\b",
    r"\bdigital\s+library\b",
    r"நூலகம்", r"லைப்ரரி"
]

ADMISSION_PATTERNS = [
    r"\bwhat\s+is\s+the\s+admission\s+procedure\b",
    r"\bhow\s+can\s+i\s+apply\s+for\s+admission\b",
    r"\beligibility\s+criteria\s+for\s+b\.?tech\b",
    r"\bwhen\s+does\s+(the\s+)?admission\s+process\s+start\b",
    r"\badmission\s+eligibility\b",
    r"\bhow\s+to\s+apply\b",
    r"சேர்க்கை", r"விண்ணப்ப", r"தகுதி"
]

FACULTY_PATTERNS = [
    r"\btell\s+me\s+about\s+(the\s+)?faculty\b",
    r"\bwho\s+are\s+the\s+(professors?|teachers?|faculty\s+members?)\b",
    r"\bfaculty\s+(qualifications?|members?|experience)\b",
    r"\bteaching\s+staff\b",
    r"பேராசிரியர்", r"ஆசிரியர்கள்"
]

CONTACT_PATTERNS = [
    r"\bhow\s+(can\s+i|to)\s+contact\s+(the\s+)?(college|admission\s+office)?\b",
    r"\b(contact|helpline|phone)\s+(number|details?|info)\b",
    r"\badmissions?\s+(phone|email|helpdesk)\b",
    r"\bemail\s+address\s+of\s+college\b",
    r"தொடர்பு", r"தொலைபேசி எண்", r"அலுவலகம்"
]

ACADEMIC_PATTERNS = [
    r"\bacademics?\s+(information|calendar|system)\b",
    r"\bhow\s+are\s+semester\s+examinations\s+conducted\b",
    r"\bminimum\s+attendance\s+required\b",
    r"\bexamination\s+rules?\b",
    r"தேர்வு", r"வருகை"
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
def get_intent_response(intent: Intent, query: str, language: str = "English") -> Optional[Dict[str, Any]]:
    """
    Returns the exact, user-friendly, and strictly relevant response for each intent.
    Never includes unrelated fee tables or generic fallback apologies.
    Supports English and Tamil dynamically.
    """
    is_tamil = (language == "Tamil")

    if intent == Intent.COLLEGE_NAME:
        if is_tamil:
            text = (
                f"எங்கள் கல்லூரியின் பெயர் **{COLLEGE_OFFICIAL_NAME}**. 😊 "
                "வணக்கம்! எங்கள் கல்லூரியைப் பற்றிய விவரங்களை உங்களுக்கு வழங்குவதில் மகிழ்ச்சி அடைகிறேன்."
            )
            raw_ans = f"எங்கள் கல்லூரியின் பெயர் {COLLEGE_OFFICIAL_NAME}."
            matched_q = "கல்லூரியின் பெயர் என்ன?"
        else:
            text = (
                f"Our college name is **{COLLEGE_OFFICIAL_NAME}**. 😊 "
                "Welcome! I'm happy to help you with information about our college."
            )
            raw_ans = f"Our college name is {COLLEGE_OFFICIAL_NAME}."
            matched_q = "What is your college name?"
        return {
            "answer": raw_ans,
            "friendly_answer": text,
            "matched_question": matched_q,
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
        if is_tamil:
            text = (
                f"**{COLLEGE_OFFICIAL_NAME}** அமைந்துள்ள இடம்:\n\n"
                "📍 **முகவரி:** நாலெட்ஜ் கேம்பஸ், செக்டார் 4, எஜுகேஷன் சிட்டி, அஞ்சல் குறியீடு: 560001, இந்தியா.\n\n"
                "எங்கள் 50 ஏக்கர் பசுமை வளாகம் முக்கிய நகர சாலைகள், மெட்ரோ மற்றும் தினசரி கல்லூரி பேருந்துகள் மூலம் எளிதில் இணைக்கப்பட்டுள்ளது. எங்களை நேரில் வந்து பார்வையிட அன்போடு வரவேற்கிறோம்! 🌿"
            )
            raw_ans = f"{COLLEGE_OFFICIAL_NAME} நாலெட்ஜ் கேம்பஸ், செக்டார் 4, எஜுகேஷன் சிட்டியில் அமைந்துள்ளது."
            matched_q = "கல்லூரி எங்கு அமைந்துள்ளது?"
        else:
            text = (
                f"**{COLLEGE_OFFICIAL_NAME}** is located at:\n\n"
                "📍 **Address:** Knowledge Campus, Sector 4, Education City, Pincode: 560001, Karnataka, India.\n\n"
                "Our 50-acre green campus is conveniently connected via major city roadways, metro stations, "
                "and our daily campus bus transit fleet. You are warmly welcome to visit us! 🌿"
            )
            raw_ans = f"{COLLEGE_OFFICIAL_NAME} is located at Knowledge Campus, Sector 4, Education City, Pincode 560001."
            matched_q = "Where is your college located?"
        return {
            "answer": raw_ans,
            "friendly_answer": text,
            "matched_question": matched_q,
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
        if is_tamil:
            text = (
                f"**{COLLEGE_OFFICIAL_NAME}**-க்கு உங்களை அன்புடன் வரவேற்கிறோம்! 🎓\n\n"
                "2005-ஆம் ஆண்டு நிறுவப்பட்ட எங்கள் நிறுவனம், AICTE அங்கீகாரம் மற்றும் NAAC 'A+' தரம் பெற்று "
                "கல்விச் சிறப்பு, பொறியியல் ஆராய்ச்சி மற்றும் சிறந்த எதிர்காலத்திற்கான வழிகாட்டியாக விளங்குகிறது.\n\n"
                "**முக்கிய சிறப்பம்சங்கள்:**\n"
                "- 🏛️ **50+ ஏக்கர் பசுமை வளாகம்** மற்றும் 24/7 அதிவேக வைஃபை வசதி\n"
                "- 🔬 **நவீன AI மற்றும் கணினி ஆய்வகங்கள்**\n"
                "- 💼 **92% நிலையான வளாக வேலைவாய்ப்பு** (அதிகபட்ச சம்பளம் ₹14.0 LPA)\n"
                "- 🏢 **மாணவ, மாணவியருக்கான நவீன விடுதிகள் & விளையாட்டு அரங்கம்**\n\n"
                "எங்கள் சேர்க்கை, பாடப்பிரிவுகள், விடுதிகள் அல்லது வளாக வாழ்க்கை குறித்து நீங்கள் எதையும் கேட்கலாம்! 😊"
            )
            raw_ans = f"{COLLEGE_OFFICIAL_NAME} AICTE அங்கீகாரம் மற்றும் NAAC 'A+' தரம் பெற்ற முன்னணி பொறியியல் கல்வி நிறுவனமாகும்."
            matched_q = "கல்லூரியை அறிமுகப்படுத்துங்கள்."
        else:
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
            raw_ans = f"{COLLEGE_OFFICIAL_NAME} is an AICTE-approved, NAAC 'A+' accredited engineering institution."
            matched_q = "Can you introduce your college?"
        return {
            "answer": raw_ans,
            "friendly_answer": text,
            "matched_question": matched_q,
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
        if is_tamil:
            text = (
                f"**{COLLEGE_OFFICIAL_NAME}** வழங்கும் அரசு அங்கீகாரம் பெற்ற பட்டப்படிப்புகள்: 🎓\n\n"
                "#### 🎓 இளங்கலை பட்டப்படிப்புகள் (B.Tech - 4 ஆண்டுகள் / 8 செமஸ்டர்கள்):\n"
                "- 💻 **கணினி அறிவியல் மற்றும் பொறியியல் (CSE)**\n"
                "- 🤖 **செயற்கை நுண்ணறிவு மற்றும் தரவு அறிவியல் (AI & DS)**\n"
                "- 📡 **மின்னணு மற்றும் தகவல் தொடர்பு பொறியியல் (ECE)**\n"
                "- ⚡ **மின் மற்றும் மின்னணு பொறியியல் (EEE)**\n"
                "- ⚙️ **மெக்கானிக்கல் இன்ஜினியரிங் (ME)**\n"
                "- 🏗️ **சிவில் இன்ஜினியரிங் (CE)**\n"
                "- 🌐 **தகவல் தொழில்நுட்பம் (IT)**\n\n"
                "#### 🎓 முதுகலை பட்டப்படிப்புகள்:\n"
                "- 🎓 **எம்.டெக் (M.Tech) - கணினி அறிவியல்**\n"
                "- 💼 **வணிக மேலாண்மை (MBA)**\n"
                "- 🖥️ **கணினி பயன்பாட்டியல் (MCA)**\n\n"
                "💡 *குறிப்பு: ஏதேனும் ஒரு குறிப்பிட்ட படிப்பிற்கான தகுதி அல்லது சேர்க்கை விவரங்களை அறிய விரும்புகிறீர்களா?*"
            )
            raw_ans = "நாங்கள் CSE, AI&DS, ECE, EEE, Mechanical, Civil, மற்றும் IT ஆகிய B.Tech படிப்புகளையும், M.Tech, MBA, மற்றும் MCA படிப்புகளையும் வழங்குகிறோம்."
            matched_q = "என்னென்ன பாடப்பிரிவுகள் உள்ளன?"
        else:
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
            raw_ans = "We offer B.Tech degrees in CSE, AI&DS, ECE, EEE, Mechanical, Civil, and IT, plus M.Tech, MBA, and MCA."
            matched_q = "What courses are available?"
        return {
            "answer": raw_ans,
            "friendly_answer": text,
            "matched_question": matched_q,
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
        if is_tamil:
            text = (
                f"ஆம்! **{COLLEGE_OFFICIAL_NAME}** மாணவர்களுக்கு பல்வேறு கல்வி உதவித்தொகைகளையும் சலுகைகளையும் வழங்குகிறது: 🎓\n\n"
                "- 🏆 **தகுதி உதவித்தொகை (Merit Scholarships):** நுழைவுத் தேர்வு மற்றும் தகுதிப் பொதுத்தேர்வில் அதிக மதிப்பெண் பெற்ற மாணவர்களுக்கு 50% வரை கல்விக் கட்டண தள்ளுபடி.\n"
                "- ⚽ **விளையாட்டுச் சலுகை:** மாநில அல்லது தேசிய அளவில் பதக்கம் வென்ற விளையாட்டு வீரர்களுக்கு 100% முழுக் கல்விக் கட்டணச் சலுகை.\n"
                "- 🏛️ **அரசு நலத்திட்டங்கள்:** இடஒதுக்கீட்டுப் பிரிவு மாணவர்களுக்கான அனைத்து அரசு மற்றும் போஸ்ட்-மெட்ரிக் உதவித்தொகைகளுக்கும் முழுமையான வழிகாட்டல்.\n"
                "- 💳 **செமஸ்டர் தவணை முறை:** அலுவலகத்தின் ஒப்புதலுடன் தவணை முறையில் கட்டணம் செலுத்தும் வசதி உள்ளது.\n\n"
                "💡 *குறிப்பு: நீங்கள் வலதுபுறம் உள்ள **Apply** பகுதி வழியாக உதவித்தொகைக்கான தகுதி குறித்து விசாரிக்கலாம்!*"
            )
            raw_ans = "தகுதி உதவித்தொகை (50% வரை தள்ளுபடி), விளையாட்டுச் சலுகை (100% தள்ளுபடி) மற்றும் அரசு நலத்திட்ட உதவித்தொகைகள் வழங்கப்படுகின்றன."
            matched_q = "கல்வி உதவித்தொகை விவரங்களை கூறுங்கள்."
        else:
            text = (
                f"Yes! **{COLLEGE_OFFICIAL_NAME}** actively provides generous scholarships and financial concessions to encourage talent: 🎓\n\n"
                "- 🏆 **Merit Scholarships:** Up to 50% tuition waiver awarded to the top 5% rankers in entrance exams and qualifying board marks.\n"
                "- ⚽ **Sports Concessions:** 100% full tuition waiver for athletes representing state or national medal events.\n"
                "- 🏛️ **Government Welfare Schemes:** Full assistance and guidance for reserved categories and post-matric government scholarships.\n"
                "- 💳 **Semester Installment Option:** Flexible split payment facility is available upon formal request to the Accounts Department.\n\n"
                "💡 *Tip: You can submit your scholarship eligibility query through the **Apply** tab on the right!*"
            )
            raw_ans = "Scholarships include Merit Scholarships (up to 50% waiver), Sports Concessions (100% waiver), and Government Welfare Schemes."
            matched_q = "Tell me about scholarships."
        return {
            "answer": raw_ans,
            "friendly_answer": text,
            "matched_question": matched_q,
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
        if is_tamil:
            text = (
                f"**{COLLEGE_OFFICIAL_NAME}** மாணவ, மாணவியருக்கு பாதுகாப்பான மற்றும் வசதியான விடுதி வசதிகளை வழங்குகிறது: 🏢\n\n"
                "- 🛏️ **அறை வசதிகள்:** ஏசி / நான்-ஏசி மற்றும் தனி, இரட்டை, மூன்று நபர் பகிரும் விசாலமான அறைகள்.\n"
                "- 🍽️ **மெஸ் உணவு:** தினமும் 4 வேளை சுகாதாரமான மற்றும் சத்தான சைவ / அசைவ உணவு.\n"
                "- ⚡ **வசதிகள்:** 24/7 அதிவேக வைஃபை, தடையற்ற மின்சார பேக்கப், படிக்கும் மேஜை மற்றும் சலவை வசதி.\n"
                "- 🛡️ **பாதுகாப்பு & நேரம்:** 24 மணி நேர சிசிடிவி கண்காணிப்பு, பயோமெட்ரிக் வருகை மற்றும் இரவு 8:30 மணி நேரக் கட்டுப்பாடு."
            )
            raw_ans = "மாணவ, மாணவியருக்கு ஏசி/நான்-ஏசி அறைகள், 4 வேளை உணவு, வைஃபை மற்றும் இரவு 8:30 மணி நேரக் கட்டுப்பாடுடன் கூடிய விடுதி வசதிகள் உள்ளன."
            matched_q = "விடுதி வசதிகள் பற்றி கூறுங்கள்."
        else:
            text = (
                f"**{COLLEGE_OFFICIAL_NAME}** provides secure, clean, and comfortable on-campus hostel facilities for both boys and girls: 🏢\n\n"
                "- 🛏️ **Room Accommodations:** Spacious single, double, and triple-sharing rooms with options for AC or Non-AC.\n"
                "- 🍽️ **Dining Mess:** Hygienic 4-meal daily dining serving nutritious vegetarian and non-vegetarian food.\n"
                "- ⚡ **Amenities:** 24/7 high-speed Wi-Fi, uninterrupted power backup, study desks, and modern laundry facilities.\n"
                "- 🛡️ **Security & Curfew:** Round-the-clock CCTV surveillance, biometric attendance, and a weekday curfew time of 8:30 PM (9:00 PM on weekends)."
            )
            raw_ans = "Hostel facilities are available for boys and girls with AC/Non-AC rooms, 4-meal mess, Wi-Fi, and 8:30 PM curfew."
            matched_q = "Tell me about hostel facilities."
        return {
            "answer": raw_ans,
            "friendly_answer": text,
            "matched_question": matched_q,
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
        if is_tamil:
            text = (
                f"**{COLLEGE_OFFICIAL_NAME}** விரிவான வளாக பேருந்து வசதியை இயக்குகிறது: 🚌\n\n"
                "- 🚍 **பேருந்து வழித்தடங்கள்:** நகரின் அனைத்து முக்கிய பகுதிகளையும் புறநகர்ப் பகுதிகளையும் இணைக்கும் 30+ குளிரூட்டப்பட்ட மற்றும் ஜிபிஎஸ் பொருத்தப்பட்ட பேருந்துகள்.\n"
                "- 🛡️ **பாதுகாப்பு:** அனுபவம் வாய்ந்த ஓட்டுநர்கள், வேகக் கட்டுப்பாட்டு கருவிகள், முதலுதவி வசதி மற்றும் பெற்றோருக்கு நேரடி ஜிபிஎஸ் கண்காணிப்பு வசதி.\n"
                "- ⏰ **நேரம்:** காலை 8:30 மணிக்கு கல்லூரி வருகை, மாலை 4:45 மணிக்கு புறப்பாடு."
            )
            raw_ans = "கல்லூரி 30-க்கும் மேற்பட்ட பேருந்துகளை அனைத்து முக்கிய நகர பகுதிகளுக்கும் இயக்குகிறது."
            matched_q = "பேருந்து வசதிகள் என்னென்ன உள்ளன?"
        else:
            text = (
                f"**{COLLEGE_OFFICIAL_NAME}** operates a comprehensive campus transit fleet: 🚌\n\n"
                "- 🚍 **Fleet Coverage:** Over 30 air-conditioned and GPS-enabled buses connecting all key city zones and suburban stops.\n"
                "- 🛡️ **Safety Standards:** Certified experienced drivers, speed governors, first-aid support, and live GPS route tracking for parents.\n"
                "- ⏰ **Timings:** Morning arrival at campus by 8:30 AM and evening departure at 4:45 PM."
            )
            raw_ans = "The college operates 30+ buses connecting all major city zones and residential suburbs."
            matched_q = "What bus facilities are available?"
        return {
            "answer": raw_ans,
            "friendly_answer": text,
            "matched_question": matched_q,
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
        if is_tamil:
            text = (
                f"**{COLLEGE_OFFICIAL_NAME}** மிகச் சிறந்த வளாக வேலைவாய்ப்பு சாதனையைப் பெற்றுள்ளது: 💼\n\n"
                "- 🌟 **வேலைவாய்ப்பு சதவீதம்:** தகுதியுள்ள மாணவர்களில் 92% பேர் முன்னணி நிறுவனங்களில் பணி வாய்ப்பு பெற்றுள்ளனர்.\n"
                "- 🚀 **அதிகபட்ச சம்பளம் (Highest CTC):** ஆண்டுக்கு **₹14.0 LPA**\n"
                "- 📈 **சராசரி சம்பளம்:** ஆண்டுக்கு சுமார் **₹4.8 LPA**\n"
                "- 🏢 **முன்னணி நிறுவனங்கள்:** TCS, Infosys, Wipro, Cognizant, Tech Mahindra, Accenture மற்றும் முன்னணி நிறுவனங்கள்.\n"
                "- 🎯 **சிறப்புப் பயிற்சி:** 3-ஆம் ஆண்டு முதல் தொடங்கும் ஆப்டிட்யூட், மாதிரி நேர்காணல் மற்றும் கோடிங் பயிற்சிகள்."
            )
            raw_ans = "92% வேலைவாய்ப்பு விகிதம், அதிகபட்ச சம்பளம் ₹14 LPA மற்றும் சராசரி சம்பளம் ₹4.8 LPA உடன் TCS, Infosys, Wipro போன்ற முன்னணி நிறுவனங்கள் வருகின்றன."
            matched_q = "வளாக வேலைவாய்ப்பு விவரங்கள் என்ன?"
        else:
            text = (
                f"**{COLLEGE_OFFICIAL_NAME}** maintains a distinguished campus placement track record: 💼\n\n"
                "- 🌟 **Placement Rate:** 92% of all eligible graduating students successfully placed.\n"
                "- 🚀 **Highest CTC:** ₹14.0 LPA offered by tier-1 product and analytics corporations.\n"
                "- 📈 **Average CTC:** Approximately ₹4.8 LPA.\n"
                "- 🏢 **Top Recruiters:** TCS, Infosys, Wipro, Cognizant, Tech Mahindra, Accenture, and leading engineering startups.\n"
                "- 🎯 **Dedicated Training:** Aptitude training, mock interviews, and technical coding bootcamps starting from 3rd year."
            )
            raw_ans = "Placement rate is 92% with highest CTC of 14 LPA and average of 4.8 LPA from recruiters like TCS, Infosys, and Wipro."
            matched_q = "What are the placements?"
        return {
            "answer": raw_ans,
            "friendly_answer": text,
            "matched_question": matched_q,
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
        if is_tamil:
            text = (
                f"**{COLLEGE_OFFICIAL_NAME}** மத்திய டிஜிட்டல் நூலகம் அதிநவீன கற்றல் மையமாக விளங்குகிறது: 📚\n\n"
                "- 📖 **புத்தக இருப்பு:** 50,000-க்கும் மேற்பட்ட பாடப்புத்தகங்கள், குறிப்பு நூல்கள் மற்றும் 120+ தேசிய மற்றும் சர்வதேச ஆய்விதழ்கள்.\n"
                "- 💻 **டிஜிட்டல் வசதி:** IEEE, Springer, ScienceDirect இணைய அணுகலுடன் கூடிய கணினி ஆய்வு மையம்.\n"
                "- ⏰ **இயங்கும் நேரம்:** திங்கள் முதல் சனிக்கிழமை வரை காலை 8:00 மணி முதல் இரவு 8:00 மணி வரை (தேர்வு காலங்களில் இரவு 10:00 மணி வரை).\n"
                "- 📚 **புத்தக கடன்:** இளங்கலை மாணவர்கள் 4 புத்தகங்களை 14 நாட்களுக்கும், முதுகலை மாணவர்கள் 6 புத்தகங்களையும் எடுத்துச் செல்லலாம்."
            )
            raw_ans = "மத்திய நூலகத்தில் 50,000+ புத்தகங்கள், IEEE டிஜிட்டல் அணுகல் உள்ளது. திங்கள் முதல் சனி வரை காலை 8:00 முதல் இரவு 8:00 வரை இயங்குகிறது."
            matched_q = "நூலக வசதிகள் என்னென்ன?"
        else:
            text = (
                f"Our Central Digital Library at **{COLLEGE_OFFICIAL_NAME}** is a state-of-the-art learning hub: 📚\n\n"
                "- 📖 **Collection:** Over 50,000 print textbooks, reference titles, and subscriptions to 120+ national and international journals.\n"
                "- 💻 **Digital Repositories:** High-speed internet stations with direct access to IEEE, Springer, ScienceDirect, and DELNET.\n"
                "- ⏰ **Working Hours:** Monday to Saturday from 8:00 AM to 8:00 PM (extended till 10:00 PM during exam weeks).\n"
                "- 📚 **Borrowing Policy:** Undergraduates can borrow up to 4 books for 14 days, and postgraduates up to 6 books."
            )
            raw_ans = "Central Library houses 50,000+ volumes, IEEE digital access, and operates 8 AM to 8 PM Monday to Saturday."
            matched_q = "Show me the library."
        return {
            "answer": raw_ans,
            "friendly_answer": text,
            "matched_question": matched_q,
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
        if is_tamil:
            text = (
                f"**{COLLEGE_OFFICIAL_NAME}** சேர்க்கை மற்றும் தகுதி வழிகாட்டுதல்கள்: 📝\n\n"
                "- 🎓 **B.Tech தகுதி:** 10+2 / மேல்நிலை (+2) தேர்வில் இயற்பியல், கணிதம் மற்றும் வேதியியல்/கணினியில் குறைந்தபட்சம் 45% மதிப்பெண்கள் (இடஒதுக்கீட்டுப் பிரிவினருக்கு 40%).\n"
                "- 📑 **விண்ணப்பிக்கும் முறை:** அதிகாரப்பூர்வ இணையதளம் மூலம் ஆன்லைனில் விண்ணப்பிக்கலாம் அல்லது கல்லூரி சேர்க்கை அலுவலகத்தில் நேரடியாகப் படிவம் சமர்ப்பிக்கலாம்.\n"
                "- 🗓️ **சேர்க்கை காலம்:** ஆண்டுதோறும் ஏப்ரல் / மே மாதங்களில் சேர்க்கை தொடங்குகிறது.\n"
                "- 📞 **உதவி எண்:** +91 98765 43210 (திங்கள் - வெள்ளி: காலை 9:00 - மாலை 5:00)."
            )
            raw_ans = "B.Tech சேர்க்கைக்கு 10+2 தேர்வில் இயற்பியல், கணிதம் பாடங்களுடன் 45% மதிப்பெண்கள் தேவை. ஏப்ரல்/மே மாதங்களில் சேர்க்கை தொடங்குகிறது."
            matched_q = "சேர்க்கை நடைமுறை என்ன?"
        else:
            text = (
                f"Here are the admissions and eligibility guidelines for **{COLLEGE_OFFICIAL_NAME}**: 📝\n\n"
                "- 🎓 **B.Tech Eligibility:** Minimum 45% aggregate in 10+2 / Higher Secondary (40% for reserved categories) with Physics, Mathematics, and Chemistry/CS.\n"
                "- 📑 **Application Process:** Apply online through our official portal or submit forms directly at the Admissions Cell on campus.\n"
                "- 🗓️ **Academic Cycle:** Admissions open annually in April / May.\n"
                "- 📞 **Admissions Helpline:** +91 98765 43210 (Mon - Fri: 9:00 AM - 5:00 PM)."
            )
            raw_ans = "B.Tech admission requires 45% aggregate in 10+2 with PCM. Applications open in April/May."
            matched_q = "What is the admission procedure?"
        return {
            "answer": raw_ans,
            "friendly_answer": text,
            "matched_question": matched_q,
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
        if is_tamil:
            text = (
                f"**{COLLEGE_OFFICIAL_NAME}** மிகச் சிறந்த, மாணவர் நலனில் அக்கறை கொண்ட பேராசிரியர்களைக் கொண்டுள்ளது: 👨‍🏫\n\n"
                "- 🎓 **உயர்ந்த தகுதி:** 65%-க்கும் மேற்பட்ட மூத்த பேராசிரியர்கள் IIT, NIT மற்றும் புகழ்பெற்ற பல்கலைக்கழகங்களில் Ph.D. பட்டம் பெற்றவர்கள்.\n"
                "- 🔬 **ஆராய்ச்சி மேன்மை:** பேராசிரியர்கள் IEEE மற்றும் Springer ஆய்விதழ்களில் ஆய்வுக் கட்டுரைகளையும் காப்புரிமைகளையும் பதிவு செய்துள்ளனர்.\n"
                "- 🤝 **தனிநபர் வழிகாட்டல்:** ஒவ்வொரு 15 மாணவர்களுக்கும் ஒரு பேராசிரியர் ஆலோசகர் நியமிக்கப்பட்டு தொடர்ந்து கண்காணிக்கப்படுகிறார்கள்."
            )
            raw_ans = "எங்கள் பேராசிரியர்களில் 65%+ பேர் Ph.D. முடித்தவர்கள், மற்றும் 1:15 வழிகாட்டி-மாணவர் விகிதம் பராமரிக்கப்படுகிறது."
            matched_q = "பேராசிரியர்கள் பற்றி கூறுங்கள்."
        else:
            text = (
                f"**{COLLEGE_OFFICIAL_NAME}** is proud of its distinguished, student-centric academic faculty: 👨‍🏫\n\n"
                "- 🎓 **High Qualifications:** Over 65% of senior professors hold Ph.D. degrees from premier IITs, NITs, and reputed universities.\n"
                "- 🔬 **Research Excellence:** Faculty members actively lead sponsored research, patents, and publications in IEEE and Springer.\n"
                "- 🤝 **Personalized Mentorship:** A 1:15 faculty-to-student mentor ratio ensures continuous academic monitoring and guidance."
            )
            raw_ans = "Our faculty includes 65%+ Ph.D. professors with active research, maintaining a 1:15 mentor-to-student ratio."
            matched_q = "Tell me about the faculty."
        return {
            "answer": raw_ans,
            "friendly_answer": text,
            "matched_question": matched_q,
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
        if is_tamil:
            text = (
                f"**{COLLEGE_OFFICIAL_NAME}** அதிகாரப்பூர்வ தொடர்பு விவரங்கள்: 📞\n\n"
                "- 📞 **உதவி எண்:** +91 98765 43210 / 0123-456789\n"
                "- ✉️ **மின்னஞ்சல்:** admissions@vrcollege.edu\n"
                "- 🏛️ **சேர்க்கை அலுவலகம்:** தரைத்தளம், பிளாக் A, நாலெட்ஜ் கேம்பஸ், செக்டார் 4, எஜுகேஷன் சிட்டி - 560001.\n"
                "- ⏰ **அலுவலக நேரம்:** திங்கள் - வெள்ளி: காலை 9:00 - மாலை 5:00 | சனி: காலை 9:00 - மதியம் 1:00."
            )
            raw_ans = "உதவி எண்: +91 98765 43210 / 0123-456789 | மின்னஞ்சல்: admissions@vrcollege.edu | திங்கள்-வெள்ளி காலை 9 முதல் மாலை 5 வரை."
            matched_q = "கல்லூரி சேர்க்கை அலுவலகத்தை எவ்வாறு தொடர்புகொள்வது?"
        else:
            text = (
                f"Here are the official contact details for **{COLLEGE_OFFICIAL_NAME}**: 📞\n\n"
                "- 📞 **Helpline:** +91 98765 43210 / 0123-456789\n"
                "- ✉️ **Email:** admissions@vrcollege.edu\n"
                "- 🏛️ **Admissions Cell:** Ground Floor, Block A, Knowledge Campus, Sector 4, Education City, Pincode: 560001\n"
                "- ⏰ **Office Timings:** Mon - Fri: 9:00 AM - 5:00 PM | Sat: 9:00 AM - 1:00 PM."
            )
            raw_ans = "Helpline: +91 98765 43210 / 0123-456789 | Email: admissions@vrcollege.edu | Mon-Fri 9 AM - 5 PM."
            matched_q = "How can I contact the college admission office?"
        return {
            "answer": raw_ans,
            "friendly_answer": text,
            "matched_question": matched_q,
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
