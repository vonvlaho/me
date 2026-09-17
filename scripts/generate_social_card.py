"""Render the text-only social card. Requires Pillow; run on macOS."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FONT = "/System/Library/Fonts/Helvetica.ttc"


def main():
    image = Image.new("RGB", (1200, 630), "white")
    draw = ImageDraw.Draw(image)
    for text, position, size, color in [
        ("Frederic von Vlahovits", (96, 148), 44, "#222222"),
        ("Musicologist and founder in Berlin.", (96, 236), 30, "#222222"),
        ("I build tools for knowledge work.", (96, 296), 30, "#222222"),
        ("vlahovits.com", (96, 476), 24, "#707070"),
    ]:
        draw.text(position, text, font=ImageFont.truetype(FONT, size), fill=color)
    image.save(ROOT / "assets/img/social.png", optimize=True)


if __name__ == "__main__":
    main()
