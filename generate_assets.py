"""
Script to generate and maintain professional College Assets across all 15 categories.
Supports both Unsplash high-resolution downloads and offline Pillow rendering fallback.
"""

import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

IMAGE_DEFINITIONS = {
    # 1. College Campus
    "campus_main.jpg": {
        "url": "https://images.unsplash.com/photo-1562774053-701939374585?w=800&auto=format&fit=crop&q=80",
        "title": "College Campus",
        "subtitle": "VR College 50-Acre Main Academic Quad",
        "gradient": ("#1E3A8A", "#2563EB"),
        "icon": "🏛️"
    },
    "campus_aerial.jpg": {
        "url": "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=800&auto=format&fit=crop&q=80",
        "title": "College Campus",
        "subtitle": "Panoramic Aerial View of Green Campus",
        "gradient": ("#0F172A", "#1E40AF"),
        "icon": "🌲"
    },

    # 2. Admissions
    "admissions_desk.jpg": {
        "url": "https://images.unsplash.com/photo-1577495508048-b635879837f1?w=800&auto=format&fit=crop&q=80",
        "title": "Admissions Cell",
        "subtitle": "Counseling & Application Guidance",
        "gradient": ("#065F46", "#059669"),
        "icon": "📝"
    },
    "admissions_hall.jpg": {
        "url": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=800&auto=format&fit=crop&q=80",
        "title": "Admissions Office",
        "subtitle": "Document Verification & Orientation",
        "gradient": ("#047857", "#10B981"),
        "icon": "🎓"
    },

    # 3. Engineering Courses
    "engineering_quad.jpg": {
        "url": "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=800&auto=format&fit=crop&q=80",
        "title": "Engineering Courses",
        "subtitle": "B.Tech Curriculum & Design Projects",
        "gradient": ("#7C2D12", "#EA580C"),
        "icon": "⚙️"
    },
    "courses_seminar.jpg": {
        "url": "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=800&auto=format&fit=crop&q=80",
        "title": "Engineering Courses",
        "subtitle": "Modern Lecture Theatre & Seminars",
        "gradient": ("#C2410C", "#F97316"),
        "icon": "📐"
    },

    # 4. Computer Science Department
    "cs_dept.jpg": {
        "url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800&auto=format&fit=crop&q=80",
        "title": "Computer Science & Engineering",
        "subtitle": "Department Block & Cloud Computing Lab",
        "gradient": ("#1E293B", "#3B82F6"),
        "icon": "💻"
    },
    "cs_coding.jpg": {
        "url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&auto=format&fit=crop&q=80",
        "title": "Computer Science Department",
        "subtitle": "AI Algorithms & Full-Stack Development",
        "gradient": ("#0F172A", "#6366F1"),
        "icon": "⚡"
    },

    # 5. Electronics and Communication Department
    "ece_lab.jpg": {
        "url": "https://images.unsplash.com/photo-1581092335397-9583fe92d232?w=800&auto=format&fit=crop&q=80",
        "title": "ECE Department",
        "subtitle": "VLSI Design & Microcontroller Testbench",
        "gradient": ("#4C1D95", "#7C3AED"),
        "icon": "🔌"
    },
    "ece_circuits.jpg": {
        "url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop&q=80",
        "title": "ECE Department",
        "subtitle": "Signal Processing & Robotics Hardware",
        "gradient": ("#5B21B6", "#8B5CF6"),
        "icon": "📡"
    },

    # 6. Laboratories
    "computer_lab.jpg": {
        "url": "https://images.unsplash.com/photo-1581092921461-eab62e97a780?w=800&auto=format&fit=crop&q=80",
        "title": "Advanced Research Labs",
        "subtitle": "High-Performance AI & Data Computing",
        "gradient": ("#134E4A", "#0D9488"),
        "icon": "🔬"
    },
    "research_lab.jpg": {
        "url": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=800&auto=format&fit=crop&q=80",
        "title": "Innovation Labs",
        "subtitle": "Prototyping & Maker Space Workstations",
        "gradient": ("#115E59", "#14B8A6"),
        "icon": "🧪"
    },

    # 7. Library
    "library.jpg": {
        "url": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=800&auto=format&fit=crop&q=80",
        "title": "Central Digital Library",
        "subtitle": "Quiet Study Pods & Reading Commons",
        "gradient": ("#78350F", "#D97706"),
        "icon": "📚"
    },
    "library_reading.jpg": {
        "url": "https://images.unsplash.com/photo-1568667256549-094345857637?w=800&auto=format&fit=crop&q=80",
        "title": "Library Repositories",
        "subtitle": "IEEE, Springer & 50,000+ Textbooks",
        "gradient": ("#92400E", "#F59E0B"),
        "icon": "📖"
    },

    # 8. Hostel Facilities
    "hostel.jpg": {
        "url": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800&auto=format&fit=crop&q=80",
        "title": "Hostel Facilities",
        "subtitle": "Furnished Living Quarters with High-Speed Wi-Fi",
        "gradient": ("#831843", "#DB2777"),
        "icon": "🏢"
    },
    "hostel_dining.jpg": {
        "url": "https://images.unsplash.com/photo-1543007630-9710e4a00a20?w=800&auto=format&fit=crop&q=80",
        "title": "Hostel Dining Mess",
        "subtitle": "Hygienic 4-Meal Multi-Cuisine Dining Hall",
        "gradient": ("#9D174D", "#EC4899"),
        "icon": "🍽️"
    },

    # 9. Transportation
    "transport_bus.jpg": {
        "url": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=800&auto=format&fit=crop&q=80",
        "title": "Campus Transportation",
        "subtitle": "Air-Conditioned Fleet of 30+ College Buses",
        "gradient": ("#1E3A8A", "#0284C7"),
        "icon": "🚌"
    },
    "transport_parking.jpg": {
        "url": "https://images.unsplash.com/photo-1506521781263-d8422e82f27a?w=800&auto=format&fit=crop&q=80",
        "title": "Transit Hub & Parking",
        "subtitle": "Convenient Commute Routes Across City",
        "gradient": ("#0369A1", "#38BDF8"),
        "icon": "🅿️"
    },

    # 10. Sports Facilities
    "sports.jpg": {
        "url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800&auto=format&fit=crop&q=80",
        "title": "Sports Arena",
        "subtitle": "Synthetic Athletic Track, Turf & Ground",
        "gradient": ("#14532D", "#16A34A"),
        "icon": "⚽"
    },
    "sports_indoor.jpg": {
        "url": "https://images.unsplash.com/photo-1517649763962-0c623266ddc0?w=800&auto=format&fit=crop&q=80",
        "title": "Indoor Sports Complex",
        "subtitle": "Badminton, Basketball & Fitness Gymnasium",
        "gradient": ("#166534", "#22C55E"),
        "icon": "🏸"
    },

    # 11. Cultural Events
    "cultural_fest.jpg": {
        "url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&auto=format&fit=crop&q=80",
        "title": "Cultural Events",
        "subtitle": "Annual 'VR Fest' Inter-College Extravaganza",
        "gradient": ("#701A75", "#C026D3"),
        "icon": "🎉"
    },
    "cultural_music.jpg": {
        "url": "https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=800&auto=format&fit=crop&q=80",
        "title": "Fine Arts & Clubs",
        "subtitle": "Music Band, Theatre, Dance & Media Society",
        "gradient": ("#86198F", "#D946EF"),
        "icon": "🎭"
    },

    # 12. Technical Symposiums
    "tech_symposium.jpg": {
        "url": "https://images.unsplash.com/photo-1505373877841-8d25f7d46678?w=800&auto=format&fit=crop&q=80",
        "title": "Technical Symposium",
        "subtitle": "National Hackathon & Engineering Conclave",
        "gradient": ("#1E1B4B", "#4F46E5"),
        "icon": "💡"
    },
    "tech_expo.jpg": {
        "url": "https://images.unsplash.com/photo-1511578314322-379afb476865?w=800&auto=format&fit=crop&q=80",
        "title": "Project Innovation Expo",
        "subtitle": "Robotics, IoT & Patent Showcase",
        "gradient": ("#312E81", "#6366F1"),
        "icon": "🤖"
    },

    # 13. Placements
    "placement_drive.jpg": {
        "url": "https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=800&auto=format&fit=crop&q=80",
        "title": "Corporate Placements",
        "subtitle": "Campus Recruitment with 150+ Top Tier MNCs",
        "gradient": ("#1E3A8A", "#1D4ED8"),
        "icon": "💼"
    },
    "students_group.jpg": {
        "url": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=800&auto=format&fit=crop&q=80",
        "title": "Placed Graduates",
        "subtitle": "92% Placement Record | Highest CTC ₹14 LPA",
        "gradient": ("#1D4ED8", "#3B82F6"),
        "icon": "🤝"
    },

    # 14. Scholarships
    "students_hero.jpg": {
        "url": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=1000&auto=format&fit=crop&q=80",
        "title": "Scholarships & Financial Aid",
        "subtitle": "Merit, Sports & Category Concessions",
        "gradient": ("#854D0E", "#CA8A04"),
        "icon": "🏆"
    },
    "scholarship_convocation.jpg": {
        "url": "https://images.unsplash.com/photo-1627556704302-624286467c65?w=800&auto=format&fit=crop&q=80",
        "title": "Merit Felicitation",
        "subtitle": "Tuition Fee Waivers for Top Rankers",
        "gradient": ("#A16207", "#EAB308"),
        "icon": "📜"
    },

    # 15. Faculty and Classrooms
    "classroom_smart.jpg": {
        "url": "https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=800&auto=format&fit=crop&q=80",
        "title": "Smart Digital Classrooms",
        "subtitle": "Air-Conditioned Interactive Multimedia Spaces",
        "gradient": ("#312E81", "#4338CA"),
        "icon": "🖥️"
    },
    "faculty_discussion.jpg": {
        "url": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=800&auto=format&fit=crop&q=80",
        "title": "Faculty & Mentorship",
        "subtitle": "Ph.D. Professors & Dedicated Student Guidance",
        "gradient": ("#3730A3", "#6366F1"),
        "icon": "👨‍🏫"
    }
}


def generate_styled_image(filename: str, meta: dict):
    """Generates a high-resolution branded poster image using Pillow when offline."""
    filepath = os.path.join(ASSETS_DIR, filename)
    width, height = 800, 480
    c1_hex, c2_hex = meta.get("gradient", ("#1E3A8A", "#3B82F6"))

    # Convert hex to RGB
    c1 = tuple(int(c1_hex.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    c2 = tuple(int(c2_hex.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

    img = Image.new("RGB", (width, height), color=c1)
    draw = ImageDraw.Draw(img)

    # Vertical gradient fill
    for y in range(height):
        ratio = y / float(height)
        r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
        g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
        b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Decorative geometry
    draw.rounded_rectangle([(40, 40), (width - 40, height - 40)], radius=24, outline="#FFFFFF", width=3)
    draw.rounded_rectangle([(60, 60), (width - 60, height - 60)], radius=18, outline=(255, 255, 255, 60), width=1)

    # Header badge
    draw.rounded_rectangle([(70, 70), (450, 120)], radius=12, fill="#FFFFFF")
    draw.text((85, 82), "🏛️ VR COLLEGE OF ENGINEERING", fill="#1E3A8A")

    # Category title and subtitle
    title = meta.get("title", "Campus Facility")
    subtitle = meta.get("subtitle", "World-class Academic Infrastructure")
    icon = meta.get("icon", "🎓")

    draw.text((70, 160), f"{icon} {title}", fill="#FFFFFF")
    draw.text((70, 210), subtitle, fill="#E2E8F0")

    # Bottom feature pills
    draw.rounded_rectangle([(70, 360), (280, 405)], radius=10, fill=(255, 255, 255, 40), outline="#FFFFFF", width=1)
    draw.text((85, 375), "✨ NAAC 'A+' Campus", fill="#FFFFFF")

    draw.rounded_rectangle([(300, 360), (520, 405)], radius=10, fill=(255, 255, 255, 40), outline="#FFFFFF", width=1)
    draw.text((315, 375), "🌟 Estd. 2005 | AICTE", fill="#FFFFFF")

    draw.rounded_rectangle([(540, 360), (730, 405)], radius=10, fill=(255, 255, 255, 40), outline="#FFFFFF", width=1)
    draw.text((555, 375), "🚀 24/7 Smart Desk", fill="#FFFFFF")

    img.save(filepath, "JPEG", quality=90)
    print(f"Generated fallback image: {filename}")


def download_or_generate_assets():
    """Iterates through all 30 assets, attempting download first, falling back to Pillow generation."""
    for filename, meta in IMAGE_DEFINITIONS.items():
        filepath = os.path.join(ASSETS_DIR, filename)
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            print(f"Asset ready: {filename}")
            continue

        url = meta.get("url")
        downloaded = False
        if url:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=6) as resp:
                    data = resp.read()
                    if len(data) > 5000:
                        with open(filepath, "wb") as f:
                            f.write(data)
                        print(f"Successfully downloaded {filename}")
                        downloaded = True
            except Exception as e:
                print(f"Download note for {filename}: {e}")

        if not downloaded:
            generate_styled_image(filename, meta)


def generate_logo():
    logo_path = os.path.join(ASSETS_DIR, "logo.png")

    width, height = 400, 140
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle([(15, 15), (115, 115)], radius=18, fill="#1E40AF", outline="#1D4ED8", width=2)
    draw.polygon([(65, 35), (100, 52), (65, 68), (30, 52)], fill="#FFFFFF")
    draw.polygon([(45, 62), (65, 75), (85, 62), (85, 70), (65, 83), (45, 70)], fill="#FCD34D")
    draw.line([(95, 54), (98, 78)], fill="#FCD34D", width=2)
    draw.ellipse([(96, 78), (100, 84)], fill="#FCD34D")

    draw.text((135, 28), "VR COLLEGE", fill="#1E40AF")
    draw.text((135, 52), "OF ENGINEERING", fill="#0F172A")
    draw.text((135, 78), "Approved by AICTE | Estd. 2005", fill="#64748B")
    draw.line([(135, 102), (370, 102)], fill="#3B82F6", width=2)

    image.save(logo_path, "PNG")
    print(f"Generated logo at {logo_path}")


if __name__ == "__main__":
    generate_logo()
    download_or_generate_assets()


