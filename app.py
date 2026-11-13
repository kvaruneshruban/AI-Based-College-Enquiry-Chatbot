"""
AI-Based College Enquiry Chatbot - Streamlit User Interface.

A modern, responsive, and intuitive web interface designed with an executive
blue-and-white theme, two-column interactive layout, quick FAQ shortcuts,
real-time NLP match diagnostics, typo-resilience, voice assistant capabilities,
admission lead capture, and an administrative desk portal.
"""

import os
import json
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from data_loader import (
    load_faq_data,
    get_categories,
    DataLoaderError,
    add_faq_entry,
    delete_faq_entry
)
from chatbot import CollegeChatbot
from lead_manager import (
    save_admission_lead,
    get_leads_df,
    update_lead_status,
    log_feedback,
    get_feedback_df,
    get_unanswered_df,
    resolve_unanswered_query,
    get_analytics_summary
)
from generate_prospectus import create_prospectus, PROSPECTUS_PATH

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
    .brand-subtitle {
        color: #E2E8F0;
        font-size: 1.02rem;
        margin-top: 6px;
        font-weight: 400;
    }

    /* Cards & Containers */
    .modern-card {
        background: rgba(255, 255, 255, 0.88);
        border: 1px solid rgba(226, 232, 240, 0.9);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 14px -2px rgba(0, 0, 0, 0.05);
        backdrop-filter: blur(10px);
    }
    .card-title {
        font-size: 1.02rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Diagnostics Pills */
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
    .fuzzy-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        background-color: #FEF3C7;
        color: #92400E;
        border: 1px solid #FDE68A;
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

# Ensure Official Prospectus PDF exists
if not os.path.exists(PROSPECTUS_PATH):
    try:
        create_prospectus()
    except Exception:
        pass

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
                "💡 **New Features:**\n"
                "- 🔤 **Typo-tolerant Search**: Even if you misspell words like 'admision' or 'scolorship', I'll find the right answer!\n"
                "- 🎙️ **Voice Query & Read Aloud**: Speak your questions or listen to audio responses.\n"
                "- 📝 **Direct Admission Leads**: Use the **Apply / Callback** tab on the right to connect with our counseling desk.\n"
                "- 📄 **Download Official Prospectus**: Get the complete 2026-27 brochure from the sidebar."
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

        st.caption(f"Active Threshold: **{threshold:.2f}** | Engine: **TF-IDF + Fuzzy NLP**")

    st.markdown("---")
    st.markdown("#### 📄 **Official Prospectus**")
    if os.path.exists(PROSPECTUS_PATH):
        with open(PROSPECTUS_PATH, "rb") as f_pdf:
            pdf_bytes = f_pdf.read()
        st.download_button(
            "📥 Download 2026-27 Prospectus (PDF)",
            data=pdf_bytes,
            file_name="Apex_College_Prospectus_2026.pdf",
            mime="application/pdf",
            use_container_width=True,
            help="Download comprehensive courses, fee structure, hostel rules, and placement report"
        )

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
            <strong>Apex Institute of Technology & Science</strong><br>
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

clicked_query = None

# =========================================================
# Right Column: Interactive Campus Hub & Management Center
# =========================================================
with col_hub:
    tab_faqs, tab_leads, tab_admin, tab_gallery, tab_campus, tab_contacts, tab_logs = st.tabs([
        "💡 FAQs",
        "📝 Apply",
        "🔐 Staff Desk",
        "📸 Gallery",
        "🏛️ Highlights",
        "📞 Helpdesk",
        "📊 Logs"
    ])

    # 1. Quick Questions Tab
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

    # 2. Admission Lead Capture Form
    with tab_leads:
        st.markdown(
            """
            <div class="card-title">📝 Apply Online / Request Counselor Callback</div>
            <div style="font-size:0.83rem; color:#475569; margin-bottom:12px;">
                Fill out this quick form. Our admissions officer will contact you within 24 hours with cutoff counseling & fee guidance.
            </div>
            """,
            unsafe_allow_html=True
        )
        with st.form("lead_form", clear_on_submit=True):
            lead_name = st.text_input("Full Name *", placeholder="e.g. Anand Kumar")
            lead_phone = st.text_input("Mobile / WhatsApp Number *", placeholder="e.g. 9876543210")
            lead_email = st.text_input("Email Address", placeholder="e.g. anand@example.com")
            lead_course = st.selectbox("Program of Interest *", [
                "B.Tech Computer Science & Engineering",
                "B.Tech Artificial Intelligence & Data Science",
                "B.Tech Electronics & Communication",
                "B.Tech Mechanical Engineering",
                "M.Tech Computer Science",
                "Master of Business Administration (MBA)",
                "Master of Computer Applications (MCA)"
            ])
            lead_cutoff = st.text_input("12th / Diploma Cutoff Marks", placeholder="e.g. 185 / 200 or 86%")
            lead_msg = st.text_area("Specific Question / Preferences", placeholder="e.g. Hostel accommodation and sports quota inquiry...")

            lead_submitted = st.form_submit_button("🚀 Submit Admission Enquiry", use_container_width=True, type="primary")
            if lead_submitted:
                lead_res = save_admission_lead(
                    name=lead_name,
                    email=lead_email,
                    phone=lead_phone,
                    course=lead_course,
                    cutoff=lead_cutoff,
                    message=lead_msg
                )
                if lead_res["status"] == "success":
                    st.success(f"🎉 **{lead_res['message']}**\n\nApplication Reference: **`{lead_res['ref_no']}`**")
                    st.balloons()
                else:
                    st.error(f"⚠️ {lead_res['message']}")

    # 3. Staff & Admin Portal (PIN: admin123)
    with tab_admin:
        st.markdown(
            """
            <div class="card-title">🔐 Admissions Staff Desk</div>
            <div style="font-size:0.83rem; color:#475569; margin-bottom:10px;">
                Access leads, identify unanswered student queries, and manage the live FAQ knowledge base.
            </div>
            """,
            unsafe_allow_html=True
        )
        admin_pin = st.text_input("Staff Security PIN:", type="password", key="admin_pin_input", help="Demo access: admin123")
        if admin_pin == "admin123":
            st.success("🔓 Authenticated as Campus Helpdesk Officer")
            
            desk_analytics, desk_leads, desk_unanswered, desk_crud = st.tabs([
                "📊 Overview", "📋 Leads", "❓ Unanswered", "📚 FAQ CRUD"
            ])

            with desk_analytics:
                analytics_data = get_analytics_summary()
                m_c1, m_c2 = st.columns(2)
                with m_c1:
                    st.metric("Total Leads", analytics_data["total_leads"])
                    st.metric("Unresolved Questions", analytics_data["unresolved_queries"])
                with m_c2:
                    st.metric("Pending Leads", analytics_data["pending_leads"])
                    st.metric("Satisfaction Rate", f"{analytics_data['satisfaction_rate']}%")

            with desk_leads:
                all_leads_df = get_leads_df()
                if not all_leads_df.empty:
                    st.dataframe(all_leads_df, use_container_width=True)
                    csv_bytes = all_leads_df.to_csv(index=False).encode("utf-8")
                    st.download_button("📥 Export Leads CSV", csv_bytes, "admission_leads.csv", "text/csv", use_container_width=True)

                    st.markdown("##### ✏️ Update Lead Status")
                    u_col1, u_col2 = st.columns([1.5, 1])
                    with u_col1:
                        target_ref = st.selectbox("Select Ref No:", all_leads_df["ref_no"].tolist())
                    with u_col2:
                        target_stat = st.selectbox("New Status:", ["Pending", "Contacted", "Counseling Scheduled", "Enrolled", "Closed"])
                    if st.button("Update Status", use_container_width=True):
                        update_lead_status(target_ref, target_stat)
                        st.success(f"Status for {target_ref} updated to {target_stat}")
                        st.rerun()
                else:
                    st.info("No admission leads registered yet.")

            with desk_unanswered:
                unans_df = get_unanswered_df()
                if not unans_df.empty:
                    st.dataframe(unans_df, use_container_width=True)
                    st.caption("These queries triggered a fallback response. Add them to the Knowledge Base below to improve bot coverage.")
                else:
                    st.info("No unanswered questions logged yet. High accuracy!")

            with desk_crud:
                st.markdown("##### ➕ Add New FAQ to Knowledge Base")
                with st.form("crud_add_form"):
                    crud_cat = st.selectbox("Category:", categories[1:] + ["General enquiries"])
                    crud_q = st.text_input("Student Question:")
                    crud_a = st.text_area("Verified Official Answer:")
                    crud_btn = st.form_submit_button("Add to Knowledge Base", type="primary")
                    if crud_btn:
                        try:
                            add_faq_entry(DATASET_PATH, crud_cat, crud_q, crud_a)
                            st.cache_resource.clear()
                            resolve_unanswered_query(crud_q)
                            st.success("New FAQ added successfully! Chatbot re-indexed.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

                st.markdown("##### 🗑️ Remove Outdated FAQ")
                q_list = faq_df["question"].tolist()
                del_target = st.selectbox("Select FAQ to Remove:", q_list)
                if st.button("🗑️ Confirm Delete FAQ", type="secondary"):
                    try:
                        delete_faq_entry(DATASET_PATH, del_target)
                        st.cache_resource.clear()
                        st.success("FAQ deleted successfully! Chatbot re-indexed.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

        elif admin_pin:
            st.error("Incorrect PIN. Please use demo PIN: admin123")
        else:
            st.info("Enter Administrator PIN (Default: `admin123`) to access leads, logs, and FAQ manager.")

    # 4. Campus Gallery Tab
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

    # 5. Highlights Tab
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

    # 6. Helpdesk Tab
    with tab_contacts:
        if os.path.exists(CAMPUS_MAIN_IMG):
            st.image(CAMPUS_MAIN_IMG, caption="Admissions Cell & Counseling Desk (Block A)", use_container_width=True)

        st.markdown(
            """
            <div class="modern-card">
                <div class="card-title">📞 Admissions Desk</div>
                <p style="font-size:0.86rem; color:#475569; margin: 4px 0 10px 0;">Reach out directly to the counseling team:</p>
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

    # 7. Session Logs Tab
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
            <div class="card-title" style="margin:0;">
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
    last_user_query = ""
    for idx, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            last_user_query = msg["content"]
            with st.chat_message("user", avatar="🧑‍🎓"):
                st.markdown(f"**{msg['content']}**")
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg["content"])
                
                # Diagnostics & Metadata
                if msg.get("meta"):
                    meta = msg["meta"]
                    status = meta.get("status")
                    cat = meta.get("category")
                    conf = meta.get("confidence", 0.0)
                    matched_q = meta.get("matched_question")
                    is_fuzzy = meta.get("is_fuzzy", False)

                    meta_html = ""
                    if cat and cat not in ["Greeting", "Gratitude", "Farewell"]:
                        meta_html += f'<span class="category-pill">📂 Category: {cat}</span> '
                    if status == "matched":
                        meta_html += f'<span class="confidence-pill">🎯 Match: {int(conf * 100)}%</span> '
                        if is_fuzzy:
                            meta_html += '<span class="fuzzy-pill">⚡ Auto-Corrected / Typo Resilient</span> '
                        if matched_q:
                            meta_html += f'<div class="matched-prompt-hint">💡 Matched FAQ: <em>"{matched_q}"</em></div>'
                    elif status == "fallback":
                        meta_html += f'<span class="fallback-pill">⚠️ Low Similarity ({int(conf * 100)}%) - Fallback Triggered</span>'
                    elif status in ["greeting", "gratitude", "farewell"]:
                        meta_html += f'<span class="confidence-pill">⚡ Instant {status.capitalize()}</span>'

                    if meta_html:
                        st.markdown(meta_html, unsafe_allow_html=True)

                # Action Bar: Audio Read Aloud & Student Feedback Rating
                if idx > 0 and msg["content"]:
                    clean_text_for_js = json.dumps(msg["content"].replace("[DEMO DATA]", "").strip())
                    
                    c_act1, c_act2, c_act3, c_act4 = st.columns([1.8, 1, 1, 5])
                    with c_act1:
                        # Native Browser Text-to-Speech
                        components.html(f"""
                        <button onclick="window.speechSynthesis.cancel(); const u = new SpeechSynthesisUtterance({clean_text_for_js}); u.rate=1.0; window.speechSynthesis.speak(u);"
                                style="background:#EFF6FF; border:1px solid #BFDBFE; color:#1D4ED8; font-size:11px; font-weight:600; padding:4px 8px; border-radius:6px; cursor:pointer;">
                            🔊 Listen
                        </button>
                        """, height=30)
                    with c_act2:
                        if st.button("👍", key=f"fb_up_{idx}", help="Helpful response"):
                            log_feedback(query=last_user_query, answer=msg["content"], rating="positive")
                            st.toast("Thank you for your feedback! 👍")
                    with c_act3:
                        if st.button("👎", key=f"fb_down_{idx}", help="Needs improvement"):
                            log_feedback(query=last_user_query, answer=msg["content"], rating="negative")
                            st.toast("Feedback noted! Our counseling desk will review this. 👎")

    # Campus Highlights Expander
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

    # Voice Assistant Speech-to-Text Bar
    components.html("""
    <script>
    function startVoiceInput() {
        var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert("Speech recognition is supported in Google Chrome, Edge, and modern browsers.");
            return;
        }
        var recognition = new SpeechRecognition();
        recognition.lang = 'en-IN';
        recognition.interimResults = false;
        var statusEl = document.getElementById('voice-status');
        statusEl.innerText = "🎙️ Listening... Speak your question now!";
        recognition.start();

        recognition.onresult = function(event) {
            var transcript = event.results[0][0].transcript;
            statusEl.innerText = "✅ Transcribed: '" + transcript + "' (Please paste or type into chat input below)";
            navigator.clipboard.writeText(transcript);
        };
        recognition.onerror = function(event) {
            statusEl.innerText = "❌ Mic: " + event.error + ". Click again to retry.";
        };
    }
    </script>
    <div style="display:flex; align-items:center; gap:10px; font-family:'Plus Jakarta Sans', sans-serif; background:#F8FAFC; padding:6px 12px; border-radius:10px; border:1px solid #E2E8F0; margin-bottom:4px;">
        <button onclick="startVoiceInput()" style="background:#2563EB; color:#FFFFFF; border:none; padding:5px 12px; border-radius:6px; cursor:pointer; font-weight:600; font-size:12px;">
            🎙️ Speak Enquiry
        </button>
        <span id="voice-status" style="font-size:11.5px; color:#64748B;">Click to speak into microphone (Auto-copies to clipboard)</span>
    </div>
    """, height=44)

    # Chat Input Box
    user_input = st.chat_input("Type or paste your question (e.g. 'B.Tech fees', 'hostal rules', 'scholarship eligibility', 'placement stats')...")

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
                <h3 class="card-title" style="margin: 0; font-size: 1.2rem;">
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

        if st.session_state.game_answered:
            user_choice = st.session_state.game_selected
            correct_ans = q_data["answer"]

            if user_choice == correct_ans:
                st.success(f"🎉 **Correct!** Great job! {q_data['fact']}")
            else:
                st.error(f"❌ **Not quite!** You picked *{user_choice}*. The correct answer is **{correct_ans}**.\n\n💡 *{q_data['fact']}*")

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
        Engineered with Natural Language Processing (TF-IDF & Fuzzy Typo Tolerance) • Safe Academic Demonstration Data
    </div>
    """,
    unsafe_allow_html=True
)
