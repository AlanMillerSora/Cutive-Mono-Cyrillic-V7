#!/usr/bin/env python3
"""V6 specimens: V5/V6 pairs for the changed glyphs, alphabets, sizes.

A  changed letters side by side (V5 above, V6 below)
B  capitals
C  lowercase
D  joints and bowls at 150 px  (the main V6 fix)
E  sentences at 34 px
F  sizes 11-24 px
G  terminal block at 14 px, V5 vs V6
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "specimens" / "v6"
V6 = ROOT / "fonts" / "CutiveMono-Cyrillic-Regular.ttf"
V5 = ROOT / "backup" / "v5-fonts" / "CutiveMono-Cyrillic-Regular.ttf"
BG, INK, ACC = "#fdfcf8", "#171717", "#7a2d4a"

EN1 = "The quick brown fox jumps over the lazy dog."
RU1 = "Съешь же ещё этих мягких французских булок."
RU2 = "В чащах юга жил бы цитрус? Да, но фальшивый экземпляр!"
RU3 = "Дом. Жизнь. Это. Яблоко."
MIX1 = "English + Русский + 1234567890"
MIX2 = "Arch Linux — операционная система на базе Linux."
MIX3 = '$ git commit -m "Добавлена кириллица"'
CAPS = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
LOWS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
TERM = [
    "[sora@archeclipse ~]$ ls -la ~/Проекты",
    "итого 48   кириллица  шрифт  ячейка",
    "drwxr-xr-x  каталог  Жизнь  ЪЫЬ  бюджет",
    "error: файл «Здание.otf» не найден",
]


def lf(size=15):
    return ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", size)


def line(text, size, font=V6, pad=16):
    f = ImageFont.truetype(str(font), size)
    asc, desc = f.getmetrics()
    im = Image.new("RGB", (int(f.getlength(text)) + pad * 2, asc + desc + pad), BG)
    ImageDraw.Draw(im).text((pad, pad // 2), text, font=f, fill=INK)
    return im


def lab(text, width):
    im = Image.new("RGB", (width, 26), "#ffffff")
    ImageDraw.Draw(im).text((12, 4), text, font=lf(), fill=ACC)
    return im


def stack(imgs, gap=8):
    w = max(i.width for i in imgs)
    h = sum(i.height for i in imgs) + gap * (len(imgs) - 1)
    out = Image.new("RGB", (w, h), "#ffffff")
    y = 0
    for i in imgs:
        out.paste(i, (0, y))
        y += i.height + gap
    return out


def a_pairs():
    rows = [lab("К к · З з · Д — V5 против V6 (54 px)", 1500)]
    for name, font in (("V5", V5), ("V6", V6)):
        rows.append(lab(name, 1500))
        rows.append(line("Как жизнь? Здание, экземпляр, Дом", 54, font))
        rows.append(line(RU1, 34, font))
    return stack(rows)


def b_caps():
    rows = [lab("Заглавные — 76 px", 1800)]
    rows.append(line(CAPS, 76))
    rows.append(line("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 76))
    return stack(rows)


def c_lows():
    rows = [lab("Строчные — 76 px", 1800)]
    rows.append(line(LOWS, 76))
    rows.append(line("abcdefghijklmnopqrstuvwxyz", 76))
    return stack(rows)


def d_joints():
    rows = [lab("Стыки чаш и стема — 150 px, V5 сверху, V6 снизу", 2400)]
    for name, font in (("V5", V5), ("V6", V6)):
        rows.append(lab(name, 2400))
        rows.append(line("БЪЫЬ бвъыь я Ж Д", 150, font))
    return stack(rows)


def e_sentences():
    rows = [lab("Предложения — 34 px", 1700)]
    for t in (EN1, RU1, RU2, RU3, MIX1, MIX2, MIX3):
        rows.append(line(t, 34))
    return stack(rows)


def f_sizes():
    rows = [lab("Кегли 11–24 px (11–16 ×3, 20/24 ×1)", 1800)]
    for s in (11, 12, 13, 14, 16):
        im = line("Съешь ещё как жизнь 0123 — The quick brown fox", s, pad=10)
        rows.append(im.resize((im.width * 3, im.height * 3), Image.NEAREST))
    for s in (20, 24):
        rows.append(line("Съешь ещё как жизнь 0123 — The quick brown fox", s, pad=12))
    return stack(rows)


def g_terminal():
    rows = [lab("Терминал — 14 px, V5 сверху, V6 снизу", 2000)]
    for name, font in (("V5", V5), ("V6", V6)):
        rows.append(lab(name, 2000))
        for t in TERM:
            im = line(t, 14, font, pad=10)
            rows.append(im.resize((im.width * 2, im.height * 2), Image.NEAREST))
    return stack(rows)


def h_hinting():
    """Same outlines, hinting on/off, at the size the terminal uses."""
    import tempfile
    from fontTools.ttLib import TTFont

    tmp = Path(tempfile.mkdtemp()) / "unhinted.ttf"
    f = TTFont(V6)
    glyf = f["glyf"]
    for name in f.getGlyphOrder():
        prog = getattr(glyf[name], "program", None)
        if prog is not None:
            prog.fromBytecode(b"")
    f.save(tmp)

    rows = [lab("Хинтинг: без него V6 и с ним — 14 px, ×3", 2000)]
    for name, font in (("без hinting (так было)", tmp), ("с ttfautohint (V6)", V6)):
        rows.append(lab(name, 2000))
        for t in ("Съешь же ещё этих мягких французских булок.",
                  "The quick brown fox jumps over the lazy dog.",
                  "Как жизнь? Здание, экземпляр, Дом."):
            im = line(t, 14, font, pad=8)
            rows.append(im.resize((im.width * 3, im.height * 3), Image.NEAREST))
    return stack(rows)


def i_polish():
    """V6 as installed vs V6 after the polish round (same outline set)."""
    old = ROOT / "backup" / "v6-fonts" / "CutiveMono-Cyrillic-Regular.ttf"
    if not old.exists():
        return None
    rows = [lab("Полировка V6: до и после (15 px ×3 и 100 px)", 2200)]
    for name, font in (("V6 до полировки", old), ("V6 после полировки", V6)):
        rows.append(lab(name, 2200))
        for t in ("Съешь же ещё этих мягких французских булок.",
                  "Как жизнь? Здание, экземпляр, Дом, Яблоко."):
            im = line(t, 15, font, pad=8)
            rows.append(im.resize((im.width * 3, im.height * 3), Image.NEAREST))
        rows.append(line("Б Г П Ч Ц Ь Ъ Ы Ю — засечки;  у я Л — стыки", 100, font))
    return stack(rows)


def j_tse():
    """Ц/ц: 6.010 (П + хвост) vs U-образное тело (П перевёрнутая) + хвост Щ."""
    old = ROOT / "backup" / "v6-pre-tse-fonts" / "CutiveMono-Cyrillic-Regular.ttf"
    if not old.exists():
        return None
    rows = [lab("Ц и ц: 6.010 (сверху) и 6.020 — U-образное тело + хвост как у Щ (снизу)", 2400)]
    for name, font in (("6.010", old), ("6.020", V6)):
        rows.append(lab(name, 2400))
        rows.append(line("П Ц Щ  п ц щ", 120, font))
        rows.append(line("Царь, цена, лицо, конец, отец, молодцы, цирк, цифра, станция, нация.", 34, font))
        rows.append(line("В чащах юга жил бы цитрус? Да, но фальшивый экземпляр!", 34, font))
        rows.append(line("Цена циркуля — 1234 ₽. The quick brown fox.", 34, font))
        for t in ("цена цирк конец молодцы", "The quick brown fox 0123"):
            im = line(t, 14, font, pad=8)
            rows.append(im.resize((im.width * 3, im.height * 3), Image.NEAREST))
    return stack(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    a_pairs().save(OUT / "A-v5-v6.png")
    b_caps().save(OUT / "B-caps.png")
    c_lows().save(OUT / "C-lowercase.png")
    d_joints().save(OUT / "D-joints.png")
    e_sentences().save(OUT / "E-sentences.png")
    f_sizes().save(OUT / "F-sizes.png")
    g_terminal().save(OUT / "G-terminal.png")
    h_hinting().save(OUT / "H-hinting.png")
    p = i_polish()
    if p is not None:
        p.save(OUT / "I-polish.png")
    p = j_tse()
    if p is not None:
        p.save(OUT / "J-tse.png")
    print("ok")


if __name__ == "__main__":
    main()
