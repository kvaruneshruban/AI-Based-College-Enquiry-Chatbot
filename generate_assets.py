"""
Script to generate and maintain professional College Assets (logo & campus photography).
"""

import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont

def generate_logo():
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    logo_path = os.path.join(assets_dir, "logo.png")

    width, height = 400, 140
    # Create image with transparent background
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Draw rounded rectangle badge / emblem background
    draw.rounded_rectangle([(15, 15), (115, 115)], radius=18, fill="#1E40AF", outline="#1D4ED8", width=2)

    # Draw graduation cap / college emblem inside badge
    draw.polygon([(65, 35), (100, 52), (65, 68), (30, 52)], fill="#FFFFFF")
    draw.polygon([(45, 62), (65, 75), (85, 62), (85, 70), (65, 83), (45, 70)], fill="#FCD34D")
    draw.line([(95, 54), (98, 78)], fill="#FCD34D", width=2)
    draw.ellipse([(96, 78), (100, 84)], fill="#FCD34D")

    # College Title Text
    draw.text((135, 28), "APEX INSTITUTE", fill="#1E40AF")
    draw.text((135, 52), "OF TECHNOLOGY & SCIENCE", fill="#0F172A")
    draw.text((135, 78), "Approved by AICTE | Estd. 2005", fill="#64748B")
    draw.line([(135, 102), (370, 102)], fill="#3B82F6", width=2)

    image.save(logo_path, "PNG")
    print(f"Generated logo at {logo_path}")


def download_campus_images():
    """Ensures high-resolution campus photography is present in assets."""
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(assets_dir, exist_ok=True)

    images = {
        "campus_main.jpg": "https://images.unsplash.com/photo-1562774053-701939374585?w=800&auto=format&fit=crop&q=80",
        "library.jpg": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=800&auto=format&fit=crop&q=80",
        "computer_lab.jpg": "https://images.unsplash.com/photo-1581092921461-eab62e97a780?w=800&auto=format&fit=crop&q=80",
        "hostel.jpg": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800&auto=format&fit=crop&q=80",
        "sports.jpg": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800&auto=format&fit=crop&q=80",
        "students_hero.jpg": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=1000&auto=format&fit=crop&q=80",
        "students_group.jpg": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=800&auto=format&fit=crop&q=80"
    }

    for name, url in images.items():
        path = os.path.join(assets_dir, name)
        if not os.path.exists(path):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as resp, open(path, "wb") as f:
                    f.write(resp.read())
                print(f"Downloaded {name}")
            except Exception as e:
                print(f"Could not download {name}: {e}")
        else:
            print(f"Image exists: {name}")


if __name__ == "__main__":
    generate_logo()
    download_campus_images()

