"""
Image Manager Module for AI-Based College Enquiry Chatbot.

Implements a dynamic image selection engine across 15 campus categories that:
1. Detects the precise topical category from user queries, answers, and metadata.
2. Selects from multiple high-resolution photographs per category.
3. Strictly prevents repeating the immediately previous image.
4. Provides interactive image cards with category titles, descriptions, and quick-prompts.
5. Supplies contextual suggestion chips for interactive UI exploration.
"""

import os
import random
import re
from typing import Dict, Any, List, Optional, Tuple

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

# -------------------------------------------------------------
# 1. Topic Image Collection across 15 College Categories
# -------------------------------------------------------------
TOPIC_IMAGE_CATALOG: Dict[str, Dict[str, Any]] = {
    "campus": {
        "title": "College Campus",
        "description": "50-acre green knowledge campus with state-of-the-art academic blocks and quads.",
        "quick_prompt": "Tell me about the college campus and infrastructure",
        "keywords": [
            "campus", "ground", "acres", "building", "infrastructure", "location", "address",
            "quad", "architecture", "where is", "reach", "visit"
        ],
        "images": [
            {"image": "campus_main.jpg", "caption": "🏛️ VR College of Engineering 50-Acre Main Academic Quad & Quadrangle"},
            {"image": "campus_aerial.jpg", "caption": "🌲 Panoramic Aerial View of Lush Green Campus"}
        ]
    },
    "admissions": {
        "title": "Admissions & Eligibility",
        "description": "Comprehensive admission guidance, eligibility criteria, cutoff counseling, and application forms.",
        "quick_prompt": "What is the admission procedure and eligibility criteria?",
        "keywords": [
            "admission", "admissions", "apply", "eligibility", "eligible", "cutoff", "entrance",
            "counseling", "seat", "seats", "process", "deadline", "application", "enrollment"
        ],
        "images": [
            {"image": "admissions_desk.jpg", "caption": "📝 Admissions Counseling & Information Desk"},
            {"image": "admissions_hall.jpg", "caption": "🎓 Student Registration & Verification Hall"}
        ]
    },
    "courses": {
        "title": "Engineering Courses",
        "description": "Accredited 4-year B.Tech undergraduate degree programs and postgraduate courses.",
        "quick_prompt": "Which undergraduate courses are offered?",
        "keywords": [
            "course", "courses", "program", "programs", "degree", "curriculum", "b.tech", "btech",
            "m.tech", "mtech", "mba", "mca", "syllabus", "academics", "branch", "branches"
        ],
        "images": [
            {"image": "engineering_quad.jpg", "caption": "⚙️ Faculty of Engineering Academic Complex"},
            {"image": "courses_seminar.jpg", "caption": "📐 Modern Engineering Lecture Theatre & Seminars"}
        ]
    },
    "cse": {
        "title": "Computer Science Department",
        "description": "Premier department specializing in AI, Machine Learning, Cloud Computing, and Software Engineering.",
        "quick_prompt": "Tell me about the Computer Science Department",
        "keywords": [
            "computer science", "cse", "comp sci", "coding", "software", "programming", "ai & ds",
            "data science", "cyber", "algorithms"
        ],
        "images": [
            {"image": "cs_dept.jpg", "caption": "💻 Department of Computer Science & AI Center"},
            {"image": "cs_coding.jpg", "caption": "⚡ Advanced Software Development & Coding Sandbox"}
        ]
    },
    "ece": {
        "title": "Electronics & Communication Department",
        "description": "Pioneering VLSI design, embedded robotics, signal processing, and communication networks.",
        "quick_prompt": "Tell me about the ECE department and labs",
        "keywords": [
            "ece", "electronics", "communication engineering", "circuits", "vlsi", "embedded",
            "microcontroller", "robotics", "signals", "hardware"
        ],
        "images": [
            {"image": "ece_lab.jpg", "caption": "🔌 VLSI Design & Microcontroller Systems Laboratory"},
            {"image": "ece_circuits.jpg", "caption": "📡 Signal Processing & Robotics Hardware Center"}
        ]
    },
    "laboratories": {
        "title": "Research & Computing Labs",
        "description": "High-end computing facilities, prototyping maker-spaces, and specialized testing equipment.",
        "quick_prompt": "What laboratory facilities are available for students?",
        "keywords": [
            "laboratory", "laboratories", "lab", "labs", "practical", "equipment", "computing",
            "research lab", "maker space", "experiment"
        ],
        "images": [
            {"image": "computer_lab.jpg", "caption": "🔬 Advanced High-Performance AI & Computing Lab"},
            {"image": "research_lab.jpg", "caption": "🧪 Prototyping Maker-Space & Innovation Workstations"}
        ]
    },
    "library": {
        "title": "Central Digital Library",
        "description": "50,000+ print volumes, IEEE & Springer digital e-journals, quiet pods, and discussion halls.",
        "quick_prompt": "What are the central library working hours and facilities?",
        "keywords": [
            "library", "librari", "book", "books", "journal", "journals", "reading room", "e-book",
            "study pod", "borrow", "borrowing", "ieee", "springer"
        ],
        "images": [
            {"image": "library.jpg", "caption": "📚 Central Digital Library & Quiet Study Pods"},
            {"image": "library_reading.jpg", "caption": "📖 Reference Section & Digital Knowledge Repositories"}
        ]
    },
    "hostel": {
        "title": "Hostel Facilities & Dining",
        "description": "Separate secure resident halls for boys and girls with 4-meal hygienic dining and 24/7 Wi-Fi.",
        "quick_prompt": "Tell me about hostel accommodation and mess facilities",
        "keywords": [
            "hostel", "hostels", "hostal", "hostle", "accommodation", "mess", "dining", "curfew",
            "warden", "room", "rooms", "sharing", "boarding", "residence"
        ],
        "images": [
            {"image": "hostel.jpg", "caption": "🏢 Furnished Student Residence Quarters & Wi-Fi"},
            {"image": "hostel_dining.jpg", "caption": "🍽️ Hygienic 4-Meal Multi-Cuisine Student Dining Hall"}
        ]
    },
    "transportation": {
        "title": "Campus Transportation Fleet",
        "description": "Air-conditioned bus fleet covering 30+ designated city and suburban routes.",
        "quick_prompt": "What are the college transport routes and bus charges?",
        "keywords": [
            "transport", "transportation", "bus", "buses", "transpot", "route", "routes", "commute",
            "pickup", "transit", "parking", "vehicle"
        ],
        "images": [
            {"image": "transport_bus.jpg", "caption": "🚌 Air-Conditioned Campus Shuttle & Bus Fleet"},
            {"image": "transport_parking.jpg", "caption": "🅿️ Dedicated Student Transit Hub & Safe Parking"}
        ]
    },
    "sports": {
        "title": "Sports & Athletic Arena",
        "description": "Olympic-grade athletic ground, cricket turf, basketball courts, and modern fitness gymnasium.",
        "quick_prompt": "What sports and fitness facilities are available on campus?",
        "keywords": [
            "sport", "sports", "game", "games", "cricket", "football", "turf", "ground", "gym",
            "gymnasium", "fitness", "athletic", "badminton", "basketball"
        ],
        "images": [
            {"image": "sports.jpg", "caption": "⚽ Olympic-Standard Athletic Ground & Multi-Sport Turf"},
            {"image": "sports_indoor.jpg", "caption": "🏸 Indoor Sports Complex, Badminton & Fitness Gym"}
        ]
    },
    "cultural": {
        "title": "Cultural Events & Arts",
        "description": "Vibrant campus life with annual fest 'VR Utsav', student music bands, drama, and photography clubs.",
        "quick_prompt": "What cultural events and student clubs take place?",
        "keywords": [
            "cultural", "fest", "festival", "events", "celebration", "arts", "drama", "music",
            "dance", "band", "utsav", "clubs", "extracurricular"
        ],
        "images": [
            {"image": "cultural_fest.jpg", "caption": "🎉 Annual 'VR Fest' Inter-College Extravaganza"},
            {"image": "cultural_music.jpg", "caption": "🎭 Acoustic Performing Arts Stage & Student Bands"}
        ]
    },
    "symposiums": {
        "title": "Technical Symposiums & Hackathons",
        "description": "National-level hackathons, coding tournaments, robotics exhibitions, and technical conclaves.",
        "quick_prompt": "Tell me about technical symposiums and hackathons",
        "keywords": [
            "symposium", "technical", "hackathon", "techfest", "expo", "robotics", "conclave",
            "coding competition", "conference", "paper presentation", "patent"
        ],
        "images": [
            {"image": "tech_symposium.jpg", "caption": "💡 National Hackathon & Engineering Conclave"},
            {"image": "tech_expo.jpg", "caption": "🤖 Student Innovation Expo & Robotics Challenge"}
        ]
    },
    "placements": {
        "title": "Corporate Placements & Career Cell",
        "description": "Consistent 92% placement track record with top recruiters offering packages up to ₹14 LPA.",
        "quick_prompt": "What are the recent campus placement statistics and top recruiters?",
        "keywords": [
            "placement", "placements", "recruit", "recruiter", "recruiters", "salary", "package",
            "ctc", "highest package", "average package", "job", "career", "companies", "tcs", "infosys"
        ],
        "images": [
            {"image": "placement_drive.jpg", "caption": "💼 Corporate Campus Recruitment & Interview Drives"},
            {"image": "students_group.jpg", "caption": "🤝 Placed Engineering Batch at Top Tier-1 Tech MNCs"}
        ]
    },
    "scholarships": {
        "title": "Scholarships & Financial Aid",
        "description": "Generous merit scholarships, sports concessions, government schemes, and semester installment plans.",
        "quick_prompt": "What scholarships and tuition fee concessions are offered?",
        "keywords": [
            "scholarship", "scholarships", "scolorship", "financial aid", "concession", "waiver",
            "fee", "fees", "tuition", "cost", "installment", "installments", "expense"
        ],
        "images": [
            {"image": "students_hero.jpg", "caption": "🎓 Merit Scholarship Awardees & Academic Scholars"},
            {"image": "scholarship_convocation.jpg", "caption": "📜 Annual Excellence Awards & Tuition Waivers"}
        ]
    },
    "faculty": {
        "title": "Faculty & Smart Classrooms",
        "description": "Distinguished professors, Ph.D. scholars, and interactive air-conditioned digital lecture halls.",
        "quick_prompt": "Tell me about the faculty members and classroom facilities",
        "keywords": [
            "faculty", "professor", "professors", "teacher", "teachers", "staff", "classroom",
            "classrooms", "smart class", "lecture hall", "teaching", "mentor", "mentorship"
        ],
        "images": [
            {"image": "classroom_smart.jpg", "caption": "🖥️ Smart Interactive Digital Lecture Theatre"},
            {"image": "faculty_discussion.jpg", "caption": "👨‍🏫 Ph.D. Faculty Mentorship & Student Guidance"}
        ]
    }
}

# General Fallback Pool when no specific topic matches
GENERAL_CAMPUS_IMAGES: List[Dict[str, str]] = [
    {"image": "campus_main.jpg", "caption": "🏛️ VR College of Engineering 50-Acre Main Academic Quad"},
    {"image": "campus_aerial.jpg", "caption": "🌲 Green Eco-Friendly Campus Overview"},
    {"image": "students_group.jpg", "caption": "🎓 Vibrant Campus Life & Student Communities"},
    {"image": "classroom_smart.jpg", "caption": "🖥️ Modern Academic Infrastructure"}
]


# -------------------------------------------------------------
# 2. Dynamic Image Selection with Anti-Repetition Engine
# -------------------------------------------------------------
def has_word(text: str, keywords: List[str]) -> bool:
    """Checks whether any keyword appears as a whole word or phrase in text."""
    for kw in keywords:
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def detect_category(query: str, answer: str = "", category_hint: Optional[str] = None) -> str:
    """
    Intelligently identifies the best matching category among the 15 categories
    using whole-word boundary matching to avoid accidental substring collisions.
    """
    combined = f"{query} {answer} {category_hint or ''}".lower()

    # Priority 1: Direct Category Hint matching
    if category_hint:
        hint_lower = category_hint.lower()
        if "hostel" in hint_lower:
            return "hostel"
        if "fee" in hint_lower or "scholarship" in hint_lower:
            return "scholarships"
        if "placement" in hint_lower:
            return "placements"
        if "librar" in hint_lower:
            return "library"
        if "course" in hint_lower:
            return "courses"
        if "admission" in hint_lower:
            return "admissions"

    # Priority 2: Specialized and precise categories
    if has_word(combined, ["computer science", "cse", "coding", "software development", "ai & ds", "data science"]):
        return "cse"
    if has_word(combined, ["ece", "electronics", "communication engineering", "vlsi", "microcontroller", "circuits", "signal processing"]):
        return "ece"
    if has_word(combined, ["symposium", "symposiums", "hackathon", "hackathons", "techfest", "tech expo", "robotics expo", "conclave"]):
        return "symposiums"
    if has_word(combined, ["cultural", "culturals", "event", "events", "fest", "festival", "music", "dance", "drama", "arts", "band", "utsav"]):
        return "cultural"
    if has_word(combined, ["bus", "buses", "transport", "transportation", "route", "routes", "commute", "pickup", "transit"]):
        return "transportation"
    if has_word(combined, ["sport", "sports", "cricket", "football", "turf", "gym", "gymnasium", "badminton", "basketball", "athletics"]):
        return "sports"
    if has_word(combined, ["hostel", "hostels", "hostal", "hostle", "mess", "dining", "curfew", "warden", "room sharing"]):
        return "hostel"
    if has_word(combined, ["placement", "placements", "recruit", "recruiter", "recruiters", "package", "ctc", "salary", "recruitment"]):
        return "placements"
    if has_word(combined, ["library", "libraries", "librari", "book", "books", "journal", "journals", "reading room", "borrow"]):
        return "library"
    if has_word(combined, ["fee", "fees", "tuition", "cost", "scholarship", "scholarships", "scolorship", "financial aid", "concession", "installment"]):
        return "scholarships"
    if has_word(combined, ["admission", "admissions", "apply", "eligibility", "cutoff", "entrance exam", "seats", "application"]):
        return "admissions"
    if has_word(combined, ["lab", "labs", "laboratory", "laboratories", "practical exam", "equipment", "maker space"]):
        return "laboratories"
    if has_word(combined, ["faculty", "professor", "professors", "teacher", "teachers", "smart class", "classroom", "classrooms", "lecture theatre"]):
        return "faculty"
    if has_word(combined, ["course", "courses", "b.tech", "btech", "degree", "branch", "branches", "curriculum", "academics"]):
        return "courses"

    # Default: General campus
    return "campus"


def get_dynamic_visual(
    query: str,
    answer: str = "",
    category_hint: Optional[str] = None,
    last_image: Optional[str] = None
) -> Dict[str, str]:
    """
    Selects an image for the question satisfying all criteria:
    - Never displays the same image repeatedly.
    - Picks according to user's question.
    - Randomly selects from multiple images belonging to the same category.
    - Avoids repeating the immediately previous image.
    - Uses a suitable fallback if an image is missing on disk.
    """
    cat_key = detect_category(query, answer, category_hint)
    cat_info = TOPIC_IMAGE_CATALOG.get(cat_key, TOPIC_IMAGE_CATALOG["campus"])
    image_candidates = cat_info["images"]

    # Filter candidates that exist on disk
    valid_candidates = [
        item for item in image_candidates
        if os.path.exists(os.path.join(ASSETS_DIR, item["image"]))
    ]

    # If none found on disk, fallback to general pool
    if not valid_candidates:
        valid_candidates = [
            item for item in GENERAL_CAMPUS_IMAGES
            if os.path.exists(os.path.join(ASSETS_DIR, item["image"]))
        ]

    # In extreme case where assets are completely missing, return default structure
    if not valid_candidates:
        return {
            "image": "campus_main.jpg",
            "caption": "🏛️ VR College of Engineering 50-Acre Campus",
            "category": cat_info["title"]
        }

    # Anti-Repetition Rule: Do not repeat immediately previous image if multiple exist
    non_repeating = [img for img in valid_candidates if img["image"] != last_image]
    chosen = random.choice(non_repeating) if non_repeating else random.choice(valid_candidates)

    return {
        "image": chosen["image"],
        "caption": chosen["caption"],
        "category": cat_info["title"],
        "category_id": cat_key
    }


# -------------------------------------------------------------
# 3. Interactive Image Cards Data Collection
# -------------------------------------------------------------
def get_all_interactive_cards() -> List[Dict[str, Any]]:
    """
    Returns the complete list of 15 interactive cards for the UI showcase.
    """
    cards = []
    for cat_id, data in TOPIC_IMAGE_CATALOG.items():
        primary_img = data["images"][0]["image"]
        img_path = os.path.join(ASSETS_DIR, primary_img)
        # Ensure image exists or fallback
        if not os.path.exists(img_path):
            primary_img = "campus_main.jpg"

        cards.append({
            "id": cat_id,
            "title": data["title"],
            "description": data["description"],
            "image": primary_img,
            "quick_prompt": data["quick_prompt"]
        })
    return cards


def get_contextual_chips(query: str, category_id: Optional[str] = None) -> List[Tuple[str, str]]:
    """
    Returns 3 relevant quick-response suggestion chips (Emoji + Label, Query Text)
    based on the current topic to provide seamless interactive click navigation.
    """
    cat = category_id or detect_category(query)

    chip_map = {
        "scholarships": [
            ("🏢 Hostel Fee Details", "How much is hostel accommodation?"),
            ("🎓 B.Tech Branch Fees", "What is the ECE and CSE fee?"),
            ("📝 Admission Procedure", "What is the admission procedure?")
        ],
        "hostel": [
            ("💰 Complete Fee Structure", "Give me the complete fee structure."),
            ("⏰ Hostel Curfew & Rules", "What is the curfew time for hostel students?"),
            ("🚌 Bus Transport Routes", "What are the transport fee and bus charges?")
        ],
        "courses": [
            ("💻 Computer Science Dept", "Tell me about the Computer Science Department"),
            ("💰 Annual Tuition Fees", "What are the annual tuition fees for courses?"),
            ("💼 Placement Packages", "What was the highest placement package?")
        ],
        "cse": [
            ("🔬 AI Research Labs", "What laboratories are available?"),
            ("💼 Top Tech Recruiters", "What companies visit for campus recruitment?"),
            ("💰 CSE Tuition Fee", "What is the CSE fee?")
        ],
        "ece": [
            ("🔌 ECE Hardware Labs", "What laboratories are available in ECE?"),
            ("💰 ECE Tuition Fee", "What is the ECE fee?"),
            ("🎓 Engineering Courses", "Which undergraduate courses are offered?")
        ],
        "placements": [
            ("🏆 Highest CTC Package", "What was the highest and average salary package in recent placements?"),
            ("🏢 Recruiting Partners", "What companies visit the college for campus recruitment?"),
            ("💰 Course Fee Structure", "Give me the complete fee structure.")
        ],
        "library": [
            ("⏰ Library Working Hours", "What are the library timings and working hours?"),
            ("📖 Book Borrowing Limits", "How many books can a student borrow at a time?"),
            ("🏛️ Campus Facilities", "Tell me about the college campus and infrastructure")
        ],
        "sports": [
            ("🎉 Cultural Events & Fest", "What cultural events and student clubs take place?"),
            ("🏢 Hostel Facilities", "Are hostel facilities available for boys and girls?"),
            ("🏆 Sports Concessions", "Are sports scholarships available?")
        ]
    }

    return chip_map.get(cat, [
        ("🎓 Courses Offered", "What undergraduate courses are offered?"),
        ("💰 College Fees", "Give me the complete fee structure."),
        ("🏢 Hostel & Dining", "How much is hostel accommodation?")
    ])
