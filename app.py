"""
AI-Based College Enquiry Chatbot - Streamlit User Interface.

A modern, responsive, and intuitive web interface designed with an executive
blue-and-white theme, two-column interactive layout, quick FAQ shortcuts,
and real-time NLP match diagnostics.
"""

import os
import streamlit as st
import pandas as pd
from data_loader import load_faq_data, get_categories, DataLoaderError
from chatbot import CollegeChatbot

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI College Enquiry Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Modern CSS Stylesheet
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Righteous&family=Montserrat:wght@800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Transparent App Viewport, Header & Sidebar */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stSidebar"],
    [data-testid="stSidebarContent"],
    [data-testid="stToolbar"] {
        background-color: transparent !important;
        background: transparent !important;
    }

    /* Top Navigation / Brand Banner */
    .brand-hero {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 58, 138, 0.92) 50%, rgba(37, 99, 235, 0.88) 100%);
        padding: 24px 28px;
        border-radius: 18px;
        color: #FFFFFF;
        margin-bottom: 20px;
        box-shadow: 0 12px 28px -5px rgba(30, 58, 138, 0.30);
        border: 1px solid rgba(255, 255, 255, 0.18);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
    }
    .hero-top-brand {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
        padding-bottom: 12px;
        margin-bottom: 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.15);
    }
    .hero-inst-name {
        font-size: 0.85rem;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #93C5FD;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .hero-accred-text {
        font-size: 0.75rem;
        color: #CBD5E1;
        font-weight: 500;
        margin-top: 2px;
    }
    .hero-live-indicator {
        background: rgba(16, 185, 129, 0.2);
        color: #A7F3D0;
        border: 1px solid rgba(52, 211, 153, 0.4);
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.74rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #34D399;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px #34D399;
    }
    .hero-brand-stats-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
        gap: 10px;
        margin-top: 16px;
        padding-top: 14px;
        border-top: 1px solid rgba(255, 255, 255, 0.14);
    }
    .hero-stat-item {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 10px;
        padding: 8px 10px;
        text-align: center;
    }
    .hero-stat-val {
        font-size: 1.12rem;
        font-weight: 800;
        color: #F8FAFC;
        line-height: 1.1;
    }
    .hero-stat-desc {
        font-size: 0.68rem;
        font-weight: 600;
        color: #93C5FD;
        text-transform: uppercase;
        letter-spacing: 0.4px;
        margin-top: 3px;
    }
    .brand-title {
        font-family: 'Righteous', 'Montserrat', 'Plus Jakarta Sans', sans-serif;
        font-size: 2.15rem;
        font-weight: 900;
        margin: 0;
        letter-spacing: 0.8px;
        color: #FFFFFF !important;
        display: flex;
        align-items: center;
        gap: 12px;
        /* Realistic Multi-Layer Extruded 3D Text Effect */
        text-shadow: 
            0 1px 0 #93C5FD,
            0 2px 0 #60A5FA,
            0 3px 0 #3B82F6,
            0 4px 0 #2563EB,
            0 5px 0 #1D4ED8,
            0 6px 0 #1E40AF,
            0 7px 2px rgba(15, 23, 42, 0.45),
            0 9px 8px rgba(15, 23, 42, 0.35),
            0 14px 18px rgba(15, 23, 42, 0.25);
        transform: perspective(600px) translateZ(0);
        transition: transform 0.2s ease, text-shadow 0.2s ease;
    }
    .brand-title:hover {
        transform: perspective(600px) translateY(-2px);
        text-shadow: 
            0 1px 0 #BFDBFE,
            0 2px 0 #93C5FD,
            0 3px 0 #60A5FA,
            0 4px 0 #3B82F6,
            0 5px 0 #2563EB,
            0 6px 0 #1D4ED8,
            0 7px 0 #1E40AF,
            0 8px 3px rgba(15, 23, 42, 0.45),
            0 11px 10px rgba(15, 23, 42, 0.38),
            0 18px 22px rgba(15, 23, 42, 0.30);
    }
    .brand-subtitle {
        margin: 6px 0 0 0;
        font-size: 0.95rem;
        color: #BFDBFE;
        font-weight: 400;
    }
    .badge-container {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }
    .hero-badge {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(8px);
        color: #FFFFFF;
        border: 1px solid rgba(255, 255, 255, 0.25);
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* 3D Section Headings */
    .heading-3d {
        font-family: 'Righteous', 'Montserrat', sans-serif !important;
        font-size: 1.35rem;
        letter-spacing: 0.5px;
        color: #1E3A8A !important;
        text-shadow: 
            1px 1px 0 #DBEAFE,
            2px 2px 0 #BFDBFE,
            3px 3px 0 #93C5FD,
            4px 4px 3px rgba(30, 58, 138, 0.20);
    }

    /* Card Panels - Translucent Glassmorphism */
    .modern-card {
        background: rgba(255, 255, 255, 0.75) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(226, 232, 240, 0.85);
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
    }
    .modern-card:hover {
        background: rgba(255, 255, 255, 0.90) !important;
        border-color: #CBD5E1;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.08);
    }
    .card-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Tag and Badge styles */
    .category-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        background-color: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #BFDBFE;
        padding: 3px 10px;
        border-radius: 9999px;
        margin-top: 6px;
    }
    .confidence-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        background-color: #ECFDF5;
        color: #047857;
        border: 1px solid #A7F3D0;
        padding: 3px 10px;
        border-radius: 9999px;
        margin-left: 6px;
    }
    .fallback-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        background-color: #FEF2F2;
        color: #B91C1C;
        border: 1px solid #FECACA;
        padding: 3px 10px;
        border-radius: 9999px;
        margin-left: 6px;
    }
    .matched-prompt-hint {
        font-size: 0.82rem;
        color: #475569;
        margin-top: 6px;
        padding: 6px 10px;
        background: #F8FAFC;
        border-left: 3px solid #3B82F6;
        border-radius: 0 6px 6px 0;
    }

    /* Stat Box in Sidebar */
    .stat-box {
        background: rgba(255, 255, 255, 0.65) !important;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(226, 232, 240, 0.85);
        border-radius: 10px;
        padding: 12px;
        text-align: center;
    }
    .stat-number {
        font-size: 1.5rem;
        font-weight: 800;
        color: #1E40AF;
        line-height: 1.1;
    }
    .stat-label {
        font-size: 0.72rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
    }

    /* Highlight Key Value Rows */
    .info-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px dashed #E2E8F0;
        font-size: 0.88rem;
    }
    .info-row:last-child {
        border-bottom: none;
    }
    .info-label {
        color: #64748B;
        font-weight: 500;
    }
    .info-val {
        color: #0F172A;
        font-weight: 700;
    }

    /* Quick starter chips */
    .starter-header {
        font-size: 0.95rem;
        font-weight: 700;
        color: #334155;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Modern Footer */
    .app-footer {
        text-align: center;
        padding: 24px 0 12px 0;
        margin-top: 36px;
        border-top: 1px solid #E2E8F0;
        color: #64748B;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Dataset & Asset Paths
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATASET_PATH = os.path.join(BASE_DIR, "college_faq.csv")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
CAMPUS_MAIN_IMG = os.path.join(ASSETS_DIR, "campus_main.jpg")
LIBRARY_IMG = os.path.join(ASSETS_DIR, "library.jpg")
LAB_IMG = os.path.join(ASSETS_DIR, "computer_lab.jpg")
HOSTEL_IMG = os.path.join(ASSETS_DIR, "hostel.jpg")
SPORTS_IMG = os.path.join(ASSETS_DIR, "sports.jpg")
STUDENTS_HERO_IMG = os.path.join(ASSETS_DIR, "students_hero.jpg")
STUDENTS_GROUP_IMG = os.path.join(ASSETS_DIR, "students_group.jpg")

# ---------------------------------------------------------
# Chatbot Model Initialization
# ---------------------------------------------------------
@st.cache_resource
def get_initialized_chatbot(csv_path: str):
    """Loads dataset and prepares the chatbot instance."""
    df = load_faq_data(csv_path)
    bot = CollegeChatbot(faq_df=df, similarity_threshold=0.25)
    return bot, df

chatbot_ready = False
try:
    chatbot, faq_df = get_initialized_chatbot(DATASET_PATH)
    chatbot_ready = True
except DataLoaderError as e:
    st.error(f"⚠️ Dataset Initialization Error: {str(e)}")
    st.info("Please verify that 'college_faq.csv' exists in the project root with the correct columns.")
except Exception as e:
    st.error(f"⚠️ Unexpected Error loading chatbot: {str(e)}")

# ---------------------------------------------------------
# Session State Management
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "👋 Hello! Welcome to the **Apex Institute Campus Helpdesk & AI Enquiry Assistant**.\n\n"
                "I am here to help you explore verified information regarding **Admissions, Courses, "
                "Fee Schedules, Hostel Facilities, Placement Records, and Campus Contacts**.\n\n"
                "You can type your enquiry below or pick any quick topic from the **Interactive Campus Hub** on the right! 🎓"
            ),
            "meta": None
        }
    ]

# ---------------------------------------------------------
# Sidebar: College Identity & System Controls
# ---------------------------------------------------------
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    else:
        st.markdown("### 🎓 **Apex Engineering College**")
        st.caption("Accredited NAAC 'A+' | AICTE Approved")

    st.markdown("---")
    st.markdown("#### ⚙️ **Enquiry & Filter Controls**")

    selected_category = "All Categories"
    if chatbot_ready:
        categories = ["All Categories"] + get_categories(faq_df)
        selected_category = st.selectbox(
            "📂 Academic Category Filter:",
            categories,
            index=0,
            help="Constrain enquiry retrieval to a specific college department or topic."
        )

        threshold = st.slider(
            "🎯 Match Sensitivity Threshold:",
            min_value=0.10,
            max_value=0.80,
            value=0.25,
            step=0.05,
            help="Higher values require closer similarity to college FAQs. Lower values are more permissive."
        )
        chatbot.set_threshold(threshold)

        # Knowledge Base Overview Cards
        st.markdown("#### 📊 **Knowledge Base Overview**")
        c_stat1, c_stat2 = st.columns(2)
        with c_stat1:
            st.markdown(
                f"""
                <div class="stat-box">
                    <div class="stat-number">{len(faq_df)}</div>
                    <div class="stat-label">Verified FAQs</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c_stat2:
            st.markdown(
                f"""
                <div class="stat-box">
                    <div class="stat-number">{len(categories) - 1}</div>
                    <div class="stat-label">Disciplines</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.caption(f"Active Threshold: **{threshold:.2f}** | Engine: **TF-IDF + Cosine**")

    st.markdown("---")
    st.markdown("#### 🛠️ **Session Tools**")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🗑️ Reset Chat", use_container_width=True, help="Clear current conversation history"):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Conversation reset. How can I help you today?",
                    "meta": None
                }
            ]
            st.rerun()

    with col_btn2:
        transcript = "\n\n".join([
            f"{'Student' if m['role'] == 'user' else 'College Assistant'}: {m['content']}"
            for m in st.session_state.messages
        ])
        st.download_button(
            "📥 Export Chat",
            data=transcript,
            file_name="college_enquiry_transcript.txt",
            mime="text/plain",
            use_container_width=True,
            help="Download chat history as text"
        )

    st.markdown("---")
    st.markdown("#### 🏛️ **Campus Snapshot**")
    if os.path.exists(CAMPUS_MAIN_IMG):
        st.image(CAMPUS_MAIN_IMG, caption="Apex 50-Acre Green Campus Quad", use_container_width=True)

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size: 0.78rem; color: #64748B; line-height: 1.5;">
            <strong>Apex Institute of Technology</strong><br>
            Knowledge Campus, Sector 4, Education City<br>
            📞 Helpline: +91 98765 43210<br>
            ✉️ Email: admissions@demo-college.edu
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# Flagship College Brand Hero Section
# ---------------------------------------------------------
col_hero_brand, col_hero_visual = st.columns([1.65, 1.0], gap="large")

with col_hero_brand:
    st.markdown(
        """
        <div class="brand-hero">
            <div class="hero-top-brand">
                <div>
                    <div class="hero-inst-name">🏛️ APEX INSTITUTE OF TECHNOLOGY & SCIENCE</div>
                    <div class="hero-accred-text">Approved by AICTE • NAAC 'A+' Grade • Estd. 2005 • Affiliated to Tech University</div>
                </div>
                <div class="hero-live-indicator">
                    <span class="pulse-dot"></span> 24/7 AI Desk Online
                </div>
            </div>
            <div>
                <h1 class="brand-title">🎓 Apex College AI Campus Portal</h1>
                <div class="brand-subtitle">
                    Official Intelligent Student Enquiry & Admissions Helpdesk for <strong>B.Tech, M.Tech, MBA & MCA</strong>
                </div>
            </div>
            <div class="hero-brand-stats-row">
                <div class="hero-stat-item">
                    <div class="hero-stat-val">NAAC 'A+'</div>
                    <div class="hero-stat-desc">Accreditation</div>
                </div>
                <div class="hero-stat-item">
                    <div class="hero-stat-val">₹ 14.0 LPA</div>
                    <div class="hero-stat-desc">Highest CTC</div>
                </div>
                <div class="hero-stat-item">
                    <div class="hero-stat-val">5,000+</div>
                    <div class="hero-stat-desc">Enrolled Students</div>
                </div>
                <div class="hero-stat-item">
                    <div class="hero-stat-val">50+ Acres</div>
                    <div class="hero-stat-desc">Green Wi-Fi Campus</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_hero_visual:
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        if os.path.exists(STUDENTS_HERO_IMG):
            st.image(STUDENTS_HERO_IMG, caption="🎓 Academic Study & Peer Teams", use_container_width=True)
    with c_s2:
        if os.path.exists(STUDENTS_GROUP_IMG):
            st.image(STUDENTS_GROUP_IMG, caption="🎉 Student Community & Clubs", use_container_width=True)

    st.markdown(
        """
        <div class="modern-card" style="padding: 10px 14px; margin-top: 4px; display: flex; justify-content: space-between; align-items: center; background: rgba(255, 255, 255, 0.75);">
            <div style="font-size: 0.8rem; font-weight: 700; color: #1E40AF;">
                🌟 Admissions Open 2026-27
            </div>
            <div style="font-size: 0.72rem; color: #059669; font-weight: 700; background: #DCFCE7; padding: 2px 8px; border-radius: 9999px;">
                92% Placement Rate
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Two-Column Modern Layout: Chat on Left, Interactive Hub on Right
# ---------------------------------------------------------
col_chat, col_hub = st.columns([1.65, 1.0], gap="large")

# Track if user clicked any suggested button
clicked_query = None

# =========================================================
# Right Column: Interactive Campus Hub & Quick Access Panel
# =========================================================
with col_hub:
    tab_faqs, tab_gallery, tab_campus, tab_contacts, tab_logs = st.tabs([
        "💡 Quick Questions",
        "📸 Campus Gallery",
        "🏛️ Highlights",
        "📞 Helpdesk",
        "📊 Session Logs"
    ])

    with tab_faqs:
        st.markdown(
            """
            <div style="font-size:0.85rem; color:#475569; margin-bottom:12px;">
                Select any frequent inquiry below to ask the AI assistant immediately:
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption("🎓 **Admissions & Eligibility**")
        if st.button("📌 Eligibility criteria for B.Tech?", key="btn_q1", use_container_width=True):
            clicked_query = "What is the eligibility criteria for B.Tech admission?"
        if st.button("📌 How can I apply for admission?", key="btn_q2", use_container_width=True):
            clicked_query = "How can I apply for admission?"
        if st.button("📌 When does the admission process start?", key="btn_q3", use_container_width=True):
            clicked_query = "When does the admission process start?"

        st.caption("💰 **Fees & Financial Aid**")
        if st.button("📌 Annual tuition fee for B.Tech?", key="btn_q4", use_container_width=True):
            clicked_query = "What is the annual tuition fee for B.Tech?"
        if st.button("📌 Are scholarships available?", key="btn_q5", use_container_width=True):
            clicked_query = "Are scholarships available for students?"
        if st.button("📌 Is installment facility available?", key="btn_q6", use_container_width=True):
            clicked_query = "Is installment facility available for fee payment?"

        st.caption("🏢 **Hostel & Life**")
        if st.button("📌 Are hostel facilities available?", key="btn_q7", use_container_width=True):
            clicked_query = "Are hostel facilities available for boys and girls?"
        if st.button("📌 What is the hostel fee structure?", key="btn_q8", use_container_width=True):
            clicked_query = "What is the hostel fee structure?"

        st.caption("💼 **Placements & Library**")
        if st.button("📌 What companies visit for campus placement?", key="btn_q9", use_container_width=True):
            clicked_query = "What companies visit the college for campus recruitment?"
        if st.button("📌 Highest and average salary package?", key="btn_q10", use_container_width=True):
            clicked_query = "What was the highest and average salary package in recent placements?"
        if st.button("📌 Central library operating hours?", key="btn_q11", use_container_width=True):
            clicked_query = "What are the library timings and working hours?"

    with tab_gallery:
        st.markdown(
            """
            <div style="font-size:0.86rem; color:#475569; margin-bottom:12px;">
                Explore world-class academic and residential infrastructure across the Apex Campus:
            </div>
            """,
            unsafe_allow_html=True
        )
        if os.path.exists(STUDENTS_HERO_IMG):
            st.image(STUDENTS_HERO_IMG, caption="👥 Student Peer Study & Group Discussions", use_container_width=True)
        if os.path.exists(STUDENTS_GROUP_IMG):
            st.image(STUDENTS_GROUP_IMG, caption="🎉 Cultural, Sports & Student Technical Clubs", use_container_width=True)
        if os.path.exists(CAMPUS_MAIN_IMG):
            st.image(CAMPUS_MAIN_IMG, caption="🏛️ Main Academic Quad & Administrative Center", use_container_width=True)
        if os.path.exists(LAB_IMG):
            st.image(LAB_IMG, caption="🔬 Advanced AI, Computing & Robotics Research Lab", use_container_width=True)
        if os.path.exists(LIBRARY_IMG):
            st.image(LIBRARY_IMG, caption="📚 Central Digital Library & Quiet Research Pods", use_container_width=True)
        if os.path.exists(HOSTEL_IMG):
            st.image(HOSTEL_IMG, caption="🏢 Modern Student Hostels & Dining Hall", use_container_width=True)
        if os.path.exists(SPORTS_IMG):
            st.image(SPORTS_IMG, caption="⚽ Olympic-Grade Sports Arena & Athletic Complex", use_container_width=True)

    with tab_campus:
        if os.path.exists(CAMPUS_MAIN_IMG):
            st.image(CAMPUS_MAIN_IMG, caption="Apex Knowledge Campus (50+ Acres Green Infrastructure)", use_container_width=True)

        st.markdown(
            """
            <div class="modern-card">
                <div class="card-title">🏆 Institutional Ranking</div>
                <div class="info-row"><span class="info-label">Accreditation:</span><span class="info-val">NAAC 'A+' Grade</span></div>
                <div class="info-row"><span class="info-label">Approval:</span><span class="info-val">AICTE & UGC Recognized</span></div>
                <div class="info-row"><span class="info-label">Affiliation:</span><span class="info-val">State Technical University</span></div>
                <div class="info-row"><span class="info-label">Establishment:</span><span class="info-val">2005 (20+ Years Legacy)</span></div>
            </div>

            <div class="modern-card">
                <div class="card-title">💼 Placement Snapshot</div>
                <div class="info-row"><span class="info-label">Highest CTC:</span><span class="info-val" style="color:#059669;">₹ 14.0 LPA</span></div>
                <div class="info-row"><span class="info-label">Average CTC:</span><span class="info-val">₹ 4.8 LPA</span></div>
                <div class="info-row"><span class="info-label">Placement Rate:</span><span class="info-val">92% Eligible Batch</span></div>
                <div class="info-row"><span class="info-label">Top Recruiters:</span><span class="info-val">TCS, Infosys, Wipro, Cognizant</span></div>
            </div>

            <div class="modern-card">
                <div class="card-title">🌳 Campus Amenities</div>
                <div class="info-row"><span class="info-label">Campus Area:</span><span class="info-val">50+ Acres Green Campus</span></div>
                <div class="info-row"><span class="info-label">High-Speed Wi-Fi:</span><span class="info-val">24/7 Available</span></div>
                <div class="info-row"><span class="info-label">Hostels:</span><span class="info-val">Dedicated Boys & Girls Wings</span></div>
                <div class="info-row"><span class="info-label">Transport:</span><span class="info-val">Fleet across all city routes</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with tab_contacts:
        if os.path.exists(CAMPUS_MAIN_IMG):
            st.image(CAMPUS_MAIN_IMG, caption="Admissions Cell & Counseling Desk (Ground Floor, Block A)", use_container_width=True)

        st.markdown(
            """
            <div class="modern-card">
                <div class="card-title">📞 Admissions Desk</div>
                <p style="font-size:0.86rem; color:#475569; margin: 4px 0 10px 0;">Reach out directly to the counseling and admission team:</p>
                <div class="info-row"><span class="info-label">Helpline:</span><span class="info-val">+91 98765 43210</span></div>
                <div class="info-row"><span class="info-label">Landline:</span><span class="info-val">0123-456789</span></div>
                <div class="info-row"><span class="info-label">Email:</span><span class="info-val">admissions@demo-college.edu</span></div>
                <div class="info-row"><span class="info-label">Hours:</span><span class="info-val">Mon - Fri: 9 AM - 5 PM</span></div>
            </div>

            <div class="modern-card">
                <div class="card-title">📍 Campus Address</div>
                <div style="font-size:0.88rem; color:#334155; line-height:1.6;">
                    <strong>Apex Institute of Technology & Science</strong><br>
                    Knowledge Campus, Sector 4, Education City<br>
                    Pincode: 560001, Karnataka, India.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with tab_logs:
        if chatbot_ready:
            logs_df = chatbot.get_logs_df()
            if not logs_df.empty:
                st.dataframe(logs_df, use_container_width=True)
                st.caption("Logs include query length, timestamp, intent/category, and match confidence. No personal data is stored.")
            else:
                st.info("No queries processed yet in this session.")

# =========================================================
# Left Column: Conversation Stream & Message Box
# =========================================================
with col_chat:
    msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px;">
            <div class="heading-3d">
                💬 Student Consultation Stream
            </div>
            <div style="font-size:0.8rem; background:#F1F5F9; color:#475569; padding:3px 10px; border-radius:9999px; font-weight:600;">
                {msg_count} questions asked
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Render Conversation Messages
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="🧑‍🎓"):
                st.markdown(f"**{msg['content']}**")
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg["content"])
                if msg.get("meta"):
                    meta = msg["meta"]
                    status = meta.get("status")
                    cat = meta.get("category")
                    conf = meta.get("confidence", 0.0)
                    matched_q = meta.get("matched_question")

                    meta_html = ""
                    if cat and cat not in ["Greeting", "Gratitude", "Farewell"]:
                        meta_html += f'<span class="category-pill">📂 Category: {cat}</span> '
                    if status == "matched":
                        meta_html += f'<span class="confidence-pill">🎯 Match: {int(conf * 100)}%</span> '
                        if matched_q:
                            meta_html += f'<div class="matched-prompt-hint">💡 Matched Question: <em>"{matched_q}"</em></div>'
                    elif status == "fallback":
                        meta_html += f'<span class="fallback-pill">⚠️ Low Similarity ({int(conf * 100)}%) - Fallback Triggered</span>'
                    elif status in ["greeting", "gratitude", "farewell"]:
                        meta_html += f'<span class="confidence-pill">⚡ Instant {status.capitalize()}</span>'

                    if meta_html:
                        st.markdown(meta_html, unsafe_allow_html=True)

    # Visual Campus Highlights Showcase (Fills empty space with college photos)
    with st.expander("📸 **Virtual Campus Tour & Facilities Showcase (Click to View)**", expanded=(len(st.session_state.messages) <= 2)):
        c_p1, c_p2, c_p3 = st.columns(3)
        with c_p1:
            if os.path.exists(CAMPUS_MAIN_IMG):
                st.image(CAMPUS_MAIN_IMG, caption="🏛️ Academic Quad & Grounds", use_container_width=True)
            if os.path.exists(HOSTEL_IMG):
                st.image(HOSTEL_IMG, caption="🏢 Student Residence & Dining", use_container_width=True)
        with c_p2:
            if os.path.exists(LAB_IMG):
                st.image(LAB_IMG, caption="🔬 AI & Computing Research Lab", use_container_width=True)
            if os.path.exists(SPORTS_IMG):
                st.image(SPORTS_IMG, caption="⚽ Sports & Recreation Arena", use_container_width=True)
        with c_p3:
            if os.path.exists(LIBRARY_IMG):
                st.image(LIBRARY_IMG, caption="📚 Central Digital Library", use_container_width=True)
            st.markdown(
                """
                <div class="modern-card" style="padding:14px; margin-top:4px;">
                    <strong style="color:#1E3A8A; font-size:0.88rem;">🏛️ Apex Campus Amenities</strong>
                    <ul style="font-size:0.80rem; color:#475569; padding-left:16px; margin: 6px 0 0 0; line-height: 1.6;">
                        <li><strong>50+ Acres</strong> Lush Green Campus</li>
                        <li><strong>24/7 High-Speed</strong> Wi-Fi & Labs</li>
                        <li><strong>Smart Digital</strong> Classrooms</li>
                        <li><strong>50,000+</strong> Library Books & E-Journals</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Chat Input Box
    user_input = st.chat_input("Type your question here (e.g. 'What is the B.Tech fee?', 'Hostel rules', 'Placement packages')...")

# ---------------------------------------------------------
# Handle Query Processing
# ---------------------------------------------------------
active_query = clicked_query if clicked_query else user_input

if active_query and chatbot_ready:
    # 1. Append user question to history
    st.session_state.messages.append({
        "role": "user",
        "content": active_query,
        "meta": None
    })

    # 2. Get intelligent response from CollegeChatbot
    res = chatbot.get_response(active_query, category_filter=selected_category)

    # 3. Append bot response to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": res["answer"],
        "meta": res
    })

    # 4. Trigger UI update
    st.rerun()

# ---------------------------------------------------------
# Mini-Game: Apex Campus Trivia Challenge
# ---------------------------------------------------------
TRIVIA_QUESTIONS = [
    {
        "question": "💼 What was the highest campus placement package offered in recent placement drives?",
        "options": ["Rs. 8.5 LPA", "Rs. 14.0 LPA", "Rs. 24.0 LPA", "Rs. 4.8 LPA"],
        "answer": "Rs. 14.0 LPA",
        "fact": "The highest package reached Rs. 14 LPA, while the average package stood at approximately Rs. 4.8 LPA with 92% placement rate!"
    },
    {
        "question": "📚 What is the minimum mandatory attendance required to be eligible for university exams?",
        "options": ["60%", "75%", "85%", "50%"],
        "answer": "75%",
        "fact": "A minimum of 75% attendance in both lectures and practical lab sessions is mandatory."
    },
    {
        "question": "🏢 What is the weekday curfew timing for hostel residents?",
        "options": ["7:30 PM", "8:30 PM", "10:00 PM", "No Curfew"],
        "answer": "8:30 PM",
        "fact": "Students must return to the hostel by 8:30 PM on weekdays and 9:00 PM on weekends for safety."
    },
    {
        "question": "📖 How many books can an undergraduate student borrow at once from the Central Library?",
        "options": ["2 Books for 7 days", "4 Books for 14 days", "6 Books for 30 days", "Unlimited"],
        "answer": "4 Books for 14 days",
        "fact": "Undergraduate students can borrow up to 4 books for 14 days, while postgraduates can borrow up to 6 books."
    },
    {
        "question": "🏆 What is the institutional NAAC accreditation grade of Apex Institute?",
        "options": ["NAAC 'B' Grade", "NAAC 'A+' Grade", "Not Accredited", "Grade C"],
        "answer": "NAAC 'A+' Grade",
        "fact": "Apex Institute is proudly accredited with NAAC 'A+' Grade and approved by AICTE."
    }
]

# Session state initialization for game
if "game_q_idx" not in st.session_state:
    st.session_state.game_q_idx = 0
if "game_score" not in st.session_state:
    st.session_state.game_score = 0
if "game_answered" not in st.session_state:
    st.session_state.game_answered = False
if "game_selected" not in st.session_state:
    st.session_state.game_selected = None
if "game_finished" not in st.session_state:
    st.session_state.game_finished = False

st.markdown("---")
with st.container():
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; margin-bottom: 14px;">
            <div>
                <h3 class="heading-3d" style="margin: 0; display: flex; align-items: center; gap: 8px;">
                    🎮 Apex Campus Trivia Challenge
                </h3>
                <p style="margin: 4px 0 0 0; color: #64748B; font-size: 0.9rem;">
                    Test how well you know the campus rules, admissions, hostels, and placement facts!
                </p>
            </div>
            <div style="background: #EFF6FF; border: 1px solid #BFDBFE; color: #1D4ED8; font-weight: 700; font-size: 0.85rem; padding: 6px 14px; border-radius: 9999px;">
                Score: {score} / {total}
            </div>
        </div>
        """.format(score=st.session_state.game_score, total=len(TRIVIA_QUESTIONS)),
        unsafe_allow_html=True
    )

    total_q = len(TRIVIA_QUESTIONS)
    curr_idx = st.session_state.game_q_idx

    if st.session_state.game_finished:
        final_score = st.session_state.game_score
        if final_score == total_q:
            badge_icon, badge_title = "🏆", "Perfect Score! Official Campus Scholar 🎓"
            msg = "Incredible! You know Apex College inside out! You are 100% campus ready."
        elif final_score >= 3:
            badge_icon, badge_title = "🌟", "Campus Whiz! Well Done"
            msg = "Great performance! You know most of the essential college policies and facts."
        else:
            badge_icon, badge_title = "💡", "Good Effort! Fresh Explorer"
            msg = "Good try! Feel free to ask the AI Chatbot above to explore more about admissions, fees, and hostels."

        st.markdown(
            f"""
            <div class="modern-card" style="text-align: center; padding: 28px; background: linear-gradient(135deg, rgba(239, 246, 255, 0.9) 0%, rgba(255, 255, 255, 0.9) 100%); border: 2px solid #3B82F6;">
                <div style="font-size: 2.8rem; margin-bottom: 8px;">{badge_icon}</div>
                <h3 style="margin: 0; color: #1E3A8A;">{badge_title}</h3>
                <p style="color: #475569; font-size: 1.05rem; margin: 10px 0 18px 0;">
                    You scored <strong>{final_score}</strong> out of <strong>{total_q}</strong>!
                </p>
                <p style="color: #64748B; font-size: 0.9rem; max-width: 600px; margin: 0 auto 16px auto;">
                    {msg}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        col_r1, col_r2, col_r3 = st.columns([1, 1.2, 1])
        with col_r2:
            if st.button("🔄 Play Trivia Again", use_container_width=True):
                st.session_state.game_q_idx = 0
                st.session_state.game_score = 0
                st.session_state.game_answered = False
                st.session_state.game_selected = None
                st.session_state.game_finished = False
                st.rerun()

    else:
        q_data = TRIVIA_QUESTIONS[curr_idx]
        progress_val = curr_idx / total_q
        st.progress(progress_val, text=f"Question {curr_idx + 1} of {total_q}")

        st.markdown(
            f"""
            <div class="modern-card" style="margin-top: 10px; margin-bottom: 14px;">
                <div style="font-size: 1.08rem; font-weight: 700; color: #0F172A; line-height: 1.5;">
                    {q_data["question"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Render 4 options in a 2x2 grid
        col_o1, col_o2 = st.columns(2)
        opts = q_data["options"]

        for i, opt in enumerate(opts):
            target_col = col_o1 if i % 2 == 0 else col_o2
            with target_col:
                is_disabled = st.session_state.game_answered
                if st.button(
                    opt,
                    key=f"opt_btn_{curr_idx}_{i}",
                    use_container_width=True,
                    disabled=is_disabled
                ):
                    st.session_state.game_answered = True
                    st.session_state.game_selected = opt
                    if opt == q_data["answer"]:
                        st.session_state.game_score += 1
                        st.balloons()
                    st.rerun()

        # Display answer feedback if answered
        if st.session_state.game_answered:
            user_choice = st.session_state.game_selected
            correct_ans = q_data["answer"]

            if user_choice == correct_ans:
                st.success(f"🎉 **Correct!** Great job! {q_data['fact']}")
            else:
                st.error(f"❌ **Not quite!** You picked *{user_choice}*. The correct answer is **{correct_ans}**.\n\n💡 *{q_data['fact']}*")

            # Next Question / Finish Button
            col_n1, col_n2, col_n3 = st.columns([1, 1.2, 1])
            with col_n2:
                btn_label = "🏆 View Final Score" if curr_idx == total_q - 1 else "➡️ Next Question"
                if st.button(btn_label, use_container_width=True, type="primary"):
                    if curr_idx < total_q - 1:
                        st.session_state.game_q_idx += 1
                        st.session_state.game_answered = False
                        st.session_state.game_selected = None
                    else:
                        st.session_state.game_finished = True
                        if st.session_state.game_score >= 4:
                            st.balloons()
                    st.rerun()

# ---------------------------------------------------------
# Modern Footer
# ---------------------------------------------------------
st.markdown(
    """
    <div class="app-footer">
        <strong>Apex Institute AI-Based College Enquiry Chatbot</strong> • Streamlit Modern Interface<br>
        Engineered with Natural Language Processing (TF-IDF & Cosine Similarity) • Safe Academic Demonstration Data
    </div>
    """,
    unsafe_allow_html=True
)
