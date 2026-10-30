#!/usr/bin/env python3
"""V4 specimens: A–E, G generated; F from real terminal screenshots."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "specimens" / "v4"
NEW = ROOT / "fonts" / "CutiveMono-Cyrillic-Regular.ttf"
V3 = ROOT / "backup" / "v3-fonts" / "CutiveMono-Cyrillic-Regular.ttf"
V2 = ROOT / "backup" / "v2-fonts" / "CutiveMono-Cyrillic-Regular.ttf"
BG, INK, ACC = "#fdfcf8", "#171717", "#7a2d4a"

EN1 = "The quick brown fox jumps over the lazy dog."
RU1 = "Съешь же ещё этих мягких французских булок."
RU2 = "В чащах юга жил бы цитрус? Да, но фальшивый экземпляр!"
RU3 = "Съешь ещё этих мягких французских булок, да выпей чаю."
MIX1 = "English + Русский + 1234567890"
MIX2 = "Arch Linux — операционная система на базе Linux."
MIX3 = '$ git commit -m "Добавлена кириллица"'

CAPS = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
LOWS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
HARD = "Дд Жж Лл Тт Фф Цц Чч Шш Щщ Ъъ Ыы Ьь Ээ Юю Яя"


def lf(size=16):
    try:
        return ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def text_img(text, size, font=NEW, pad=20):
    f = ImageFont.truetype(str(font), size)
    asc, desc = f.getmetrics()
    im = Image.new("RGB", (int(f.getlength(text)) + pad * 2, asc + desc + pad), BG)
    ImageDraw.Draw(im).text((pad, pad // 2), text, font=f, fill=INK)
    return im


def title(text, width, sub=""):
    im = Image.new("RGB", (width, 46 if sub else 30), "#ffffff")
    d = ImageDraw.Draw(im)
    d.text((16, 5), text, font=lf(15), fill=ACC)
    if sub:
        d.text((16, 25), sub, font=lf(12), fill="#8a8a8a")
    return im


def vstack(imgs, gap=10):
    w = max(i.width for i in imgs)
    h = sum(i.height for i in imgs) + gap * (len(imgs) - 1)
    out = Image.new("RGB", (w, h), "#ffffff")
    y = 0
    for i in imgs:
        out.paste(i, (0, y))
        y += i.height + gap
    return out


def a_alphabets():
    parts = [title("A. Alphabets — 80 px (Latin + Cyrillic, one font)", 1800)]
    parts += [text_img(s, 80) for s in (CAPS, LOWS,
              "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
              "abcdefghijklmnopqrstuvwxyz")]
    return vstack(parts)


def b_versions():
    parts = [title("B. V2 / V3 / V4 — the letters that changed", 2600)]
    for name, path in (("V2", V2), ("V3 (installed)", V3)):
        if path.exists():
            parts.append(title(name, 2600))
            parts.append(text_img(HARD, 110, path))
    parts.append(title("V4 (candidate, not installed)", 2600))
    parts.append(text_img(HARD, 110))
    return vstack(parts)


def c_latin_cyr():
    parts = [title("C. Latin vs Cyrillic — 36 px", 1600)]
    for t in (EN1, RU1, RU2):
        parts.append(text_img(t, 36))
    return vstack(parts)


def d_sizes():
    parts = [title("D. Sizes — 11/12/13/14/16 ×3 nearest, 18/24 natural", 1700)]
    for s in (11, 12, 13, 14, 16):
        im = text_img("Съешь ещё 0123 — The quick brown fox", s, pad=10)
        parts.append(im.resize((im.width * 3, im.height * 3), Image.NEAREST))
    for s in (18, 24):
        parts.append(text_img("Съешь ещё 0123 — The quick brown fox", s, pad=12))
    return vstack(parts)


def e_mixed():
    parts = [title("E. Mixed paragraphs", 1600)]
    for t in (MIX1, MIX2, MIX3, RU3):
        parts.append(text_img(t, 36))
    return vstack(parts)


ANNOT = [
    ("з / З", "шире: 661/950 вместо 498/567 — как s и C"),
    ("ш / Щ", "шире, засечки 230/200 — ритм как у m"),
    ("ь ъ ы", "чаши 660/650/580, стена стыка залита"),
    ("г / т", "стопа 540/560, как у r и t"),
    ("ц / ч", "вынос 280, стопа 420"),
    ("Ж", "ветви от краёв стема, узел легче"),
    ("Ю", "чаша 800, перекладина до счётчика"),
    ("Я", "нога из-под чаши, не режет счётчик"),
]


def g_notes():
    cols = 3
    cw, ch = 640, 300
    rows = (len(ANNOT) + cols - 1) // cols
    out = Image.new("RGB", (cw * cols, ch * rows + 30), "#ffffff")
    d = ImageDraw.Draw(out)
    d.text((16, 8), "G. V4 changes and why", font=lf(15), fill=ACC)
    for i, (glyph, note) in enumerate(ANNOT):
        r, c = divmod(i, cols)
        x, y = c * cw, 30 + r * ch
        d.rectangle([x, y, x + cw - 6, y + ch - 6], outline="#ececec")
        out.paste(text_img(glyph, 110, pad=8), (x + 12, y + 16))
        d.text((x + 14, y + ch - 80), note, font=lf(13), fill="#555555")
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    a_alphabets().save(OUT / "A-alphabets.png")
    b_versions().save(OUT / "B-v2-v3-v4.png")
    c_latin_cyr().save(OUT / "C-latin-vs-cyrillic.png")
    d_sizes().save(OUT / "D-sizes.png")
    e_mixed().save(OUT / "E-mixed.png")
    g_notes().save(OUT / "G-notes.png")
    print("ok")


if __name__ == "__main__":
    main()
