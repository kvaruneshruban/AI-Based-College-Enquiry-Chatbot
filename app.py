"""
AI-Based College Enquiry Chatbot - Streamlit User Interface.

A modern, responsive, ChatGPT-like conversational web interface designed with an executive
blue-and-white theme, two-column interactive layout, quick FAQ shortcuts,
real-time NLP match diagnostics, typo-resilience, multi-turn conversational context,
voice assistant capabilities, admission lead capture, and an administrative desk portal.
"""

import os
import json
import uuid
import base64
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
    save_admission_application,
    get_applications_df,
    get_leads_df,
    update_lead_status,
    log_feedback,
    get_feedback_df,
    get_unanswered_df,
    resolve_unanswered_query,
    get_analytics_summary
)
from application_form import render_admission_application_form
from generate_prospectus import create_prospectus, PROSPECTUS_PATH
from ai_agent import get_api_key, is_ai_available
from image_manager import get_all_interactive_cards, get_contextual_chips
from chat_history_manager import (
    init_db,
    get_connection,
    create_conversation,
    get_conversation,
    save_message,
    get_conversation_messages,
    list_conversations,
    delete_conversation,
    add_recent_search,
    get_recent_searches,
    generate_conversation_title
)

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="VRBot | VR College of Engineering Enquiry Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Dataset & Asset Paths (Loaded early for CSS Assets)
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATASET_PATH = os.path.join(BASE_DIR, "college_faq.csv")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
CAMPUS_BG_IMG = os.path.join(ASSETS_DIR, "campus_bg.png")
if not os.path.exists(CAMPUS_BG_IMG):
    CAMPUS_BG_IMG = os.path.join(ASSETS_DIR, "campus_uploaded_raw.png")
CAMPUS_MAIN_IMG = os.path.join(ASSETS_DIR, "campus_main.jpg")
LIBRARY_IMG = os.path.join(ASSETS_DIR, "library.jpg")
LAB_IMG = os.path.join(ASSETS_DIR, "computer_lab.jpg")
HOSTEL_IMG = os.path.join(ASSETS_DIR, "hostel.jpg")
SPORTS_IMG = os.path.join(ASSETS_DIR, "sports.jpg")
STUDENTS_HERO_IMG = os.path.join(ASSETS_DIR, "students_hero.jpg")
STUDENTS_GROUP_IMG = os.path.join(ASSETS_DIR, "students_group.jpg")

# Load Uploaded Campus Background
campus_bg_b64 = ""
if os.path.exists(CAMPUS_BG_IMG):
    try:
        with open(CAMPUS_BG_IMG, "rb") as f_img:
            campus_bg_b64 = base64.b64encode(f_img.read()).decode("utf-8")
    except Exception:
        pass

# Ensure Official Prospectus PDF exists
if not os.path.exists(PROSPECTUS_PATH):
    try:
        create_prospectus()
    except Exception:
        pass

# ---------------------------------------------------------
# Modern CSS Stylesheet (Orély University Campus Aesthetic & Chat UX)
# ---------------------------------------------------------
MAIN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=Righteous&family=Montserrat:wght@700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* 1. Base App Viewport with Illustrated Campus Background */
    .stApp {
        background-color: #0E7490 !important;
        background-image: 
            linear-gradient(180deg, rgba(255, 255, 255, 0.40) 0%, rgba(240, 253, 250, 0.55) 50%, rgba(224, 242, 254, 0.65) 100%),
            url('data:image/png;base64,__CAMPUS_BG_B64__') !important;
        background-size: cover !important;
        background-position: center top !important;
        background-attachment: fixed !important;
        background-repeat: no-repeat !important;
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"] {
        background-color: transparent !important;
        background: transparent !important;
    }

    /* 2. Glassmorphic Left Sidebar (Clean White & Light Teal) */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.97) 0%, rgba(240, 253, 250, 0.95) 50%, rgba(224, 242, 254, 0.96) 100%) !important;
        border-right: 1.5px solid rgba(204, 251, 241, 0.85) !important;
        box-shadow: 4px 0 24px rgba(15, 118, 110, 0.08) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
    }

    [data-testid="stSidebarContent"] {
        background: transparent !important;
    }

    /* Top Navigation Bar */
    .top-nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(255, 255, 255, 0.94);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1.5px solid rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 8px 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 16px rgba(15, 118, 110, 0.08);
        gap: 12px;
    }
    .top-nav-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .top-nav-logo-wrap {
        width: 38px;
        height: 38px;
        background: linear-gradient(135deg, #0D9488 0%, #06B6D4 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 8px rgba(13, 148, 136, 0.3);
    }
    .top-nav-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.95rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        line-height: 1.2;
    }
    .top-nav-subtitle {
        font-size: 0.72rem;
        color: #0F766E;
        font-weight: 600;
    }
    .user-profile-badge {
        display: flex;
        align-items: center;
        gap: 8px;
        background: #F0FDFA;
        border: 1.2px solid #99F6E4;
        padding: 5px 12px;
        border-radius: 9999px;
        box-shadow: 0 2px 6px rgba(13, 148, 136, 0.06);
        white-space: nowrap;
    }
    .profile-avatar {
        font-size: 1.15rem;
    }
    .profile-name {
        font-size: 0.78rem;
        font-weight: 700;
        color: #0F766E;
        line-height: 1.1;
    }
    .profile-status {
        font-size: 0.68rem;
        color: #047857;
        display: flex;
        align-items: center;
        gap: 4px;
        font-weight: 600;
    }
    .pulse-emerald-dot {
        width: 7px;
        height: 7px;
        background: #10B981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 6px #10B981;
        animation: pulseEmerald 2s infinite;
    }
    @keyframes pulseEmerald {
        0% { transform: scale(0.9); opacity: 0.7; }
        50% { transform: scale(1.2); opacity: 1; }
        100% { transform: scale(0.9); opacity: 0.7; }
    }

    /* 3. Welcome Campus Hero Banner with Mascot (Orély Theme) */
    .campus-welcome-hero {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.94) 0%, rgba(15, 118, 110, 0.90) 45%, rgba(13, 148, 136, 0.86) 80%, rgba(6, 182, 212, 0.82) 100%);
        padding: 24px 28px;
        border-radius: 20px;
        color: #FFFFFF;
        margin-bottom: 16px;
        box-shadow: 0 14px 32px -4px rgba(15, 118, 110, 0.35);
        border: 1.5px solid rgba(255, 255, 255, 0.24);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 20px;
        flex-wrap: wrap;
    }
    .hero-left-content {
        flex: 1 1 580px;
    }
    .hero-college-badge {
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        color: #5EEAD4;
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 6px;
    }
    .hero-portal-heading {
        font-family: 'Righteous', 'Montserrat', sans-serif;
        font-size: 2.15rem;
        font-weight: 900;
        margin: 0 0 8px 0;
        letter-spacing: 0.6px;
        color: #FFFFFF !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.35);
    }
    .hero-portal-subtext {
        font-size: 0.94rem;
        color: #E2E8F0;
        line-height: 1.5;
        margin: 0 0 16px 0;
        max-width: 780px;
    }
    .hero-stats-deck {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
    }
    .hero-stat-pill {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 12px;
        padding: 6px 12px;
    }
    .hero-stat-pill.highlight-gold {
        background: rgba(245, 158, 11, 0.25);
        border-color: rgba(251, 191, 36, 0.55);
    }
    .pill-icon {
        font-size: 1.15rem;
    }
    .pill-num {
        font-size: 0.95rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.1;
    }
    .pill-lbl {
        font-size: 0.64rem;
        color: #A5F3FC;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.4px;
    }
    .highlight-gold .pill-lbl {
        color: #FEF08A;
    }
    .hero-mascot-container {
        flex-shrink: 0;
    }
    .mascot-card-outer {
        background: rgba(255, 255, 255, 0.14);
        border: 1.5px solid rgba(255, 255, 255, 0.32);
        border-radius: 18px;
        padding: 14px 18px;
        text-align: center;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        min-width: 155px;
    }
    .mascot-icon-display {
        font-size: 2.6rem;
        filter: drop-shadow(0 4px 10px rgba(0, 0, 0, 0.25));
        margin-bottom: 4px;
        animation: floatMascot 3s ease-in-out infinite alternate;
    }
    @keyframes floatMascot {
        0% { transform: translateY(0px); }
        100% { transform: translateY(-5px); }
    }
    .mascot-badge-name {
        font-size: 0.92rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: 0.4px;
    }
    .mascot-badge-role {
        font-size: 0.70rem;
        color: #67E8F9;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .mascot-live-indicator {
        background: rgba(16, 185, 129, 0.25);
        color: #A7F3D0;
        border: 1px solid rgba(52, 211, 153, 0.45);
        border-radius: 9999px;
        font-size: 0.66rem;
        font-weight: 700;
        padding: 2px 8px;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }

    /* 4. Quick Access Section */
    .section-label-chip {
        font-size: 0.82rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #0F766E;
        margin: 6px 0 8px 0;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .quick-access-btn button {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 1.5px solid #CCFBF1 !important;
        border-top: 3.5px solid #0D9488 !important;
        border-radius: 14px !important;
        padding: 10px 6px !important;
        color: #0F172A !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        box-shadow: 0 4px 14px rgba(15, 118, 110, 0.08) !important;
        transition: all 0.22s ease !important;
        text-align: center !important;
        height: 62px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
    }
    .quick-access-btn button:hover {
        background: #FFFFFF !important;
        border-color: #2DD4BF !important;
        border-top-color: #0F766E !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 22px rgba(13, 148, 136, 0.22) !important;
        color: #0F766E !important;
    }

    /* 5. Modern Cards & Containers */
    .modern-card {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid rgba(204, 251, 241, 0.9);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 14px -2px rgba(15, 118, 110, 0.06);
        backdrop-filter: blur(10px);
    }
    .card-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: #0F766E;
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
        font-size: 0.74rem;
        font-weight: 600;
        background-color: #F0FDFA;
        color: #0F766E;
        border: 1px solid #99F6E4;
        padding: 2px 8px;
        border-radius: 9999px;
    }
    .confidence-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.74rem;
        font-weight: 600;
        background-color: #ECFDF5;
        color: #047857;
        border: 1px solid #A7F3D0;
        padding: 2px 8px;
        border-radius: 9999px;
        margin-left: 4px;
    }
    .ai-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.74rem;
        font-weight: 700;
        background: linear-gradient(135deg, #F0FDFA 0%, #E0F2FE 100%);
        color: #0284C7;
        border: 1px solid #BAE6FD;
        padding: 2px 8px;
        border-radius: 9999px;
        margin-left: 4px;
    }
    .fuzzy-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.74rem;
        font-weight: 600;
        background-color: #FEF3C7;
        color: #92400E;
        border: 1px solid #FDE68A;
        padding: 2px 8px;
        border-radius: 9999px;
        margin-left: 4px;
    }
    .fallback-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.74rem;
        font-weight: 600;
        background-color: #FEF2F2;
        color: #B91C1C;
        border: 1px solid #FECACA;
        padding: 2px 8px;
        border-radius: 9999px;
        margin-left: 4px;
    }
    .matched-prompt-hint {
        font-size: 0.80rem;
        color: #475569;
        margin-top: 6px;
        padding: 5px 10px;
        background: #F8FAFC;
        border-left: 3px solid #0D9488;
        border-radius: 0 6px 6px 0;
    }

    /* Stat Box in Sidebar */
    .stat-box {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(204, 251, 241, 0.95);
        border-radius: 10px;
        padding: 12px;
        text-align: center;
    }
    .stat-number {
        font-size: 1.5rem;
        font-weight: 800;
        color: #0F766E;
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
        border-top: 1px solid rgba(204, 251, 241, 0.8);
        color: #475569;
        font-size: 0.85rem;
    }

    /* Sidebar College Branding Card */
    .sidebar-brand-card {
        background: linear-gradient(145deg, #FFFFFF 0%, #F0FDFA 100%);
        border: 1px solid rgba(204, 251, 241, 0.95);
        border-radius: 16px;
        padding: 16px 14px 14px 14px;
        box-shadow: 0 4px 16px -2px rgba(15, 118, 110, 0.08), 0 2px 6px -1px rgba(0, 0, 0, 0.04);
        margin-bottom: 18px;
        margin-top: -6px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .sidebar-brand-card:hover {
        box-shadow: 0 8px 24px -4px rgba(15, 118, 110, 0.14);
        border-color: #5EEAD4;
    }
    .sidebar-brand-content {
        display: flex;
        align-items: center;
        gap: 13px;
    }
    .sidebar-logo-frame {
        flex-shrink: 0;
        width: 72px;
        height: 72px;
        background: linear-gradient(135deg, #F0FDFA 0%, #CCFBF1 100%);
        border-radius: 16px;
        border: 2px solid #5EEAD4;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 5px;
        box-shadow: 0 4px 10px rgba(15, 118, 110, 0.12);
    }
    .sidebar-logo-img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        border-radius: 10px;
        display: block;
    }
    .sidebar-text-col {
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-width: 0;
        flex: 1;
    }
    .sidebar-brand-title {
        font-family: 'Montserrat', 'Plus Jakarta Sans', sans-serif;
        font-size: 1.12rem;
        font-weight: 900;
        color: #0F766E;
        letter-spacing: 0.6px;
        line-height: 1.22;
        margin: 0 0 6px 0;
        text-transform: uppercase;
        word-break: normal;
        overflow-wrap: break-word;
    }
    .sidebar-badges-row {
        display: flex;
        align-items: center;
        gap: 6px;
        flex-wrap: wrap;
        margin-bottom: 4px;
    }
    .sidebar-badge-aicte {
        background: #F0FDFA;
        color: #0F766E;
        border: 1px solid #99F6E4;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 6px;
        white-space: nowrap;
        letter-spacing: 0.2px;
    }
    .sidebar-badge-estd {
        background: #FEF3C7;
        color: #92400E;
        border: 1px solid #FDE68A;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 6px;
        white-space: nowrap;
        letter-spacing: 0.2px;
    }
    .sidebar-sub-accred {
        font-size: 0.70rem;
        color: #475569;
        font-weight: 600;
        letter-spacing: 0.2px;
    }
    .sidebar-brand-divider {
        height: 2px;
        background: linear-gradient(90deg, #0D9488 0%, #5EEAD4 60%, transparent 100%);
        border-radius: 2px;
        margin-top: 13px;
    }

    /* Sidebar Navigation Styles */
    .sidebar-section-header {
        font-size: 0.76rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.9px;
        color: #0F766E;
        margin: 16px 0 8px 0;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* ChatGPT New Chat Button */
    .chatgpt-new-chat-btn button {
        background: linear-gradient(135deg, #0D9488 0%, #0284C7 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        box-shadow: 0 4px 12px rgba(13, 148, 136, 0.25) !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
        width: 100% !important;
        margin-bottom: 8px !important;
    }
    .chatgpt-new-chat-btn button:hover {
        background: linear-gradient(135deg, #0F766E 0%, #0369A1 100%) !important;
        box-shadow: 0 6px 16px rgba(13, 148, 136, 0.35) !important;
        transform: translateY(-1px) !important;
    }

    /* Previous Conversations List */
    .chatgpt-conv-btn button {
        text-align: left !important;
        justify-content: flex-start !important;
        font-size: 0.81rem !important;
        font-weight: 500 !important;
        padding: 7px 10px !important;
        border-radius: 8px !important;
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        color: #334155 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        transition: all 0.15s ease !important;
        width: 100% !important;
    }
    .chatgpt-conv-btn button:hover {
        background: #F0FDFA !important;
        border-color: #5EEAD4 !important;
        color: #0F766E !important;
    }

    /* Active Conversation Highlight */
    .chatgpt-conv-active button {
        background: #F0FDFA !important;
        border: 1.5px solid #14B8A6 !important;
        color: #0F766E !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(20, 184, 166, 0.20) !important;
    }

    /* Delete Conversation Button */
    .chatgpt-del-btn button {
        padding: 6px 0 !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        color: #94A3B8 !important;
        border-radius: 8px !important;
        font-size: 0.82rem !important;
        transition: all 0.15s ease !important;
    }
    .chatgpt-del-btn button:hover {
        color: #DC2626 !important;
        background: #FEE2E2 !important;
        border-color: #FCA5A5 !important;
    }

    /* Recent Searches Pill Buttons */
    .recent-search-item button {
        text-align: left !important;
        justify-content: flex-start !important;
        font-size: 0.80rem !important;
        font-weight: 500 !important;
        padding: 6px 9px !important;
        border-radius: 8px !important;
        background: #FFFFFF !important;
        border: 1px solid #CCFBF1 !important;
        color: #134E4A !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        transition: all 0.15s ease !important;
        width: 100% !important;
        margin-bottom: 3px !important;
    }
    .recent-search-item button:hover {
        background: #F0FDFA !important;
        border-color: #5EEAD4 !important;
        color: #0F766E !important;
    }

    /* ========================================================= */
    /* PREMIUM GLOWING CHAT INPUT BOX & CONTROLS                 */
    /* ========================================================= */
    
    @keyframes chatInputGlowPulse {
        0% {
            border-color: #5EEAD4;
            box-shadow: 0 0 14px rgba(13, 148, 136, 0.28), 
                        0 0 28px rgba(6, 182, 212, 0.18), 
                        0 2px 8px rgba(15, 23, 42, 0.05);
        }
        50% {
            border-color: #2DD4BF;
            box-shadow: 0 0 22px rgba(13, 148, 136, 0.45), 
                        0 0 38px rgba(6, 182, 212, 0.32), 
                        0 4px 14px rgba(13, 148, 136, 0.15);
        }
        100% {
            border-color: #5EEAD4;
            box-shadow: 0 0 14px rgba(13, 148, 136, 0.28), 
                        0 0 28px rgba(6, 182, 212, 0.18), 
                        0 2px 8px rgba(15, 23, 42, 0.05);
        }
    }

    @keyframes sparkleFloat {
        0% { transform: translateY(0px) rotate(0deg); opacity: 0.85; }
        100% { transform: translateY(-2px) rotate(10deg); opacity: 1; filter: drop-shadow(0 0 8px rgba(6, 182, 212, 0.9)); }
    }

    [data-testid="stChatInput"] {
        padding-top: 8px !important;
        padding-bottom: 14px !important;
        background: transparent !important;
    }

    [data-testid="stChatInput"] > div {
        background: rgba(255, 255, 255, 0.96) !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        border: 2px solid #5EEAD4 !important;
        border-radius: 28px !important;
        animation: chatInputGlowPulse 4s ease-in-out infinite !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        padding: 5px 10px !important;
        display: flex !important;
        align-items: center !important;
    }

    [data-testid="stChatInput"] > div::before {
        content: "✨";
        font-size: 1.2rem;
        margin-left: 12px;
        margin-right: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        filter: drop-shadow(0 0 6px rgba(6, 182, 212, 0.7));
        cursor: default;
        user-select: none;
        animation: sparkleFloat 3s ease-in-out infinite alternate;
    }

    [data-testid="stChatInput"] > div:hover {
        border-color: #2DD4BF !important;
        background: #FFFFFF !important;
        box-shadow: 0 0 22px rgba(13, 148, 136, 0.42), 
                    0 0 38px rgba(6, 182, 212, 0.32), 
                    0 4px 16px rgba(13, 148, 136, 0.14) !important;
        transform: translateY(-1px) !important;
    }

    [data-testid="stChatInput"] > div:focus-within {
        border-color: #0D9488 !important;
        background: #FFFFFF !important;
        box-shadow: 0 0 0 2.5px rgba(13, 148, 136, 0.25), 
                    0 0 28px rgba(13, 148, 136, 0.55), 
                    0 0 50px rgba(6, 182, 212, 0.42) !important;
        animation: none !important;
        transform: translateY(-1px) !important;
    }

    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: #0F172A !important;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 0.94rem !important;
        font-weight: 500 !important;
        line-height: 1.5 !important;
        padding: 9px 12px !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #64748B !important;
        font-weight: 400 !important;
        font-size: 0.91rem !important;
        opacity: 0.88 !important;
    }

    [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #0D9488 0%, #06B6D4 100%) !important;
        border: none !important;
        border-radius: 50% !important;
        width: 38px !important;
        height: 38px !important;
        min-height: 38px !important;
        min-width: 38px !important;
        padding: 0 !important;
        margin-right: 4px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        color: #FFFFFF !important;
        box-shadow: 0 3px 12px rgba(13, 148, 136, 0.38) !important;
        cursor: pointer !important;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    [data-testid="stChatInput"] button:hover {
        transform: scale(1.09) !important;
        background: linear-gradient(135deg, #0F766E 0%, #0891B2 100%) !important;
        box-shadow: 0 0 16px rgba(13, 148, 136, 0.70), 
                    0 0 28px rgba(6, 182, 212, 0.55) !important;
    }

    [data-testid="stChatInput"] button:active {
        transform: scale(0.93) !important;
        box-shadow: 0 0 8px rgba(13, 148, 136, 0.40) !important;
    }

    [data-testid="stChatInput"] button svg {
        fill: #FFFFFF !important;
        stroke: #FFFFFF !important;
        width: 18px !important;
        height: 18px !important;
        transition: transform 0.15s ease !important;
    }

    [data-testid="stChatInput"] button:hover svg {
        transform: translateX(1.5px) translateY(-1px) !important;
    }

    [data-testid="stBottom"], [data-testid="stBottom"] > div {
        background: transparent !important;
    }

    /* ========================================================= */
    /* CHAT AREA IMPROVEMENTS: EXPANDED 90-95% FULL WIDTH CONTAINER */
    /* ========================================================= */

    /* Main Content Viewport: Clean Spacing & Center Alignment */
    .block-container,
    [data-testid="stMainBlockContainer"] {
        max-width: 95% !important;
        width: 95% !important;
        padding-top: 1.5rem !important;
        padding-bottom: 6rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* Chat Stream Header */
    .chat-stream-header {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        margin-bottom: 18px !important;
        padding: 0 4px !important;
        width: 95% !important;
        max-width: 1200px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    
    [data-testid="stChatMessage"] {
        padding: 8px 12px !important;
        margin-bottom: 22px !important;
        gap: 14px !important;
        border-radius: 18px !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }

    /* User Message Bubble: Compact & Distinctive (Preserved Design) */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]),
    [data-testid="stChatMessage"]:has([aria-label="🧑‍🎓"]) {
        width: fit-content !important;
        max-width: 82% !important;
        margin-left: auto !important;
        margin-right: 2.5% !important;
        background: linear-gradient(135deg, #F0FDFA 0%, #E0F2FE 100%) !important;
        border: 1.5px solid #99F6E4 !important;
        border-radius: 18px 18px 4px 18px !important;
        box-shadow: 0 2px 10px rgba(13, 148, 136, 0.08) !important;
        margin-bottom: 20px !important;
        padding: 12px 20px !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]):hover,
    [data-testid="stChatMessage"]:has([aria-label="🧑‍🎓"]):hover {
        box-shadow: 0 4px 14px rgba(13, 148, 136, 0.14) !important;
        transform: translateY(-1px) !important;
    }

    /* AI Response Box: 90-95% Full Width Expanded Container */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]),
    [data-testid="stChatMessage"]:has([aria-label="🤖"]) {
        width: 95% !important;
        max-width: 1200px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        background: #FFFFFF !important;
        background: linear-gradient(180deg, #FFFFFF 0%, #F0F9FF 100%) !important;
        border: 1.5px solid #BAE6FD !important;
        border-top: 4px solid #0E7490 !important;
        border-radius: 18px !important;
        box-shadow: 0 8px 28px -4px rgba(14, 116, 144, 0.10), 0 2px 8px -2px rgba(15, 23, 42, 0.04) !important;
        padding: 24px 30px !important;
        margin-bottom: 26px !important;
        transition: box-shadow 0.2s ease, border-color 0.2s ease !important;
        overflow: visible !important;
        height: auto !important;
        max-height: none !important;
        display: flex !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]):hover,
    [data-testid="stChatMessage"]:has([aria-label="🤖"]):hover {
        box-shadow: 0 12px 36px rgba(14, 116, 144, 0.15), 0 4px 12px rgba(15, 23, 42, 0.06) !important;
        border-color: #38BDF8 !important;
    }

    [data-testid="stChatMessageContent"] {
        width: 100% !important;
        max-width: 100% !important;
        flex: 1 1 100% !important;
    }

    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        border-radius: 50% !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12) !important;
        border: 2px solid #FFFFFF !important;
    }

    .chat-user-text {
        font-size: 0.95rem;
        font-weight: 600;
        color: #0F172A;
        line-height: 1.55;
    }

    /* AI Writing Block Header */
    .ai-wb-header {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        padding-bottom: 14px !important;
        margin-bottom: 16px !important;
        border-bottom: 1.5px solid #E0F2FE !important;
        flex-wrap: wrap !important;
        gap: 10px !important;
        width: 100% !important;
    }
    .ai-wb-title-group {
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
    }
    .ai-wb-icon {
        font-size: 20px !important;
        background: #E0F2FE !important;
        width: 38px !important;
        height: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border-radius: 10px !important;
        border: 1px solid #BAE6FD !important;
        box-shadow: 0 2px 6px rgba(14, 116, 144, 0.08) !important;
    }
    .ai-wb-heading {
        font-size: 1.05rem !important;
        font-weight: 800 !important;
        color: #0E7490 !important;
        letter-spacing: -0.2px !important;
        line-height: 1.25 !important;
    }
    .ai-wb-subtitle {
        font-size: 0.74rem !important;
        font-weight: 500 !important;
        color: #64748B !important;
        margin-top: 1px !important;
    }
    .ai-wb-badge {
        background: linear-gradient(135deg, #0284C7 0%, #0E7490 100%) !important;
        color: #FFFFFF !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        padding: 3px 10px !important;
        border-radius: 9999px !important;
        letter-spacing: 0.2px !important;
        box-shadow: 0 2px 6px rgba(14, 116, 144, 0.2) !important;
    }

    /* AI Response Formatting & Typography */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) p {
        color: #0F172A !important;
        font-size: 0.96rem !important;
        line-height: 1.7 !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) strong,
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) b {
        color: #0C4A6E !important;
        font-weight: 700 !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) h1,
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) h2,
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) h3,
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) h4 {
        color: #0E7490 !important;
        font-weight: 800 !important;
        margin-top: 16px !important;
        margin-bottom: 10px !important;
        letter-spacing: -0.2px !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) ul,
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) ol {
        margin: 10px 0 14px 22px !important;
        padding-left: 8px !important;
        color: #0F172A !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) li {
        margin-bottom: 7px !important;
        line-height: 1.65 !important;
    }

    /* Structured Tables: 100% Full Available Width */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) table {
        width: 100% !important;
        min-width: 100% !important;
        display: table !important;
        border-collapse: separate !important;
        border-spacing: 0 !important;
        border: 1.5px solid #BAE6FD !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        margin: 18px 0 !important;
        background: #FFFFFF !important;
        box-shadow: 0 3px 12px rgba(14, 116, 144, 0.06) !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) th {
        background: linear-gradient(135deg, #0E7490 0%, #0284C7 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        padding: 12px 18px !important;
        text-align: left !important;
        font-size: 0.90rem !important;
        letter-spacing: 0.2px !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) td {
        padding: 11px 18px !important;
        border-bottom: 1px solid #E2E8F0 !important;
        color: #1E293B !important;
        font-size: 0.90rem !important;
        line-height: 1.5 !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) tr:last-child td {
        border-bottom: none !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) tr:nth-child(even) td {
        background: #F8FAFC !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) tr:hover td {
        background: #F0FDF4 !important;
    }

    /* Action Buttons inside Chat (Regenerate & Feedback) */
    [data-testid="stChatMessage"] div.stButton > button {
        border-radius: 8px !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        padding: 5px 12px !important;
        height: 34px !important;
        line-height: 1 !important;
        transition: all 0.2s ease !important;
        border: 1.2px solid #BAE6FD !important;
        background: #F0F9FF !important;
        color: #0369A1 !important;
    }
    [data-testid="stChatMessage"] div.stButton > button:hover {
        background: #E0F2FE !important;
        border-color: #38BDF8 !important;
        color: #0284C7 !important;
        box-shadow: 0 2px 8px rgba(14, 116, 144, 0.15) !important;
        transform: translateY(-1px) !important;
    }

    /* Bottom Controls & Voice Dock: Max width aligned with 95% answer box */
    [data-testid="stChatInput"],
    .dock-container {
        max-width: 1200px !important;
        width: 95% !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* Responsive Width Controls for Desktop, Tablet, Mobile */
    @media (max-width: 1024px) {
        .block-container,
        [data-testid="stMainBlockContainer"],
        .chat-stream-header,
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]),
        [data-testid="stChatMessage"]:has([aria-label="🤖"]),
        [data-testid="stChatInput"],
        .dock-container {
            width: 96% !important;
            max-width: 96% !important;
        }
    }
    @media (max-width: 768px) {
        .block-container,
        [data-testid="stMainBlockContainer"],
        .chat-stream-header,
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]),
        [data-testid="stChatMessage"]:has([aria-label="🤖"]),
        [data-testid="stChatInput"],
        .dock-container {
            width: 98% !important;
            max-width: 98% !important;
            padding: 16px 14px !important;
        }
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]),
        [data-testid="stChatMessage"]:has([aria-label="🧑‍🎓"]) {
            max-width: 92% !important;
            margin-right: 1% !important;
        }
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) table {
            display: block !important;
            overflow-x: auto !important;
            white-space: nowrap !important;
        }
    }
</style>
"""

st.markdown(MAIN_CSS.replace("__CAMPUS_BG_B64__", campus_bg_b64), unsafe_allow_html=True)

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
# Session State Management & Conversation Helpers
# ---------------------------------------------------------
def get_initial_messages(language=None):
    """Returns the default initial welcome message for VRBot in English or Tamil."""
    if language is None:
        language = st.session_state.get("selected_language", "English")
    if language == "Tamil":
        return [
            {
                "role": "assistant",
                "content": (
                    "👋 வணக்கம்! **வி.ஆர் பொறியியல் கல்லூரி வளாக உதவி மையம் மற்றும் AI சேர்க்கை மையத்திற்கு (VR College AI Helpdesk)** உங்களை அன்புடன் வரவேற்கிறோம்.\n\n"
                    "நான் **VRBot**, உங்கள் கல்லூரி AI வழிகாட்டி! வி.ஆர் பொறியியல் கல்லூரி பற்றிய அனைத்து தகவல்களையும் அறிய நான் உங்களுக்கு உதவ முடியும்:\n"
                    "- 🎓 **பாடப்பிரிவுகள் & பட்டங்கள்** (B.Tech CSE, AI&DS, ECE, Mech, Civil, IT, M.Tech, MBA, MCA)\n"
                    "- 📝 **சேர்க்கை நடைமுறை & தகுதி வரம்புகள்** (TNEA கலந்தாய்வு, கட்-ஆப் மதிப்பெண்கள், தேவையான ஆவணங்கள்)\n"
                    "- 💰 **கட்டண விவரங்கள் & கல்வி உதவித்தொகை** (ஆண்டு கல்விக் கட்டணம், தவணை முறை வசதி, மெரிட் உதவித்தொகை)\n"
                    "- 🏢 **வளாக விடுதிகள் & வசதிகள்** (மாணவர்/மாணவியர் விடுதி, மெஸ் உணவு, பாதுகாப்பு)\n"
                    "- 💼 **வளாக வேலைவாய்ப்பு** (அதிகபட்ச சம்பளம்: ₹14.0 LPA, முன்னணி நிறுவனங்கள்)\n"
                    "- 📚 **மத்திய டிஜிட்டல் நூலகம் & அதிநவீன ஆய்வகங்கள்**\n\n"
                    "உங்களுக்கு தேவையான தகவல்களை தமிழில் எளிதாகக் கேளுங்கள்—அல்லது *'என்னென்ன பாடப்பிரிவுகள் உள்ளன?'*, *'விடுதி கட்டணம் எவ்வளவு?'* என்றும் கேட்கலாம்! இன்று நான் உங்களுக்கு எவ்வாறு உதவட்டும்? 😊"
                ),
                "meta": {
                    "visual": {
                        "image": "campus_main.jpg",
                        "caption": "🏛️ வி.ஆர் பொறியியல் கல்லூரி 50 ஏக்கர் வளாகம்"
                    }
                }
            }
        ]
    return [
        {
            "role": "assistant",
            "content": (
                "👋 Hello there! Welcome to the **VR College of Engineering Campus Helpdesk & AI Admissions Desk**.\n\n"
                "I'm **VRBot**, your friendly campus AI advisor! Think of me as your personal guide to everything about "
                "VR College of Engineering. I can help you with:\n"
                "- 🎓 **Courses & Programs** (B.Tech CSE, AI&DS, ECE, Mech, M.Tech, MBA, MCA)\n"
                "- 📝 **Admissions & Eligibility Criteria** (Cutoffs, lateral entry, documents required)\n"
                "- 💰 **Fee Schedules & Scholarships** (Installment options, tuition breakdown)\n"
                "- 🏢 **Campus Hostels & Facilities** (Mess menus, curfew timings, room amenities)\n"
                "- 💼 **Placements & Recruiter Records** (Highest CTC: ₹14 LPA, top hiring companies)\n"
                "- 📚 **Central Library & Research Labs**\n\n"
                "Feel free to ask your questions in normal, everyday language—or even ask follow-up questions like *'explain the first course'* or *'what is the fee for that?'*! How can I help you today? 😊"
            ),
            "meta": {
                "visual": {
                    "image": "campus_main.jpg",
                    "caption": "🏛️ VR College of Engineering 50-Acre Campus"
                }
            }
        }
    ]


def get_answer_heading_and_icon(category=None, matched_q=None, content="", language="English"):
    """Returns a topical heading and emoji icon for the AI response box (ChatGPT Writing Block UI)."""
    if language == "Tamil":
        category_map_tamil = {
            "Courses": ("கல்விப் பாடப்பிரிவுகள் மற்றும் பட்டங்கள்", "🎓"),
            "Admission": ("சேர்க்கை நடைமுறை மற்றும் தகுதி வரம்புகள்", "📝"),
            "Fee": ("கல்விக் கட்டணம் மற்றும் கட்டண அட்டவணை", "💰"),
            "Fees": ("கல்விக் கட்டணம் மற்றும் கட்டண அட்டவணை", "💰"),
            "Hostel": ("வளாக விடுதிகள் மற்றும் தங்கும் வசதிகள்", "🏢"),
            "Placement": ("வளாக வேலைவாய்ப்பு மற்றும் நிறுவனங்கள்", "💼"),
            "Scholarship": ("கல்வி உதவித்தொகை மற்றும் நிதி சலுகைகள்", "🎖️"),
            "Library": ("மத்திய டிஜிட்டல் நூலகம் மற்றும் ஆய்வு வளங்கள்", "📚"),
            "Transport": ("கல்லூரி பேருந்து வழித்தடங்கள்", "🚌"),
            "Department": ("கல்வித் துறைகள் மற்றும் ஆய்வகங்கள்", "🔬"),
            "Departments": ("கல்வித் துறைகள் மற்றும் ஆய்வகங்கள்", "🔬"),
            "Facility": ("வளாக கட்டமைப்பு மற்றும் வசதிகள்", "🏛️"),
            "Cutoff": ("கட்-ஆப் மதிப்பெண்கள் மற்றும் சேர்க்கை வழிகாட்டி", "📊"),
            "Contact": ("சேர்க்கை உதவி மையம் மற்றும் தொடர்புகள்", "📞"),
            "Greeting": ("வி.ஆர் பொறியியல் கல்லூரிக்கு நல்வரவு", "👋"),
            "Gratitude": ("வி.ஆர் கல்லூரி ஆலோசனை உதவி", "😊"),
            "Farewell": ("உங்கள் கல்விப் பயணம் சிறக்க வாழ்த்துகள்", "🌟"),
        }
        cat = (category or "").strip()
        if cat in category_map_tamil:
            return category_map_tamil[cat]
        lower_c = (content or "").lower()
        if any(k in lower_c for k in ["கட்டணம்", "fee", "tuition"]):
            return ("கல்விக் கட்டணம் மற்றும் கட்டண அட்டவணை", "💰")
        elif any(k in lower_c for k in ["பாடப்பிரிவு", "course", "b.tech", "degree"]):
            return ("கல்விப் பாடப்பிரிவுகள் மற்றும் பட்டங்கள்", "🎓")
        elif any(k in lower_c for k in ["சேர்க்கை", "admission", "eligibility"]):
            return ("சேர்க்கை மற்றும் தகுதி வழிகாட்டுதல்", "📝")
        elif any(k in lower_c for k in ["விடுதி", "hostel", "room"]):
            return ("வளாக விடுதிகள் மற்றும் வசதிகள்", "🏢")
        elif any(k in lower_c for k in ["வேலைவாய்ப்பு", "placement"]):
            return ("வேலைவாய்ப்பு மற்றும் நிறுவனங்கள்", "💼")
        elif any(k in lower_c for k in ["உதவித்தொகை", "scholarship"]):
            return ("கல்வி உதவித்தொகை மற்றும் சலுகைகள்", "🎖️")
        return ("வி.ஆர் கல்லூரி அதிகாரப்பூர்வ தகவல்", "✨")

    cat = (category or "").strip()
    category_map = {
        "Courses": ("Academic Programs & Degree Courses", "🎓"),
        "Admission": ("Admissions Procedure & Eligibility Criteria", "📝"),
        "Fee": ("Tuition Fees & Complete Payment Schedule", "💰"),
        "Fees": ("Tuition Fees & Complete Payment Schedule", "💰"),
        "Hostel": ("Campus Hostels & Residential Facilities", "🏢"),
        "Placement": ("Campus Placements & Recruiter Records", "💼"),
        "Scholarship": ("Scholarships & Financial Assistance", "🎖️"),
        "Library": ("Central Digital Library & Academic Resources", "📚"),
        "Transport": ("Campus Bus Routes & Connectivity", "🚌"),
        "Department": ("Academic Departments & Laboratories", "🔬"),
        "Departments": ("Academic Departments & Laboratories", "🔬"),
        "Facility": ("Campus Infrastructure & Student Amenities", "🏛️"),
        "Cutoff": ("Cutoff Marks & Counseling Trends", "📊"),
        "Contact": ("Admissions Desk & Contact Directory", "📞"),
        "Greeting": ("Welcome to VR College of Engineering", "👋"),
        "Gratitude": ("VR College Advisory Assistance", "😊"),
        "Farewell": ("Wishing You Success on Your Academic Journey", "🌟"),
    }
    if cat in category_map:
        return category_map[cat]

    lower_c = (content or "").lower()
    if "fee" in lower_c or "tuition" in lower_c:
        return ("Tuition Fees & Payment Schedule", "💰")
    elif "course" in lower_c or "b.tech" in lower_c or "degree" in lower_c:
        return ("Academic Programs & Degree Courses", "🎓")
    elif "admission" in lower_c or "eligibility" in lower_c or "apply" in lower_c:
        return ("Admissions & Eligibility Guidance", "📝")
    elif "hostel" in lower_c or "room" in lower_c or "mess" in lower_c:
        return ("Campus Hostels & Amenities", "🏢")
    elif "placement" in lower_c or "recruiter" in lower_c or "package" in lower_c:
        return ("Placements & Career Opportunities", "💼")
    elif "scholarship" in lower_c or "concession" in lower_c:
        return ("Scholarships & Financial Concessions", "🎖️")

    if matched_q:
        clean = matched_q.strip().rstrip("?")
        if len(clean) <= 45:
            return (clean, "📘")

    return ("VR College Official Advisory", "✨")


# Pre-initialize clicked_query before the sidebar so sidebar actions can set it
clicked_query = None

# Initialize Conversation State with SQLite persistence
if "current_conversation_id" not in st.session_state:
    recent_convs = list_conversations(limit=1)
    if recent_convs:
        latest_id = recent_convs[0]["id"]
        st.session_state.current_conversation_id = latest_id
        db_msgs = get_conversation_messages(latest_id)
        st.session_state.messages = db_msgs if db_msgs else get_initial_messages()
    else:
        new_id = uuid.uuid4().hex[:10]
        st.session_state.current_conversation_id = new_id
        st.session_state.messages = get_initial_messages()
elif "messages" not in st.session_state:
    db_msgs = get_conversation_messages(st.session_state.current_conversation_id)
    st.session_state.messages = db_msgs if db_msgs else get_initial_messages()

# ---------------------------------------------------------
# Sidebar: ChatGPT-Style Navigation, AI Engine & System Controls
# ---------------------------------------------------------
with st.sidebar:
    logo_b64 = ""
    if os.path.exists(LOGO_PATH):
        try:
            with open(LOGO_PATH, "rb") as img_f:
                logo_b64 = base64.b64encode(img_f.read()).decode("utf-8")
        except Exception:
            pass

    logo_img_html = (
        f'<img src="data:image/png;base64,{logo_b64}" class="sidebar-logo-img" alt="VR College Logo" />'
        if logo_b64
        else '<span style="font-size:2.2rem;">🎓</span>'
    )

    st.markdown(
        f"""
        <div class="sidebar-brand-card">
            <div class="sidebar-brand-content">
                <div class="sidebar-logo-frame">
                    {logo_img_html}
                </div>
                <div class="sidebar-text-col">
                    <div class="sidebar-brand-title">VR COLLEGE OF ENGINEERING</div>
                    <div class="sidebar-badges-row">
                        <span class="sidebar-badge-aicte">Approved by AICTE</span>
                        <span class="sidebar-badge-estd">Estd. 2005</span>
                    </div>
                    <div class="sidebar-sub-accred">NAAC 'A+' Accredited Institution</div>
                </div>
            </div>
            <div class="sidebar-brand-divider"></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # 1. ➕ New Chat Button (ChatGPT Style)
    # -----------------------------------------------------
    st.markdown('<div class="chatgpt-new-chat-btn">', unsafe_allow_html=True)
    if st.button("➕ New Chat", use_container_width=True, type="primary", key="btn_new_chat"):
        new_id = uuid.uuid4().hex[:10]
        st.session_state.current_conversation_id = new_id
        st.session_state.messages = get_initial_messages()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------
    # 2. 🔍 Search Conversations
    # -----------------------------------------------------
    search_term = st.text_input(
        "Search conversations",
        placeholder="🔍 Search conversations...",
        label_visibility="collapsed",
        key="search_conversations_input"
    )

    # -----------------------------------------------------
    # 3. 🕘 Recent Searches (User's recently asked questions)
    # -----------------------------------------------------
    st.markdown('<div class="sidebar-section-header">🕘 Recent Searches</div>', unsafe_allow_html=True)
    recent_searches_list = get_recent_searches(limit=8)
    if recent_searches_list:
        for s_idx, q_text in enumerate(recent_searches_list):
            st.markdown('<div class="recent-search-item">', unsafe_allow_html=True)
            if st.button(f"🔍 {q_text}", key=f"recent_s_btn_{s_idx}", use_container_width=True, help="Click to ask this enquiry"):
                clicked_query = q_text
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.caption("No recent searches yet.")

    # -----------------------------------------------------
    # 4. 📂 Previous Conversations (SQLite Persistent History)
    # -----------------------------------------------------
    st.markdown('<div class="sidebar-section-header">📂 Previous Conversations</div>', unsafe_allow_html=True)
    convs = list_conversations(search_query=search_term, limit=20)

    if not convs:
        if search_term:
            st.caption(f"No chats found matching '{search_term}'")
        else:
            st.caption("No saved conversations yet. Ask a question to begin!")
    else:
        for c in convs:
            is_active = (c["id"] == st.session_state.get("current_conversation_id"))
            col_c1, col_c2 = st.columns([0.82, 0.18])
            with col_c1:
                title_label = f"👉 {c['title']}" if is_active else f"💬 {c['title']}"
                st.markdown(f'<div class="chatgpt-conv-btn {"chatgpt-conv-active" if is_active else ""}">', unsafe_allow_html=True)
                if st.button(title_label, key=f"conv_select_{c['id']}", use_container_width=True, help=f"Last updated: {c['updated_at']}"):
                    st.session_state.current_conversation_id = c["id"]
                    db_msgs = get_conversation_messages(c["id"])
                    st.session_state.messages = db_msgs if db_msgs else get_initial_messages()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with col_c2:
                st.markdown('<div class="chatgpt-del-btn">', unsafe_allow_html=True)
                if st.button("🗑️", key=f"conv_del_{c['id']}", help="Delete this conversation", use_container_width=True):
                    delete_conversation(c["id"])
                    if st.session_state.get("current_conversation_id") == c["id"]:
                        new_id = uuid.uuid4().hex[:10]
                        st.session_state.current_conversation_id = new_id
                        st.session_state.messages = get_initial_messages()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # -----------------------------------------------------
    # 5. AI Engine & System Controls
    # -----------------------------------------------------
    st.markdown("#### 🧠 **AI Intelligence Engine**")

    # API Key Configuration
    env_key = get_api_key() or ""
    custom_key = st.text_input(
        "Google Gemini API Key (Optional):",
        value=env_key,
        type="password",
        help="Optional: Enter a Gemini API Key to enable ChatGPT-like LLM generation. If empty, the smart local conversational engine is used 100% free with zero API costs!"
    )
    active_api_key = custom_key.strip() if custom_key else env_key

    if is_ai_available(active_api_key):
        st.markdown(
            """
            <div style="background:#ECFDF5; border:1px solid #A7F3D0; color:#047857; font-size:0.78rem; font-weight:700; padding:6px 10px; border-radius:8px; margin-bottom:8px;">
                🤖 Mode: Gemini 2.5 Flash (AI Enhanced)
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style="background:#EFF6FF; border:1px solid #BFDBFE; color:#1D4ED8; font-size:0.78rem; font-weight:700; padding:6px 10px; border-radius:8px; margin-bottom:8px;">
                ⚡ Mode: Local Smart Conversational Agent (100% Free / Offline)
            </div>
            """,
            unsafe_allow_html=True
        )
        st.caption("💡 Tip: To enable Gemini generative responses, get a free key from [aistudio.google.com](https://aistudio.google.com/).")

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

        engine_label = "Gemini AI + TF-IDF Grounding" if is_ai_available(active_api_key) else "TF-IDF + Fuzzy Conversational NLP"
        st.caption(f"Engine: **{engine_label}** | Threshold: **{threshold:.2f}**")

    st.markdown("---")
    st.markdown("#### 📄 **Official Prospectus**")
    if os.path.exists(PROSPECTUS_PATH):
        with open(PROSPECTUS_PATH, "rb") as f_pdf:
            pdf_bytes = f_pdf.read()
        st.download_button(
            "📥 Download 2026-27 Prospectus (PDF)",
            data=pdf_bytes,
            file_name="VR_College_Prospectus_2026.pdf",
            mime="application/pdf",
            use_container_width=True,
            help="Download comprehensive courses, fee structure, hostel rules, and placement report"
        )

    st.markdown("---")
    st.markdown("#### 🛠️ **Session Tools**")
    if st.session_state.get("show_admission_form", False):
        if st.button("🏠 Return to Chatbot Home", key="side_return_home_btn", use_container_width=True, help="Return to conversational chatbot"):
            st.session_state["show_admission_form"] = False
            st.rerun()
    else:
        if st.button("📝 Apply for Admission (Form)", key="side_open_form_btn", use_container_width=True, help="Open the official College Admission Application Form"):
            st.session_state["show_admission_form"] = True
            st.rerun()
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🗑️ Clear Chat", use_container_width=True, help="Clear current conversation history"):
            conv_id = st.session_state.get("current_conversation_id")
            if conv_id:
                delete_conversation(conv_id)
            new_id = uuid.uuid4().hex[:10]
            st.session_state.current_conversation_id = new_id
            st.session_state.messages = get_initial_messages()
            st.rerun()

    with col_btn2:
        transcript = "\n\n".join([
            f"{'Student' if m['role'] == 'user' else 'VRBot'}: {m['content']}"
            for m in st.session_state.messages
        ])
        st.download_button(
            "📥 Export Chat",
            data=transcript,
            file_name="vr_college_chat_transcript.txt",
            mime="text/plain",
            use_container_width=True,
            help="Download chat history as text"
        )

    st.markdown("---")
    st.markdown("#### 🏛️ **Campus Snapshot**")
    if os.path.exists(CAMPUS_MAIN_IMG):
        st.image(CAMPUS_MAIN_IMG, caption="VR College of Engineering 50-Acre Green Campus Quad", use_container_width=True)

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size: 0.78rem; color: #64748B; line-height: 1.5;">
            <strong>VR College of Engineering</strong><br>
            Knowledge Campus, Sector 4, Education City<br>
            📞 Helpline: +91 98765 43210<br>
            ✉️ Email: admissions@vrcollege.edu
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# Top Navigation Bar: Branding, Language Translator & Profile
# ---------------------------------------------------------
col_nav_brand, col_nav_ctrl = st.columns([1.5, 1.0], gap="medium")

with col_nav_brand:
    st.markdown(
        """
        <div class="top-nav-bar" style="margin-bottom:0;">
            <div class="top-nav-left">
                <div class="top-nav-logo-wrap">
                    <span style="font-size: 1.3rem;">🏛️</span>
                </div>
                <div>
                    <div class="top-nav-title">VR College of Engineering</div>
                    <div class="top-nav-subtitle">Approved by AICTE • NAAC 'A+' Grade • Estd. 2005 • Affiliated to Tech University</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_nav_ctrl:
    c_lang_col, c_prof_col = st.columns([1.1, 1.3], gap="small")
    with c_lang_col:
        curr_lang = st.session_state.get("selected_language", "English")
        lang_idx = 1 if curr_lang == "Tamil" else 0
        chosen_language = st.selectbox(
            "Language Translator",
            ["🌐 English", "🌐 தமிழ் (Tamil)"],
            index=lang_idx,
            label_visibility="collapsed",
            help="Select your consultation language / மொழியைத் தேர்ந்தெடுக்கவும்",
            key="language_translator_select"
        )
        detected_lang = "Tamil" if ("Tamil" in chosen_language or "தமிழ்" in chosen_language) else "English"
        if st.session_state.get("selected_language") != detected_lang:
            st.session_state.selected_language = detected_lang
            if len(st.session_state.messages) == 1 and st.session_state.messages[0].get("role") == "assistant":
                st.session_state.messages = get_initial_messages(detected_lang)
            st.rerun()

    with c_prof_col:
        prof_name = "மாணவர் வழிகாட்டி" if st.session_state.get("selected_language") == "Tamil" else "Student Scholar"
        prof_desk = "24/7 உதவி மையம்" if st.session_state.get("selected_language") == "Tamil" else "24/7 Consultation Desk"
        st.markdown(
            f"""
            <div class="user-profile-badge">
                <div class="profile-avatar">🧑‍🎓</div>
                <div class="profile-meta">
                    <div class="profile-name">{prof_name}</div>
                    <div class="profile-status"><span class="pulse-emerald-dot"></span> {prof_desk}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Welcome Banner: Mascot, College Intro & Illustrated Scenery
# ---------------------------------------------------------
is_tamil_ui = (st.session_state.get("selected_language") == "Tamil")
if is_tamil_ui:
    hero_badge = "🏛️ வி.ஆர் பொறியியல் கல்லூரி • NAAC 'A+' அங்கீகாரம்"
    hero_heading = "🎓 வி.ஆர் கல்லூரி AI வளாக தகவல் மையத்திற்கு நல்வரவு"
    hero_subtext = "எங்கள் 50 ஏக்கர் பசுமை வைஃபை வளாகத்தை அறிந்து கொள்ளுங்கள், சிறந்த பொறியியல் பட்டப்படிப்புகளைக் கண்டறியுங்கள், கல்விக் கட்டணம் மற்றும் விடுதி கட்டணங்களை கணக்கிடுங்கள், மற்றும் எங்கள் AI வழிகாட்டியிடமிருந்து 24/7 உடனடி சேர்க்கை வழிகாட்டலைப் பெறுங்கள்."
    stat1_num, stat1_lbl = "NAAC 'A+'", "அங்கீகாரம்"
    stat2_num, stat2_lbl = "₹ 14.0 LPA", "அதிகபட்ச சம்பளம்"
    stat3_num, stat3_lbl = "92%", "வேலைவாய்ப்பு"
    stat4_num, stat4_lbl = "50+ ஏக்கர்", "பசுமை வளாகம்"
    stat5_num, stat5_lbl = "2026-27", "சேர்க்கை திறக்கப்பட்டுள்ளது"
    mascot_role = "AI சேர்க்கை வழிகாட்டி"
    mascot_live = "24/7 உதவி மையம் தயார்"
else:
    hero_badge = "🏛️ VR COLLEGE OF ENGINEERING • NAAC 'A+' INSTITUTION"
    hero_heading = "🎓 Welcome to VR College AI Campus Portal"
    hero_subtext = "Explore our 50-acre Wi-Fi green campus, discover top engineering &amp; technology degrees, calculate tuition and hostel fees, and receive immediate admissions advisory 24/7 from our intelligent campus assistant."
    stat1_num, stat1_lbl = "NAAC 'A+'", "Accredited"
    stat2_num, stat2_lbl = "₹ 14.0 LPA", "Highest Package"
    stat3_num, stat3_lbl = "92%", "Placements"
    stat4_num, stat4_lbl = "50+ Acres", "Green Campus"
    stat5_num, stat5_lbl = "2026-27", "Admissions Open"
    mascot_role = "AI Admissions Counselor"
    mascot_live = "24/7 Desk Online"

st.markdown(
    f"""
    <div class="campus-welcome-hero">
        <div class="hero-left-content">
            <div class="hero-college-badge">
                <span>🏛️</span> {hero_badge}
            </div>
            <h1 class="hero-portal-heading">
                {hero_heading}
            </h1>
            <p class="hero-portal-subtext">
                {hero_subtext}
            </p>
            <div class="hero-stats-deck">
                <div class="hero-stat-pill">
                    <span class="pill-icon">🏆</span>
                    <div>
                        <div class="pill-num">{stat1_num}</div>
                        <div class="pill-lbl">{stat1_lbl}</div>
                    </div>
                </div>
                <div class="hero-stat-pill">
                    <span class="pill-icon">💼</span>
                    <div>
                        <div class="pill-num">{stat2_num}</div>
                        <div class="pill-lbl">{stat2_lbl}</div>
                    </div>
                </div>
                <div class="hero-stat-pill">
                    <span class="pill-icon">🎓</span>
                    <div>
                        <div class="pill-num">{stat3_num}</div>
                        <div class="pill-lbl">{stat3_lbl}</div>
                    </div>
                </div>
                <div class="hero-stat-pill">
                    <span class="pill-icon">🌳</span>
                    <div>
                        <div class="pill-num">{stat4_num}</div>
                        <div class="pill-lbl">{stat4_lbl}</div>
                    </div>
                </div>
                <div class="hero-stat-pill highlight-gold">
                    <span class="pill-icon">🌟</span>
                    <div>
                        <div class="pill-num">{stat5_num}</div>
                        <div class="pill-lbl">{stat5_lbl}</div>
                    </div>
                </div>
            </div>
        </div>
        <div class="hero-mascot-container">
            <div class="mascot-card-outer">
                <div class="mascot-icon-display">🤖</div>
                <div class="mascot-badge-name">VRBot Mascot</div>
                <div class="mascot-badge-role">{mascot_role}</div>
                <div class="mascot-live-indicator">
                    <span class="pulse-emerald-dot"></span> {mascot_live}
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Direct Navigation via Query Params or Admissions State
# ---------------------------------------------------------
if st.query_params.get("page") == "apply" or st.query_params.get("apply") == "true":
    st.session_state["show_admission_form"] = True

if st.session_state.get("show_admission_form", False):
    render_admission_application_form()
else:
    # Quick Access Cards (Courses, Fee Structure, Hostel, Placements, Admissions)
    # ---------------------------------------------------------
    qa_chip_text = "⚡ உடனடி அணுகல் போர்ட்டல்கள் (அறிய கிளிக் செய்க)" if is_tamil_ui else "⚡ Quick Access Portals (Click to Explore)"
    st.markdown(f"<div class='section-label-chip'>{qa_chip_text}</div>", unsafe_allow_html=True)
    c_qa1, c_qa2, c_qa3, c_qa4, c_qa5 = st.columns(5)
    
    with c_qa1:
        st.markdown('<div class="quick-access-btn">', unsafe_allow_html=True)
        lbl1 = "🎓 பாடப்பிரிவுகள்\nB.Tech & PG" if is_tamil_ui else "🎓 Courses\nB.Tech & PG"
        if st.button(lbl1, key="qa_courses", use_container_width=True, help="Explore engineering & PG degree programs"):
            clicked_query = "வி.ஆர் பொறியியல் கல்லூரியில் என்னென்ன பாடப்பிரிவுகள் உள்ளன?" if is_tamil_ui else "What undergraduate and postgraduate courses are offered at VR College?"
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c_qa2:
        st.markdown('<div class="quick-access-btn">', unsafe_allow_html=True)
        lbl2 = "💰 கட்டண விவரம்\nகல்விக் கட்டணம்" if is_tamil_ui else "💰 Fee Structure\nTuition & Aid"
        if st.button(lbl2, key="qa_fees", use_container_width=True, help="Check tuition fees, installments, and scholarships"):
            clicked_query = "கல்லூரி கட்டண விவரங்கள் மற்றும் உதவித்தொகை என்ன?" if is_tamil_ui else "What is the annual tuition fee for B.Tech and installment options?"
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c_qa3:
        st.markdown('<div class="quick-access-btn">', unsafe_allow_html=True)
        lbl3 = "🏢 விடுதி வசதி\nஅறைகள் & மெஸ்" if is_tamil_ui else "🏢 Hostel\nAC Rooms & Mess"
        if st.button(lbl3, key="qa_hostel", use_container_width=True, help="Hostel facilities, food menu, and security"):
            clicked_query = "மாணவர் மற்றும் மாணவியர் விடுதி வசதிகள் என்ன?" if is_tamil_ui else "What are the hostel facilities and fee structure for boys and girls?"
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c_qa4:
        st.markdown('<div class="quick-access-btn">', unsafe_allow_html=True)
        lbl4 = "💼 வேலைவாய்ப்பு\n14 LPA CTC" if is_tamil_ui else "💼 Placements\n14 LPA CTC"
        if st.button(lbl4, key="qa_placements", use_container_width=True, help="Campus recruitment statistics and top recruiters"):
            clicked_query = "வளாக வேலைவாய்ப்பு மற்றும் சம்பள விவரங்கள் என்ன?" if is_tamil_ui else "What was the highest and average salary package in recent placements?"
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c_qa5:
        st.markdown('<div class="quick-access-btn">', unsafe_allow_html=True)
        lbl5 = "📋 சேர்க்கை\nவிண்ணப்பிக்க 2026-27" if is_tamil_ui else "📋 Admissions\nApply 2026-27"
        if st.button(lbl5, key="qa_admissions", use_container_width=True, help="Eligibility criteria, cutoffs, and application process"):
            st.session_state["show_admission_form"] = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)
    
    clicked_query = clicked_query if "clicked_query" in locals() and clicked_query else None
    
    # =========================================================
    # Campus Hub & Exploration Center (Collapsible Full-Width Hub)
    # =========================================================
    hub_title = "🏛️ **வளாக ஆய்வு மையம் (அடிக்கடி கேட்கப்படும் கேள்விகள், சேர்க்கை விண்ணப்பம், உதவி மையம் & தொடர்புகள்)**" if is_tamil_ui else "🏛️ **Interactive Campus Exploration Hub (Quick FAQs, Apply Online, Staff Desk, Campus Highlights & Contacts)**"
    with st.expander(hub_title, expanded=False):
        hub_tabs_list = [
            "💡 கேள்விகள் (FAQs)", "📝 விண்ணப்பிக்க (Apply)", "🔐 பணியாளர் மையம்", "📸 புகைப்படங்கள்", "🏛️ சிறப்பம்சங்கள்", "📞 உதவி மையம்", "📊 பதிவுகள்"
        ] if is_tamil_ui else [
            "💡 FAQs", "📝 Apply", "🔐 Staff Desk", "📸 Gallery", "🏛️ Highlights", "📞 Helpdesk", "📊 Logs"
        ]
        tab_faqs, tab_leads, tab_admin, tab_gallery, tab_campus, tab_contacts, tab_logs = st.tabs(hub_tabs_list)
    
        # 1. Quick Questions Tab
        with tab_faqs:
            faq_hint = "கீழே உள்ள கேள்விகளில் ஏதேனும் ஒன்றைத் தேர்ந்தெடுத்து உடனடியாக AI உதவியாளரிடம் கேளுங்கள்:" if is_tamil_ui else "Select any frequent inquiry below to ask the AI assistant immediately:"
            st.markdown(
                f"""
                <div style="font-size:0.85rem; color:#475569; margin-bottom:12px;">
                    {faq_hint}
                </div>
                """,
                unsafe_allow_html=True
            )
    
            st.caption("🎓 **சேர்க்கை & தகுதி**" if is_tamil_ui else "🎓 **Admissions & Eligibility**")
            btn1_txt = "📌 B.Tech சேர்க்கைக்கான தகுதி வரம்புகள்?" if is_tamil_ui else "📌 Eligibility criteria for B.Tech?"
            btn1_q = "B.Tech சேர்க்கை தகுதி என்ன?" if is_tamil_ui else "What is the eligibility criteria for B.Tech admission?"
            if st.button(btn1_txt, key="btn_q1", use_container_width=True):
                clicked_query = btn1_q

            btn2_txt = "📌 சேர்க்கைக்கு எவ்வாறு விண்ணப்பிப்பது?" if is_tamil_ui else "📌 How can I apply for admission?"
            btn2_q = "சேர்க்கைக்கு எவ்வாறு விண்ணப்பிப்பது?" if is_tamil_ui else "How can I apply for admission?"
            if st.button(btn2_txt, key="btn_q2", use_container_width=True):
                clicked_query = btn2_q

            btn3_txt = "📌 சேர்க்கை எப்போது தொடங்கும்?" if is_tamil_ui else "📌 When does the admission process start?"
            btn3_q = "சேர்க்கை செயல்முறை எப்போது தொடங்கும்?" if is_tamil_ui else "When does the admission process start?"
            if st.button(btn3_txt, key="btn_q3", use_container_width=True):
                clicked_query = btn3_q
    
            st.caption("💰 **கட்டணம் & நிதி உதவி**" if is_tamil_ui else "💰 **Fees & Financial Aid**")
            btn4_txt = "📌 B.Tech ஆண்டு கல்விக் கட்டணம் எவ்வளவு?" if is_tamil_ui else "📌 Annual tuition fee for B.Tech?"
            btn4_q = "B.Tech ஆண்டு கல்விக் கட்டணம் எவ்வளவு?" if is_tamil_ui else "What is the annual tuition fee for B.Tech?"
            if st.button(btn4_txt, key="btn_q4", use_container_width=True):
                clicked_query = btn4_q

            btn5_txt = "📌 மாணவர்களுக்கு உதவித்தொகை உள்ளதா?" if is_tamil_ui else "📌 Are scholarships available?"
            btn5_q = "மாணவர்களுக்கு உதவித்தொகை உள்ளதா?" if is_tamil_ui else "Are scholarships available for students?"
            if st.button(btn5_txt, key="btn_q5", use_container_width=True):
                clicked_query = btn5_q

            btn6_txt = "📌 தவணை முறையில் கட்டணம் செலுத்தலாமா?" if is_tamil_ui else "📌 Is installment facility available?"
            btn6_q = "தவணை முறை கட்டண வசதி உள்ளதா?" if is_tamil_ui else "Is installment facility available for fee payment?"
            if st.button(btn6_txt, key="btn_q6", use_container_width=True):
                clicked_query = btn6_q
    
            st.caption("🏢 **விடுதி & வாழ்க்கை**" if is_tamil_ui else "🏢 **Hostel & Life**")
            btn7_txt = "📌 மாணவ, மாணவியருக்கு விடுதி வசதி உள்ளதா?" if is_tamil_ui else "📌 Are hostel facilities available?"
            btn7_q = "மாணவ மாணவியருக்கு விடுதி வசதிகள் உள்ளதா?" if is_tamil_ui else "Are hostel facilities available for boys and girls?"
            if st.button(btn7_txt, key="btn_q7", use_container_width=True):
                clicked_query = btn7_q

            btn8_txt = "📌 விடுதி கட்டண விவரங்கள் என்ன?" if is_tamil_ui else "📌 What is the hostel fee structure?"
            btn8_q = "விடுதி கட்டண விவரங்கள் என்ன?" if is_tamil_ui else "What is the hostel fee structure?"
            if st.button(btn8_txt, key="btn_q8", use_container_width=True):
                clicked_query = btn8_q
    
            st.caption("💼 **வேலைவாய்ப்பு & நூலகம்**" if is_tamil_ui else "💼 **Placements & Library**")
            btn9_txt = "📌 வளாக நேர்காணலுக்கு வரும் நிறுவனங்கள் எவை?" if is_tamil_ui else "📌 What companies visit for campus placement?"
            btn9_q = "வளாக நேர்காணலுக்கு வரும் முன்னணி நிறுவனங்கள் எவை?" if is_tamil_ui else "What companies visit the college for campus recruitment?"
            if st.button(btn9_txt, key="btn_q9", use_container_width=True):
                clicked_query = btn9_q

            btn10_txt = "📌 அதிகபட்ச மற்றும் சராசரி சம்பளம் எவ்வளவு?" if is_tamil_ui else "📌 Highest and average salary package?"
            btn10_q = "அதிகபட்ச மற்றும் சராசரி சம்பள விவரங்கள் என்ன?" if is_tamil_ui else "What was the highest and average salary package in recent placements?"
            if st.button(btn10_txt, key="btn_q10", use_container_width=True):
                clicked_query = btn10_q

            btn11_txt = "📌 மத்திய நூலகம் இயங்கும் நேரம் என்ன?" if is_tamil_ui else "📌 Central library operating hours?"
            btn11_q = "நூலகம் இயங்கும் நேரம் என்ன?" if is_tamil_ui else "What are the library timings and working hours?"
            if st.button(btn11_txt, key="btn_q11", use_container_width=True):
                clicked_query = btn11_q
    
        # 2. Admission Lead Capture Form
        with tab_leads:
            st.markdown(
                """
                <div class="card-title">📝 Apply Online / Formal Application Portal</div>
                <div style="font-size:0.83rem; color:#475569; margin-bottom:10px;">
                    Open the official 11-field formal College Admission Application Form (2026-27) or request an instant counseling callback below:
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("📝 Open Official College Admission Application Form", key="hub_open_full_form", type="primary", use_container_width=True, help="Launch the full formal 11-field admission application form"):
                st.session_state["show_admission_form"] = True
                st.rerun()
    
            st.markdown("<div style='text-align:center; font-size:0.78rem; color:#64748B; margin: 10px 0 12px 0;'>— OR Request Instant Counselor Callback Below —</div>", unsafe_allow_html=True)
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
    
        # 4. Campus Gallery Tab with Interactive Image Cards across 15 Categories
        with tab_gallery:
            st.markdown(
                """
                <div class="card-title">📸 Interactive Campus Showcase</div>
                <div style="font-size:0.83rem; color:#475569; margin-bottom:12px;">
                    Explore all 15 specialized facilities across the 50-acre VR College of Engineering Campus. Click any card to enquire immediately:
                </div>
                """,
                unsafe_allow_html=True
            )
            gallery_cards = get_all_interactive_cards()
            for c_idx, card in enumerate(gallery_cards):
                card_img_path = os.path.join(ASSETS_DIR, card["image"])
                with st.container():
                    st.markdown(
                        f"""
                        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:10px 12px; margin-bottom:6px; box-shadow:0 2px 4px rgba(0,0,0,0.03);">
                            <div style="font-size:0.90rem; font-weight:700; color:#1E3A8A; margin-bottom:3px;">
                                {card['title']}
                            </div>
                            <div style="font-size:0.78rem; color:#475569; line-height:1.4;">
                                {card['description']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if os.path.exists(card_img_path):
                        st.image(card_img_path, caption=card["title"], use_container_width=True)
                    if st.button(f"👉 Enquire: {card['title']}", key=f"gal_card_{card['id']}_{c_idx}", use_container_width=True):
                        clicked_query = card["quick_prompt"]
                    st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
    
        # 5. Highlights Tab
        with tab_campus:
            if os.path.exists(CAMPUS_MAIN_IMG):
                st.image(CAMPUS_MAIN_IMG, caption="VR College of Engineering Knowledge Campus (50+ Acres Green Infrastructure)", use_container_width=True)
    
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
                    <div class="info-row"><span class="info-label">Email:</span><span class="info-val">admissions@vrcollege.edu</span></div>
                    <div class="info-row"><span class="info-label">Hours:</span><span class="info-val">Mon - Fri: 9 AM - 5 PM</span></div>
                </div>
    
                <div class="modern-card">
                    <div class="card-title">📍 Campus Address</div>
                    <div style="font-size:0.88rem; color:#334155; line-height:1.6;">
                        <strong>VR College of Engineering</strong><br>
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
    # Full-Width Conversational Interface (90-95% Centered Viewport)
    # =========================================================
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
    
    # Render Conversation Messages (ChatGPT Style)
    last_user_query = ""
    for idx, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            last_user_query = msg["content"]
            with st.chat_message("user", avatar="🧑‍🎓"):
                st.markdown(f'<div class="chat-user-text">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            with st.chat_message("assistant", avatar="🤖"):
                meta = msg.get("meta") or {}
                visual = meta.get("visual") or {}
                img_name = visual.get("image") or "campus_main.jpg"
                img_caption = visual.get("caption") or "🏛️ VR College of Engineering Campus"
                img_full_path = os.path.join(ASSETS_DIR, img_name)
    
                # Diagnostics & Metadata
                status = meta.get("status")
                cat = meta.get("category")
                conf = meta.get("confidence", 0.0)
                matched_q = meta.get("matched_question")
                is_fuzzy = meta.get("is_fuzzy", False)
                ai_gen = meta.get("ai_generated", False)
    
                # Writing Block Header (ChatGPT Writing Block UI)
                heading_title, heading_icon = get_answer_heading_and_icon(
                    cat, matched_q, msg["content"],
                    language=st.session_state.get("selected_language", "English")
                )
                subtitle_text = "வி.ஆர் பொறியியல் கல்லூரி • சரிபார்க்கப்பட்ட AI தகவல்" if is_tamil_ui else "VR College of Engineering • Verified AI Advisory"
                st.markdown(f"""
                <div class="ai-wb-header">
                    <div class="ai-wb-title-group">
                        <span class="ai-wb-icon">{heading_icon}</span>
                        <div>
                            <div class="ai-wb-heading">{heading_title}</div>
                            <div class="ai-wb-subtitle">{subtitle_text}</div>
                        </div>
                    </div>
                    <div class="ai-wb-badge-group">
                        <span class="ai-wb-badge">✨ Writing Block</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
                meta_html = ""
                if ai_gen:
                    meta_html += '<span class="ai-pill">✨ Gemini AI Generated</span> '
                if cat and cat not in ["Greeting", "Gratitude", "Farewell"]:
                    meta_html += f'<span class="category-pill">📂 Category: {cat}</span> '
                if status == "matched":
                    meta_html += f'<span class="confidence-pill">🎯 Grounded: {int(conf * 100)}%</span> '
                    if is_fuzzy:
                        meta_html += '<span class="fuzzy-pill">⚡ Auto-Corrected / Typo Resilient</span> '
                    if matched_q and not ai_gen:
                        meta_html += f'<div class="matched-prompt-hint">💡 Matched FAQ: <em>"{matched_q}"</em></div>'
                elif status == "fallback":
                    meta_html += f'<span class="fallback-pill">💡 Guided Campus Advisory</span>'
                elif status in ["greeting", "gratitude", "farewell"]:
                    meta_html += f'<span class="confidence-pill">⚡ Instant {status.capitalize()}</span>'
    
                # Related Campus Picture Banner (1:3 vertical-to-horizontal aesthetic ratio)
                if os.path.exists(img_full_path):
                    try:
                        with open(img_full_path, "rb") as f_img:
                            img_b64 = base64.b64encode(f_img.read()).decode("utf-8")
                        st.markdown(
                            f'''
                            <div style="margin-bottom: 16px; border-radius: 14px; overflow: hidden; border: 1.5px solid #BAE6FD; box-shadow: 0 4px 16px rgba(14, 116, 144, 0.08);">
                                <img src="data:image/jpeg;base64,{img_b64}" alt="{img_caption}" style="width: 100%; max-height: 230px; object-fit: cover; display: block;" />
                                <div style="background: rgba(240, 249, 255, 0.95); padding: 6px 14px; font-size: 12px; font-weight: 600; color: #0369A1; border-top: 1px solid #E0F2FE;">
                                    📷 {img_caption}
                                </div>
                            </div>
                            ''',
                            unsafe_allow_html=True
                        )
                    except Exception:
                        st.image(img_full_path, caption=img_caption, use_container_width=True)
    
                # Full-Width Markdown Content (Tables, Headings, Lists span 100% of answer container)
                st.markdown(msg["content"])
                if meta_html:
                    st.markdown(meta_html, unsafe_allow_html=True)
    
                # Interactive Action Bar: 📋 Copy Answer, 🔊 Listen, 🔄 Regenerate, 👍/👎 Feedback
                if msg.get("content"):
                    clean_answer_text = msg["content"].replace("[DEMO DATA]", "").strip()
                    clean_text_for_js = json.dumps(clean_answer_text)
                    copy_lbl = "பதிலை நகலெடு" if is_tamil_ui else "Copy Answer"
                    tts_lbl = "கேளுங்கள்" if is_tamil_ui else "Listen"
                    copied_lbl = "நகலெடுக்கப்பட்டது!" if is_tamil_ui else "Copied!"

                    copy_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                    <meta charset="utf-8">
                    <style>
                    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
                    body {{ background: transparent; display: flex; align-items: center; height: 100%; overflow: hidden; }}
                    .btn-group {{ display: flex; align-items: center; gap: 8px; }}
                    .act-btn {{
                        display: inline-flex;
                        align-items: center;
                        gap: 6px;
                        background: #F0F9FF;
                        border: 1.2px solid #BAE6FD;
                        color: #0369A1;
                        font-size: 11.5px;
                        font-weight: 600;
                        padding: 5px 12px;
                        border-radius: 8px;
                        cursor: pointer;
                        transition: all 0.2s ease;
                        outline: none;
                        user-select: none;
                        white-space: nowrap;
                    }}
                    .act-btn:hover {{
                        background: #E0F2FE;
                        border-color: #38BDF8;
                        color: #0284C7;
                        transform: translateY(-1px);
                        box-shadow: 0 2px 6px rgba(14, 116, 144, 0.12);
                    }}
                    .act-btn:active {{
                        transform: translateY(0);
                    }}
                    .copied {{
                        background: #ECFDF5 !important;
                        border-color: #6EE7B7 !important;
                        color: #047857 !important;
                    }}
                    </style>
                    </head>
                    <body>
                    <div class="btn-group">
                        <button id="copy-btn" class="act-btn" onclick="doCopy()">
                            📋 <span>{copy_lbl}</span>
                        </button>
                        <button id="tts-btn" class="act-btn" onclick="doTTS()">
                            🔊 <span>{tts_lbl}</span>
                        </button>
                    </div>
                    <script>
                    const answerText = {clean_text_for_js};
    
                    function doCopy() {{
                        function success() {{
                            const btn = document.getElementById('copy-btn');
                            btn.classList.add('copied');
                            btn.innerHTML = '✅ <span>{copied_lbl}</span>';
                            setTimeout(() => {{
                                btn.classList.remove('copied');
                                btn.innerHTML = '📋 <span>{copy_lbl}</span>';
                            }}, 2200);
                        }}
    
                        if (navigator.clipboard && window.isSecureContext) {{
                            navigator.clipboard.writeText(answerText).then(success).catch(() => fallbackCopy(answerText, success));
                        }} else {{
                            fallbackCopy(answerText, success);
                        }}
                    }}
    
                    function fallbackCopy(text, cb) {{
                        const ta = document.createElement('textarea');
                        ta.value = text;
                        ta.style.position = 'fixed';
                        ta.style.left = '-9999px';
                        ta.style.top = '-9999px';
                        document.body.appendChild(ta);
                        ta.focus();
                        ta.select();
                        try {{
                            const ok = document.execCommand('copy');
                            if (ok) cb();
                        }} catch (e) {{
                            console.error(e);
                        }}
                        document.body.removeChild(ta);
                    }}
    
                    function doTTS() {{
                        try {{
                            window.speechSynthesis.cancel();
                            const u = new SpeechSynthesisUtterance(answerText);
                            u.rate = 1.0;
                            window.speechSynthesis.speak(u);
                        }} catch(e) {{
                            console.error(e);
                        }}
                    }}
                    </script>
                    </body>
                    </html>
                    """
    
                    st.markdown("<div style='margin-top:14px; margin-bottom:4px;'></div>", unsafe_allow_html=True)
                    if idx == 0:
                        col_act_left, col_act_regen = st.columns([3.8, 1.8], gap="small")
                        with col_act_left:
                            components.html(copy_html, height=34)
                        with col_act_regen:
                            regen_welcome_lbl = "🔄 மீண்டும் உருவாக்கு" if is_tamil_ui else "🔄 Regenerate"
                            if st.button(regen_welcome_lbl, key=f"regen_{idx}", help="Refresh initial welcome guidance", use_container_width=True):
                                st.session_state.messages = get_initial_messages()
                                st.rerun()
                    else:
                        prev_user_q = ""
                        target_user_idx = None
                        for p_i in range(idx - 1, -1, -1):
                            if st.session_state.messages[p_i]["role"] == "user":
                                prev_user_q = st.session_state.messages[p_i]["content"]
                                target_user_idx = p_i
                                break
    
                        col_act_left, col_act_regen, col_act_up, col_act_down = st.columns([3.6, 2.0, 0.7, 0.7], gap="small")
                        with col_act_left:
                            components.html(copy_html, height=34)
                        with col_act_regen:
                            regen_ans_lbl = "🔄 மீண்டும் உருவாக்கு" if is_tamil_ui else "🔄 Regenerate"
                            if st.button(regen_ans_lbl, key=f"regen_{idx}", help="Regenerate this answer", use_container_width=True):
                                if target_user_idx is not None and prev_user_q:
                                    st.session_state.messages = st.session_state.messages[:target_user_idx]
                                    st.session_state["regenerate_query"] = prev_user_q
                                    current_conv_id = st.session_state.get("current_conversation_id")
                                    if current_conv_id:
                                        try:
                                            conn = get_connection()
                                            cur = conn.cursor()
                                            cur.execute(
                                                "DELETE FROM messages WHERE conversation_id = ? AND id >= (SELECT id FROM messages WHERE conversation_id = ? AND role = 'user' AND content = ? ORDER BY id DESC LIMIT 1);",
                                                (current_conv_id, current_conv_id, prev_user_q)
                                            )
                                            conn.commit()
                                            conn.close()
                                        except Exception:
                                            pass
                                    st.rerun()
                                else:
                                    st.rerun()
                        with col_act_up:
                            if st.button("👍", key=f"fb_up_{idx}", help="Helpful response", use_container_width=True):
                                log_feedback(query=last_user_query, answer=msg["content"], rating="positive")
                                st.toast("Thank you for your feedback! 👍")
                        with col_act_down:
                            if st.button("👎", key=f"fb_down_{idx}", help="Needs improvement", use_container_width=True):
                                log_feedback(query=last_user_query, answer=msg["content"], rating="negative")
                                st.toast("Feedback noted! Our counseling desk will review this. 👎")
    
                # Contextual Interactive Suggestion Chips (Prompt Requirement: Interactive quick-response cards)
                if idx == len(st.session_state.messages) - 1:
                    cat_id_hint = meta.get("category_id") or meta.get("category")
                    context_chips = get_contextual_chips(last_user_query, cat_id_hint)
                    st.markdown("<div style='margin-top:10px; margin-bottom:4px; font-size:0.78rem; color:#64748B; font-weight:600;'>💡 Interactive Suggestions (Click to Ask):</div>", unsafe_allow_html=True)
                    chip_cols = st.columns(len(context_chips))
                    for c_i, (chip_label, chip_query) in enumerate(context_chips):
                        with chip_cols[c_i]:
                            if st.button(chip_label, key=f"chip_dyn_{idx}_{c_i}", use_container_width=True):
                                clicked_query = chip_query
    
    # Suggested Starter Prompts (Show when chat has few messages)
    if len(st.session_state.messages) <= 2:
        st.markdown("<div style='margin-top: 10px; margin-bottom: 6px; font-size: 0.84rem; color: #64748B; font-weight: 600;'>💡 Try asking a question or follow-up:</div>", unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("🎓 What undergraduate courses are offered?", key="chip_c1", use_container_width=True):
                clicked_query = "What undergraduate courses are offered?"
            if st.button("💰 How much is the annual fee for B.Tech?", key="chip_c2", use_container_width=True):
                clicked_query = "How much is the annual tuition fee for B.Tech?"
        with col_s2:
            if st.button("🏢 Are hostel facilities available on campus?", key="chip_c3", use_container_width=True):
                clicked_query = "Are hostel facilities available for boys and girls?"
            if st.button("💼 What was the highest placement package?", key="chip_c4", use_container_width=True):
                clicked_query = "What was the highest and average salary package in recent placements?"
    
    # Campus Highlights Expander with Interactive Facility Cards
    with st.expander("📸 **Virtual Campus Tour & 15 Facility Showcases (Click to Explore)**", expanded=(len(st.session_state.messages) <= 2)):
        st.markdown(
            """
            <div style="font-size:0.83rem; color:#475569; margin-bottom:10px;">
                Browse our 15 key campus facilities. Click any card button to trigger an immediate conversational enquiry:
            </div>
            """,
            unsafe_allow_html=True
        )
        featured_cards = get_all_interactive_cards()
        # Display in 3 responsive columns
        c_p1, c_p2, c_p3 = st.columns(3)
        cols_list = [c_p1, c_p2, c_p3]
        for f_i, card_item in enumerate(featured_cards):
            target_col = cols_list[f_i % 3]
            c_img_path = os.path.join(ASSETS_DIR, card_item["image"])
            with target_col:
                with st.container():
                    st.markdown(
                        f"""
                        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:8px 10px; margin-bottom:4px;">
                            <div style="font-size:0.86rem; font-weight:700; color:#1E3A8A;">{card_item['title']}</div>
                            <div style="font-size:0.75rem; color:#475569; line-height:1.35; margin-top:2px;">{card_item['description'][:85]}...</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if os.path.exists(c_img_path):
                        st.image(c_img_path, caption=card_item["title"], use_container_width=True)
                    if st.button(f"👉 Enquire: {card_item['title'][:14]}..", key=f"tour_btn_{card_item['id']}_{f_i}", use_container_width=True):
                        clicked_query = card_item["quick_prompt"]
                    st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)
    
    # ---------------------------------------------------------
    # Premium AI & Voice Control Dock (Companion to Chat Input)
    # ---------------------------------------------------------
    components.html("""
    <script>
    function startVoiceInput() {
        var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert("Speech recognition is supported in Google Chrome, Microsoft Edge, and modern Web Speech browsers.");
            return;
        }
        var recognition = new SpeechRecognition();
        recognition.lang = 'en-IN';
        recognition.interimResults = false;
        var statusEl = document.getElementById('voice-status');
        var micBtn = document.getElementById('mic-btn');
        var pulseDot = document.getElementById('pulse-recording-dot');
        
        statusEl.innerHTML = "🎙️ <strong style='color:#2563EB;'>Listening...</strong> Speak your question clearly into your microphone.";
        if (micBtn) {
            micBtn.style.background = "linear-gradient(135deg, #DC2626 0%, #EF4444 100%)";
            micBtn.style.boxShadow = "0 0 16px rgba(239, 68, 68, 0.6)";
        }
        if (pulseDot) pulseDot.style.display = "inline-block";
        
        recognition.start();
    
        recognition.onresult = function(event) {
            var transcript = event.results[0][0].transcript;
            statusEl.innerHTML = "✅ Transcribed: <span style='color:#1D4ED8; font-weight:600;'>\\"" + transcript + "\\"</span> <span style='color:#64748B;'>(Copied to clipboard - paste into chat box)</span>";
            navigator.clipboard.writeText(transcript);
            resetMicBtn();
            
            try {
                var parentDoc = window.parent.document;
                var chatTextarea = parentDoc.querySelector('[data-testid="stChatInput"] textarea');
                if (chatTextarea) {
                    chatTextarea.value = transcript;
                    chatTextarea.dispatchEvent(new Event('input', { bubbles: true }));
                    chatTextarea.focus();
                }
            } catch(e) {}
        };
        recognition.onerror = function(event) {
            statusEl.innerHTML = "❌ <span style='color:#DC2626;'>Mic: " + event.error + ". Click to retry.</span>";
            resetMicBtn();
        };
        recognition.onend = function() {
            resetMicBtn();
        };
    
        function resetMicBtn() {
            if (micBtn) {
                micBtn.style.background = "linear-gradient(135deg, #2563EB 0%, #06B6D4 100%)";
                micBtn.style.boxShadow = "0 2px 10px rgba(37, 99, 235, 0.35)";
            }
            if (pulseDot) pulseDot.style.display = "none";
        }
    }
    </script>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700&display=swap');
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
    .dock-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(135deg, rgba(248, 250, 252, 0.95) 0%, rgba(239, 246, 255, 0.95) 100%);
        border: 1.5px solid #BFDBFE;
        border-radius: 14px;
        padding: 6px 12px;
        box-shadow: 0 2px 10px rgba(37, 99, 235, 0.08);
        gap: 10px;
        margin-bottom: 2px;
    }
    .left-badge {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 11.5px;
        font-weight: 700;
        color: #1E3A8A;
        letter-spacing: 0.2px;
        white-space: nowrap;
    }
    .ai-sparkle {
        font-size: 13px;
        filter: drop-shadow(0 0 5px rgba(6, 182, 212, 0.8));
    }
    .live-dot {
        width: 7px;
        height: 7px;
        background: #10B981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 6px #10B981;
        animation: pulseLive 2s infinite;
    }
    @keyframes pulseLive {
        0% { transform: scale(0.9); opacity: 0.7; }
        50% { transform: scale(1.2); opacity: 1; }
        100% { transform: scale(0.9); opacity: 0.7; }
    }
    .mic-btn {
        background: linear-gradient(135deg, #2563EB 0%, #06B6D4 100%);
        color: #FFFFFF;
        border: none;
        padding: 5px 12px;
        border-radius: 20px;
        cursor: pointer;
        font-weight: 600;
        font-size: 11.5px;
        display: flex;
        align-items: center;
        gap: 5px;
        transition: all 0.2s ease;
        box-shadow: 0 2px 10px rgba(37, 99, 235, 0.35);
        white-space: nowrap;
    }
    .mic-btn:hover {
        transform: translateY(-1px) scale(1.03);
        box-shadow: 0 0 14px rgba(37, 99, 235, 0.5), 0 0 22px rgba(6, 182, 212, 0.35);
    }
    .status-text {
        font-size: 11px;
        color: #64748B;
        flex: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    #pulse-recording-dot {
        width: 6px;
        height: 6px;
        background: #FFFFFF;
        border-radius: 50%;
        display: none;
        animation: pulseLive 1s infinite;
    }
    </style>
    <div class="dock-container">
        <div class="left-badge">
            <span class="ai-sparkle">✨</span>
            <span>VRBot AI Active</span>
            <span class="live-dot"></span>
        </div>
        <div class="status-text" id="voice-status">
            Speak or type below • Ask courses, fees, hostels, cutoffs
        </div>
        <button id="mic-btn" class="mic-btn" onclick="startVoiceInput()">
            🎙️ <span>Voice Enquiry</span>
            <span id="pulse-recording-dot"></span>
        </button>
    </div>
    """.replace(
        "<span>VRBot AI Active</span>",
        f"<span>{'VRBot AI தயார்' if is_tamil_ui else 'VRBot AI Active'}</span>"
    ).replace(
        "Speak or type below • Ask courses, fees, hostels, cutoffs",
        "பேசுங்கள் அல்லது தட்டச்சு செய்க • பாடப்பிரிவு, கட்டணம், விடுதி பற்றி கேளுங்கள்" if is_tamil_ui else "Speak or type below • Ask courses, fees, hostels, cutoffs"
    ).replace(
        "<span>Voice Enquiry</span>",
        f"<span>{'குரல் வழி விசாரணை' if is_tamil_ui else 'Voice Enquiry'}</span>"
    ), height=44)
    
    # Chat Input Box with Premium Glowing Styling & Updated Placeholder
    chat_placeholder = (
        "VRBot-யிடம் கேளுங்கள்... உங்கள் கல்லூரி AI உதவியாளர் உங்களுக்கு உதவ தயாராக உள்ளார்!"
        if is_tamil_ui
        else "Ask VRBot anything... Your college assistant is here to help!"
    )
    user_input = st.chat_input(chat_placeholder)
    
    # ---------------------------------------------------------
    # Handle Query Processing with Multi-Turn Context & Streaming
    # ---------------------------------------------------------
    active_query = clicked_query if clicked_query else user_input
    if not active_query and "regenerate_query" in st.session_state and st.session_state["regenerate_query"]:
        active_query = st.session_state.pop("regenerate_query")
    
    if active_query and chatbot_ready:
        current_conv_id = st.session_state.get("current_conversation_id")
        if not current_conv_id:
            current_conv_id = uuid.uuid4().hex[:10]
            st.session_state.current_conversation_id = current_conv_id
    
        # 1. Append user question to history and SQLite
        st.session_state.messages.append({
            "role": "user",
            "content": active_query,
            "meta": None
        })
        save_message(current_conv_id, "user", active_query, None)
        add_recent_search(active_query)
    
        # 2. Get intelligent, context-aware response from CollegeChatbot
        spinner_msg = "VRBot பதிலளிக்கிறது..." if is_tamil_ui else "VRBot is thinking..."
        with st.spinner(spinner_msg):
            res = chatbot.get_response(
                user_query=active_query,
                category_filter=selected_category,
                conversation_history=st.session_state.messages,
                api_key=active_api_key,
                language=st.session_state.get("selected_language", "English")
            )
    
        # 3. Prefer friendly, structured conversational response
        display_content = res.get("friendly_answer") or res.get("answer")
    
        # 4. Append bot response to history and SQLite
        st.session_state.messages.append({
            "role": "assistant",
            "content": display_content,
            "meta": res
        })
        save_message(current_conv_id, "assistant", display_content, res)
    
        # 5. Trigger UI update
        st.rerun()
    
    # ---------------------------------------------------------
    # Mini-Game: VR College Campus Trivia Challenge
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
            "question": "🏆 What is the institutional NAAC accreditation grade of VR College of Engineering?",
            "options": ["NAAC 'B' Grade", "NAAC 'A+' Grade", "Not Accredited", "Grade C"],
            "answer": "NAAC 'A+' Grade",
            "fact": "VR College of Engineering is proudly accredited with NAAC 'A+' Grade and approved by AICTE."
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
                        🎮 VR College Campus Trivia Challenge
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
                msg = "Incredible! You know VR College of Engineering inside out! You are 100% campus ready."
            elif final_score >= 3:
                badge_icon, badge_title = "🌟", "Campus Whiz! Well Done"
                msg = "Great performance! You know most of the essential college policies and facts."
            else:
                badge_icon, badge_title = "💡", "Good Effort! Fresh Explorer"
                msg = "Good try! Feel free to ask VRBot above to explore more about admissions, fees, and hostels."
    
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
        <strong>VR College of Engineering AI-Based College Enquiry Chatbot (VRBot)</strong> • Streamlit ChatGPT-Style Interface<br>
        Engineered with Natural Language Processing (TF-IDF & Fuzzy Typo Tolerance) & Google Gemini AI • Safe Academic Demonstration Data
    </div>
    """,
    unsafe_allow_html=True
)
