"""想一想樂園: the pictures that belong to the whole park, not to one land.

    python3 park_art.py                  # writes app/assets/art/park/*.svg and design/art/park_spots.json
    python3 park_art.py preview OUT.png  # one sheet: the nine 阿布 (full size and 120 px), both maps with
                                         # grey boxes where the app puts its words and buttons, and the icon
    python3 park_art.py boxes OUT.png    # only the day map with the grey boxes (to check the free spots)

Pictures (all in app/assets/art/park/):
    abu_<land>_<pose>.svg   阿布, the little fox detective (brown detective cap, magnifying glass),
                            200 x 200, see-through, standing on the same spot at the same size in
                            all nine, so the app can swap them in place.
                            land: city  A 動畫片風 (thin outlines in a darker shade of each fill,
                                        flat fills, one hard cel shadow per shape)
                                  forest B 剪紙拼貼風 (layers of paper with uneven edges, a soft
                                        shadow under each layer, paper grain, no outlines)
                                  blocks C 幾何積木風 (circles, triangles, rounded rectangles; flat,
                                        no outlines)
                            pose: wave (waving hello), think (paw on chin, glass up, eyes up to the
                                  side), cheer (both arms up, big smile, happy eyes)
    map.svg                 the park map (home screen), 390 x 844, painted edge to edge: one sky, one
                            cream path from the entrance at the bottom through 卡通城 (A), 紙片森林 (B)
                            and 積木王國 (C) to the block castle at the top. No words and no signs:
                            the app puts the title, the six game signs, the land labels, 阿布 and the
                            buttons on top. park_spots.json says where (fractions of 390 x 844).
    map_night.svg           the same map at night (the rest screen): dark blue sky, stars, a crescent
                            moon, warm lights in the windows, the castle, the paper lanterns.

The approved look is docs/mockups/ (10_樂園地圖, 15_阿布變身, 0_畫風選擇) drawn by make_mockups.py.
The app draws these with flutter_svg, which has no filters, masks or CSS, so the mockups' looks are
rebuilt here from paths, gradients, clip paths, <use> and opacity:
  - style A's cel shadow (a mask in the mockup): inside a clip of the shape, the shape in the shadow
    colour, then the shape again in its own colour moved up-left.
  - style B's paper filter (torn edge, grain, drop shadow): the outline is cut into short pieces and
    pushed in and out a little (a fixed random wobble), two see-through copies moved down-right make
    the soft shadow, and a sprinkle of tiny paper fibres is drawn inside a clip of the layer.
Every shape a picture uses more than once is written once in <defs> without paint, and every <use>
says its own fill and stroke (flutter_svg lets the <use>'s paint win; Chromium too, as the shape has none).
Deterministic: random numbers come from random.Random seeded with the shape itself.
"""
import colorsys
import hashlib
import json
import math
import pathlib
import random
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "app" / "assets" / "art" / "park"
SPOTS_JSON = HERE / "park_spots.json"
W, H = 390, 844

# ---------------------------------------------------------------- colours (as the mockups)
FOX = "#FF8A3D"
FOXD = "#6E3B22"       # paws, feet, ear tips
CREAM = "#FFF6EA"
GOLD = "#FFC233"
INK = "#4B3A5E"
WHITE_OL = "#8E86A8"
CAP = "#A8693D"
CAP_D = "#8A5330"
CAP_BOW = "#B97A48"
HANDLE = "#9B5E34"
LENS = "#D9F3FF"
# style C (blocks)
CR, CB, CY, CG, CP, CT = "#EF233C", "#3A86FF", "#FFBF1F", "#2EC46A", "#8338EC", "#2EC4B6"
C_DK = "#2B2D42"


def _rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def mix(a, b, t):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(x + (y - x) * t))) for x, y in zip(_rgb(a), _rgb(b)))


def lt(c, t):
    return mix(c, "#FFFFFF", t)


def _hls(c):
    return colorsys.rgb_to_hls(*[x / 255 for x in _rgb(c)])


def _hex(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h % 1, max(0, min(1, l)), max(0, min(1, s)))
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def tone(c, l=1.0, s=1.0, dh=0.0):
    h, L, S = _hls(c)
    return _hex(h + dh, L * l, S * s)


def shd(c):
    """Cel shadow: the same colour, darker and a little richer."""
    h, L, S = _hls(c)
    if S < .12:
        return mix(c, "#B9B2D6", .45)
    return _hex(h - .01, L * .84, min(1, S * 1.08 + .04))


def lin(c):
    """Style A outline: a dark shade of the fill (not black)."""
    h, L, S = _hls(c)
    if S < .12 or L > .93:
        return WHITE_OL
    return _hex(h - .015, L * .52, min(1, S * 1.05 + .1))


def mute(c):
    """Style B: paper colours (a little softer)."""
    h, L, S = _hls(c)
    return mix(_hex(h, L, S * .8), "#EFE4D2", .14)


def night(c):
    """The map at night: the same colour, darker, bluer and quieter."""
    h, L, S = _hls(c)
    d = _hex(h, L * .5 + .03, S * .5)
    return mix(d, "#1E2A5E", .4)


# ---------------------------------------------------------------- numbers and the defs registry
def n(v):
    s = f"{v:.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    return "0" if s == "-0" else s


class Defs:
    """The <defs> of one picture. raw=True: not changed by the night colours (lights, stars)."""

    def __init__(self):
        self.d = {}

    def add(self, key, svg, raw=False):
        self.d.setdefault(key, (svg, raw))
        return key

    def svg(self, mapper=None):
        out = []
        for svg, raw in self.d.values():
            out.append(svg if raw or mapper is None else mapper(svg))
        return "<defs>" + "".join(out) + "</defs>" if out else ""


D = Defs()
STYLE = "A"        # A cartoon, B paper (C has its own drawings)
SC = 1.0           # picture units per drawing unit (paper wobble and shadows are sized on the picture)
SW = 2.2           # style A outline width, in drawing units
GRAIN = None       # id of the paper-fibre sprinkle for this picture (style B), or None
NIGHT = False
RAW = False        # gradients made now are lights (not darkened at night)


def _h(*parts):
    return hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:7]


def _stops(stops):
    out = []
    for s in stops:
        o = f' stop-opacity="{s[2]:.3g}"' if len(s) > 2 and s[2] != 1 else ""
        out.append(f'<stop offset="{s[0]:.3g}" stop-color="{s[1]}"{o}/>')
    return "".join(out)


def lg(stops, x1=0, y1=0, x2=0, y2=1, user=False):
    k = "l" + _h(stops, x1, y1, x2, y2, user, RAW)
    u = ' gradientUnits="userSpaceOnUse"' if user else ""
    D.add(k, f'<linearGradient id="{k}" x1="{n(x1) if user else x1}" y1="{n(y1) if user else y1}" '
             f'x2="{n(x2) if user else x2}" y2="{n(y2) if user else y2}"{u}>{_stops(stops)}</linearGradient>', RAW)
    return f"url(#{k})"


def rg(stops, cx=.5, cy=.5, r=.5, user=False):
    k = "r" + _h(stops, cx, cy, r, user, RAW)
    u = ' gradientUnits="userSpaceOnUse"' if user else ""
    D.add(k, f'<radialGradient id="{k}" cx="{n(cx) if user else cx}" cy="{n(cy) if user else cy}" '
             f'r="{n(r) if user else r}"{u}>{_stops(stops)}</radialGradient>', RAW)
    return f"url(#{k})"


def shape(d):
    """A shape kept once in <defs> (no paint); returns its id."""
    k = "p" + _h(d)
    D.add(k, f'<path id="{k}" d="{d}"/>')
    return k


def use(k, paint, extra=""):
    return f'<use href="#{k}" {paint}{extra}/>'


def clip_of(k):
    c = "k" + k[1:]
    D.add(c, f'<clipPath id="{c}"><use href="#{k}"/></clipPath>')
    return f"url(#{c})"


def clip(d):
    return clip_of(shape(d))


LIT0, LIT1 = "<!--lit-->", "<!--/lit-->"


def lit(svg):
    """A light: kept in its own colours at night."""
    return LIT0 + svg + LIT1 if NIGHT else svg


def glow(cx, cy, r, col="#FFD66B", op=.55):
    """A soft round glow (night lights)."""
    global RAW
    RAW = True
    f = rg([(0, col, op), (.45, col, op * .45), (1, col, 0)])
    RAW = False
    return lit(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{f}"/>')


# ---------------------------------------------------------------- shape helpers
def spline(pts, k=10, closed=False):
    """Catmull-Rom curve through pts (tuples: x, y[, width])."""
    P = list(pts)
    P = [P[-1]] + P + [P[0], P[1]] if closed else [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(k):
            t = j / k
            out.append(tuple(.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t ** 3)
                             for a, b, c, d in zip(p0, p1, p2, p3)))
    if not closed:
        out.append(tuple(P[-2]))
    return out


def poly(pts, close=True):
    return "M" + " L".join(f"{n(p[0])},{n(p[1])}" for p in pts) + ("Z" if close else "")


def _num(v):
    t = n(v)
    return t.replace("0.", ".", 1) if t.startswith("0.") else t.replace("-0.", "-.", 1)


def rpoly(pts, close=True):
    """A polyline in relative steps (short to write): rounded to 0.1 first, so the steps add up exactly."""
    q = [(round(x * 10), round(y * 10)) for x, y in pts]
    out = [f"M{_num(q[0][0] / 10)},{_num(q[0][1] / 10)}l"]
    steps = []
    for (x0, y0), (x1, y1) in zip(q, q[1:]):
        dx, dy = _num((x1 - x0) / 10), _num((y1 - y0) / 10)
        steps.append(f"{dx}{dy}" if dy.startswith("-") else f"{dx},{dy}")
    return out[0] + " ".join(steps) + ("Z" if close else "")


def tube(pts, k=10):
    """Outline of an arm, a handle...: pts are (x, y, half-width) along its middle, round ends."""
    c = spline(pts, k)
    L, R = [], []
    for i, (x, y, w) in enumerate(c):
        a, b = c[max(0, i - 1)], c[min(len(c) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln_ = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln_, dx / ln_
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
    w1, w0 = c[-1][2], c[0][2]
    d = "M" + " L".join(f"{n(x)},{n(y)}" for x, y in L)
    d += f" A{n(w1)},{n(w1)} 0 0 0 {n(R[-1][0])},{n(R[-1][1])}"
    d += " L" + " L".join(f"{n(x)},{n(y)}" for x, y in reversed(R))
    d += f" A{n(w0)},{n(w0)} 0 0 0 {n(L[0][0])},{n(L[0][1])}Z"
    return d


def sym(top, segs):
    """Closed path symmetric about x=0: cubic segments (c1, c2, p) down the right half."""
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
    r = min(r, w / 2, h / 2)
    return (f"M{n(x + r)},{n(y)} H{n(x + w - r)} A{n(r)},{n(r)} 0 0 1 {n(x + w)},{n(y + r)} V{n(y + h - r)} "
            f"A{n(r)},{n(r)} 0 0 1 {n(x + w - r)},{n(y + h)} H{n(x + r)} A{n(r)},{n(r)} 0 0 1 {n(x)},{n(y + h - r)} "
            f"V{n(y + r)} A{n(r)},{n(r)} 0 0 1 {n(x + r)},{n(y)}Z")


def star_d(R, r, k=5, cx=0, cy=0, rot=-90, round_=0.0):
    pts = []
    for i in range(2 * k):
        a = math.radians(rot + i * 180 / k)
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


def sparkle_d(cx, cy, r):
    """A four-pointed twinkle."""
    k = .16
    return (f"M{n(cx)},{n(cy - r)} Q{n(cx + r * k)},{n(cy - r * k)} {n(cx + r)},{n(cy)} Q{n(cx + r * k)},{n(cy + r * k)} {n(cx)},{n(cy + r)} "
            f"Q{n(cx - r * k)},{n(cy + r * k)} {n(cx - r)},{n(cy)} Q{n(cx - r * k)},{n(cy - r * k)} {n(cx)},{n(cy - r)}Z")


def cloud_d(cx, cy, s=1.0):
    p = lambda x, y: f"{n(cx + x * s)},{n(cy + y * s)}"
    return (f"M{p(-40, 12)} C{p(-56, 12)} {p(-56, -8)} {p(-40, -10)} C{p(-38, -28)} {p(-14, -32)} {p(-6, -18)} "
            f"C{p(2, -34)} {p(32, -32)} {p(34, -10)} C{p(52, -10)} {p(54, 12)} {p(38, 12)} Z")


def g(inner, tr=""):
    return f'<g transform="{tr}">{inner}</g>' if tr else inner


# ---------------------------------------------------------------- paths to points (for the paper edge)
_TOK = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
_NARGS = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7}


def _arc(x1, y1, rx, ry, phi, fa, fs, x2, y2, tol):
    if rx == 0 or ry == 0:
        return [(x2, y2)]
    rx, ry = abs(rx), abs(ry)
    c, s = math.cos(math.radians(phi)), math.sin(math.radians(phi))
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = c * dx + s * dy, -s * dx + c * dy
    lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    co = math.sqrt(max(0.0, num / den)) if den else 0.0
    if fa == fs:
        co = -co
    cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
    cx, cy = c * cxp - s * cyp + (x1 + x2) / 2, s * cxp + c * cyp + (y1 + y2) / 2

    def ang(ux, uy, vx, vy):
        return math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)

    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not fs and dt > 0:
        dt -= 2 * math.pi
    elif fs and dt < 0:
        dt += 2 * math.pi
    k = max(2, math.ceil(abs(dt) * max(rx, ry) / tol))
    out = []
    for j in range(1, k + 1):
        t = t1 + dt * j / k
        out.append((cx + rx * math.cos(t) * c - ry * math.sin(t) * s, cy + rx * math.cos(t) * s + ry * math.sin(t) * c))
    return out


def flatten(d, tol=1.0):
    """A path -> [(points, closed)]: curves and arcs cut into short straight pieces about `tol` long."""
    toks = _TOK.findall(d)
    subs, cur = [], []
    i, cmd = 0, "M"
    x = y = sx = sy = 0.0
    last_c = None
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]
            i += 1
            if cmd in "Zz":
                if len(cur) > 1:
                    subs.append((cur, True))
                cur = []
                x, y = sx, sy
                last_c = None
                continue
        U, rel = cmd.upper(), cmd.islower()
        k = _NARGS[U]
        a = [float(v) for v in toks[i:i + k]]
        i += k
        ox, oy = (x, y) if rel else (0.0, 0.0)
        if U == "M":
            if len(cur) > 1:
                subs.append((cur, False))
            x, y = a[0] + ox, a[1] + oy
            sx, sy = x, y
            cur = [(x, y)]
            cmd = "l" if rel else "L"
            last_c = None
            continue
        if not cur:
            cur = [(x, y)]
        if U == "L":
            pts, last_c = [(a[0] + ox, a[1] + oy)], None
        elif U == "H":
            pts, last_c = [(a[0] + ox, y)], None
        elif U == "V":
            pts, last_c = [(x, a[0] + oy)], None
        elif U in "CS":
            if U == "C":
                p1, p2, p3 = (a[0] + ox, a[1] + oy), (a[2] + ox, a[3] + oy), (a[4] + ox, a[5] + oy)
            else:
                p1 = (2 * x - last_c[0], 2 * y - last_c[1]) if last_c and last_c[2] == "C" else (x, y)
                p2, p3 = (a[0] + ox, a[1] + oy), (a[2] + ox, a[3] + oy)
            L_ = math.dist((x, y), p1) + math.dist(p1, p2) + math.dist(p2, p3)
            m = max(2, math.ceil(L_ / tol))
            pts = []
            for j in range(1, m + 1):
                t = j / m
                u = 1 - t
                pts.append((u ** 3 * x + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                            u ** 3 * y + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
            last_c = (p2[0], p2[1], "C")
        elif U in "QT":
            if U == "Q":
                p1, p2 = (a[0] + ox, a[1] + oy), (a[2] + ox, a[3] + oy)
            else:
                p1 = (2 * x - last_c[0], 2 * y - last_c[1]) if last_c and last_c[2] == "Q" else (x, y)
                p2 = (a[0] + ox, a[1] + oy)
            L_ = math.dist((x, y), p1) + math.dist(p1, p2)
            m = max(2, math.ceil(L_ / tol))
            pts = []
            for j in range(1, m + 1):
                t = j / m
                u = 1 - t
                pts.append((u * u * x + 2 * u * t * p1[0] + t * t * p2[0], u * u * y + 2 * u * t * p1[1] + t * t * p2[1]))
            last_c = (p1[0], p1[1], "Q")
        else:  # A
            pts = _arc(x, y, a[0], a[1], a[2], int(a[3]), int(a[4]), a[5] + ox, a[6] + oy, tol)
            last_c = None
        cur += pts
        x, y = pts[-1]
    if len(cur) > 1:
        subs.append((cur, False))
    return subs


def _resample(pts, closed, step):
    P = list(pts) + ([pts[0]] if closed else [])
    seg = [math.dist(P[i], P[i + 1]) for i in range(len(P) - 1)]
    total = sum(seg)
    if total == 0:
        return [pts[0]], total
    m = max(6 if closed else 2, round(total / step))
    out, j, acc = [], 0, 0.0
    for q in range(m + (0 if closed else 1)):
        s = total * q / m
        while j < len(seg) - 1 and acc + seg[j] < s:
            acc += seg[j]
            j += 1
        t = 0 if seg[j] == 0 else min(1, max(0, (s - acc) / seg[j]))
        out.append((P[j][0] + (P[j + 1][0] - P[j][0]) * t, P[j][1] + (P[j + 1][1] - P[j][1]) * t))
    return out, total


def torn(d, amp=1.1, step=2.6, wave=20.0, bbox=False):
    """The paper edge: the outline cut into pieces `step` long and pushed in and out by a fixed wobble
    (long waves about `wave` long, plus small fibres). Sizes are in picture units (divided by SC)."""
    amp, step, wave = amp / SC, step / SC, wave / SC
    out, allp = [], []
    for si, (pts, closed) in enumerate(flatten(d, step / 3)):
        q, total = _resample(pts, closed, step)
        if len(q) < 3:
            continue
        rnd = random.Random(int(_h(d, si, round(SC, 3)), 16))
        m = len(q)
        c1 = max(1, round(total / wave))
        c2 = max(2, round(total / (wave * .38)))
        p1, p2 = rnd.uniform(0, 6.3), rnd.uniform(0, 6.3)
        r = [rnd.uniform(-1, 1) for _ in range(m)]
        res = []
        for i in range(m):
            a, b = q[(i - 1) % m] if closed else q[max(0, i - 1)], q[(i + 1) % m] if closed else q[min(m - 1, i + 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            l_ = math.hypot(dx, dy) or 1
            nx, ny = -dy / l_, dx / l_
            t = i / m
            rr_ = (r[i] * 2 + r[i - 1] + r[(i + 1) % m]) / 4
            off = amp * (.55 * math.sin(2 * math.pi * c1 * t + p1) + .3 * math.sin(2 * math.pi * c2 * t + p2) + .45 * rr_)
            if not closed and (i == 0 or i == m - 1):
                off = 0
            res.append((q[i][0] + nx * off, q[i][1] + ny * off))
        out.append(rpoly(res, closed))
        allp += res
    d2 = " ".join(out)
    if bbox:
        xs, ys = [p[0] for p in allp], [p[1] for p in allp]
        return d2, (min(xs), min(ys), max(xs), max(ys))
    return d2


# ---------------------------------------------------------------- one shape, in style A or B
PSH = "#4A3420"        # the colour of paper shadows


def paper(d, fill, op=None, grain=True, sh=1.0, step=None):
    """Style B: one paper layer (torn edge, soft shadow under it, grain), no outline."""
    td, (x0, y0, x1, y1) = torn(d, step=step or (3.4 if ONE_SHADOW else 2.6), bbox=True)
    k = shape(td)
    o_ = f' opacity="{op}"' if op is not None else ""
    c = mute(fill)
    f = c if ONE_SHADOW else lg([(0, lt(c, .07)), (1, tone(c, .965))], 0, 0, .8, 1)
    out = ""
    if sh and not ONE_SHADOW:
        out += use(k, f'fill="{PSH}" opacity="{_num(.10 * sh)}"', f' transform="translate({n(1.9 / SC)} {n(3.4 / SC)})"')
        out += use(k, f'fill="{PSH}" opacity="{_num(.16 * sh)}"', f' transform="translate({n(.8 / SC)} {n(1.5 / SC)})"')
    elif sh:
        out += use(k, f'fill="{PSH}" opacity="{_num(.2 * sh)}"', f' transform="translate({n(1.1 / SC)} {n(2.1 / SC)})"')
    out += use(k, f'fill="{f}"{o_}')
    if grain and GRAIN:
        T = GRAIN_T / SC
        tiles = "".join(f'<use href="#{GRAIN}" transform="translate({n(i * T)} {n(j * T)})"/>'
                        for j in range(math.floor(y0 / T), math.ceil(y1 / T)) for i in range(math.floor(x0 / T), math.ceil(x1 / T)))
        out += f'<g clip-path="{clip_of(k)}">{tiles}</g>'
    return out


GRAIN_T = 40.0     # the paper fibres come in tiles this big (picture units)
ONE_SHADOW = False # the small paper things of the map get one shadow copy, not two


def make_grain(gap=4.2, seed=7):
    """The paper fibres: one tile of tiny light and dark strokes about `gap` apart (picture units)."""
    global GRAIN
    rnd = random.Random(seed)
    T, gp = GRAIN_T / SC, gap / SC
    light, dark = [], []
    k = max(1, round(T / gp))
    for j in range(k):
        for i in range(k):
            px, py = (i + rnd.uniform(.05, .95)) * T / k, (j + rnd.uniform(.05, .95)) * T / k
            a = rnd.uniform(-.5, .5) + (0 if rnd.random() < .7 else 1.57)
            ln_ = rnd.uniform(.5, 1.6) / SC
            (light if rnd.random() < .6 else dark).append(f"M{n(px)},{n(py)}l{n(math.cos(a) * ln_)},{n(math.sin(a) * ln_)}")
    w = n(.9 / SC)
    GRAIN = "grain"
    D.add("grain", f'<g id="grain"><path d="{"".join(light)}" fill="none" stroke="#FFFFFF" stroke-width="{w}" stroke-linecap="round" opacity=".3"/>'
                   f'<path d="{"".join(dark)}" fill="none" stroke="#5A3A1E" stroke-width="{w}" stroke-linecap="round" opacity=".1"/></g>')


def part(d, fill, s=(-6, -7), sh=None, ol=None, hl="", cls=1.0, op=None):
    """One shape: flat fill, a hard shadow crescent at the bottom-right, an optional highlight and a thin
    outline in a darker shade of the fill (style A). In style B: one paper layer."""
    if STYLE == "B":
        return paper(d, fill, op)
    k = shape(d)
    o_ = f' opacity="{op}"' if op is not None else ""
    if s:
        out = (f'<g clip-path="{clip_of(k)}"{o_}>' + use(k, f'fill="{sh or shd(fill)}"')
               + use(k, f'fill="{fill}"', f' transform="translate({n(s[0])} {n(s[1])})"') + "</g>")
    else:
        out = use(k, f'fill="{fill}"{o_}')
    out += hl
    if ol is not False:
        out += use(k, f'fill="none" stroke="{ol or lin(fill)}"', f' stroke-width="{n(SW * cls)}" stroke-linejoin="round"')
    return out


def comp(d, fill, inner="", s=(-6, -7), sh=None, ol=None, hl=""):
    """A shape with things painted inside it (clipped to it), outline on top."""
    if STYLE == "B":
        out = paper(d, fill)
        if inner:
            out += f'<g clip-path="{clip_of(shape(torn(d, step=3.4 if ONE_SHADOW else 2.6)))}">{inner}</g>'
        return out
    out = part(d, fill, s, sh, False)
    k = shape(d)
    if inner:
        out += f'<g clip-path="{clip_of(k)}">{inner}</g>'
    out += hl
    if ol is not False:
        out += use(k, f'fill="none" stroke="{ol or lin(fill)}"', f' stroke-width="{n(SW)}" stroke-linejoin="round"')
    return out


def ln(d, col, cls=.9):
    """A drawn line (mouth, brow, crease). Style B: a thin strip of paper."""
    if STYLE == "B":
        dd = torn(d, .35, 2.2, 12)
        w = 2.7 / SC
        c = mute(col)
        return (f'<path d="{dd}" fill="none" stroke="{PSH}" stroke-width="{n(w)}" stroke-linecap="round" stroke-linejoin="round" '
                f'opacity=".16" transform="translate({n(.7 / SC)} {n(1.3 / SC)})"/>'
                f'<path d="{dd}" fill="none" stroke="{c}" stroke-width="{n(w)}" stroke-linecap="round" stroke-linejoin="round"/>')
    return (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{n(SW * cls)}" stroke-linecap="round" '
            f'stroke-linejoin="round"/>')


def hi(d, w=5, op=.75):
    """A white highlight stroke (style A only)."""
    if STYLE == "B":
        return ""
    return f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="{n(w)}" stroke-linecap="round" opacity="{op}"/>'


def hidot(cx, cy, r, op=.85):
    if STYLE == "B":
        return ""
    return f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="#FFFFFF" opacity="{op}"/>'


def eye(cx, cy, rx, ry, lx=1.0, ly=2.0, pc="#2E1C14", ol="#5A3424"):
    """Big cartoon eye: white, a large dark pupil, two shines."""
    o = part(ell(cx, cy, rx, ry), "#FFFFFF", s=None, ol=ol)
    px, py, prx, pry = cx + lx, cy + ly, rx * .7, ry * .72
    if STYLE == "A":
        k = shape(ell(cx, cy, rx, ry))
        o += (f'<g clip-path="{clip_of(k)}">' + part(ell(px, py, prx, pry), pc, s=None, ol=False)
              + f'<g clip-path="{clip(ell(px, py, prx, pry))}"><ellipse cx="{n(px)}" cy="{n(py + pry * .95)}" rx="{n(prx * 1.1)}" '
              f'ry="{n(pry * .55)}" fill="{mix(pc, "#C8875A", .55)}" opacity=".8"/></g></g>')
    else:
        o += part(ell(px, py, prx, pry), pc, s=None, ol=False)
    o += f'<circle cx="{n(px - prx * .32)}" cy="{n(py - pry * .36)}" r="{n(prx * .42)}" fill="#FFFFFF"/>'
    o += f'<circle cx="{n(px + prx * .38)}" cy="{n(py + pry * .3)}" r="{n(prx * .17)}" fill="#FFFFFF"/>'
    return o


def blush(cx, cy, rx=9, ry=5.5, col="#FF8E9A", op=.5):
    if STYLE == "B":
        return paper(ell(cx, cy, rx, ry), col, op=.85, grain=False, sh=.5)
    return f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}" fill="{col}" opacity="{op}"/>'


# ================================================================ 阿布 (styles A and B: the same shapes)
def magnifier(cx, cy, r, ang=135, hl_len=1.25):
    """A magnifying glass: lens centre (cx, cy), handle pointing at angle `ang` (degrees, screen)."""
    a = math.radians(ang)
    hx0, hy0 = cx + math.cos(a) * r * 1.02, cy + math.sin(a) * r * 1.02
    hx1, hy1 = cx + math.cos(a) * r * (1 + hl_len), cy + math.sin(a) * r * (1 + hl_len)
    o = part(tube([(hx0, hy0, r * .2), (hx1, hy1, r * .24)], 2), HANDLE, s=(-2, -2.5))
    o += part(ell(cx, cy, r * 1.16), GOLD, s=(-2.5, -3))
    o += part(ell(cx, cy, r * .86), LENS, s=None, ol="#B88A1E")
    if STYLE == "A":
        o += f'<g clip-path="{clip(ell(cx, cy, r * .86))}"><circle cx="{n(cx + r * .5)}" cy="{n(cy + r * .55)}" r="{n(r * .75)}" fill="#BCE6FA"/></g>'
        o += hi(f"M{n(cx - r * .55)},{n(cy - r * .1)} A{n(r * .58)},{n(r * .58)} 0 0 1 {n(cx - r * .1)},{n(cy - r * .55)}", r * .16, .95)
    else:
        o += paper(ell(cx - r * .3, cy - r * .3, r * .22, r * .16), "#FFFFFF", grain=False, sh=0)
    return o


def glass_to(lens, paw, r):
    """A magnifying glass whose handle ends in the paw."""
    dx, dy = paw[0] - lens[0], paw[1] - lens[1]
    dist = math.hypot(dx, dy)
    return magnifier(lens[0], lens[1], r, math.degrees(math.atan2(dy, dx)), dist / r - 1 + .1)


def fox_arm(pts, paw):
    return part(tube(pts), FOX, s=(-3, -3.5)) + part(ell(paw[0], paw[1], paw[2]), FOXD, s=(-2.5, -3))


def twinkle(cx, cy, r):
    return part(sparkle_d(cx, cy, r), "#F7A400" if STYLE == "B" else GOLD, s=None, cls=.8)


HEAD = sym((0, -104), [((34, -104), (62, -92), (70, -66)), ((75, -50), (77, -36), (80, -26)),
                       ((86, -20), (94, -14), (102, -10)), ((94, -4), (86, -2), (80, -1)),
                       ((84, 4), (88, 8), (92, 12)), ((78, 17), (66, 20), (56, 22)), ((40, 31), (20, 35), (0, 35))])
FACE = ("M-130,70 L-130,-20 C-100,-24 -72,-12 -50,-8 C-32,-5 -18,-18 -11,-29 C-6,-36 6,-36 11,-29 "
        "C18,-18 32,-5 50,-8 C72,-12 100,-24 130,-20 L130,70 Z")


def fox_head(pose="wave", look=(2.0, 2.5)):
    """The head (ears, cap, face) in fox units: head centre about (0, -40), chin at y 35."""
    o = []
    ear = "M26,-92 C38,-124 62,-152 84,-158 C90,-130 88,-100 74,-70 Z"
    ear_in = "M40,-96 C48,-116 62,-134 76,-142 C80,-122 78,-102 70,-84 Z"
    ear_tip = "M30,-200 L130,-200 L130,-126 C112,-130 92,-128 40,-118Z"
    for sx in (1, -1):
        o.append(g(comp(ear, FOX, part(ear_tip, FOXD, s=None, ol=False) + part(ear_in, "#FFE2C8", s=None, ol="#E7A47A"), s=(-5, -6)),
                   f"scale({sx} 1)"))
    o.append(comp(HEAD, FOX, part(FACE, CREAM, s=(-4, -6), ol="#D9A47C"), s=(-9, -10),
                  hl=hi("M-46,-90 C-34,-98 -20,-101 -8,-101", 6, .5)))
    # the cap (a little tilted)
    dome = "M-58,-86 C-58,-128 -32,-148 0,-148 C32,-148 58,-128 58,-86 C30,-95 -30,-95 -58,-86 Z"
    checks = "".join(ln(dd, "#7E4A28", .62) for dd in ("M-30,-146 C-34,-120 -34,-100 -32,-88", "M0,-150 L0,-88",
                                                      "M30,-146 C34,-120 34,-100 32,-88", "M-60,-118 C-30,-126 30,-126 60,-118"))
    brim = "M-64,-88 C-34,-100 34,-100 64,-88 C66,-80 60,-75 52,-77 C26,-86 -26,-86 -52,-77 C-60,-75 -66,-80 -64,-88 Z"
    bow = ("M0,-147 C-6,-160 -22,-164 -22,-154 C-22,-146 -10,-144 0,-147 Z", "M0,-147 C6,-160 22,-164 22,-154 C22,-146 10,-144 0,-147 Z")
    o.append(g(comp(dome, CAP, checks, s=(-6, -7), hl=hi("M-40,-112 C-34,-128 -20,-138 -6,-140", 5, .45))
               + part(brim, CAP_D, s=(-3, -4)) + "".join(part(b, CAP_BOW, s=(-2, -3)) for b in bow)
               + part(ell(0, -148, 5), CAP_D, s=None), "rotate(-7 0 -100)"))
    # eyes and brows
    lx, ly = look
    for x in (-32, 32):
        if pose == "cheer":
            o.append(ln(f"M{x - 13},-42 Q{x},-62 {x + 13},-42", "#3A2418", 1.6))
        else:
            o.append(eye(x, -46, 16, 20, lx, ly, ol="#5A2E1A"))
    if pose == "think":
        o.append(ln("M-44,-80 Q-32,-92 -20,-82", "#7A3E1C", 1.35) + ln("M21,-76 Q32,-80 43,-74", "#7A3E1C", 1.35))
    elif pose == "cheer":
        o.append(ln("M-43,-76 Q-32,-86 -21,-77", "#7A3E1C", 1.35) + ln("M21,-77 Q32,-86 43,-76", "#7A3E1C", 1.35))
    else:
        o.append("".join(ln(f"M{x - 11},-74 Q{x},-81 {x + 11},-74", "#7A3E1C", 1.35) for x in (-32, 32)))
    if pose == "cheer":
        o.append(blush(-56, -18, 12, 7, op=.65) + blush(56, -18, 12, 7, op=.65))
    else:
        o.append(blush(-58, -16, 10, 6) + blush(58, -16, 10, 6))
    # mouth and nose
    if pose == "think":
        o.append(part(ell(4, 9, 5.5, 6.5), "#8A2F2F", s=None, ol="#5A2018"))
    else:
        mo = ("M-17,-2 Q0,4 17,-2 C16,15 8,24 0,24 C-8,24 -16,15 -17,-2Z" if pose == "cheer"
              else "M-13,-1 Q0,4 13,-1 C12,12 6,18 0,18 C-6,18 -12,12 -13,-1Z")
        ty = 23 if pose == "cheer" else 18
        o.append(comp(mo, "#8A2F2F", part(ell(0, ty, 10, 7.5), "#FF8A93", s=None, ol=False), s=None, ol="#5A2018"))
    o.append(part("M-9,-17 C-9,-23 9,-23 9,-17 C9,-11 3,-7 0,-7 C-3,-7 -9,-11 -9,-17Z", "#3B2418", s=None, ol="#2A160E",
                  hl=hidot(-3, -18, 2.4, .9)))
    return "".join(o)


def fox(pose="wave"):
    """阿布 in fox units (feet on y about 116, body centre x 0), style A or B."""
    o = []
    # tail (behind, to the right)
    tail = "M26,92 C60,106 108,98 122,66 C134,40 128,12 108,-4 C104,20 96,38 80,50 C64,60 44,62 28,60 Z"
    tip = "M70,-40 L150,-40 L150,36 C130,38 112,30 102,20 C94,12 88,0 84,-40Z"
    o.append(comp(tail, FOX, part(tip, CREAM, s=(-5, -6), ol="#C8936C"), s=(-8, -9)))
    if pose == "wave":     # the glass held down at the side, behind the body
        o.append(magnifier(-86, 50, 24, 50, 1.0))
        o.append(fox_arm([(-30, 40, 10.5), (-48, 58, 9.5), (-58, 74, 9.5)], (-60, 78, 11.5)))
    # body
    body = "M-38,20 C-52,44 -56,80 -44,98 C-30,112 30,112 44,98 C56,80 52,44 38,20 Z"
    belly = "M-22,40 C-31,56 -31,84 -18,96 C-6,102 6,102 18,96 C31,84 31,56 22,40 C10,33 -10,33 -22,40 Z"
    o.append(comp(body, FOX, part(belly, CREAM, s=(-5, -6), ol="#D9A47C"), s=(-9, -10)))
    for x in (-23, 23):
        o.append(part(ell(x, 105, 19, 11), FOXD, s=(-3, -3.5)))
    # head
    if pose == "think":
        o.append(g(fox_head(pose, (-4.5, -6)), "rotate(-5 0 30)"))
    else:
        o.append(fox_head(pose))
    # arms in front
    if pose == "wave":
        o.append(ln("M88,-48 Q98,-40 100,-28 M98,-58 Q112,-46 114,-30", "#E0773A", 1.35))
        o.append(fox_arm([(32, 40, 10.5), (54, 22, 9.5), (70, -6, 9.5)], (72, -12, 12)))
    elif pose == "think":
        o.append(fox_arm([(-30, 42, 10.5), (-60, 34, 9.5), (-78, 6, 9.5)], (-80, 0, 12)))
        o.append(glass_to((-110, -58), (-80, 0), 26))
        o.append(part(ell(-80, 0, 12), FOXD, s=(-2.5, -3)))
        o.append(fox_arm([(32, 42, 10.5), (58, 46, 9.5), (54, 30, 9.5), (24, 30, 9.5)], (20, 29, 12)))
    elif pose == "cheer":
        o.append(fox_arm([(-30, 42, 10.5), (-70, 32, 9.5), (-100, 4, 9.5), (-108, -24, 9.5)], (-108, -30, 12)))
        o.append(glass_to((-118, -88), (-108, -30), 24))
        o.append(part(ell(-108, -30, 12), FOXD, s=(-2.5, -3)))
        o.append(fox_arm([(30, 42, 10.5), (70, 32, 9.5), (100, 4, 9.5), (108, -24, 9.5)], (108, -30, 12.5)))
        o.append(twinkle(126, -74, 11) + twinkle(-74, -136, 8) + twinkle(96, -128, 7))
    return "".join(o)


# ================================================================ 阿布 in style C (blocks)
C_OR = FOX       # the same colours as styles A and B


def cap_(x0, y0, x1, y1, r, col):
    """A capsule (a rounded bar) from (x0, y0) to (x1, y1)."""
    return (f'<path d="M{n(x0)},{n(y0)} L{n(x1)},{n(y1)}" fill="none" stroke="{col}" stroke-width="{n(2 * r)}" '
            f'stroke-linecap="round"/>')


def cpath(d, col, rnd=0):
    """A flat shape; rnd: corners rounded by a stroke of the same colour."""
    if rnd:
        return f'<path d="{d}" fill="{col}" stroke="{col}" stroke-width="{n(rnd)}" stroke-linejoin="round"/>'
    return f'<path d="{d}" fill="{col}"/>'


def ccirc(cx, cy, r, col):
    return f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{col}"/>'


def c_glass(lens, paw, r):
    """The magnifying glass built from circles and a bar."""
    dx, dy = paw[0] - lens[0], paw[1] - lens[1]
    dist = math.hypot(dx, dy)
    ux, uy = dx / dist, dy / dist
    return (cap_(lens[0] + ux * r, lens[1] + uy * r, paw[0], paw[1], r * .22, HANDLE)
            + ccirc(lens[0], lens[1], r * 1.16, GOLD) + ccirc(lens[0], lens[1], r * .84, LENS)
            + f'<path d="M{n(lens[0] - r * .84)},{n(lens[1])} A{n(r * .84)},{n(r * .84)} 0 0 0 {n(lens[0] + r * .84)},{n(lens[1])}Z" '
              f'fill="#BCE6FA"/>'
            + ccirc(lens[0] - r * .32, lens[1] - r * .32, r * .2, "#FFFFFF"))


def c_star(cx, cy, r, col=GOLD):
    return cpath(star_d(r, r * .45, cx=cx, cy=cy), col, r * .25)


def c_fox(pose="wave"):
    """阿布 drawn again from circles, triangles and rounded bars: same colours, cap, glass and size."""
    o = []
    # tail: a lens of two circle arcs, cream tip
    o.append(cpath("M24,96 A70,70 0 0 1 112,-6 A70,70 0 0 1 24,96Z", C_OR))
    o.append(cpath("M88,20 A24,24 0 0 1 112,-6 A24,24 0 0 1 88,20Z", CREAM))
    if pose == "wave":
        o.append(c_glass((-88, 48), (-58, 72), 24))
        o.append(cap_(-30, 40, -56, 70, 10.5, C_OR) + ccirc(-58, 74, 12, FOXD))
    # body, belly, feet
    o.append(f'<rect x="-44" y="14" width="88" height="96" rx="34" fill="{C_OR}"/>')
    o.append(ccirc(0, 70, 28, CREAM))
    o.append(f'<rect x="-44" y="96" width="38" height="20" rx="10" fill="{FOXD}"/><rect x="6" y="96" width="38" height="20" rx="10" fill="{FOXD}"/>')
    # head
    h = []
    for sx in (-1, 1):
        h.append(cpath(f"M{sx * 22},-88 L{sx * 82},-156 L{sx * 78},-72Z", C_OR, 12))
        h.append(cpath(f"M{sx * 82},-156 L{sx * 72},-124 L{sx * 60},-133Z", FOXD, 10))
        h.append(cpath(f"M{sx * 42},-96 L{sx * 72},-130 L{sx * 70},-90Z", "#FFE2C8", 4))
        h.append(cpath(f"M{sx * 60},-36 L{sx * 102},-10 L{sx * 58},18Z", C_OR, 10))     # cheek tufts
    h.append(ccirc(0, -36, 70, C_OR))
    h.append(cpath("M-86,-8 A40,34 0 0 0 0,30 A40,34 0 0 0 86,-8 L58,-16 A34,30 0 0 1 0,-14 A34,30 0 0 1 -58,-16Z", CREAM))
    h.append(ccirc(-30, -6, 30, CREAM) + ccirc(30, -6, 30, CREAM))
    # cap: a half-disc dome, a bar for the brim, a bow of two triangles and a button
    cap = (f'<path d="M-58,-86 A58,56 0 0 1 58,-86Z" fill="{CAP}"/>'
           f'<path d="M-28,-138 L-30,-86 L-22,-86 L-20,-140Z" fill="#94592F"/><path d="M28,-138 L30,-86 L22,-86 L20,-140Z" fill="#94592F"/>'
           f'<rect x="-66" y="-94" width="132" height="14" rx="7" fill="{CAP_D}"/>'
           + cpath("M0,-144 L-20,-153 L-20,-137Z", CAP_BOW, 5) + cpath("M0,-144 L20,-153 L20,-137Z", CAP_BOW, 5)
           + ccirc(0, -144, 6, CAP_D))
    h.append(g(cap, "rotate(-7 0 -100)"))
    # face
    if pose == "think":
        look = (-5, -6)
    else:
        look = (2, 3)
    for x in (-32, 32):
        if pose == "cheer":
            h.append(cpath(f"M{x - 14},-44 A14,14 0 0 1 {x + 14},-44 L{x + 8},-44 A8,8 0 0 0 {x - 8},-44Z", "#3A2418", 3))
        else:
            h.append(ccirc(x, -46, 17, "#FFFFFF") + ccirc(x + look[0], -46 + look[1], 11.5, "#2E1C14")
                     + ccirc(x + look[0] - 4, -46 + look[1] - 4.5, 4.2, "#FFFFFF"))
    if pose == "think":
        h.append(cap_(-43, -80, -22, -86, 3.4, "#7A3E1C") + cap_(22, -77, 42, -75, 3.4, "#7A3E1C"))
    else:
        h.append(cap_(-42, -77, -22, -79, 3.4, "#7A3E1C") + cap_(22, -79, 42, -77, 3.4, "#7A3E1C"))
    br = 8 if pose == "cheer" else 7
    h.append(f'<circle cx="-56" cy="-16" r="{br}" fill="#FF8E9A" opacity=".75"/><circle cx="56" cy="-16" r="{br}" fill="#FF8E9A" opacity=".75"/>')
    if pose == "think":
        h.append(ccirc(4, 9, 6, "#8A2F2F"))
    else:
        mr = 16 if pose == "cheer" else 12
        h.append(f'<path d="M{-mr},-1 A{mr},{mr} 0 0 0 {mr},-1Z" fill="#8A2F2F"/>'
                 f'<path d="M{-mr * .62:.1f},{mr * .62:.1f} A{mr * .7:.1f},{mr * .5:.1f} 0 0 1 {mr * .62:.1f},{mr * .62:.1f} '
                 f'A{mr},{mr} 0 0 1 {-mr * .62:.1f},{mr * .62:.1f}Z" fill="#FF8A93"/>')
    h.append(cpath("M-10,-20 L10,-20 L0,-8Z", "#3B2418", 7))
    head = "".join(h)
    o.append(g(head, "rotate(-5 0 30)") if pose == "think" else head)
    # arms in front
    if pose == "wave":
        o.append(cap_(90, -50, 98, -32, 3, "#E0773A") + cap_(104, -58, 114, -36, 3, "#E0773A"))
        o.append(cap_(32, 38, 68, -6, 10.5, C_OR) + ccirc(72, -12, 13, FOXD))
    elif pose == "think":
        o.append(cap_(-32, 40, -64, 30, 10.5, C_OR) + cap_(-64, 30, -80, 2, 10, C_OR))
        o.append(c_glass((-110, -58), (-80, 0), 26) + ccirc(-80, 0, 13, FOXD))
        o.append(cap_(32, 40, 58, 44, 10.5, C_OR) + cap_(58, 44, 24, 30, 10, C_OR) + ccirc(20, 29, 13, FOXD))
    elif pose == "cheer":
        o.append(cap_(-32, 40, -72, 30, 10.5, C_OR) + cap_(-72, 30, -106, -26, 10, C_OR))
        o.append(c_glass((-118, -88), (-108, -30), 24) + ccirc(-108, -30, 13, FOXD))
        o.append(cap_(32, 40, 72, 30, 10.5, C_OR) + cap_(72, 30, 106, -26, 10, C_OR) + ccirc(108, -30, 13.5, FOXD))
        o.append(c_star(126, -74, 12) + c_star(-74, -136, 9) + c_star(96, -128, 8))
    return "".join(o)


# ================================================================ writing 阿布
FOX_S = 0.6                    # every 阿布 at the same size and on the same spot
FOX_T = (104.8, 114.6)         # where fox (0, 0) goes in the 200 x 200 box
LANDS = {"city": "A", "forest": "B", "blocks": "C"}
POSES = ("wave", "think", "cheer")


def svg_doc(body, w, h, mapper=None):
    defs = D.svg(mapper)
    text = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}">{defs}{body}</svg>\n')
    return short_ids(text)


def short_ids(text):
    """The ids are hashes while drawing (so equal shapes share one); here they get short names."""
    ids = re.findall(r' id="([^"]+)"', text)
    abc = "abcdefghijklmnopqrstuvwxyz"
    name = {}
    for i, k in enumerate(ids):
        t, j = "", i
        while True:
            t = abc[j % 26] + t
            j = j // 26 - 1
            if j < 0:
                break
        name[k] = t
    return re.sub(r'(id="|#)([A-Za-z0-9_]+)(?=["\)])', lambda m: m.group(1) + name.get(m.group(2), m.group(2)), text)


def abu_svg(land, pose):
    global D, STYLE, SC, SW, GRAIN
    D, GRAIN = Defs(), None
    st = LANDS[land]
    SC, SW = FOX_S, 2.3 / FOX_S
    tx, ty = FOX_T
    if st == "C":
        shadow = f'<ellipse cx="{n(tx - 2)}" cy="{n(ty + 117 * FOX_S)}" rx="44" ry="5" fill="#5A4A70" opacity=".14"/>'
        body = c_fox(pose)
    elif st == "B":
        STYLE = "B"
        make_grain()
        f = rg([(0, PSH, .22), (.6, PSH, .1), (1, PSH, 0)])
        shadow = f'<ellipse cx="{n(tx - 2)}" cy="{n(ty + 116 * FOX_S)}" rx="50" ry="7" fill="{f}"/>'
        body = fox(pose)
    else:
        STYLE = "A"
        shadow = f'<ellipse cx="{n(tx - 2)}" cy="{n(ty + 116 * FOX_S)}" rx="46" ry="5.5" fill="#5A4A70" opacity=".14"/>'
        body = fox(pose)
    out = svg_doc(shadow + f'<g transform="translate({n(tx)} {n(ty)}) scale({FOX_S})">{body}</g>', 200, 200)
    STYLE, SC, SW, GRAIN = "A", 1.0, 2.2, None
    return out


# ================================================================ THE PARK MAP
BOX = {}


def reg(box):
    def deco(f):
        BOX[f.__name__] = box
        return f
    return deco


def place(name, cx, cy, w, h, sw=1.8, style="A", flip=False, **kw):
    """Draw `name` scaled to fit a w x h box centred on (cx, cy); outlines `sw` map units wide."""
    global SC, SW, STYLE, ONE_SHADOW
    x0, y0, x1, y1 = BOX[name]
    s = min(w / (x1 - x0), h / (y1 - y0))
    SC, SW, STYLE, ONE_SHADOW = s, sw / s, style, True
    svg = globals()[name](**kw)
    SC, SW, STYLE, ONE_SHADOW = 1.0, 2.2, "A", False
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    fx = -1 if flip else 1
    return f'<g transform="translate({n(cx)} {n(cy)}) scale({fx * s:.4f} {s:.4f}) translate({n(-mx)} {n(-my)})">{svg}</g>'


def window(d, wall, cx, cy, r):
    """A window: pale blue by day, warm light at night."""
    if not NIGHT:
        return part(d, "#CDEEFF", s=None, ol=lin(wall))
    k = shape(d)
    return glow(cx, cy, r * 2.6, "#FFC85A", .5) + lit(use(k, 'fill="#FFE08A"')) + use(k, f'fill="none" stroke="{lin(wall)}"', f' stroke-width="{n(SW)}"')


# ---------------------------------------------------------------- 卡通城 (style A)
@reg((-46, -62, 46, 46))
def house(col="#FF8A8A", roof="#4F7FE8"):
    o = part(rr(-36, -16, 72, 60, 6), col, s=(-6, -7))
    o += part("M-46,-12 L0,-58 L46,-12 C48,-10 46,-6 42,-6 L-42,-6 C-46,-6 -48,-10 -46,-12Z", roof, s=(-5, -6))
    o += part(rr(-10, 12, 20, 32, 9), "#8C5A3C", s=None) + part(ell(5, 30, 2.2), GOLD, s=None, ol=False)
    o += window(rr(-30, 0, 16, 16, 4), col, -22, 8, 8) + window(rr(14, 0, 16, 16, 4), col, 22, 8, 8)
    o += part(rr(18, -50, 12, 22, 2), "#C9746A", s=(-2, -2)) if col == "#FF8A8A" else ""
    return o


@reg((-74, -96, 74, 52))
def firestation():
    red = "#F04A3E"
    o = part(rr(30, -84, 30, 56, 5), red, s=(-3, -4)) + part("M24,-80 L45,-96 L66,-80Z", "#9B2E2A", s=None)
    if NIGHT:
        o += glow(45, -64, 18, "#FFC85A", .5)
        o += lit(f'<circle cx="45" cy="-64" r="8" fill="#FFE08A"/>') + f'<circle cx="45" cy="-64" r="8" fill="none" stroke="{lin(GOLD)}" stroke-width="{n(SW)}"/>'
    else:
        o += part(ell(45, -64, 8), GOLD, s=None)
    o += part(rr(-66, -40, 132, 90, 8), red, s=(-9, -10), hl=hi("M-56,-30 L40,-30", 4, .45))
    o += part("M-72,-38 L72,-38 L66,-58 L-66,-58 Z", "#9B2E2A", s=(-3, -4))
    o += part(rr(-54, -8, 66, 58, 6), "#FFFFFF", s=None, ol=lin(red))
    o += "".join(ln(f"M-54,{y} L12,{y}", "#C9C2DD", .62) for y in (4, 16, 28, 40))
    o += window(rr(26, -8, 26, 22, 4), red, 39, 3, 12)
    o += part(rr(-30, -30, 60, 16, 5), "#FFFFFF", s=None, ol=lin(red))
    o += part(star_d(6, 2.8, cx=0, cy=-22, round_=.15), GOLD, s=None, ol=False)
    return o


@reg((-30, -26, 30, 16))
def bush(col="#6CCB5F"):
    o = part(ell(-12, -2, 17), col, s=(-3, -4))
    o += part(ell(12, 0, 14), col, s=(-3, -4))
    o += part(ell(0, -10, 14), lt(col, .1), s=(-3, -4))
    return o


@reg((-8, -40, 8, 40))
def flower(col="#FF7FA3"):
    o = ln("M0,30 L0,-2", "#4FA84A", 1.2)
    o += part("".join(ell(math.cos(a) * 7, -8 + math.sin(a) * 7, 5) for a in (0, 1.26, 2.51, 3.77, 5.03)), col, s=None, cls=.7)
    return o + part(ell(0, -8, 4), GOLD, s=None, cls=.7)


@reg((-14, -60, 14, 60))
def lamp():
    """A street lamp by the path (lit at night)."""
    o = part(rr(-3, -36, 6, 92, 3), "#5E6A8A", s=None, cls=.8)
    o += part(rr(-9, 52, 18, 8, 3), "#5E6A8A", s=None, cls=.8)
    if NIGHT:
        o += glow(0, -44, 30, "#FFD27A", .5)
        o += lit('<path d="M-11,-36 L-8,-52 L8,-52 L11,-36Z" fill="#FFE9A6"/>')
    else:
        o += part("M-11,-36 L-8,-52 L8,-52 L11,-36Z", "#FFF4CC", s=None, ol="#5E6A8A", cls=.8)
    o += part(rr(-12, -58, 24, 7, 3), "#5E6A8A", s=None, cls=.8)
    return o


# ---------------------------------------------------------------- 紙片森林 (style B)
@reg((-50, -100, 50, 62))
def ptree(col="#5DBB63", kind="round", lantern=0):
    """A paper tree; lantern=-1 or 1: a paper lantern hangs from its left or right side."""
    o = part(rr(-8, 10, 16, 52, 6), "#9A6A3E", s=(-2, -3))
    if kind == "round":
        for (cx, cy, r, c) in ((-20, -16, 28, col), (20, -18, 28, col), (0, -44, 34, lt(col, .12)), (0, -6, 30, shd(col))):
            o += part(ell(cx, cy, r), c, s=(-4, -5))
        hang = 16
    else:
        for i, (y, w) in enumerate(((-6, 46), (-40, 38), (-70, 28))):
            o += part(f"M{-w},{y + 18} L0,{y - 30} L{w},{y + 18} Z", tone(col, 1 - i * .06), s=(-4, -5))
        hang = 6
    if lantern:
        o += hanging_lantern(lantern * 30, hang, 1.25)
    return o


def hanging_lantern(x, y, s=1.0):
    """A little paper lantern on a string from (x, y): pale by day, glowing at night."""
    cy = y + 22 * s
    body = f"M{n(x - 10 * s)},{n(cy)} C{n(x - 10 * s)},{n(cy - 11 * s)} {n(x + 10 * s)},{n(cy - 11 * s)} {n(x + 10 * s)},{n(cy)} " \
           f"C{n(x + 10 * s)},{n(cy + 11 * s)} {n(x - 10 * s)},{n(cy + 11 * s)} {n(x - 10 * s)},{n(cy)}Z"
    o = ln(f"M{n(x)},{n(y)} L{n(x)},{n(cy - 8 * s)}", "#6A4A2A", 1)
    if NIGHT:
        o += glow(x, cy, 30 * s, "#FFB347", .6)
        o += lit(f'<path d="{body}" fill="#FFC56B"/><circle cx="{n(x)}" cy="{n(cy)}" r="{n(5 * s)}" fill="#FFF0B8"/>')
    else:
        o += part(body, "#FF9F6E")
    o += part(rr(x - 5.5 * s, cy - 11 * s, 11 * s, 4 * s, 1.5 * s), "#B5543A") + part(rr(x - 5.5 * s, cy + 7 * s, 11 * s, 4 * s, 1.5 * s), "#B5543A")
    return o


@reg((-38, -40, 38, 40))
def mushroom():
    o = part(rr(-13, -6, 26, 44, 11), "#FFF3E0", s=(-3, -4), ol="#C9A77A")
    cap = "M-36,2 C-38,-26 -18,-40 0,-40 C18,-40 38,-26 36,2 C20,8 -20,8 -36,2 Z"
    o += comp(cap, "#F0473F", "".join(part(ell(x, y, r), "#FFFFFF", s=None, ol=False) for x, y, r in ((-18, -14, 6), (6, -26, 5.5), (18, -8, 6), (-2, -6, 4))),
              s=(-5, -6))
    return o


@reg((-90, -40, 90, 40))
def pond():
    o = part("M-84,0 C-84,-26 -40,-36 0,-34 C44,-34 86,-24 86,2 C86,26 44,36 0,36 C-42,36 -84,26 -84,0Z", "#7CC7F0", s=(-6, -7))
    o += part("M-60,-4 C-58,-18 -26,-22 0,-20 C30,-20 56,-14 58,0 C40,4 -40,6 -60,-4Z", "#A8DDF8", s=None, ol=False)
    o += part("M30,10 A16,9 0 1 1 46,4 L34,6 Z", "#4FB45A", s=None)
    o += part(ell(-34, 14, 12, 6), "#4FB45A", s=None) + part(ell(-34, 10, 5), "#FF8FB1", s=None)
    return o


@reg((-30, -14, 30, 14))
def pgrass(col="#86B86C"):
    """A tuft of paper grass."""
    return part("M-28,12 L-18,-6 L-12,8 L-4,-12 L4,8 L12,-8 L18,8 L28,-2 L26,12Z", col)


# ---------------------------------------------------------------- 積木王國 (style C: flat, no outlines)
def c_castle():
    o = [f'<rect x="-70" y="-40" width="140" height="90" fill="#FF8FAB"/>']
    for x in (-70, -42, -14, 14, 42):
        o.append(f'<rect x="{x}" y="-52" width="18" height="14" fill="#FF8FAB"/>')
    for x, c in ((-86, CP), (62, CP)):
        o.append(f'<rect x="{x}" y="-70" width="24" height="120" fill="{c}"/><path d="M{x - 6},-70 L{x + 12},-104 L{x + 30},-70Z" fill="{CB}"/>')
        o.append(_cwin(f'<rect x="{x + 6}" y="-50" width="12" height="16" rx="6" fill="#FFFFFF"/>',
                       f'<rect x="{x + 6}" y="-50" width="12" height="16" rx="6" fill="#FFE08A"/>', x + 12, -42, 10))
    o.append(f'<rect x="-22" y="-96" width="44" height="60" fill="{CY}"/><path d="M-30,-96 L0,-136 L30,-96Z" fill="{CR}"/>'
             f'<rect x="-1" y="-160" width="3" height="26" fill="{C_DK}"/><path d="M2,-160 L22,-153 L2,-146Z" fill="{CT}"/>')
    o.append(_cwin('<path d="M-20,50 L-20,16 A20,20 0 0 1 20,16 L20,50Z" fill="#2B2D42"/>',
                   '<path d="M-20,50 L-20,16 A20,20 0 0 1 20,16 L20,50Z" fill="#FFC85A"/>'
                   '<path d="M-13,50 L-13,18 A13,13 0 0 1 13,18 L13,50Z" fill="#FFE7A0"/>', 0, 30, 26))
    o.append(_cwin('<circle cx="0" cy="-66" r="9" fill="#FFFFFF"/>', '<circle cx="0" cy="-66" r="9" fill="#FFE08A"/>', 0, -66, 11))
    for x in (-46, 30):
        o.append(_cwin(f'<rect x="{x}" y="-24" width="16" height="20" rx="8" fill="#FFFFFF" opacity=".55"/>',
                       f'<rect x="{x}" y="-24" width="16" height="20" rx="8" fill="#FFD36E"/>', x + 8, -14, 12))
    return "".join(o)


def _cwin(day, night_, cx, cy, r):
    if not NIGHT:
        return day
    return glow(cx, cy, r * 2.4, "#FFC85A", .55) + lit(night_)


def c_tower(cols=(CB, CY, CR, CG)):
    o = []
    y = 40
    for i, c in enumerate(cols):
        w = 44 - i * 4
        o.append(f'<rect x="{-w / 2}" y="{y - 26}" width="{w}" height="26" rx="3" fill="{c}"/>')
        y -= 27
    o.append(f'<path d="M-20,{y + 1} L0,{y - 26} L20,{y + 1}Z" fill="{CP}"/>')
    o.append(_cwin(f'<circle cx="0" cy="{y - 8}" r="4" fill="#FFFFFF" opacity=".6"/>', f'<circle cx="0" cy="{y - 8}" r="5" fill="#FFE08A"/>', 0, y - 8, 7))
    return "".join(o)


def c_engine():
    o = (f'<path d="M-86,30 L-70,6 L-58,6 L-58,30Z" fill="{CY}"/>'
         f'<rect x="-74" y="4" width="160" height="14" rx="4" fill="{C_DK}"/>'
         f'<rect x="-66" y="-40" width="86" height="46" fill="{CR}"/><circle cx="-66" cy="-17" r="23" fill="{CR}"/>')
    o += _cwin(f'<circle cx="-72" cy="-17" r="7" fill="{CY}"/>', '<circle cx="-72" cy="-17" r="8" fill="#FFF2B0"/>', -80, -17, 16)
    o += (f'<rect x="-56" y="-70" width="22" height="30" fill="{C_DK}"/><rect x="-62" y="-80" width="34" height="12" rx="3" fill="{C_DK}"/>'
          f'<circle cx="-4" cy="-40" r="11" fill="{CY}"/>'
          f'<rect x="18" y="-74" width="64" height="80" rx="6" fill="{CB}"/><rect x="12" y="-86" width="76" height="16" rx="5" fill="#2557C9"/>')
    o += _cwin('<rect x="34" y="-60" width="32" height="26" rx="5" fill="#FFFFFF"/>', '<rect x="34" y="-60" width="32" height="26" rx="5" fill="#FFE08A"/>', 50, -47, 18)
    o += "".join(f'<circle cx="{x}" cy="24" r="{r}" fill="{C_DK}"/><circle cx="{x}" cy="24" r="{r * .42:.1f}" fill="{CY}"/>'
                 for x, r in ((-46, 15), (-12, 15), (50, 21)))
    return o


def c_wagon(col=CY, load="circle"):
    o = (f'<rect x="-40" y="-2" width="10" height="6" fill="{C_DK}"/><rect x="-32" y="-12" width="64" height="24" rx="4" fill="{col}"/>'
         f'<circle cx="-17" cy="16" r="10" fill="{C_DK}"/><circle cx="17" cy="16" r="10" fill="{C_DK}"/>'
         f'<circle cx="-17" cy="16" r="4" fill="#FFFFFF"/><circle cx="17" cy="16" r="4" fill="#FFFFFF"/>')
    if load == "circle":
        o += f'<circle cx="0" cy="-28" r="16" fill="{CR}"/><circle cx="-5" cy="-33" r="4" fill="#FFFFFF" opacity=".55"/>'
    elif load == "square":
        o += f'<rect x="-15" y="-43" width="30" height="30" rx="3" fill="{CB}"/><rect x="-10" y="-38" width="7" height="7" rx="2" fill="#FFFFFF" opacity=".5"/>'
    else:
        o += f'<path d="M0,-46 L17,-14 L-17,-14Z" fill="{CG}" stroke="{CG}" stroke-width="4" stroke-linejoin="round"/>'
    return o


C_BOX = {"castle": (c_castle, (-92, -162, 92, 52)), "tower": (c_tower, (-24, -96, 24, 42)),
         "engine": (c_engine, (-88, -88, 90, 46)), "wagon": (c_wagon, (-42, -48, 34, 28))}


def place_c(name, cx, cy, w, h, **kw):
    f, (x0, y0, x1, y1) = C_BOX[name]
    s = min(w / (x1 - x0), h / (y1 - y0))
    return f'<g transform="translate({n(cx)} {n(cy)}) scale({s:.4f}) translate({n(-(x0 + x1) / 2)} {n(-(y0 + y1) / 2)})">{f(**kw)}</g>'


# ---------------------------------------------------------------- the free spots the app fills
# centre (x, y) and size (w, h) in map pixels (390 x 844); park_spots.json has them as fractions
SPOTS = {
    "title": (195, 87, 222, 58),
    "odd": (106, 258, 117, 59),
    "next": (292, 368, 117, 59),
    "blocks": (113, 384, 101, 42),
    "detective": (316, 484, 117, 59),
    "pairs": (76, 528, 117, 59),
    "forest": (150, 590, 101, 42),
    "sort": (72, 744, 117, 59),
    "owner": (318, 790, 117, 59),
    "city": (205, 720, 101, 42),
    "abu": (205, 792, 94, 101),
}
BUTTONS = {"book": (78, 816, 132, 40), "parents": (337, 28, 74, 32)}

MAP_PATH = [(205, 880), (205, 800), (204, 756), (184, 714), (150, 686), (138, 652), (148, 614), (176, 590),
            (228, 572), (254, 546), (236, 516), (190, 498), (146, 482), (120, 456), (112, 420), (118, 384),
            (140, 350), (190, 330), (246, 318), (292, 304), (316, 296)]
BLOCKS_TOP = 204      # the row of coloured bricks between the sky and 積木王國
FOREST_TOP = 448      # the torn paper edge between 積木王國 and 紙片森林
FOREST_BOTTOM = 648   # the paper grass edge between 紙片森林 and 卡通城


def map_svg(night_=False):
    global D, NIGHT, SC, STYLE, GRAIN
    D, NIGHT, GRAIN = Defs(), night_, None
    o = []
    # ---- the sky
    if night_:
        sky = lg([(0, "#0D1433"), (.3, "#1A2656"), (1, "#2B3B78")])
        o.append(LIT0 + f'<rect width="{W}" height="{H}" fill="{sky}"/>' + night_sky() + LIT1)
    else:
        o.append(f'<rect width="{W}" height="{H}" fill="{lg([(0, "#BFE4FF"), (.25, "#E2F3FF"), (1, "#EEF8FF")])}"/>')
        o.append("".join(f'<path d="{cloud_d(x, y, s)}" fill="#FFFFFF" opacity=".9"/>' for x, y, s in ((40, 172, .42), (210, 160, .3))))
    # ---- the title: an empty rainbow arch with a blank plank (the app writes the name on it)
    for i, c in enumerate(("#FF7A6E", "#FFD166", "#7CC7FF")):
        o.append(f'<path d="M{70 + i * 9},126 A{125 - i * 9},{98 - i * 8} 0 0 1 {320 - i * 9},126" fill="none" stroke="{c}" stroke-width="9"/>')
    o.append(f'<path d="{cloud_d(72, 124, .5)}" fill="#FFFFFF" stroke="#C9DDF0" stroke-width="2"/>'
             f'<path d="{cloud_d(318, 124, .5)}" fill="#FFFFFF" stroke="#C9DDF0" stroke-width="2"/>')
    o.append(f'<path d="{rr(84, 63, 222, 58, 22)}" fill="#FFD2A6" stroke="{lin(FOX)}" stroke-width="2.4"/>'
             f'<path d="{rr(84, 58, 222, 58, 22)}" fill="#FFFFFF" stroke="{lin(FOX)}" stroke-width="2.4"/>')
    # ---- 積木王國 ground: a floor of block tiles, a row of bricks along its top edge
    o.append(f'<rect x="0" y="{BLOCKS_TOP}" width="{W}" height="{FOREST_TOP + 20 - BLOCKS_TOP}" fill="#E4E1FA"/>')
    tiles = []
    for j, y in enumerate(range(BLOCKS_TOP + 12, FOREST_TOP + 10, 28)):
        for x in range(4 + (28 if j % 2 else 0), W, 56):
            tiles.append(f"M{x},{y}h24v24h-24Z")
    o.append(f'<path d="{"".join(tiles)}" fill="#D7D2F5"/>')
    cols = [CB, CY, CR, CG]
    o.append("".join(f'<rect x="{x}" y="{BLOCKS_TOP - 6}" width="20" height="11" rx="2" fill="{cols[(x // 22) % 4]}"/>' for x in range(0, W, 22)))
    # ---- 卡通城 ground: cartoon grass
    o.append(f'<rect x="0" y="{FOREST_BOTTOM - 20}" width="{W}" height="{H - FOREST_BOTTOM + 20}" fill="{lg([(0, "#A3DE88"), (1, "#B2E79A")])}"/>')
    tufts = "".join(f"M{x - 8},{y} Q{x - 6},{y - 9} {x - 2},{y - 2} Q{x},{y - 12} {x + 3},{y - 2} Q{x + 7},{y - 9} {x + 9},{y}"
                    for x, y in ((24, 808), (260, 838), (134, 790), (178, 690), (370, 830), (250, 768), (36, 700)))
    o.append(f'<path d="{tufts}" fill="none" stroke="#6DBE57" stroke-width="2" stroke-linecap="round"/>')
    # ---- 紙片森林 ground: paper, torn along the top, grass blades along the bottom
    SC = 1.0
    o.append(forest_ground())
    # ---- the path (one for the whole park)
    k = shape(rpoly(spline(MAP_PATH, 7), False))
    o.append(use(k, 'fill="none" stroke="#D9B87C"', ' stroke-width="40" stroke-linecap="round" stroke-linejoin="round"')
             + use(k, 'fill="none" stroke="#FAE8C2"', ' stroke-width="32" stroke-linecap="round" stroke-linejoin="round"')
             + use(k, 'fill="none" stroke="#EFD49E"', ' stroke-width="5" stroke-linecap="round" stroke-dasharray="1 15"'))
    # ---- 積木王國 (style C)
    o.append(place_c("castle", 318, 214, 134, 160))
    o.append(place_c("tower", 26, 298, 40, 110, cols=(CR, CB, CY, CG)))
    o.append(place_c("tower", 372, 352, 26, 70, cols=(CG, CY, CB, CR)))
    o.append(f'<rect x="196" y="438" width="{W - 196}" height="5" fill="{C_DK}"/>'
             + f'<path d="{"".join(f"M{x},440h8v6h-8Z" for x in range(200, W, 16))}" fill="#C99A6B"/>')
    o.append(place_c("wagon", 222, 424, 42, 33, col=CB, load="triangle"))
    o.append(place_c("engine", 274, 418, 66, 42))
    o.append(place_c("wagon", 330, 424, 42, 33, col=CY, load="circle") + place_c("wagon", 374, 424, 42, 33, col=CG, load="square"))
    o.append(f'<rect x="196" y="236" width="20" height="20" rx="3" fill="{CY}" transform="rotate(12 206 246)"/>'
             f'<path d="M222,258 L233,238 L244,258Z" fill="{CG}" stroke="{CG}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
             f'<circle cx="22" cy="414" r="9" fill="{CB}"/><rect x="34" y="420" width="14" height="14" rx="2" fill="{CR}" transform="rotate(-8 41 427)"/>'
             f'<circle cx="196" cy="390" r="7" fill="{CP}"/>')
    o.append(gate_c(SPOTS["blocks"][0], SPOTS["blocks"][1] + 16, FOREST_TOP - 2))
    # ---- 紙片森林 (style B)
    make_grain_map()
    o.append(place("pond", 52, 612, 96, 46, style="B"))
    for x, y, sz, kd, c, lan in ((22, 474, 42, "pine", "#5FA35A", 1), (368, 550, 54, "pine", "#6BAF62", -1),
                                 (226, 470, 40, "round", "#7DBB6A", 0), (252, 624, 36, "round", "#76B565", 1),
                                 (306, 610, 30, "pine", "#5FA35A", 0), (388, 600, 40, "round", "#7DBB6A", 0)):
        o.append(place("ptree", x, y, sz, sz * 1.62, style="B", kind=kd, col=c, lantern=lan))
    o.append(place("mushroom", 344, 622, 26, 26, style="B"))
    o.append(place("mushroom", 196, 534, 22, 22, style="B"))
    for x, y in ((150, 568), (330, 534), (12, 568)):
        o.append(place("pgrass", x, y, 26, 12, style="B"))
    o.append(gate_b(SPOTS["forest"][0], SPOTS["forest"][1] + 16, FOREST_BOTTOM + 4))
    if night_:
        o.append(fireflies())
    # ---- 卡通城 (style A)
    o.append(place("house", 36, 670, 60, 64))
    o.append(place("house", 94, 684, 48, 52, col="#FFD166", roof="#FF7A6E"))
    o.append(place("firestation", 322, 690, 134, 122))
    for x, y, s in ((256, 744, 26), (14, 762, 26), (140, 724, 22)):
        o.append(place("bush", x, y, s * 1.4, s))
    for x, y, c in ((138, 766, "#FF7FA3"), (150, 772, "#FFD43B"), (270, 832, "#9B8CFF"), (382, 834, "#FF7FA3")):
        o.append(place("flower", x, y, 8, 22, sw=1.2, col=c))
    o.append(gate_a(SPOTS["city"][0], SPOTS["city"][1] + 16, 804))
    body = "".join(o)
    SC, STYLE, GRAIN = 1.0, "A", None
    if night_:
        out = svg_doc(night_map(body), W, H, mapper=night_map)
    else:
        out = svg_doc(body, W, H)
    NIGHT = False
    return out.replace(LIT0, "").replace(LIT1, "")


def night_map(s):
    """Night colours for everything outside the lights."""
    parts = re.split(f"({re.escape(LIT0)}.*?{re.escape(LIT1)})", s, flags=re.S)
    out = []
    for p in parts:
        if p.startswith(LIT0):
            out.append(p)
        else:
            out.append(re.sub(r"#[0-9A-Fa-f]{6}(?![0-9A-Za-z_])", lambda m: night(m.group(0)), p))
    return "".join(out)


def forest_ground():
    top = f"M-10,{FOREST_TOP + 2} " + " ".join(
        f"Q{x + 30},{FOREST_TOP - 8 + (8 if (x // 60) % 2 else 0)} {x + 60},{FOREST_TOP + 2}" for x in range(-10, 400, 60))
    blades = " ".join(f"L{x + 6},{FOREST_BOTTOM + 14 + (k % 3) * 4} L{x + 12},{FOREST_BOTTOM}" for k, x in enumerate(range(400, -20, -12)))
    global GRAIN, STYLE, GRAIN_T
    STYLE, GRAIN_T = "B", 64.0
    ground = top + f" L400,{FOREST_BOTTOM} {blades} Z"
    o = paper(ground, "#A2D184", grain=False, step=3.4)
    o += paper(f"M-10,{FOREST_TOP + 70} C60,{FOREST_TOP + 46} 130,{FOREST_TOP + 66} 176,{FOREST_TOP + 100} "
               f"C120,{FOREST_TOP + 122} 40,{FOREST_TOP + 120} -10,{FOREST_TOP + 116}Z", "#BBDB9F", grain=False, step=3.4)
    o += paper(f"M240,{FOREST_TOP + 22} C300,{FOREST_TOP + 6} 360,{FOREST_TOP + 12} 400,{FOREST_TOP + 28} "
               f"L400,{FOREST_TOP + 74} C340,{FOREST_TOP + 74} 280,{FOREST_TOP + 56} 240,{FOREST_TOP + 22}Z", "#97C47C", grain=False, step=3.4)
    o += paper(f"M200,{FOREST_BOTTOM - 40} C250,{FOREST_BOTTOM - 62} 330,{FOREST_BOTTOM - 60} 400,{FOREST_BOTTOM - 46} "
               f"L400,{FOREST_BOTTOM - 4} C320,{FOREST_BOTTOM - 10} 250,{FOREST_BOTTOM - 14} 200,{FOREST_BOTTOM - 40}Z", "#9CC985", grain=False, step=3.4)
    # the fibres, once over the whole floor (hills included)
    make_grain(gap=6.8, seed=3)
    k = shape(torn(ground, step=3.4))
    T = GRAIN_T
    tiles = "".join(f'<use href="#{GRAIN}" transform="translate({n(i * T)} {n(j * T)})"/>'
                    for j in range(math.floor((FOREST_TOP - 12) / T), math.ceil((FOREST_BOTTOM + 26) / T)) for i in range(0, math.ceil(W / T)))
    o += f'<g clip-path="{clip_of(k)}">{tiles}</g>'
    STYLE, GRAIN_T, GRAIN = "A", 40.0, None
    return o


def make_grain_map():
    """No fibres on the small paper things of the map (too small to see); only the ground has them."""
    global GRAIN
    GRAIN = None


def gate_a(cx, top, base):
    """卡通城's gate: two candy-striped posts."""
    o = ""
    for sx in (-1, 1):
        x = cx + sx * 40 - 7
        d = rr(x, top, 14, base - top, 5)
        k = shape(d)
        stripes = "".join(f'<path d="M{x - 2},{y + 8} L{x + 16},{y - 2}" stroke="#FFFFFF" stroke-width="4.5" fill="none"/>'
                          for y in range(int(top) + 4, int(base) + 8, 14))
        o += (use(k, 'fill="#FF8A8A"') + f'<g clip-path="{clip_of(k)}">{stripes}</g>'
              + use(k, f'fill="none" stroke="{lin("#FF8A8A")}"', ' stroke-width="2"')
              + f'<circle cx="{x + 7}" cy="{top - 1}" r="8" fill="{YELLOW}" stroke="{lin(YELLOW)}" stroke-width="2"/>')
    return o


def gate_b(cx, top, base):
    """紙片森林's gate: two paper posts with leafy tops."""
    global STYLE, SC
    STYLE, SC = "B", 1.0
    o = ""
    for sx in (-1, 1):
        x = cx + sx * 40
        o += paper(rr(x - 7, top + 6, 14, base - top - 6, 4), "#A07A52")
        o += paper(ell(x, top + 6, 20, 15), "#7DBB6A")
        o += paper(ell(x + sx * 8, top - 1, 11, 9), "#8FC77A")
    STYLE = "A"
    return o


def gate_c(cx, top, base):
    """積木王國's gate: two pillars of coloured blocks."""
    o = ""
    hgt = (base - top) / 4
    for sx in (-1, 1):
        x = cx + sx * 40 - 9
        for i, c in enumerate((CB, CY, CR, CG)):
            o += f'<rect x="{n(x)}" y="{n(base - (i + 1) * hgt)}" width="18" height="{n(hgt - 1.5)}" rx="2" fill="{c}"/>'
        o += f'<path d="M{n(x - 2)},{n(top)} L{n(x + 9)},{n(top - 14)} L{n(x + 20)},{n(top)}Z" fill="{CP}"/>'
    return o


YELLOW = "#FFD43B"


# ---------------------------------------------------------------- night extras (never darkened)
def night_sky():
    rnd = random.Random(42)
    o = []
    # the crescent moon
    o.append(glow(44, 168, 48, "#FFF1B8", .35).replace(LIT0, "").replace(LIT1, ""))
    o.append('<path d="M56,146 A26,26 0 1 0 64,188 A20,20 0 1 1 56,146Z" fill="#FFE9A8"/>')
    stars = []
    tries = 0
    while len(stars) < 40 and tries < 2000:
        tries += 1
        x, y = rnd.uniform(6, 384), rnd.uniform(6, 230)
        if 60 < x < 330 and 24 < y < 140:        # not behind the title
            continue
        if 290 < x and y < 56:                    # not under the parents' button
            continue
        if math.hypot(x - 46, y - 170) < 40:
            continue
        if any(math.hypot(x - a, y - b) < 18 for a, b, _ in stars):
            continue
        stars.append((x, y, rnd.random()))
    levels = {0: [], 1: [], 2: []}
    for x, y, r in stars:
        if r < .22:
            o.append(f'<path d="{sparkle_d(x, y, 5 + r * 8)}" fill="#FFF3C4"/>')
        else:
            levels[min(2, int((r - .22) / .26))].append(ell(x, y, .9 + r * 1.3))
    for lv, ds in levels.items():
        o.append(f'<path d="{"".join(ds)}" fill="#FFF8DC" opacity="{(.6, .78, .95)[lv]}"/>')
    return "".join(o)


def fireflies():
    rnd = random.Random(9)
    o = []
    for x, y in ((150, 470), (328, 452), (60, 640), (300, 560), (210, 606), (24, 600), (372, 600)):
        x, y = x + rnd.uniform(-6, 6), y + rnd.uniform(-6, 6)
        o.append(glow(x, y, 7, "#E9FF8A", .6) + lit(f'<circle cx="{n(x)}" cy="{n(y)}" r="1.6" fill="#F6FFC8"/>'))
    return "".join(o)


# ================================================================ checks, files, preview
BAD = re.compile(r"<(filter|mask|style|text|image|foreignObject|pattern)\b|style=|class=")


def check(name, text):
    import xml.dom.minidom
    xml.dom.minidom.parseString(text)
    assert text.rstrip().endswith("</svg>"), name
    m = BAD.search(text)
    if m:
        raise SystemExit(f"{name}: uses {m.group(0)} (flutter_svg cannot draw it)")
    uses = text.count("<use ")
    kb = len(text.encode()) / 1024
    if uses > 800 or kb > 64:
        print(f"warning: {name}: {uses} <use>, {kb:.1f} KB")
    return uses, kb


def write_all():
    OUT.mkdir(parents=True, exist_ok=True)
    files = {}
    for land in LANDS:
        for pose in POSES:
            files[f"abu_{land}_{pose}.svg"] = abu_svg(land, pose)
    files["map.svg"] = map_svg(False)
    files["map_night.svg"] = map_svg(True)
    for name, text in files.items():
        uses, kb = check(name, text)
        (OUT / name).write_text(text)
        print(f"{name:24s} {kb:5.1f} KB  {uses:3d} <use>")
    spots = {k: {"x": round(v[0] / W, 4), "y": round(v[1] / H, 4), "w": round(v[2] / W, 4), "h": round(v[3] / H, 4)}
             for k, v in SPOTS.items()}
    SPOTS_JSON.write_text(json.dumps(spots, ensure_ascii=False, indent=2) + "\n")
    print(SPOTS_JSON.relative_to(ROOT))


RENDER_JS = """
const { chromium } = require('playwright');
(async () => {
  const jobs = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  for (const j of jobs) {
    const page = await browser.newPage({ viewport: { width: j.w, height: j.h }, deviceScaleFactor: 1 });
    await page.goto('file://' + j.src);
    await page.screenshot({ path: j.out, omitBackground: true });
    await page.close();
  }
  await browser.close();
})();
"""


def render_many(jobs):
    """jobs: (svg text, width px, height px) -> PIL images (RGBA), drawn by Chromium."""
    from PIL import Image
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        spec = []
        for i, (text, w, h) in enumerate(jobs):
            src = tmp / f"{i}.svg"
            text = re.sub(r'width="[\d.]+" height="[\d.]+" viewBox', f'width="{w}" height="{h}" viewBox', text, count=1)
            src.write_text(text)
            spec.append({"src": str(src), "out": str(tmp / f"{i}.png"), "w": w, "h": h})
        (tmp / "jobs.json").write_text(json.dumps(spec))
        (tmp / "r.js").write_text(RENDER_JS)
        subprocess.run(["node", str(tmp / "r.js"), str(tmp / "jobs.json")], check=True)
        return [Image.open(s["out"]).convert("RGBA").copy() for s in spec]


def boxes_overlay(img, scale):
    from PIL import ImageDraw
    over = img.copy()
    dr = ImageDraw.Draw(over, "RGBA")
    for k, (cx, cy, w, h) in list(SPOTS.items()) + list(BUTTONS.items()):
        x0, y0 = (cx - w / 2) * scale, (cy - h / 2) * scale
        dr.rounded_rectangle((x0, y0, x0 + w * scale, y0 + h * scale), radius=8 * scale, fill=(110, 110, 120, 150),
                             outline=(60, 60, 70, 230), width=max(1, round(1.5 * scale)))
        dr.text((x0 + 4 * scale, y0 + 3 * scale), k, fill=(255, 255, 255, 255))
    return over


def preview(out):
    from PIL import Image, ImageDraw
    names = [(land, pose) for land in LANDS for pose in POSES]
    texts = [(OUT / f"abu_{l}_{p}.svg").read_text() for l, p in names]
    maps = [(OUT / f"{m}.svg").read_text() for m in ("map", "map_night")]
    imgs = render_many([(t, 200, 200) for t in texts] + [(m, 780, 1688) for m in maps])
    abus, mp = imgs[:9], imgs[9:]
    pad = 20
    grid_w = 3 * (200 + pad) + pad
    small_w = 3 * (120 + pad) + pad
    map_w = 2 * (390 + pad)
    Wd = grid_w + small_w + map_w + pad
    Hd = max(3 * (200 + pad) + pad + 260, 844 + 2 * pad)
    sheet = Image.new("RGB", (Wd, Hd), "#F2EEF8")
    dr = ImageDraw.Draw(sheet)
    for i, im in enumerate(abus):
        r, c = divmod(i, 3)
        x, y = pad + c * (200 + pad), pad + r * (200 + pad)
        dr.rounded_rectangle((x, y, x + 200, y + 200), 14, fill="#FFFFFF", outline="#DDD6EA")
        sheet.paste(im, (x, y), im)
        sm = im.resize((120, 120), Image.LANCZOS)
        x2, y2 = grid_w + pad + c * (120 + pad), pad + r * (120 + pad)
        dr.rounded_rectangle((x2, y2, x2 + 120, y2 + 120), 10, fill="#FFFFFF", outline="#DDD6EA")
        sheet.paste(sm, (x2, y2), sm)
    for j, im in enumerate(mp):
        ov = boxes_overlay(im, 2).resize((390, 844), Image.LANCZOS)
        sheet.paste(ov.convert("RGB"), (grid_w + small_w + j * (390 + pad), pad))
    # the icon: round (adaptive, as a launcher shows it) and square (full art) at 48, 96 and 192 px
    import icon
    y = 3 * (200 + pad) + pad + 20
    x = pad
    for kind, row in icon.sheet_pieces():
        for im, m in row:
            sheet.paste(im, (x, y + 192 - im.size[1]), m)
            x += im.size[0] + pad
        x += pad
    sheet.save(out)
    print(out)


def boxes(out):
    from PIL import Image
    im = render_many([((OUT / "map.svg").read_text(), 780, 1688)])[0]
    bg = Image.new("RGBA", im.size, "#FFFFFF")
    bg.alpha_composite(boxes_overlay(im, 2))
    bg.convert("RGB").save(out)
    print(out)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "preview":
        preview(sys.argv[2])
    elif len(sys.argv) >= 3 and sys.argv[1] == "boxes":
        boxes(sys.argv[2])
    elif len(sys.argv) == 1:
        write_all()
    else:
        print(__doc__)
