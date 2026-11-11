"""
Script to generate a professional College Logo placeholder (assets/logo.png).
"""

import os
from PIL import Image, ImageDraw, ImageFont

def generate_logo():
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    logo_path = os.path.join(assets_dir, "logo.png")

    width, height = 400, 140
    # Create image with transparent or white background
    image = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Draw rounded rectangle badge / emblem background
    draw.rounded_rectangle([(15, 15), (115, 115)], radius=18, fill="#1E40AF", outline="#1D4ED8", width=2)

    # Draw graduation cap / college emblem inside badge
    # Cap diamond
    draw.polygon([(65, 35), (100, 52), (65, 68), (30, 52)], fill="#FFFFFF")
    # Cap lower band
    draw.polygon([(45, 62), (65, 75), (85, 62), (85, 70), (65, 83), (45, 70)], fill="#FCD34D")
    # Tassel
    draw.line([(95, 54), (98, 78)], fill="#FCD34D", width=2)
    draw.ellipse([(96, 78), (100, 84)], fill="#FCD34D")

    # College Title Text
    # Since default PIL font is always available:
    draw.text((135, 28), "APEX INSTITUTE", fill="#1E40AF")
    draw.text((135, 52), "OF TECHNOLOGY & SCIENCE", fill="#0F172A")
    draw.text((135, 78), "Approved by AICTE | Estd. 2005", fill="#64748B")

    # Underline accent
    draw.line([(135, 102), (370, 102)], fill="#3B82F6", width=2)

    image.save(logo_path, "PNG")
    print(f"Generated logo at {logo_path}")

if __name__ == "__main__":
    generate_logo()

