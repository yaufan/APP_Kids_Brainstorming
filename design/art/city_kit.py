"""卡通城 drawing kit: style A 「動畫片風」 for 想一想樂園 (shared by every 卡通城 picture).

The look (the approved mockups: docs/mockups/make_mockups.py, 0_畫風選擇.png, 2_放哪裡.png):
  * every shape is a bright flat fill with ONE hard-edged cel shadow (a crescent along its
    bottom-right edge: the shape minus a copy of itself moved up-left), an optional small white
    highlight, and a thin outline in a darker shade of its own fill (never black);
  * big friendly eyes (white, a large dark pupil, two shines) and soft pink cheeks;
  * big, round, simple shapes.

The mockups were drawn for Chromium with <mask>, filters and CSS (`vector-effect:
non-scaling-stroke`). The app draws its pictures with flutter_svg, which has no <mask>, <filter>,
<style>/style=, CSS, <text>, <image>, <foreignObject> or <pattern>, so this kit builds the same
look only from paths, linear and radial gradients, clipPath, transforms and opacity:
  cel shadow   the shape in the shadow colour, then the shape in its own colour moved up-left and
               clipped to the shape; what stays uncovered is the crescent (`part`)
  celov()      a see-through crescent over a many-coloured shape: inside a clip of the shape, a huge
               rectangle with the moved shape cut out of it (even-odd)
  outlines     explicit stroke widths. A picture says how thick its outline is in ITS OWN units
               (`begin(ol=...)`); a drawing made in its own units and fitted into the picture with
               `fit()` divides that by its scale, so every line comes out the same weight
  soft shadow  an ellipse filled with a radial gradient that fades out (`ground`), not a blur

One picture:
    begin(ol=OL_THING)              # fresh <defs>; outline 4.4 units of the 200 x 200 picture
    body = fit(apple, APPLE_BOX)    # apple() draws in its own units; the box is (x0, y0, x1, y1)
    save("apple", body)             # -> app/assets/art/city/apple.svg (checks the flutter_svg rules)

Drawing functions return SVG strings. Every element carries its own fill/stroke attributes. All
numbers are rounded and every id is a hash of what it holds, so the output is the same bytes on
every run. Random numbers, where wanted, must come from random.Random(<fixed seed>).
"""
import colorsys
import hashlib
import math
import pathlib
import re
import xml.etree.ElementTree as ET

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "app" / "assets" / "art" / "city"

# ---------------------------------------------------------------- sizes
THING = 200          # things, people and places are 200 x 200 pictures
FILL = 170           # a thing's longer side, in units of the 200 picture (85 %)
OL_THING = 4.4       # outline of a thing, in units of the 200 picture (about 2 px when shown 90 px wide)
SCENE_W, SCENE_H = 390, 600
OL_SCENE = 1.6       # outlines in a scene background (390 x 600, shown about 1:1 on a phone)
SCREEN_PX = 2.3      # wanted outline on screen, px, for pictures whose shown size is known (places)


def ol_for(shown_px, size=THING):
    """Outline width (units of a `size` picture) that is SCREEN_PX on screen when the picture is
    shown `shown_px` wide. Kept between 1.2 and 4.6 units so tiny or huge places still look right."""
    return max(1.2, min(4.6, SCREEN_PX * size / shown_px))


# ---------------------------------------------------------------- colours (the mockups' palette)
INK = "#4B3A5E"        # deep plum (words, dark lines in the UI)
FOX = "#FF8A3D"
FOXD = "#6E3B22"
CREAM = "#FFF6EA"
GOLD = "#FFC233"
RED = "#F2463F"
BLUE = "#3D8BF2"
SKY = "#5BC0F8"
GREEN = "#4FC461"
PINK = "#FF7FA3"
PURPLE = "#9B5DE5"
TEAL = "#2EC4B6"
YELLOW = "#FFD43B"
ORANGE = "#FF8C2B"
BROWN = "#A8693D"
WOOD = "#D08E57"
WHITE = "#FFFFFF"
WHITE_OL = "#8E86A8"   # outline of white things (a soft lavender grey, never black)
GLASS = "#CDEEFF"      # windows, glass
SHADOW = "#4B3A5E"     # colour of soft ground shadows


def _rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def mix(a, b, t):
    """Colour a moved t of the way to b."""
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(x + (y - x) * t))) for x, y in zip(_rgb(a), _rgb(b)))


def lt(c, t):
    """Lighter: t of the way to white."""
    return mix(c, "#FFFFFF", t)


def dk(c, t):
    """Darker: t of the way to a deep plum (not black)."""
    return mix(c, "#2A1E36", t)


def _hls(c):
    return colorsys.rgb_to_hls(*[x / 255 for x in _rgb(c)])


def _hex(h, l, s):
    r, g_, b = colorsys.hls_to_rgb(h % 1, max(0, min(1, l)), max(0, min(1, s)))
    return "#%02X%02X%02X" % (round(r * 255), round(g_ * 255), round(b * 255))


def tone(c, l=1.0, s=1.0, dh=0.0):
    """The same colour with lightness and saturation scaled and the hue turned by dh (0..1)."""
    h, L, S = _hls(c)
    return _hex(h + dh, L * l, S * s)


def shd(c):
    """Cel shadow colour: the same colour, darker and a little richer."""
    h, L, S = _hls(c)
    if S < .12:
        return mix(c, "#B9B2D6", .45)
    return _hex(h - .01, L * .84, min(1, S * 1.08 + .04))


def lin(c):
    """Outline colour: a dark shade of the fill (white and grey things get WHITE_OL)."""
    h, L, S = _hls(c)
    if S < .12 or L > .93:
        return WHITE_OL
    return _hex(h - .015, L * .52, min(1, S * 1.05 + .1))


def calm(c, t=.45, bg="#FFF8EE"):
    """A background colour: the colour pulled towards a soft cream so things in front stand out."""
    h, L, S = _hls(c)
    return mix(_hex(h, L, S * .75), bg, t)


# ---------------------------------------------------------------- numbers
def n(v):
    """A number for SVG: one decimal, no trailing .0, no -0."""
    s = f"{v:.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    return "0" if s == "-0" else s


# ---------------------------------------------------------------- picture state
class Defs:
    """The <defs> of one picture: gradients and clip paths, each once, keyed by a hash of itself."""

    def __init__(self):
        self.d = {}

    def add(self, key, svg):
        self.d.setdefault(key, svg)
        return key

    def svg(self):
        return "<defs>" + "".join(self.d.values()) + "</defs>" if self.d else ""


D = Defs()
OLW = OL_THING      # outline width of the picture being made, in the picture's own units
SCALE = 1.0         # scale of the drawing being made inside the picture (set by fit())


def begin(ol=OL_THING):
    """Start a new picture: empty <defs>, outline `ol` units of the finished picture."""
    global D, OLW, SCALE
    D = Defs()
    OLW = ol
    SCALE = 1.0


def sw(k=1.0):
    """A stroke width in the current drawing's units: k times the picture's outline."""
    s = f"{OLW * k / SCALE:.2f}".rstrip("0").rstrip(".")
    return s or "0"


def _h(*parts):
    return hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:9]


def _stops(stops):
    out = []
    for s in stops:
        o = f' stop-opacity="{s[2]:.3g}"' if len(s) > 2 and s[2] != 1 else ""
        out.append(f'<stop offset="{s[0]:.3g}" stop-color="{s[1]}"{o}/>')
    return "".join(out)


def lg(stops, x1=0, y1=0, x2=0, y2=1, user=False):
    """Linear gradient; stops are (offset, colour[, opacity]). user=True: x/y in drawing units."""
    k = "l" + _h(stops, x1, y1, x2, y2, user)
    u = ' gradientUnits="userSpaceOnUse"' if user else ""
    f = n if user else (lambda v: f"{v:.3g}")
    D.add(k, f'<linearGradient id="{k}" x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}"{u}>{_stops(stops)}</linearGradient>')
    return f"url(#{k})"


def rg(stops, cx=.5, cy=.5, r=.5, user=False):
    """Radial gradient (object bounding box unless user=True)."""
    k = "r" + _h(stops, cx, cy, r, user)
    u = ' gradientUnits="userSpaceOnUse"' if user else ""
    f = n if user else (lambda v: f"{v:.3g}")
    D.add(k, f'<radialGradient id="{k}" cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}"{u}>{_stops(stops)}</radialGradient>')
    return f"url(#{k})"


def clip(d, fr=False):
    """A clip path of path data d (fr: even-odd)."""
    k = "c" + _h(d, fr)
    r = ' clip-rule="evenodd"' if fr else ""
    D.add(k, f'<clipPath id="{k}"><path d="{d}"{r}/></clipPath>')
    return f"url(#{k})"


def clipped(d, inner, fr=False):
    return f'<g clip-path="{clip(d, fr)}">{inner}</g>' if inner else ""


# ---------------------------------------------------------------- shapes (path data)
def spline(pts, n_=10, closed=False):
    """Catmull-Rom curve through pts (tuples x, y[, width])."""
    P = list(pts)
    P = [P[-1]] + P + [P[0], P[1]] if closed else [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n_):
            t = j / n_
            out.append(tuple(.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t ** 3)
                             for a, b, c, d in zip(p0, p1, p2, p3)))
    if not closed:
        out.append(tuple(P[-2]))
    return out


def poly(pts, close=True):
    return "M" + " L".join(f"{n(p[0])},{n(p[1])}" for p in pts) + ("Z" if close else "")


def blob(pts, n_=8):
    """A smooth closed shape through pts."""
    return poly(spline(pts, n_, closed=True))


def tube(pts, n_=10):
    """Outline of an arm, leg, tail...: pts are (x, y, half-width) along its middle; round ends."""
    c = spline(pts, n_)
    L, R = [], []
    for i, (x, y, w) in enumerate(c):
        a, b = c[max(0, i - 1)], c[min(len(c) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l_ = math.hypot(dx, dy) or 1
        nx, ny = -dy / l_, dx / l_
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
    w1, w0 = c[-1][2], c[0][2]
    d = "M" + " L".join(f"{n(x)},{n(y)}" for x, y in L)
    d += f" A{n(w1)},{n(w1)} 0 0 0 {n(R[-1][0])},{n(R[-1][1])}"
    d += " L" + " L".join(f"{n(x)},{n(y)}" for x, y in reversed(R))
    d += f" A{n(w0)},{n(w0)} 0 0 0 {n(L[0][0])},{n(L[0][1])}Z"
    return d


def sym(top, segs):
    """A closed path symmetric about x = 0: `segs` are cubic segments (c1, c2, p) down the right
    half from `top` to a point on the middle line."""
    f = lambda p: f"{n(p[0])},{n(p[1])}"
    m = lambda p: (-p[0], p[1])
    d = "M" + f(top)
    for c1, c2, p in segs:
        d += f" C{f(c1)} {f(c2)} {f(p)}"
    for i in reversed(range(len(segs))):
        c1, c2, _ = segs[i]
        p0 = top if i == 0 else segs[i - 1][2]
        d += f" C{f(m(c2))} {f(m(c1))} {f(m(p0))}"
    return d + "Z"


def ell(cx, cy, rx, ry=None):
    ry = rx if ry is None else ry
    return (f"M{n(cx - rx)},{n(cy)} A{n(rx)},{n(ry)} 0 1 0 {n(cx + rx)},{n(cy)} "
            f"A{n(rx)},{n(ry)} 0 1 0 {n(cx - rx)},{n(cy)}Z")


def rr(x, y, w, h, r):
    """A rounded rectangle (top-left corner x, y)."""
    r = max(0, min(r, w / 2, h / 2))
    if r == 0:
        return f"M{n(x)},{n(y)} H{n(x + w)} V{n(y + h)} H{n(x)}Z"
    return (f"M{n(x + r)},{n(y)} H{n(x + w - r)} A{n(r)},{n(r)} 0 0 1 {n(x + w)},{n(y + r)} V{n(y + h - r)} "
            f"A{n(r)},{n(r)} 0 0 1 {n(x + w - r)},{n(y + h)} H{n(x + r)} A{n(r)},{n(r)} 0 0 1 {n(x)},{n(y + h - r)} "
            f"V{n(y + r)} A{n(r)},{n(r)} 0 0 1 {n(x + r)},{n(y)}Z")


def star_d(R, r, n_=5, cx=0, cy=0, rot=-90, round_=0.0):
    """A star with n_ points (outer radius R, inner r); round_ softens the corners (0..0.5)."""
    pts = []
    for i in range(2 * n_):
        a = math.radians(rot + i * 180 / n_)
        rad = R if i % 2 == 0 else r
        pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad))
    if not round_:
        return poly(pts)
    d = ""
    for i in range(len(pts)):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
        a = (p1[0] + (p0[0] - p1[0]) * round_, p1[1] + (p0[1] - p1[1]) * round_)
        b = (p1[0] + (p2[0] - p1[0]) * round_, p1[1] + (p2[1] - p1[1]) * round_)
        d += ("M" if i == 0 else " L") + f"{n(a[0])},{n(a[1])} Q{n(p1[0])},{n(p1[1])} {n(b[0])},{n(b[1])}"
    return d + "Z"


def heart_d(s=1.0, cx=0, cy=0):
    return (f"M{n(cx)},{n(cy + 9 * s)} C{n(cx - 14 * s)},{n(cy)} {n(cx - 16 * s)},{n(cy - 9 * s)} {n(cx - 9 * s)},{n(cy - 13 * s)} "
            f"C{n(cx - 4 * s)},{n(cy - 15 * s)} {n(cx)},{n(cy - 11 * s)} {n(cx)},{n(cy - 8 * s)} "
            f"C{n(cx)},{n(cy - 11 * s)} {n(cx + 4 * s)},{n(cy - 15 * s)} {n(cx + 9 * s)},{n(cy - 13 * s)} "
            f"C{n(cx + 16 * s)},{n(cy - 9 * s)} {n(cx + 14 * s)},{n(cy)} {n(cx)},{n(cy + 9 * s)}Z")


def cloud_d(cx, cy, s=1.0):
    """A cartoon cloud about 112 x 46 units (times s), flat bottom at cy + 12 s."""
    p = lambda x, y: f"{n(cx + x * s)},{n(cy + y * s)}"
    return (f"M{p(-40, 12)} C{p(-56, 12)} {p(-56, -8)} {p(-40, -10)} C{p(-38, -28)} {p(-14, -32)} {p(-6, -18)} "
            f"C{p(2, -34)} {p(32, -32)} {p(34, -10)} C{p(52, -10)} {p(54, 12)} {p(38, 12)} Z")


def drop_d(x, y, s=1.0):
    """A water drop with its tip at (x, y), about 16 x 27 units (times s)."""
    p = lambda a, b: f"{n(x + a * s)},{n(y + b * s)}"
    return (f"M{p(0, 0)} C{p(4, 9)} {p(8, 15)} {p(8, 19)} C{p(8, 24)} {p(4, 27)} {p(0, 27)} "
            f"C{p(-4, 27)} {p(-8, 24)} {p(-8, 19)} C{p(-8, 15)} {p(-4, 9)} {p(0, 0)}Z")


_TOK = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
_NARGS = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}


def shift_path(d, dx, dy):
    """Path data d moved by (dx, dy). Only absolute commands are moved (this kit writes only
    those); relative ones keep their offsets, which is right except for a leading `m`."""
    toks = _TOK.findall(d)
    out, i, cmd, first = [], 0, None, True
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            out.append(t)
            i += 1
            continue
        C = cmd.upper()
        k = _NARGS[C]
        a = [float(v) for v in toks[i:i + k]]
        i += k
        absolute = cmd.isupper() or (first and cmd == "m")
        if absolute:
            if C == "H":
                a[0] += dx
            elif C == "V":
                a[0] += dy
            elif C == "A":
                a[5] += dx
                a[6] += dy
            else:
                for j in range(0, k, 2):
                    a[j] += dx
                    a[j + 1] += dy
        first = False
        out.append(" ".join(n(v) for v in a))
        if C == "M":
            cmd = "L" if cmd == "M" else "l"
    return " ".join(out).replace(" Z", "Z")


def path_points(d):
    """Every end and control point of a path (absolute commands), enough for a rough bounding box."""
    toks = _TOK.findall(d)
    i, cmd, pts = 0, None, []
    x = y = 0.0
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            continue
        C = cmd.upper()
        k = _NARGS[C]
        a = [float(v) for v in toks[i:i + k]]
        i += k
        if C == "H":
            x = a[0]
        elif C == "V":
            y = a[0]
        elif C == "A":
            x, y = a[5], a[6]
        else:
            for j in range(0, k, 2):
                pts.append((a[j], a[j + 1]))
            x, y = a[k - 2], a[k - 1]
        pts.append((x, y))
        if C == "M":
            cmd = "L"
    return pts


# ---------------------------------------------------------------- painting
def stroke(d, col, k=1.0, cap=False, extra=""):
    """The outline of d: k times the picture's outline width."""
    c = ' stroke-linecap="round"' if cap else ""
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw(k)}" stroke-linejoin="round"{c}{extra}/>'


def part(d, fill, s=(-6, -7), sh=None, ol=None, hl="", k=1.0, fr=False, op=None):
    """One shape: flat fill, a hard cel shadow crescent at the bottom-right (s = how far the lit
    copy moves up-left; None for no shadow), highlight `hl` (SVG drawn on top), and an outline
    (ol: its colour, None = lin(fill), False = none; k: its weight)."""
    f = ' fill-rule="evenodd"' if fr else ""
    o_ = f' opacity="{op}"' if op is not None else ""
    if s:
        out = f'<path d="{d}" fill="{sh or shd(fill)}"{f}{o_}/>'
        out += (f'<g clip-path="{clip(d, fr)}"><path d="{d}" fill="{fill}"{f}{o_} '
                f'transform="translate({n(s[0])} {n(s[1])})"/></g>')
    else:
        out = f'<path d="{d}" fill="{fill}"{f}{o_}/>'
    out += hl
    if ol is not False:
        out += stroke(d, ol or lin(fill), k)
    return out


def comp(d, fill, inner="", s=(-6, -7), sh=None, ol=None, hl="", fr=False, k=1.0):
    """A shape with things painted inside it (clipped to it); highlight and outline on top."""
    out = part(d, fill, s, sh, False, "", fr=fr)
    out += clipped(d, inner, fr)
    out += hl
    if ol is not False:
        out += stroke(d, ol or lin(fill), k)
    return out


def flat(d, fill, op=None, fr=False):
    """A plain filled path (no shadow, no outline): patterns, spots, background shapes."""
    f = ' fill-rule="evenodd"' if fr else ""
    o_ = f' opacity="{op}"' if op is not None else ""
    return f'<path d="{d}" fill="{fill}"{f}{o_}/>'


def celov(d, s, op=.16, col="#3B1E5A"):
    """A see-through cel shadow over a many-coloured shape d (moved copy s, like part's)."""
    big = "M-5000,-5000 H5000 V5000 H-5000Z "
    return clipped(d, f'<path d="{big}{shift_path(d, s[0], s[1])}" fill="{col}" fill-rule="evenodd" opacity="{op}"/>')


def ln(d, col, k=.9, op=None):
    """A drawn line (mouth, crease, seam...), k times the outline weight, round ends."""
    o_ = f' opacity="{op}"' if op is not None else ""
    return (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw(k)}" stroke-linecap="round" '
            f'stroke-linejoin="round"{o_}/>')


def hi(d, w=5, op=.75):
    """A white highlight stroke (w in drawing units: it grows with the drawing)."""
    return (f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="{n(w)}" stroke-linecap="round" '
            f'stroke-linejoin="round" opacity="{op}"/>')


def hidot(cx, cy, r, op=.85):
    return f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="#FFFFFF" opacity="{op}"/>'


def hose(d, col, w, ol=None):
    """A tube drawn as a thick line (w drawing units) with a thin darker edge."""
    e = OLW * .9 / SCALE
    return (f'<path d="{d}" fill="none" stroke="{ol or lin(col)}" stroke-width="{n(w + 2 * e)}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{n(w)}" stroke-linecap="round" stroke-linejoin="round"/>')


def ground(cx, cy, rx, ry, op=.22, col=SHADOW):
    """A soft contact shadow under something standing (an ellipse that fades out at its edge)."""
    f = rg([(0, col, op), (.55, col, op * .7), (1, col, 0)])
    return f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}" fill="{f}"/>'


def g(inner, tr=""):
    return f'<g transform="{tr}">{inner}</g>' if tr else inner


def sparkle(cx, cy, r, col="#FFFFFF", op=.95):
    """A four-pointed twinkle (clean, shiny)."""
    d = (f"M{n(cx)},{n(cy - r)} Q{n(cx + r * .16)},{n(cy - r * .16)} {n(cx + r)},{n(cy)} "
         f"Q{n(cx + r * .16)},{n(cy + r * .16)} {n(cx)},{n(cy + r)} Q{n(cx - r * .16)},{n(cy + r * .16)} {n(cx - r)},{n(cy)} "
         f"Q{n(cx - r * .16)},{n(cy - r * .16)} {n(cx)},{n(cy - r)}Z")
    return f'<path d="{d}" fill="{col}" opacity="{op}"/>'


# ---------------------------------------------------------------- faces
def eye(cx, cy, rx, ry, lx=1.0, ly=2.0, pc="#2E1C14", ol="#5A3424", big=1.0):
    """A big cartoon eye: white, a large dark pupil (moved lx, ly to look somewhere), a warm glow
    at the pupil's bottom and two shines."""
    o = part(ell(cx, cy, rx, ry), "#FFFFFF", s=None, ol=ol, k=.8)
    px, py, prx, pry = cx + lx, cy + ly, rx * .7 * big, ry * .72 * big
    o += flat(ell(px, py, prx, pry), pc)
    o += clipped(ell(px, py, prx, pry),
                 f'<ellipse cx="{n(px)}" cy="{n(py + pry * .95)}" rx="{n(prx * 1.1)}" ry="{n(pry * .55)}" '
                 f'fill="{mix(pc, "#C8875A", .55)}" opacity=".8"/>')
    o += f'<circle cx="{n(px - prx * .32)}" cy="{n(py - pry * .36)}" r="{n(prx * .42)}" fill="#FFFFFF"/>'
    o += f'<circle cx="{n(px + prx * .38)}" cy="{n(py + pry * .3)}" r="{n(prx * .17)}" fill="#FFFFFF"/>'
    return o


def dot_eye(cx, cy, r, pc="#2E1C14"):
    """A small shiny dark eye (for small faces where a big white eye would not fit)."""
    return (flat(ell(cx, cy, r * .82, r), pc) + f'<circle cx="{n(cx - r * .28)}" cy="{n(cy - r * .38)}" r="{n(r * .36)}" fill="#FFFFFF"/>'
            + f'<circle cx="{n(cx + r * .3)}" cy="{n(cy + r * .34)}" r="{n(r * .14)}" fill="#FFFFFF"/>')


def happy_eye(cx, cy, w, col="#3A2418"):
    """A closed, smiling eye (^)."""
    return ln(f"M{n(cx - w)},{n(cy + w * .35)} Q{n(cx)},{n(cy - w * .9)} {n(cx + w)},{n(cy + w * .35)}", col, 1.35)


def blush(cx, cy, rx=9, ry=5.5, col="#FF8E9A", op=.5):
    return f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}" fill="{col}" opacity="{op}"/>'


def smile(cx, cy, w, col="#5A2018", k=1.2):
    """A simple smile line w wide."""
    return ln(f"M{n(cx - w / 2)},{n(cy)} Q{n(cx)},{n(cy + w * .45)} {n(cx + w / 2)},{n(cy)}", col, k)


def open_mouth(cx, cy, w, col="#8A2F2F", tongue="#FF8A93", ol="#5A2018"):
    """A happy open mouth (D shape) w wide, top edge at cy."""
    h = w * .62
    d = (f"M{n(cx - w / 2)},{n(cy)} Q{n(cx)},{n(cy + w * .18)} {n(cx + w / 2)},{n(cy)} "
         f"C{n(cx + w * .46)},{n(cy + h * .8)} {n(cx + w * .2)},{n(cy + h)} {n(cx)},{n(cy + h)} "
         f"C{n(cx - w * .2)},{n(cy + h)} {n(cx - w * .46)},{n(cy + h * .8)} {n(cx - w / 2)},{n(cy)}Z")
    inner = f'<ellipse cx="{n(cx)}" cy="{n(cy + h)}" rx="{n(w * .34)}" ry="{n(h * .42)}" fill="{tongue}"/>'
    return comp(d, col, inner, s=None, ol=ol, k=.8)


# ---------------------------------------------------------------- fitting and writing
def fit(fn, box, size=THING, fill=FILL, cx=None, cy=None, rot=0, flip=False, maxs=99.0, **kw):
    """Draw fn(**kw) (in its own units; `box` = (x0, y0, x1, y1) is how far it reaches) scaled so its
    longer side is `fill` units and centred at (cx, cy) of a `size` picture (default its middle).
    While it draws, SCALE holds the scale, so outlines come out at the picture's weight."""
    global SCALE
    x0, y0, x1, y1 = box
    s = min(fill / max(x1 - x0, y1 - y0), maxs)
    old = SCALE
    SCALE = old * s
    try:
        svg = fn(**kw)
    finally:
        SCALE = old
    cx = size / 2 if cx is None else cx
    cy = size / 2 if cy is None else cy
    fx = -1 if flip else 1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    r = f" rotate({n(rot)})" if rot else ""
    return (f'<g transform="translate({n(cx)} {n(cy)}){r} scale({fx * s:.4f} {s:.4f}) '
            f'translate({n(-mx)} {n(-my)})">{svg}</g>')


def at(svg_fn, x, y, s, rot=0, **kw):
    """Draw svg_fn(**kw) moved to (x, y) and scaled by s (outlines keep the picture's weight)."""
    global SCALE
    old = SCALE
    SCALE = old * s
    try:
        svg = svg_fn(**kw)
    finally:
        SCALE = old
    r = f" rotate({n(rot)})" if rot else ""
    return f'<g transform="translate({n(x)} {n(y)}){r} scale({s:.4f})">{svg}</g>'


def doc(body, w=THING, h=THING):
    """A whole SVG file: the picture's <defs> first, then the drawing."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'{D.svg()}{body}</svg>\n')


FORBIDDEN = ("<filter", "<mask", "<style", "style=", "class=", "<text", "<image", "<foreignObject",
             "<pattern", "vector-effect", "mask=", "filter=")


def check(name, svg):
    """The flutter_svg rules: no filters, masks, CSS, text, images or patterns; under 800 <use>;
    about 60 KB at most; whole, parseable XML."""
    bad = [f for f in FORBIDDEN if f in svg]
    if bad:
        raise SystemExit(f"{name}: uses {bad} (flutter_svg cannot draw these)")
    if svg.count("<use") >= 800:
        raise SystemExit(f"{name}: too many <use>")
    if not svg.rstrip().endswith("</svg>"):
        raise SystemExit(f"{name}: does not end with </svg>")
    ET.fromstring(svg)
    kb = len(svg.encode()) / 1024
    if kb > 60:
        raise SystemExit(f"{name}: {kb:.0f} KB (keep under 60 KB)")
    return kb


def save(name, body, w=THING, h=THING, out=OUT):
    """Write <out>/<name>.svg after checking it; returns its size in KB."""
    svg = doc(body, w, h)
    kb = check(name, svg)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{name}.svg").write_text(svg)
    ET.parse(out / f"{name}.svg")
    return kb
