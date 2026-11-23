"""
College Admission Application Form Module for VR College of Engineering.

Provides a dedicated, professional admission application page:
- Collects 11 comprehensive student & academic fields
- Validates required inputs (Full name, DOB, Gender, Email, Phone, Parent Name, Address, Marks, Dept, Category, Course)
- Generates unique institutional application reference numbers (e.g. VRCE-APP-26-XXXXX)
- Persists records to applications.csv, leads.csv, and SQLite database
- Cleanly renders the green-and-white Success View using native HTML rendering without raw tags or markdown code blocks
- Provides Submit Application, Reset Form, and Back to Home navigation
"""

import os
import re
import datetime
import textwrap
import pandas as pd
import streamlit as st
from typing import Dict, Any, Optional

from lead_manager import save_admission_application


DEPARTMENTS_LIST = [
    "Select Department",
    "Computer Science & Engineering (CSE)",
    "Electronics & Communication Engineering (ECE)",
    "Electrical & Electronics Engineering (EEE)",
    "Mechanical Engineering",
    "Civil Engineering",
    "Information Technology (IT)",
    "Artificial Intelligence & Data Science (AI & DS)"
]

ADMISSION_CATEGORIES_LIST = [
    "Select Admission Category",
    "General Merit (State CET / Direct)",
    "Management Quota",
    "Sports Quota",
    "OBC / Reserved Category",
    "NRI / International Candidate"
]

COURSE_PREFERENCES_LIST = [
    "Select Course Preference",
    "B.Tech Regular (4-Year Undergraduate)",
    "B.Tech Lateral Entry (3-Year for Diploma Holders)",
    "M.Tech (2-Year Postgraduate)",
    "Master of Business Administration (MBA - 2 Years)",
    "Master of Computer Applications (MCA - 2 Years)"
]

GENDER_OPTIONS = [
    "Select Gender",
    "Male",
    "Female",
    "Other"
]


def clean_html_for_markdown(html_str: str) -> str:
    """
    Strips all leading and trailing whitespace from every line of HTML.
    This guarantees that no line has 4 or more leading spaces, completely
    preventing CommonMark parsers from treating HTML tags as indented code blocks (<pre><code>).
    """
    clean_lines = [line.strip() for line in html_str.strip().splitlines() if line.strip()]
    return "\n".join(clean_lines)


def render_html(html_str: str):
    """
    Renders trusted, application-generated HTML cleanly without CommonMark indentation escaping.
    Uses st.markdown(clean_html, unsafe_allow_html=True) exclusively for trusted application HTML,
    ensuring all tags are properly parsed and rendered as DOM components rather than raw code.
    """
    clean_html = clean_html_for_markdown(html_str)
    st.markdown(clean_html, unsafe_allow_html=True)


def reset_application_form_state():
    """Resets all form input fields and success state in session state."""
    keys_to_clear = [
        "app_student_name",
        "app_dob",
        "app_gender",
        "app_email",
        "app_phone",
        "app_parent_name",
        "app_address",
        "app_marks",
        "app_dept",
        "app_category",
        "app_course",
        "app_submission_success"
    ]
    for k in keys_to_clear:
        st.session_state.pop(k, None)


def translate_error_to_tamil(msg: str) -> str:
    """Translates validation error messages into Tamil if Tamil is selected."""
    err_map = {
        "Please enter student's valid full name (at least 2 characters).": "மாணவரின் சரியான முழுப் பெயரை உள்ளிடவும் (குறைந்தபட்சம் 2 எழுத்துக்கள்).",
        "Please enter or select a valid Date of Birth.": "சரியான பிறந்த தேதியைத் தேர்ந்தெடுக்கவும்.",
        "Please select student's gender.": "மாணவரின் பாலினத்தைத் தேர்ந்தெடுக்கவும்.",
        "Please enter a valid email address (e.g., student@example.com).": "சரியான மின்னஞ்சல் முகவரியை உள்ளிடவும் (எ.கா: student@example.com).",
        "Please enter a valid 10-digit mobile number.": "சரியான 10 இலக்க இந்திய கைபேசி எண்ணை உள்ளிடவும்.",
        "Please enter Parent / Guardian Name (at least 2 characters).": "பெற்றோர் அல்லது பாதுகாவலரின் பெயரை உள்ளிடவும்.",
        "Please enter complete residential address.": "முழுமையான குடியிருப்பு முகவரியை உள்ளிடவும்.",
        "Please enter 12th Standard / Diploma marks or percentage.": "12-ஆம் வகுப்பு அல்லது டிப்ளமோ கட்-ஆப் மதிப்பெண்களை உள்ளிடவும்.",
        "Please select a preferred department.": "விருப்பமான பொறியியல் துறையைத் தேர்ந்தெடுக்கவும்.",
        "Please select an admission category.": "சேர்க்கை ஒதுக்கீடு வகையைத் தேர்ந்தெடுக்கவும்.",
        "Please select an admission quota / category.": "சேர்க்கை ஒதுக்கீடு வகையைத் தேர்ந்தெடுக்கவும்.",
        "Please select a course preference.": "படிப்பு விருப்பத்தைத் தேர்ந்தெடுக்கவும்."
    }
    return err_map.get(msg, msg)


def render_admission_application_form():
    """
    Renders the dedicated, separate College Admission Application Form interface.
    Includes top navigation bar with breadcrumb, institutional branding, 3 structured
    sections for all 11 fields, form validation, and action buttons.
    Supports English and Tamil dynamically.
    """
    lang = st.session_state.get("selected_language", "English")
    is_tamil = (lang == "Tamil")

    # ---------------------------------------------------------
    # 1. Top Navigation Bar & Breadcrumb
    # ---------------------------------------------------------
    col_nav_back, col_nav_crumb = st.columns([1.2, 4.0], gap="medium")
    with col_nav_back:
        back_btn_lbl = "⬅️ முகப்புக்குத் திரும்பு" if is_tamil else "⬅️ Back to Home"
        if st.button(back_btn_lbl, key="app_form_top_back_btn", use_container_width=True, help="Return to VR College chatbot homepage"):
            st.session_state["show_admission_form"] = False
            st.session_state.pop("app_submission_success", None)
            if "page" in st.query_params:
                del st.query_params["page"]
            if "apply" in st.query_params:
                del st.query_params["apply"]
            st.rerun()

    with col_nav_crumb:
        if is_tamil:
            breadcrumb_html = """
            <div style="font-size:0.88rem; font-weight:700; color:#0E7490; padding-top:6px; display:flex; align-items:center; gap:8px;">
                <span>🏛️ வி.ஆர் பொறியியல் கல்லூரி</span>
                <span>&gt;</span>
                <span>சேர்க்கை அலுவலகம்</span>
                <span>&gt;</span>
                <span style="color:#0369A1; background:#E0F2FE; padding:2px 10px; border-radius:9999px; border:1px solid #BAE6FD;">
                    அதிகாரப்பூர்வ விண்ணப்பப் படிவம் (2026-27)
                </span>
            </div>
            """
        else:
            breadcrumb_html = """
            <div style="font-size:0.88rem; font-weight:700; color:#0E7490; padding-top:6px; display:flex; align-items:center; gap:8px;">
                <span>🏛️ VR College of Engineering</span>
                <span>&gt;</span>
                <span>Admissions Cell</span>
                <span>&gt;</span>
                <span style="color:#0369A1; background:#E0F2FE; padding:2px 10px; border-radius:9999px; border:1px solid #BAE6FD;">
                    Formal Application Form (2026-27)
                </span>
            </div>
            """
        render_html(breadcrumb_html)

    # ---------------------------------------------------------
    # 2. Institutional Branding Hero Banner
    # ---------------------------------------------------------
    if is_tamil:
        hero_banner_html = """
        <div style="background: linear-gradient(135deg, rgba(14, 116, 144, 0.96) 0%, rgba(30, 58, 138, 0.95) 100%);
                    padding: 24px 28px; border-radius: 18px; color: #FFFFFF; margin: 12px 0 20px 0;
                    box-shadow: 0 12px 28px rgba(14, 116, 144, 0.22); border: 1.5px solid #BAE6FD;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
                <div>
                    <div style="font-size:0.75rem; font-weight:800; letter-spacing:1px; text-transform:uppercase; color:#A5F3FC; margin-bottom:4px;">
                        சேர்க்கை அலுவலகம் & கல்வி விழிப்புணர்வு மையம் • கல்வியாண்டு 2026-2027
                    </div>
                    <h1 style="font-family:'Righteous', sans-serif; font-size:1.95rem; color:#FFFFFF; margin:0 0 6px 0; letter-spacing:0.5px;">
                        📝 கல்லூரி சேர்க்கை விண்ணப்பப் படிவம்
                    </h1>
                    <div style="font-size:0.90rem; color:#E0F2FE;">
                        வி.ஆர் பொறியியல் கல்லூரி • AICTE அங்கீகாரம் • NAAC 'A+' தரம் • நிறுவப்பட்டது 2005
                    </div>
                </div>
                <div style="background:rgba(255,255,255,0.15); border:1.5px solid rgba(255,255,255,0.3); border-radius:14px; padding:10px 18px; text-align:center;">
                    <div style="font-size:0.72rem; color:#A5F3FC; font-weight:700; text-transform:uppercase;">சேர்க்கை நிலை</div>
                    <div style="font-size:1.15rem; color:#FFFFFF; font-weight:800;">சேர்க்கை திறக்கப்பட்டுள்ளது</div>
                    <div style="font-size:0.72rem; color:#E2E8F0;">B.Tech / M.Tech / MBA / MCA</div>
                </div>
            </div>
        </div>
        """
    else:
        hero_banner_html = """
        <div style="background: linear-gradient(135deg, rgba(14, 116, 144, 0.96) 0%, rgba(30, 58, 138, 0.95) 100%);
                    padding: 24px 28px; border-radius: 18px; color: #FFFFFF; margin: 12px 0 20px 0;
                    box-shadow: 0 12px 28px rgba(14, 116, 144, 0.22); border: 1.5px solid #BAE6FD;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
                <div>
                    <div style="font-size:0.75rem; font-weight:800; letter-spacing:1px; text-transform:uppercase; color:#A5F3FC; margin-bottom:4px;">
                        OFFICE OF ADMISSIONS & ACADEMIC OUTREACH • SESSION 2026-2027
                    </div>
                    <h1 style="font-family:'Righteous', sans-serif; font-size:1.95rem; color:#FFFFFF; margin:0 0 6px 0; letter-spacing:0.5px;">
                        📝 College Admission Application Form
                    </h1>
                    <div style="font-size:0.90rem; color:#E0F2FE;">
                        VR College of Engineering • Approved by AICTE • Accredited NAAC 'A+' Grade • Estd. 2005
                    </div>
                </div>
                <div style="background:rgba(255,255,255,0.15); border:1.5px solid rgba(255,255,255,0.3); border-radius:14px; padding:10px 18px; text-align:center;">
                    <div style="font-size:0.72rem; color:#A5F3FC; font-weight:700; text-transform:uppercase;">Admission Status</div>
                    <div style="font-size:1.15rem; color:#FFFFFF; font-weight:800;">Admissions Open</div>
                    <div style="font-size:0.72rem; color:#E2E8F0;">B.Tech / M.Tech / MBA / MCA</div>
                </div>
            </div>
        </div>
        """
    render_html(hero_banner_html)

    # ---------------------------------------------------------
    # 3. Success View (Rendered after successful submission)
    # ---------------------------------------------------------
    if "app_submission_success" in st.session_state and st.session_state["app_submission_success"]:
        res_info = st.session_state["app_submission_success"]
        rec = res_info.get("data", {})
        ref_no = res_info.get("ref_no", "VRCE-APP-26-00000")

        # 1. Professional Green and White Success Card (Cleanly Rendered via render_html)
        success_card_html = f"""
        <div style="background: linear-gradient(135deg, #ECFDF5 0%, #FFFFFF 100%);
                    border: 2px solid #10B981;
                    border-radius: 18px;
                    padding: 26px 30px;
                    margin: 12px 0 20px 0;
                    box-shadow: 0 10px 25px rgba(16, 185, 129, 0.12);
                    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 12px;">
                <span style="font-size: 2.6rem; line-height: 1;">🎉</span>
                <div>
                    <h2 style="color: #065F46; margin: 0; font-size: 1.65rem; font-weight: 800; letter-spacing: -0.3px;">
                        Application Submitted Successfully!
                    </h2>
                    <p style="color: #047857; margin: 4px 0 0 0; font-size: 1.0rem; font-weight: 600;">
                        Your college admission application has been registered successfully.
                    </p>
                </div>
            </div>

            <hr style="border: none; border-top: 1.5px solid #D1FAE5; margin: 16px 0;" />

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin: 16px 0;">
                <div style="background: #FFFFFF; border: 2px solid #6EE7B7; border-left: 5px solid #059669; border-radius: 14px; padding: 14px 18px; box-shadow: 0 2px 8px rgba(16, 185, 129, 0.08);">
                    <div style="font-size: 0.78rem; font-weight: 800; color: #047857; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 4px;">
                        Application Reference Number:
                    </div>
                    <div style="font-size: 1.55rem; font-weight: 900; color: #065F46; font-family: monospace; letter-spacing: 1.2px;">
                        {ref_no}
                    </div>
                </div>

                <div style="background: #FFFFFF; border: 2px solid #6EE7B7; border-left: 5px solid #10B981; border-radius: 14px; padding: 14px 18px; box-shadow: 0 2px 8px rgba(16, 185, 129, 0.08);">
                    <div style="font-size: 0.78rem; font-weight: 800; color: #047857; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 4px;">
                        Application Status:
                    </div>
                    <div style="font-size: 1.02rem; font-weight: 800; color: #047857; display: flex; align-items: center; gap: 8px;">
                        <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #10B981;"></span>
                        Application Registered – Pending Counselor Review.
                    </div>
                </div>
            </div>

            <div style="background: #F0FDF4; border: 1.5px solid #A7F3D0; border-radius: 14px; padding: 16px 20px; margin-top: 16px;">
                <div style="font-size: 0.98rem; font-weight: 800; color: #065F46; margin-bottom: 8px;">
                    📌 Next Steps:
                </div>
                <ul style="margin: 0; padding-left: 20px; color: #1E293B; font-size: 0.92rem; line-height: 1.75;">
                    <li>Our Admissions Counselling Officer will verify your academic details.</li>
                    <li>Your application confirmation will be provided through the appropriate confirmation channel.</li>
                    <li>Please keep your application reference number for future communication.</li>
                </ul>
            </div>
        </div>
        """
        render_html(success_card_html)

        # 2. Easy-to-Copy Reference Number Box (using Streamlit native code element with 1-click copy)
        st.caption("📋 **Quick Copy:** Click the copy button below to copy your Application Reference Number to clipboard:")
        st.code(ref_no, language="")

        # 3. Application Summary Table
        st.markdown("#### 📋 **Application Summary Details**")
        summary_df = pd.DataFrame({
            "Application Parameter": [
                "Application Reference No.",
                "Submission Timestamp",
                "Student Full Name",
                "Date of Birth",
                "Gender",
                "Email Address",
                "Mobile Number",
                "Parent / Guardian Name",
                "Residential Address",
                "12th Standard / Diploma Marks",
                "Preferred Department",
                "Admission Category",
                "Course Preference",
                "Application Status"
            ],
            "Registered Details": [
                ref_no,
                rec.get("timestamp", ""),
                rec.get("student_name", ""),
                rec.get("dob", ""),
                rec.get("gender", ""),
                rec.get("email", ""),
                rec.get("phone", ""),
                rec.get("parent_name", ""),
                rec.get("address", ""),
                rec.get("marks_12th", ""),
                rec.get("department", ""),
                rec.get("admission_category", ""),
                rec.get("course_preference", ""),
                "Application Registered – Pending Counselor Review"
            ]
        })
        st.table(summary_df)

        # 4. Action Buttons Bar
        col_act1, col_act2, col_act3 = st.columns([1.6, 1.4, 1.4], gap="medium")
        with col_act1:
            confirmation_text = (
                f"========================================================\n"
                f"  VR COLLEGE OF ENGINEERING - ADMISSIONS PORTAL 2026\n"
                f"       APPLICATION CONFIRMATION ACKNOWLEDGEMENT\n"
                f"========================================================\n\n"
                f"🎉 APPLICATION SUBMITTED SUCCESSFULLY!\n\n"
                f"Your college admission application has been registered successfully.\n\n"
                f"Application Reference Number : {ref_no}\n"
                f"Application Status           : Application Registered – Pending Counselor Review.\n"
                f"Submission Timestamp         : {rec.get('timestamp', '')}\n\n"
                f"--- CANDIDATE DETAILS ---\n"
                f"Student Full Name            : {rec.get('student_name', '')}\n"
                f"Date of Birth                : {rec.get('dob', '')}\n"
                f"Gender                       : {rec.get('gender', '')}\n"
                f"Email Address                : {rec.get('email', '')}\n"
                f"Mobile Number                : {rec.get('phone', '')}\n"
                f"Parent / Guardian Name       : {rec.get('parent_name', '')}\n"
                f"Residential Address          : {rec.get('address', '')}\n\n"
                f"--- ACADEMIC PREFERENCES ---\n"
                f"12th Standard / Diploma Marks: {rec.get('marks_12th', '')}\n"
                f"Preferred Department         : {rec.get('department', '')}\n"
                f"Admission Category           : {rec.get('admission_category', '')}\n"
                f"Course Preference            : {rec.get('course_preference', '')}\n\n"
                f"--- NEXT STEPS ---\n"
                f"1. Our Admissions Counselling Officer will verify your academic details.\n"
                f"2. Your application confirmation will be provided through the appropriate confirmation channel.\n"
                f"3. Please keep your application reference number for future communication.\n\n"
                f"Admissions Office Helpline   : +91 98765 43210 / 0123-456789\n"
                f"Email                        : admissions@vrcollege.edu\n"
                f"Campus Location              : Knowledge Campus, Sector 4, Education City, Pincode: 560001\n"
                f"========================================================\n"
            )
            st.download_button(
                "📥 Download Application Confirmation",
                data=confirmation_text,
                file_name=f"VR_College_Application_Confirmation_{ref_no}.txt",
                mime="text/plain",
                use_container_width=True,
                type="primary",
                help="Download official application confirmation text document"
            )

        with col_act2:
            if st.button("📝 Submit Another Application", key="btn_submit_another", use_container_width=True):
                reset_application_form_state()
                st.rerun()

        with col_act3:
            if st.button("⬅️ Back to Home", key="btn_back_home_succ", use_container_width=True, help="Return to the chatbot homepage"):
                st.session_state["show_admission_form"] = False
                reset_application_form_state()
                if "page" in st.query_params:
                    del st.query_params["page"]
                if "apply" in st.query_params:
                    del st.query_params["apply"]
                st.rerun()

        return

    # ---------------------------------------------------------
    # 4. Application Form Fields (Grouped in 3 Institutional Cards)
    # ---------------------------------------------------------
    if is_tamil:
        info_note_html = """
        <div style="font-size:0.86rem; color:#475569; margin-bottom:14px; background:#F0F9FF; border:1px solid #BAE6FD; padding:10px 16px; border-radius:12px;">
            ℹ️ நட்சத்திரக் குறியீடு (<span style="color:#EF4444; font-weight:700;">*</span>) இடப்பட்ட அனைத்துப் புலங்களும் கட்டாயமானவை.
            உங்கள் விண்ணப்பம் இட ஒதுக்கீடு மற்றும் தகுதி உதவித்தொகை பரிசீலனைக்காக சேர்க்கை ஆலோசனை பிரிவால் செயலாக்கப்படும்.
        </div>
        """
    else:
        info_note_html = """
        <div style="font-size:0.86rem; color:#475569; margin-bottom:14px; background:#F0F9FF; border:1px solid #BAE6FD; padding:10px 16px; border-radius:12px;">
            ℹ️ All fields marked with an asterisk (<span style="color:#EF4444; font-weight:700;">*</span>) are required.
            Your application will be processed by the Admissions Counseling Cell for seat allocation and merit scholarship consideration.
        </div>
        """
    render_html(info_note_html)

    # ---------------------------------------------------------
    # Card 1: Personal Information
    # ---------------------------------------------------------
    c1_title = "👤 மாணவர் தனிநபர் விவரங்கள் (Student Personal Information)" if is_tamil else "👤 Student Personal Information"
    c1_header_html = f"""
    <div style="display:flex; align-items:center; gap:8px; font-size:1.05rem; font-weight:800; color:#0C4A6E; margin-bottom:14px;">
        <span style="background:#E0F2FE; color:#0369A1; padding:3px 9px; border-radius:50%; font-size:0.85rem; font-weight:800;">1</span>
        <span>{c1_title}</span>
    </div>
    """

    with st.container(border=True):
        render_html(c1_header_html)
        col_p1, col_p2, col_p3 = st.columns([2.0, 1.2, 1.2], gap="medium")
        with col_p1:
            s_name = st.text_input(
                "மாணவர் முழுப் பெயர் *" if is_tamil else "Student Full Name *",
                key="app_student_name",
                placeholder="e.g. Anand Kumar",
                help="Candidate's complete legal name as per 10th/12th marksheet"
            )
        with col_p2:
            default_dob = datetime.date(2008, 1, 1)
            s_dob = st.date_input(
                "பிறந்த தேதி *" if is_tamil else "Date of Birth *",
                key="app_dob",
                value=default_dob,
                min_value=datetime.date(1970, 1, 1),
                max_value=datetime.date(2012, 12, 31),
                help="Candidate's Date of Birth"
            )
        with col_p3:
            s_gender = st.selectbox(
                "பாலினம் *" if is_tamil else "Gender *",
                GENDER_OPTIONS,
                key="app_gender",
                help="Candidate's gender for records and hostel allotment"
            )

    # ---------------------------------------------------------
    # Card 2: Contact & Guardian Details
    # ---------------------------------------------------------
    c2_title = "📞 தொடர்பு மற்றும் பெற்றோர் விவரங்கள் (Contact & Guardian Details)" if is_tamil else "📞 Contact & Guardian Details"
    c2_header_html = f"""
    <div style="display:flex; align-items:center; gap:8px; font-size:1.05rem; font-weight:800; color:#0C4A6E; margin-bottom:14px;">
        <span style="background:#E0F2FE; color:#0369A1; padding:3px 9px; border-radius:50%; font-size:0.85rem; font-weight:800;">2</span>
        <span>{c2_title}</span>
    </div>
    """

    with st.container(border=True):
        render_html(c2_header_html)
        col_c1, col_c2 = st.columns([1.0, 1.0], gap="medium")
        with col_c1:
            s_email = st.text_input(
                "மின்னஞ்சல் முகவரி *" if is_tamil else "Email Address *",
                key="app_email",
                placeholder="e.g. anand.kumar@gmail.com",
                help="Official communication, admission updates, and seat allotment letters will be sent to this email"
            )
            s_phone = st.text_input(
                "கைபேசி எண் (WhatsApp) *" if is_tamil else "Mobile Number (WhatsApp) *",
                key="app_phone",
                placeholder="e.g. 9876543210",
                help="10-digit primary mobile contact number"
            )
        with col_c2:
            s_parent = st.text_input(
                "பெற்றோர் / பாதுகாவலர் பெயர் *" if is_tamil else "Parent / Guardian Name *",
                key="app_parent_name",
                placeholder="e.g. Ramesh Kumar (Father / Mother / Guardian)",
                help="Full name of parent or legal guardian"
            )
            s_address = st.text_area(
                "குடியிருப்பு முகவரி *" if is_tamil else "Residential Address *",
                key="app_address",
                placeholder="House/Flat No., Street, City, District, State, Pincode",
                height=70,
                help="Permanent residential address for institutional postal correspondence"
            )

    # ---------------------------------------------------------
    # Card 3: Academic & Department Preferences
    # ---------------------------------------------------------
    c3_title = "🎓 கல்வித் தகுதி மற்றும் விருப்பப் பாடப்பிரிவு (Academic & Department Preferences)" if is_tamil else "🎓 Academic & Department Preferences"
    c3_header_html = f"""
    <div style="display:flex; align-items:center; gap:8px; font-size:1.05rem; font-weight:800; color:#0C4A6E; margin-bottom:14px;">
        <span style="background:#E0F2FE; color:#0369A1; padding:3px 9px; border-radius:50%; font-size:0.85rem; font-weight:800;">3</span>
        <span>{c3_title}</span>
    </div>
    """

    with st.container(border=True):
        render_html(c3_header_html)
        col_a1, col_a2 = st.columns([1.0, 1.0], gap="medium")
        with col_a1:
            s_marks = st.text_input(
                "12-ஆம் வகுப்பு / டிப்ளமோ மதிப்பெண் *" if is_tamil else "12th Standard / Diploma Marks *",
                key="app_marks",
                placeholder="e.g. 92.5%, 185 / 200, or Cutoff Score",
                help="Aggregate percentage or cutoff score in 10+2 / Diploma"
            )
            s_dept = st.selectbox(
                "விருப்பமான பொறியியல் துறை *" if is_tamil else "Preferred Department *",
                DEPARTMENTS_LIST,
                key="app_dept",
                help="Primary engineering branch choice (CSE, ECE, EEE, Mechanical, Civil, IT, AI & DS)"
            )
        with col_a2:
            s_category = st.selectbox(
                "சேர்க்கை ஒதுக்கீடு வகை *" if is_tamil else "Admission Category *",
                ADMISSION_CATEGORIES_LIST,
                key="app_category",
                help="Select quota category for fee concessions, reservation, and merit verification"
            )
            s_course = st.selectbox(
                "படிப்பு விருப்பம் *" if is_tamil else "Course Preference *",
                COURSE_PREFERENCES_LIST,
                key="app_course",
                help="Select program duration and level (B.Tech Regular, Lateral Entry, M.Tech, MBA, MCA)"
            )

    # ---------------------------------------------------------
    # Institutional Declaration Note
    # ---------------------------------------------------------
    if is_tamil:
        declaration_html = """
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:12px 18px; font-size:0.82rem; color:#64748B; margin-bottom:20px; line-height:1.5;">
            🔒 <strong>நிறுவன உறுதிமொழி:</strong> இந்த விண்ணப்பத்தில் அளிக்கப்பட்டுள்ள அனைத்து விவரங்களும் உண்மையானவை என்று உறுதியளிக்கிறேன்.
        </div>
        """
    else:
        declaration_html = """
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:12px 18px; font-size:0.82rem; color:#64748B; margin-bottom:20px; line-height:1.5;">
            🔒 <strong>Institutional Declaration:</strong> I hereby declare that all details furnished in this application are authentic and true. I understand that seat allocation is subject to document verification and institutional merit eligibility.
        </div>
        """
    render_html(declaration_html)

    # ---------------------------------------------------------
    # 5. Action Buttons: Submit Application, Reset Form, Back to Home
    # ---------------------------------------------------------
    col_sub, col_res, col_bck = st.columns([2.0, 1.2, 1.2], gap="medium")

    with col_sub:
        btn_submit_lbl = "🚀 விண்ணப்பத்தைச் சமர்ப்பிக்கவும்" if is_tamil else "🚀 Submit Application"
        btn_submit = st.button(btn_submit_lbl, key="app_form_submit_btn", type="primary", use_container_width=True)

    with col_res:
        btn_reset_lbl = "🔄 படிவத்தை மீட்டமை" if is_tamil else "🔄 Reset Form"
        btn_reset = st.button(btn_reset_lbl, key="app_form_reset_btn", use_container_width=True, help="Clear all fields and reset form")

    with col_bck:
        btn_back_lbl = "⬅️ முகப்புக்குத் திரும்பு" if is_tamil else "⬅️ Back to Home"
        btn_back = st.button(btn_back_lbl, key="app_form_back_btn", use_container_width=True, help="Return to the chatbot homepage")

    # Handle Back to Home
    if btn_back:
        st.session_state["show_admission_form"] = False
        st.session_state.pop("app_submission_success", None)
        if "page" in st.query_params:
            del st.query_params["page"]
        if "apply" in st.query_params:
            del st.query_params["apply"]
        st.rerun()

    # Handle Reset Form
    if btn_reset:
        reset_application_form_state()
        rst_msg = "படிவம் மீட்டமைக்கப்பட்டது." if is_tamil else "Form fields have been reset."
        st.toast(rst_msg, icon="🔄")
        st.rerun()

    # Handle Submit Application
    if btn_submit:
        result = save_admission_application(
            student_name=s_name,
            dob=str(s_dob),
            gender=s_gender,
            email=s_email,
            phone=s_phone,
            parent_name=s_parent,
            address=s_address,
            marks_12th=s_marks,
            department=s_dept,
            admission_category=s_category,
            course_preference=s_course
        )
        if result["status"] == "success":
            st.session_state["app_submission_success"] = result
            st.balloons()
            st.rerun()
        else:
            err_msg = translate_error_to_tamil(result["message"]) if is_tamil else result["message"]
            st.error(f"⚠️ {err_msg}")
