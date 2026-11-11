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
            "subtitle": "An Intelligent Natural Language Processing Assistant for Academic Enquiries",
            "meta": [
                "Course: Mini Project / Capstone",
                "Domain: Artificial Intelligence & Natural Language Processing",
                "Technologies: Python, Streamlit, Pandas, Scikit-learn, TF-IDF",
                "Academic Year: 2026-2027"
            ]
        },
        # Slide 2: Introduction
        {
            "type": "content",
            "title": "Introduction & Background",
            "points": [
                ("Need for Automation in Colleges", "Prospective and enrolled students frequently seek critical information regarding admissions, fees, hostel rules, courses, and exam dates."),
                ("Bottlenecks of Manual Systems", "Administrative desks, phone helplines, and notice boards experience congestion, long delays, and restricted operating hours."),
                ("Conversational AI Solution", "Chatbots provide instant, 24/7 conversational assistance directly through natural language queries."),
                ("Lightweight & Reliable Design", "Utilizes local Machine Learning vectorization without paid APIs or external dependencies.")
            ]
        },
        # Slide 3: Problem Statement
        {
            "type": "content",
            "title": "Problem Statement",
            "points": [
                ("Information Fragmentation", "College data is scattered across multipage prospectuses, PDF circulars, and departmental web pages."),
                ("High Administrative Workload", "College office staff spend substantial time repeatedly answering identical routine enquiries."),
                ("Lack of 24/7 Student Support", "Students and parents cannot receive verified answers during non-office hours, holidays, or admission rushes."),
                ("Hallucination Risk in LLMs", "Generic generative AI often produces inaccurate or fabricated college policies; our system ensures strictly verified answers.")
            ]
        },
        # Slide 4: Objectives
        {
            "type": "content",
            "title": "Project Objectives",
            "points": [
                ("Natural Language Understanding", "Accurately parse and interpret user enquiries regardless of variation in phrasing."),
                ("Mathematical Similarity Matching", "Implement TF-IDF Vectorization and Cosine Similarity to find the best-matched FAQ entry."),
                ("Zero Hallucination Policy", "Ensure the chatbot never fabricates college facts; all answers are drawn from verified datasets or safely fallback."),
                ("Intuitive Web User Interface", "Develop a responsive, modern Streamlit UI with conversation bubbles, category filters, and suggested questions.")
            ]
        },
        # Slide 5: Technologies Used
        {
            "type": "content",
            "title": "Technologies & Tools",
            "points": [
                ("Python 3.13+", "Core programming language for data processing, NLP algorithms, and system integration."),
                ("Streamlit", "Modern open-source web application framework for rapid and elegant UI development."),
                ("Pandas", "Robust data manipulation library for loading, validating, and filtering FAQ datasets."),
                ("Scikit-learn", "Machine learning library providing TfidfVectorizer and Cosine Similarity computations."),
                ("CSV Knowledge Base", "Modular, transparent, and easily maintainable knowledge store for academic FAQs.")
            ]
        },
        # Slide 6: System Architecture
        {
            "type": "content",
            "title": "System Architecture",
            "points": [
                ("Presentation Layer (Streamlit)", "Chat interface, query input box, suggested enquiry buttons, topic filters, and conversation history."),
                ("Pre-Processing & Intent Classification", "Handles conversational pleasantries (Greetings, Gratitude, Farewells) and validates empty inputs."),
                ("NLP Vectorization Engine", "Transforms FAQ corpus and user questions into TF-IDF n-gram feature vectors."),
                ("Similarity Evaluation & Thresholding", "Calculates Cosine Similarity; returns verified answer if score >= threshold, else triggers fallback."),
                ("Logging & Verification", "Maintains privacy-safe activity logs (timestamps, score, categories) without storing sensitive user identities.")
            ]
        },
        # Slide 7: AI Working Principle
        {
            "type": "content",
            "title": "AI Working Principle: TF-IDF & Cosine Similarity",
            "points": [
                ("Term Frequency (TF)", "Measures the frequency of words in an enquiry: TF(t, d) = count(t in d) / total words in d."),
                ("Inverse Document Frequency (IDF)", "Penalizes common words and emphasizes informative terms: IDF(t) = log((1 + n) / (1 + df(t))) + 1."),
                ("Vector Representation", "Both stored FAQs and user queries are transformed into high-dimensional vector representations."),
                ("Cosine Similarity Metric", "Computes the cosine of the angle between query vector (A) and FAQ vector (B): Sim(A, B) = (A · B) / (||A|| * ||B||)."),
                ("Threshold Decision Logic", "If max(Sim) >= threshold (default 0.25), the matched answer is returned; otherwise, safe fallback is executed.")
            ]
        },
        # Slide 8: Module Descriptions
        {
            "type": "content",
            "title": "Key Software Modules",
            "points": [
                ("data_loader.py", "Validates dataset existence, confirms required schema (category, question, answer), and filters blank rows."),
                ("chatbot.py", "Core CollegeChatbot class encapsulating intent logic, TF-IDF matrix generation, similarity scoring, and logging."),
                ("app.py", "Streamlit application rendering header, interactive sidebar, suggested pills, chat streams, and session history."),
                ("test_chatbot.py", "Automated pytest suite testing 15+ functional areas including greeting, domain queries, edge cases, and fallbacks.")
            ]
        },
        # Slide 9: Application Interface Design
        {
            "type": "content",
            "title": "Application Interface & UX Design",
            "points": [
                ("Modern Blue & White Aesthetic", "Professional institutional styling with custom CSS, visual badges, and high-contrast typography."),
                ("Session-Based Chat History", "Maintains full multi-turn conversational dialogue within user sessions with clear avatars (🧑‍🎓 & 🤖)."),
                ("Category Filter & Suggestions", "Enables students to filter by academic departments and click ready-made suggested queries."),
                ("Transparency Badges", "Displays match confidence scores, matched questions, and explicit [DEMO DATA] indicators.")
            ]
        },
        # Slide 10: Testing and Results
        {
            "type": "content",
            "title": "Testing & Verification Results",
            "points": [
                ("Automated Test Suite", "100% pass rate across 15+ automated test modules covering 10 functional college domains."),
                ("Conversational Intent Accuracy", "Accurate instantaneous detection for greetings ('Hello', 'Hi') and gratitude ('Thank you')."),
                ("Domain Enquiries", "Consistently retrieves correct information for Courses, Fees, Admissions, Hostels, and Placements."),
                ("Fallback Robustness", "Successfully deflects off-topic queries (e.g. general trivia, cooking) to the official college helpdesk contact.")
            ]
        },
        # Slide 11: Advantages & Future Scope
        {
            "type": "content",
            "title": "Advantages & Future Enhancements",
            "points": [
                ("Zero Operational Cost", "Runs fully locally without cloud API subscriptions, tokens, or expensive GPUs."),
                ("High Speed & Determinism", "Sub-second response times; eliminates false generative hallucinations."),
                ("Future Scope - Multilingual NLP", "Incorporate regional language tokenizers (Hindi, Tamil, Telugu, etc.) for broader accessibility."),
                ("Future Scope - Speech Interface", "Integrate Speech-to-Text and Text-to-Speech for voice-activated campus kiosks.")
            ]
        },
        # Slide 12: Conclusion
        {
            "type": "content",
            "title": "Conclusion",
            "points": [
                ("Successful Implementation", "Successfully engineered a robust, intelligent, and user-friendly College Enquiry Chatbot."),
                ("Academic & Institutional Impact", "Significantly reduces administrative burden while offering students 24/7 enquiry access."),
                ("Production-Ready Architecture", "Easily upgradeable from demonstration data to live institutional data by updating a simple CSV file."),
                ("Summary", "The project proves that lightweight classical NLP with clean UX provides reliable, trustworthy academic assistance.")
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
