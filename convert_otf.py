"""Convert CFF OTF to TrueType TTF using fontTools.
Handles Goudy Heavyface and Brandon Grotesque OTFs.
"""
import sys
from fontTools.ttLib import TTFont, newTable
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

MAX_ERR = 1.0

def convert(otf_path, ttf_path):
    font = TTFont(otf_path)
    if "glyf" in font:
        print(f"  {otf_path}: already TT outlines, copying as-is")
        font.save(ttf_path)
        return

    glyph_order = font.getGlyphOrder()
    glyph_set = font.getGlyphSet()

    # Build new glyf table from CFF outlines
    glyf = newTable("glyf")
    glyf.glyphs = {}
    for name in glyph_order:
        ttPen = TTGlyphPen(glyph_set)
        cu2quPen = Cu2QuPen(ttPen, MAX_ERR, reverse_direction=True)
        glyph_set[name].draw(cu2quPen)
        glyf.glyphs[name] = ttPen.glyph()
    font["glyf"] = glyf

    # Add a loca table (will be auto-computed on save)
    loca = newTable("loca")
    font["loca"] = loca

    # Switch sfnt to TrueType
    font.sfntVersion = "\x00\x01\x00\x00"

    # Drop CFF/CFF2/VORG
    for tag in ("CFF ", "CFF2", "VORG"):
        if tag in font:
            del font[tag]

    # Maxp v1 with required TT fields (zeros are fine; reportlab is lenient)
    maxp = font["maxp"]
    maxp.tableVersion = 0x00010000
    for attr, val in [
        ("maxPoints", 0), ("maxContours", 0),
        ("maxCompositePoints", 0), ("maxCompositeContours", 0),
        ("maxZones", 2), ("maxTwilightPoints", 0),
        ("maxStorage", 0), ("maxFunctionDefs", 0),
        ("maxInstructionDefs", 0), ("maxStackElements", 0),
        ("maxSizeOfInstructions", 0), ("maxComponentElements", 0),
        ("maxComponentDepth", 0),
    ]:
        if not hasattr(maxp, attr):
            setattr(maxp, attr, val)

    font.save(ttf_path)
    print(f"  {otf_path} -> {ttf_path}")

if __name__ == "__main__":
    for src in sys.argv[1:]:
        dst = src.rsplit(".", 1)[0] + ".ttf"
        convert(src, dst)
