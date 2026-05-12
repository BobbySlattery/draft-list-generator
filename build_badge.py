#!/usr/bin/env python3
"""Generate brand/badge.png — the scalloped sage starburst with sparkle decorations.

Run: python build_badge.py
Outputs: brand/badge.png  (800x800 RGBA, transparent background)
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

OUT_PATH = Path(__file__).resolve().parent / "brand" / "badge.png"

# Canvas
SIZE = 800
PAD  = 60                 # margin inside canvas (room for sparkles + shadow)
CX = CY = SIZE / 2

# Scalloped shape geometry (radii in px)
N_SCALLOPS = 16
R_AVG = (SIZE / 2) - PAD - 30
AMP   = 18
SAMPLES = 1440             # very high resolution for smooth edges

SAGE   = (145, 195, 169, 255)   # #91C3A9
FOREST = (31, 61, 52, 255)       # #1F3D34
OUTLINE_W = 8


def scallop_points(cx, cy, r_avg, amp, n, samples):
    pts = []
    for i in range(samples):
        theta = 2 * math.pi * i / samples
        r = r_avg + amp * math.cos(n * theta)
        pts.append((cx + r * math.cos(theta), cy + r * math.sin(theta)))
    return pts


def diamond(cx, cy, half_w, half_h):
    """Four-pointed star/diamond (rhombus) shape centered at cx, cy."""
    return [(cx, cy - half_h), (cx + half_w, cy), (cx, cy + half_h), (cx - half_w, cy)]


def main():
    # Working canvas, larger so we can draw shadow then crop
    canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))

    # Drop shadow: draw badge in dark, blur, offset, paste
    shadow_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow_layer)
    pts = scallop_points(CX, CY, R_AVG, AMP, N_SCALLOPS, SAMPLES)
    sd.polygon(pts, fill=(0, 0, 0, 110))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=8))
    # Offset shadow down-right
    canvas.alpha_composite(shadow_layer, dest=(8, 10))

    # Badge fill
    badge = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)
    bd.polygon(pts, fill=SAGE, outline=FOREST)
    canvas.alpha_composite(badge)

    # Outline the scallop with thicker stroke (PIL polygon outline is hairline,
    # so we draw the outline ourselves as a thicker line connecting consecutive points).
    outline_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    od = ImageDraw.Draw(outline_layer)
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        od.line([(x1, y1), (x2, y2)], fill=FOREST, width=OUTLINE_W)
    canvas.alpha_composite(outline_layer)

    # Sparkles — three 4-point diamonds in dark forest
    sd2 = ImageDraw.Draw(canvas)
    # upper-right large
    sd2.polygon(diamond(SIZE - 70, 110, 38, 60), fill=FOREST)
    # lower-left large
    sd2.polygon(diamond(70, SIZE - 100, 38, 60), fill=FOREST)
    # lower-left small (between large sparkle and badge)
    sd2.polygon(diamond(170, SIZE - 175, 18, 28), fill=FOREST)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUT_PATH, "PNG")
    print(f"Wrote {OUT_PATH}  ({SIZE}x{SIZE} RGBA)")


if __name__ == "__main__":
    main()
