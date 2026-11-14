"""
Prospectus PDF Generator for VR College of Engineering.

Creates an official academic brochure and prospectus for students to download.
Output: assets/VR_College_Prospectus_2026.pdf
"""

import os
from fpdf import FPDF

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
PROSPECTUS_PATH = os.path.join(ASSETS_DIR, "VR_College_Prospectus_2026.pdf")


class ProspectusPDF(FPDF):
    def header(self):
        # Top banner background
        self.set_fill_color(30, 58, 138)  # Deep Navy Blue
        self.rect(0, 0, 210, 28, "F")
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 6)
        self.cell(190, 8, "VR COLLEGE OF ENGINEERING", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(191, 219, 254)
        self.cell(190, 6, "Approved by AICTE | Accredited NAAC 'A+' | Official Academic Prospectus 2026-27", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(10)

    def footer(self):
        self.set_y(-18)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 6, "VR College of Engineering, Knowledge Campus, Sector 4 | Helpline: +91 98765 43210 | admissions@vrcollege.edu", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 6, f"Page {self.page_no()}/{{nb}} | Safe Academic Demonstration Document", align="C")


def create_prospectus():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    pdf = ProspectusPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Section Heading helper
    def section_header(title):
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_fill_color(239, 246, 255)
        pdf.set_text_color(30, 58, 138)
        pdf.cell(190, 8, f"  {title}", border="L", fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # 1. Institutional Profile
    section_header("1. ABOUT VR COLLEGE OF ENGINEERING")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(190, 5.5, (
        "Established in 2005, VR College of Engineering is a premier technical institution "
        "spread across 50+ acres of lush green campus. Accredited with NAAC 'A+' grade and approved by AICTE, "
        "the college fosters cutting-edge research in Artificial Intelligence, Cloud Computing, and Sustainable Engineering."
    ))
    pdf.ln(4)

    # 2. Programs Offered & Fee Schedule
    section_header("2. ACADEMIC PROGRAMS & ANNUAL TUITION FEES (2026-27)")
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_fill_color(226, 232, 240)
    pdf.set_text_color(15, 23, 42)
    
    # Table header
    pdf.cell(50, 7, "Program", border=1, fill=True)
    pdf.cell(30, 7, "Duration", border=1, fill=True)
    pdf.cell(70, 7, "Eligibility", border=1, fill=True)
    pdf.cell(40, 7, "Annual Fee", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 8.5)
    programs = [
        ("B.Tech Computer Science (CSE)", "4 Years (8 Sem)", "10+2 with PCM (Min 50%) + Entrance", "Rs. 1,50,000 / Yr"),
        ("B.Tech Electronics & Comm (ECE)", "4 Years (8 Sem)", "10+2 with PCM (Min 50%) + Entrance", "Rs. 1,25,000 / Yr"),
        ("B.Tech Electrical & Electronics (EEE)", "4 Years (8 Sem)", "10+2 with PCM (Min 50%) + Entrance", "Rs. 1,10,000 / Yr"),
        ("B.Tech Mechanical Engineering (ME)", "4 Years (8 Sem)", "10+2 with PCM (Min 50%) + Entrance", "Rs. 1,00,000 / Yr"),
        ("B.Tech Civil Engineering (CE)", "4 Years (8 Sem)", "10+2 with PCM (Min 50%) + Entrance", "Rs. 95,000 / Yr"),
        ("Master of Business Admin (MBA)", "2 Years (4 Sem)", "Graduation (Min 50%) + CAT/MAT", "Rs. 1,20,000 / Yr"),
        ("Master of Computer App (MCA)", "2 Years (4 Sem)", "BCA / B.Sc with Maths (Min 50%)", "Rs. 85,000 / Yr"),
    ]

    for p, d, e, f in programs:
        pdf.cell(50, 6.5, p, border=1)
        pdf.cell(30, 6.5, d, border=1)
        pdf.cell(70, 6.5, e, border=1)
        pdf.cell(40, 6.5, f, border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # 3. Scholarships & Financial Aid
    section_header("3. SCHOLARSHIPS & FINANCIAL ASSISTANCE")
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(190, 5, (
        "* Merit Scholarships: Up to 50% tuition fee waiver for top 5% rankers in entrance exams.\n"
        "* Sports Concession: Full tuition waiver for national and state-level sports medalists.\n"
        "* Government Scholarships: 100% assistance for post-matric and minority scheme applicants.\n"
        "* Fee Installment: Flexible semester-wise split payment options available upon request."
    ))
    pdf.ln(3)

    # 4. Campus Infrastructure & Hostels
    section_header("4. RESIDENTIAL HOSTELS & CAMPUS FACILITIES")
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(190, 5, (
        "* Separate Secure Hostels: Dedicated hostel wings for boys and girls with 24/7 security & CCTV.\n"
        "* Hostel Fee: Rs. 60,000 per year (includes 4-meal hygienic dining mess & Wi-Fi).\n"
        "* Central Digital Library: 50,000+ volumes, IEEE e-journals, open 8:00 AM to 8:00 PM.\n"
        "* Sports Complex: Olympic turf football ground, cricket nets, gym, and badminton arenas."
    ))
    pdf.ln(3)

    # 5. Placements Snapshot
    section_header("5. TRAINING & PLACEMENT RECORD")
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(63, 6, "Highest Package: Rs. 14.0 LPA", border=0)
    pdf.cell(63, 6, "Average Package: Rs. 4.8 LPA", border=0)
    pdf.cell(64, 6, "Placement Rate: 92% Batch", border=0, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.cell(190, 6, "Recruiters: TCS, Infosys, Wipro, Cognizant, Tech Mahindra, Mindtree, and leading AI startups.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # 6. How to Apply
    section_header("6. ADMISSIONS DESK & COUNSELING HELPLINE")
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(190, 5, (
        "Prospective candidates can apply online through the college portal or walk in to the Admissions Cell.\n"
        "Address: VR College of Engineering, Knowledge Campus, Sector 4, Education City.\n"
        "Helpline Phone: +91 98765 43210 | Landline: 0123-456789 | Email: admissions@vrcollege.edu\n"
        "Office Hours: Monday to Friday: 9:00 AM - 5:00 PM | Saturday: 9:00 AM - 1:00 PM."
    ))

    pdf.output(PROSPECTUS_PATH)
    print(f"Prospectus PDF created successfully at: {PROSPECTUS_PATH}")


if __name__ == "__main__":
    create_prospectus()

