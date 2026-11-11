"""
Generates an attractive visual mockup/screenshot of the running Streamlit UI
and saves it to assets/ui_preview.png for documentation and presentation slides.
"""

import os
from PIL import Image, ImageDraw, ImageFont

def generate_ui_preview():
    width, height = 1200, 780
    img = Image.new("RGBA", (width, height), "#F8FAFC")
    draw = ImageDraw.Draw(img)

    # 1. Sidebar background
    draw.rectangle([(0, 0), (320, height)], fill="#FFFFFF", outline="#E2E8F0", width=1)

    # Sidebar Header / Logo
    draw.rounded_rectangle([(30, 30), (290, 110)], radius=10, fill="#1E40AF")
    draw.text((50, 48), "🎓 APEX INSTITUTE", fill="#FFFFFF")
    draw.text((50, 72), "AI Enquiry Assistant v1.0", fill="#93C5FD")

    # Sidebar Controls
    draw.text((30, 135), "ENQUIRY CONTROLS", fill="#1E40AF")
    draw.rectangle([(30, 155), (290, 160)], fill="#3B82F6")

    draw.text((30, 180), "Filter by Category:", fill="#475569")
    draw.rounded_rectangle([(30, 205), (290, 245)], radius=6, fill="#F1F5F9", outline="#CBD5E1", width=1)
    draw.text((45, 218), "📂 All Categories  ▼", fill="#0F172A")

    draw.text((30, 265), "Match Threshold: 0.25", fill="#475569")
    draw.line([(30, 295), (290, 295)], fill="#CBD5E1", width=4)
    draw.line([(30, 295), (100, 295)], fill="#2563EB", width=4)
    draw.ellipse([(95, 290), (105, 300)], fill="#1E40AF")

    # Knowledge Base Stats Cards
    draw.text((30, 330), "KNOWLEDGE BASE STATS", fill="#1E40AF")
    draw.rectangle([(30, 350), (290, 355)], fill="#3B82F6")

    # Stat Card 1
    draw.rounded_rectangle([(30, 375), (150, 445)], radius=8, fill="#EFF6FF", outline="#BFDBFE", width=1)
    draw.text((42, 385), "Total FAQs", fill="#1E40AF")
    draw.text((42, 410), "42", fill="#1E3A8A")

    # Stat Card 2
    draw.rounded_rectangle([(170, 375), (290, 445)], radius=8, fill="#EFF6FF", outline="#BFDBFE", width=1)
    draw.text((182, 385), "Categories", fill="#1E40AF")
    draw.text((182, 410), "10", fill="#1E3A8A")

    # Clear Chat Button
    draw.rounded_rectangle([(30, 480), (290, 520)], radius=8, fill="#FEE2E2", outline="#FCA5A5", width=1)
    draw.text((85, 493), "🗑️ Clear Chat History", fill="#991B1B")

    # Architecture Tag
    draw.rounded_rectangle([(30, 560), (290, 740)], radius=8, fill="#F8FAFC", outline="#E2E8F0", width=1)
    draw.text((45, 575), "SYSTEM DETAILS", fill="#64748B")
    draw.text((45, 605), "• Engine: TF-IDF + Cosine", fill="#334155")
    draw.text((45, 630), "• Vectorizer: Scikit-learn", fill="#334155")
    draw.text((45, 655), "• Data: college_faq.csv", fill="#334155")
    draw.text((45, 680), "• Status: Online (Demo Mode)", fill="#059669")
    draw.text((45, 705), "• Port: http://localhost:8501", fill="#64748B")

    # 2. Main Page Header Banner
    draw.rounded_rectangle([(350, 25), (1170, 115)], radius=12, fill="#1E40AF")
    draw.text((375, 40), "🎓 AI-Based College Enquiry Chatbot", fill="#FFFFFF")
    # Demo badge
    draw.rounded_rectangle([(870, 45), (990, 72)], radius=14, fill="#FEF3C7", outline="#FCD34D", width=1)
    draw.text((885, 50), "DEMO DATA", fill="#92400E")
    draw.text((375, 78), "Ask questions in natural language regarding courses, admissions, hostel, fees, exams, and placements.", fill="#DBEAFE")

    # 3. Quick Suggestions Section
    draw.text((350, 135), "💡 Quick Suggested Questions (Click to Ask):", fill="#1E40AF")
    sug_items = [
        "📌 What undergraduate courses are offered?",
        "📌 What is the annual tuition fee for B.Tech?",
        "📌 Are hostel facilities available for boys and girls?"
    ]
    for i, s in enumerate(sug_items):
        sx = 350 + i * 275
        draw.rounded_rectangle([(sx, 160), (sx + 265, 195)], radius=6, fill="#FFFFFF", outline="#CBD5E1", width=1)
        draw.text((sx + 10, 172), s[:36] + "...", fill="#1E40AF")

    # 4. Chat Messages Area
    draw.text((350, 215), "💬 Conversation", fill="#0F172A")

    # Message 1: Bot Welcome
    draw.rounded_rectangle([(400, 245), (1150, 325)], radius=10, fill="#FFFFFF", outline="#E2E8F0", width=1)
    draw.text((360, 255), "🤖", fill="#000000")
    draw.text((420, 255), "Hello! 🎓 Welcome to the College Enquiry Chatbot.", fill="#0F172A")
    draw.text((420, 275), "I can assist you with courses, admissions, fees, hostel rules, placements, and more.", fill="#475569")
    draw.text((420, 295), "All answers currently represent demonstration data.", fill="#64748B")

    # Message 2: User Query
    draw.rounded_rectangle([(650, 345), (1110, 395)], radius=10, fill="#E0E7FF", outline="#C7D2FE", width=1)
    draw.text((1130, 355), "🧑‍🎓", fill="#000000")
    draw.text((670, 360), "What undergraduate courses are offered in the college?", fill="#1E1B4B")

    # Message 3: Bot Response with Confidence Tag
    draw.rounded_rectangle([(400, 415), (1150, 520)], radius=10, fill="#FFFFFF", outline="#E2E8F0", width=1)
    draw.text((360, 425), "🤖", fill="#000000")
    draw.text((420, 425), "[DEMO DATA] The college offers Bachelor of Technology (B.Tech) degrees in Computer Science,", fill="#0F172A")
    draw.text((420, 445), "Information Technology, Electronics & Communication, Mechanical, and Civil Engineering.", fill="#0F172A")

    # Badges
    draw.rounded_rectangle([(420, 475), (550, 500)], radius=6, fill="#DBEAFE")
    draw.text((430, 480), "📂 Category: Courses", fill="#1E40AF")

    draw.rounded_rectangle([(565, 475), (715, 500)], radius=6, fill="#DCFCE7")
    draw.text((575, 480), "🎯 Similarity Score: 0.94", fill="#166534")

    # Message 4: User Query 2
    draw.rounded_rectangle([(750, 540), (1110, 590)], radius=10, fill="#E0E7FF", outline="#C7D2FE", width=1)
    draw.text((1130, 550), "🧑‍🎓", fill="#000000")
    draw.text((770, 555), "How much is the hostel fee per year?", fill="#1E1B4B")

    # Message 5: Bot Response 2
    draw.rounded_rectangle([(400, 610), (1150, 690)], radius=10, fill="#FFFFFF", outline="#E2E8F0", width=1)
    draw.text((360, 620), "🤖", fill="#000000")
    draw.text((420, 620), "[DEMO DATA] The hostel accommodation fee is approximately Rs. 60,000 per year, inclusive of mess dining charges.", fill="#0F172A")
    draw.rounded_rectangle([(420, 650), (540, 675)], radius=6, fill="#DBEAFE")
    draw.text((430, 655), "📂 Category: Hostel", fill="#1E40AF")
    draw.rounded_rectangle([(555, 650), (705, 675)], radius=6, fill="#DCFCE7")
    draw.text((565, 655), "🎯 Similarity Score: 0.88", fill="#166534")

    # 5. Input Box Area at bottom
    draw.rounded_rectangle([(350, 710), (1170, 755)], radius=10, fill="#FFFFFF", outline="#CBD5E1", width=1)
    draw.text((370, 725), "Type your question here (e.g. 'Tell me about hostel fees', 'How to apply for admission?')...", fill="#94A3B8")
    # Send button
    draw.rounded_rectangle([(1120, 715), (1160, 750)], radius=6, fill="#1E40AF")
    draw.text((1132, 723), "➤", fill="#FFFFFF")

    os.makedirs(os.path.dirname(os.path.abspath("assets/ui_preview.png")), exist_ok=True)
    out_path = os.path.join(os.path.dirname(__file__), "assets", "ui_preview.png")
    img.save(out_path, "PNG")
    print(f"Generated UI Preview at {out_path}")

if __name__ == "__main__":
    generate_ui_preview()

