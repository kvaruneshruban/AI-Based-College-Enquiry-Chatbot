"""
PDF Project Report Generator for AI-Based College Enquiry Chatbot.

Converts project documentation into a clean, professional, academic PDF report.
Output: documentation/project_report.pdf
"""

import os
import re
from fpdf import FPDF


class ProjectReportPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(100, 116, 139)
            self.cell(0, 10, "AI-Based College Enquiry Chatbot | Mini Project Report", border=0, align="L")
            self.cell(0, 10, "Academic Year 2026-2027", border=0, align="R", new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(226, 232, 240)
            self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
            self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def generate_pdf():
    project_dir = os.path.dirname(__file__)
    md_path = os.path.join(project_dir, "documentation", "project_report.md")
    pdf_path = os.path.join(project_dir, "documentation", "project_report.pdf")

    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found")
        return

    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    pdf = ProjectReportPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    in_code_block = False

    for line in lines:
        raw_line = line.rstrip()

        # Handle code blocks
        if raw_line.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            pdf.set_font("Courier", size=8.5)
            pdf.set_text_color(30, 41, 59)
            # Replace non-latin1 characters with ASCII approximations
            safe_text = raw_line.encode("latin-1", "replace").decode("latin-1")
            pdf.cell(0, 4.5, safe_text, new_x="LMARGIN", new_y="NEXT")
            continue

        # Handle H1 Title
        if raw_line.startswith("# "):
            title = raw_line[2:].strip()
            pdf.set_font("Helvetica", "B", 18)
            pdf.set_text_color(30, 64, 175) # Primary Blue
            safe_title = title.encode("latin-1", "replace").decode("latin-1")
            pdf.ln(5)
            pdf.cell(0, 10, safe_title, align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
            continue

        # Handle H2 Section Headers
        if raw_line.startswith("## "):
            sec_title = raw_line[3:].strip()
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(30, 64, 175)
            safe_sec = sec_title.encode("latin-1", "replace").decode("latin-1")
            pdf.ln(6)
            pdf.cell(0, 8, safe_sec, new_x="LMARGIN", new_y="NEXT")
            pdf.set_draw_color(59, 130, 246)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(3)
            continue

        # Handle H3 Subsections
        if raw_line.startswith("### "):
            sub_title = raw_line[4:].strip()
            pdf.set_font("Helvetica", "B", 10.5)
            pdf.set_text_color(15, 23, 42)
            safe_sub = sub_title.encode("latin-1", "replace").decode("latin-1")
            pdf.ln(4)
            pdf.cell(0, 6, safe_sub, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
            continue

        # Horizontal separator
        if raw_line.startswith("---"):
            pdf.ln(2)
            pdf.set_draw_color(226, 232, 240)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(2)
            continue

        # Handle Table rows (convert cleanly)
        if raw_line.startswith("|"):
            if "---" in raw_line:
                continue
            cells = [c.strip() for c in raw_line.split("|")[1:-1]]
            row_text = " | ".join(cells)
            pdf.set_font("Helvetica", size=7.5)
            pdf.set_text_color(51, 65, 85)
            clean_row = re.sub(r"\*\*|\*", "", row_text).encode("latin-1", "replace").decode("latin-1")
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(pdf.epw, 4.5, clean_row, new_x="LMARGIN", new_y="NEXT")
            continue

        # Regular paragraph text
        if raw_line.strip():
            pdf.set_font("Helvetica", size=9.5)
            pdf.set_text_color(15, 23, 42)
            clean_text = re.sub(r"\*\*|\*", "", raw_line)
            clean_text = clean_text.replace("→", "->").replace("✓", "V").replace("—", "-")
            safe_text = clean_text.encode("latin-1", "replace").decode("latin-1")
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(pdf.epw, 5, safe_text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        else:
            pdf.ln(2)

    pdf.output(pdf_path)
    print(f"Generated PDF report at {pdf_path}")


if __name__ == "__main__":
    generate_pdf()
