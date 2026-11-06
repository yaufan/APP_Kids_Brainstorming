"""Design-stage sketches for the logic game 「動腦小偵探」 (working name, not final).

    python3 make_mockups.py          # writes docs/mockups/*.png (needs Node.js and Playwright)
    python3 make_mockups.py items    # one big sheet of every drawing, to check them (written to the temp folder)
    python3 make_mockups.py 4        # only one page: 0 = style page, 1..9 = a screen, c = contact sheet

Every picture is drawn here as SVG shapes by code (no outside pictures, no emoji). render.js turns
each page into a PNG with Playwright's Chromium. The font is jf open-huninn from the sibling
字母寵物 checkout.

    0_畫風選擇.png      the same set (fox 阿布, toothbrush, goldfish, apple, toy box) in three styles
    1_首頁.png          hub: the five games, 阿布 waving, 偵探手冊 and the parents' lock
    2_放哪裡.png        put things back where they live (messy bedroom, drag a sock to the basket)
    3_是誰的.png        whose is it? (firefighter, doctor, dog and their things)
    4_連連看.png        draw lines between things that go together
    5_哪個不一樣.png    which one is different? (three fruits and a toy car)
    6_接下來是什麼.png  what comes next? (a train carrying a pattern)
    7_小偵探.png        harder game for 5-6: who took the cake? (suspects and clues)
    8_答對了.png        the explanation after a right answer, and a new sticker
    9_家長模式.png      parents' settings
    contact_sheet.png  screens 1-9 in two rows

Style A 「動畫片風」 (used for screens 1-9): thin outlines in a darker shade of each fill (about
2.2 px on screen whatever the size: `vector-effect: non-scaling-stroke`), bright flat fills with
one hard-edged cel shadow (the `cel_mask` crescent) and a small highlight, big eyes.
Style B 「剪紙拼貼風」: the same shapes as paper layers (`paper` filter: torn edge, grain, small
shadow under each layer), muted colours, no outlines. Style C 「幾何積木風」: drawn again from
circles, squares, triangles and rounded rectangles, flat, no outlines.
"""
import colorsys
import hashlib
import math
import pathlib
import random
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
FONT = pathlib.Path("/home/user/app_kids_paint_for_learning_writing/app/assets/fonts/jf-openhuninn-2.1.ttf")
if not FONT.exists():
    FONT = HERE.parents[2] / "app_kids_paint_for_learning_writing" / "app" / "assets" / "fonts" / "jf-openhuninn-2.1.ttf"
W, H = 390, 844
STYLE = "A"        # A cartoon, B paper cut-out (C has its own drawings)
SCALE = 1.0        # scale of the drawing being made (for the paper filter)
GHOST = False      # True: draw only an empty dashed outline (a thing that is missing)
GHOST_OL = "#A194C4"

# ---------------------------------------------------------------- colours
INK = "#4B3A5E"        # words: deep plum
SOFT = "#9C90AE"
FOX = "#FF8A3D"
FOXD = "#6E3B22"       # fox paws, ear tips
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
WHITE_OL = "#8E86A8"   # outline of white things


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
    """Outline: a dark shade of the fill (not black)."""
    h, L, S = _hls(c)
    if S < .12 or L > .93:
        return WHITE_OL
    return _hex(h - .015, L * .52, min(1, S * 1.05 + .1))


def mute(c):
    """Style B: paper colours (a little softer)."""
    h, L, S = _hls(c)
    return mix(_hex(h, L, S * .8), "#EFE4D2", .14)


# ---------------------------------------------------------------- defs registry
class Defs:
    def __init__(self):
        self.d = {}

    def add(self, key, svg):
        self.d.setdefault(key, svg)
        return key

    def svg(self):
        return "<defs>" + "".join(self.d.values()) + "</defs>"


D = Defs()


def _h(*parts):
    return hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:10]


def _stops(stops):
    return "".join(f'<stop offset="{s[0]}" stop-color="{s[1]}"' + (f' stop-opacity="{s[2]}"' if len(s) > 2 else "") + "/>" for s in stops)


def lg(stops, x1=0, y1=0, x2=0, y2=1, user=False):
    k = "lg" + _h(stops, x1, y1, x2, y2, user)
    u = ' gradientUnits="userSpaceOnUse"' if user else ""
    D.add(k, f'<linearGradient id="{k}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{u}>{_stops(stops)}</linearGradient>')
    return f"url(#{k})"


def rg(stops, cx=.5, cy=.5, r=.5, user=False):
    k = "rg" + _h(stops, cx, cy, r, user)
    u = ' gradientUnits="userSpaceOnUse"' if user else ""
    D.add(k, f'<radialGradient id="{k}" cx="{cx}" cy="{cy}" r="{r}"{u}>{_stops(stops)}</radialGradient>')
    return f"url(#{k})"


def clip(d, fr=""):
    k = "cp" + _h(d, fr)
    D.add(k, f'<clipPath id="{k}"><path d="{d}"{fr.replace("fill-rule", "clip-rule")}/></clipPath>')
    return f"url(#{k})"


def cel_mask(d, s, fr=""):
    """The hard-edged cel shadow: the shape minus a copy of itself moved up-left."""
    k = "cm" + _h(d, s, fr)
    D.add(k, f'<mask id="{k}" maskUnits="userSpaceOnUse" x="-4000" y="-4000" width="8000" height="8000">'
             f'<path d="{d}" fill="#fff"{fr}/><path d="{d}" fill="#000"{fr} transform="translate({s[0]} {s[1]})"/></mask>')
    return f"url(#{k})"


def blur(sd):
    k = "bl" + str(sd).replace(".", "_")
    D.add(k, f'<filter id="{k}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="{sd}"/></filter>')
    return f"url(#{k})"


def drop(op=.14, dy=5, sd=7, col="#5A4A70"):
    k = "ds" + _h(op, dy, sd, col)
    D.add(k, f'<filter id="{k}" x="-20%" y="-20%" width="140%" height="150%">'
             f'<feDropShadow dx="0" dy="{dy}" stdDeviation="{sd}" flood-color="{col}" flood-opacity="{op}"/></filter>')
    return f"url(#{k})"


def paper_filter():
    """Style B: a slightly torn edge, paper grain and a small shadow under the layer (sizes on screen)."""
    s = SCALE
    k = "pp" + _h(round(s, 3))
    D.add(k, f'<filter id="{k}" x="-12%" y="-12%" width="130%" height="135%" color-interpolation-filters="sRGB">'
             f'<feTurbulence type="fractalNoise" baseFrequency="{.05 / s:.4f}" numOctaves="2" seed="5" result="w"/>'
             f'<feDisplacementMap in="SourceGraphic" in2="w" scale="{3.2 / s:.2f}" xChannelSelector="R" yChannelSelector="G" result="c"/>'
             f'<feTurbulence type="fractalNoise" baseFrequency="{.9 / s:.3f} {.35 / s:.3f}" numOctaves="2" seed="11" result="n"/>'
             '<feColorMatrix in="n" type="matrix" values=".33 .33 .33 0 0 .33 .33 .33 0 0 .33 .33 .33 0 0 0 0 0 0 1" result="g"/>'
             '<feComposite in="c" in2="g" operator="arithmetic" k2="1" k3=".16" k4="-.08" result="t"/>'
             '<feComposite in="t" in2="c" operator="in" result="t2"/>'
             f'<feDropShadow in="t2" dx="{1.1 / s:.2f}" dy="{2.0 / s:.2f}" stdDeviation="{1.5 / s:.2f}" flood-color="#4A3420" flood-opacity=".4"/>'
             '</filter>')
    return f"url(#{k})"


# ---------------------------------------------------------------- shape helpers
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
    return "M" + " L".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts) + ("Z" if close else "")


def blob(pts, n=8):
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
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in L)
    d += f" A{w1:.1f},{w1:.1f} 0 0 0 {R[-1][0]:.1f},{R[-1][1]:.1f}"
    d += " L" + " L".join(f"{x:.1f},{y:.1f}" for x, y in reversed(R))
    d += f" A{w0:.1f},{w0:.1f} 0 0 0 {L[0][0]:.1f},{L[0][1]:.1f}Z"
    return d


def sym(top, segs):
    """Closed path symmetric about x=0: `segs` are cubic segments (c1, c2, p) down the right half
    from `top` to a point on the middle line."""
    f = lambda p: f"{p[0]:.1f},{p[1]:.1f}"
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
    return f"M{cx - rx:.1f},{cy:.1f} A{rx:.1f},{ry:.1f} 0 1 0 {cx + rx:.1f},{cy:.1f} A{rx:.1f},{ry:.1f} 0 1 0 {cx - rx:.1f},{cy:.1f}Z"


def rr(x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    return (f"M{x + r:.1f},{y:.1f} H{x + w - r:.1f} A{r:.1f},{r:.1f} 0 0 1 {x + w:.1f},{y + r:.1f} V{y + h - r:.1f} "
            f"A{r:.1f},{r:.1f} 0 0 1 {x + w - r:.1f},{y + h:.1f} H{x + r:.1f} A{r:.1f},{r:.1f} 0 0 1 {x:.1f},{y + h - r:.1f} "
            f"V{y + r:.1f} A{r:.1f},{r:.1f} 0 0 1 {x + r:.1f},{y:.1f}Z")


def star_d(R, r, n=5, cx=0, cy=0, rot=-90, round_=0.0):
    pts = []
    for i in range(2 * n):
        a = math.radians(rot + i * 180 / n)
        rad = R if i % 2 == 0 else r
        pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad))
    if not round_:
        return poly(pts)
    # soft corners: quadratic through each point
    d = ""
    for i in range(len(pts)):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
        a = (p1[0] + (p0[0] - p1[0]) * round_, p1[1] + (p0[1] - p1[1]) * round_)
        b = (p1[0] + (p2[0] - p1[0]) * round_, p1[1] + (p2[1] - p1[1]) * round_)
        d += ("M" if i == 0 else " L") + f"{a[0]:.1f},{a[1]:.1f} Q{p1[0]:.1f},{p1[1]:.1f} {b[0]:.1f},{b[1]:.1f}"
    return d + "Z"


def heart_d(s=1.0, cx=0, cy=0):
    return (f"M{cx},{cy + 9 * s} C{cx - 14 * s},{cy} {cx - 16 * s},{cy - 9 * s} {cx - 9 * s},{cy - 13 * s} "
            f"C{cx - 4 * s},{cy - 15 * s} {cx},{cy - 11 * s} {cx},{cy - 8 * s} C{cx},{cy - 11 * s} {cx + 4 * s},{cy - 15 * s} {cx + 9 * s},{cy - 13 * s} "
            f"C{cx + 16 * s},{cy - 9 * s} {cx + 14 * s},{cy} {cx},{cy + 9 * s}Z")


# ---------------------------------------------------------------- the cel-shaded part (style A) / paper layer (style B)
def part(d, fill, s=(-6, -7), sh=None, ol=None, hl="", cls="o", fr=False, op=None):
    """One shape: flat fill, a hard shadow crescent at the bottom-right, an optional highlight,
    and a thin outline in a darker shade of the fill (style A). In style B: one paper layer."""
    f = ' fill-rule="evenodd"' if fr else ""
    o_ = f' opacity="{op}"' if op is not None else ""
    if GHOST:
        return f'<path d="{d}" fill="#FBF9FF"{f} stroke="{GHOST_OL}" class="o" stroke-dasharray="5 4" stroke-linejoin="round"/>'
    if STYLE == "B":
        return f'<path d="{d}" fill="{mute(fill)}"{f}{o_} filter="{paper_filter()}"/>'
    out = f'<path d="{d}" fill="{fill}"{f}{o_}/>'
    if s:
        out += f'<path d="{d}" fill="{sh or shd(fill)}"{f}{o_} mask="{cel_mask(d, s, f)}"/>'
    out += hl
    if ol is not False:
        out += f'<path d="{d}" fill="none" stroke="{ol or lin(fill)}" class="{cls}" stroke-linejoin="round"/>'
    return out


def comp(d, fill, inner="", s=(-6, -7), sh=None, ol=None, hl="", fr=False):
    """A shape with things painted inside it (clipped to it), outline on top."""
    f = ' fill-rule="evenodd"' if fr else ""
    out = part(d, fill, s, sh, False, "", fr=fr)
    if inner:
        out += f'<g clip-path="{clip(d, f)}">{inner}</g>'
    if STYLE == "A" and not GHOST:
        out += hl
        if ol is not False:
            out += f'<path d="{d}" fill="none" stroke="{ol or lin(fill)}" class="o" stroke-linejoin="round"/>'
    return out


def ln(d, col, cls="o2", extra=""):
    """A drawn line (mouth, crease...), fixed width on screen."""
    if GHOST:
        return f'<path d="{d}" fill="none" stroke="{GHOST_OL}" class="o0" stroke-dasharray="4 4" stroke-linecap="round"/>'
    if STYLE == "B":
        return f'<path d="{d}" fill="none" stroke="{mute(col)}" stroke-width="{2.6 / SCALE:.2f}" stroke-linecap="round" stroke-linejoin="round" filter="{paper_filter()}"/>'
    return f'<path d="{d}" fill="none" stroke="{col}" class="{cls}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def hi(d, w=5, op=.75):
    """A white highlight stroke (scales with the drawing). Not in style B."""
    if STYLE == "B" or GHOST:
        return ""
    return f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="{w}" stroke-linecap="round" opacity="{op}"/>'


def hidot(cx, cy, r, op=.85):
    if STYLE == "B" or GHOST:
        return ""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#FFFFFF" opacity="{op}"/>'


def eye(cx, cy, rx, ry, lx=1.0, ly=2.0, pc="#2E1C14", ol="#5A3424", big=1.0):
    """Big cartoon eye: white, a large dark pupil, two shines."""
    o = part(ell(cx, cy, rx, ry), "#FFFFFF", s=None, ol=ol)
    px, py, prx, pry = cx + lx, cy + ly, rx * .7 * big, ry * .72 * big
    o += part(ell(px, py, prx, pry), pc, s=None, ol=False)
    if STYLE == "A":
        o += f'<g clip-path="{clip(ell(px, py, prx, pry))}"><ellipse cx="{px}" cy="{py + pry * .95}" rx="{prx * 1.1}" ry="{pry * .55}" fill="{mix(pc, "#C8875A", .55)}" opacity=".8"/></g>'
    o += f'<circle cx="{px - prx * .32:.1f}" cy="{py - pry * .36:.1f}" r="{prx * .42:.1f}" fill="#FFFFFF"/>'
    o += f'<circle cx="{px + prx * .38:.1f}" cy="{py + pry * .3:.1f}" r="{prx * .17:.1f}" fill="#FFFFFF"/>'
    return o


def happy_eye(cx, cy, w, col="#3A2418"):
    return ln(f"M{cx - w},{cy + w * .35} Q{cx},{cy - w * .9} {cx + w},{cy + w * .35}", col, "o3")


def blush(cx, cy, rx=9, ry=5.5, col="#FF8E9A", op=.5):
    if STYLE == "B":
        return part(ell(cx, cy, rx, ry), col, s=None, op=.8)
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{col}" opacity="{op}"/>'


def g(inner, tr=""):
    return f'<g transform="{tr}">{inner}</g>' if tr else f"<g>{inner}</g>"


# ================================================================ STYLE A DRAWINGS
BOX = {}


def reg(box):
    def deco(f):
        BOX[f.__name__] = box
        return f
    return deco


# ---------------------------------------------------------------- 阿布 the fox detective
def magnifier(cx, cy, r, ang=135, hl_len=1.25):
    """A magnifying glass: lens centre (cx, cy), handle pointing at angle `ang` (degrees, screen)."""
    a = math.radians(ang)
    hx0, hy0 = cx + math.cos(a) * r * 1.02, cy + math.sin(a) * r * 1.02
    hx1, hy1 = cx + math.cos(a) * r * (1 + hl_len), cy + math.sin(a) * r * (1 + hl_len)
    o = part(tube([(hx0, hy0, r * .2), (hx1, hy1, r * .24)], 2), "#9B5E34", s=(-2, -2.5))
    o += part(ell(cx, cy, r * 1.16), GOLD, s=(-2.5, -3))
    o += part(ell(cx, cy, r * .86), "#D9F3FF", s=None, ol="#B88A1E")
    if STYLE == "A":
        o += f'<g clip-path="{clip(ell(cx, cy, r * .86))}"><circle cx="{cx + r * .5}" cy="{cy + r * .55}" r="{r * .75}" fill="#BCE6FA"/></g>'
        o += hi(f"M{cx - r * .55:.1f},{cy - r * .1:.1f} A{r * .58:.1f},{r * .58:.1f} 0 0 1 {cx - r * .1:.1f},{cy - r * .55:.1f}", r * .16, .95)
    return o


def fox_arm(pts, paw):
    return part(tube(pts), FOX, s=(-3, -3.5)) + part(ell(paw[0], paw[1], paw[2]), FOXD, s=(-2.5, -3))


@reg((-118, -168, 150, 122))
def fox(pose="wave", mouth="open", look=(1.0, 2.0), hold=None):
    """阿布. pose: wave (right paw up, glass in left), glass (glass held up by the face),
    sticker (right paw holds `hold` up high), point (glass in left, right paw pointing)."""
    o = []
    # tail (behind, to the right)
    tail = "M26,92 C60,106 108,98 122,66 C134,40 128,12 108,-4 C104,20 96,38 80,50 C64,60 44,62 28,60 Z"
    tip = "M70,-40 L150,-40 L150,36 C130,38 112,30 102,20 C94,12 88,0 84,-40Z"
    o.append(comp(tail, FOX, part(tip, CREAM, s=(-5, -6), ol="#C8936C"), s=(-8, -9)))
    # left arm (viewer's left) holding the glass down at the side, or resting
    if pose in ("wave", "sticker", "point"):
        o.append(magnifier(-86, 50, 24, 50, 1.0))
        o.append(fox_arm([(-30, 40, 10.5), (-48, 58, 9.5), (-58, 74, 9.5)], (-60, 78, 11.5)))
    # body
    body = "M-38,20 C-52,44 -56,80 -44,98 C-30,112 30,112 44,98 C56,80 52,44 38,20 Z"
    belly = "M-22,40 C-31,56 -31,84 -18,96 C-6,102 6,102 18,96 C31,84 31,56 22,40 C10,33 -10,33 -22,40 Z"
    o.append(comp(body, FOX, part(belly, CREAM, s=(-5, -6), ol="#D9A47C"), s=(-9, -10)))
    for x in (-23, 23):
        o.append(part(ell(x, 105, 19, 11), FOXD, s=(-3, -3.5)))
    if pose == "glass":
        o.append(fox_arm([(-30, 40, 10.5), (-46, 62, 9.5), (-50, 80, 9.5)], (-50, 84, 11.5)))
    # ears
    ear = "M26,-92 C38,-124 62,-152 84,-158 C90,-130 88,-100 74,-70 Z"
    ear_in = "M40,-96 C48,-116 62,-134 76,-142 C80,-122 78,-102 70,-84 Z"
    ear_tip = "M30,-200 L130,-200 L130,-126 C112,-130 92,-128 40,-118Z"
    for sx in (1, -1):
        o.append(g(comp(ear, FOX, part(ear_tip, FOXD, s=None, ol=False) + part(ear_in, "#FFE2C8", s=None, ol="#E7A47A"), s=(-5, -6)),
                   f"scale({sx} 1)"))
    # head
    head = sym((0, -104), [((34, -104), (62, -92), (70, -66)), ((75, -50), (77, -36), (80, -26)),
                           ((86, -20), (94, -14), (102, -10)), ((94, -4), (86, -2), (80, -1)),
                           ((84, 4), (88, 8), (92, 12)), ((78, 17), (66, 20), (56, 22)), ((40, 31), (20, 35), (0, 35))])
    face = ("M-130,70 L-130,-20 C-100,-24 -72,-12 -50,-8 C-32,-5 -18,-18 -11,-29 C-6,-36 6,-36 11,-29 "
            "C18,-18 32,-5 50,-8 C72,-12 100,-24 130,-20 L130,70 Z")
    o.append(comp(head, FOX, part(face, CREAM, s=(-4, -6), ol="#D9A47C"), s=(-9, -10),
                  hl=hi("M-46,-90 C-34,-98 -20,-101 -8,-101", 6, .5)))
    # cap (a little tilted)
    dome = "M-58,-86 C-58,-128 -32,-148 0,-148 C32,-148 58,-128 58,-86 C30,-95 -30,-95 -58,-86 Z"
    checks = "".join(ln(dd, "#7E4A28", "o0") for dd in ("M-30,-146 C-34,-120 -34,-100 -32,-88", "M0,-150 L0,-88",
                                                        "M30,-146 C34,-120 34,-100 32,-88", "M-60,-118 C-30,-126 30,-126 60,-118"))
    brim = "M-64,-88 C-34,-100 34,-100 64,-88 C66,-80 60,-75 52,-77 C26,-86 -26,-86 -52,-77 C-60,-75 -66,-80 -64,-88 Z"
    bow = ("M0,-147 C-6,-160 -22,-164 -22,-154 C-22,-146 -10,-144 0,-147 Z"
           "M0,-147 C6,-160 22,-164 22,-154 C22,-146 10,-144 0,-147 Z")
    o.append(g(comp(dome, "#A8693D", checks, s=(-6, -7), hl=hi("M-40,-112 C-34,-128 -20,-138 -6,-140", 5, .45))
               + part(brim, "#8A5330", s=(-3, -4)) + part(bow, "#B97A48", s=(-2, -3)) + part(ell(0, -148, 5), "#8A5330", s=None),
               "rotate(-7 0 -100)"))
    # face
    lx, ly = look
    for x in (-32, 32):
        o.append(eye(x, -46, 16, 20, lx, ly, ol="#5A2E1A"))
        o.append(ln(f"M{x - 11},{-74} Q{x},{-81} {x + 11},{-74}", "#7A3E1C", "o3"))
    o.append(blush(-58, -16, 10, 6) + blush(58, -16, 10, 6))
    if mouth == "open":
        mo = "M-13,-1 Q0,4 13,-1 C12,12 6,18 0,18 C-6,18 -12,12 -13,-1Z"
        o.append(comp(mo, "#8A2F2F", f'<ellipse cx="0" cy="18" rx="9" ry="7" fill="#FF8A93"/>', s=None, ol="#5A2018"))
    else:
        o.append(ln("M-12,-1 Q-6,7 0,1 Q6,7 12,-1", "#5A2018", "o3"))
    o.append(part("M-9,-17 C-9,-23 9,-23 9,-17 C9,-11 3,-7 0,-7 C-3,-7 -9,-11 -9,-17Z", "#3B2418", s=None, ol="#2A160E",
                  hl=hidot(-3, -18, 2.4, .9)))
    # right arm (viewer's right)
    if pose == "wave":
        o.append(ln("M88,-48 Q98,-40 100,-28 M98,-58 Q112,-46 114,-30", "#E0773A", "o3"))
        o.append(fox_arm([(32, 40, 10.5), (54, 22, 9.5), (70, -6, 9.5)], (72, -12, 12)))
    elif pose == "glass":
        o.append(fox_arm([(32, 40, 10.5), (58, 26, 9.5), (78, 0, 9.5)], (80, -6, 12)))
        o.append(magnifier(104, -58, 27, 115, .9))
        o.append(part(ell(80, -6, 12), FOXD, s=(-2.5, -3)))
    elif pose == "sticker":
        o.append(fox_arm([(32, 40, 10.5), (60, 20, 9.5), (84, -18, 9.5)], (86, -24, 12)))
        if hold:
            o.append(hold)
        o.append(part(ell(86, -24, 12), FOXD, s=(-2.5, -3)))
    elif pose == "point":
        o.append(fox_arm([(32, 40, 10.5), (58, 32, 9.5), (84, 20, 9.5)], (88, 18, 12)))
    return "".join(o)


# ---------------------------------------------------------------- fruit and small things
APPLE = ("M0,-50 C20,-68 62,-66 76,-30 C88,6 68,58 36,70 C22,76 10,72 0,67 C-10,72 -22,76 -36,70 "
         "C-68,58 -88,6 -76,-30 C-62,-66 -20,-68 0,-50 Z")


@reg((-82, -98, 82, 76))
def apple(col=RED):
    o = part("M-3,-46 C-5,-62 -1,-76 7,-88 L15,-84 C8,-72 5,-60 5,-46 Z", "#8A5A35", s=(-1.5, -2))
    o += part(APPLE, col, s=(-12, -12), hl=hi("M-56,-26 C-52,-40 -40,-48 -28,-48", 9, .8) + hidot(-60, -8, 4.5))
    o += part("M8,-66 C18,-90 46,-96 60,-84 C48,-64 24,-58 8,-66 Z", "#5CC452", s=(-3, -3.5))
    o += ln("M14,-68 C28,-76 40,-80 50,-82", "#3E8C3A", "o0")
    return o


@reg((-94, -62, 96, 52))
def banana():
    o = part("M-73,-34 L-76,-58 C-76,-62 -66,-63 -64,-59 L-58,-40 Z", "#8A6A35", s=None)
    body = ("M-74,-38 C-66,8 -12,44 44,36 C64,33 80,20 90,4 L86,-2 C68,8 42,14 14,12 "
            "C-22,8 -48,-16 -58,-42 Z")
    o += part(body, YELLOW, s=(-4, -11), hl=hi("M-56,-22 C-40,0 -10,18 24,22", 5, .7))
    o += ln("M-66,-30 C-50,4 -10,30 44,28", "#E2A41E", "o0")
    o += part("M86,-2 L92,6 L88,9 L82,3 Z", "#6B4A26", s=None)
    return o


@reg((-62, -96, 62, 78))
def grapes(col=PURPLE):
    o = part("M2,-56 C0,-70 4,-82 12,-90 L18,-86 C12,-78 9,-68 10,-56Z", "#7A5532", s=None)
    o += part("M10,-70 C22,-92 50,-94 58,-80 C46,-62 26,-60 10,-70 Z", "#5CC452", s=(-3, -3.5))
    rows = [(-52, [-36, -12, 12, 36]), (-28, [-24, 0, 24]), (-4, [-36, -12, 12, 36]), (20, [-24, 0, 24]), (44, [-12, 12]), (64, [0])]
    for y, xs in rows:
        for x in xs:
            o += part(ell(x, y, 14), col, s=(-3.5, -4), hl=hidot(x - 5, y - 5, 3.4))
    return o


@reg((-92, -66, 96, 44))
def toycar(col=BLUE):
    body = ("M-82,8 L-82,-12 C-82,-20 -76,-25 -68,-25 L-48,-26 L-32,-52 C-28,-58 -22,-60 -14,-60 L28,-60 "
            "C36,-60 42,-57 47,-51 L64,-28 L76,-26 C84,-24 88,-18 88,-10 L88,8 C88,14 84,18 78,18 L-76,18 C-80,18 -82,14 -82,8 Z")
    o = part(body, col, s=(-9, -10), hl=hi("M-70,-16 L-40,-16", 5, .6))
    o += part("M-38,-28 L-26,-50 C-24,-53 -21,-54 -17,-54 L-2,-54 L-2,-28 Z", "#CDEEFF", s=None, ol=lin(col))
    o += part("M6,-54 L26,-54 C31,-54 35,-52 38,-48 L52,-28 L6,-28 Z", "#CDEEFF", s=None, ol=lin(col))
    o += hi("M-28,-34 L-20,-48 M14,-34 L22,-48", 3.5, .9)
    o += part(rr(76, -18, 12, 8, 3), "#FFE066", s=None, ol=lin(col))
    o += part(rr(-86, -6, 10, 8, 3), "#FF7A6E", s=None, ol=lin(col))
    o += ln("M2,-26 L2,12", lin(col), "o0")
    for x in (-48, 52):
        o += part(ell(x, 18, 19), "#3E3A4A", s=(-3, -4), ol="#221E2C")
        o += part(ell(x, 18, 8.5), "#D7D3E2", s=None, ol="#6E6880")
    return o


@reg((-96, -58, 98, 46))
def toothbrush(col="#2EC4C0"):
    o = []
    handle = ("M-92,6 C-92,-2 -88,-6 -80,-6 L20,-8 C30,-8 38,-6 46,-4 L92,-6 C96,-6 98,-2 98,2 L98,10 "
              "C98,14 96,16 92,16 L46,14 C38,16 30,18 20,18 L-80,18 C-88,18 -92,14 -92,6 Z")
    o.append(part(handle, col, s=(-4, -6), hl=hi("M-78,-1 L10,-3", 4, .7)))
    o.append(part(rr(-56, -3, 34, 16, 8), "#FF8FB1", s=(-2, -3)))
    # bristles: one block of tufts on the head, white with blue tops
    block = "M44,-8 L44,-36 C44,-40 46,-42 50,-42 L88,-42 C92,-42 94,-40 94,-36 L94,-8 Z"
    tops = "M30,-60 L110,-60 L110,-30 L30,-30 Z"
    o.append(comp(block, "#FFFFFF", part(tops, "#7CC7FF", s=None, ol=False)
                  + "".join(ln(f"M{x},-41 L{x},-9", "#9AA9C8", "o0") for x in (54.5, 65, 75.5, 85)), s=(-3, -4)))
    return g("".join(o), "rotate(-28)")


@reg((-104, -76, 102, 72))
def goldfish(col="#FF8A26"):
    o = []
    fin_c = "#FFC23D"
    tail = "M52,0 C70,-22 90,-44 102,-40 C96,-20 92,-8 92,0 C92,8 96,20 102,40 C90,44 70,22 52,0 Z"
    o.append(part(tail, fin_c, s=(-4, -5)) + ln("M60,0 L94,-26 M60,0 L94,26 M60,0 L96,0", "#E88A1E", "o0"))
    o.append(part("M-14,-40 C-6,-66 22,-74 40,-62 C34,-50 26,-42 18,-38 Z", fin_c, s=(-3, -4)))
    body = "M-78,4 C-78,-30 -40,-50 -2,-48 C34,-46 58,-24 62,0 C58,24 34,46 -2,48 C-40,50 -78,36 -78,4 Z"
    belly = "M-70,20 C-50,44 0,50 40,30 L60,60 L-90,60 Z"
    o.append(comp(body, col, part(belly, "#FFC77A", s=None, ol=False), s=(-9, -10),
                  hl=hi("M-56,-26 C-44,-38 -28,-42 -14,-42", 6, .7)))
    o.append(ln("M14,-36 C22,-20 22,20 14,36", "#D9631A", "o0"))
    o.append(part("M-6,18 C4,30 20,34 30,30 C24,20 10,14 -6,18 Z", fin_c, s=None))
    o.append(eye(-44, -10, 13, 15, -2, 1, ol="#8A3A10"))
    o.append(ln("M-72,12 Q-66,18 -58,14", "#8A3A10", "o2"))
    o.append(blush(-50, 12, 7, 4))
    for (bx, by, r) in ((-96, -38, 6), (-90, -60, 4.2), (-100, -72, 3)):
        o.append(part(ell(bx, by, r), "#DFF4FF", s=None, ol="#7FB8E0", hl=hidot(bx - r * .35, by - r * .35, r * .3)))
    return "".join(o)


@reg((-84, -98, 84, 66))
def toybox(col="#4FB3F6", toys=True):
    o = []
    lid = "M-72,-26 L-62,-74 C-60,-80 -56,-82 -50,-82 L50,-82 C56,-82 60,-80 62,-74 L72,-26 Z"
    o.append(part(lid, shd(col), s=(-4, -5)) + part(rr(-56, -90, 112, 12, 5), YELLOW, s=None)
             + part(rr(-30, -60, 60, 14, 7), lt(col, .35), s=None, ol=lin(col)))
    o.append(part("M-66,-26 L66,-26 L60,-14 L-60,-14 Z", "#3A3150", s=None, ol=False))
    if toys:
        o.append(part(ell(-30, -30, 24), RED, s=(-4, -5), hl=hi("M-44,-36 A16,16 0 0 1 -34,-48", 4, .8))
                 + part("M-30,-54 C-24,-42 -24,-18 -30,-6 C-36,-18 -36,-42 -30,-54Z", "#FFFFFF", s=None, ol=lin(RED)))
        o.append(g(part(rr(-20, -20, 40, 40, 6), YELLOW, s=(-4, -5)) + part(star_d(12, 5.5, round_=.18), "#FF8A3D", s=None),
                   "translate(24 -36) rotate(12)"))
        o.append(part("M44,-40 C44,-58 64,-62 66,-46 L66,-20 L44,-20Z", GREEN, s=(-3, -4)))
    front = "M-74,-26 L74,-26 L74,48 C74,56 68,62 60,62 L-60,62 C-68,62 -74,56 -74,48 Z"
    trim = "M-80,-30 L80,-30 L80,-12 L-80,-12 Z"
    o.append(comp(front, col, part(trim, YELLOW, s=None, ol=lin(YELLOW))
                  + part(star_d(17, 8, round_=.18, cx=0, cy=20), "#FFFFFF", s=(-2, -3), ol=lin(col)), s=(-9, -10)))
    o.append(ln("M-74,-12 L74,-12", lin(col), "o2"))
    o.append(part(ell(-44, 20, 7), "#FF7FA3", s=None) + part(ell(44, 20, 7), "#FF7FA3", s=None))
    return "".join(o)


def celov(d, s, op=.16, col="#3B1E5A"):
    """A see-through cel shadow over a many-coloured shape."""
    if STYLE == "B" or GHOST:
        return ""
    return f'<path d="{d}" fill="{col}" opacity="{op}" mask="{cel_mask(d, s)}"/>'


def outline(d, col, cls="o"):
    if STYLE == "B" or GHOST:
        return ""
    return f'<path d="{d}" fill="none" stroke="{col}" class="{cls}" stroke-linejoin="round"/>'


def hose_line(d, col, w, ol=None):
    """A tube drawn as a thick line with a thin darker edge (scales with the drawing)."""
    if GHOST:
        return (f'<path d="{d}" fill="none" stroke="#EEE9F8" stroke-width="{w}" stroke-linecap="round"/>'
                f'<path d="{d}" fill="none" stroke="{GHOST_OL}" class="o" stroke-dasharray="5 4" stroke-linecap="round"/>')
    if STYLE == "B":
        return f'<path d="{d}" fill="none" stroke="{mute(col)}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" filter="{paper_filter()}"/>'
    e = max(2.2 / max(SCALE, .2), 1.2)
    return (f'<path d="{d}" fill="none" stroke="{ol or lin(col)}" stroke-width="{w + 2 * e:.1f}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')


# ---------------------------------------------------------------- the bedroom
@reg((-70, -84, 70, 76))
def teddy(col="#C98A52"):
    li = "#F3D2A6"
    o = []
    for sx in (-1, 1):
        o.append(part(ell(sx * 40, -66, 17), col, s=(-3, -4)) + part(ell(sx * 40, -66, 8.5), li, s=None))
    o.append(part(ell(0, 28, 42, 40), col, s=(-8, -8)))
    o.append(part(ell(0, 34, 24, 24), li, s=None, ol=lin(col)))
    for sx in (-1, 1):
        o.append(part(ell(sx * 42, 20, 13, 20), col, s=(-3, -4)))
        o.append(part(ell(sx * 30, 58, 22, 17), col, s=(-4, -5)) + part(ell(sx * 31, 60, 12, 10), li, s=None))
    o.append(part(ell(0, -28, 48, 42), col, s=(-9, -9), hl=hi("M-30,-56 C-20,-64 -6,-67 6,-66", 5, .55)))
    o.append(part(ell(0, -12, 19, 14), li, s=None, ol=lin(col)))
    o.append(part(ell(0, -18, 7.5, 5.5), "#3A2418", s=None, hl=hidot(-2, -20, 1.8)))
    o.append(ln("M0,-12 L0,-6 M-6,-4 Q0,0 6,-4", "#3A2418", "o2"))
    for sx in (-1, 1):
        o.append(part(ell(sx * 20, -32, 6.5, 7.5), "#2E1C14", s=None, ol=False, hl=hidot(sx * 20 - 2, -35, 2.4)))
    bow = "M0,8 C-8,0 -22,-2 -22,8 C-22,18 -8,16 0,8 Z M0,8 C8,0 22,-2 22,8 C22,18 8,16 0,8 Z"
    o.append(part(bow, RED, s=(-2, -2.5)) + part(ell(0, 8, 5), RED, s=None))
    return "".join(o)


@reg((-46, -46, 46, 46))
def ball():
    c = ell(0, 0, 42)
    P = (-12, -14)
    cols = [RED, "#FFFFFF", BLUE, YELLOW, "#FFFFFF", GREEN]
    wed = []
    for i in range(6):
        a0, a1 = math.radians(i * 60 + 15), math.radians(i * 60 + 75)
        f0 = (P[0] + 120 * math.cos(a0), P[1] + 120 * math.sin(a0))
        f1 = (P[0] + 120 * math.cos(a1), P[1] + 120 * math.sin(a1))
        c0 = (P[0] + 50 * math.cos(a0 + .42), P[1] + 50 * math.sin(a0 + .42))
        c1 = (P[0] + 50 * math.cos(a1 + .42), P[1] + 50 * math.sin(a1 + .42))
        d = f"M{P[0]},{P[1]} Q{c0[0]:.1f},{c0[1]:.1f} {f0[0]:.1f},{f0[1]:.1f} L{f1[0]:.1f},{f1[1]:.1f} Q{c1[0]:.1f},{c1[1]:.1f} {P[0]},{P[1]}Z"
        wed.append(part(d, cols[i], s=None, ol=False))
    o = comp(c, "#FFFFFF", "".join(wed) + part(ell(P[0], P[1], 7), "#FFFFFF", s=None, ol=WHITE_OL), s=None, ol="#6E5A8A")
    o = o[:o.rfind("<path")] + celov(c, (-8, -9), .2) + hi("M-30,-6 A30,30 0 0 1 -14,-30", 5, .7) + o[o.rfind("<path"):]
    return o


@reg((-76, -60, 76, 60))
def picturebook(col="#FF7A59"):
    o = part(rr(-60, -44, 128, 94, 8), "#FFF3D9", s=None, ol="#C9A77A")
    o += "".join(ln(f"M{x},-40 L{x},46", "#D9C19A", "o0") for x in (62, 65))
    cover = rr(-68, -52, 128, 94, 9)
    o += part(cover, col, s=(-6, -7))
    o += part(rr(-68, -52, 18, 94, 7), shd(col), s=None, ol=lin(col))
    win = rr(-40, -38, 88, 66, 10)
    o += comp(win, "#BFE8FF", part(ell(-14, 44, 70, 36), "#7BD36A", s=None, ol=lin("#7BD36A"))
              + part(ell(26, -14, 11), YELLOW, s=None, ol=lin(YELLOW)), s=None, ol=lin(col))
    return g(o, "rotate(-6)")


@reg((-44, -76, 80, 72))
def sock(col="#FF8FB1"):
    leg = ("M-22,-56 L20,-56 L20,6 C20,14 26,19 34,21 L56,27 C70,31 76,46 70,57 C64,67 50,69 38,65 "
           "L-6,52 C-20,48 -26,36 -24,22 Z")
    inner = "".join(part(f"M-40,{y} L40,{y} L40,{y + 9} L-40,{y + 9} Z", "#FFFFFF", s=None, ol=False) for y in (-38, -18))
    inner += part(ell(66, 52, 20), "#B67CF0", s=None, ol=lin("#B67CF0")) + part(ell(-24, 44, 16), "#B67CF0", s=None, ol=lin("#B67CF0"))
    o = comp(leg, col, inner, s=(-7, -8), hl=hi("M-14,-2 L-14,24", 4, .55))
    o += part(rr(-28, -70, 54, 18, 6), "#FFFFFF", s=(-2, -3), ol=lin(col))
    o += "".join(ln(f"M{x},-66 L{x},-56", "#E4A6C0", "o0") for x in (-18, -9, 0, 9, 18))
    return g(o, "rotate(-8)")


@reg((-80, -64, 80, 68))
def tshirt(col="#36C46E"):
    d = ("M-24,-56 C-14,-47 14,-47 24,-56 L58,-42 C64,-40 68,-36 70,-30 L78,-10 L52,0 L46,-12 L46,56 "
         "C46,60 42,63 38,63 L-38,63 C-42,63 -46,60 -46,56 L-46,-12 L-52,0 L-78,-10 L-70,-30 C-68,-36 -64,-40 -58,-42 Z")
    o = part(d, col, s=(-8, -9), hl=hi("M-36,-30 L-36,40", 5, .45))
    o += part("M-24,-56 C-14,-44 14,-44 24,-56 C16,-38 -16,-38 -24,-56 Z", shd(col), s=None)
    o += part(star_d(22, 10, round_=.16, cx=0, cy=10), YELLOW, s=(-2, -3))
    o += ln("M-46,-12 L-46,0 M46,-12 L46,0", lin(col), "o0")
    return o


@reg((-66, -150, 66, 132))
def bookshelf(gap=True):
    wood, back = "#D08E57", "#9E6339"
    o = part(rr(-46, -150, 28, 26, 6), "#E8735A", s=(-2, -3)) + part(ell(-32, -150, 16, 12), GREEN, s=(-2, -3))
    o += part(rr(-60, -126, 120, 252, 9), wood, s=(-7, -8))
    shelves = [(-114, -44), (-32, 40), (52, 114)]
    rng = random.Random(4)
    cols = [RED, BLUE, YELLOW, GREEN, PURPLE, PINK, TEAL, "#FF8A3D"]
    for si, (y0, y1) in enumerate(shelves):
        o += part(f"M-50,{y0} L50,{y0} L50,{y1} L-50,{y1} Z", back, s=None, ol=lin(wood))
        x = -48
        k = 0
        while x < 44:
            if gap and si == 1 and k == 2:
                x += 30
                k += 1
                continue
            bw = rng.choice([12, 14, 16, 18])
            if x + bw > 48:
                break
            bh = rng.randint(int((y1 - y0) * .62), int((y1 - y0) * .9))
            c = cols[(si * 3 + k) % len(cols)]
            o += part(rr(x, y1 - bh, bw, bh, 3), c, s=(-2, -2.5))
            o += ln(f"M{x + 3},{y1 - bh + 10} L{x + bw - 3},{y1 - bh + 10}", lt(c, .55), "o0")
            x += bw + 2
            k += 1
        o += part(rr(-58, y1, 116, 9, 3), lt(wood, .12), s=None, ol=lin(wood))
    o += part(rr(-54, 124, 14, 8, 3), shd(wood), s=None) + part(rr(40, 124, 14, 8, 3), shd(wood), s=None)
    return o


@reg((-66, -64, 70, 68))
def basket(col="#E9B866"):
    body = "M-58,-36 L58,-36 L48,56 C47,61 43,64 38,64 L-38,64 C-43,64 -47,61 -48,56 Z"
    weave = "".join(ln(f"M-70,{y} L70,{y}", shd(col), "o0") for y in (-14, 8, 30, 50))
    for r, y in enumerate((-36, -14, 8, 30)):
        for x in range(-64 + (r % 2) * 9, 70, 18):
            weave += ln(f"M{x},{y + 3} L{x},{y + 19}", shd(col), "o0")
    o = part(ell(0, -38, 60, 13), "#8C5A2C", s=None)
    o += part("M-30,-44 C-24,-60 -2,-64 10,-52 C18,-62 34,-58 36,-44 L30,-34 L-26,-36Z", "#FF8FB1", s=(-2, -3))
    o += comp(body, col, weave, s=(-8, -9))
    o += part("M-60,-40 C-60,-48 60,-48 60,-40 C60,-31 -60,-31 -60,-40Z", shd(col), s=None, ol=lin(col))
    o += part(rr(-46, -26, 22, 9, 4.5), "#8C5A2C", s=None) + part(rr(24, -26, 22, 9, 4.5), "#8C5A2C", s=None)
    towel = "M-48,-44 C-40,-48 -18,-48 -8,-44 L-10,0 C-15,7 -21,1 -27,7 C-33,13 -40,7 -47,3 Z"
    o += comp(towel, "#7CC7FF", part("M-60,-10 L0,-10 L0,-4 L-60,-4Z", "#FFFFFF", s=None, ol=False), s=(-3, -4))
    return o


@reg((-104, -82, 104, 66))
def bed(col="#7C8CF8"):
    wood = "#C9834F"
    o = part("M-100,60 L-100,-56 C-100,-74 -72,-80 -72,-62 L-72,60 Z", wood, s=(-4, -5))
    o += part(rr(-96, 44, 12, 18, 3), shd(wood), s=None) + part(rr(84, 44, 12, 18, 3), shd(wood), s=None)
    o += part(rr(-78, -10, 162, 30, 10), "#FFFFFF", s=(-3, -4))
    o += part(rr(-76, 18, 160, 30, 6), "#B98B6A", s=None)
    o += part(ell(-46, -16, 28, 15), "#FFFFFF", s=(-3, -4), hl=hi("M-62,-22 C-56,-27 -48,-29 -40,-29", 3.5, .9))
    blanket = "M-16,-24 C10,-30 50,-30 82,-22 C90,-20 92,-12 92,-4 L90,40 C90,46 86,48 80,48 L-16,48 C-22,48 -24,44 -24,38 L-24,-14 C-24,-20 -22,-23 -16,-24Z"
    dots = "".join(part(star_d(6, 3, cx=x, cy=y, round_=.15), "#FFFFFF", s=None, ol=False) for x, y in
                   ((0, -6), (30, 10), (60, -8), (8, 28), (44, 34), (74, 22)))
    o += comp(blanket, col, dots, s=(-6, -7))
    o += ln("M-24,-4 C10,-12 50,-12 92,-6", lin(col), "o0")
    o += part("M76,60 L76,-14 C76,-28 104,-28 104,-14 L104,60 Z", wood, s=(-3, -4))
    return o


# ---------------------------------------------------------------- whose is it?
@reg((-74, -64, 78, 44))
def helmet(col="#F04A3E"):
    brim = ("M-64,6 C-40,14 30,14 60,4 C72,0 78,8 70,16 C46,30 -40,28 -66,16 C-74,12 -72,4 -64,6 Z")
    dome = "M-50,10 C-52,-28 -28,-58 4,-58 C36,-58 56,-34 56,8 C24,16 -18,16 -50,10 Z"
    o = part(brim, shd(col), s=(-3, -4))
    o += part(dome, col, s=(-9, -10), hl=hi("M-36,-18 C-32,-36 -18,-48 -4,-50", 6, .7))
    o += ln("M4,-58 C2,-40 2,-20 4,12", lin(col), "o2")
    shield = "M-14,-38 L22,-38 L22,-12 C22,0 12,8 4,12 C-4,8 -14,0 -14,-12 Z"
    o += part(shield, GOLD, s=(-2, -3)) + part(star_d(9, 4, cx=4, cy=-17, round_=.15), "#FFFFFF", s=None, ol=lin(GOLD))
    return o


@reg((-74, -64, 78, 52))
def hose(col="#F04A3E"):
    o = []
    for y in (22, 8, -6):
        o.append(hose_line(ell(-4, y, 52, 22), col, 12))
    o.append(hi(f"M-44,{-14} C-30,-26 -10,-29 10,-28", 3, .7))
    o.append(hose_line("M48,-6 C60,-14 62,-32 54,-40", col, 12))
    noz = "M44,-42 L60,-54 C64,-57 70,-52 67,-48 L56,-34 Z"
    o.append(part(noz, "#C9CED9", s=(-2, -2.5)))
    o.append(part("M59,-52 L70,-62 C72,-64 76,-60 74,-58 L66,-46 Z", GOLD, s=None))
    return "".join(o)


@reg((-60, -72, 64, 70))
def stethoscope(col="#3D7FE0"):
    o = ""
    o += hose_line("M0,-6 C0,24 -34,36 -26,54 C-18,70 30,66 34,40", col, 8)
    o += hose_line("M-24,-60 C-30,-30 -16,-12 0,-6 M24,-60 C30,-30 16,-12 0,-6", "#B9C0CE", 5)
    o += part(ell(-24, -62, 6, 5), "#4B4560", s=None) + part(ell(24, -62, 6, 5), "#4B4560", s=None)
    o += part(ell(0, -6, 6), "#B9C0CE", s=None)
    o += part(ell(38, 30, 19), "#C9CED9", s=(-3, -4), hl=hi("M26,24 A12,12 0 0 1 34,16", 3, .9))
    o += part(ell(38, 30, 11), "#8E95A6", s=None)
    return o


BONE = ("M-38.3,-9 L38.3,-9 A14,14 0 1 1 59.2,0 A14,14 0 1 1 38.3,9 L-38.3,9 "
        "A14,14 0 1 1 -59.2,0 A14,14 0 1 1 -38.3,-9 Z")


@reg((-70, -30, 70, 30))
def bone():
    return part(BONE, "#FFF0D4", s=(-4, -5), ol="#B98A56", hl=hi("M-56,-16 A10,10 0 0 1 -46,-24", 3, .9))


@reg((-40, -82, 42, 74))
def carrot():
    o = ""
    for a in (-24, 0, 24):
        o += g(part("M0,-36 C-10,-50 -10,-70 0,-80 C10,-70 10,-50 0,-36 Z", GREEN, s=(-2, -3)), f"rotate({a} 0 -36)")
    body = "M-22,-34 C-24,-48 22,-48 22,-34 C20,0 8,40 2,62 C0,68 -4,68 -6,62 C-14,40 -22,0 -22,-34Z"
    o += part(body, "#FF8C2B", s=(-6, -7), hl=hi("M-14,-28 C-14,-10 -10,10 -6,24", 4, .6))
    o += ln("M-14,-12 L-4,-12 M6,4 L16,4 M-10,22 L0,22 M2,38 L8,38", "#D9631A", "o2")
    return g(o, "rotate(18)")


# ---------------------------------------------------------------- what goes together?
@reg((-76, -36, 76, 36))
def key(col=GOLD):
    o = part("M-20,-7 L66,-7 C70,-7 72,-5 72,-1 L72,7 L64,7 L64,22 L54,22 L54,7 L50,7 L50,18 L40,18 L40,7 L-20,7 Z", col, s=(-2, -3))
    o += part(ell(-44, 0, 29) + ell(-44, 0, 11), col, s=(-5, -6), fr=True, hl=hi("M-62,-8 A20,20 0 0 1 -50,-24", 4, .8))
    return g(o, "rotate(-20)")


@reg((-74, -52, 72, 70))
def raincloud():
    cl = ("M-54,12 C-72,12 -74,-14 -56,-18 C-58,-42 -28,-50 -16,-36 C-8,-56 28,-56 34,-32 C52,-40 72,-24 62,-6 "
          "C76,0 72,22 56,22 L-50,22 C-52,22 -53,17 -54,12 Z")
    o = ""
    for x, y in ((-30, 44), (0, 56), (30, 44)):
        o += part(f"M{x},{y - 14} C{x + 4},{y - 5} {x + 8},{y + 1} {x + 8},{y + 5} C{x + 8},{y + 10} {x + 4},{y + 13} {x},{y + 13} "
                  f"C{x - 4},{y + 13} {x - 8},{y + 10} {x - 8},{y + 5} C{x - 8},{y + 1} {x - 4},{y - 5} {x},{y - 14}Z", "#4FA8F5", s=(-2, -2.5),
                  hl=hidot(x - 3, y + 2, 2))
    o += part(cl, "#B3C6DE", s=(-8, -10), hl=hi("M-46,-6 C-46,-14 -40,-18 -34,-18", 5, .8))
    return o


@reg((-74, -78, 74, 70))
def umbrella():
    can = ("M-68,0 C-66,-40 -36,-64 0,-64 C36,-64 66,-40 68,0 Q57,-10 45,0 Q34,-10 22,0 Q11,-10 0,0 "
           "Q-11,-10 -22,0 Q-34,-10 -45,0 Q-57,-10 -68,0Z")
    o = hose_line("M0,-4 L0,50 C0,64 -18,64 -18,52", "#8A5A35", 6)
    panels = ""
    xs = [-68, -45, -22, 0, 22, 45, 68]
    for i in range(6):
        if i % 2 == 0:
            panels += part(f"M0,-64 L{xs[i]},0 L{xs[i + 1]},0 Z", YELLOW, s=None, ol=False)
    o += comp(can, "#FF6F91", panels, s=None)
    o += celov(can, (-8, -9), .16)
    o += "".join(ln(f"M0,-63 Q{x * .6:.0f},-34 {x},0", "#C2406A", "o0") for x in xs[1:-1])
    o += outline(can, "#C2406A")
    o += part(rr(-3, -76, 6, 14, 3), "#8A5A35", s=None)
    return o


@reg((-84, -38, 86, 38))
def toothpaste():
    body = "M-70,-22 L-70,22 L-62,22 C-30,24 20,26 46,16 L46,-16 C20,-26 -30,-24 -62,-22 Z"
    inner = part("M-30,-40 L18,-40 L18,40 L-30,40 Z", BLUE, s=None, ol=False)
    inner += part("M-30,-4 C-18,-12 -6,4 6,-4 C10,-7 14,-6 18,-4 L18,4 C10,0 6,8 -6,6 C-18,4 -22,-2 -30,6Z", "#FFFFFF", s=None, ol=False)
    inner += part("M30,-40 L36,-40 L36,40 L30,40Z", RED, s=None, ol=False)
    o = comp(body, "#FFFFFF", inner, s=(-4, -6), ol="#7A86B8", hl=hi("M-58,-14 L-38,-15", 3, .8))
    o += ln("M-66,-18 L-66,18", "#7A86B8", "o0")
    o += part("M46,-16 L58,-11 L58,11 L46,16 Z", "#FFFFFF", s=None, ol="#7A86B8")
    o += part(rr(57, -13, 22, 26, 5), RED, s=(-2, -3))
    o += "".join(ln(f"M{x},-13 L{x},13", lin(RED), "o0") for x in (63, 68, 73))
    return g(o, "rotate(-16)")


@reg((-76, -52, 82, 34))
def shoe(col="#F2545B"):
    up = "M-66,-6 C-66,-30 -56,-46 -40,-46 L-12,-46 C-2,-46 4,-38 10,-28 L40,-18 C62,-12 76,-2 76,14 L-66,14 Z"
    o = part(up, col, s=(-7, -8), hl=hi("M-56,-20 C-54,-32 -48,-40 -40,-41", 4, .6))
    o += part("M-56,-40 C-48,-48 -26,-48 -16,-42 C-24,-34 -46,-34 -56,-40Z", "#5A2E3A", s=None)
    o += part(rr(-72, 8, 156, 18, 9), "#FFFFFF", s=(-2, -3), ol="#8E86A8")
    o += ln("M-60,17 L76,17", "#C8C2D8", "o0")
    o += part(ell(-26, -8, 13), YELLOW, s=None) + part(star_d(7, 3.2, cx=-26, cy=-8, round_=.15), "#FFFFFF", s=None, ol=False)
    for i in range(3):
        x = 0 + i * 12
        o += ln(f"M{x - 4},{-34 + i * 4} L{x + 8},{-26 + i * 4}", "#FFFFFF", "o3")
    return o


@reg((-42, -66, 42, 48))
def padlock(col=GOLD):
    o = hose_line("M-22,-8 L-22,-32 A22,22 0 0 1 22,-32 L22,-8", "#B9C0CE", 9)
    o += part(rr(-38, -14, 76, 60, 14), col, s=(-6, -7), hl=hi("M-28,-2 L-28,30", 4, .6))
    o += part("M0,2 C7,2 10,8 7,13 L11,30 L-11,30 L-7,13 C-10,8 -7,2 0,2Z", "#5A3A1A", s=None)
    return o


# ---------------------------------------------------------------- train and pattern pieces
@reg((-84, -100, 86, 48))
def engine(col="#F04A3E"):
    o = ""
    o += part("M-82,22 L-66,2 L-56,2 L-56,26 Z", YELLOW, s=None)
    o += part(rr(-74, 2, 158, 14, 5), "#4B4560", s=None)
    o += part(rr(-70, -44, 92, 48, 20), col, s=(-6, -8), hl=hi("M-56,-34 L0,-34", 5, .55))
    o += part(rr(-74, -40, 12, 40, 6), shd(col), s=None)
    o += part(ell(-74, -22, 6, 8), "#FFE066", s=None)
    o += part("M-56,-44 L-60,-70 L-34,-70 L-38,-44 Z", "#4B4560", s=(-2, -3)) + part(rr(-64, -78, 34, 10, 4), "#4B4560", s=None)
    o += part("M-14,-44 C-14,-58 6,-58 6,-44 Z", GOLD, s=None)
    o += part(rr(16, -72, 64, 76, 8), BLUE, s=(-6, -8))
    o += part(rr(10, -84, 76, 16, 7), "#2E5FB8", s=(-2, -3))
    o += part(rr(30, -60, 34, 28, 7), "#CDEEFF", s=None, ol=lin(BLUE), hl=hi("M37,-52 L44,-52", 3, .9))
    for x, r in ((-48, 15), (-14, 15), (48, 21)):
        o += part(ell(x, 24, r), "#3E3A4A", s=(-3, -3), ol="#221E2C") + part(ell(x, 24, r * .45), RED, s=None, ol="#8A1E1E")
    return o


@reg((-34, -28, 34, 30))
def wagon(col=YELLOW):
    o = part(rr(-40, -4, 8, 6, 2), "#4B4560", s=None)
    o += part(rr(-32, -10, 64, 24, 6), col, s=(-3, -4))
    o += ln("M-26,-2 L26,-2", lin(col), "o0")
    for x in (-17, 17):
        o += part(ell(x, 17, 10), "#3E3A4A", s=None, ol="#221E2C") + part(ell(x, 17, 4), "#D7D3E2", s=None, ol=False)
    return o


@reg((-44, -44, 44, 44))
def redball():
    return part(ell(0, 0, 40), "#F2463F", s=(-8, -9), hl=hi("M-26,-12 A28,28 0 0 1 -10,-28", 7, .8) + hidot(-28, 4, 3.5))


@reg((-44, -44, 44, 44))
def bluestar():
    return part(star_d(42, 20, round_=.14, cy=3), BLUE, s=(-6, -7), hl=hi("M-10,-20 L-4,-32", 5, .75))


@reg((-44, -42, 44, 42))
def greentri():
    d = "M0,-38 C5,-38 8,-35 10,-31 L40,26 C43,32 39,38 32,38 L-32,38 C-39,38 -43,32 -40,26 L-10,-31 C-8,-35 -5,-38 0,-38Z"
    return part(d, GREEN, s=(-6, -7), hl=hi("M-8,-20 L-22,8", 5, .7))


# ---------------------------------------------------------------- detective game pieces
@reg((-42, -46, 42, 14))
def tophat(col="#4A5BD8"):
    o = part("M-24,-42 C-24,-46 24,-46 24,-42 L20,0 L-20,0 Z", col, s=(-4, -5), hl=hi("M-15,-36 L-13,-6", 4, .5))
    o += part("M-21,-12 L21,-12 L20,-2 L-20,-2Z", RED, s=None)
    o += part(ell(0, 2, 38, 9), col, s=(-3, -3))
    return o


@reg((-78, -38, 78, 30))
def plate():
    o = part(ell(0, 4, 74, 24), "#FFFFFF", s=(-5, -6), ol=WHITE_OL)
    o += part(ell(0, 2, 50, 14), "#F1EEF8", s=None, ol="#C9C2DD")
    o += part("M-26,0 C-20,-6 -8,-4 -4,2 C-10,6 -22,6 -26,0Z", "#FFD3E0", s=None, ol="#E28AA8")
    for x, y, r in ((6, -2, 3.2), (16, 4, 2.4), (-8, 6, 2.2), (24, -4, 2), (-34, 4, 2.4)):
        o += part(ell(x, y, r), "#C88A54", s=None, ol=False)
    return o


def critter(kind, hat=False, crumbs=False, grey=False):
    """Suspects for 「誰拿走了蛋糕？」: rabbit, cat, bear."""
    fur = {"rabbit": "#FBF5EE", "cat": "#AAB4C6", "bear": "#B98252"}[kind]
    li = {"rabbit": "#FFFFFF", "cat": "#E9EDF4", "bear": "#EBC9A0"}[kind]
    ol = {"rabbit": "#9A8AA8", "cat": None, "bear": None}[kind]
    o = []
    if kind == "cat":
        o.append(part(tube([(30, 84, 6), (54, 70, 6), (60, 44, 6), (52, 30, 6)]), fur, s=(-2, -3)))
    # body, feet, arms
    body = "M-32,14 C-44,36 -46,70 -36,86 C-24,98 24,98 36,86 C46,70 44,36 32,14 Z"
    o.append(comp(body, fur, part(ell(0, 62, 20, 24), li, s=None, ol=ol or lin(fur)), s=(-7, -8), ol=ol))
    for sx in (-1, 1):
        o.append(part(ell(sx * 19, 94, 16, 9), fur, s=(-2, -3), ol=ol))
        o.append(part(tube([(sx * 30, 30, 8.5), (sx * 40, 50, 8), (sx * 42, 64, 8)]), fur, s=(-2, -3), ol=ol))
    # ears
    if kind == "rabbit":
        for sx in (-1, 1):
            o.append(g(part(ell(0, -96, 15, 44), fur, s=(-3, -4), ol=ol) + part(ell(0, -92, 7, 32), "#FFC2D1", s=None, ol="#E596AE"),
                       f"translate({sx * 18} 0) rotate({sx * 9} 0 -60)"))
    elif kind == "cat":
        for sx in (-1, 1):
            o.append(g(part("M-22,-50 L-6,-92 C-4,-96 0,-96 2,-92 L22,-56 Z", fur, s=(-3, -4))
                       + part("M-12,-56 L-3,-82 L10,-58 Z", "#FFC2D1", s=None, ol=False), f"translate({sx * 30} 0) rotate({sx * 8})"))
    else:
        for sx in (-1, 1):
            o.append(part(ell(sx * 40, -62, 17), fur, s=(-3, -4)) + part(ell(sx * 40, -62, 8), li, s=None, ol=False))
    # head
    hw = 56 if kind != "rabbit" else 52
    head = ell(0, -24, hw, 46)
    inner = ""
    if kind == "cat":
        inner = ln("M-10,-70 L-8,-56 M0,-72 L0,-58 M10,-70 L8,-56", shd(fur), "o2")
    o.append(comp(head, fur, inner, s=(-9, -9), ol=ol, hl=hi(f"M{-hw * .6:.0f},-52 C-24,-64 -10,-68 4,-68", 5, .55)))
    if kind == "bear":
        o.append(part(ell(0, -8, 20, 15), li, s=None, ol=lin(fur)))
    o.append(eye(-21, -26, 11, 13, .5, 1.5, ol="#4A3346"))
    o.append(eye(21, -26, 11, 13, .5, 1.5, ol="#4A3346"))
    o.append(blush(-36, -6, 8, 5) + blush(36, -6, 8, 5))
    nose = {"rabbit": "#FF8FAB", "cat": "#FF8FAB", "bear": "#3A2418"}[kind]
    o.append(part("M-6,-12 C-6,-16 6,-16 6,-12 C6,-8 2,-5 0,-5 C-2,-5 -6,-8 -6,-12Z", nose, s=None, ol=lin(nose)))
    o.append(ln("M-9,0 Q-4,5 0,-3 Q4,5 9,0", "#4A3346", "o2"))
    if kind == "rabbit":
        o.append(part("M-5,1 L5,1 L5,8 C5,10 -5,10 -5,8 Z", "#FFFFFF", s=None, ol="#9A8AA8") + ln("M0,1 L0,9", "#9A8AA8", "o0"))
    if kind == "cat":
        o.append(ln("M-24,-10 L-50,-14 M-24,-4 L-50,-2 M24,-10 L50,-14 M24,-4 L50,-2", "#6E7890", "o0"))
    if crumbs:
        o.append(part(ell(13, 6, 5, 4), "#FFD3E0", s=None, ol="#E28AA8"))
        for x, y in ((20, 12), (9, 14), (25, 3)):
            o.append(part(ell(x, y, 2.2), "#C88A54", s=None, ol=False))
    if hat:
        o.append(g(tophat(), "translate(0 -60) rotate(-6)"))
    return "".join(o)


@reg((-74, -148, 74, 104))
def rabbit(hat=False, crumbs=False):
    return critter("rabbit", hat, crumbs)


@reg((-70, -110, 74, 104))
def cat(hat=False):
    return critter("cat", hat)


@reg((-70, -100, 70, 104))
def bear(hat=False):
    return critter("bear", hat)


@reg((-92, -96, 96, 92))
def dog(bone_=True):
    fur, ear = "#F8E6C8", "#B9773F"
    o = []
    o.append(part(tube([(36, 60, 9), (62, 46, 8), (74, 20, 7)]), fur, s=(-2, -3), ol="#B98A56"))
    o.append(ln("M84,8 Q92,18 90,30 M92,-2 Q104,14 102,32", "#E0A160", "o3"))
    body = "M-34,0 C-50,30 -54,66 -44,84 L44,84 C54,66 50,30 34,0 Z"
    o.append(part(body, fur, s=(-7, -8), ol="#B98A56"))
    for sx in (-1, 1):
        o.append(part(tube([(sx * 14, 30, 9), (sx * 15, 62, 9), (sx * 16, 80, 10)]), fur, s=(-2, -3), ol="#B98A56"))
    o.append(part(rr(-30, -6, 60, 12, 6), RED, s=None) + part(ell(0, 10, 7), GOLD, s=None))
    for sx in (-1, 1):
        o.append(part(f"M{sx * 34},-74 C{sx * 62},-76 {sx * 70},-50 {sx * 64},-22 C{sx * 60},-8 {sx * 48},-12 {sx * 44},-26 C{sx * 40},-40 {sx * 36},-54 {sx * 34},-74Z",
                      ear, s=(-3, -4)))
    head = ell(0, -42, 50, 44)
    o.append(comp(head, fur, part(ell(22, -56, 18, 16), "#E8C08E", s=None, ol=False), s=(-8, -8), ol="#B98A56",
                  hl=hi("M-30,-70 C-20,-80 -6,-84 8,-83", 5, .6)))
    o.append(part(ell(0, -22, 26, 18), "#FFFFFF", s=None, ol="#B98A56"))
    o.append(happy_eye(-20, -50, 9, "#3A2418") + happy_eye(22, -50, 9, "#3A2418"))
    o.append(blush(-36, -30, 8, 5) + blush(36, -30, 8, 5))
    o.append(part("M-9,-32 C-9,-38 9,-38 9,-32 C9,-26 3,-23 0,-23 C-3,-23 -9,-26 -9,-32Z", "#3A2418", s=None, hl=hidot(-3, -33, 2)))
    if bone_:
        o.append(g(part(BONE, "#FFF0D4", s=(-4, -5), ol="#B98A56"), "translate(0 -10) scale(.95)"))
    return "".join(o)


def person(kind):
    """Grown-ups for 「這是誰的？」."""
    if kind == "fire":
        skin, coat, pants = "#A86B45", "#F4B63A", "#3E4A6B"
    else:
        skin, coat, pants = "#F8D2B4", "#FFFFFF", "#5A86D6"
    sko = "#B97B5C" if kind == "doctor" else None
    o = []
    if kind == "doctor":
        o.append(part(ell(0, -110, 18), "#2E2A3A", s=None))
    for sx in (-1, 1):
        o.append(part(rr(sx * 16 - 11, 50, 22, 44, 8), pants, s=(-3, -4)))
        o.append(part(ell(sx * 18, 96, 17, 9), "#3B3446", s=(-2, -3)))
    torso = "M-34,-20 C-40,-20 -44,-14 -44,-6 L-46,56 L46,56 L44,-6 C44,-14 40,-20 34,-20 Z"
    inner = ""
    if kind == "fire":
        inner = "".join(part(f"M-60,{y} L60,{y} L60,{y + 8} L-60,{y + 8} Z", "#E3E8F0", s=None, ol="#B9C0CE") for y in (34,))
        inner += ln("M0,-20 L0,56", lin(coat), "o2")
    else:
        inner = part("M-14,-22 L0,8 L14,-22 Z", "#8FD0FF", s=None, ol="#5A86D6") + ln("M0,8 L0,56", WHITE_OL, "o2")
        inner += part(rr(18, 16, 16, 12, 3), "#F1EEF8", s=None, ol=WHITE_OL)
    o.append(comp(torso, coat, inner, s=(-8, -9), ol=None if kind == "fire" else WHITE_OL))
    for sx in (-1, 1):
        o.append(part(tube([(sx * 38, -10, 10), (sx * 50, 14, 9.5), (sx * 54, 34, 9.5)]), coat, s=(-2, -3), ol=None if kind == "fire" else WHITE_OL))
        if kind == "fire":
            o.append(part(rr(sx * 54 - 11, 18, 22, 6, 3), "#E3E8F0", s=None, ol="#B9C0CE"))
        o.append(part(ell(sx * 55, 42, 9), skin, s=None, ol=sko))
    o.append(part(rr(-9, -32, 18, 16, 6), skin, s=None, ol=sko))
    # head
    o.append(part(ell(0, -64, 40, 38), skin, s=(-6, -7), ol=sko))
    if kind == "doctor":
        o.append(part("M-42,-60 C-46,-92 -20,-106 2,-104 C26,-104 46,-88 42,-60 C34,-76 18,-86 0,-84 C-18,-84 -32,-76 -42,-60 Z", "#2E2A3A", s=None))
    o.append(eye(-15, -60, 8, 10, .5, 1.2, ol="#3A2A30"))
    o.append(eye(15, -60, 8, 10, .5, 1.2, ol="#3A2A30"))
    o.append(blush(-26, -46, 6.5, 4) + blush(26, -46, 6.5, 4))
    o.append(ln("M-10,-42 Q0,-34 10,-42", "#6A3030", "o3"))
    if kind == "fire":
        o.append(g(helmet(), "translate(0 -94) scale(.72)"))
    return "".join(o)


@reg((-62, -150, 62, 108))
def firefighter():
    return person("fire")


@reg((-62, -130, 62, 108))
def doctor():
    return person("doctor")


# ---------------------------------------------------------------- stickers and the sticker book
@reg((-42, -42, 42, 42))
def sticker(inner="toothbrush"):
    o = ""
    if STYLE == "A":
        o += f'<circle cx="0" cy="2" r="38" fill="#5A4A70" opacity=".18"/>'
    o += part(ell(0, 0, 38), "#FFFFFF", s=None, ol=WHITE_OL)
    o += part(ell(0, 0, 31), "#FFE48A", s=(-4, -5))
    if inner:
        x0, y0, x1, y1 = BOX[inner]
        sc = 44 / max(x1 - x0, y1 - y0)
        o += f'<g transform="scale({sc:.3f}) translate({-(x0 + x1) / 2:.1f} {-(y0 + y1) / 2:.1f})">{globals()[inner]()}</g>'
    o += part("M18,26 C24,22 28,16 30,10 C24,12 18,16 18,26Z", "#E9E4F2", s=None, ol=WHITE_OL)
    return o


@reg((-54, -62, 54, 62))
def handbook(col="#2EB5A8"):
    o = part(rr(-44, -54, 96, 112, 10), "#FFF3D9", s=None, ol="#C9A77A")
    o += part(rr(-50, -60, 96, 112, 12), col, s=(-7, -8), hl=hi("M-30,-50 L20,-50", 4, .5))
    o += part(rr(-50, -60, 16, 112, 8), shd(col), s=None, ol=lin(col))
    o += part(rr(-24, -40, 58, 58, 12), "#FFFFFF", s=None, ol=lin(col))
    o += magnifier(2, -14, 15, 135, .8)
    for x, c in ((-16, YELLOW), (4, PINK), (24, "#7CC7FF")):
        o += part(star_d(8, 3.8, cx=x, cy=36, round_=.15), c, s=None)
    return o


@reg((-96, -62, 96, 62))
def openbook(filled=5):
    o = part("M0,-50 C-30,-60 -70,-58 -90,-50 L-90,54 C-70,46 -30,46 0,56 C30,46 70,46 90,54 L90,-50 C70,-58 30,-60 0,-50Z",
             "#2EB5A8", s=(-4, -5))
    o += part("M0,-46 C-28,-56 -64,-54 -84,-46 L-84,46 C-64,40 -28,40 0,50 Z", "#FFFBF2", s=None, ol="#C9A77A")
    o += part("M0,-46 C28,-56 64,-54 84,-46 L84,46 C64,40 28,40 0,50 Z", "#FFFBF2", s=None, ol="#C9A77A")
    slots = [(-62, -22), (-30, -22), (-62, 14), (-30, 14), (30, -22), (62, -22), (30, 14), (62, 14)]
    cols = [YELLOW, PINK, "#7CC7FF", GREEN, "#FFB066"]
    for i, (x, y) in enumerate(slots):
        if i < filled:
            o += part(ell(x, y, 13), cols[i % len(cols)], s=(-2, -2.5), ol=lin(cols[i % len(cols)]))
            o += part(star_d(6, 2.8, cx=x, cy=y, round_=.15), "#FFFFFF", s=None, ol=False)
        else:
            o += f'<circle cx="{x}" cy="{y}" r="13" fill="none" stroke="#D9C9AA" stroke-width="2" stroke-dasharray="4 3"/>'
    return o


# ================================================================ PAGE MACHINERY
def tx(x, y, s, size=16, color=INK, anchor="middle", extra="", weight=""):
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}"{w} '
            f'font-family="Huninn, sans-serif" {extra}>{s}</text>')


def txo(x, y, s, size, color, ol="#FFFFFF", ow=6, anchor="middle"):
    """Words with a soft outline around them (titles on pictures)."""
    return tx(x, y, s, size, color, anchor, f'stroke="{ol}" stroke-width="{ow}" stroke-linejoin="round" paint-order="stroke"')


def place(name, cx, cy, w, h, maxs=99.0, flip=False, sw=None, rot=0, **kw):
    """Draw `name` scaled to fit a w x h box centred on (cx, cy). sw: outline width on screen."""
    global SCALE
    x0, y0, x1, y1 = BOX[name]
    s = min(w / (x1 - x0), h / (y1 - y0), maxs)
    SCALE = s
    svg = globals()[name](**kw)
    SCALE = 1.0
    fx = -1 if flip else 1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    st = f' style="--sw:{sw}px"' if sw else ""
    r = f" rotate({rot})" if rot else ""
    return (f'<g transform="translate({cx:.2f} {cy:.2f}){r} scale({fx * s:.4f} {s:.4f}) translate({-mx:.2f} {-my:.2f})"{st}>{svg}</g>')


CSS_LINES = (".o{vector-effect:non-scaling-stroke;stroke-width:var(--sw,2.2px)}"
             ".o0{vector-effect:non-scaling-stroke;stroke-width:calc(var(--sw,2.2px)*.62)}"
             ".o2{vector-effect:non-scaling-stroke;stroke-width:calc(var(--sw,2.2px)*.9)}"
             ".o3{vector-effect:non-scaling-stroke;stroke-width:calc(var(--sw,2.2px)*1.35)}"
             ".o4{vector-effect:non-scaling-stroke;stroke-width:calc(var(--sw,2.2px)*2.2)}")


def page(body, bg, w=W, h=H):
    css = (f"@font-face {{ font-family: Huninn; src: url('file://{FONT}'); }}"
           f"* {{ margin: 0; padding: 0; }} body {{ width: {w}px; height: {h}px; overflow: hidden; background: {bg}; }}" + CSS_LINES)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{D.svg()}{body}</svg>'
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{svg}</body></html>'


def render(html, out, w, h, scale):
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp) / "page.html"
        p.write_text(html)
        subprocess.run(["node", str(HERE / "render.js"), str(p), str(out), str(w), str(h), str(scale)], check=True)


def items_sheet(names=None, style="A"):
    global STYLE
    STYLE = style
    names = names or list(BOX)
    cols, cw, ch = 5, 240, 220
    rows = (len(names) + cols - 1) // cols
    o = []
    for i, n in enumerate(names):
        x, y = 16 + (i % cols) * (cw + 16), 16 + (i // cols) * (ch + 16)
        o.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="20" fill="#FFFFFF" stroke="#E4DEEE"/>')
        o.append(place(n, x + cw / 2, y + ch / 2 - 8, cw - 40, ch - 56))
        o.append(tx(x + cw / 2, y + ch - 12, n, 15, SOFT))
    STYLE = "A"
    w, h = 16 + cols * (cw + 16), 16 + rows * (ch + 16)
    return page("".join(o), "#F6F2FB", w, h), w, h


# ================================================================ UI PIECES (style A)
UI_OL = "#5B4A78"      # outline of white UI things
PANEL_LIP = "#D9CFEA"


def ghost(name, cx, cy, w, h, **kw):
    global GHOST
    GHOST = True
    out = place(name, cx, cy, w, h, **kw)
    GHOST = False
    return out


def lipbox(x, y, w, h, r, fill="#FFFFFF", ol=None, lip=None, lipd=5, sw=2.2, extra=""):
    """A rounded box with a hard 'lip' under it (cartoon game UI)."""
    ol = ol or (UI_OL if fill == "#FFFFFF" else lin(fill))
    lip = lip or (PANEL_LIP if fill == "#FFFFFF" else shd(shd(fill)))
    return (f'<path d="{rr(x, y + lipd, w, h, r)}" fill="{lip}" stroke="{ol}" stroke-width="{sw}" stroke-opacity=".9"/>'
            f'<path d="{rr(x, y, w, h, r)}" fill="{fill}" stroke="{ol}" stroke-width="{sw}" {extra}/>')


def roundbtn(cx, cy, r, fill, icon="", lipd=4):
    ol = UI_OL if fill == "#FFFFFF" else lin(fill)
    lip = PANEL_LIP if fill == "#FFFFFF" else shd(shd(fill))
    o = f'<circle cx="{cx}" cy="{cy + lipd}" r="{r}" fill="{lip}" stroke="{ol}" stroke-width="2.2"/>'
    o += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{ol}" stroke-width="2.2"/>'
    if fill != "#FFFFFF":
        o += f'<path d="M{cx - r * .62:.1f},{cy - r * .3:.1f} A{r * .7:.1f},{r * .7:.1f} 0 0 1 {cx - r * .2:.1f},{cy - r * .66:.1f}" stroke="#FFFFFF" stroke-width="{r * .14:.1f}" fill="none" stroke-linecap="round" opacity=".55"/>'
    return o + icon


def bubble_d(x, y, w, h, r, side=None, at=0, tl=16, tw=13):
    x1, y1 = x + w, y + h
    d = f"M{x + r},{y}"
    if side == "up":
        d += f" L{at - tw},{y} L{at - 3},{y - tl} L{at + tw},{y}"
    d += f" L{x1 - r},{y} A{r},{r} 0 0 1 {x1},{y + r}"
    if side == "right":
        d += f" L{x1},{at - tw} L{x1 + tl},{at + 3} L{x1},{at + tw}"
    d += f" L{x1},{y1 - r} A{r},{r} 0 0 1 {x1 - r},{y1}"
    if side == "down":
        d += f" L{at + tw},{y1} L{at - 4},{y1 + tl} L{at - tw},{y1}"
    d += f" L{x + r},{y1} A{r},{r} 0 0 1 {x},{y1 - r}"
    if side == "left":
        d += f" L{x},{at + tw} L{x - tl},{at + 3} L{x},{at - tw}"
    d += f" L{x},{y + r} A{r},{r} 0 0 1 {x + r},{y}Z"
    return d


def bubble(x, y, w, h, r=26, side=None, at=0, fill="#FFFFFF", ol=UI_OL):
    d = bubble_d(x, y, w, h, r, side, at)
    return (f'<path d="{d}" fill="{PANEL_LIP}" stroke="{ol}" stroke-width="2.2" transform="translate(0 5)"/>'
            f'<path d="{d}" fill="{fill}" stroke="{ol}" stroke-width="2.2"/>')


def i_speaker(c="#FFFFFF"):
    return (f'<g transform="translate(-2 0)"><path d="M-12,-5 L-6,-5 L2,-12 L2,12 L-6,5 L-12,5Z" fill="{c}" stroke="{c}" stroke-width="3" stroke-linejoin="round"/>'
            f'<path d="M7.5,-6 A9,9 0 0 1 7.5,6 M11.5,-11 A15,15 0 0 1 11.5,11" stroke="{c}" stroke-width="2.8" fill="none" stroke-linecap="round"/></g>')


def i_home(c):
    return (f'<path d="M-13,-1 L0,-13 L13,-1" stroke="{c}" stroke-width="3.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M-9,-2 L-9,11 L-3,11 L-3,4 L3,4 L3,11 L9,11 L9,-2" fill="{c}" stroke="{c}" stroke-width="2" stroke-linejoin="round"/>')


def i_lock(c):
    return (f'<path d="M-5.5,-2 V-6 A5.5,5.5 0 0 1 5.5,-6 V-2" stroke="{c}" stroke-width="2.6" fill="none"/>'
            f'<rect x="-8.5" y="-2.5" width="17" height="13" rx="3" fill="{c}"/>')


def i_check(c="#FFFFFF", w=4.5):
    return f'<path d="M-9,0 L-3,7 L10,-7" stroke="{c}" stroke-width="{w}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'


def i_arrow(c="#FFFFFF", w=4):
    return f'<path d="M-10,0 L9,0 M1,-9 L10,0 L1,9" stroke="{c}" stroke-width="{w}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'


def i_x(c, w=3):
    return f'<path d="M-8,-8 L8,8 M8,-8 L-8,8" stroke="{c}" stroke-width="{w}" stroke-linecap="round"/>'


def ic(inner, cx, cy, s=1.0):
    return f'<g transform="translate({cx} {cy}) scale({s})">{inner}</g>'


def star_icon(cx, cy, R, on=True):
    d = star_d(R, R * .48, cx=cx, cy=cy, round_=.16)
    if on:
        return (f'<path d="{d}" fill="{GOLD}" stroke="#C98A0E" stroke-width="2" stroke-linejoin="round"/>'
                f'<path d="{d}" fill="#E8A417" mask="{cel_mask(d, (-R * .14, -R * .18))}"/>'
                f'<path d="{d}" fill="none" stroke="#C98A0E" stroke-width="2" stroke-linejoin="round"/>')
    return f'<path d="{d}" fill="#ECE7F5" stroke="#C9C0DE" stroke-width="2" stroke-linejoin="round"/>'


def sparkle(cx, cy, r, c=GOLD, op=1.0):
    return (f'<path d="M{cx},{cy - r} Q{cx + r * .16},{cy - r * .16} {cx + r},{cy} Q{cx + r * .16},{cy + r * .16} {cx},{cy + r} '
            f'Q{cx - r * .16},{cy + r * .16} {cx - r},{cy} Q{cx - r * .16},{cy - r * .16} {cx},{cy - r}Z" fill="{c}" opacity="{op}"/>')


def dots(cx, y, n, k, on=FOX, r=6, gap=20):
    """Progress: k done (filled), the current one bigger, the rest pale."""
    x0 = cx - (n - 1) * gap / 2
    o = []
    for i in range(n):
        x = x0 + i * gap
        if i < k:
            o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{on}" stroke="{lin(on)}" stroke-width="2"/>')
        elif i == k:
            o.append(f'<circle cx="{x}" cy="{y}" r="{r + 2.5}" fill="#FFFFFF" stroke="{on}" stroke-width="3"/>')
        else:
            o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#FFFFFF" stroke="#CFC6E0" stroke-width="2"/>')
    return "".join(o)


def finger(cx, cy, r=24):
    """Where the child's finger is: a soft see-through white circle."""
    return (f'<circle cx="{cx}" cy="{cy + 2}" r="{r + 2}" fill="#5B4A78" opacity=".12"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#FFFFFF" opacity=".55"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#FFFFFF" stroke-width="3" opacity=".95"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r + 1.5}" fill="none" stroke="#8E86A8" stroke-width="1" opacity=".55"/>')


def header(title, col=FOX, home=True):
    o = ""
    if home:
        o += roundbtn(40, 46, 24, "#FFFFFF", ic(i_home(UI_OL), 40, 46, .95))
    w = len(title) * 22 + 44
    o += lipbox(195 - w / 2, 26, w, 42, 21, col, lipd=4)
    o += tx(195, 55, title, 22, "#FFFFFF", extra=f'stroke="{lin(col)}" stroke-width="3" paint-order="stroke" stroke-linejoin="round"')
    return o


def ask(y, text, size=24, col=TEAL, x=20, w=350, h=72, side=None, at=0):
    """The spoken question: a bubble with a speaker button."""
    o = bubble(x, y, w, h, 28, side, at)
    o += roundbtn(x + 38, y + h / 2, 23, col, ic(i_speaker(), x + 38, y + h / 2, .95), lipd=3)
    o += tx(x + 72, y + h / 2 + size * .36, text, size, INK, "start")
    return o


def check_badge(cx, cy, r=18, col="#3CC46A"):
    return roundbtn(cx, cy, r, col, ic(i_check(), cx, cy, r / 18), lipd=3)


def cloud_d(cx, cy, s=1.0):
    return (f"M{cx - 40 * s},{cy + 12 * s} C{cx - 56 * s},{cy + 12 * s} {cx - 56 * s},{cy - 8 * s} {cx - 40 * s},{cy - 10 * s} "
            f"C{cx - 38 * s},{cy - 28 * s} {cx - 14 * s},{cy - 32 * s} {cx - 6 * s},{cy - 18 * s} C{cx + 2 * s},{cy - 34 * s} {cx + 32 * s},{cy - 32 * s} {cx + 34 * s},{cy - 10 * s} "
            f"C{cx + 52 * s},{cy - 10 * s} {cx + 54 * s},{cy + 12 * s} {cx + 38 * s},{cy + 12 * s} Z")


# ================================================================ PAGE 0: the three styles
# style C: built again from circles, squares, triangles and rounded rectangles (flat, no outlines)
C_OR, C_DK, C_CR, C_BR = "#FF7A2F", "#2B2D42", "#FFF4E2", "#8C5A3C"


def cap_(x0, y0, x1, y1, r, col):
    """A capsule (rounded bar) from (x0, y0) to (x1, y1)."""
    return f'<path d="M{x0},{y0} L{x1},{y1}" stroke="{col}" stroke-width="{2 * r}" stroke-linecap="round"/>'


def c_fox():
    o = []
    o.append(f'<path d="M24,94 A66,66 0 0 1 108,-2 A66,66 0 0 1 24,94Z" fill="{C_OR}"/>')          # tail: a lens of two circles
    o.append(f'<path d="M86,22 A22,22 0 0 1 108,-2 A22,22 0 0 1 86,22Z" fill="{C_CR}"/>')
    o.append(cap_(-30, 34, -58, 56, 11, C_OR) + cap_(-62, 52, -76, 34, 6, C_BR))                       # arm + handle
    o.append(f'<circle cx="-88" cy="18" r="21" fill="#FFC21F"/><circle cx="-88" cy="18" r="13" fill="#CFEFFF"/>'
             f'<circle cx="-93" cy="13" r="4" fill="#FFFFFF"/>')
    o.append(f'<rect x="-38" y="12" width="76" height="86" rx="30" fill="{C_OR}"/><circle cx="0" cy="64" r="24" fill="{C_CR}"/>')
    o.append(f'<rect x="-38" y="90" width="32" height="16" rx="8" fill="{C_DK}"/><rect x="6" y="90" width="32" height="16" rx="8" fill="{C_DK}"/>')
    o.append(cap_(32, 32, 62, -16, 11, C_OR) + f'<circle cx="66" cy="-24" r="12" fill="{C_DK}"/>')
    for sx in (-1, 1):
        o.append(f'<path d="M{sx * 52},-80 L{sx * 70},-144 L{sx * 12},-100Z" fill="{C_OR}" stroke="{C_OR}" stroke-width="10" stroke-linejoin="round"/>')
        o.append(f'<path d="M{sx * 70},-144 L{sx * 63},-118 L{sx * 52},-127Z" fill="{C_DK}" stroke="{C_DK}" stroke-width="7" stroke-linejoin="round"/>')
    o.append(f'<circle cx="0" cy="-40" r="60" fill="{C_OR}"/>')
    o.append(f'<circle cx="-26" cy="-12" r="31" fill="{C_CR}"/><circle cx="26" cy="-12" r="31" fill="{C_CR}"/>')
    o.append(f'<circle cx="0" cy="-24" r="9" fill="{C_DK}"/><path d="M-9,-8 A9,9 0 0 0 9,-8Z" fill="#E5484D"/>')
    for x in (-24, 24):
        o.append(f'<circle cx="{x}" cy="-50" r="11" fill="{C_DK}"/><circle cx="{x - 4}" cy="-54" r="4" fill="#FFFFFF"/>')
    o.append(f'<circle cx="-46" cy="-26" r="7" fill="#FF9E9E"/><circle cx="46" cy="-26" r="7" fill="#FF9E9E"/>')
    o.append(f'<path d="M-46,-84 A46,42 0 0 1 46,-84Z" fill="{C_BR}"/><rect x="-58" y="-92" width="116" height="12" rx="6" fill="#6B4129"/>'
             f'<circle cx="0" cy="-128" r="7" fill="#6B4129"/><rect x="-46" y="-104" width="92" height="7" fill="#A87553"/>')
    return "".join(o)


def c_toothbrush():
    return ('<g transform="rotate(-28)">'
            f'<rect x="-92" y="-8" width="190" height="22" rx="11" fill="#2EC4B6"/>'
            f'<rect x="-56" y="-3" width="34" height="12" rx="6" fill="#FF5D8F"/>'
            + "".join(f'<rect x="{x}" y="-40" width="9" height="32" rx="4.5" fill="#FFFFFF"/><rect x="{x}" y="-40" width="9" height="13" rx="4.5" fill="#3A86FF"/>'
                      for x in (46, 58, 70, 82)) + '</g>')


def c_goldfish():
    return (f'<path d="M48,0 L100,-38 L100,38Z" fill="#FFBF1F"/>'
            f'<path d="M-10,-40 L34,-40 L10,-70Z" fill="#FFBF1F"/>'
            f'<ellipse cx="-6" cy="0" rx="72" ry="48" fill="#FF7A2F"/>'
            f'<path d="M-6,0 L44,0 A50,48 0 0 1 -6,48Z" fill="#FF9F43"/>'
            f'<path d="M0,14 L28,14 L14,36Z" fill="#FFBF1F"/>'
            f'<circle cx="-40" cy="-10" r="13" fill="#FFFFFF"/><circle cx="-43" cy="-10" r="8" fill="{C_DK}"/><circle cx="-46" cy="-13" r="3" fill="#FFFFFF"/>'
            f'<circle cx="-92" cy="-46" r="7" fill="#7FD4F5"/><circle cx="-100" cy="-68" r="4.5" fill="#7FD4F5"/>')


def c_apple():
    return (f'<rect x="-4" y="-92" width="9" height="34" rx="4.5" fill="{C_BR}" transform="rotate(12 0 -60)"/>'
            f'<path d="M6,-72 A30,30 0 0 1 48,-90 A30,30 0 0 1 6,-72Z" fill="#2EC46A"/>'
            f'<circle cx="-30" cy="-6" r="50" fill="#EF233C"/><circle cx="30" cy="-6" r="50" fill="#EF233C"/>'
            f'<rect x="-46" y="0" width="92" height="66" rx="30" fill="#EF233C"/>'
            f'<rect x="-50" y="-34" width="14" height="30" rx="7" fill="#FF8A8A"/>')


def c_toybox():
    return (f'<rect x="-72" y="-46" width="144" height="16" rx="6" fill="#2563D8" transform="rotate(-24 -72 -32)"/>'
            f'<circle cx="-28" cy="-40" r="26" fill="#EF233C"/>'
            f'<rect x="4" y="-62" width="38" height="38" rx="4" fill="#FFBF1F" transform="rotate(12 23 -43)"/>'
            f'<path d="M40,-30 L54,-66 L68,-30Z" fill="#2EC46A"/>'
            f'<rect x="-72" y="-32" width="144" height="96" rx="10" fill="#3A86FF"/>'
            f'<rect x="-72" y="-32" width="144" height="18" fill="#FFBF1F"/>'
            f'<circle cx="0" cy="22" r="18" fill="#FFFFFF"/><rect x="-50" y="14" width="16" height="16" fill="#FFFFFF" transform="rotate(45 -42 22)"/>'
            f'<path d="M36,32 L44,12 L52,32Z" fill="#FFFFFF"/>')


C_ITEMS = {"fox": (c_fox, (-112, -150, 112, 108)), "toothbrush": (c_toothbrush, (-96, -66, 98, 50)),
           "goldfish": (c_goldfish, (-108, -76, 102, 52)), "apple": (c_apple, (-82, -96, 82, 68)),
           "toybox": (c_toybox, (-76, -104, 76, 66))}


def place_c(name, cx, cy, w, h):
    f, (x0, y0, x1, y1) = C_ITEMS[name]
    s = min(w / (x1 - x0), h / (y1 - y0))
    return f'<g transform="translate({cx} {cy}) scale({s:.4f}) translate({-(x0 + x1) / 2} {-(y0 + y1) / 2})">{f()}</g>'


def style_sheet():
    global STYLE
    PH = 1264
    o = [f'<rect width="{W}" height="{PH}" fill="#F4F0FA"/>']
    o.append(tx(195, 52, "選一個畫風", 30, INK))
    o.append(tx(195, 82, "同一組東西，三種卡通畫法", 16, SOFT))
    bands = [("A", "A 動畫片風（建議）", ["細細的彩色框線、亮亮的平塗顏色，", "一塊清楚的陰影和大眼睛，像兒童卡通。"], "#E4F4FF", "#FFF7E8"),
             ("B", "B 剪紙拼貼風", ["像彩色紙一層層剪下來貼上，", "邊緣不太整齊，有紙紋和小小的陰影。"], "#F3E6D3", "#EADAC2"),
             ("C", "C 幾何積木風", ["用圓形、方形、三角形拼出來，", "沒有框線、顏色飽滿，乾淨又現代。"], "#EEF0FF", "#FFFFFF")]
    y = 104
    for key, title, desc, c1, c2 in bands:
        h = 368
        o.append(f'<rect x="14" y="{y}" width="362" height="{h}" rx="26" fill="#FFFFFF" stroke="#E2DAF0" stroke-width="1.5" filter="{drop(.10, 4, 8)}"/>')
        o.append(tx(34, y + 40, title, 23, INK, "start"))
        if key == "A":
            o.append(f'<rect x="14" y="{y}" width="362" height="{h}" rx="26" fill="none" stroke="{FOX}" stroke-width="3"/>')
        for i, line in enumerate(desc):
            o.append(tx(34, y + 68 + i * 22, line, 15, "#6E6284", "start"))
        ay, ah = y + 112, h - 126
        if key == "B":
            bg = (f'<rect x="28" y="{ay}" width="334" height="{ah}" rx="18" fill="{c1}"/>'
                  f'<rect x="28" y="{ay}" width="334" height="{ah}" rx="18" fill="#FFFFFF" opacity=".35" filter="{paper_bg()}"/>')
        elif key == "C":
            dots_ = "".join(f'<circle cx="{x}" cy="{yy}" r="1.6" fill="#C9CCF2"/>' for x in range(40, 360, 16) for yy in range(ay + 10, ay + ah, 16))
            bg = f'<rect x="28" y="{ay}" width="334" height="{ah}" rx="18" fill="{c1}"/>{dots_}'
        else:
            bg = f'<rect x="28" y="{ay}" width="334" height="{ah}" rx="18" fill="{lg([(0, c1), (1, c2)])}"/>'
        o.append(bg)
        fx, fy = 104, ay + ah / 2
        spots = [(232, ay + 58, "toothbrush"), (318, ay + 58, "goldfish"), (232, ay + ah - 56, "apple"), (318, ay + ah - 56, "toybox")]
        if key == "C":
            o.append(place_c("fox", fx, fy, 150, ah - 24))
            for sx, sy, n in spots:
                o.append(place_c(n, sx, sy, 78, 92))
        else:
            STYLE = key
            o.append(place("fox", fx, fy, 150, ah - 24, look=(2, 2.5)))
            for sx, sy, n in spots:
                o.append(place(n, sx, sy, 78, 92))
            STYLE = "A"
        y += h + 16
    return page("".join(o), "#F4F0FA", W, PH), PH


def paper_bg():
    k = "pbg"
    D.add(k, '<filter id="pbg" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".8 .25" numOctaves="3" seed="2"/>'
             '<feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 -1.6 1.05"/>'
             '<feComposite in2="SourceGraphic" operator="in"/></filter>')
    return "url(#pbg)"


# ================================================================ SCREENS (style A)
def soft_clouds(spec, op=.85):
    return "".join(f'<path d="{cloud_d(x, y, s)}" fill="#FFFFFF" opacity="{op}"/>' for x, y, s in spec)


# ---------------------------------------------------------------- 1 hub
def tile_icon_room(cx, cy):
    return (place("toybox", cx + 2, cy - 6, 62, 60) + place("sock", cx - 34, cy + 22, 34, 36, rot=-12)
            + place("ball", cx + 36, cy + 24, 26, 26))


def tile_icon_whose(cx, cy):
    return place("helmet", cx - 12, cy - 12, 70, 52) + place("bone", cx + 16, cy + 26, 58, 26, rot=-14)


def tile_icon_link(cx, cy):
    d = f"M{cx - 28},{cy - 16} C{cx - 6},{cy - 30} {cx - 2},{cy + 20} {cx + 28},{cy + 14}"
    return (f'<path d="{d}" stroke="{lin(BLUE)}" stroke-width="9" fill="none" stroke-linecap="round"/>'
            f'<path d="{d}" stroke="{BLUE}" stroke-width="5.5" fill="none" stroke-linecap="round"/>'
            + "".join(f'<circle cx="{x}" cy="{y}" r="12" fill="{c}" stroke="{lin(c)}" stroke-width="2.2"/><circle cx="{x}" cy="{y}" r="4.5" fill="#FFFFFF"/>'
                      for x, y, c in ((cx - 28, cy - 16, PINK), (cx + 28, cy + 14, YELLOW))))


def tile_icon_odd(cx, cy):
    o = ""
    for (dx, dy) in ((-19, -18), (19, -18), (-19, 20)):
        o += place("apple", cx + dx, cy + dy, 32, 34, sw=1.6)
    o += f'<circle cx="{cx + 19}" cy="{cy + 20}" r="19" fill="#FFF3C4" stroke="{GOLD}" stroke-width="2.5"/>'
    o += place("toycar", cx + 19, cy + 20, 34, 24, sw=1.5)
    return o


def tile_icon_train(cx, cy):
    o = place("engine", cx - 52, cy + 2, 70, 62, sw=1.8)
    for i, (c, cargo) in enumerate(((YELLOW, "redball"), (GREEN, "bluestar"), (PINK, "redball"))):
        x = cx - 2 + i * 38
        o += place(cargo, x, cy + 1, 24, 24, sw=1.6) + place("wagon", x, cy + 21, 36, 30, sw=1.6, col=c)
    return o


def screen_hub():
    o = [f'<rect width="{W}" height="{H}" fill="{lg([(0, "#D7EEFF"), (.55, "#EAF5FF"), (1, "#FFF3DF")])}"/>']
    o.append(soft_clouds([(70, 40, .7), (300, 116, .55), (350, 30, .45)], .8))
    # parents (grey, small) top-right
    o.append(f'<rect x="300" y="18" width="74" height="34" rx="17" fill="#ECEEF3" stroke="#C9CDD6" stroke-width="1.5"/>'
             + ic(i_lock("#9AA0AE"), 320, 35, .85) + tx(350, 41, "家長", 15, "#8D93A1"))
    # title
    t = "動腦小偵探"
    o.append(tx(195, 104, t, 42, "#BFD9F2", extra='stroke="#BFD9F2" stroke-width="10" stroke-linejoin="round" paint-order="stroke"'))
    o.append(tx(195, 100, t, 42, FOX, extra='stroke="#FFFFFF" stroke-width="10" stroke-linejoin="round" paint-order="stroke"'))
    o.append(tx(195, 100, t, 42, FOX, extra=f'stroke="{lin(FOX)}" stroke-width="2.5" stroke-linejoin="round" paint-order="stroke"'))
    # 阿布 + bubble
    o.append(f'<ellipse cx="104" cy="290" rx="62" ry="9" fill="#9DB8D6" opacity=".35"/>')
    o.append(place("fox", 106, 206, 168, 168))
    o.append(bubble(198, 150, 172, 74, 26, "left", 196))
    o.append(tx(284, 183, "今天想玩", 20, INK) + tx(284, 209, "哪一個呢？", 20, INK))
    # five game tiles
    tiles = [("放哪裡？", "#FFB066", tile_icon_room, 2), ("是誰的？", "#FF8A8A", tile_icon_whose, 1),
             ("連連看", "#6FB6FF", tile_icon_link, 3), ("哪個不一樣？", "#63CF7A", tile_icon_odd, 2)]
    for i, (name, col, icon, stars) in enumerate(tiles):
        x, y = 22 + (i % 2) * 180, 306 + (i // 2) * 162
        o.append(lipbox(x, y, 166, 146, 28, "#FFFFFF", lin(col), lt(col, .35), 6))
        o.append(f'<circle cx="{x + 83}" cy="{y + 56}" r="44" fill="{lt(col, .72)}"/>')
        o.append(icon(x + 83, y + 56))
        o.append(tx(x + 83, y + 120, name, 19, INK))
        o.append("".join(star_icon(x + 83 + (k - 1) * 22, y + 135, 7.5, k < stars) for k in range(3)))
    x, y, col = 22, 630, "#B48CF5"
    o.append(lipbox(x, y, 346, 116, 28, "#FFFFFF", lin(col), lt(col, .35), 6))
    o.append(f'<rect x="{x + 12}" y="{y + 12}" width="176" height="92" rx="20" fill="{lt(col, .75)}"/>')
    o.append(f'<path d="M{x + 16},{y + 86} L{x + 184},{y + 86}" stroke="#B9A6D6" stroke-width="3" stroke-linecap="round"/>')
    o.append(tile_icon_train(x + 104, y + 58))
    o.append(tx(x + 266, y + 56, "接下來", 20, INK) + tx(x + 266, y + 80, "是什麼？", 20, INK))
    o.append("".join(star_icon(x + 266 + (k - 1) * 22, y + 99, 7.5, k < 1) for k in range(3)))
    # sticker book
    o.append(lipbox(110, 770, 170, 50, 25, "#2EB5A8", lipd=5))
    o.append(place("handbook", 140, 793, 34, 40, sw=1.6))
    o.append(tx(214, 802, "偵探手冊", 20, "#FFFFFF", extra=f'stroke="{lin("#2EB5A8")}" stroke-width="3" paint-order="stroke" stroke-linejoin="round"'))
    return page("".join(o), "#EAF5FF")


# ---------------------------------------------------------------- 2 put it back
def arrow_head(e, frm, col, size=13, w=5.5):
    ux, uy = e[0] - frm[0], e[1] - frm[1]
    l_ = math.hypot(ux, uy)
    ux, uy = ux / l_, uy / l_
    px, py = -uy, ux
    a = (e[0] - ux * size + px * size * .75, e[1] - uy * size + py * size * .75)
    b = (e[0] - ux * size - px * size * .75, e[1] - uy * size - py * size * .75)
    return (f'<path d="M{a[0]:.1f},{a[1]:.1f} L{e[0]},{e[1]} L{b[0]:.1f},{b[1]:.1f}" stroke="{col}" stroke-width="{w}" fill="none" '
            'stroke-linecap="round" stroke-linejoin="round"/>')


def screen_room():
    o = []
    wall, floor = "#FFF1D2", "#F2C892"
    o.append(f'<rect width="{W}" height="{H}" fill="{wall}"/>')
    o.append("".join(f'<rect x="{x}" y="0" width="14" height="548" fill="#FFE8BE" opacity=".7"/>' for x in range(10, 390, 40)))
    o.append(f'<rect x="0" y="540" width="{W}" height="{H - 540}" fill="{floor}"/>')
    o.append("".join(f'<path d="M0,{y} L390,{y}" stroke="#E3B47C" stroke-width="2"/>' for y in (600, 672, 752)))
    o.append("".join(f'<path d="M{x},{y0} L{x},{y1}" stroke="#E3B47C" stroke-width="2"/>' for x, y0, y1 in
                     ((120, 540, 600), (300, 540, 600), (60, 600, 672), (250, 600, 672), (170, 672, 752), (340, 672, 752), (90, 752, 844), (280, 752, 844))))
    o.append(f'<rect x="0" y="532" width="{W}" height="12" fill="#FFFFFF" stroke="#E3C9A0" stroke-width="1.5"/>')
    # window
    o.append(f'<rect x="186" y="214" width="120" height="104" rx="14" fill="#FFFFFF" stroke="{UI_OL}" stroke-width="2.2"/>'
             f'<rect x="196" y="224" width="100" height="84" rx="8" fill="#BFE7FF" stroke="#8BB8D9" stroke-width="1.5"/>'
             f'<path d="{cloud_d(234, 262, .42)}" fill="#FFFFFF"/><circle cx="276" cy="244" r="9" fill="{YELLOW}" stroke="{lin(YELLOW)}" stroke-width="1.6"/>'
             f'<path d="M246,224 L246,308 M196,266 L296,266" stroke="#FFFFFF" stroke-width="5"/>'
             f'<path d="M178,206 C178,240 186,300 172,330 L198,330 C204,290 200,240 204,206Z" fill="#FF9FB8" stroke="{lin("#FF9FB8")}" stroke-width="2"/>'
             f'<path d="M314,206 C314,240 306,300 320,330 L294,330 C288,290 292,240 288,206Z" fill="#FF9FB8" stroke="{lin("#FF9FB8")}" stroke-width="2"/>'
             f'<rect x="170" y="200" width="152" height="9" rx="4.5" fill="#C9834F" stroke="{lin("#C9834F")}" stroke-width="1.8"/>')
    # where things live
    o.append(place("bookshelf", 70, 420, 112, 262))
    o.append(place("bed", 274, 500, 192, 140))
    o.append(f'<ellipse cx="78" cy="704" rx="62" ry="9" fill="#C99A62" opacity=".45"/>')
    o.append(place("toybox", 78, 642, 122, 120))
    o.append(f'<ellipse cx="318" cy="708" rx="54" ry="8" fill="#C99A62" opacity=".45"/>')
    o.append(place("basket", 318, 650, 112, 112))
    # things on the floor
    o.append(place("teddy", 170, 596, 64, 70))
    o.append(place("picturebook", 64, 762, 92, 72, rot=-8))
    o.append(place("tshirt", 164, 764, 78, 66, rot=6))
    o.append(place("ball", 246, 770, 46, 46))
    o.append(place("toycar", 324, 772, 92, 48, col=GREEN))
    # the sock being dragged, a dotted path to the basket
    o.append(f'<ellipse cx="206" cy="722" rx="28" ry="6" fill="#B98A52" opacity=".35"/>')
    o.append(f'<path d="M240,648 C244,592 292,560 314,588" stroke="{FOX}" stroke-width="6" fill="none" stroke-linecap="round" stroke-dasharray="0.1 13"/>')
    o.append(arrow_head((314, 590), (292, 560), FOX))
    o.append(place("sock", 216, 680, 68, 74, rot=-14))
    o.append(finger(198, 650, 19))
    # header + question
    o.append(header("把東西放回家", "#FF9F4A"))
    o.append(ask(90, "襪子要放哪裡呢？", 24))
    o.append(f'<rect x="125" y="811" width="140" height="26" rx="13" fill="#FFFFFF" opacity=".6"/>' + dots(195, 824, 6, 2))
    return page("".join(o), wall)


# ---------------------------------------------------------------- 3 whose is it?
def thought(cx, cy, r, tail_to):
    tx_, ty_ = tail_to
    o = f'<circle cx="{cx}" cy="{cy + 4}" r="{r}" fill="{PANEL_LIP}" stroke="{UI_OL}" stroke-width="2.2"/>'
    o += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#FFFFFF" stroke="{UI_OL}" stroke-width="2.2"/>'
    for t, rr_ in ((.45, 7), (.8, 4.5)):
        x = cx + (tx_ - cx) * t
        y = cy + r * .9 + (ty_ - cy - r * .9) * t
        o += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr_}" fill="#FFFFFF" stroke="{UI_OL}" stroke-width="2"/>'
    return o


def screen_whose():
    o = [f'<rect width="{W}" height="{H}" fill="{lg([(0, "#E3F7EC"), (1, "#F2FBF5")])}"/>']
    o.append(f'<rect x="0" y="520" width="{W}" height="{H - 520}" fill="{lg([(0, "#CDEBD6"), (.3, "#DDF3E3"), (1, "#E9F8EE")])}"/>')
    o.append(f'<path d="M0,520 L390,520" stroke="#A9D7B6" stroke-width="2"/>')
    o.append(header("這是誰的？", "#FF7F7F"))
    o.append(ask(90, "聽診器是誰的？", 24))
    # three who need something
    o.append(thought(72, 236, 46, (66, 330)))
    o.append(ghost("hose", 72, 236, 66, 58))
    o.append(thought(198, 236, 46, (196, 330)))
    o.append(ghost("stethoscope", 198, 238, 60, 70))
    for x in (72, 198, 320):
        o.append(f'<ellipse cx="{x}" cy="530" rx="46" ry="8" fill="#8CC79E" opacity=".45"/>')
    o.append(place("firefighter", 72, 428, 118, 208))
    o.append(place("doctor", 198, 437, 118, 190))
    o.append(place("dog", 318, 456, 132, 132))
    o.append(check_badge(364, 360, 20))
    for sx, sy, r in ((262, 368, 10), (378, 418, 8), (266, 430, 7), (346, 324, 7)):
        o.append(sparkle(sx, sy, r, GOLD))
    # the shelf with things to give
    o.append(f'<rect x="10" y="740" width="370" height="18" rx="6" fill="#D08E57" stroke="{lin("#D08E57")}" stroke-width="2.2"/>')
    o.append(f'<rect x="30" y="758" width="14" height="30" rx="4" fill="#B97A48" stroke="{lin("#D08E57")}" stroke-width="2"/>'
             f'<rect x="346" y="758" width="14" height="30" rx="4" fill="#B97A48" stroke="{lin("#D08E57")}" stroke-width="2"/>')
    slots = [("hose", 62), ("stethoscope", 152), (None, 240), ("carrot", 328)]
    for n, cx in slots:
        if n is None:
            o.append(f'<rect x="{cx - 40}" y="636" width="80" height="94" rx="20" fill="#FFFFFF" fill-opacity=".5" stroke="#B5A9D0" stroke-width="2.2" stroke-dasharray="6 5"/>')
            continue
        o.append(lipbox(cx - 40, 636, 80, 94, 20, "#FFFFFF", lipd=5))
        o.append(place(n, cx, 683, 62, 70))
    o.append(tx(195, 620, "拿給需要它的人", 15, "#6E8C78"))
    o.append(dots(195, 818, 5, 1, "#FF7F7F"))
    return page("".join(o), "#EAF8F0")




# ---------------------------------------------------------------- 4 draw a line between friends
def crayon(p0, p1, col, t_end=1.0, seed=1):
    """A wobbly crayon line from p0 toward p1 (an S curve), drawn up to t_end."""
    (x0, y0), (x3, y3) = p0, p1
    dx_, dy_ = x3 - x0, y3 - y0
    ln_ = math.hypot(dx_, dy_)
    bx, by = -dy_ / ln_ * 14, dx_ / ln_ * 14
    c1 = (x0 + dx_ * .33 + bx, y0 + dy_ * .33 + by)
    c2 = (x0 + dx_ * .66 + bx, y0 + dy_ * .66 + by)
    pts = []
    n = 40
    for i in range(n + 1):
        t = t_end * i / n
        u = 1 - t
        x = u ** 3 * x0 + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * x3
        y = u ** 3 * y0 + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * y3
        pts.append((x, y))
    out = []
    for i, (x, y) in enumerate(pts):
        a, b = pts[max(0, i - 1)], pts[min(n, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l_ = math.hypot(dx, dy) or 1
        j = 1.3 * math.sin(i * .45 + seed) + .5 * math.sin(i * 1.3 + seed * 2)
        out.append((x - dy / l_ * j, y + dx / l_ * j))
    d = poly(out, False)
    end = out[-1]
    o = (f'<path d="{d}" stroke="{col}" stroke-width="9" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity=".95"/>'
         f'<path d="{d}" stroke="{lt(col, .45)}" stroke-width="3" fill="none" stroke-linecap="round" opacity=".75" transform="translate(-1.5 -1.5)"/>'
         f'<path d="{d}" stroke="#FFFFFF" stroke-width="2.2" fill="none" stroke-dasharray="1 7" opacity=".45" transform="translate(1.5 2)"/>')
    for (x, y) in ((x0, y0),) + (((end[0], end[1]),) if t_end >= 1 else ()):
        o += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{col}" stroke="{lin(col)}" stroke-width="2.2"/><circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="#FFFFFF"/>'
    return o, end


def screen_link():
    o = [f'<rect width="{W}" height="{H}" fill="{lg([(0, "#E1F0FF"), (1, "#F2F8FF")])}"/>']
    o.append(header("連連看", "#5AA9F5"))
    o.append(ask(90, "誰和誰是好朋友？", 24))
    left = [("toothbrush", {}), ("key", {}), ("raincloud", {}), ("sock", {})]
    right = [("umbrella", {}), ("toothpaste", {}), ("shoe", {}), ("padlock", {})]
    rows = [196 + i * 150 for i in range(4)]
    cw, ch = 118, 124
    lx, rx = 22, 250
    done = {0: ("#FF8A3D", 1), 1: ("#9B5DE5", 3)}
    matched_r = {1: "#FF8A3D", 3: "#9B5DE5"}
    for i, y in enumerate(rows):
        c = done.get(i, (None,))[0]
        o.append(lipbox(lx, y, cw, ch, 24, "#FFFFFF", c, lt(c, .5) if c else None, 5, 3 if c else 2.2))
        o.append(place(left[i][0], lx + cw / 2, y + ch / 2, cw - 30, ch - 30))
        c2 = matched_r.get(i)
        o.append(lipbox(rx, y, cw, ch, 24, "#FFFFFF", c2, lt(c2, .5) if c2 else None, 5, 3 if c2 else 2.2))
        o.append(place(right[i][0], rx + cw / 2, y + ch / 2, cw - 30, ch - 30))
        if i not in done and i != 2:
            o.append(f'<circle cx="{lx + cw + 10}" cy="{y + ch / 2}" r="6" fill="#FFFFFF" stroke="#B5A9D0" stroke-width="2"/>')
        if i not in matched_r and i != 0:
            o.append(f'<circle cx="{rx - 10}" cy="{y + ch / 2}" r="6" fill="#FFFFFF" stroke="#B5A9D0" stroke-width="2"/>')
    ax, bx = lx + cw + 10, rx - 10
    line1, _ = crayon((ax, rows[0] + ch / 2), (bx, rows[1] + ch / 2), "#FF8A3D", 1.0, 1)
    line2, _ = crayon((ax, rows[1] + ch / 2), (bx, rows[3] + ch / 2), "#9B5DE5", 1.0, 3)
    line3, end = crayon((ax, rows[2] + ch / 2), (bx, rows[0] + ch / 2), BLUE, .45, 5)
    o.append(line1 + line2 + line3)
    o.append(finger(end[0], end[1], 21))
    o.append(dots(195, 816, 4, 2, "#5AA9F5"))
    return page("".join(o), "#EAF4FF")


# ---------------------------------------------------------------- 5 which one is different?
def screen_odd():
    o = [f'<rect width="{W}" height="{H}" fill="{lg([(0, "#FFF4D6"), (1, "#FFFBEE")])}"/>']
    o.append(header("哪個不一樣？", "#4CC46A"))
    o.append(roundbtn(350, 46, 24, TEAL, ic(i_speaker(), 350, 46, .9)))
    cards = [("apple", 22, 96, {}), ("banana", 202, 96, {}), ("grapes", 22, 330, {}), ("toycar", 202, 330, {})]
    for n, x, y, kw in cards:
        if n == "toycar":
            o.append(f'<rect x="{x - 6}" y="{y - 6}" width="178" height="232" rx="34" fill="#FFE27A" opacity=".8" filter="{blur(8)}"/>')
            o.append(lipbox(x, y, 166, 220, 28, "#FFFDF2", "#D99A0B", "#FFD45C", 6, 4))
        else:
            o.append(lipbox(x, y, 166, 220, 28, "#FFFFFF", lipd=6))
        o.append(place(n, x + 83, y + 110, 128, 150, **kw))
    burst = star_d(40, 27, 12, 350, 342, -90, .1)
    o.append(f'<path d="{burst}" fill="#FFD84D" stroke="#E0A10E" stroke-width="2.2" stroke-linejoin="round"/>')
    o.append(check_badge(350, 340, 20))
    for sx, sy, r in ((236, 372, 9), (226, 528, 7), (348, 520, 10), (282, 356, 6)):
        o.append(sparkle(sx, sy, r, "#F5B70F"))
    # 阿布 explains
    o.append(f'<ellipse cx="80" cy="800" rx="52" ry="8" fill="#E8D49A" opacity=".55"/>')
    o.append(place("fox", 84, 716, 150, 170, pose="point", look=(4, 1)))
    o.append(bubble(168, 620, 204, 140, 30, "left", 704))
    o.append(tx(270, 676, "對了！", 30, "#2FA84F", extra='stroke="#FFFFFF" stroke-width="4" paint-order="stroke"'))
    o.append(tx(270, 722, "汽車不是水果。", 22, INK))
    o.append(dots(195, 822, 5, 3, "#4CC46A"))
    return page("".join(o), "#FFF8E4")


# ---------------------------------------------------------------- 6 what comes next?
def screen_next():
    dy = -40
    o = [f'<rect width="{W}" height="{H}" fill="{lg([(0, "#D2ECFF"), (.5, "#E6F5FF"), (1, "#F6F1FF")])}"/>']
    o.append(soft_clouds([(300, 210, .7), (120, 196, .5)], .9))
    o.append(f'<circle cx="336" cy="250" r="22" fill="{YELLOW}" stroke="{lin(YELLOW)}" stroke-width="2.2"/>')
    o.append(f'<g transform="translate(0 {dy})">')
    o.append(f'<path d="M0,392 C60,350 120,346 190,380 C250,410 320,350 390,370 L390,470 L0,470Z" fill="#B6E3A4"/>')
    o.append(f'<path d="M0,420 C80,396 160,408 230,424 C300,440 350,416 390,410 L390,480 L0,480Z" fill="#9ED68C"/>')
    o.append(f'<rect x="0" y="446" width="{W}" height="40" fill="#CDEFC0"/>')
    for x in range(-6, 400, 22):
        o.append(f'<rect x="{x}" y="447" width="12" height="11" rx="2" fill="#B98A5A" stroke="#8C6440" stroke-width="1.2"/>')
    o.append(f'<path d="M0,447 L390,447" stroke="#7A6A80" stroke-width="3.5"/><path d="M0,456 L390,456" stroke="#9A8AA0" stroke-width="2"/>')
    for x, y, sc in ((12, 360, .17), (24, 340, .23), (42, 314, .3)):
        o.append(f'<path d="{cloud_d(x, y, sc)}" fill="#FFFFFF" stroke="#B9C7DA" stroke-width="2"/>')
    o.append(place("engine", 35.3, 404.8, 170 * .58, 148 * .58))
    cargo = ["redball", "bluestar", "redball", "bluestar", "redball", None]
    cols = [YELLOW, GREEN, PINK, "#7CC7FF", "#FFB066", PURPLE]
    for i, cg in enumerate(cargo):
        cx = 114.8 + i * 49.6
        o.append(place("wagon", cx, 427.6, 68 * .7059, 58 * .7059, col=cols[i]))
        if cg:
            o.append(place(cg, cx, 400, 38, 38, sw=1.8))
        else:
            o.append(f'<circle cx="{cx}" cy="398" r="27" fill="{PURPLE}" opacity=".16"/>')
            o.append(f'<rect x="{cx - 19}" y="379" width="38" height="38" rx="10" fill="#FFFFFF" stroke="{PURPLE}" stroke-width="2.4" stroke-dasharray="5 4"/>')
            o.append(tx(cx, 407, "?", 26, PURPLE))
    o.append("</g>")
    o.append(f'<rect x="0" y="446" width="{W}" height="{H - 446}" fill="{lg([(0, "#CDEFC0"), (.12, "#EEF6F4"), (1, "#F6F1FF")])}"/>')
    o.append(header("接下來是什麼？", "#A982F0"))
    o.append(ask(90, "下一個是什麼呢？", 24))
    # choices
    o.append(tx(195, 500, "選一個放上火車", 15, "#7E7196"))
    for i, n in enumerate(("bluestar", "redball", "greentri")):
        x = 22 + i * 120
        o.append(lipbox(x, 516, 106, 136, 24, "#FFFFFF", lipd=6))
        o.append(place(n, x + 53, 584, 74, 74))
    # 阿布 says the pattern
    o.append(place("fox", 64, 742, 110, 120, pose="point", mouth="smile", look=(3, 0)))
    o.append(bubble(128, 702, 244, 76, 28, "left", 740))
    o.append(tx(250, 735, "紅球、藍星星、", 19, INK) + tx(250, 762, "紅球、藍星星……", 19, INK))
    o.append(dots(195, 826, 5, 1, "#A982F0"))
    return page("".join(o), "#EAF5FF")




# ---------------------------------------------------------------- 7 little detective (5-6 years)
def grey_filter():
    D.add("greyf", '<filter id="greyf"><feColorMatrix type="saturate" values=".12"/></filter>')
    return "url(#greyf)"


def place_on(name, cx, base, s, **kw):
    """Place at a fixed scale with the bottom of its box on `base`."""
    x0, y0, x1, y1 = BOX[name]
    return place(name, cx, base - (y1 - y0) / 2 * s, (x1 - x0) * s, (y1 - y0) * s, **kw)


def i_ears():
    o = ""
    for a in (-14, 14):
        o += g(part(ell(0, -4, 8, 21), "#FBF5EE", s=None, ol="#9A8AA8") + part(ell(0, -2, 3.8, 14), "#FFC2D1", s=None, ol=False),
               f"rotate({a} 0 16) translate({a * .55} 0)")
    return o


def i_nohat():
    return (g(tophat(), "translate(0 8) scale(.42)")
            + '<circle cx="0" cy="0" r="22" fill="none" stroke="#E5484D" stroke-width="4"/>'
            + '<path d="M-15,15 L15,-15" stroke="#E5484D" stroke-width="4" stroke-linecap="round"/>')


def screen_detective():
    o = [f'<rect width="{W}" height="{H}" fill="{lg([(0, "#ECE5FF"), (1, "#F8F4FF")])}"/>']
    o.append(header("小偵探", "#8C6BE8"))
    o.append(f'<rect x="300" y="30" width="74" height="32" rx="16" fill="#FFE08A" stroke="#D9A520" stroke-width="2"/>' + tx(337, 52, "5～6 歲", 15, "#8A5A00"))
    o.append(ask(90, "誰拿走了蛋糕？", 24))
    o.append(place("plate", 324, 128, 72, 36, sw=1.8))
    # the line-up
    o.append(lipbox(14, 184, 362, 298, 26, "#FBF8FF", lipd=5))
    o.append("".join(f'<path d="M30,{y} L360,{y}" stroke="#E6DDF6" stroke-width="2"/>' for y in (236, 286, 336, 386)))
    o.append(f'<g clip-path="{clip(rr(14, 184, 362, 298, 26))}"><rect x="14" y="420" width="362" height="62" fill="#EFE8FB"/></g>'
             f'<path d="{rr(14, 184, 362, 298, 26)}" fill="none" stroke="{UI_OL}" stroke-width="2.2"/>')
    base, s = 436, .66
    suspects = [("rabbit", {"hat": True}, 62), ("rabbit", {"crumbs": True}, 152), ("cat", {"hat": True}, 242), ("bear", {}, 330)]
    for i, (n, kw, cx) in enumerate(suspects):
        o.append(f'<ellipse cx="{cx}" cy="{base + 2}" rx="38" ry="6" fill="#CFC3EA" opacity=".7"/>')
        art = place_on(n, cx, base, s, **kw)
        if i == 1:
            o.append(art)
        else:
            o.append(f'<g filter="{grey_filter()}" opacity=".42">{art}</g>')
            o.append(f'<path d="M{cx - 22},{base - 62} L{cx + 22},{base - 20} M{cx + 22},{base - 62} L{cx - 22},{base - 20}" '
                     f'stroke="#E07B86" stroke-width="7" stroke-linecap="round" opacity=".8"/>')
        o.append(f'<circle cx="{cx}" cy="{base + 24}" r="12" fill="{"#8C6BE8" if i == 1 else "#D8CFEA"}"/>' + tx(cx, base + 30, str(i + 1), 15, "#FFFFFF"))
    # magnifying glass around the one left
    mx, my, mr = 152, 362, 64
    o.append(f'<circle cx="{mx}" cy="{my}" r="{mr}" fill="#DDF3FF" opacity=".25"/>')
    o.append(f'<path d="M{mx + 47},{my + 47} L{mx + 76},{my + 78}" stroke="{lin("#9B5E34")}" stroke-width="17" stroke-linecap="round"/>'
             f'<path d="M{mx + 47},{my + 47} L{mx + 76},{my + 78}" stroke="#9B5E34" stroke-width="12" stroke-linecap="round"/>')
    o.append(f'<circle cx="{mx}" cy="{my}" r="{mr}" fill="none" stroke="{lin(GOLD)}" stroke-width="13"/>'
             f'<circle cx="{mx}" cy="{my}" r="{mr}" fill="none" stroke="{GOLD}" stroke-width="8.5"/>'
             f'<path d="M{mx - 46},{my - 30} A54,54 0 0 1 {mx - 20},{my - 52}" stroke="#FFFFFF" stroke-width="5" fill="none" stroke-linecap="round" opacity=".85"/>')
    # clues
    clues = [("線索1：", "牠有長耳朵", i_ears(), "#FFE3EC"), ("線索2：", "牠沒有戴帽子", i_nohat(), "#FFE9E2")]
    for k, (lab, txt, icon, bgc) in enumerate(clues):
        y = 506 + k * 88
        o.append(lipbox(20, y, 350, 74, 22, "#FFFFFF", lipd=5))
        o.append(f'<circle cx="60" cy="{y + 37}" r="27" fill="{bgc}"/>' + ic(icon, 60, y + 37, 1.0))
        o.append(f'<text x="100" y="{y + 45}" font-size="21" fill="{INK}" font-family="Huninn, sans-serif">'
                 f'<tspan fill="#8C6BE8">{lab}</tspan>{txt}</text>')
        o.append(check_badge(338, y + 37, 15))
    # 阿布
    o.append(place("fox", 70, 748, 120, 130, pose="glass", look=(3, -1)))
    o.append(bubble(140, 700, 232, 84, 28, "left", 744))
    o.append(tx(256, 734, "找到了！", 21, "#2FA84F", extra='stroke="#FFFFFF" stroke-width="4" paint-order="stroke"'))
    o.append(tx(256, 764, "是沒戴帽子的兔子。", 19, INK))
    o.append(dots(195, 826, 3, 1, "#8C6BE8"))
    return page("".join(o), "#F2EDFF")


# ---------------------------------------------------------------- 8 right answer + why
def screen_right():
    o = [f'<rect width="{W}" height="{H}" fill="#DDF4F7"/>']
    o.append("".join(f'<path d="M{x},0 L{x},540" stroke="#C9EAEF" stroke-width="2"/>' for x in range(0, 391, 39)))
    o.append("".join(f'<path d="M0,{y} L390,{y}" stroke="#C9EAEF" stroke-width="2"/>' for y in range(0, 541, 39)))
    o.append(f'<rect x="0" y="540" width="{W}" height="{H - 540}" fill="#FBE9EF"/>')
    o.append("".join(f'<path d="M0,{y} L390,{y}" stroke="#F2D3DE" stroke-width="2"/>' for y in (600, 680, 770)))
    o.append("".join(f'<path d="M{x},540 L{x + (x - 195) * .35:.0f},844" stroke="#F2D3DE" stroke-width="2"/>' for x in range(15, 390, 60)))
    o.append(f'<rect x="0" y="532" width="{W}" height="10" fill="#FFFFFF" stroke="#BFDDE3" stroke-width="1.5"/>')
    # mirror
    o.append(f'<path d="{rr(130, 196, 132, 112, 44)}" fill="#FFFFFF" stroke="{UI_OL}" stroke-width="2.2"/>'
             f'<path d="{rr(140, 206, 112, 92, 36)}" fill="{lg([(0, "#E4F6FF"), (1, "#BFE6FA")])}" stroke="#8BB8D9" stroke-width="1.6"/>'
             f'<path d="M168,276 L210,226 M184,284 L222,240" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round" opacity=".8"/>')
    # towel rail
    o.append(f'<rect x="300" y="300" width="72" height="9" rx="4.5" fill="#C9CED9" stroke="#8E95A6" stroke-width="1.8"/>'
             f'<path d="M310,304 L362,304 L362,394 C362,400 358,404 352,404 L320,404 C314,404 310,400 310,394Z" fill="#FF9FB8" stroke="{lin("#FF9FB8")}" stroke-width="2.2"/>'
             f'<path d="M310,376 L362,376 M310,386 L362,386" stroke="#FFFFFF" stroke-width="4"/>')
    # sink
    wol = UI_OL
    o.append(f'<path d="{rr(172, 430, 46, 104, 14)}" fill="#FFFFFF" stroke="{wol}" stroke-width="2.2"/>'
             f'<path d="M184,440 L184,526" stroke="#E4DEF0" stroke-width="5" stroke-linecap="round"/>')
    o.append(f'<path d="M100,392 L290,392 C286,428 250,446 195,446 C140,446 104,428 100,392Z" fill="#FFFFFF" stroke="{wol}" stroke-width="2.2"/>'
             f'<path d="M120,404 C140,430 250,430 270,404" stroke="#E4DEF0" stroke-width="5" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="{rr(86, 374, 218, 22, 11)}" fill="#FFFFFF" stroke="{wol}" stroke-width="2.2"/>')
    o.append(f'<path d="M188,374 L188,350 C188,340 198,336 206,340 L222,348" stroke="#8E95A6" stroke-width="13" fill="none" stroke-linecap="round"/>'
             f'<path d="M188,374 L188,350 C188,340 198,336 206,340 L222,348" stroke="#D3D8E2" stroke-width="8.5" fill="none" stroke-linecap="round"/>'
             f'<path d="{rr(176, 330, 24, 9, 4.5)}" fill="#D3D8E2" stroke="#8E95A6" stroke-width="1.8"/>')
    o.append(place("toothpaste", 262, 360, 66, 32, sw=1.8))
    # cup and the toothbrush landing in it
    o.append(f'<path d="M104,318 L144,318 L139,372 C139,375 137,376 134,376 L114,376 C111,376 109,375 109,372Z" fill="#5BC0F8" stroke="{lin("#5BC0F8")}" stroke-width="2.2"/>'
             f'<path d="M112,326 L115,366" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" opacity=".7"/>')
    o.append(place("toothbrush", 128, 280, 86, 86, rot=-58))
    o.append(f'<path d="M112,196 L112,212 M126,190 L126,208 M140,196 L140,212" stroke="#7FB8D0" stroke-width="3" stroke-linecap="round"/>')
    for sx, sy, r in ((86, 300, 10), (160, 300, 12), (94, 262, 7), (166, 262, 7)):
        o.append(sparkle(sx, sy, r, "#F5B70F"))
    # the explanation
    o.append(bubble(16, 24, 358, 152, 30))
    o.append(roundbtn(56, 64, 22, TEAL, ic(i_speaker(), 56, 64, .9), lipd=3))
    o.append(tx(90, 76, "答對了！", 30, "#2FA84F", "start", 'stroke="#FFFFFF" stroke-width="4" paint-order="stroke"'))
    o.append(tx(195, 120, "牙刷放在浴室，", 23, INK) + tx(195, 154, "因為我們在浴室刷牙。", 23, INK))
    # 阿布 with the new sticker
    stk = g(sticker(), "translate(100 -66) scale(.92)")
    o.append(f'<ellipse cx="104" cy="742" rx="64" ry="9" fill="#EBC3D2" opacity=".6"/>')
    o.append(place("fox", 112, 640, 200, 210, pose="sticker", hold=stk, look=(4, -2)))
    # mini sticker book in the corner, the sticker going in
    o.append(f'<path d="M206,566 C248,520 300,532 326,580" stroke="{GOLD}" stroke-width="5" fill="none" stroke-linecap="round" stroke-dasharray="0.1 12"/>')
    o.append(place("openbook", 300, 652, 156, 102, filled=5))
    o.append(place("sticker", 344, 616, 36, 36, rot=-14, sw=1.6))
    o.append(f'<path d="M312,594 L300,588 M310,606 L296,604" stroke="#E0A10E" stroke-width="3" stroke-linecap="round"/>')
    o.append(sparkle(368, 592, 8, "#F5B70F"))
    o.append(tx(300, 724, "偵探手冊", 15, "#5E8F8A"))
    # next
    o.append(lipbox(104, 762, 182, 56, 28, "#3CC46A", lipd=6))
    o.append(tx(180, 799, "下一題", 24, "#FFFFFF", extra=f'stroke="{lin("#3CC46A")}" stroke-width="3" paint-order="stroke"'))
    o.append(ic(i_arrow("#FFFFFF", 4.5), 248, 790, 1.0))
    return page("".join(o), "#DDF4F7")


# ---------------------------------------------------------------- 9 parents
P_BG, P_LINE, P_TXT, P_SUB, P_ACC = "#F2F3F7", "#E2E5EC", "#2F3540", "#7C8494", "#3E8E86"


def toggle(x, y, on=True):
    if on:
        return (f'<rect x="{x}" y="{y}" width="46" height="26" rx="13" fill="{P_ACC}"/>'
                f'<circle cx="{x + 33}" cy="{y + 13}" r="10" fill="#FFFFFF"/>')
    return (f'<rect x="{x}" y="{y}" width="46" height="26" rx="13" fill="#D5D9E2"/>'
            f'<circle cx="{x + 13}" cy="{y + 13}" r="10" fill="#FFFFFF"/>')


def section(y, h, title=None):
    o = f'<rect x="14" y="{y}" width="362" height="{h}" rx="16" fill="#FFFFFF" stroke="{P_LINE}" stroke-width="1.2"/>'
    if title:
        o += tx(30, y + 26, title, 15, P_SUB, "start")
    return o


def screen_parents():
    o = [f'<rect width="{W}" height="{H}" fill="{P_BG}"/>']
    o.append(tx(195, 52, "家長模式", 20, P_TXT))
    o.append(f'<circle cx="350" cy="46" r="18" fill="#E4E7EE"/>' + ic(i_x("#5C6474", 2.6), 350, 46, .85))
    # age
    o.append(section(80, 86, "年齡"))
    o.append(f'<rect x="30" y="118" width="330" height="36" rx="10" fill="#EEF0F4"/>')
    for i, a in enumerate(("3～4 歲", "4～5 歲", "5～6 歲")):
        x = 32 + i * 109
        if i == 1:
            o.append(f'<rect x="{x}" y="120" width="108" height="32" rx="9" fill="{P_ACC}"/>')
        o.append(tx(x + 54, 142, a, 15, "#FFFFFF" if i == 1 else P_TXT))
    # games
    o.append(section(178, 264, "要玩哪些遊戲"))
    games = [("放哪裡？", "#FFB066", True), ("是誰的？", "#FF8A8A", True), ("連連看", "#6FB6FF", True),
             ("哪個不一樣？", "#63CF7A", True), ("接下來是什麼？", "#B48CF5", True), ("小偵探（5～6 歲）", "#8C6BE8", False)]
    for i, (n, c, on) in enumerate(games):
        y = 214 + i * 37
        if i:
            o.append(f'<path d="M30,{y - 4} L360,{y - 4}" stroke="#EEF0F4" stroke-width="1.2"/>')
        o.append(f'<rect x="30" y="{y + 4}" width="20" height="20" rx="6" fill="{c}"/>')
        o.append(tx(60, y + 20, n, 16, P_TXT, "start"))
        o.append(toggle(314, y + 1, on))
    # time
    o.append(section(454, 92, "每次玩多久"))
    for i, m in enumerate((5, 10, 15, 20, 30)):
        x = 30 + i * 67
        sel = m == 15
        o.append(f'<rect x="{x}" y="492" width="61" height="36" rx="18" fill="{P_ACC if sel else "#FFFFFF"}" stroke="{P_ACC if sel else "#D5D9E2"}" stroke-width="1.5"/>')
        o.append(tx(x + 30.5, 515, f"{m} 分鐘", 14, "#FFFFFF" if sel else P_TXT))
    # english and sound
    o.append(section(558, 104))
    o.append(tx(30, 588, "英文", 16, P_TXT, "start") + tx(30, 608, "說完國語，再說一次英文", 13, P_SUB, "start"))
    o.append(toggle(314, 582, True))
    o.append(f'<path d="M30,620 L360,620" stroke="#EEF0F4" stroke-width="1.2"/>')
    o.append(tx(30, 648, "聲音", 16, P_TXT, "start"))
    o.append(f'<rect x="96" y="640" width="210" height="6" rx="3" fill="#E1E4EA"/><rect x="96" y="640" width="140" height="6" rx="3" fill="{P_ACC}"/>'
             f'<circle cx="236" cy="643" r="10" fill="#FFFFFF" stroke="{P_ACC}" stroke-width="2"/>')
    o.append(ic(i_speaker(P_SUB), 336, 643, .7))
    # progress
    o.append(section(674, 156, "能力進度"))
    o.append(tx(360, 700, "這一週", 13, P_SUB, "end"))
    skills = [("分類", .72, "#F29A4A", "18 題"), ("配對", .58, "#4F9BE8", "14 題"), ("規律", .40, "#9B7BE0", "9 題"), ("推理", .18, "#3EAE7E", "3 題")]
    for i, (n, v, c, cnt) in enumerate(skills):
        y = 722 + i * 28
        o.append(tx(30, y + 5, n, 15, P_TXT, "start"))
        o.append(f'<rect x="76" y="{y - 6}" width="222" height="12" rx="6" fill="#EEF0F4"/><rect x="76" y="{y - 6}" width="{222 * v:.0f}" height="12" rx="6" fill="{c}"/>')
        o.append(tx(360, y + 5, cnt, 13, P_SUB, "end"))
    return page("".join(o), P_BG)


def contact_sheet(names):
    cw_, ch_, gap, m = 232, 502, 22, 30
    per = 5
    w = per * cw_ + (per - 1) * gap + 2 * m
    rowh = ch_ + 64
    h = 2 * rowh + 40
    items = []
    for i, n in enumerate(names):
        r, c = divmod(i, per)
        x = m + c * (cw_ + gap) + (0 if r == 0 else (cw_ + gap) / 2)
        y = 28 + r * rowh
        items.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{cw_}px;text-align:center">'
                     f'<img src="file://{HERE / (n + ".png")}" style="width:{cw_}px;height:{ch_}px;border-radius:18px;box-shadow:0 6px 16px rgba(70,50,110,.18)">'
                     f'<div style="font:19px Huninn, sans-serif;color:{INK};margin-top:10px">{n.replace("_", " ")}</div></div>')
    css = f"@font-face {{ font-family: Huninn; src: url('file://{FONT}'); }} * {{ margin:0; padding:0 }} body {{ width:{w}px; height:{h}px; background:#F4F0FA; position:relative }}"
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(items)}</body></html>', w, h


SCREENS = {"1_首頁": screen_hub, "2_放哪裡": screen_room, "3_是誰的": screen_whose, "4_連連看": screen_link,
           "5_哪個不一樣": screen_odd, "6_接下來是什麼": screen_next, "7_小偵探": screen_detective,
           "8_答對了": screen_right, "9_家長模式": screen_parents}

SCRATCH = pathlib.Path(tempfile.gettempdir())


def main(only=None):
    global D
    if only and only.startswith("items"):
        D = Defs()
        style = only[5:] or "A"
        html, w, h = items_sheet(style=style)
        out = SCRATCH / f"logic_items_{style}.png"
        render(html, out, w, h, 1)
        print(out)
        return
    if only in (None, "0"):
        D = Defs()
        html, ph = style_sheet()
        render(html, HERE / "0_畫風選擇.png", W, ph, 2)
        print("0_畫風選擇")
    for name, make in SCREENS.items():
        if only not in (None, name[0]):
            continue
        D = Defs()
        render(make(), HERE / f"{name}.png", W, H, 2)
        print(name)
    if only in (None, "c"):
        html, w, h = contact_sheet(list(SCREENS))
        render(html, HERE / "contact_sheet.png", w, h, 1.25)
        print("contact_sheet")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
