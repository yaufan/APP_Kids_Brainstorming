"""Drawing kit for 積木王國 (style C 幾何積木風): flat shapes, no outlines, no shading.

Everything is built from circles, squares, triangles, rounded rectangles, capsules and arcs in flat
bold colours, as in docs/mockups (0_畫風選擇 band C, 13 and 14). At most one flat darker shape gives
a thing its side; a white dot or bar at half opacity is its shine.

The app draws the pictures with flutter_svg, so the kit writes only what flutter_svg draws: plain
shapes and paths with their paint attributes on the element itself, clip paths, <use>, and group
transforms and opacity. No <filter>, <mask>, <pattern>, <style>, CSS, <text> or <image>.

    from blocks_kit import *          # used by blocks_art.py
"""
import hashlib
import math
import pathlib
import re
import subprocess
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "app" / "assets" / "art" / "blocks"

# ---------------------------------------------------------------- colours (from make_mockups.py, style C)
CR, CB, CY, CG, CP, CT = "#EF233C", "#3A86FF", "#FFBF1F", "#2EC46A", "#8338EC", "#2EC4B6"
OR, DK, CREAM, BR = "#FF7A2F", "#2B2D42", "#FFF4E2", "#8C5A3C"
PINK, ROSE, ORANGE = "#FF8FAB", "#FF4D6D", "#FF9F43"
BG, DOT, SH = "#EEF0FF", "#C9CCF2", "#D5D8F5"
WHITE = "#FFFFFF"
SKIN = "#EDB48A"
HAIR = "#3B2A24"
BLUSH = "#FF9E9E"


def _rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def mix(a, b, t):
    """Colour a moved towards b by t (0..1)."""
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(x + (y - x) * t))) for x, y in zip(_rgb(a), _rgb(b)))


def dk(c, t=.18):
    """A darker shade of c (the flat side of a thing)."""
    return mix(c, "#1B1530", t)


def lt(c, t=.35):
    return mix(c, "#FFFFFF", t)


def n(v):
    """A number, short (deterministic text)."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def pts_(pts):
    return " ".join(f"{n(x)},{n(y)}" for x, y in pts)


# ---------------------------------------------------------------- defs of the picture being drawn
_DEFS = {}


def begin():
    _DEFS.clear()


def _h(*parts):
    return hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:7]


def clip(inner):
    """A clip path made of the given shapes (in the user space of the element it clips)."""
    k = "c" + _h(inner)
    _DEFS.setdefault(k, f'<clipPath id="{k}">{inner}</clipPath>')
    return f"url(#{k})"


def lg(stops, x1=0, y1=0, x2=0, y2=1):
    k = "l" + _h(stops, x1, y1, x2, y2)
    st = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    _DEFS.setdefault(k, f'<linearGradient id="{k}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{st}</linearGradient>')
    return f"url(#{k})"


# ---------------------------------------------------------------- shapes (every one carries its own paint)
def _op(op):
    return f' opacity="{n(op)}"' if op is not None and op != 1 else ""


def _rot(rot):
    if rot is None:
        return ""
    a, cx, cy = rot
    return f' transform="rotate({n(a)} {n(cx)} {n(cy)})"'


def circle(cx, cy, r, fill, op=None):
    return f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{fill}"{_op(op)}/>'


def ell(cx, cy, rx, ry, fill, op=None, rot=None):
    if rot is not None and not isinstance(rot, tuple):
        rot = (rot, cx, cy)
    return f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}" fill="{fill}"{_op(op)}{_rot(rot)}/>'


def rect(x, y, w, h, fill, rx=0, op=None, rot=None):
    r = f' rx="{n(rx)}"' if rx else ""
    if rot is not None and not isinstance(rot, tuple):
        rot = (rot, x + w / 2, y + h / 2)
    return f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}"{r} fill="{fill}"{_op(op)}{_rot(rot)}/>'


def path(d, fill, op=None, rot=None, extra=""):
    return f'<path d="{d}" fill="{fill}"{_op(op)}{_rot(rot)}{extra}/>'


def poly(pts, fill, round_=0, op=None, rot=None):
    """A polygon; round_ > 0 rounds its corners (a stroke of the same colour with round joins)."""
    d = "M" + " L".join(f"{n(x)},{n(y)}" for x, y in pts) + "Z"
    if round_:
        return (f'<path d="{d}" fill="{fill}" stroke="{fill}" stroke-width="{n(round_)}" stroke-linejoin="round"'
                f'{_op(op)}{_rot(rot)}/>')
    return path(d, fill, op, rot)


def cap(x0, y0, x1, y1, r, col, op=None):
    """A capsule (rounded bar) from (x0, y0) to (x1, y1), r its half width."""
    return (f'<path d="M{n(x0)},{n(y0)} L{n(x1)},{n(y1)}" fill="none" stroke="{col}" stroke-width="{n(2 * r)}" '
            f'stroke-linecap="round"{_op(op)}/>')


def line(pts, w, col, op=None, linecap="round", closed=False):
    d = "M" + " L".join(f"{n(x)},{n(y)}" for x, y in pts) + ("Z" if closed else "")
    return (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{n(w)}" stroke-linecap="{linecap}" '
            f'stroke-linejoin="round"{_op(op)}/>')


def stroke(d, w, col, op=None, linecap="round"):
    return (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{n(w)}" stroke-linecap="{linecap}" '
            f'stroke-linejoin="round"{_op(op)}/>')


def ring(cx, cy, r, w, col, op=None):
    return f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="none" stroke="{col}" stroke-width="{n(w)}"{_op(op)}/>'


def pt(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def arc_d(cx, cy, r, a0, a1):
    """An arc path from angle a0 to a1 (degrees, clockwise on screen when a1 > a0)."""
    x0, y0 = pt(cx, cy, r, a0)
    x1, y1 = pt(cx, cy, r, a1)
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1 if a1 > a0 else 0
    return f"M{n(x0)},{n(y0)} A{n(r)},{n(r)} 0 {large} {sweep} {n(x1)},{n(y1)}"


def arc(cx, cy, r, a0, a1, w, col, op=None, linecap="round"):
    return stroke(arc_d(cx, cy, r, a0, a1), w, col, op, linecap)


def half(cx, cy, r, fill, up=True, ry=None, op=None):
    """Half a disc (or ellipse) standing on the line y = cy (up) or hanging from it."""
    ry = r if ry is None else ry
    s = 1 if up else 0
    return path(f"M{n(cx - r)},{n(cy)} A{n(r)},{n(ry)} 0 0 {s} {n(cx + r)},{n(cy)}Z", fill, op)


def lens_d(x0, y0, x1, y1, bulge, bulge2=None):
    """A leaf / lens between two points; bulge is how far each side swells out (in units)."""
    bulge2 = bulge if bulge2 is None else bulge2
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    c1 = (mx + nx * bulge * 1.33, my + ny * bulge * 1.33)
    c2 = (mx - nx * bulge2 * 1.33, my - ny * bulge2 * 1.33)
    return (f"M{n(x0)},{n(y0)} Q{n(c1[0])},{n(c1[1])} {n(x1)},{n(y1)} "
            f"Q{n(c2[0])},{n(c2[1])} {n(x0)},{n(y0)}Z")


def lens(x0, y0, x1, y1, bulge, fill, bulge2=None, op=None):
    return path(lens_d(x0, y0, x1, y1, bulge, bulge2), fill, op)


def star_d(R, r, k=5, cx=0, cy=0, rot=-90):
    p = []
    for i in range(2 * k):
        rad = R if i % 2 == 0 else r
        p.append(pt(cx, cy, rad, rot + i * 180 / k))
    return "M" + " L".join(f"{n(x)},{n(y)}" for x, y in p) + "Z"


def star(cx, cy, R, fill, r=None, k=5, rot=-90, round_=0, op=None):
    r = R * .48 if r is None else r
    d = star_d(R, r, k, cx, cy, rot)
    if round_:
        return f'<path d="{d}" fill="{fill}" stroke="{fill}" stroke-width="{n(round_)}" stroke-linejoin="round"{_op(op)}/>'
    return path(d, fill, op)


def g(inner, tr="", op=None, clip_=None):
    t = f' transform="{tr}"' if tr else ""
    c = f' clip-path="{clip_}"' if clip_ else ""
    return f"<g{t}{c}{_op(op)}>{inner}</g>"


def shine(cx, cy, r, op=.55):
    """The white shine dot of a round thing."""
    return circle(cx, cy, r, WHITE, op)


def shine_bar(x, y, w, h, op=.5, rot=None):
    return rect(x, y, w, h, WHITE, rx=min(w, h) / 2, op=op, rot=rot)


def eye(cx, cy, r=5, hl=True):
    o = circle(cx, cy, r, DK)
    if hl:
        o += circle(cx - r * .35, cy - r * .38, r * .38, WHITE)
    return o


def smile(cx, cy, w, col=DK, sw=3.2):
    return stroke(f"M{n(cx - w / 2)},{n(cy)} Q{n(cx)},{n(cy + w * .55)} {n(cx + w / 2)},{n(cy)}", sw, col)


# ---------------------------------------------------------------- documents
def doc(body, w=200, h=200):
    defs = "".join(_DEFS[k] for k in sorted(_DEFS))
    d = f"<defs>{defs}</defs>" if defs else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f"{d}{body}</svg>\n")


def fit(body, box, size=200, fill=.85, dy=0.0):
    """Place a drawing whose extent is box=(x0, y0, x1, y1) in the middle of a size x size picture,
    its longer side filling `fill` of it."""
    x0, y0, x1, y1 = box
    s = size * fill / max(x1 - x0, y1 - y0)
    tx, ty = size / 2 - s * (x0 + x1) / 2, size / 2 - s * (y0 + y1) / 2 + dy
    return g(body, f"translate({n(tx)} {n(ty)}) scale({n(s)})")


BAD = re.compile(r"<(filter|mask|pattern|style|text|image|foreignObject)\b|style=|class=")


def check(name, svg):
    m = BAD.search(svg)
    if m:
        raise SystemExit(f"{name}: uses {m.group(0)} (flutter_svg cannot draw it)")
    if not svg.rstrip().endswith("</svg>"):
        raise SystemExit(f"{name}: not closed")
    if svg.count("<use") > 800:
        raise SystemExit(f"{name}: {svg.count('<use')} <use>")
    if len(svg.encode()) > 60_000:
        raise SystemExit(f"{name}: {len(svg.encode())} bytes")
    for el in re.finditer(r"<(path|circle|ellipse|rect|use|polygon)\b[^>]*>", svg):
        t = el.group(0)
        if "fill=" not in t and "stroke=" not in t and "id=" not in t:
            raise SystemExit(f"{name}: element without paint: {t[:80]}")


def write(name, svg, out=OUT):
    check(name, svg)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{name}.svg").write_text(svg)


# ---------------------------------------------------------------- rendering (Node.js + Playwright's Chromium)
RENDER_JS = """const { chromium } = require('playwright');
(async () => {
  const [inp, out, w, h] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 1 });
  await page.goto('file://' + inp);
  await page.waitForTimeout(200);
  await page.screenshot({ path: out, fullPage: true });
  await browser.close();
})();
"""


def render_html(html, out, w, h):
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        (td / "page.html").write_text(html)
        (td / "render.js").write_text(RENDER_JS)
        subprocess.run(["node", str(td / "render.js"), str(td / "page.html"), str(out), str(w), str(h)], check=True)
