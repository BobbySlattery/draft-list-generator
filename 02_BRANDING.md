# Brand Customization

The generator's look is driven by `brand.json` and a few asset files in the `brand/` folder. Defaults are eyeballed from your sample tap list (`Deerfield Tap List.pdf`). When your designer hands over the real assets, swap them in with no code changes.

## What you can swap

### 1. Exact brand colors

Open `brand.json` and replace the hex codes:

```json
"colors": {
  "header_bar":    "#C66331",   // orange header bar (currently eyeballed)
  "accent_orange": "#C66331",   // beer name color + alternate tap number
  "accent_sage":   "#93B0A0",   // badge fill + alternate tap number
  "background":    "#F2EAD5",   // page cream
  "text_dark":     "#1B3D38",   // body text + ABV
  "text_light":    "#F5EDDD"    // text on the orange bar
}
```

Get the exact values from your designer or sample any pixel from your real PDF in Photoshop / a color-picker browser extension.

### 2. Logo (replaces the "$7 Pints" badge)

Drop a PNG or JPG (transparent PNG preferred) into the `brand/` folder, then point at it in `brand.json`:

```json
"logo": { "path": "brand/logo.png" }
```

The image is centered in the badge area and scaled to ~75% of the orange bar height. Anything roughly square (1:1) or slightly wider works best.

If `logo.path` is `null`, the generator draws the sage circle with the configured `left_badge` text instead.

### 3. Custom fonts (e.g. the chunky slab serif used on "Draft Beer")

Drop the TTF or OTF files into `brand/fonts/`, then point at them in `brand.json`:

```json
"fonts": {
  "title_font_file":  "Cooper-Black.ttf",      // headline + tap numbers
  "title_font_name":  "Cooper Black",          // CSS family name (used in HTML)
  "body_font_file":   "Helvetica-Now.ttf",     // body text
  "body_font_name":   "Helvetica Now",
  "body_bold_file":   "Helvetica-Now-Bold.ttf",
  "body_bold_name":   "Helvetica Now Bold"
}
```

If a font file is missing, the generator falls back to the named font (so leave a sensible name like "Helvetica" or "Times-Bold" in the `_name` field). For the HTML, the `_name` is used as the CSS `font-family`, so the TV display picks up whatever font is installed locally if it matches.

> **Font licensing:** make sure you have the right to embed the font you use. Most foundry licenses cover desktop use (PDF generation) but check the EULA. Free OFL fonts from Google Fonts are always safe.

### 4. Header text (badge + right callout)

```json
"header": {
  "title":      "Draft Beer",
  "left_badge": "$7\nPints",
  "right_text": "$10 32OZ\nCROWLERS TO-GO"
}
```

Use `\n` for line breaks. If you upload a logo this overrides the badge text.

## How to preview your changes

```bash
python generate_draft_list.py --sample
open draft_list.pdf draft_list.html
```

Tweak `brand.json` and rerun. No restart of anything needed.

## Sending us your real assets

When you have them, drop these files into the folder:

- `brand/logo.png` — your logo (transparent PNG)
- `brand/fonts/<your-headline-font>.ttf` — the chunky serif from "Draft Beer"
- `brand/fonts/<your-body-font>.ttf` (and bold variant) — for everything else
- A note with the exact hex codes for orange / sage / cream / dark text

Then update `brand.json` to reference the filenames and you're done.
