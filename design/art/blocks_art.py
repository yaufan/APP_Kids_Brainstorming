"""積木王國 pictures (style C 幾何積木風), drawn with blocks_kit.py.

    python3 blocks_art.py export            # write app/assets/art/blocks/*.svg
    python3 blocks_art.py preview out.png   # contact sheet: full size and 120 px, sequences as rows, the scene

Things for 哪個不一樣？ are 200 x 200 with a see-through background, the subject in the middle filling
about 85 % of the box. Sequence steps (接下來是什麼？) are little scenes in the same 200 x 200 box, drawn
in the box's own units so the steps of one sequence share their ground, scale and place. The scene
behind both games is 390 x 844, painted edge to edge, quiet in the middle (y 300-700) where the cards
and the train go. Ids follow app/lib/core/content.dart (blockThings, sequences, sequenceThings).
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from blocks_kit import *  # noqa: E402,F403
from blocks_kit import _DEFS  # noqa: E402

# ================================================================ things (local units, fitted by box)
THINGS = {}


def thing(box, dy=0.0):
    def deco(f):
        THINGS[f.__name__.rstrip("_")] = (f, box, dy)
        return f
    return deco


# ---------------------------------------------------------------- fruit and vegetables
@thing((-80, -93, 80, 66))
def apple():
    return (rect(-4, -92, 9, 34, BR, rx=4.5, rot=(12, 0, -60))
            + path("M6,-72 A30,30 0 0 1 48,-90 A30,30 0 0 1 6,-72Z", CG)
            + circle(-30, -6, 50, CR) + circle(30, -6, 50, CR) + rect(-46, 0, 92, 66, CR, rx=30)
            + rect(-50, -34, 14, 30, "#FF8A8A", rx=7))


@thing((-91, -52, 68, 35))
def banana():
    o = path("M-72,-24 A74,74 0 0 0 72,-24 A150,150 0 0 1 -72,-24Z", CY)
    o += path("M-72,-24 A74,74 0 0 0 72,-24 A86,86 0 0 1 -72,-24Z", "#F5A000")
    o += path("M-46,-6 A96,96 0 0 0 40,0", "none", extra=' stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" opacity=".5"')
    o += rect(-86, -34, 16, 18, BR, rx=3, rot=(30, -78, -25))
    o += rect(67, -30, 11, 11, "#5C3A22", rx=3)
    return g(o, "rotate(-18)")


GRAPE_AT = [(-48, -24), (-16, -24), (16, -24), (48, -24), (-32, 6), (0, 6), (32, 6), (-16, 36), (16, 36), (0, 64)]


@thing((-68, -83, 72, 89))
def grapes():
    o = cap(0, -44, 5, -74, 5, BR) + lens(4, -64, 54, -80, 13, CG)
    for x, y in GRAPE_AT[::-1]:
        o += circle(x + 4, y + 4, 20, "#6420C0") + circle(x, y, 20, "#9150F0") + shine(x - 7, y - 8, 4.2, .55)
    return o


@thing((-77, -88, 76, 75))
def orange():
    o = ell(0, 6, 76, 68, "#EB7A0C") + ell(-5, 1, 71, 63, "#FF9A1A")
    o += circle(-26, 16, 3, "#F08A10") + circle(18, 30, 3, "#F08A10") + circle(34, -8, 3, "#F08A10") + circle(-6, 42, 3, "#F08A10")
    o += circle(0, -60, 7, "#D8740A") + cap(0, -62, 3, -72, 4.5, BR)
    o += lens(4, -68, 52, -86, 13, CG)
    o += shine_bar(-50, -34, 14, 30, .5, rot=(25, -43, -19))
    return o


@thing((-76, -79, 76, 86))
def strawberry():
    o = poly([(-54, -26), (54, -26), (0, 64)], CR, round_=44)
    for x, y in ((-46, -22), (-16, -24), (16, -24), (46, -22), (-30, 2), (0, 0), (30, 2), (-15, 26), (15, 26), (0, 50)):
        o += ell(x, y + 6, 3.4, 5.4, "#FFD95A")
    o += shine_bar(-52, -18, 12, 26, .45, rot=(18, -46, -5))
    for tx_, ty_ in ((-50, -44), (-24, -30), (24, -30), (50, -44), (-26, -60), (26, -60)):
        o += lens(0, -48, tx_, ty_, 8, "#1E9E50")
    o += cap(0, -50, 6, -74, 5, "#1E9E50")
    return o


@thing((-87, -106, 99, 89))
def watermelon():
    cx, cy, R = -10, -8, 76
    body = circle(cx, cy, R, "#5DCB6E")
    inner = ""
    top, bot = f"{cx},{cy - R}", f"{cx},{cy + R}"
    for a1, a2 in ((22, 10), (52, 38), (76, 66)):
        inner += path(f"M{top} A{a1},{R} 0 0 1 {bot} A{a2},{R} 0 0 0 {top}Z", "#1E8E4A")
        inner += path(f"M{top} A{a1},{R} 0 0 0 {bot} A{a2},{R} 0 0 1 {top}Z", "#1E8E4A")
    o = body + g(inner, clip_=clip(circle(cx, cy, R, "#000000")))
    o += shine(cx - 40, cy - 38, 9, .5)
    o += cap(cx, cy - R + 2, cx + 4, cy - R - 12, 4.5, BR)
    o += arc(cx + 14, cy - R - 12, 8, 180, 400, 3.5, "#1E8E4A")
    # a slice in front
    s = (half(0, 0, 44, "#1E8E4A", up=False) + half(0, 0, 38, "#FFF4E2", up=False) + half(0, 0, 33, "#FF4D6D", up=False)
         + "".join(ell(x, y, 2.8, 4.6, DK, rot=x * .8) for x, y in ((-18, 8), (0, 12), (18, 8), (-9, 22), (9, 22))))
    o += g(s, "translate(54 44) rotate(-14)")
    return o


@thing((-79, -75, 79, 72))
def tomato():
    o = ell(0, 8, 78, 64, "#C9221A") + ell(-5, 3, 73, 59, "#F23B2F")
    st = [(0 + (34 if i % 2 == 0 else 14) * math.cos(math.radians(-90 + i * 36)),
           -46 + (34 if i % 2 == 0 else 14) * math.sin(math.radians(-90 + i * 36)) * .55) for i in range(10)]
    o += poly(st, "#1E9E50", round_=6)
    o += cap(0, -48, 5, -70, 5, "#1E9E50")
    o += shine_bar(-56, -26, 14, 30, .5, rot=(30, -49, -11))
    return o


@thing((-46, -102, 68, 83))
def carrot():
    o = lens(0, -46, -30, -98, 11, "#1E9E50") + lens(0, -46, 30, -98, 11, "#1E9E50") + lens(0, -46, 0, -108, 12, CG)
    o += poly([(-28, -42), (28, -42), (0, 76)], "#E8690C", round_=26)
    o += poly([(-28, -42), (16, -42), (-4, 70)], "#FF8A1F", round_=26)
    for y, w in ((-20, 18), (8, 14), (34, 10)):
        o += cap(-w / 2 - 6, y, w / 2 - 6, y, 3, "#E8690C")
    return g(o, "rotate(24)")


@thing((-76, -90, 81, 86))
def broccoli():
    o = poly([(-16, 4), (16, 4), (26, 78), (-26, 78)], "#9FD86A", round_=14)
    o += cap(-2, 24, -30, -6, 9, "#9FD86A") + cap(2, 24, 30, -6, 9, "#9FD86A")
    fl = [(-48, -14, 30), (48, -14, 30), (-26, -50, 30), (26, -50, 30), (0, -60, 32), (0, -24, 34), (-24, 4, 22), (24, 4, 22)]
    for x, y, r in fl:
        o += circle(x + 3, y + 4, r, "#17824A")
    for x, y, r in fl:
        o += circle(x - 1, y - 1, r - 3, "#2EB85F")
    for x, y in ((-50, -22), (-28, -58), (6, -70), (36, -50), (-6, -30), (50, -20), (-30, -2), (22, -10)):
        o += circle(x, y, 4, "#6BDB8E")
    return o


# ---------------------------------------------------------------- vehicles
@thing((-86, -68, 88, 42))
def car():
    return (rect(-84, -24, 172, 44, CB, rx=14)
            + poly([(-46, -24), (-30, -62), (28, -62), (50, -24)], CB, round_=10)
            + poly([(-30, -28), (-20, -52), (-4, -52), (-4, -28)], WHITE) + poly([(6, -28), (6, -52), (24, -52), (38, -28)], WHITE)
            + rect(74, -16, 12, 9, CY, rx=3) + rect(-86, -16, 10, 9, CR, rx=3)
            + circle(-46, 20, 21, DK) + circle(50, 20, 21, DK) + circle(-46, 20, 8, WHITE) + circle(50, 20, 8, WHITE))


@thing((-95, -75, 103, 60))
def bus():
    o = rect(-94, -64, 188, 104, "#E89A00", rx=16)
    o += rect(-94, -64, 188, 84, CY, rx=16) + rect(-94, -6, 188, 26, CY)
    o += rect(-94, 0, 188, 9, OR)
    for i in range(4):
        o += rect(-82 + i * 34, -52, 26, 32, WHITE, rx=5)
    o += rect(56, -52, 18, 60, "#E89A00", rx=4) + rect(59, -48, 12, 22, WHITE, rx=3)
    o += rect(78, -52, 14, 38, WHITE, rx=5)
    o += rect(-56, -74, 52, 12, DK, rx=5) + rect(-50, -71, 40, 6, CT, rx=3)
    o += circle(88, 26, 6, WHITE) + rect(84, 34, 14, 8, DK, rx=4) + cap(94, -44, 100, -54, 3, DK)
    o += circle(-54, 40, 20, DK) + circle(54, 40, 20, DK) + circle(-54, 40, 8, "#C3C8DE") + circle(54, 40, 8, "#C3C8DE")
    return o


@thing((-92, -62, 92, 62))
def bicycle():
    R, F, B, S, H = (-56, 26), (56, 26), (-4, 26), (-20, -26), (38, -30)
    o = ""
    for cx, cy in (R, F):
        for a in (0, 60, 120):
            x0, y0 = pt(cx, cy, 30, a)
            x1, y1 = pt(cx, cy, 30, a + 180)
            o += line([(x0, y0), (x1, y1)], 2.6, "#B4BAD3")
        o += ring(cx, cy, 31, 10, DK) + circle(cx, cy, 6, "#B4BAD3")
    fc = CG
    o += line([R, B, S, R], 9, fc, closed=True) + line([S, H, B], 9, fc, closed=True) + line([H, F], 9, fc)
    o += cap(-20, -26, -22, -36, 4, DK) + rect(-40, -44, 36, 12, DK, rx=6)
    o += cap(38, -30, 34, -50, 4.5, DK) + cap(30, -52, 52, -56, 5, DK)
    o += circle(-4, 26, 10, "#B4BAD3") + cap(-4, 26, 6, 42, 3, DK) + rect(-2, 39, 18, 7, DK, rx=3)
    return o


@thing((-96, -82, 101, 58))
def fire_truck():
    o = ""
    # the ladder on top, tilted up to the front
    a = -12
    lad = cap(-90, -6, 34, -6, 4, "#AEB5CF") + cap(-90, 8, 34, 8, 4, "#AEB5CF")
    lad += "".join(cap(x, -6, x, 8, 3, "#AEB5CF") for x in range(-80, 34, 16))
    o += g(lad, f"translate(0 -52) rotate({a} -60 0)")
    o += rect(-56, -50, 14, 14, DK, rx=3)
    o += rect(-94, -42, 134, 76, CR, rx=8)
    o += rect(34, -62, 62, 96, CR, rx=12)
    o += rect(48, -50, 36, 30, WHITE, rx=6)
    o += half(64, -62, 11, CB) + rect(52, -64, 24, 4, DK, rx=2)
    o += rect(-84, -32, 34, 30, "#C51A30", rx=4) + rect(-42, -32, 34, 30, "#C51A30", rx=4)
    o += rect(-94, 6, 190, 9, CY)
    o += circle(92, 22, 5, CY) + rect(88, 26, 12, 9, DK, rx=4)
    o += circle(-56, 36, 21, DK) + circle(62, 36, 21, DK) + circle(-56, 36, 8, "#C3C8DE") + circle(62, 36, 8, "#C3C8DE")
    return o


@thing((-116, -55, 93, 69))
def airplane():
    body = "#4CC3F2"
    o = poly([(-4, -10), (26, -10), (-14, -54), (-30, -54)], "#2E8BD8", round_=8)
    o += poly([(-70, -10), (-92, -10), (-102, -58), (-86, -58)], CY, round_=10)
    o += poly([(-70, -20), (-108, -16), (-104, 8), (-70, 20)], body, round_=10)
    o += cap(-72, 0, 72, 0, 22, body)
    o += poly([(-84, 2), (-102, 2), (-112, 16), (-96, 16)], "#2E8BD8", round_=6)
    o += poly([(-12, 8), (28, 8), (-18, 58), (-40, 58)], CB, round_=8)
    for x in range(-52, 40, 17):
        o += circle(x, -5, 5.5, WHITE)
    o += path("M64,-14 L80,-14 Q92,-12 92,-4 L66,-4Z", WHITE)
    return g(o, "rotate(-10)")


@thing((-105, -97, 105, 73))
def boat():
    o = cap(0, -92, 0, 8, 4, BR)
    o += poly([(3, -94), (28, -86), (3, -78)], "#FF5D8F", round_=4)
    o += poly([(10, -76), (10, -4), (72, -4)], CY, round_=8)
    o += poly([(-10, -62), (-10, -4), (-58, -4)], OR, round_=8)
    o += poly([(-86, 4), (86, 4), (64, 44), (-64, 44)], CB, round_=10)
    o += poly([(-75, 26), (75, 26), (64, 44), (-64, 44)], "#2557C9", round_=10)
    for x in (-38, 0, 38):
        o += circle(x, 15, 5.5, WHITE)
    w = rect(-104, 56, 208, 16, "#7FD4F5", rx=8)
    for x in range(-90, 91, 30):
        w += half(x, 58, 15, "#7FD4F5")
    return o + w


# ---------------------------------------------------------------- animals
DOG, DOGD, DOGE, MUZ = "#E3A35F", "#C0803F", "#8C5A3C", "#F8E2C6"


@thing((-88, -74, 102, 64))
def dog():
    o = cap(-58, -6, -80, -40, 7.5, DOG)
    o += rect(-46, 4, 16, 56, DOGD, rx=8) + rect(24, 4, 16, 56, DOGD, rx=8)
    o += rect(-68, -26, 122, 54, DOG, rx=27)
    o += circle(-26, -8, 15, DOGE)
    o += rect(-62, 8, 18, 56, DOG, rx=9) + rect(10, 8, 18, 56, DOG, rx=9)
    o += cap(26, -18, 40, -6, 6, CB)
    o += circle(52, -40, 34, DOG)
    o += rect(14, -66, 20, 46, DOGE, rx=10, rot=(18, 24, -66)) + rect(70, -66, 20, 46, DOGE, rx=10, rot=(-18, 80, -66))
    o += ell(52, -24, 21, 16, MUZ)
    o += ell(52, -33, 8, 6, DK) + smile(52, -24, 12, DK, 2.8)
    o += eye(39, -47, 5) + eye(65, -47, 5)
    o += circle(32, -30, 5, BLUSH, .8) + circle(72, -30, 5, BLUSH, .8)
    return o


CAT, CATD, CATL = "#9AA4C2", "#7480A2", "#F1F0F8"


@thing((-95, -95, 90, 60))
def cat():
    o = stroke("M-60,0 Q-100,-6 -84,-58", 13, CAT)
    o += rect(-44, 4, 14, 52, CATD, rx=7) + rect(22, 4, 14, 52, CATD, rx=7)
    o += rect(-66, -22, 118, 48, CAT, rx=24)
    for x in (-40, -20, 0):
        o += cap(x, -20, x + 4, -6, 4, CATD)
    o += rect(-58, 8, 15, 52, CAT, rx=7.5) + rect(8, 8, 15, 52, CAT, rx=7.5)
    for s in (-1, 1):
        o += poly([(50 + s * 30, -56), (50 + s * 24, -90), (50 + s * 4, -68)], CAT, round_=8)
        o += poly([(50 + s * 25, -60), (50 + s * 22, -80), (50 + s * 10, -66)], "#FFAFC4", round_=4)
    o += circle(50, -38, 32, CAT)
    for x in (42, 50, 58):
        o += cap(x, -70, x, -60, 2.5, CATD)
    o += circle(43, -27, 10, CATL) + circle(57, -27, 10, CATL)
    o += poly([(45, -34), (55, -34), (50, -28)], "#FF7FA3", round_=4)
    o += eye(38, -44, 5) + eye(62, -44, 5)
    for s in (-1, 1):
        o += cap(50 + s * 18, -28, 50 + s * 38, -32, 1.4, DK) + cap(50 + s * 18, -23, 50 + s * 38, -20, 1.4, DK)
    return o


RAB, RABD, RABL = "#B3BAD3", "#959DBB", "#D6DAEA"


@thing((-78, -112, 70, 62))
def rabbit():
    o = circle(-62, 2, 16, RABL)
    o += rect(20, 14, 14, 44, RABD, rx=7)
    o += ell(-14, 10, 54, 44, RAB)
    o += ell(-28, 22, 24, 28, RABD, rot=-20) + rect(-62, 44, 68, 18, RABD, rx=9)
    o += rect(32, 14, 15, 48, RAB, rx=7.5)
    for x, a in ((28, -10), (52, 10)):
        o += rect(x - 9, -112, 18, 66, RAB, rx=9, rot=(a, x, -50))
        o += rect(x - 4.5, -102, 9, 46, "#FFA3BC", rx=4.5, rot=(a, x, -50))
    o += circle(40, -30, 30, RAB)
    o += eye(30, -36, 4.5) + eye(50, -36, 4.5)
    o += ell(40, -25, 5, 3.6, "#FF7FA3") + rect(37, -21, 6, 7, WHITE, rx=1.5)
    o += circle(22, -22, 5, BLUSH, .8) + circle(58, -22, 5, BLUSH, .8)
    return o


ELE, ELED = "#8497C0", "#6B7EAA"


@thing((-86, -70, 110, 64))
def elephant():
    o = cap(-66, -16, -80, 8, 3, ELED) + circle(-81, 11, 5, DK)
    o += rect(-48, 6, 24, 54, ELED, rx=11) + rect(16, 6, 24, 54, ELED, rx=11)
    o += rect(-72, -46, 118, 76, ELE, rx=36)
    o += rect(-62, 10, 26, 54, ELE, rx=12) + rect(2, 10, 26, 54, ELE, rx=12)
    for x in (-58, -48, 6, 16):
        o += ell(x + 3, 60, 4, 3, "#E5E9F5")
    o += stroke("M70,-26 Q96,-8 90,26 Q88,40 100,40", 20, ELE)
    o += circle(50, -34, 36, ELE)
    o += ell(28, -30, 24, 32, ELED)
    o += eye(60, -44, 5)
    o += cap(72, -12, 82, -6, 4, "#F6F0E2")
    o += circle(68, -24, 5, BLUSH, .7)
    return o


@thing((-105, -73, 100, 49))
def fish():
    return (path("M48,0 L100,-38 L100,38Z", "#FFBF1F")
            + path("M-10,-40 L34,-40 L10,-70Z", "#FFBF1F")
            + ell(-6, 0, 72, 48, OR)
            + path("M-6,0 L44,0 A50,48 0 0 1 -6,48Z", ORANGE)
            + path("M0,14 L28,14 L14,36Z", "#FFBF1F")
            + circle(-40, -10, 13, WHITE) + circle(-43, -10, 8, DK) + circle(-46, -13, 3, WHITE)
            + circle(-92, -46, 7, "#7FD4F5") + circle(-100, -68, 4.5, "#7FD4F5"))


BIRD, BIRDD, BIRDL = CB, "#2557C9", "#A9CCFF"


@thing((-85, -84, 81, 55))
def bird():
    o = poly([(-34, 6), (-80, -16), (-74, 8)], BIRDD, round_=8) + poly([(-34, 12), (-78, 18), (-66, 36)], BIRDD, round_=8)
    o += circle(0, 10, 44, BIRD) + circle(28, -16, 28, BIRD)
    o += ell(10, 28, 30, 20, BIRDL)
    o += lens(-6, -6, -30, -84, 20, BIRDD)
    o += poly([(52, -24), (78, -15), (52, -6)], ORANGE, round_=5)
    o += eye(36, -22, 5.5) + circle(38, -6, 5, BLUSH, .8)
    return o


BFLY_UP, BFLY_LO = "#FF5D8F", "#FFBF1F"


@thing((-90, -91, 90, 63))
def butterfly():
    o = ""
    for s in (-1, 1):
        o += ell(s * 34, 34, 32, 27, BFLY_LO, rot=s * 30)
        o += ell(s * 46, -24, 46, 36, BFLY_UP, rot=s * -28)
        o += circle(s * 58, -34, 13, "#FFD45C") + circle(s * 28, -12, 7, "#FFD45C")
        o += circle(s * 40, 40, 9, "#FF8FAB")
        o += stroke(f"M{s * 4},-54 Q{s * 10},-78 {s * 28},-84", 4, DK)
        o += circle(s * 30, -85, 5.5, DK)
    o += cap(0, -36, 0, 52, 9, DK)
    o += circle(0, -46, 13, DK)
    o += circle(-5, -48, 3, WHITE) + circle(5, -48, 3, WHITE)
    return o


@thing((-85, -74, 59, 56))
def bee():
    o = ell(-14, -40, 22, 28, "#BFE3FF", rot=-20) + ell(14, -44, 20, 26, "#D9EEFF", rot=15)
    o += poly([(-58, 6), (-82, 14), (-58, 22)], DK, round_=4)
    body = ell(-4, 12, 62, 44, CY)
    stripes = rect(-36, -40, 16, 110, DK) + rect(-6, -40, 16, 110, DK)
    o += body + g(stripes, clip_=clip(ell(-4, 12, 62, 44, "#000000")))
    o += eye(36, 2, 6) + smile(40, 16, 12, DK, 3) + circle(50, 14, 5, BLUSH, .9)
    o += stroke("M34,-28 Q38,-52 52,-60", 4, DK) + circle(53, -61, 5, DK)
    o += stroke("M24,-30 Q20,-56 30,-68", 4, DK) + circle(31, -69, 5, DK)
    return o


# ---------------------------------------------------------------- things at home
@thing((-75, -75, 79, 79))
def ball():
    o = circle(2, 2, 77, "#C41A30") + circle(-3, -3, 72, CR)
    band = stroke("M-90,4 Q0,-58 90,4", 20, CY) + stroke("M-90,52 Q0,-6 90,52", 9, CY)
    o += g(band, clip_=clip(circle(2, 2, 77, "#000000")))
    o += shine(-36, -38, 11, .55)
    return o


@thing((-74, -76, 74, 70))
def cube():
    o = poly([(-70, -42), (40, -42), (70, -72), (-40, -72)], "#7FB0FF", round_=6)
    o += poly([(40, -42), (70, -72), (70, 36), (40, 66)], "#2563D8", round_=6)
    o += rect(-70, -44, 110, 110, CB, rx=6)
    o += rect(-56, -30, 82, 82, "none", rx=8).replace('fill="none"', 'fill="none" stroke="#7DAEFF" stroke-width="6"')
    o += star(-15, 11, 26, CY, round_=6)
    return o


@thing((-79, -93, 84, 83))
def clock():
    o = circle(3, 3, 80, "#2557C9") + circle(0, 0, 78, CB)
    o += circle(0, -84, 9, "#2557C9")
    o += circle(0, 0, 63, CREAM)
    for i in range(12):
        a = -90 + i * 30
        if i % 3 == 0:
            x0, y0 = pt(0, 0, 50, a)
            x1, y1 = pt(0, 0, 58, a)
            o += cap(x0, y0, x1, y1, 4, DK)
        else:
            x, y = pt(0, 0, 54, a)
            o += circle(x, y, 3.5, "#A6ACC4")
    x, y = pt(0, 0, 30, -150)
    o += cap(0, 0, x, y, 5, DK)
    x, y = pt(0, 0, 44, -30)
    o += cap(0, 0, x, y, 3.8, DK)
    o += circle(0, 0, 8, CR)
    return o


SOCK, SOCKD = PINK, "#FF5D8F"


def sock_shape(fill):
    return rect(-46, -86, 64, 120, fill, rx=14) + rect(-46, -8, 130, 62, fill, rx=31)


@thing((-61, -98, 86, 56))
def sock():
    o = sock_shape(SOCK)
    o += g(circle(-46, 54, 30, SOCKD) + circle(84, 23, 28, SOCKD) + rect(-46, -54, 64, 10, WHITE) + rect(-46, -34, 64, 10, WHITE),
           clip_=clip(sock_shape("#000000")))
    o += rect(-52, -96, 76, 28, SOCKD, rx=10)
    return g(o, "rotate(-6 0 0)")


@thing((-94, -45, 94, 54))
def hat():
    o = ell(0, 30, 94, 24, "#F0A000")
    o += path("M-56,32 A56,76 0 0 1 56,32Z", CY)
    o += g(rect(-60, 6, 120, 18, CB), clip_=clip(path("M-56,32 A56,76 0 0 1 56,32Z", "#000000")))
    o += circle(30, 14, 10, "#FF5D8F") + circle(30, 14, 4.5, "#FFE08A")
    o += shine_bar(-34, -24, 12, 26, .45, rot=(-28, -28, -11))
    return o


@thing((-101, -70, 101, 77))
def tshirt():
    pts = [(-24, -64), (-54, -60), (-96, -30), (-76, 4), (-54, -12), (-54, 72), (54, 72), (54, -12), (76, 4), (96, -30), (54, -60), (24, -64)]
    d = "M" + " L".join(f"{x},{y}" for x, y in pts) + " A26,22 0 0 1 -24,-64Z"
    o = path(d, CG, extra=f' stroke="{CG}" stroke-width="10" stroke-linejoin="round"')
    o += stroke("M-24,-64 A26,22 0 0 0 24,-64", 8, "#1E9E55")
    o += cap(-96, -30, -76, 4, 5, "#1E9E55") + cap(96, -30, 76, 4, 5, "#1E9E55")
    o += star(0, 12, 24, CY, round_=6)
    return o


# ================================================================ sequences (drawn in the 200 x 200 box)
SEQ = {}


def step(f):
    SEQ[f.__name__.rstrip("_")] = f
    return f


# ---------------------------------------------------------------- 蛋 → 小雞 → 母雞: in the same nest
NEST, NESTD, STRAW, EGG = "#B9773F", "#8A5428", "#E2A961", "#F2CC9A"


def nest_back():
    return ell(100, 140, 74, 15, NESTD)


def nest_front():
    o = path("M24,140 A76,44 0 0 0 176,140Z", NEST)
    for x0, y0, x1, y1 in ((40, 150, 70, 160), (64, 168, 98, 162), (104, 160, 136, 170), (130, 152, 160, 146), (82, 150, 112, 148)):
        o += cap(x0, y0, x1, y1, 2.6, STRAW)
    o += cap(26, 140, 174, 140, 6, "#CC8A4C")
    return o


@step
def egg():
    o = nest_back()
    o += path("M64,112 A36,54 0 0 1 136,112 A36,40 0 0 1 64,112Z", EGG)
    o += shine_bar(76, 78, 11, 26, .55, rot=(20, 81.5, 91))
    return g(o + nest_front(), "translate(0 -12)")


@step
def chick():
    o = nest_back()
    o += circle(100, 102, 43, CY)
    o += ell(58, 106, 10, 17, "#F5A000", rot=30) + ell(142, 106, 10, 17, "#F5A000", rot=-30)
    o += eye(85, 96, 5.5) + eye(115, 96, 5.5)
    o += poly([(92, 104), (108, 104), (100, 115)], OR, round_=4)
    o += circle(77, 111, 5.5, BLUSH, .8) + circle(123, 111, 5.5, BLUSH, .8)
    shell_top = path("M70,70 A30,26 0 0 1 130,70 L122,77 L114,69 L106,77 L98,69 L90,77 L82,69 L74,77Z", EGG)
    o += g(shell_top, "rotate(-14 100 66)")
    o += path("M60,126 L68,117 L76,126 L84,117 L92,126 L100,117 L108,126 L116,117 L124,126 L132,117 L140,126 L142,142 L58,142Z", EGG)
    return g(o + nest_front(), "translate(0 -12)")


HEN, HEND, HENT = "#EE8A3C", "#C6652A", "#8C4A2A"


@step
def hen():
    o = nest_back()
    for (x0, y0, x1, y1), c in (((60, 100, 18, 66), HENT), ((66, 96, 40, 48), "#A85530"), ((56, 108, 14, 92), "#A85530")):
        o += lens(x0, y0, x1, y1, 13, c)
    o += ell(96, 108, 58, 40, HEN)
    o += circle(140, 72, 26, HEN)
    o += lens(70, 96, 122, 116, 14, HEND)
    o += circle(132, 46, 8, CR) + circle(143, 42, 9, CR) + circle(154, 48, 8, CR)
    o += poly([(162, 66), (180, 73), (162, 80)], CY, round_=5)
    o += ell(160, 88, 5, 8, CR)
    o += eye(148, 66, 5) + circle(146, 82, 5, BLUSH, .8)
    return g(o + nest_front(), "translate(0 -12)")


# ---------------------------------------------------------------- 種子 → 發芽 → 開花: in the same soil, under the same sun
SOIL, SOILD, ROOT, STEM = "#9C6440", "#7E4C2E", "#E3BE8E", "#2EAE58"


def garden(inner_soil=""):
    o = circle(34, 36, 16, CY)
    for a in range(0, 360, 45):
        x0, y0 = pt(34, 36, 22, a)
        x1, y1 = pt(34, 36, 28, a)
        o += cap(x0, y0, x1, y1, 2.5, CY)
    o += rect(12, 130, 176, 58, SOIL, rx=16)
    for x, y, r in ((34, 170, 4), (60, 150, 3), (150, 168, 4), (170, 148, 3), (126, 176, 3), (78, 178, 3)):
        o += circle(x, y, r, SOILD)
    o += inner_soil
    o += rect(12, 124, 176, 14, CG, rx=7)
    return o


def seed_(cx=100, cy=160):
    return ell(cx, cy, 19, 12, "#F0B84E", rot=-20) + ell(cx - 5, cy - 4, 7, 3, "#FFE2A0", rot=-20)


@step
def seed():
    return garden(seed_())


@step
def sprout():
    roots = line([(100, 164), (94, 178)], 2.6, ROOT) + line([(102, 164), (110, 176)], 2.6, ROOT)
    o = garden(roots + seed_() + cap(100, 152, 100, 130, 4, STEM))
    o += cap(100, 130, 100, 96, 4.5, STEM)
    o += lens(100, 102, 70, 88, 11, CG) + lens(100, 100, 130, 84, 11, CG)
    return o


@step
def flower():
    roots = (line([(100, 136), (100, 160), (92, 176)], 2.6, ROOT) + line([(100, 152), (114, 170)], 2.6, ROOT)
             + line([(100, 146), (86, 158)], 2.6, ROOT))
    o = garden(roots)
    o += cap(100, 132, 100, 56, 5, STEM)
    o += lens(100, 112, 62, 96, 14, CG) + lens(100, 98, 138, 82, 14, CG)
    for k in range(6):
        x, y = pt(100, 46, 22, -90 + k * 60)
        o += circle(x, y, 17, "#FF5D8F")
    o += circle(100, 46, 15, CY) + shine(95, 41, 4, .6)
    return o


# ---------------------------------------------------------------- 光腳丫 → 穿襪子 → 穿鞋子: the same leg and foot
LEGC, LEGD = SKIN, "#D9926A"
FOOT_TOES = [(166, 152, 13), (154, 136, 10), (143, 129.5, 9), (133, 125.5, 8), (124, 122.5, 7)]
FOOT = "M48,148 A24,24 0 0 1 72,124 L106,122 Q126,124 152,138 A18,18 0 0 1 174,156 A10,10 0 0 1 164,166 L60,166 A12,12 0 0 1 48,154Z"
SOCK_FOOT = ("M58,76 L114,76 L114,118 Q132,124 158,134 A20,20 0 0 1 180,156 A13,13 0 0 1 167,170 L58,170 "
             "A14,14 0 0 1 44,156 L44,140 A18,18 0 0 1 58,124Z")


def leg_base():
    o = rect(14, 166, 172, 14, "#C9CCF2", rx=7)
    o += rect(62, 16, 48, 124, LEGC, rx=24)
    o += rect(50, 4, 72, 34, CB, rx=10) + rect(50, 30, 72, 8, "#2563D8", rx=4)
    return o


@step
def bare_foot():
    o = leg_base()
    o += path(FOOT, LEGC)
    for x, y, r in FOOT_TOES[::-1]:
        o += circle(x + 2.5, y + 2, r, LEGD) + circle(x, y, r, LEGC)
        o += ell(x + r * .3, y - r * .3, r * .45, r * .32, "#FBE0D0")
    return o


def sock_parts():
    return (circle(46, 172, 28, SOCKD) + circle(182, 160, 26, SOCKD) + rect(58, 96, 56, 9, WHITE) + rect(58, 110, 56, 9, WHITE))


@step
def sock_on():
    o = leg_base()
    o += path(SOCK_FOOT, SOCK)
    o += g(sock_parts(), clip_=clip(path(SOCK_FOOT, "#000000")))
    o += rect(54, 70, 64, 18, SOCKD, rx=8)
    return o


@step
def shoe_on():
    o = leg_base()
    o += rect(58, 76, 56, 44, SOCK) + rect(58, 96, 56, 9, WHITE)
    o += rect(54, 70, 64, 18, SOCKD, rx=8)
    shoe = "M46,128 Q46,110 62,110 L110,110 Q126,110 140,122 Q176,130 184,154 L184,162 L46,162Z"
    o += path(shoe, CB)
    o += path("M140,122 Q176,130 184,154 L184,162 L146,162Z", "#2563D8")
    o += rect(40, 156, 150, 16, DK, rx=8)
    o += cap(92, 120, 130, 128, 7.5, CY) + circle(124, 127, 3, "#E89A00")
    return o


# ---------------------------------------------------------------- 起床 → 刷牙 → 吃早餐: the same child
PJ, PJD, PJDOT = CT, "#22A89B", "#FFE08A"
HEAD = (100, 74)


def child_head(eyes="open", mouth="smile"):
    cx, cy = HEAD
    o = circle(cx, cy - 34, 10, HAIR)
    o += circle(cx, cy - 4, 32, HAIR) + rect(cx - 32, cy - 6, 64, 22, HAIR, rx=6)
    o += circle(cx - 30, cy + 6, 6, SKIN) + circle(cx + 30, cy + 6, 6, SKIN)
    o += circle(cx, cy + 4, 27, SKIN)
    o += path(f"M{cx - 27},{cy - 1} A27,27 0 0 1 {cx + 27},{cy - 1} Q{cx + 10},{cy - 10} {cx - 4},{cy - 8} Q{cx - 18},{cy - 6} {cx - 27},{cy - 1}Z", HAIR)
    if eyes == "open":
        o += eye(cx - 10, cy + 4, 4) + eye(cx + 10, cy + 4, 4)
    else:
        o += arc(cx - 10, cy + 2, 5, 20, 160, 2.8, DK) + arc(cx + 10, cy + 2, 5, 20, 160, 2.8, DK)
    o += circle(cx - 18, cy + 13, 4.5, BLUSH, .9) + circle(cx + 18, cy + 13, 4.5, BLUSH, .9)
    if mouth == "smile":
        o += smile(cx, cy + 15, 12, DK, 2.8)
    elif mouth == "yawn":
        o += ell(cx, cy + 18, 5, 6, "#B5303F")
    elif mouth == "open":
        o += path(f"M{cx - 7},{cy + 14} L{cx + 7},{cy + 14} A7,7 0 0 1 {cx - 7},{cy + 14}Z", "#B5303F")
    return o


def torso(y1=160):
    cx = HEAD[0]
    o = rect(cx - 26, 100, 52, y1 - 100, PJ, rx=18)
    for x, y in ((-12, 116), (10, 128), (-8, 142), (14, 150)):
        if 100 + 8 < 100 + (y - 100) < y1 - 4:
            o += circle(cx + x, y, 3.5, PJDOT)
    return o


@step
def wake_up():
    o = rect(138, 8, 54, 54, "#C98A52", rx=8) + rect(144, 14, 42, 42, "#BDE3FF", rx=4)
    o += circle(165, 35, 11, CY)
    o += rect(163, 14, 4, 42, "#C98A52") + rect(144, 33, 42, 4, "#C98A52")
    o += rect(8, 96, 22, 88, BR, rx=8)
    o += rect(26, 110, 48, 26, "#CFE0FF", rx=12)
    o += torso(150)
    o += cap(80, 112, 62, 70, 8, PJ) + cap(120, 112, 138, 70, 8, PJ)
    o += circle(60, 64, 8.5, SKIN) + circle(140, 64, 8.5, SKIN)
    o += child_head("closed", "yawn")
    o += rect(52, 128, 140, 44, CY, rx=14) + rect(52, 128, 140, 12, "#FFE08A", rx=6)
    o += rect(8, 158, 184, 18, BR, rx=6) + rect(14, 174, 10, 12, BR, rx=3) + rect(176, 174, 10, 12, BR, rx=3)
    return o


@step
def brushing():
    o = rect(18, 14, 164, 126, "#D6F0F2", rx=16)
    for x in range(18 + 41, 182, 41):
        o += rect(x - 1.5, 14, 3, 126, WHITE)
    for y in range(14 + 42, 140, 42):
        o += rect(18, y - 1.5, 164, 3, WHITE)
    o += torso(170)
    o += cap(126, 116, 128, 98, 8, PJ)
    o += child_head("open", "open")
    o += cap(108, 90, 150, 82, 4.5, "#FF5D8F")
    o += rect(98, 82, 14, 8, WHITE, rx=2) + rect(98, 82, 14, 3.5, "#7DB8FF", rx=1.5)
    o += circle(128, 92, 8.5, SKIN)
    for x, y, r in ((90, 96, 4), (95, 101, 3.5), (84, 92, 3)):
        o += circle(x, y, r, WHITE)
    for x, y, r in ((62, 60, 6), (52, 44, 4.5), (150, 48, 5), (160, 62, 3.5)):
        o += circle(x, y, r, WHITE) + ring(x, y, r, 1.5, "#9ED3FF")
    o += rect(20, 140, 160, 12, "#7FC8E8", rx=6)
    o += path("M30,148 L170,148 L164,166 Q160,182 144,182 L56,182 Q40,182 36,166Z", "#A9DDF2")
    o += rect(150, 128, 8, 16, "#9AA3C7", rx=3) + rect(144, 126, 22, 6, "#9AA3C7", rx=3)
    return o


@step
def breakfast():
    o = torso(150)
    o += cap(76, 116, 66, 132, 8, PJ) + cap(124, 116, 134, 124, 8, PJ)
    o += child_head("open", "smile")
    o += rect(8, 136, 184, 14, "#C98A52", rx=7) + rect(18, 148, 164, 8, "#A86F3C", rx=4)
    o += rect(24, 150, 10, 36, "#A86F3C", rx=4) + rect(166, 150, 10, 36, "#A86F3C", rx=4)
    o += path("M78,112 L122,112 A22,24 0 0 1 78,112Z", CB) + rect(76, 108, 48, 7, "#2563D8", rx=3.5)
    o += half(100, 109, 20, "#FFF1D0", ry=8)
    o += cap(108, 106, 138, 116, 3, "#9AA3C7") + ell(106, 104, 6, 4, "#9AA3C7")
    o += circle(136, 118, 8.5, SKIN) + circle(66, 132, 8.5, SKIN)
    o += rect(150, 104, 26, 34, "#CFE9FF", rx=5) + rect(153, 112, 20, 23, WHITE, rx=3)
    o += ell(40, 135, 24, 5, "#FFD45C")
    o += rect(24, 108, 30, 28, "#C9883E", rx=8) + rect(28, 112, 22, 21, "#F4CF8C", rx=5)
    return o


# ---------------------------------------------------------------- 烏雲 → 下雨 → 彩虹: the same sky and grass
CLOUD, CLOUDD = "#7A819E", "#5D6482"


def ground():
    o = rect(10, 166, 180, 22, "#7ED38E", rx=11)
    for x in (30, 70, 132, 168):
        o += cap(x, 168, x - 3, 160, 2.4, "#4FC461") + cap(x + 5, 168, x + 7, 159, 2.4, "#4FC461")
    return o


def dark_cloud(dx=0, dy=0):
    parts = lambda c, o_: (circle(68 + dx, 76 + dy + o_, 26, c) + circle(102 + dx, 58 + dy + o_, 34, c)  # noqa: E731
                           + circle(138 + dx, 74 + dy + o_, 26, c) + rect(42 + dx, 70 + dy + o_, 122, 32, c, rx=16))
    return parts(CLOUDD, 0) + parts(CLOUD, -6)


def drop(x, y, col=CB):
    return path(f"M{x},{y - 12} L{x + 6.5},{y} A6.5,6.5 0 1 1 {x - 6.5},{y}Z", col)


@step
def cloud():
    return ground() + dark_cloud()


@step
def rain():
    o = ground() + ell(100, 172, 44, 7, "#7FC8F8")
    for x, y in ((60, 116), (88, 124), (116, 116), (144, 124), (74, 146), (102, 152), (130, 146), (158, 150), (46, 142)):
        o += drop(x, y)
    return o + dark_cloud()


@step
def rainbow():
    o = ground() + ell(100, 172, 22, 4, "#7FC8F8")
    for i, c in enumerate((CR, ORANGE, CY, CG, CB, CP)):
        o += arc(100, 168, 86 - i * 9, 180, 360, 9.5, c, linecap="butt")
    o += circle(160, 40, 18, CY)
    for a in range(0, 360, 45):
        x0, y0 = pt(160, 40, 24, a)
        x1, y1 = pt(160, 40, 31, a)
        o += cap(x0, y0, x1, y1, 3, CY)
    for cx in (22, 178):
        o += circle(cx - 10, 160, 11, "#DCE1F6") + circle(cx + 4, 154, 14, "#DCE1F6") + rect(cx - 22, 156, 42, 14, "#DCE1F6", rx=7)
    return o


# ---------------------------------------------------------------- 毛毛蟲 → 蛹 → 蝴蝶
LEAF, LEAFL, CAT_B, CAT_S = "#22A65A", "#6FD88F", "#B9E35A", "#93C83A"


def leaf_big():
    o = lens(18, 156, 188, 112, 40, LEAF)
    o += stroke("M28,153 Q104,140 180,114", 3.5, LEAFL)
    for x, y, a in ((70, 145, 1), (110, 133, 1), (150, 121, 1)):
        o += stroke(f"M{x},{y} L{x - 14},{y - 18}", 2.6, LEAFL) + stroke(f"M{x},{y} L{x + 2},{y + 18}", 2.6, LEAFL)
    return o


@step
def caterpillar():
    o = leaf_big()
    seg = [(46, 132), (64, 124), (82, 116), (100, 112), (118, 112)]
    for x, y in seg:
        o += circle(x + 1.5, y + 13, 3.5, DK)
    for i, (x, y) in enumerate(seg):
        o += circle(x, y, 13, CAT_S if i % 2 else CAT_B)
        o += circle(x - 2, y - 5, 3, "#FFE066")
    hx, hy = 140, 100
    o += stroke(f"M{hx - 6},{hy - 14} Q{hx - 10},{hy - 30} {hx - 18},{hy - 34}", 3, DK) + circle(hx - 18, hy - 34, 4, DK)
    o += stroke(f"M{hx + 6},{hy - 14} Q{hx + 10},{hy - 30} {hx + 18},{hy - 34}", 3, DK) + circle(hx + 18, hy - 34, 4, DK)
    o += circle(hx, hy, 18, CAT_B)
    o += eye(hx - 6, hy - 2, 3.6) + eye(hx + 8, hy - 2, 3.6) + smile(hx + 1, hy + 7, 9, DK, 2.4)
    o += circle(hx - 12, hy + 6, 3.5, BLUSH, .9) + circle(hx + 14, hy + 6, 3.5, BLUSH, .9)
    return o


@step
def cocoon():
    o = cap(14, 36, 186, 28, 6, BR) + cap(150, 31, 170, 14, 4, BR)
    o += lens(132, 33, 178, 74, 14, LEAF) + stroke("M134,34 L172,68", 2.4, LEAFL)
    o += lens(40, 34, 18, 74, 10, LEAF)
    o += cap(98, 34, 98, 50, 1.6, "#BBA98E")
    o += path(lens_d(98, 46, 98, 162, 26), "#7FAE3E")
    o += path(lens_d(94, 46, 92, 158, 22), "#A3CB5B")
    for y in (118, 132, 146):
        o += stroke(f"M{78 + (y - 118) * .35},{y} Q98,{y + 6} {116 - (y - 118) * .35},{y}", 2.6, "#7FAE3E")
    o += shine_bar(84, 70, 8, 26, .45, rot=(10, 88, 83))
    return o


# ================================================================ the scene behind both games (390 x 844)
SW, SH_ = 390, 844


def soft(c, t=.62):
    """A palette colour made calm: mixed into the lilac background."""
    return mix(c, BG, t)


def dot_grid(y0, y1, col="#D3D6F5", step_=18, r=1.7):
    row = "".join(f"M{x - r},0 a{r},{r} 0 1 0 {2 * r},0 a{r},{r} 0 1 0 {-2 * r},0" for x in range(9, SW, step_))
    _DEFS.setdefault("dotrow", f'<path id="dotrow" d="{row}"/>')
    return "".join(f'<use href="#dotrow" x="0" y="{y}" fill="{col}"/>' for y in range(y0, y1, step_))


def block_tower(x, base, cols, w0=34, h=24, roof=None):
    o, y = "", base
    for i, c in enumerate(cols):
        w = w0 - i * 3
        o += rect(x - w / 2, y - h, w, h - 1, c, rx=3)
        y -= h
    if roof:
        o += poly([(x - w0 / 2 + 2, y), (x, y - 26), (x + w0 / 2 - 2, y)], roof, round_=3)
    return o


def castle(cx, base):
    pk, pu, bl, ye, re_, te = soft("#FF8FAB", .66), soft(CP, .77), soft(CB, .72), soft(CY, .66), soft(CR, .7), soft(CT, .64)
    o = rect(cx - 82, base - 92, 164, 92, pk)
    for x in range(-82, 82, 28):
        o += rect(cx + x, base - 106, 18, 16, pk)
    for sx in (-1, 1):
        x = cx + sx * 92
        o += rect(x - 15, base - 132, 30, 132, pu) + poly([(x - 21, base - 132), (x, base - 172), (x + 21, base - 132)], bl)
        o += rect(x - 6, base - 112, 12, 18, BG, rx=6)
    o += rect(cx - 26, base - 150, 52, 72, ye) + poly([(cx - 34, base - 150), (cx, base - 196), (cx + 34, base - 150)], re_)
    o += rect(cx - 1.5, base - 226, 3, 32, soft(DK, .7)) + poly([(cx + 1, base - 226), (cx + 24, base - 218), (cx + 1, base - 210)], te)
    o += circle(cx, base - 120, 11, BG)
    o += path(f"M{cx - 22},{base} L{cx - 22},{base - 30} A22,22 0 0 1 {cx + 22},{base - 30} L{cx + 22},{base}Z", soft(DK, .74))
    for x in (-60, 46):
        o += rect(cx + x, base - 66, 14, 18, BG, rx=7)
    return o


def cloud_c(cx, cy, s, col):
    return (circle(cx - 18 * s, cy, 16 * s, col) + circle(cx + 4 * s, cy - 10 * s, 22 * s, col) + circle(cx + 24 * s, cy, 14 * s, col)
            + rect(cx - 34 * s, cy, 72 * s, 16 * s, col, rx=8 * s))


def scene_kingdom():
    o = rect(0, 0, SW, SH_, BG)
    o += dot_grid(9, SH_)
    # far sky: a calm sun and clouds
    o += circle(58, 168, 24, soft(CY, .6))
    o += cloud_c(306, 112, 1.1, "#F8F8FF") + cloud_c(104, 124, .8, "#F8F8FF")
    # hills and the block castle on the horizon (y 300)
    o += half(60, 304, 110, soft(CG, .78), ry=48) + half(330, 304, 120, soft(CG, .74), ry=56)
    o += castle(205, 304)
    o += block_tower(26, 304, [soft(CR), soft(CB), soft(CY), soft(CG)], 34, 22, soft(CP, .7))
    o += block_tower(374, 304, [soft(CG), soft(CY), soft(CB)], 32, 22, soft(CR, .66))
    o += block_tower(88, 304, [soft(CY), soft(CP, .7)], 26, 20)
    o += rect(0, 300, SW, 6, soft(CG, .66))
    # foreground floor (y 704 down): a row of blocks and quiet tiles
    o += rect(0, 704, SW, SH_ - 704, "#E3E1FA")
    for row, y in enumerate(range(726, SH_, 30)):
        off = 15 if row % 2 else 0
        for x in range(-30 + off, SW, 60):
            o += rect(x + 3, y, 54, 26, "#DAD6F7", rx=4)
    cols = [soft(CB), soft(CY), soft(CR), soft(CG), soft(CP, .7), soft(CT)]
    for i, x in enumerate(range(0, SW, 26)):
        o += rect(x + 1, 704, 24, 16, cols[i % len(cols)], rx=3)
    return o


# ================================================================ output
def thing_svg(name):
    begin()
    f, box, dy = THINGS[name]
    return doc(fit(f(), box, dy=dy))


def seq_svg(name):
    begin()
    return doc(SEQ[name]())


def scene_svg():
    begin()
    return doc(scene_kingdom(), SW, SH_)


SEQUENCES = [("chicken", ["egg", "chick", "hen"]), ("flower", ["seed", "sprout", "flower"]),
             ("dressing", ["bare_foot", "sock_on", "shoe_on"]), ("morning", ["wake_up", "brushing", "breakfast"]),
             ("rain", ["cloud", "rain", "rainbow"]), ("butterfly", ["caterpillar", "cocoon", "butterfly"])]


def all_svgs():
    out = {name: thing_svg(name) for name in THINGS}
    for name in SEQ:
        out[name] = seq_svg(name)
    out["scene_kingdom"] = scene_svg()
    return out


def export():
    svgs = all_svgs()
    for name, svg in svgs.items():
        write(name, svg)
    print(f"wrote {len(svgs)} pictures to {OUT}")


def preview(out):
    svgs = all_svgs()
    css = ("body{margin:0;padding:16px;background:#EEF0FF;font:13px sans-serif;color:#2B2D42;width:1640px}"
           "h2{margin:18px 0 8px}.row{display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end}"
           ".c{background:#fff;border-radius:16px;padding:6px;text-align:center}.c img{display:block}"
           ".seq{display:flex;gap:10px;align-items:flex-end;margin-bottom:10px}")

    def card(name, size):
        p = OUT / f"{name}.svg"
        return f'<div class="c"><img src="file://{p}" width="{size}" height="{size}"><div>{name}</div></div>'

    things = list(THINGS)
    h = [f"<style>{css}</style><h2>哪個不一樣？ things (200 px)</h2><div class='row'>"]
    h += [card(nm, 200) for nm in things] + ["</div><h2>at 120 px</h2><div class='row'>"]
    h += [card(nm, 120) for nm in things] + ["</div><h2>接下來是什麼？ sequences (200 px and 120 px)</h2>"]
    for sid, steps in SEQUENCES:
        h.append("<div class='seq'>" + "".join(card(s, 200) for s in steps) + "<div style='width:30px'></div>"
                 + "".join(card(s, 120) for s in steps) + "</div>")
    p = OUT / "scene_kingdom.svg"
    h.append(f"<h2>scene_kingdom</h2><div class='row'><img src='file://{p}' width='390' height='844'>"
             f"<img src='file://{p}' width='195' height='422'></div>")
    render_html("".join(h), out, 1672, 800)
    _ = svgs


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "export"
    if cmd == "export":
        export()
    elif cmd == "preview":
        export()
        preview(sys.argv[2] if len(sys.argv) > 2 else "/tmp/blocks_preview.png")
    else:
        raise SystemExit(__doc__)
