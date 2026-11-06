"""想一想樂園's app icon: 阿布's face (style A, 動畫片風) with his magnifying glass, in front of a soft
rainbow arch in the three lands' colours (卡通城 yellow, 紙片森林 green, 積木王國 purple) on a sky.

    python3 icon.py preview out.png   # a sheet: round / squircle / square masks at 48, 96 and 192 px, and a big one
    python3 icon.py export            # writes the Android and iOS icons into app/

export writes
- Android, full square art: app/android/app/src/main/res/mipmap-{mdpi..xxxhdpi}/ic_launcher.png (48..192 px, opaque).
- Android adaptive icon (API 26+): mipmap-anydpi-v26/ic_launcher.xml, with
  drawable-{mdpi..xxxhdpi}/ic_launcher_foreground.png and ic_launcher_background.png
  (108 dp canvas; the face and the glass stay inside the central 66 dp circle).
- iOS: every PNG listed in app/ios/Runner/Assets.xcassets/AppIcon.appiconset/Contents.json,
  at its size, opaque (no alpha).
The fox is drawn by park_art.py (the same shapes as abu_city_*.svg). Needs Node.js with Playwright
(Chromium draws the SVGs) and Pillow.
"""
import json
import math
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw

import park_art as P

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
APP = ROOT / "app"
RES = APP / "android" / "app" / "src" / "main" / "res"
IOS = APP / "ios" / "Runner" / "Assets.xcassets" / "AppIcon.appiconset"

C = 1024
DENSITIES = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
BANDS = ("#B48BFF", "#8FD67A", "#FFD84D")      # outside in: 積木王國, 紙片森林, 卡通城
SKY = ("#BDE6FF", "#E9F7FF")

FULL_R = 0.44 * C                 # full square art (legacy Android, iOS)
SAFE_R = 33 / 108 * C * 0.97      # adaptive foreground: the central 66 dp circle of 108 dp
FIT = {}


def face():
    """阿布's head and his magnifying glass in fox units, and the defs they need."""
    P.D = P.Defs()
    P.STYLE, P.SC, P.SW = "A", 3.0, 5.2
    head = P.fox_head("wave", (1.5, 2.5))
    glass = P.magnifier(58, 10, 34, 116, .8)
    defs = P.D.svg()
    P.STYLE, P.SC, P.SW = "A", 1.0, 2.2
    return defs, head + glass


# a box in fox units centred on the middle of the head (ears, cap, cheeks, chin and glass around it)
BOX = (-130, -190, 130, 70)


def subject_svg(px, radius):
    """The face and glass, see-through around them, centred so they reach `radius` (in 1024ths) from the middle."""
    defs, body = face()
    x0, y0, x1, y1 = BOX
    s = radius / (max(x1 - x0, y1 - y0) / 2) * FIT.get(radius, 1.0)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {C} {C}" width="{px}" height="{px}">'
            f'{defs}'
            f'<g transform="translate({C / 2} {C / 2}) scale({s:.4f}) translate({-(x0 + x1) / 2:.1f} {-(y0 + y1) / 2:.1f})">'
            f'{body}</g></svg>')


def background_svg(px):
    """Sky, a soft three-band arch (the three lands) and two little clouds at its feet."""
    a, b = SKY
    o = [f'<rect width="{C}" height="{C}" fill="url(#sky)"/>']
    cx, cy = C / 2, C * .66
    for i, col in enumerate(BANDS):
        r = C * (.47 - i * .085)
        o.append(f'<path d="M{cx - r:.1f},{cy:.1f} A{r:.1f},{r:.1f} 0 0 1 {cx + r:.1f},{cy:.1f}" fill="none" '
                 f'stroke="{col}" stroke-width="{C * .085 + 1:.1f}"/>')
    o.append(f'<rect x="0" y="{cy:.1f}" width="{C}" height="{C - cy:.1f}" fill="url(#ground)"/>')
    for x in (C * .14, C * .86):
        o.append(f'<path d="{P.cloud_d(x, cy - C * .01, C / 300)}" fill="#FFFFFF"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {C} {C}" width="{px}" height="{px}">'
            f'<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{a}"/>'
            f'<stop offset="1" stop-color="{b}"/></linearGradient>'
            f'<linearGradient id="ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A8E08C"/>'
            f'<stop offset="1" stop-color="#8FD474"/></linearGradient></defs>'
            f'{"".join(o)}</svg>')


# ---------------------------------------------------------------- rendering
RENDER_JS = """
const { chromium } = require('playwright');
(async () => {
  const [inp, out, w, h] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 1 });
  await page.goto('file://' + inp);
  await page.screenshot({ path: out, omitBackground: true });
  await browser.close();
})();
"""


def render(svg_text, px):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        src, out, js = tmp / "in.svg", tmp / "out.png", tmp / "r.js"
        src.write_text(svg_text)
        js.write_text(RENDER_JS)
        subprocess.run(["node", str(js), str(src), str(out), str(px), str(px)], check=True)
        return Image.open(out).convert("RGBA").copy()


def reach(img):
    """How far from the middle the opaque part of the image reaches (ignoring the faint shadow)."""
    a = img.getchannel("A")
    w, h = img.size
    px = a.load()
    best = 0.0
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            if px[x, y] > 200:
                best = max(best, math.hypot(x + 0.5 - w / 2, y + 0.5 - h / 2))
    return best


def fit():
    for radius in (FULL_R, SAFE_R):
        FIT[radius] = 1.0
        got = reach(render(subject_svg(512, radius), 512)) * C / 512
        FIT[radius] = radius / got


def full_art():
    bg = render(background_svg(C), C)
    fg = render(subject_svg(C, FULL_R), C)
    return Image.alpha_composite(bg, fg).convert("RGB")


def adaptive_layers():
    return render(background_svg(C), C).convert("RGB"), render(subject_svg(C, SAFE_R), C)


def resized(img, px):
    return img.resize((px, px), Image.LANCZOS)


def mask(kind, px):
    m = Image.new("L", (px * 4, px * 4), 0)
    dr = ImageDraw.Draw(m)
    s = px * 4
    if kind == "round":
        dr.ellipse((0, 0, s - 1, s - 1), fill=255)
    elif kind == "squircle":
        pts = []
        for i in range(720):
            t = 2 * math.pi * i / 720
            c, si = math.cos(t), math.sin(t)
            pts.append((s / 2 + s / 2 * math.copysign(abs(c) ** (2 / 5), c), s / 2 + s / 2 * math.copysign(abs(si) ** (2 / 5), si)))
        dr.polygon(pts, fill=255)
    else:
        dr.rounded_rectangle((0, 0, s - 1, s - 1), radius=s * 0.08, fill=255)
    return m.resize((px, px), Image.LANCZOS)


def views():
    """(adaptive icon as a launcher shows it, full square art)."""
    fit()
    full = full_art()
    bg, fg = adaptive_layers()
    adaptive = Image.alpha_composite(bg.convert("RGBA"), fg).convert("RGB")
    k = C * 18 / 108          # a launcher shows the middle 72 dp of the 108 dp canvas
    return adaptive.crop((round(k), round(k), round(C - k), round(C - k))), full


def sheet_pieces():
    """For park_art.py's preview: rows (mask kind, [(image, mask)]) at 48, 96 and 192 px."""
    adaptive_view, full = views()
    rows = []
    for kind, art_ in (("round", adaptive_view), ("square", full)):
        rows.append((kind, [(resized(art_, s), mask(kind, s)) for s in (48, 96, 192)]))
    return rows


def preview(out):
    adaptive_view, full = views()
    sizes = (48, 96, 192)
    rows = [("round", adaptive_view), ("squircle", adaptive_view), ("square", full)]
    pad = 24
    W = pad + sum(s + pad for s in sizes) + 420 + pad
    H = pad + len(rows) * (192 + pad) + 120
    sheet = Image.new("RGB", (W, H), "#E9E4DE")
    sheet.paste(Image.new("RGB", (W, 120), "#2F2B33"), (0, H - 120))
    for r, (kind, art_) in enumerate(rows):
        x = pad
        y = pad + r * (192 + pad)
        for s in sizes:
            sheet.paste(resized(art_, s), (x, y + 192 - s), mask(kind, s))
            x += s + pad
    sheet.paste(resized(full, 420), (W - pad - 420, pad), mask("squircle", 420))
    x = pad
    for kind, art_ in rows:
        sheet.paste(resized(art_, 72), (x, H - 96), mask(kind, 72))
        x += 72 + pad
    sheet.save(out)
    print(out)


ADAPTIVE_XML = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_launcher_background"/>
    <foreground android:drawable="@drawable/ic_launcher_foreground"/>
</adaptive-icon>
"""


def export():
    fit()
    full = full_art()
    bg, fg = adaptive_layers()
    written = []
    for name, k in DENSITIES.items():
        mip = RES / f"mipmap-{name}"
        mip.mkdir(parents=True, exist_ok=True)
        resized(full, round(48 * k)).save(mip / "ic_launcher.png")
        draw = RES / f"drawable-{name}"
        draw.mkdir(parents=True, exist_ok=True)
        resized(fg, round(108 * k)).save(draw / "ic_launcher_foreground.png")
        resized(bg, round(108 * k)).save(draw / "ic_launcher_background.png")
        written += [mip / "ic_launcher.png", draw / "ic_launcher_foreground.png", draw / "ic_launcher_background.png"]
    anydpi = RES / "mipmap-anydpi-v26"
    anydpi.mkdir(parents=True, exist_ok=True)
    (anydpi / "ic_launcher.xml").write_text(ADAPTIVE_XML)
    written.append(anydpi / "ic_launcher.xml")
    contents = json.loads((IOS / "Contents.json").read_text())
    for image in contents["images"]:
        if not image.get("filename"):
            continue
        size = float(image["size"].split("x")[0]) * float(image["scale"].rstrip("x"))
        resized(full, round(size)).convert("RGB").save(IOS / image["filename"])
        written.append(IOS / image["filename"])
    manifest = (APP / "android" / "app" / "src" / "main" / "AndroidManifest.xml").read_text()
    if 'android:icon="@mipmap/ic_launcher"' not in manifest:
        print("note: AndroidManifest.xml's android:icon is not @mipmap/ic_launcher")
    for p in written:
        print(p.relative_to(ROOT))


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "export":
        export()
    elif len(sys.argv) >= 3 and sys.argv[1] == "preview":
        preview(sys.argv[2])
    else:
        print(__doc__)
