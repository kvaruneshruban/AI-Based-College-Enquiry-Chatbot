"""
Generates an attractive visual mockup/screenshot of the running Streamlit UI
with the Orély University campus scenery, turquoise/teal aesthetic, VRBot mascot,
ChatGPT sidebar, Top Nav with Language Translator & User Profile, and Quick Access cards.
Saves it to assets/ui_preview.png for documentation and presentation slides.
"""

import os
from PIL import Image, ImageDraw, ImageFont

def generate_ui_preview():
    width, height = 1200, 780
    img = Image.new("RGBA", (width, height), "#083344")
    draw = ImageDraw.Draw(img)

    # 1. Illustrated Campus Sky & Gradient
    for y in range(height):
        ratio = y / height
        # Turquoise & Teal Gradient
        r = int(8 + (14 - 8) * ratio + 10 * (1 - ratio))
        g = int(51 + (116 - 51) * ratio + 30 * ratio)
        b = int(68 + (144 - 68) * ratio + 60 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # Illustrated Clouds
    draw.ellipse([(600, 40), (800, 100)], fill=(255, 255, 255, 120))
    draw.ellipse([(700, 30), (950, 95)], fill=(255, 255, 255, 140))
    draw.ellipse([(850, 45), (1050, 105)], fill=(255, 255, 255, 110))

    # Illustrated Distant Campus Skyline
    draw.rectangle([(650, 180), (710, 320)], fill=(8, 145, 178, 90))
    draw.polygon([(645, 180), (680, 130), (715, 180)], fill=(8, 145, 178, 120))
    draw.rectangle([(730, 210), (840, 320)], fill=(8, 145, 178, 80))
    draw.rectangle([(860, 190), (980, 320)], fill=(8, 145, 178, 70))

    # Rolling Green Campus Lawns (Orély Style)
    draw.ellipse([(300, 480), (1400, 950)], fill=(5, 150, 105, 220))
    draw.ellipse([(200, 560), (1300, 1050)], fill=(16, 185, 129, 230))
    draw.ellipse([(400, 620), (1500, 1150)], fill=(52, 211, 153, 240))

    # 2. Sidebar background (Clean White & Light Teal with Subtle Shadow)
    draw.rectangle([(0, 0), (310, height)], fill="#F8FAFC", outline="#CCFBF1", width=2)

    # Sidebar Header / Logo Card
    draw.rounded_rectangle([(16, 16), (294, 98)], radius=12, fill="#FFFFFF", outline="#5EEAD4", width=2)
    draw.rounded_rectangle([(24, 24), (82, 90)], radius=10, fill="#0F766E")
    draw.text((38, 45), "🎓", fill="#FFFFFF")
    draw.text((94, 28), "VR COLLEGE", fill="#0F766E")
    draw.text((94, 46), "OF ENGINEERING", fill="#0F766E")
    draw.rounded_rectangle([(94, 66), (180, 84)], radius=4, fill="#F0FDFA", outline="#99F6E4", width=1)
    draw.text((100, 69), "AICTE Approved", fill="#0D9488")
    draw.rounded_rectangle([(185, 66), (250, 84)], radius=4, fill="#FEF3C7", outline="#FDE68A", width=1)
    draw.text((192, 69), "NAAC 'A+'", fill="#92400E")

    # ➕ New Chat Button (ChatGPT-Style Teal Gradient)
    draw.rounded_rectangle([(16, 112), (294, 150)], radius=8, fill="#0D9488")
    draw.text((95, 122), "➕ New Chat", fill="#FFFFFF")

    # 🔍 Search Conversations Input
    draw.rounded_rectangle([(16, 160), (294, 192)], radius=8, fill="#FFFFFF", outline="#CCFBF1", width=1)
    draw.text((30, 169), "🔍 Search conversations...", fill="#64748B")

    # 🕘 Recent Searches Section
    draw.text((18, 208), "🕘 RECENT SEARCHES", fill="#0F766E")
    recent_items = [
        "🔍 Available Engineering Courses",
        "🔍 College Fee Structure",
        "🔍 Hostel Facilities",
        "🔍 Placement Details"
    ]
    for idx, item in enumerate(recent_items):
        ry = 228 + idx * 32
        draw.rounded_rectangle([(16, ry), (294, ry + 26)], radius=6, fill="#FFFFFF", outline="#E2E8F0", width=1)
        draw.text((26, ry + 6), item, fill="#334155")

    # 📂 Previous Conversations List
    draw.text((18, 368), "📂 PREVIOUS CONVERSATIONS", fill="#0F766E")
    conv_items = [
        ("👉 Hostel Fee Structure", True),
        ("💬 B.Tech Admissions 2026", False),
        ("💬 Campus Recruitment Highest CTC", False)
    ]
    for idx, (c_title, is_active) in enumerate(conv_items):
        cy = 388 + idx * 34
        bg_col = "#F0FDFA" if is_active else "#FFFFFF"
        b_col = "#14B8A6" if is_active else "#E2E8F0"
        t_col = "#0F766E" if is_active else "#475569"
        draw.rounded_rectangle([(16, cy), (260, cy + 28)], radius=6, fill=bg_col, outline=b_col, width=1)
        draw.text((26, cy + 7), c_title, fill=t_col)
        # Delete icon
        draw.rounded_rectangle([(266, cy), (294, cy + 28)], radius=6, fill="#FFFFFF", outline="#E2E8F0", width=1)
        draw.text((274, cy + 6), "🗑️", fill="#94A3B8")

    # AI Engine Indicator in Sidebar
    draw.rounded_rectangle([(16, 500), (294, 535)], radius=6, fill="#ECFDF5", outline="#A7F3D0", width=1)
    draw.text((30, 510), "🤖 Mode: Gemini 2.5 Flash / Local NLP", fill="#047857")

    # 3. Main Dashboard: Top Navigation Bar
    draw.rounded_rectangle([(330, 16), (1180, 62)], radius=12, fill="#FFFFFF", outline="#CCFBF1", width=1)
    draw.text((345, 28), "🏛️ VR College AI Admissions Desk • 24/7 Live", fill="#0F766E")
    # Language Translator Dropdown
    draw.rounded_rectangle([(810, 24), (970, 54)], radius=8, fill="#F0FDFA", outline="#99F6E4", width=1)
    draw.text((822, 32), "🌐 Language: English ▼", fill="#0D9488")
    # User Profile Badge
    draw.rounded_rectangle([(980, 24), (1170, 54)], radius=15, fill="#F0FDFA", outline="#99F6E4", width=1)
    draw.text((992, 32), "🧑‍🎓 Student Scholar • Online", fill="#047857")

    # 4. Welcome Banner with VR Mascot (Orély Theme)
    draw.rounded_rectangle([(330, 74), (1180, 195)], radius=16, fill="#0F766E", outline="#5EEAD4", width=1)
    draw.text((350, 86), "🏛️ VR COLLEGE OF ENGINEERING • NAAC 'A+' INSTITUTION", fill="#5EEAD4")
    draw.text((350, 106), "🎓 Welcome to VR College AI Campus Portal", fill="#FFFFFF")
    draw.text((350, 130), "Your 24/7 intelligent conversational advisor for admissions, degree courses, fee structures & hostels.", fill="#E2E8F0")
    # Badges
    p_items = ["🏆 NAAC 'A+'", "💼 ₹14 LPA Highest", "🎓 92% Placements", "🌟 Admissions Open"]
    for p_i, p_t in enumerate(p_items):
        px = 350 + p_i * 145
        draw.rounded_rectangle([(px, 155), (px + 135, 180)], radius=6, fill=(255, 255, 255, 30))
        draw.text((px + 8, 160), p_t, fill="#FFFFFF")
    # Mascot Card inside Hero
    draw.rounded_rectangle([(1040, 85), (1165, 184)], radius=12, fill=(255, 255, 255, 35), outline="#99F6E4", width=1)
    draw.text((1085, 95), "🤖", fill="#FFFFFF")
    draw.text((1055, 135), "VRBot Mascot", fill="#FFFFFF")
    draw.text((1052, 155), "AI Counselor 24/7", fill="#A5F3FC")

    # 5. Quick Access Cards Row (Courses, Fees, Hostel, Placements, Admissions)
    draw.text((330, 206), "⚡ QUICK ACCESS PORTALS (CLICK TO EXPLORE)", fill="#0F766E")
    qa_cards = [
        ("🎓 Courses", "B.Tech & PG"),
        ("💰 Fee Structure", "Tuition & Aid"),
        ("🏢 Hostel & Mess", "AC Rooms & Wi-Fi"),
        ("💼 Placements", "14 LPA CTC"),
        ("📋 Admissions", "Apply 2026-27")
    ]
    for q_i, (q_t, q_sub) in enumerate(qa_cards):
        qx = 330 + q_i * 172
        draw.rounded_rectangle([(qx, 226), (qx + 162, 280)], radius=10, fill="#FFFFFF", outline="#CCFBF1", width=1)
        draw.line([(qx, 226), (qx + 162, 226)], fill="#0D9488", width=3)
        draw.text((qx + 10, 236), q_t, fill="#0F172A")
        draw.text((qx + 10, 256), q_sub, fill="#0F766E")

    # 6. Two-Column Layout (Chat Stream & Hub)
    # Chat Column (Frosted Glass Container)
    draw.rounded_rectangle([(330, 295), (880, 765)], radius=14, fill="#FFFFFF", outline="#CCFBF1", width=1)
    draw.text((345, 308), "💬 Student Consultation Stream", fill="#0F766E")

    # User Bubble
    draw.rounded_rectangle([(480, 340), (865, 385)], radius=12, fill="#F0FDFA", outline="#99F6E4", width=1)
    draw.text((495, 353), "What are the hostel fee details for boys and girls?", fill="#0F172A")

    # Bot Bubble
    draw.rounded_rectangle([(345, 400), (865, 520)], radius=12, fill="#FFFFFF", outline="#E2E8F0", width=1)
    draw.line([(345, 400), (345, 520)], fill="#0D9488", width=4)
    draw.text((360, 412), "🤖 VRBot", fill="#0D9488")
    draw.text((360, 432), "VR College of Engineering offers separate AC & Non-AC hostels:", fill="#334155")
    draw.text((360, 452), "• Annual Hostel & Mess Fee: Rs. 65,000 (inclusive of dining, 24/7 Wi-Fi)", fill="#1E293B")
    draw.text((360, 472), "• Curfew: 8:30 PM (Weekdays), 9:00 PM (Weekends) with biometric security.", fill="#1E293B")
    # Action buttons
    draw.rounded_rectangle([(360, 492), (430, 514)], radius=4, fill="#F0FDFA", outline="#99F6E4", width=1)
    draw.text((370, 495), "🔊 Listen", fill="#0D9488")
    draw.text((440, 495), "👍 👎", fill="#64748B")

    # Voice Assistant & Companion Dock
    draw.rounded_rectangle([(345, 660), (865, 696)], radius=10, fill="#F0FDFA", outline="#99F6E4", width=1)
    draw.text((360, 670), "✨ VRBot AI Active  •  Speak or type below", fill="#0F766E")
    draw.rounded_rectangle([(735, 665), (855, 691)], radius=12, fill="#0D9488")
    draw.text((750, 670), "🎙️ Voice Enquiry", fill="#FFFFFF")

    # Glowing Chat Input Box
    draw.rounded_rectangle([(345, 710), (865, 755)], radius=24, fill="#FFFFFF", outline="#2DD4BF", width=2)
    draw.text((365, 725), "✨ Ask VRBot anything... Your college assistant is here to help!", fill="#64748B")
    draw.ellipse([(820, 718), (855, 748)], fill="#0D9488")
    draw.text((833, 724), "➤", fill="#FFFFFF")

    # Right Column: Interactive Campus Hub
    draw.rounded_rectangle([(895, 295), (1180, 765)], radius=14, fill="#FFFFFF", outline="#CCFBF1", width=1)
    draw.text((910, 308), "🏛️ Campus Hub & FAQs", fill="#0F766E")
    # Tabs
    draw.rounded_rectangle([(910, 335), (960, 360)], radius=6, fill="#0D9488")
    draw.text((918, 340), "FAQs", fill="#FFFFFF")
    draw.rounded_rectangle([(968, 335), (1020, 360)], radius=6, fill="#F1F5F9")
    draw.text((976, 340), "Apply", fill="#475569")
    draw.rounded_rectangle([(1028, 335), (1085, 360)], radius=6, fill="#F1F5F9")
    draw.text((1035, 340), "Staff", fill="#475569")
    draw.rounded_rectangle([(1093, 335), (1165, 360)], radius=6, fill="#F1F5F9")
    draw.text((1100, 340), "Gallery", fill="#475569")

    # FAQ Sample items
    hub_faqs = [
        "💡 B.Tech CSE Eligibility & Cutoffs",
        "💡 Annual Tuition Fee Breakdown",
        "💡 Hostel Admission & Mess Amenities",
        "💡 Placement Drives & Recruiters",
        "💡 Scholarships & Fee Concessions"
    ]
    for h_i, h_t in enumerate(hub_faqs):
        hy = 375 + h_i * 42
        draw.rounded_rectangle([(910, hy), (1165, hy + 34)], radius=8, fill="#F8FAFC", outline="#E2E8F0", width=1)
        draw.text((920, hy + 9), h_t, fill="#334155")

    # Prospectus Box
    draw.rounded_rectangle([(910, 600), (1165, 750)], radius=10, fill="#F0FDFA", outline="#99F6E4", width=1)
    draw.text((925, 615), "📄 Official 2026 Prospectus", fill="#0F766E")
    draw.text((925, 640), "Download complete academic curriculum,", fill="#475569")
    draw.text((925, 660), "fee schedules, and admissions handbook.", fill="#475569")
    draw.rounded_rectangle([(925, 690), (1150, 730)], radius=8, fill="#0D9488")
    draw.text((950, 702), "📥 Download PDF Prospectus", fill="#FFFFFF")

    # Save preview image
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "ui_preview.png")
    img.save(output_path, "PNG")
    print(f"UI preview generated successfully at: {output_path}")

if __name__ == "__main__":
    generate_ui_preview()
