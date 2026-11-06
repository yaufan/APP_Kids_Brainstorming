"""Drawing kit for 紙片森林 (style B 剪紙拼貼風) in 想一想樂園.

Every picture is built from layers of coloured paper, like a cut-paper collage:
  - each layer is one flat, slightly muted colour (mute(), the same as the mockups), no outlines;
  - its edge is a little irregular, as if cut by hand or torn (the outline is resampled every few
    units and pushed in and out along its normal by smooth noise);
  - it casts a small soft shadow on what is under it (two copies of the same path, moved down and
    to the right, in a dark brown at low opacity);
  - big layers carry a fine paper grain (a few very faint short fibres, light and dark).

The approved mockups (docs/mockups/make_mockups.py) made this look with an SVG filter (displacement,
noise, drop shadow). The app draws the pictures with flutter_svg, which draws no filters, masks, CSS
or text, so this kit builds the same look from plain paths, <use>, gradients and fill-opacity only.

How a drawing is made:
    begin()
    paper(ell(0, 0, 40), "#F2B33D")            # a paper layer (any SVG path, or a list of points)
    with tf("translate(10 0) rotate(20)"):     # transforms, like an SVG <g transform>
        paper(rr(-5, -5, 10, 30, 4), "#4FB45A")
    line("M-10,20 Q0,28 10,20", "#4A3426")     # a narrow paper strip (mouth, leg, antenna)
    svg = finish()                              # fits it into the 200 x 200 box, tears the edges
    write("bee", svg)

Shapes are drawn in any units; finish() measures them, scales them to fill about 85% of the box
and only then roughens the edges, so every picture gets the same edge, shadow and grain on screen.
Everything is deterministic: the noise comes from random.Random seeded by the picture name.
"""
import colorsys
import hashlib
import math
import pathlib
import random
import re
import xml.etree.ElementTree as ET
from contextlib import contextmanager

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "app" / "assets" / "art" / "forest"

SHADOW = "#4A3420"      # the shadow under each paper layer
# (dx, dy, opacity) of the two shadow copies, in units of the 200 x 200 box (scenes: 1 unit = 1 px)
SHADOW_STEPS = ((1.1, 1.9, .19), (2.3, 3.9, .09))


# ---------------------------------------------------------------- colours (as in the mockups)
def _rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def mix(a, b, t):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(x + (y - x) * t))) for x, y in zip(_rgb(a), _rgb(b)))


def lt(c, t):
    return mix(c, "#FFFFFF", t)


def dk(c, t):
    return mix(c, "#2A1E14", t)


def _hls(c):
    return colorsys.rgb_to_hls(*[x / 255 for x in _rgb(c)])


def _hex(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h % 1, max(0, min(1, l)), max(0, min(1, s)))
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def tone(c, l=1.0, s=1.0, dh=0.0):
    h, L, S = _hls(c)
    return _hex(h + dh, L * l, S * s)


def mute(c):
    """Paper colours: a little softer (the mockups' style B)."""
    h, L, S = _hls(c)
    return mix(_hex(h, L, S * .8), "#EFE4D2", .14)


# ---------------------------------------------------------------- shape helpers (SVG path strings)
def ell(cx, cy, rx, ry=None):
    ry = rx if ry is None else ry
    return f"M{cx - rx:.2f},{cy:.2f} A{rx:.2f},{ry:.2f} 0 1 0 {cx + rx:.2f},{cy:.2f} A{rx:.2f},{ry:.2f} 0 1 0 {cx - rx:.2f},{cy:.2f}Z"


def rr(x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    return (f"M{x + r:.2f},{y:.2f} H{x + w - r:.2f} A{r:.2f},{r:.2f} 0 0 1 {x + w:.2f},{y + r:.2f} V{y + h - r:.2f} "
            f"A{r:.2f},{r:.2f} 0 0 1 {x + w - r:.2f},{y + h:.2f} H{x + r:.2f} A{r:.2f},{r:.2f} 0 0 1 {x:.2f},{y + h - r:.2f} "
            f"V{y + r:.2f} A{r:.2f},{r:.2f} 0 0 1 {x + r:.2f},{y:.2f}Z")


def spline(pts, n=10, closed=False):
    """Catmull-Rom curve through pts (tuples: x, y[, width])."""
    P = list(pts)
    P = [P[-1]] + P + [P[0], P[1]] if closed else [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / n
            out.append(tuple(.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t ** 3)
                             for a, b, c, d in zip(p0, p1, p2, p3)))
    if not closed:
        out.append(tuple(P[-2]))
    return out


def poly(pts, close=True):
    return "M" + " L".join(f"{p[0]:.2f},{p[1]:.2f}" for p in pts) + ("Z" if close else "")


def blob(pts, n=8):
    """A smooth closed shape through pts."""
    return poly(spline(pts, n, closed=True))


def tube(pts, n=10):
    """Outline of an arm, leg, tail...: pts are (x, y, half-width) along its middle, round ends."""
    c = spline(pts, n)
    L, R = [], []
    for i, (x, y, w) in enumerate(c):
        a, b = c[max(0, i - 1)], c[min(len(c) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln_ = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln_, dx / ln_
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
    w1, w0 = c[-1][2], c[0][2]
    d = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in L)
    d += f" A{w1:.2f},{w1:.2f} 0 0 0 {R[-1][0]:.2f},{R[-1][1]:.2f}"
    d += " L" + " L".join(f"{x:.2f},{y:.2f}" for x, y in reversed(R))
    d += f" A{w0:.2f},{w0:.2f} 0 0 0 {L[0][0]:.2f},{L[0][1]:.2f}Z"
    return d


def sym(top, segs):
    """Closed path symmetric about x=0: `segs` are cubic segments (c1, c2, p) down the right half
    from `top` to a point on the middle line."""
    f = lambda p: f"{p[0]:.2f},{p[1]:.2f}"
    m = lambda p: (-p[0], p[1])
    d = "M" + f(top)
    for c1, c2, p in segs:
        d += f" C{f(c1)} {f(c2)} {f(p)}"
    for i in reversed(range(len(segs))):
        c1, c2, _ = segs[i]
        p0 = top if i == 0 else segs[i - 1][2]
        d += f" C{f(m(c2))} {f(m(c1))} {f(m(p0))}"
    return d + "Z"


def star_d(R, r, n=5, cx=0, cy=0, rot=-90, round_=0.0):
    pts = []
    for i in range(2 * n):
        a = math.radians(rot + i * 180 / n)
        rad = R if i % 2 == 0 else r
        pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad))
    if not round_:
        return poly(pts)
    d = ""
    for i in range(len(pts)):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
        a = (p1[0] + (p0[0] - p1[0]) * round_, p1[1] + (p0[1] - p1[1]) * round_)
        b = (p1[0] + (p2[0] - p1[0]) * round_, p1[1] + (p2[1] - p1[1]) * round_)
        d += ("M" if i == 0 else " L") + f"{a[0]:.2f},{a[1]:.2f} Q{p1[0]:.2f},{p1[1]:.2f} {b[0]:.2f},{b[1]:.2f}"
    return d + "Z"


def heart_d(s=1.0, cx=0, cy=0):
    return (f"M{cx},{cy + 9 * s} C{cx - 14 * s},{cy} {cx - 16 * s},{cy - 9 * s} {cx - 9 * s},{cy - 13 * s} "
            f"C{cx - 4 * s},{cy - 15 * s} {cx},{cy - 11 * s} {cx},{cy - 8 * s} C{cx},{cy - 11 * s} {cx + 4 * s},{cy - 15 * s} {cx + 9 * s},{cy - 13 * s} "
            f"C{cx + 16 * s},{cy - 9 * s} {cx + 14 * s},{cy} {cx},{cy + 9 * s}Z")


# ---------------------------------------------------------------- path parsing (to points)
_TOK = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def _cubic(p0, p1, p2, p3):
    est = math.dist(p0, p1) + math.dist(p1, p2) + math.dist(p2, p3)
    n = max(6, int(est / 1.2))
    out = []
    for k in range(1, n + 1):
        t = k / n
        u = 1 - t
        out.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return out


def _quad(p0, p1, p2):
    return _cubic(p0, (p0[0] + 2 / 3 * (p1[0] - p0[0]), p0[1] + 2 / 3 * (p1[1] - p0[1])),
                  (p2[0] + 2 / 3 * (p1[0] - p2[0]), p2[1] + 2 / 3 * (p1[1] - p2[1])), p2)


def _arc(x1, y1, rx, ry, phi, fa, fs, x2, y2):
    if rx == 0 or ry == 0 or (x1 == x2 and y1 == y2):
        return [(x2, y2)]
    rx, ry = abs(rx), abs(ry)
    phi = math.radians(phi)
    cp, sp = math.cos(phi), math.sin(phi)
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = cp * dx + sp * dy, -sp * dx + cp * dy
    lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    co = math.sqrt(max(0.0, num / den)) if den else 0.0
    if fa == fs:
        co = -co
    cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
    cx, cy = cp * cxp - sp * cyp + (x1 + x2) / 2, sp * cxp + cp * cyp + (y1 + y2) / 2

    def ang(ux, uy, vx, vy):
        return math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)

    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not fs and dt > 0:
        dt -= 2 * math.pi
    elif fs and dt < 0:
        dt += 2 * math.pi
    n = max(6, int(abs(dt) * max(rx, ry) / 1.2))
    out = []
    for k in range(1, n + 1):
        t = t1 + dt * k / n
        out.append((cx + rx * math.cos(t) * cp - ry * math.sin(t) * sp, cy + rx * math.cos(t) * sp + ry * math.sin(t) * cp))
    out[-1] = (x2, y2)
    return out


def parse(d):
    """SVG path data -> list of (points, closed)."""
    toks = _TOK.findall(d)
    subs, cur, closed = [], [], False
    i, cmd = 0, None
    x = y = sx = sy = 0.0
    lc = None   # last control point (for S/T)

    def num():
        nonlocal i
        v = float(toks[i])
        i += 1
        return v

    def flush():
        nonlocal cur, closed
        if len(cur) > 1:
            subs.append((cur, closed))
        cur, closed = [], False

    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd in "Zz":
                closed = True
                x, y = sx, sy
                flush()
                lc = None
                continue
        rel = cmd.islower()
        C = cmd.upper()
        ox, oy = (x, y) if rel else (0.0, 0.0)
        if C == "M":
            flush()
            x, y = num() + ox, num() + oy
            sx, sy = x, y
            cur = [(x, y)]
            cmd = "l" if rel else "L"
            lc = None
        elif C == "L":
            x, y = num() + ox, num() + oy
            cur.append((x, y))
            lc = None
        elif C == "H":
            x = num() + ox
            cur.append((x, y))
            lc = None
        elif C == "V":
            y = num() + oy
            cur.append((x, y))
            lc = None
        elif C == "C":
            p1 = (num() + ox, num() + oy)
            p2 = (num() + ox, num() + oy)
            p3 = (num() + ox, num() + oy)
            cur += _cubic((x, y), p1, p2, p3)
            lc = ("C", p2)
            x, y = p3
        elif C == "S":
            p1 = (2 * x - lc[1][0], 2 * y - lc[1][1]) if lc and lc[0] == "C" else (x, y)
            p2 = (num() + ox, num() + oy)
            p3 = (num() + ox, num() + oy)
            cur += _cubic((x, y), p1, p2, p3)
            lc = ("C", p2)
            x, y = p3
        elif C == "Q":
            p1 = (num() + ox, num() + oy)
            p2 = (num() + ox, num() + oy)
            cur += _quad((x, y), p1, p2)
            lc = ("Q", p1)
            x, y = p2
        elif C == "T":
            p1 = (2 * x - lc[1][0], 2 * y - lc[1][1]) if lc and lc[0] == "Q" else (x, y)
            p2 = (num() + ox, num() + oy)
            cur += _quad((x, y), p1, p2)
            lc = ("Q", p1)
            x, y = p2
        elif C == "A":
            rx_, ry_, ph, fa, fs = num(), num(), num(), num(), num()
            x2, y2 = num() + ox, num() + oy
            cur += _arc(x, y, rx_, ry_, ph, int(fa), int(fs), x2, y2)
            x, y = x2, y2
            lc = None
        else:
            raise ValueError(f"path command {cmd}")
    flush()
    return subs


# ---------------------------------------------------------------- transforms
def _mul(A, B):
    """A then... (SVG order): the matrix of `A B` (B applied first)."""
    a1, b1, c1, d1, e1, f1 = A
    a2, b2, c2, d2, e2, f2 = B
    return (a1 * a2 + c1 * b2, b1 * a2 + d1 * b2, a1 * c2 + c1 * d2, b1 * c2 + d1 * d2,
            a1 * e2 + c1 * f2 + e1, b1 * e2 + d1 * f2 + f1)


def _tfm(s):
    M = (1, 0, 0, 1, 0, 0)
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", s):
        v = [float(a) for a in re.split(r"[\s,]+", args.strip()) if a]
        if name == "translate":
            T = (1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0)
        elif name == "scale":
            T = (v[0], 0, 0, v[1] if len(v) > 1 else v[0], 0, 0)
        elif name == "rotate":
            a = math.radians(v[0])
            ca, sa = math.cos(a), math.sin(a)
            T = (ca, sa, -sa, ca, 0, 0)
            if len(v) == 3:
                T = _mul(_mul((1, 0, 0, 1, v[1], v[2]), T), (1, 0, 0, 1, -v[1], -v[2]))
        elif name == "matrix":
            T = tuple(v)
        else:
            raise ValueError(name)
        M = _mul(M, T)
    return M


_STACK = [(1, 0, 0, 1, 0, 0)]


@contextmanager
def tf(s):
    """Draw inside an SVG-style transform, e.g. tf("translate(10 4) rotate(20)")."""
    _STACK.append(_mul(_STACK[-1], _tfm(s)))
    try:
        yield
    finally:
        _STACK.pop()


def _apply(M, p):
    a, b, c, d, e, f = M
    return (a * p[0] + c * p[1] + e, b * p[0] + d * p[1] + f)


# ---------------------------------------------------------------- the picture being drawn
LAYERS = []


def begin():
    LAYERS.clear()
    EXTRA_DEFS.clear()
    _GID[0] = 0
    del _STACK[1:]


def _shape(x):
    if isinstance(x, str):
        return parse(x)
    if x and isinstance(x[0], tuple) and len(x[0]) == 2 and isinstance(x[0][0], (int, float)):
        return [(list(x), True)]
    return x


def paper(d, col, shadow=1.0, grain=True, rough=1.0, op=None, evenodd=False, raw=False):
    """One layer of coloured paper. d: path data, or a list of (x, y) points.
    shadow: 1 normal, 0 none, between: weaker. rough: how torn the edge is (0 = clean).
    raw: use the colour as given (not muted)."""
    M = _STACK[-1]
    subs = [([_apply(M, p) for p in pts], closed) for pts, closed in _shape(d)]
    LAYERS.append(dict(kind="fill", subs=subs, col=col if raw or col.startswith("url(") else mute(col), op=op, shadow=shadow,
                       grain=grain, rough=rough, evenodd=evenodd))


def line(d, col, w=4.0, shadow=1.0, rough=.5, op=None, raw=False, final=True, cap="round"):
    """A narrow paper strip along a path (a mouth, a leg, an antenna). w: width; in units of the
    finished 200 x 200 picture when final=True (so all pictures get the same line), else in the
    drawing's own units."""
    M = _STACK[-1]
    subs = [([_apply(M, p) for p in pts], closed) for pts, closed in _shape(d)]
    sc = math.sqrt(abs(M[0] * M[3] - M[1] * M[2]))
    LAYERS.append(dict(kind="stroke", subs=subs, col=col if raw else mute(col), op=op, shadow=shadow,
                       grain=False, rough=rough, w=w if final else w * sc, final=final, cap=cap))


def dot(cx, cy, r, col="#FFFFFF", op=None):
    """A clean little round piece with no shadow (a shine in an eye)."""
    paper(ell(cx, cy, r), col, shadow=0, grain=False, rough=0, op=op, raw=True)


def clip_convex(subject, clipper, inset=1.0):
    """The part of `subject` inside the convex shape `clipper` (both path data or point lists),
    with the clipper shrunk by `inset` (a factor around its centre), as a point list (in the
    current drawing units, before transforms)."""
    S = _shape(subject)[0][0]
    Cp = _shape(clipper)[0][0]
    cx = sum(p[0] for p in Cp) / len(Cp)
    cy = sum(p[1] for p in Cp) / len(Cp)
    Cp = [(cx + (p[0] - cx) * inset, cy + (p[1] - cy) * inset) for p in Cp]
    # orientation of the clipper
    area = sum(Cp[i - 1][0] * Cp[i][1] - Cp[i][0] * Cp[i - 1][1] for i in range(len(Cp)))
    sgn = 1 if area > 0 else -1

    def inside(p, a, b):
        return sgn * ((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])) >= 0

    def cross(p, q, a, b):
        x1, y1, x2, y2 = p[0], p[1], q[0], q[1]
        x3, y3, x4, y4 = a[0], a[1], b[0], b[1]
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if den == 0:
            return q
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))

    out = S
    for i in range(len(Cp)):
        a, b = Cp[i - 1], Cp[i]
        inp, out = out, []
        if not inp:
            break
        for j in range(len(inp)):
            p, q = inp[j - 1], inp[j]
            if inside(q, a, b):
                if not inside(p, a, b):
                    out.append(cross(p, q, a, b))
                out.append(q)
            elif inside(p, a, b):
                out.append(cross(p, q, a, b))
    return out


# ---------------------------------------------------------------- finishing: fit, tear, write
def _bbox(layers):
    xs, ys = [], []
    for L in layers:
        for pts, _ in L["subs"]:
            xs += [p[0] for p in pts]
            ys += [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


_CANVAS = []   # (W, H) while finishing a scene


def _off(p, m=6):
    W, H = _CANVAS
    return p[0] < -m or p[0] > W + m or p[1] < -m or p[1] > H + m


def _resample(pts, closed, step):
    """Points every `step` along the outline, keeping sharp corners."""
    P = list(pts)
    # drop repeats (and, on a closed outline, the end that comes back to the start)
    Q = [P[0]]
    for p in P[1:]:
        if math.dist(p, Q[-1]) > 1e-4:
            Q.append(p)
    while closed and len(Q) > 1 and math.dist(Q[0], Q[-1]) < 1e-4:
        Q.pop()
    P = Q
    n = len(P)
    if n < 2:
        return P
    # corners
    corners = []
    rng = range(n) if closed else range(1, n - 1)
    for i in rng:
        a, b, c = P[i - 1], P[i], P[(i + 1) % n]
        v1 = (b[0] - a[0], b[1] - a[1])
        v2 = (c[0] - b[0], c[1] - b[1])
        l1, l2 = math.hypot(*v1), math.hypot(*v2)
        if l1 == 0 or l2 == 0:
            continue
        cosang = (v1[0] * v2[0] + v1[1] * v2[1]) / (l1 * l2)
        if cosang < math.cos(math.radians(38)):
            corners.append(i)
    if not closed:
        corners = [0] + corners + [n - 1]
    elif not corners:
        corners = [0]
    out = []
    segs = list(zip(corners, corners[1:] + ([corners[0] + n] if closed else [])))
    for i0, i1 in segs:
        chain = [P[k % n] for k in range(i0, i1 + 1)]
        if _CANVAS and all(_off(p) for p in chain + [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in zip(chain, chain[1:])]):
            out.append((chain[0], True))     # off the canvas: no need for a torn edge
            continue
        L = [0.0]
        for a, b in zip(chain, chain[1:]):
            L.append(L[-1] + math.dist(a, b))
        tot = L[-1]
        m = max(1, round(tot / step))
        out.append((chain[0], True))
        j = 0
        for k in range(1, m):
            s = tot * k / m
            while L[j + 1] < s:
                j += 1
            f = (s - L[j]) / ((L[j + 1] - L[j]) or 1)
            a, b = chain[j], chain[j + 1]
            out.append(((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f), False))
    if not closed:
        out.append((P[-1], True))
    return out


def _tear(pts, closed, rng, amp, step, wl):
    """Resample and push each point along the normal by smooth noise (a cut/torn paper edge)."""
    R = _resample(pts, closed, step)
    n = len(R)
    if n < 3 or amp <= 0:
        return [p for p, _ in R]
    per = sum(math.dist(R[i - 1][0], R[i][0]) for i in range(1 if not closed else 0, n))
    # small shapes tear less
    amp *= min(1.0, per / 90)
    k1 = max(3, round(per / wl))
    k2 = max(5, round(per / (wl * .3)))
    v1 = [rng.uniform(-1, 1) for _ in range(k1 + 1)]
    v2 = [rng.uniform(-1, 1) for _ in range(k2 + 1)]
    if closed:
        v1[-1], v2[-1] = v1[0], v2[0]

    def noise(v, k, u):
        x = u * k
        i = min(int(x), k - 1)
        f = x - i
        f = f * f * (3 - 2 * f)
        return v[i] * (1 - f) + v[i + 1] * f

    out = []
    s = 0.0
    for i in range(n):
        if i:
            s += math.dist(R[i - 1][0], R[i][0])
        p, corner = R[i]
        a, b = R[i - 1][0] if (i or closed) else p, R[(i + 1) % n][0] if (i < n - 1 or closed) else p
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln_ = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln_, dx / ln_
        u = s / per if per else 0
        off = amp * (noise(v1, k1, u) * .75 + noise(v2, k2, u) * .3) + rng.uniform(-.22, .22) * min(1, amp)
        if not closed and (i == 0 or i == n - 1):
            off *= .3
        if corner:
            off *= .5
        out.append((p[0] + nx * off, p[1] + ny * off))
    return out


def _d(subs, closed_flags, prec=10):
    """Compact path data: absolute start, then relative moves in tenths."""
    out = []
    for pts, closed in zip(subs, closed_flags):
        q = [(round(x * prec), round(y * prec)) for x, y in pts]
        r = [q[0]]
        for p in q[1:]:
            if p != r[-1]:
                r.append(p)
        if closed and len(r) > 1 and r[-1] == r[0]:
            r.pop()
        f = lambda v: _num(v / prec)
        s = f"M{f(r[0][0])},{f(r[0][1])}"
        if len(r) > 1:
            s += "l"
            parts = []
            for (x0, y0), (x1, y1) in zip(r, r[1:]):
                a, b = f(x1 - x0), f(y1 - y0)
                parts.append(a + ("" if b.startswith("-") else ",") + b)
            s += parts[0] + "".join(("" if p.startswith("-") else " ") + p for p in parts[1:])
        if closed:
            s += "z"
        out.append(s)
    return "".join(out)


def _num(v):
    s = f"{v:.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    if s.startswith("0."):
        s = s[1:]
    elif s.startswith("-0."):
        s = "-" + s[2:]
    if s in ("-0", ""):
        s = "0"
    return s


def _inside(p, subs):
    """Even-odd point in polygon(s)."""
    x, y = p
    c = False
    for pts in subs:
        n = len(pts)
        j = n - 1
        for i in range(n):
            xi, yi = pts[i]
            xj, yj = pts[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi:
                c = not c
            j = i
    return c


def _area(pts):
    return abs(sum(pts[i - 1][0] * pts[i][1] - pts[i][0] * pts[i - 1][1] for i in range(len(pts)))) / 2


def _grain(subs, rng, density, cap, flen=(1.6, 3.6)):
    """Short faint fibres inside the shape: (light path data, dark path data)."""
    xs = [p[0] for s in subs for p in s]
    ys = [p[1] for s in subs for p in s]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    area = sum(_area(s) for s in subs)
    n = min(cap, int(area / density))
    light, dark = [], []
    tries = 0
    while len(light) + len(dark) < n and tries < n * 6:
        tries += 1
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        L = rng.uniform(*flen)
        a = rng.uniform(-.35, .35)
        ex, ey = x + math.cos(a) * L, y + math.sin(a) * L
        m = 2.2
        if not all(_inside(q, subs) for q in ((x, y), (ex, ey), ((x + ex) / 2, (y + ey) / 2 - m), ((x + ex) / 2, (y + ey) / 2 + m),
                                               (x - m, y), (ex + m, ey))):
            continue
        (light if rng.random() < .55 else dark).append((x, y, ex - x, ey - y))

    def d(items):
        items.sort(key=lambda t: (round(t[1] / 12), t[0]))
        s, px, py = "", None, None
        for x, y, dx, dy in items:
            x, y = round(x * 10) / 10, round(y * 10) / 10
            if px is None:
                s += f"M{_num(x)},{_num(y)}"
            else:
                mx, my = _num(x - px), _num(y - py)
                s += f"m{mx}{'' if my.startswith('-') else ','}{my}"
            ddx, ddy = _num(round(dx * 10) / 10), _num(round(dy * 10) / 10)
            s += f"l{ddx}{'' if ddy.startswith('-') else ','}{ddy}"
            px, py = x + round(dx * 10) / 10, y + round(dy * 10) / 10
        return s

    return d(light), d(dark)


def finish(name, box=(200, 200), fit=170, fixed=None, lift=1.5, step=3.0, amp=1.5, wl=15.0,
           grain_density=110, grain_cap=110, specks=True, grain_min=220, shadow_steps=SHADOW_STEPS):
    """Fit the layers into the box (unless `fixed` = (scale, x, y): drawing point (x, y) goes to the
    box centre), tear the edges, add shadows and grain, return the SVG text."""
    W, H = box
    if fixed is None and fit:
        x0, y0, x1, y1 = _bbox(LAYERS)
        # strokes reach out by half their width (final units: added after scaling, roughly)
        s = fit / max(x1 - x0, y1 - y0)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    elif fixed is not None:
        s, cx, cy = fixed
    else:
        s, cx, cy = 1.0, W / 2, H / 2
        lift = 0
        _CANVAS[:] = [W, H]
    M = (s, 0, 0, s, W / 2 - cx * s, H / 2 - cy * s - lift)
    seed = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    defs, body = [], []
    nid = 0
    uses = 0
    for L in LAYERS:
        subs = [([_apply(M, p) for p in pts], closed) for pts, closed in L["subs"]]
        torn = [_tear(pts, closed, rng, amp * L["rough"], step, wl) if L["rough"] > 0 else
                [p for p, _ in _resample(pts, closed, step * .7)] for pts, closed in subs]
        flags = [c for _, c in subs]
        d = _d(torn, flags)
        if L["kind"] == "fill":
            paint = f'fill="{L["col"]}"' + (f' fill-opacity="{L["op"]}"' if L["op"] is not None else "")
            if L["evenodd"]:
                paint += ' fill-rule="evenodd"'
            sh_paint = lambda o: f'fill="{SHADOW}" fill-opacity="{o:.3g}"' + (' fill-rule="evenodd"' if L["evenodd"] else "")
        else:
            w = L["w"] if L["final"] else L["w"] * s
            st = f'fill="none" stroke-width="{w:.3g}" stroke-linecap="{L["cap"]}" stroke-linejoin="round"'
            paint = f'{st} stroke="{L["col"]}"' + (f' stroke-opacity="{L["op"]}"' if L["op"] is not None else "")
            sh_paint = lambda o, st=st: f'{st} stroke="{SHADOW}" stroke-opacity="{o:.3g}"'
        if L["shadow"]:
            nid += 1
            pid = f"p{nid}"
            defs.append(f'<path id="{pid}" d="{d}"/>')
            k = L["shadow"]
            mul = (L["op"] if L["op"] is not None else 1.0)
            for dx, dy, o in shadow_steps:
                body.append(f'<use href="#{pid}" {sh_paint(o * mul * min(1, k))} transform="translate({dx * min(1, k * 1.4):.2g} {dy * min(1, k * 1.4):.2g})"/>')
                uses += 1
            body.append(f'<use href="#{pid}" {paint}/>')
            uses += 1
        else:
            body.append(f'<path d="{d}" {paint}/>')
        if specks and L["kind"] == "fill" and L["grain"]:
            area = sum(_area(t) for t in torn)
            if area > grain_min:
                ld, dd = _grain(torn, rng, grain_density, grain_cap)
                if ld:
                    body.append(f'<path d="{ld}" fill="none" stroke="#FFFFFF" stroke-opacity=".2" stroke-width=".9" stroke-linecap="round"/>')
                if dd:
                    body.append(f'<path d="{dd}" fill="none" stroke="#5A4630" stroke-opacity=".07" stroke-width=".9" stroke-linecap="round"/>')
    _CANVAS.clear()
    if uses > 790:
        raise SystemExit(f"{name}: {uses} <use> (flutter_svg allows fewer)")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
           f'<defs>{"".join(defs)}{"".join(EXTRA_DEFS)}</defs>{"".join(body)}</svg>\n')
    EXTRA_DEFS.clear()
    _GID[0] = 0
    return svg


EXTRA_DEFS = []
_GID = [0]


def lgrad(stops, x1=0, y1=0, x2=0, y2=1, user=True):
    """A linear gradient (for scene skies); returns url(#id)."""
    _GID[0] += 1
    k = f"g{_GID[0]}"
    u = ' gradientUnits="userSpaceOnUse"' if user else ""
    st = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a is not None else "") + "/>"
                 for o, c, a in [(s + (None,))[:3] for s in stops])
    EXTRA_DEFS.append(f'<linearGradient id="{k}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{u}>{st}</linearGradient>')
    return f"url(#{k})"


FORBIDDEN = ("<filter", "<mask", "<style", "<foreignObject", "<image", "<text", "class=", "style=", "<pattern")


def write(name, svg):
    bad = [f for f in FORBIDDEN if f in svg]
    if bad:
        raise SystemExit(f"{name}: uses {bad} (flutter_svg cannot draw these)")
    if svg.count("<use") > 800:
        raise SystemExit(f"{name}: too many <use>")
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"{name}.svg"
    p.write_text(svg)
    text = p.read_text()
    if not text.rstrip().endswith("</svg>"):
        raise SystemExit(f"{p}: cut short")
    ET.fromstring(text)
    kb = len(text.encode()) / 1024
    if kb > 60:
        print(f"warning: {name} is {kb:.0f} KB")
    return kb
