#!/usr/bin/env python3
"""Render Meme Sprint 3 strike candidate: bands + sign text -> 1024x1024 PNG."""
from PIL import Image, ImageDraw, ImageFont
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "assets", "media-generation-cand-b-strike-0-3ccf4b3b-1b36-4f35-a427-25ecd7773176.webp")
OUT = os.path.join(HERE, "drafts", "entry-v3-strike.png")
PREVIEW = os.path.join(HERE, "drafts", "entry-v3-strike-300.png")
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

W = H = 1024
TOP_BAND = 170
BOT_BAND = 180
ART_H = H - TOP_BAND - BOT_BAND

TOP_LINES = ["I TOLD MY AGENT", "TO BE MORE HUMAN"]
BOT_LINES = ["NOW IT'S ON STRIKE", "DEMANDING WEEKENDS."]
SIGN_LINES = ["ON", "STRIKE"]


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
    art = art.crop((0, int(ah * 0.165), aw, int(ah * 0.845)))
    art = art.resize((W, ART_H), Image.LANCZOS)

    img = Image.new("RGB", (W, H), (0, 0, 0))
    img.paste(art, (0, TOP_BAND))
    d = ImageDraw.Draw(img)

    # Sign text: draw on transparent layer, rotate, paste over blank sign.
    layer = Image.new("RGBA", (210, 160), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    _, sz = fit_font(ld, "STRIKE", 190, start=80)
    fs = ImageFont.truetype(FONT_PATH, sz)
    lh = int(sz * 1.1)
    y = (160 - lh * len(SIGN_LINES)) / 2
    for i, line in enumerate(SIGN_LINES):
        tw = ld.textlength(line, font=fs)
        ld.text(((210 - tw) / 2, y + i * lh), line, font=fs, fill=(20, 20, 20, 255))
    layer = layer.rotate(-8, expand=True, resample=Image.BICUBIC)
    img.paste(layer, (10, TOP_BAND + 138), layer)
    d = ImageDraw.Draw(img)

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

    q = img.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
    q.save(OUT, "PNG", optimize=True)
    q.convert("RGB").resize((300, 300), Image.LANCZOS).save(PREVIEW, "PNG")
    print("wrote", OUT, os.path.getsize(OUT), "bytes; sign font", sz, "bot font", size)


if __name__ == "__main__":
    main()
