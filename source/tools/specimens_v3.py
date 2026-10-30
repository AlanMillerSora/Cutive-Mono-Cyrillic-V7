#!/usr/bin/env python3
"""V3 specimen set (A–E, G). Real terminal shots are added as F-*.png."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "specimens" / "v3"
FONT = ROOT / "fonts" / "CutiveMono-Cyrillic-Regular.ttf"
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
LAT = "ABCDEFGHIJKLMNOPQRSTUVWXYZ\nabcdefghijklmnopqrstuvwxyz"

ANNOT = [
    ("Д д", "верхняя перекладина уже, лапки-засечки, база шире"),
    ("Ж ж", "ветви крепятся к краям стема — узел разгружен"),
    ("Л л", "нога 13–14°, широкая стопа как у r"),
    ("Т т", "чистая перекладина, широкая стопа"),
    ("Ф ф", "чаша из O/o, ось строго по центру"),
    ("Ц ц", "вынос 300, стопа 220"),
    ("Ч ч", "перекладина на 650, стопа как у u"),
    ("Ш ш", "засечки 235 — зубцы не слипаются"),
    ("Щ щ", "4 стема, засечки 205, хвост читается"),
    ("Ъ ъ", "чаша o, база под стемом"),
    ("Ы ы", "правая стойка отодвинута, засечки 200"),
    ("Ь ь", "чаша o, ровный стык со стемом"),
    ("Э э", "перекладина 665–1040, ровный изгиб"),
    ("Ю ю", "чаша 800, перекладина подходит к счётчику"),
    ("Я я", "нога выходит из-под чаши, не режет счётчик"),
]


def lf(size=16, bold=False):
    try:
        return ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def text_img(text, size, font=FONT, pad=20, color=INK):
    f = ImageFont.truetype(str(font), size)
    asc, desc = f.getmetrics()
    im = Image.new("RGB", (int(f.getlength(text)) + pad * 2, asc + desc + pad), BG)
    ImageDraw.Draw(im).text((pad, pad // 2), text, font=f, fill=color)
    return im


def title(text, width, sub=""):
    im = Image.new("RGB", (width, 48 if sub else 30), "#ffffff")
    d = ImageDraw.Draw(im)
    d.text((16, 6), text, font=lf(15), fill=ACC)
    if sub:
        d.text((16, 26), sub, font=lf(12), fill="#8a8a8a")
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


def a_alphabet():
    parts = [title("A. Alphabets — 84 px", 1700)]
    for s in (CAPS, LOWS):
        parts.append(text_img(s, 84))
    for line in LAT.split("\n"):
        parts.append(text_img(line, 84))
    return vstack(parts)


def b_v2_v3():
    parts = [title("B. V2 vs V3 — problem letters", 2430)]
    for name, font in (("V2", V2), ("V3", FONT)):
        parts.append(title(name, 2430))
        parts.append(text_img(HARD, 120, font))
    return vstack(parts)


def c_latin_cyr():
    parts = [title("C. Latin vs Cyrillic — 40 px", 1600)]
    for t in (EN1, RU1, RU2):
        parts.append(text_img(t, 40))
    return vstack(parts)


def d_small():
    parts = [title("D. Sizes 11–24 px (11–16 ×3 nearest, 18/24 natural)", 1700)]
    for s in (11, 12, 13, 14, 16):
        im = text_img("Съешь ещё 0123 — The quick brown fox", s, pad=10)
        im = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
        parts.append(im)
    for s in (18, 24):
        parts.append(text_img("Съешь ещё 0123 — The quick brown fox", s, pad=12))
    return vstack(parts)


def e_mixed():
    parts = [title("E. Mixed text", 1600)]
    for t in (MIX1, MIX2, MIX3, RU3):
        parts.append(text_img(t, 38))
    return vstack(parts)


def g_annotated():
    cols, rows = 3, 5
    cw, ch = 620, 300
    out = Image.new("RGB", (cw * cols, ch * rows + 30), "#ffffff")
    d = ImageDraw.Draw(out)
    d.text((16, 8), "G. What changed in V3", font=lf(15), fill=ACC)
    for i, (glyph, note) in enumerate(ANNOT):
        r, c = divmod(i, cols)
        x, y = c * cw, 30 + r * ch
        d.rectangle([x, y, x + cw - 6, y + ch - 6], outline="#ececec")
        gimg = text_img(glyph, 120, pad=8)
        out.paste(gimg, (x + 12, y + 16))
        d.text((x + 14, y + ch - 78), note, font=lf(13), fill="#555555")
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    a_alphabet().save(OUT / "A-alphabets.png")
    b_v2_v3().save(OUT / "B-v2-vs-v3.png")
    c_latin_cyr().save(OUT / "C-latin-vs-cyrillic.png")
    d_small().save(OUT / "D-sizes-11-24.png")
    e_mixed().save(OUT / "E-mixed-text.png")
    g_annotated().save(OUT / "G-glyph-notes.png")
    print("ok")


if __name__ == "__main__":
    main()
