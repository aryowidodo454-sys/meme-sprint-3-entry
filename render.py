#!/usr/bin/env python3
"""Render Meme Sprint 3 entry: caption bands + art -> 1024x1024 PNG."""
from PIL import Image, ImageDraw, ImageFont
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "assets", "media-generation-cand-a-ducks-0-a060c3e2-5b86-47dc-8d09-bb32360d85ae.webp")
OUT = os.path.join(HERE, "entry.png")
PREVIEW = os.path.join(HERE, "drafts", "entry-300.png")
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

W = H = 1024
TOP_BAND = 170
BOT_BAND = 180
ART_H = H - TOP_BAND - BOT_BAND

TOP_LINES = ["I ASKED MY AGENT", "TO SAVE ME MONEY"]
BOT_LINES = ["IT SOLD MY CAR.", "WENT ALL-IN ON DUCKS."]
BUBBLE_LINES = ["4,000 DUCKS.", "THEY ONLY GO UP."]


def fit_font(draw, text, max_w, start=92):
    size = start
    while size > 20:
        f = ImageFont.truetype(FONT_PATH, size)
        if draw.textlength(text, font=f) <= max_w:
            return f, size
        size -= 4
    return ImageFont.truetype(FONT_PATH, 20), 20


def main():
    art = Image.open(ART).convert("RGB")
    aw, ah = art.size
    # Crop away the plain beige bands: keep middle 62% vertically.
    top_crop = int(ah * 0.182)
    bot_crop = int(ah * 0.848)
    art = art.crop((0, top_crop, aw, bot_crop))
    # Fit whole art height into the art area so feet stay whole;
    # stretch the last few percent horizontally (imperceptible) to fill width.
    art = art.resize((W, ART_H), Image.LANCZOS)

    img = Image.new("RGB", (W, H), (0, 0, 0))
    img.paste(art, (0, TOP_BAND))
    d = ImageDraw.Draw(img)

    # Speech bubble for the agent: white, black border, tail to robot mouth.
    bx0, by0, bx1, by1 = 238, TOP_BAND + 6, 578, TOP_BAND + 118
    d.polygon([(332, by1 - 4), (370, by1 - 4), (274, TOP_BAND + 258)], fill=(255, 255, 255), outline=(0, 0, 0), width=5)
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=28, fill=(255, 255, 255), outline=(0, 0, 0), width=5)
    bsizes = []
    for line in BUBBLE_LINES:
        _, sz = fit_font(d, line, (bx1 - bx0) - 36, start=52)
        bsizes.append(sz)
    bsize = min(bsizes)
    fb = ImageFont.truetype(FONT_PATH, bsize)
    bline_h = int(bsize * 1.15)
    by = by0 + ((by1 - by0) - bline_h * len(BUBBLE_LINES)) / 2
    for i, line in enumerate(BUBBLE_LINES):
        tw = d.textlength(line, font=fb)
        d.text((bx0 + ((bx1 - bx0) - tw) / 2, by + i * bline_h), line, font=fb, fill=(0, 0, 0))

    # Top: two lines, same size.
    top_sizes = []
    for line in TOP_LINES:
        _, sz = fit_font(d, line, W - 48, start=72)
        top_sizes.append(sz)
    tsize = min(top_sizes)
    ft = ImageFont.truetype(FONT_PATH, tsize)
    tline_h = int(tsize * 1.15)
    ty = (TOP_BAND - tline_h * len(TOP_LINES)) / 2
    for i, line in enumerate(TOP_LINES):
        tw = d.textlength(line, font=ft)
        d.text(((W - tw) / 2, ty + i * tline_h), line, font=ft, fill=(255, 255, 255))
    s = tsize

    # Bottom: two lines, same size, second line accent yellow.
    sizes = []
    for line in BOT_LINES:
        _, sz = fit_font(d, line, W - 48)
        sizes.append(sz)
    size = min(sizes)
    f2 = ImageFont.truetype(FONT_PATH, size)
    line_h = int(size * 1.18)
    total = line_h * len(BOT_LINES)
    y = TOP_BAND + ART_H + (BOT_BAND - total) / 2
    colors = [(255, 255, 255), (255, 213, 0)]
    for i, line in enumerate(BOT_LINES):
        tw = d.textlength(line, font=f2)
        d.text(((W - tw) / 2, y + i * line_h), line, font=f2, fill=colors[i])

    # Quantize to palette: cartoon art stays clean, file shrinks under gate.
    q = img.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
    q.save(OUT, "PNG", optimize=True)
    q.convert("RGB").resize((300, 300), Image.LANCZOS).save(PREVIEW, "PNG")
    print("wrote", OUT, os.path.getsize(OUT), "bytes; top font", s, "bot font", size)


if __name__ == "__main__":
    main()
