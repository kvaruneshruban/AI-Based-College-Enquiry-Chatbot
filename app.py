"""
AI-Based College Enquiry Chatbot - Streamlit User Interface.

A modern, responsive, and intuitive web interface designed with a professional
blue-and-white theme for college enquiry handling.
"""

import os
import streamlit as st
import pandas as pd
from data_loader import load_faq_data, get_categories, get_questions_by_category, DataLoaderError
from chatbot import CollegeChatbot

# Configure Streamlit page settings
st.set_page_config(
    page_title="AI College Enquiry Chatbot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern Blue-and-White Theme & Chat Styling
st.markdown("""
<style>
    /* Theme Variables & Font Setup */
    :root {
        --primary-blue: #1A56DB;
        --secondary-blue: #3B82F6;
        --light-blue-bg: #EFF6FF;
        --accent-blue: #2563EB;
        --navy-dark: #0F172A;
        --border-color: #E2E8F0;
        --chat-user-bg: #E0E7FF;
        --chat-bot-bg: #F8FAFC;
    }

    /* Overall Header Styling */
    .main-header {
        background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
        padding: 24px 30px;
        border-radius: 12px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 14px rgba(30, 64, 175, 0.15);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        color: #FFFFFF !important;
        letter-spacing: -0.5px;
    }
    .main-header p {
        margin: 8px 0 0 0;
        font-size: 1.05rem;
        color: #DBEAFE;
    }
    .demo-badge {
        display: inline-block;
        background-color: #FEF3C7;
        color: #92400E;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 9999px;
        margin-left: 12px;
        vertical-align: middle;
        border: 1px solid #FCD34D;
    }

    /* Metric & Card Boxes */
    .info-card {
        background-color: #FFFFFF;
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* Category Pill styling */
    .category-tag {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 600;
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 2px 8px;
        border-radius: 6px;
        margin-top: 4px;
    }

    .confidence-tag {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 600;
        background-color: #DCFCE7;
        color: #166534;
        padding: 2px 8px;
        border-radius: 6px;
        margin-left: 6px;
    }

    .fallback-tag {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 600;
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 2px 8px;
        border-radius: 6px;
        margin-left: 6px;
    }

    /* Footer styling */
    .app-footer {
        text-align: center;
        padding: 20px 0;
        margin-top: 40px;
        border-top: 1px solid #E2E8F0;
        color: #64748B;
        font-size: 0.88rem;
    }
</style>
""", unsafe_allow_html=True)

# Dataset path
DATASET_PATH = os.path.join(os.path.dirname(__file__), "college_faq.csv")
LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo.png")

# Initialize Chatbot and Cache in Session State
@st.cache_resource
def get_initialized_chatbot(csv_path: str):
    """Loads dataset and prepares the chatbot instance."""
    df = load_faq_data(csv_path)
    bot = CollegeChatbot(faq_df=df, similarity_threshold=0.25)
    return bot, df

# Load backend
chatbot_ready = False
try:
    chatbot, faq_df = get_initialized_chatbot(DATASET_PATH)
    chatbot_ready = True
except DataLoaderError as e:
    st.error(f"⚠️ Dataset Initialization Error: {str(e)}")
    st.info("Please verify that 'college_faq.csv' exists in the project root with the correct columns.")
except Exception as e:
    st.error(f"⚠️ Unexpected Error loading chatbot: {str(e)}")

# Initialize session state for messages and active query
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! 🎓 Welcome to the **College Enquiry Chatbot**.\n\n"
                "I can help you with information about **Courses, Admissions, Fees, "
                "Hostel Facilities, Placements, Library, and Contact Details**.\n\n"
                "*All answers currently represent demonstration data.* How may I assist you today?"
            ),
            "meta": None
        }
    ]

# Sidebar implementation
with st.sidebar:
    # Logo / College Branding
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    else:
        st.markdown("### 🎓 **Apex Engineering College**")

    st.markdown("---")
    st.markdown("### ⚙️ **Enquiry Controls**")

    # Category Filter
    if chatbot_ready:
        categories = ["All Categories"] + get_categories(faq_df)
        selected_category = st.selectbox(
            "📂 Filter by Topic / Category:",
            categories,
            index=0,
            help="Filter knowledge retrieval to a specific college department or topic."
        )

        # Similarity Threshold Slider
        threshold = st.slider(
            "🎯 Match Confidence Threshold:",
            min_value=0.10,
            max_value=0.80,
            value=0.25,
            step=0.05,
            help="Higher values demand closer match to FAQ questions. Lower values are more permissive."
        )
        chatbot.set_threshold(threshold)

        st.markdown("---")
        st.markdown("### 📊 **Knowledge Base Stats**")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.metric("Total FAQs", len(faq_df))
        with col_s2:
            st.metric("Categories", len(categories) - 1)

        st.caption(f"Active Threshold: **{threshold:.2f}**")
        st.caption("Algorithm: **TF-IDF + Cosine Similarity**")

    st.markdown("---")
    # Action buttons: Clear & Download Chat History
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Chat history cleared. How can I help you today?",
                    "meta": None
                }
            ]
            st.rerun()
    with col_b2:
        # Format chat transcript for download
        transcript = "\n\n".join([
            f"{'Student' if m['role'] == 'user' else 'College Bot'}: {m['content']}"
            for m in st.session_state.messages
        ])
        st.download_button(
            "📥 Save Chat",
            data=transcript,
            file_name="college_chat_transcript.txt",
            mime="text/plain",
            use_container_width=True
        )

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size: 0.8rem; color: #64748B;">
        <strong>Project:</strong> AI-Based College Enquiry Chatbot<br>
        <strong>Architecture:</strong> Python, NLP, Streamlit<br>
        <strong>Mode:</strong> Demonstration (Demo Data)
        </div>
        """,
        unsafe_allow_html=True
    )

# Main Page Header
st.markdown(
    """
    <div class="main-header">
        <h1>🎓 AI-Based College Enquiry Chatbot <span class="demo-badge">DEMO DATA</span></h1>
        <p>Ask questions in natural language regarding courses, admissions, hostel, fees, exams, and placements.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Suggested Questions Section
st.markdown("##### 💡 **Quick Suggested Questions (Click to Ask):**")
suggested_queries = [
    "What undergraduate courses are offered?",
    "What is the annual tuition fee for B.Tech?",
    "What is the eligibility criteria for B.Tech admission?",
    "Are hostel facilities available for boys and girls?",
    "What companies visit for campus placement?",
    "What are the library operating hours?"
]

# Display suggestions in responsive horizontal columns
cols = st.columns(3)
clicked_suggested = None
for i, query in enumerate(suggested_queries):
    col_idx = i % 3
    with cols[col_idx]:
        if st.button(f"📌 {query}", key=f"sug_{i}", use_container_width=True):
            clicked_suggested = query

# Display Chat History
st.markdown("### 💬 **Conversation**")
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.write(msg["content"])
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.write(msg["content"])
            if msg.get("meta"):
                meta = msg["meta"]
                status = meta.get("status")
                cat = meta.get("category")
                conf = meta.get("confidence", 0.0)
                matched_q = meta.get("matched_question")

                meta_html = ""
                if cat and cat not in ["Greeting", "Gratitude", "Farewell"]:
                    meta_html += f'<span class="category-tag">📂 Category: {cat}</span> '
                if status == "matched":
                    meta_html += f'<span class="confidence-tag">🎯 Similarity Score: {conf:.2f}</span> '
                    if matched_q:
                        meta_html += f'<div style="font-size:0.8rem; color:#475569; margin-top:4px;"><em>Matched Question: "{matched_q}"</em></div>'
                elif status == "fallback":
                    meta_html += f'<span class="fallback-tag">⚠️ Fallback Triggered (Score: {conf:.2f})</span>'

                if meta_html:
                    st.markdown(meta_html, unsafe_allow_html=True)

# Handle Input: either from chat_input or clicked suggested button
user_input = st.chat_input("Type your question here (e.g. 'Tell me about hostel fees', 'How to apply for admission?')...")
active_query = clicked_suggested if clicked_suggested else user_input

if active_query and chatbot_ready:
    # Append user question to history
    st.session_state.messages.append({
        "role": "user",
        "content": active_query,
        "meta": None
    })

    # Get response from CollegeChatbot
    res = chatbot.get_response(active_query, category_filter=selected_category)

    # Append bot response to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": res["answer"],
        "meta": res
    })

    # Refresh page to render updated message stream
    st.rerun()

# Interaction Activity Log Expander (Privacy Safe)
if chatbot_ready:
    with st.expander("📋 View Chatbot Activity & Query Logs (Privacy-Safe Session Data)"):
        logs_df = chatbot.get_logs_df()
        if not logs_df.empty:
            st.dataframe(logs_df, use_container_width=True)
            st.caption("Logs record query length, timestamp, intent/category, and match confidence. No personal data is stored.")
        else:
            st.info("No queries processed yet in this session.")

# Footer
st.markdown(
    """
    <div class="app-footer">
        <strong>AI-Based College Enquiry Chatbot</strong> | Final Year / Mini Project<br>
        Developed with Python, Streamlit, Pandas & Scikit-learn (TF-IDF & Cosine Similarity)<br>
        <em>All college data shown is for academic and demonstration purposes.</em>
    </div>
    """,
    unsafe_allow_html=True
)

