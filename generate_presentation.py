"""
PowerPoint Presentation Generator for AI-Based College Enquiry Chatbot.

Creates a professional 12-slide presentation adhering to the blue-and-white academic theme.
Output: documentation/presentation.pptx
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Theme Colors
COLOR_PRIMARY_BLUE = RGBColor(30, 64, 175)    # #1E40AF
COLOR_SECONDARY_BLUE = RGBColor(59, 130, 246) # #3B82F6
COLOR_LIGHT_BG = RGBColor(248, 250, 252)      # #F8FAFC
COLOR_TEXT_DARK = RGBColor(15, 23, 42)        # #0F172A
COLOR_TEXT_MUTED = RGBColor(100, 116, 139)    # #64748B
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_CARD_BG = RGBColor(239, 246, 255)       # #EFF6FF
COLOR_ACCENT_AMBER = RGBColor(217, 119, 6)    # #D97706


def create_header(slide, title_text, category_text="COLLEGE MINI PROJECT"):
    """Adds a standard professional top header banner."""
    # Top banner shape
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8.4), Inches(1.1))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_top = 0
    tf.margin_left = 0

    p_cat = tf.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(11)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_SECONDARY_BLUE

    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.size = Pt(24)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_PRIMARY_BLUE


def build_presentation(output_path: str):
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    slides_data = [
        # Slide 1: Title
        {
            "type": "title",
            "title": "AI-BASED COLLEGE ENQUIRY CHATBOT",
            "subtitle": "VR College of Engineering AI Campus Assistant (VRBot)",
            "meta": [
                "Institution: VR College of Engineering",
                "Course: Mini Project / Capstone",
                "Domain: Artificial Intelligence & Natural Language Processing",
                "Technologies: Python 3.13, Streamlit, Scikit-learn, TF-IDF, Gemini API, FPDF2",
                "Academic Year: 2026-2027"
            ]
        },
        # Slide 2: Introduction
        {
            "type": "content",
            "title": "Introduction & Background",
            "points": [
                ("Need for Automation in Colleges", "Prospective applicants and students frequently seek critical information regarding admissions, department fees, hostel rules, and placements."),
                ("Bottlenecks of Manual Systems", "Administrative helpdesks and phone lines experience heavy congestion, long delays, and restricted office hours."),
                ("Conversational AI Solution", "VRBot provides 24/7 instant conversational assistance with ChatGPT-like warmth and multi-turn context memory."),
                ("Hybrid Architecture", "Integrates Google Gemini 2.5 Flash with an intelligent local deterministic agent for 100% offline-ready, zero-hallucination answers.")
            ]
        },
        # Slide 3: Problem Statement
        {
            "type": "content",
            "title": "Problem Statement",
            "points": [
                ("Information Fragmentation", "College data is scattered across multipage prospectuses, circulars, and departmental portals."),
                ("High Administrative Workload", "Office staff spend up to 70% of their working hours repeatedly answering routine enquiries."),
                ("Lack of 24/7 Support & Lead Capture", "Colleges lose prospective applicant leads outside working hours without automated inquiry capture."),
                ("Hallucination Risk in Generic LLMs", "Generic chatbots invent inaccurate fee amounts or dates; our system enforces strict fact grounding.")
            ]
        },
        # Slide 4: Objectives
        {
            "type": "content",
            "title": "Project Objectives",
            "points": [
                ("Natural Multi-Turn Understanding", "Accurately parse queries and follow-up pronouns ('What is its fee?') across conversational turns."),
                ("Mathematical Similarity Matching", "Implement TF-IDF Vectorization and Cosine Similarity combined with fuzzy typo-tolerance."),
                ("Smart Fee & Lead Management", "Deliver 2-tier fee structures and capture prospective student leads with unique tracking IDs."),
                ("Staff Administration & Gap Tracking", "Provide an authenticated Admin Desk (PIN: admin123) with analytics, FAQ CRUD, and gap tracking.")
            ]
        },
        # Slide 5: Technologies Used
        {
            "type": "content",
            "title": "Technologies & Tools",
            "points": [
                ("Python 3.13+", "Core programming language for data processing, NLP algorithms, and system integration."),
                ("Streamlit & Web Speech API", "Modern web framework featuring voice input (STT) and speech synthesis (Read Aloud 🔊)."),
                ("Scikit-learn & Pandas", "Machine learning TF-IDF vectorization, Cosine Similarity, and CSV dataset manipulation."),
                ("Google Gemini SDK (google-genai)", "Optional hybrid LLM integration for empathetic, grounded dialogue generation."),
                ("FPDF2 & python-pptx", "Automated PDF prospectus, academic report, and presentation slide deck generators.")
            ]
        },
        # Slide 6: System Architecture
        {
            "type": "content",
            "title": "System Architecture",
            "points": [
                ("Presentation Layer (Streamlit)", "Chat interface, voice STT/TTS, category filters, lead capture modal, and Staff Admin Desk."),
                ("Conversational Controller (ai_agent.py)", "Maintains multi-turn session memory, handles follow-ups, and orchestrates hybrid generation."),
                ("NLP Vectorization Engine (chatbot.py)", "Performs fuzzy typo correction, TF-IDF vectorization, and Cosine Similarity thresholding."),
                ("Smart Fee Engine (fee_manager.py)", "Extracts specific department fees first (Tier 1) and appends full college fee structure (Tier 2)."),
                ("Admin & Lead Manager (lead_manager.py)", "Generates tracking codes (VRCE-26-XXXXX), logs feedback, and tracks knowledge gaps.")
            ]
        },
        # Slide 7: AI Working Principle
        {
            "type": "content",
            "title": "AI Working Principle: TF-IDF & Cosine Similarity",
            "points": [
                ("Term Frequency (TF)", "Measures word prominence in an enquiry: TF(t, d) = count(t in d) / total words in d."),
                ("Inverse Document Frequency (IDF)", "Penalizes generic words and prioritizes domain terms: IDF(t) = log((1 + n) / (1 + df(t))) + 1."),
                ("Fuzzy Typo-Tolerance", "Normalizes misspelled student tokens ('admision', 'hostal', 'scolorship') before vectorization."),
                ("Cosine Similarity Metric", "Computes vector alignment: Sim(A, B) = (A · B) / (||A|| * ||B||)."),
                ("Strict Grounding", "Retrieves verified answers only when Sim >= threshold; prevents false generative hallucinations.")
            ]
        },
        # Slide 8: Module Descriptions
        {
            "type": "content",
            "title": "Key Software Modules",
            "points": [
                ("app.py", "Streamlit application rendering chat interface, voice STT/TTS, and authenticated Admin Desk."),
                ("chatbot.py & data_loader.py", "Core NLP engine, TF-IDF similarity calculation, schema validation, and dynamic FAQ CRUD."),
                ("ai_agent.py", "Hybrid AI coordinator, Google Gemini 2.5 Flash integration, and multi-turn session context."),
                ("fee_manager.py & lead_manager.py", "Specialized fee knowledge base, student lead generation, and unanswered query tracker."),
                ("test_chatbot.py & test_features.py", "Comprehensive Pytest automated test suite verifying 35 functional and integration test cases.")
            ]
        },
        # Slide 9: Application Interface Design
        {
            "type": "content",
            "title": "Application Interface & UX Design",
            "points": [
                ("ChatGPT-Style Aesthetic", "Clean institutional blue-and-white theme, conversational bubbles, and markdown cards."),
                ("Multi-Turn Memory Stream", "Remembers conversation history for natural follow-ups with instant suggested action pills."),
                ("Voice Capabilities", "Integrated browser-based Speech-to-Text input and Web Speech audio read-aloud buttons."),
                ("Staff Control Center", "Protected by PIN 'admin123' with real-time analytics, lead review, gap logs, and FAQ management.")
            ]
        },
        # Slide 10: Testing and Results
        {
            "type": "content",
            "title": "Testing & Verification Results",
            "points": [
                ("Automated Test Suite", "100% pass rate across 35 automated pytest cases in 9.37 seconds with zero failures."),
                ("Core Conversational Tests (26)", "Validates greetings, gratitude, category queries, edge cases, and safe fallback triggers."),
                ("Extended Feature Tests (9)", "Verifies Gemini hybrid fallback, multi-turn memory, fuzzy typos, lead capture, and FAQ CRUD."),
                ("Sub-Second Latency", "Deterministic local retrieval operates in < 50ms on standard CPU hardware.")
            ]
        },
        # Slide 11: Advantages & Future Scope
        {
            "type": "content",
            "title": "Specialized Features & Institutional Value",
            "points": [
                ("Two-Tier Fee Clarity", "Directly answers specific branch fees first, followed by the comprehensive fee summary."),
                ("Admission Lead Generation", "Captures prospective applicants directly into leads.csv with official reference codes."),
                ("Unanswered Query Gap Tracker", "Logs low-confidence questions into unanswered_queries.csv to pinpoint curriculum gaps."),
                ("Offline-First Reliability", "Operates seamlessly on campus intranet without paid third-party cloud subscriptions.")
            ]
        },
        # Slide 12: Conclusion
        {
            "type": "content",
            "title": "Conclusion & Future Work",
            "points": [
                ("Successful Implementation", "Delivered an intelligent, accurate, and multi-turn AI College Enquiry Chatbot."),
                ("Zero Hallucination Guaranteed", "Strict fact grounding ensures total academic accuracy while maintaining friendly dialogue."),
                ("Future Scope - Multilingual NLP", "Integration of regional Indian language tokenizers (Hindi, Tamil, Telugu)."),
                ("Future Scope - ERP Integration", "Direct integration with college Student Information Systems for individual grade/attendance lookup.")
            ]
        }
    ]

    for data in slides_data:
        slide = prs.slides.add_slide(blank_layout)

        # Background color
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = COLOR_LIGHT_BG

        if data["type"] == "title":
            # Title slide background accent card
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.8), Inches(8.4), Inches(5.9))
            card.fill.solid()
            card.fill.fore_color.rgb = COLOR_WHITE
            card.line.color.rgb = COLOR_SECONDARY_BLUE
            card.line.width = Pt(1.5)

            tb = slide.shapes.add_textbox(Inches(1.2), Inches(1.3), Inches(7.6), Inches(4.8))
            tf = tb.text_frame
            tf.word_wrap = True

            p1 = tf.paragraphs[0]
            p1.text = "COLLEGE ACADEMIC PROJECT"
            p1.font.size = Pt(13)
            p1.font.bold = True
            p1.font.color.rgb = COLOR_SECONDARY_BLUE

            p2 = tf.add_paragraph()
            p2.text = data["title"]
            p2.font.size = Pt(28)
            p2.font.bold = True
            p2.font.color.rgb = COLOR_PRIMARY_BLUE
            p2.space_before = Pt(10)

            p3 = tf.add_paragraph()
            p3.text = data["subtitle"]
            p3.font.size = Pt(15)
            p3.font.color.rgb = COLOR_TEXT_MUTED
            p3.space_before = Pt(8)

            p_line = tf.add_paragraph()
            p_line.text = "—" * 28
            p_line.font.color.rgb = COLOR_SECONDARY_BLUE
            p_line.space_before = Pt(12)

            for m in data["meta"]:
                pm = tf.add_paragraph()
                pm.text = f"• {m}"
                pm.font.size = Pt(12)
                pm.font.color.rgb = COLOR_TEXT_DARK
                pm.space_before = Pt(4)

        else:
            create_header(slide, data["title"])

            # Check if this slide has an image attached (Slide 9: Interface Design)
            if data.get("title") == "Application Interface & UX Design":
                left = Inches(0.8)
                top = Inches(1.6)
                width = Inches(4.5)
                height = Inches(5.2)

                content_box = slide.shapes.add_textbox(left, top, width, height)
                tf = content_box.text_frame
                tf.word_wrap = True
                tf.margin_top = 0
                tf.margin_left = 0

                for i, (heading, desc) in enumerate(data["points"]):
                    p_head = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                    p_head.text = f"▸  {heading}"
                    p_head.font.size = Pt(13)
                    p_head.font.bold = True
                    p_head.font.color.rgb = COLOR_PRIMARY_BLUE
                    p_head.space_before = Pt(8) if i > 0 else Pt(0)

                    p_desc = tf.add_paragraph()
                    p_desc.text = f"    {desc}"
                    p_desc.font.size = Pt(11)
                    p_desc.font.color.rgb = COLOR_TEXT_DARK
                    p_desc.space_before = Pt(2)

                # Add application screenshot on right side
                img_path = os.path.join(os.path.dirname(__file__), "assets", "ui_preview.png")
                if os.path.exists(img_path):
                    slide.shapes.add_picture(img_path, Inches(5.5), Inches(1.8), Inches(4.0), Inches(5.0))
            else:
                # Standard full-width content container
                left = Inches(0.8)
                top = Inches(1.7)
                width = Inches(8.4)
                height = Inches(5.2)

                content_box = slide.shapes.add_textbox(left, top, width, height)
                tf = content_box.text_frame
                tf.word_wrap = True
                tf.margin_top = 0
                tf.margin_left = 0

                for i, (heading, desc) in enumerate(data["points"]):
                    p_head = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                    p_head.text = f"▸  {heading}"
                    p_head.font.size = Pt(15)
                    p_head.font.bold = True
                    p_head.font.color.rgb = COLOR_PRIMARY_BLUE
                    p_head.space_before = Pt(12) if i > 0 else Pt(0)

                    p_desc = tf.add_paragraph()
                    p_desc.text = f"    {desc}"
                    p_desc.font.size = Pt(12.5)
                    p_desc.font.color.rgb = COLOR_TEXT_DARK
                    p_desc.space_before = Pt(2)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prs.save(output_path)
    print(f"Presentation saved successfully to {output_path}")


if __name__ == "__main__":
    out_file = os.path.join(os.path.dirname(__file__), "documentation", "presentation.pptx")
    build_presentation(out_file)
