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
BOT_LINES = ["IT SOLD MY CAR.", "BOUGHT 4,000 RUBBER DUCKS."]


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
    top_crop = int(ah * 0.17)
    bot_crop = int(ah * 0.86)
    art = art.crop((0, top_crop, aw, bot_crop))
    # Resize to fill art area width, center-crop height.
    scale = W / art.width
    art = art.resize((W, int(art.height * scale)), Image.LANCZOS)
    if art.height > ART_H:
        # Bias crop upward so feet at the bottom survive.
        y = 0
        art = art.crop((0, y, W, y + ART_H))
    else:
        canvas_art = Image.new("RGB", (W, ART_H), (0, 0, 0))
        canvas_art.paste(art, (0, (ART_H - art.height) // 2))
        art = canvas_art

    img = Image.new("RGB", (W, H), (0, 0, 0))
    img.paste(art, (0, TOP_BAND))
    d = ImageDraw.Draw(img)

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
