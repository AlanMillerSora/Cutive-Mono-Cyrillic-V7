#!/usr/bin/env python3
"""Build the specimen images shipped with the project.

Rendering goes through pango-view so that fontconfig fallback is real:
the "before" images use the untouched original font, where Cyrillic is
served by the system fallback, exactly as it happens today.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "specimens"
ORIG = ROOT / "source" / "original"
NEW = ROOT / "fonts" / "CutiveMono-Cyrillic-Regular.ttf"

LATIN = [
    "The quick brown fox jumps over the lazy dog.",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "abcdefghijklmnopqrstuvwxyz",
    "0123456789 !?.,:;()[]{}«»—–…№₽",
]

CYR = [
    "Съешь же ещё этих мягких французских булок.",
    "В чащах юга жил бы цитрус? Да, но фальшивый экземпляр!",
    "Съешь ещё этих мягких французских булок, да выпей чаю.",
    "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
    "абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
]

MIXED = [
    "English + Русский + 1234567890",
    "Arch Linux — операционная система на базе Linux.",
    '$ git commit -m "Добавлена кириллица"',
    "Ґґ Єє Іі Її Ўў — Українська та білоруська",
    "Ѐѐ Ѝѝ Јј Ѕѕ Ѓѓ Ќќ Љљ Њњ Џџ",
]


def pango(text: str, font: str, out: Path, size: int = 30, fc: Path | None = None,
          bg: str = "#fdfcf8", fg: str = "#1a1a1a") -> Path:
    cmd = ["pango-view", "--no-display", "--font", f"{font} {size}",
           "--text", text, "--output", str(out), "--margin", "0",
           f"--background={bg}"]
    env = None
    if fc:
        import os
        env = dict(os.environ, FONTCONFIG_FILE=str(fc))
    subprocess.run(cmd, check=True, env=env, capture_output=True)
    return out


def orig_fontconfig() -> Path:
    p = Path(tempfile.mkdtemp()) / "orig-fonts.conf"
    p.write_text(f"""<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig>
  <dir>{ORIG}</dir>
  <cachedir>/tmp/fc-cache-orig</cachedir>
  <include ignore_missing="yes">/etc/fonts/fonts.conf</include>
</fontconfig>
""")
    subprocess.run(["fc-cache", "-f"], env={"FONTCONFIG_FILE": str(p)}, check=False,
                   capture_output=True)
    return p


def label(img: Image.Image, text: str, color="#7a2d4a") -> Image.Image:
    try:
        f = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 15)
    except OSError:
        f = ImageFont.load_default()
    out = Image.new("RGB", (img.width, img.height + 26), "#ffffff")
    out.paste(img, (0, 26))
    d = ImageDraw.Draw(out)
    d.text((14, 6), text, font=f, fill=color)
    return out


def stack(images: list[Image.Image], gap: int = 14, bg="#ffffff") -> Image.Image:
    w = max(i.width for i in images)
    h = sum(i.height for i in images) + gap * (len(images) - 1)
    out = Image.new("RGB", (w, h), bg)
    y = 0
    for i in images:
        out.paste(i, (0, y))
        y += i.height + gap
    return out


def main() -> None:
    SPEC.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    fc_orig = orig_fontconfig()

    # 1. latin.png — original vs fork, Latin only
    rows = []
    for title, font, fc in (
        ("Original Cutive Mono", "Cutive Mono", fc_orig),
        ("Cutive Mono Cyrillic (this fork)", "Cutive Mono Cyrillic", None),
    ):
        block = []
        for line in LATIN:
            p = pango(line, font, tmp / "l.png", 34, fc)
            block.append(Image.open(p))
        rows.append(label(stack(block, 8), title))
    stack(rows, 22).save(SPEC / "latin.png")

    # 2. cyrillic.png
    block = []
    for line in CYR:
        p = pango(line, "Cutive Mono Cyrillic", tmp / "c.png", 34)
        block.append(Image.open(p))
    label(stack(block, 10), "Cyrillic — Cutive Mono Cyrillic").save(SPEC / "cyrillic.png")

    # 3. comparison.png — before/after with real fallback
    before, after = [], []
    for line in CYR + MIXED[:3]:
        before.append(Image.open(pango(line, "Cutive Mono", tmp / "b.png", 30, fc_orig)))
        after.append(Image.open(pango(line, "Cutive Mono Cyrillic", tmp / "a.png", 30)))
    img_b = label(stack(before, 8), "BEFORE: original Cutive Mono, Cyrillic falls back")
    img_a = label(stack(after, 8), "AFTER: Cutive Mono Cyrillic")
    stack([img_b, img_a], 24).save(SPEC / "comparison.png")

    # 4. mixed-text.png
    block = [Image.open(pango(line, "Cutive Mono Cyrillic", tmp / "m.png", 34)) for line in MIXED]
    label(stack(block, 10), "Mixed Latin / Cyrillic / extended").save(SPEC / "mixed-text.png")

    # 5. detail-problem-letters.png — the hard letters, enlarged
    letters = "Дд Жж Йй Лл Тт Фф Цц Чч Шш Щщ Ъъ Ыы Ьь Ээ Юю Яя"
    detail = Image.open(pango(letters, "Cutive Mono Cyrillic", tmp / "d.png", 120))
    label(detail, "Hard letters at 120 px").save(SPEC / "detail-problem-letters.png")

    # 6. side-by-side of the same paragraph at text size
    para_en = "Handgloves 0123"
    para_ru = "Съешь ещё 0123"
    a = Image.open(pango(para_en, "Cutive Mono Cyrillic", tmp / "p1.png", 60))
    b = Image.open(pango(para_ru, "Cutive Mono Cyrillic", tmp / "p2.png", 60))
    stack([label(a, "Latin"), label(b, "Cyrillic")], 16).save(SPEC / "same-size.png")


if __name__ == "__main__":
    main()
