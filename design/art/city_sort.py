"""放哪裡？ (put things back where they belong) pictures for 卡通城, style A 「動畫片風」.

    python3 city_sort.py                  # writes every picture to app/assets/art/city/
    python3 city_sort.py preview OUT.png  # contact sheet: the things at 200 and 120 px, the places,
                                          # and the six scenes with their places laid out (needs
                                          # Node.js + Playwright)

What it draws (ids exactly as in app/lib/core/content.dart: sortScenes, sortThings):
  scene_<id>   six backgrounds, 390 x 600, painted edge to edge, calm and low in contrast: only the
               backdrop (walls, floor, sky...), never a place or a thing
  places       200 x 200, transparent: where things go, each with an obvious opening. The app lays
               a place over its scene as a square `w` of the scene's width wide, centred at (x, y)
               (fractions of the scene). Each place is drawn where it should stand inside its square
               (standing ones touch the bottom edge and carry a soft ground shadow), and its outline
               is thick enough to be about 2.3 px on screen at that width (read from content.dart)
  things       200 x 200, transparent, centred, the longer side 85 % of the box (FILL)

Shared style-A helpers are in city_kit.py.
"""
import math
import pathlib
import random
import re
import subprocess
import sys
import tempfile

import city_kit as K
from city_kit import (BLUE, BROWN, CREAM, GOLD, GREEN, ORANGE, PINK, PURPLE, RED, SKY, TEAL, WHITE, WHITE_OL,
                      WOOD, YELLOW, at, blob, blush, calm, celov, clipped, cloud_d, comp, dk, dot_eye, drop_d, ell,
                      eye, fit, flat, g, ground, happy_eye, hi, hidot, hose, lg, lin, ln, lt, mix, n, open_mouth, part,
                      poly, rg, rr, save, shd, smile, sparkle, spline, star_d, stroke, tone, tube)

CONTENT = K.ROOT / "app" / "lib" / "core" / "content.dart"


# ================================================================ THINGS (200 x 200, in their own units)
THINGS = {}


def thing(box):
    """Register a thing drawing: box = (x0, y0, x1, y1), how far it reaches in its own units."""
    def deco(f):
        THINGS[f.__name__] = (f, box)
        return f
    return deco


# ---------------------------------------------------------------- 房間
@thing((-46, -46, 46, 46))
def ball():
    c = ell(0, 0, 42)
    P = (-12, -14)
    cols = [RED, WHITE, BLUE, YELLOW, WHITE, GREEN]
    wed = ""
    for i in range(6):
        a0, a1 = math.radians(i * 60 + 15), math.radians(i * 60 + 75)
        f0 = (P[0] + 120 * math.cos(a0), P[1] + 120 * math.sin(a0))
        f1 = (P[0] + 120 * math.cos(a1), P[1] + 120 * math.sin(a1))
        c0 = (P[0] + 50 * math.cos(a0 + .42), P[1] + 50 * math.sin(a0 + .42))
        c1 = (P[0] + 50 * math.cos(a1 + .42), P[1] + 50 * math.sin(a1 + .42))
        d = (f"M{n(P[0])},{n(P[1])} Q{n(c0[0])},{n(c0[1])} {n(f0[0])},{n(f0[1])} L{n(f1[0])},{n(f1[1])} "
             f"Q{n(c1[0])},{n(c1[1])} {n(P[0])},{n(P[1])}Z")
        wed += flat(d, cols[i])
    inner = wed + part(ell(P[0], P[1], 7), WHITE, s=None, ol=WHITE_OL, k=.7)
    o = comp(c, WHITE, inner, s=None, ol=False)
    o += celov(c, (-8, -9), .2) + hi("M-30,-6 A30,30 0 0 1 -14,-30", 5, .7) + K.stroke(c, "#6E5A8A")
    return o


def _block(x, y, s, col, emblem):
    dp = s * .2
    o = part(poly([(x + s, y), (x + s + dp, y - dp), (x + s + dp, y + s - dp), (x + s, y + s)]), shd(col), s=None, ol=lin(col))
    o += part(poly([(x, y), (x + dp, y - dp), (x + s + dp, y - dp), (x + s, y)]), lt(col, .35), s=None, ol=lin(col))
    inner = part(rr(x + 7, y + 7, s - 14, s - 14, 5), lt(col, .22), s=None, ol=False)
    cx, cy = x + s / 2, y + s / 2
    if emblem == "star":
        inner += part(star_d(s * .3, s * .14, cx=cx, cy=cy + 1, round_=.18), "#FFFFFF", s=None, ol=lin(col), k=.7)
    elif emblem == "heart":
        inner += part(K.heart_d(s * .016, cx, cy + 2), "#FFFFFF", s=None, ol=lin(col), k=.7)
    else:
        inner += part(ell(cx, cy, s * .22), "#FFFFFF", s=None, ol=lin(col), k=.7)
    return o + comp(rr(x, y, s, s, 4), col, inner, s=(-5, -6), hl=hi(f"M{n(x + 5)},{n(y + s * .3)} L{n(x + 5)},{n(y + 6)}", 3, .6))


@thing((-70, -82, 72, 58))
def blocks():
    o = _block(-68, 0, 58, RED, "star")
    o += _block(4, 0, 58, BLUE, "circle")
    o += _block(-30, -60, 58, YELLOW, "heart")
    return o


@thing((-92, -66, 96, 44))
def toy_car(col=RED):
    body = ("M-82,8 L-82,-12 C-82,-20 -76,-25 -68,-25 L-48,-26 L-32,-52 C-28,-58 -22,-60 -14,-60 L28,-60 "
            "C36,-60 42,-57 47,-51 L64,-28 L76,-26 C84,-24 88,-18 88,-10 L88,8 C88,14 84,18 78,18 L-76,18 C-80,18 -82,14 -82,8 Z")
    o = part(body, col, s=(-9, -10), hl=hi("M-70,-16 L-40,-16", 5, .6))
    o += part("M-38,-28 L-26,-50 C-24,-53 -21,-54 -17,-54 L-2,-54 L-2,-28 Z", K.GLASS, s=None, ol=lin(col))
    o += part("M6,-54 L26,-54 C31,-54 35,-52 38,-48 L52,-28 L6,-28 Z", K.GLASS, s=None, ol=lin(col))
    o += hi("M-28,-34 L-20,-48 M14,-34 L22,-48", 3.5, .9)
    o += part(rr(76, -18, 12, 8, 3), "#FFE066", s=None, ol=lin(col))
    o += part(rr(-86, -6, 10, 8, 3), "#FF7A6E", s=None, ol=lin(col))
    o += ln("M2,-26 L2,12", lin(col), .62)
    for x in (-48, 52):
        o += part(ell(x, 18, 19), "#3E3A4A", s=(-3, -4), ol="#221E2C")
        o += part(ell(x, 18, 8.5), "#D7D3E2", s=None, ol="#6E6880")
    return o


@thing((-78, -64, 74, 62))
def book(col="#FF7A59"):
    o = part(rr(-60, -44, 128, 94, 8), "#FFF3D9", s=None, ol="#C9A77A")
    o += "".join(ln(f"M{x},-40 L{x},46", "#D9C19A", .62) for x in (62, 65))
    cover = rr(-68, -52, 128, 94, 9)
    o += part(cover, col, s=(-6, -7))
    o += part(rr(-68, -52, 18, 94, 7), shd(col), s=None, ol=lin(col))
    win = rr(-40, -38, 88, 66, 10)
    o += comp(win, "#BFE8FF", part(ell(-14, 44, 70, 36), "#7BD36A", s=None, ol=lin("#7BD36A"))
              + part(ell(26, -14, 11), YELLOW, s=None, ol=lin(YELLOW)), s=None, ol=lin(col))
    return g(o, "rotate(-6)")


@thing((-46, -76, 80, 72))
def sock(col="#FF8FB1"):
    leg = ("M-22,-56 L20,-56 L20,6 C20,14 26,19 34,21 L56,27 C70,31 76,46 70,57 C64,67 50,69 38,65 "
           "L-6,52 C-20,48 -26,36 -24,22 Z")
    inner = "".join(flat(f"M-40,{y} L40,{y} L40,{y + 9} L-40,{y + 9} Z", "#FFFFFF") for y in (-38, -18))
    inner += part(ell(66, 52, 20), "#B67CF0", s=None, ol=lin("#B67CF0")) + part(ell(-24, 44, 16), "#B67CF0", s=None, ol=lin("#B67CF0"))
    o = comp(leg, col, inner, s=(-7, -8), hl=hi("M-14,-2 L-14,24", 4, .55))
    o += part(rr(-28, -70, 54, 18, 6), "#FFFFFF", s=(-2, -3), ol=lin(col))
    o += "".join(ln(f"M{x},-66 L{x},-56", "#E4A6C0", .62) for x in (-18, -9, 0, 9, 18))
    return g(o, "rotate(-8)")


@thing((-80, -60, 80, 66))
def tshirt(col="#36C46E"):
    d = ("M-24,-56 C-14,-47 14,-47 24,-56 L58,-42 C64,-40 68,-36 70,-30 L78,-10 L52,0 L46,-12 L46,56 "
         "C46,60 42,63 38,63 L-38,63 C-42,63 -46,60 -46,56 L-46,-12 L-52,0 L-78,-10 L-70,-30 C-68,-36 -64,-40 -58,-42 Z")
    o = part(d, col, s=(-8, -9), hl=hi("M-36,-30 L-36,40", 5, .45))
    o += part("M-24,-56 C-14,-44 14,-44 24,-56 C16,-38 -16,-38 -24,-56 Z", shd(col), s=None)
    o += part(star_d(22, 10, round_=.16, cx=0, cy=10), YELLOW, s=(-2, -3))
    o += ln("M-46,-12 L-46,0 M46,-12 L46,0", lin(col), .62)
    return o


@thing((-76, -46, 76, 46))
def pillow(col="#B9DCFF"):
    d = "M-72,-42 C-40,-31 40,-31 72,-42 C63,-14 63,14 72,42 C40,31 -40,31 -72,42 C-63,14 -63,-14 -72,-42Z"
    dots = "".join(part(star_d(6, 2.8, cx=x, cy=y, round_=.2), "#FFFFFF", s=None, ol=False)
                   for x, y in ((-38, -12), (-6, 8), (28, -14), (46, 16), (-30, 20), (10, -20)))
    o = comp(d, col, dots, s=(-9, -10), hl=hi("M-54,-24 C-30,-19 -4,-19 16,-21", 5, .75))
    o += ln("M-60,-33 C-34,-25 34,-25 60,-33 M-60,33 C-34,25 34,25 60,33", lin(col), .5, op=.5)
    return o


# ---------------------------------------------------------------- 浴室
@thing((-96, -60, 98, 48))
def toothbrush(col="#2EC4C0"):
    o = []
    handle = ("M-92,6 C-92,-2 -88,-6 -80,-6 L20,-8 C30,-8 38,-6 46,-4 L92,-6 C96,-6 98,-2 98,2 L98,10 "
              "C98,14 96,16 92,16 L46,14 C38,16 30,18 20,18 L-80,18 C-88,18 -92,14 -92,6 Z")
    o.append(part(handle, col, s=(-4, -6), hl=hi("M-78,-1 L10,-3", 4, .7)))
    o.append(part(rr(-56, -3, 34, 16, 8), "#FF8FB1", s=(-2, -3)))
    block = "M44,-8 L44,-36 C44,-40 46,-42 50,-42 L88,-42 C92,-42 94,-40 94,-36 L94,-8 Z"
    tops = "M30,-60 L110,-60 L110,-30 L30,-30 Z"
    o.append(comp(block, "#FFFFFF", flat(tops, "#7CC7FF") + "".join(ln(f"M{x},-41 L{x},-9", "#9AA9C8", .62) for x in (54.5, 65, 75.5, 85)),
                  s=(-3, -4)))
    return g("".join(o), "rotate(-28)")


@thing((-84, -54, 86, 52))
def toothpaste():
    body = "M-70,-22 L-70,22 L-62,22 C-30,24 20,26 46,16 L46,-16 C20,-26 -30,-24 -62,-22 Z"
    inner = flat("M-30,-40 L18,-40 L18,40 L-30,40 Z", BLUE)
    inner += flat("M-30,-4 C-18,-12 -6,4 6,-4 C10,-7 14,-6 18,-4 L18,4 C10,0 6,8 -6,6 C-18,4 -22,-2 -30,6Z", "#FFFFFF")
    inner += flat("M30,-40 L36,-40 L36,40 L30,40Z", RED)
    o = comp(body, "#FFFFFF", inner, s=(-4, -6), ol="#7A86B8", hl=hi("M-58,-14 L-38,-15", 3, .8))
    o += ln("M-66,-18 L-66,18", "#7A86B8", .62)
    o += part("M46,-16 L58,-11 L58,11 L46,16 Z", "#FFFFFF", s=None, ol="#7A86B8")
    o += part(rr(57, -13, 22, 26, 5), RED, s=(-2, -3))
    o += "".join(ln(f"M{x},-13 L{x},13", lin(RED), .62) for x in (63, 68, 73))
    return g(o, "rotate(-16)")


@thing((-66, -80, 66, 80))
def towel(col="#FFA94D"):
    back = "M-44,-66 C-44,-74 -38,-78 -30,-78 L44,-78 C52,-78 58,-72 58,-64 L60,58 L-42,58 Z"
    front = "M-58,-62 C-58,-70 -52,-74 -44,-74 L40,-74 C48,-74 54,-68 54,-60 L56,66 L-60,66 Z"
    o = part(back, shd(col), s=None, ol=lin(col))
    stripes = (flat("M-70,30 L70,30 L70,42 L-70,42Z", "#FFFFFF") + flat("M-70,48 L70,48 L70,53 L-70,53Z", "#FFFFFF")
               + flat("M-70,-40 L70,-40 L70,-46 L-70,-46Z", lt(col, .45)))
    fold = flat("M-70,-80 L70,-80 L70,-52 C30,-46 -30,-46 -70,-52Z", lt(col, .25))
    o += comp(front, col, fold + stripes, s=(-8, -9), hl=hi("M-46,-32 L-46,18", 5, .5))
    o += ln("M-58,-50 C-30,-45 30,-45 54,-50", lin(col), .62)
    o += "".join(ln(f"M{x},66 L{x - 1},76", lin(col), .7) for x in range(-54, 56, 9))
    return o


@thing((-86, -70, 78, 58))
def rubber_duck(col="#FFD43B"):
    o = ""
    body = ("M-66,8 C-66,-14 -40,-20 -10,-14 C14,-10 34,-12 50,-24 C58,-30 66,-36 71,-31 C78,-10 74,18 58,34 "
            "C42,50 10,56 -20,52 C-48,48 -66,32 -66,8Z")
    o += part(body, col, s=(-9, -10), hl=hi("M-52,6 C-50,22 -38,34 -22,38", 5, .6))
    o += part("M-4,6 C10,-8 38,-6 46,8 C38,24 12,28 -4,6Z", lt(col, .1), s=(-3, -4), ol=lin(col))
    o += ln("M8,10 C18,8 30,10 36,14", lin(col), .62)
    o += part(ell(-30, -36, 30, 28), col, s=(-6, -7), hl=hi("M-48,-46 C-44,-56 -36,-61 -28,-62", 4, .7))
    o += part("M-56,-36 C-70,-42 -86,-36 -84,-26 C-82,-18 -66,-18 -56,-24Z", ORANGE, s=(-2, -3))
    o += ln("M-84,-28 C-74,-28 -64,-29 -57,-30", lin(ORANGE), .62)
    o += eye(-34, -44, 8.5, 10, -1.5, 1, ol="#8A6410")
    o += blush(-20, -28, 7, 4.5)
    return o


@thing((-68, -88, 68, 40))
def soap(col="#FF9EC4"):
    body = ("M-64,-12 C-64,-28 -50,-34 -36,-34 L36,-34 C50,-34 64,-28 64,-12 L64,14 C64,30 50,36 36,36 "
            "L-36,36 C-50,36 -64,30 -64,14Z")
    top = "M-56,-14 C-56,-24 -46,-28 -34,-28 L34,-28 C46,-28 56,-24 56,-14 C56,-4 46,0 34,0 L-34,0 C-46,0 -56,-4 -56,-14Z"
    o = part(body, col, s=(-7, -8))
    o += part(top, lt(col, .3), s=None, ol=lin(col), k=.7, hl=hi("M-44,-20 L-20,-22", 3.5, .8))
    o += g(ln(K.heart_d(.8, 0, 0), lin(col), .62), "translate(0 -14) scale(1 .62)")
    for x, y, r in ((-30, -48, 13), (2, -62, 18), (32, -46, 11), (46, -74, 8), (-48, -70, 7)):
        o += part(ell(x, y, r), "#EAF6FF", s=None, ol="#7FB8E0", k=.7, hl=hidot(x - r * .35, y - r * .35, r * .28))
    return o


# ---------------------------------------------------------------- 廚房
@thing((-40, -72, 40, 64))
def milk():
    o = part("M-30,-36 L0,-62 L30,-36 Z", "#FFFFFF", s=None, ol="#5A86D6")
    o += part(rr(-6, -72, 12, 12, 2), "#FFFFFF", s=None, ol="#5A86D6")
    body = rr(-30, -36, 60, 96, 4)
    o += comp(body, "#FFFFFF", flat("M-40,10 L40,10 L40,70 L-40,70Z", "#5A9BEA")
              + flat("M-40,4 C-20,-2 -10,14 6,8 C18,4 26,0 40,4 L40,14 L-40,14Z", "#5A9BEA"), s=(-6, -7), ol="#5A86D6")
    o += flat("M-8,-28 C0,-30 8,-24 6,-16 C4,-10 -4,-8 -10,-12 C-16,-16 -14,-26 -8,-28Z", "#3A3446")
    o += flat("M14,-10 C20,-12 26,-6 24,0 C22,4 16,4 13,0 C10,-4 10,-8 14,-10Z", "#3A3446")
    o += flat("M-22,-8 C-18,-10 -14,-6 -16,-2 C-18,2 -24,0 -24,-4Z", "#3A3446")
    o += part(drop_d(0, 22, 1.2), "#FFFFFF", s=None, ol="#3F6FC0", k=.7)
    o += hi("M-20,-26 L-20,0", 4, .7)
    return o


def _bok_leaf(a):
    stem = tube([(0, 66, 9), (0, 26, 12), (0, -12, 14)])
    blade = "M0,-96 C27,-94 38,-60 32,-32 C27,-12 13,-2 0,-2 C-13,-2 -27,-12 -32,-32 C-38,-60 -27,-94 0,-96Z"
    o = part(stem, "#D3F0AE", s=(-3, -4), ol="#6FA84A")
    o += part(blade, "#3FAE4A", s=(-5, -6), hl=hi("M-18,-70 C-14,-82 -8,-88 -2,-90", 3.5, .5))
    o += ln("M0,-86 L0,-4", "#A8DB7E", 1.0)
    o += ln("M0,-60 L-18,-72 M0,-40 L-22,-50 M0,-60 L18,-72 M0,-40 L22,-50 M0,-22 L-16,-30 M0,-22 L16,-30", "#2E8A3A", .55)
    return g(o, f"rotate({a} 0 66)")


@thing((-92, -100, 92, 76))
def vegetables():
    o = "".join(_bok_leaf(a) for a in (-30, 30, -15, 15, 0))
    o += part(rr(-25, 34, 50, 11, 5), RED, s=(-2, -3))
    return o


@thing((-80, -40, 80, 66))
def bowl(col="#FFFFFF"):
    blue = "#4F7FD8"
    o = part(rr(-26, 46, 52, 14, 5), col, s=(-2, -3), ol="#6F7FB8")
    body = "M-76,-14 C-74,28 -42,54 0,54 C42,54 74,28 76,-14 Z"
    band = flat("M-90,4 L90,4 L90,13 L-90,13Z", blue) + "".join(
        part(ell(x, 30, 5), blue, s=None, ol=False) for x in (-40, -20, 0, 20, 40))
    o += comp(body, col, band, s=(-10, -9), ol="#6F7FB8", hl=hi("M-60,8 C-54,24 -42,34 -28,40", 5, .9))
    o += part(ell(0, -14, 76, 17), "#E6EAF8", s=None, ol="#6F7FB8")
    o += flat("M-66,-12 C-50,-24 50,-24 66,-12 C40,-4 -40,-4 -66,-12Z", "#D5DBF0")
    o += sparkle(54, -30, 9, GOLD) + sparkle(68, -6, 5, GOLD) + sparkle(-56, -32, 6, GOLD)
    return o


@thing((-86, -44, 86, 44))
def plate(col="#FFFFFF"):
    rim = "#6FC2F5"
    o = part(ell(0, 6, 82, 34), "#DDE3F4", s=None, ol="#6F7FB8")
    o += part(ell(0, 0, 82, 34), col, s=(-6, -6), ol="#6F7FB8")
    o += part(ell(0, 0, 76, 30) + " " + ell(0, 0, 68, 26), rim, s=None, ol=False, fr=True)
    o += part(ell(0, 0, 50, 17), "#EEF1FB", s=None, ol="#B9C3E6", k=.7)
    o += hi("M-40,-16 C-28,-21 -14,-23 0,-23", 4, .9)
    o += sparkle(46, -28, 9, GOLD) + sparkle(62, -12, 5, GOLD) + sparkle(-52, -26, 6, GOLD)
    return o


@thing((-62, -64, 80, 70))
def dirty_cup(col="#7DC4F5"):
    brown = "#8A5A36"
    o = f'<ellipse cx="2" cy="58" rx="56" ry="10" fill="none" stroke="{brown}" stroke-width="{K.sw(1.4)}" opacity=".55"/>'
    o += f'<path d="M-40,62 C-30,70 0,72 24,66" fill="none" stroke="{brown}" stroke-width="{K.sw(1)}" opacity=".4" stroke-linecap="round"/>'
    o += part("M40,-28 C72,-32 76,26 38,26 L38,14 C58,14 58,-14 40,-16Z", col, s=(-3, -4))
    body = "M-46,-40 L46,-40 L42,40 C42,48 36,54 28,54 L-28,54 C-36,54 -42,48 -42,40Z"
    drips = (flat("M20,-36 L20,-2 C20,6 30,6 30,-2 L30,-36Z", brown)
             + flat("M-28,-36 L-28,-18 C-28,-12 -21,-12 -21,-18 L-21,-36Z", brown)
             + flat("M-60,-44 L60,-44 L60,-34 L-60,-34Z", brown))
    o += comp(body, col, drips, s=(-9, -10), hl=hi("M-34,-24 L-32,30", 5, .55))
    o += part(ell(0, -40, 46, 15), "#E8F4FC", s=None, ol=lin(col))
    o += clipped(ell(0, -40, 46, 15), flat(ell(2, -30, 34, 10), "#7A4A2C") + flat(ell(-6, -32, 14, 3), "#A9775A"))
    o += ln("M-38,-44 C-20,-36 20,-36 38,-44", brown, .7, op=.6)
    return o


@thing((-54, -122, 54, 98))
def ice_cream():
    o = ""
    cone = "M-38,-4 L38,-4 L4,92 C2,97 -2,97 -4,92Z"
    waffle = "".join(ln(f"M{x},-10 L{x + 60},90", "#B9773A", .6) for x in range(-90, 50, 15))
    waffle += "".join(ln(f"M{x},-10 L{x - 60},90", "#B9773A", .6) for x in range(-40, 100, 15))
    o += comp(cone, "#EDB062", waffle, s=(-6, -7))
    scoop = ("M-46,-4 C-52,-30 -30,-54 0,-54 C30,-54 52,-30 46,-4 C40,4 32,-2 26,4 C20,10 12,4 4,8 "
             "C-4,12 -12,4 -20,6 C-28,8 -40,4 -46,-4Z")
    o += part(scoop, "#9BE3C3", s=(-7, -8), hl=hi("M-32,-24 C-28,-36 -18,-44 -8,-46", 5, .7))
    o += g(part(scoop, "#FF9EBB", s=(-7, -8), hl=hi("M-32,-24 C-28,-36 -18,-44 -8,-46", 5, .7)), "translate(0 -40) scale(.86)")
    for x, y, a, c in ((-18, -66, 30, YELLOW), (10, -74, -40, BLUE), (24, -58, 70, "#FFFFFF"), (-4, -56, -10, GREEN), (-24, -50, 80, "#FFFFFF")):
        o += g(part(rr(-5, -2, 10, 4, 2), c, s=None, ol=lin(c) if c != "#FFFFFF" else "#E07A9A", k=.5), f"translate({x} {y}) rotate({a})")
    o += ln("M6,-100 C8,-108 14,-114 20,-118", "#6B4A26", 1.2)
    o += part(ell(4, -94, 11), RED, s=(-2, -3), hl=hidot(0, -98, 3))
    return o


# ---------------------------------------------------------------- 大自然
@thing((-70, -84, 84, 50))
def bird(col="#4FA8F5"):
    o = part("M10,-14 C2,-50 22,-72 44,-80 C50,-58 42,-30 26,-10Z", shd(col), s=None)
    o += part("M38,4 L80,-12 C84,-4 80,6 74,8 C82,14 82,26 74,28 L36,22Z", col, s=(-3, -4))
    body = ell(0, 0, 46, 40)
    o += comp(body, col, flat(ell(-8, 30, 36, 26), "#FFE48A"), s=(-8, -9), hl=hi("M-30,-22 C-22,-32 -10,-36 2,-36", 5, .65))
    o += part("M-8,-12 C-14,-52 4,-76 30,-82 C36,-58 30,-30 14,-8Z", lt(col, .18), s=(-3, -4), ol=lin(col))
    o += ln("M2,-30 C8,-46 16,-58 24,-66 M-2,-20 C6,-32 12,-40 20,-48", lin(col), .55)
    o += part("M-42,-8 L-66,0 L-42,10 Z", ORANGE, s=None)
    o += eye(-20, -10, 10, 12, -2, 1, ol="#2E5A8A")
    o += blush(-26, 12, 7, 4.5)
    o += ln("M-6,40 L-8,48 M8,40 L8,48", ORANGE, 1.2)
    return o


def _critter_squirrel():
    fur, li = "#D9874A", "#FBE3C4"
    o = []
    tail = blob([(24, 88), (66, 86), (96, 56), (104, 12), (92, -30), (64, -48), (40, -40), (58, -18), (68, 14), (58, 44), (34, 56)])
    o.append(comp(tail, fur, flat(blob([(58, -30), (82, -10), (86, 24), (72, 50), (66, 20), (62, -6)]), li), s=(-7, -8)))
    body = "M-32,14 C-44,36 -46,70 -36,86 C-24,98 24,98 36,86 C46,70 44,36 32,14 Z"
    o.append(comp(body, fur, part(ell(0, 62, 20, 24), li, s=None, ol=lin(fur)), s=(-7, -8)))
    for sx in (-1, 1):
        o.append(part(ell(sx * 19, 94, 16, 9), fur, s=(-2, -3)))
    # an acorn held in both paws
    o.append(part(ell(0, 56, 13, 15), "#C98A4E", s=(-2, -3), hl=hidot(-4, 52, 2.5)))
    o.append(part("M-15,46 C-15,36 15,36 15,46 C10,49 -10,49 -15,46Z", "#8A5A35", s=None))
    o.append(ln("M0,38 L2,32", "#6B4A26", 1))
    for sx in (-1, 1):
        o.append(part(tube([(sx * 30, 30, 8.5), (sx * 26, 46, 8), (sx * 14, 54, 7.5)]), fur, s=(-2, -3)))
    for sx in (-1, 1):
        o.append(g(part("M-12,8 C-14,-10 -6,-26 2,-30 C8,-20 12,-6 12,8 Z", fur, s=(-2, -3))
                   + flat("M-5,4 C-6,-8 -2,-16 2,-19 C5,-12 6,-4 5,4 Z", "#FFC2D1"), f"translate({sx * 34} -62) rotate({sx * 12})"))
    head = ell(0, -24, 56, 46)
    o.append(comp(head, fur, "", s=(-9, -9), hl=hi("M-34,-52 C-24,-64 -10,-68 4,-68", 5, .55)))
    o.append(part(ell(0, -8, 20, 15), li, s=None, ol=lin(fur)))
    o.append(eye(-21, -26, 11, 13, .5, 1.5, ol="#4A3346"))
    o.append(eye(21, -26, 11, 13, .5, 1.5, ol="#4A3346"))
    o.append(blush(-36, -6, 8, 5) + blush(36, -6, 8, 5))
    o.append(part("M-6,-12 C-6,-16 6,-16 6,-12 C6,-8 2,-5 0,-5 C-2,-5 -6,-8 -6,-12Z", "#5A3424", s=None))
    o.append(ln("M-9,0 Q-4,5 0,-3 Q4,5 9,0", "#4A3346", .9))
    return "".join(o)


@thing((-70, -100, 108, 104))
def squirrel():
    return _critter_squirrel()


@thing((-78, -96, 92, 104))
def monkey():
    fur, face, li = "#A88A6C", "#F6B8A6", "#E9D3B8"
    o = []
    o.append(part(tube([(30, 84, 7), (58, 80, 6.5), (70, 62, 6), (62, 50, 5.5)]), fur, s=(-2, -3)))
    body = "M-30,12 C-42,34 -44,66 -34,84 C-22,96 22,96 34,84 C44,66 42,34 30,12 Z"
    o.append(comp(body, fur, part(ell(0, 58, 21, 26), li, s=None, ol=lin(fur)), s=(-7, -8)))
    for sx in (-1, 1):
        o.append(part(ell(sx * 20, 94, 17, 9), face, s=(-2, -3), ol="#C98272"))
    o.append(part(tube([(-28, 26, 8.5), (-46, 48, 8), (-50, 70, 8)]), fur, s=(-2, -3))
             + part(ell(-50, 74, 9.5), face, s=(-2, -2.5), ol="#C98272"))
    o.append(part(tube([(28, 24, 8.5), (50, 6, 8), (64, -26, 8)]), fur, s=(-2, -3))
             + part(ell(66, -32, 10), face, s=(-2, -2.5), ol="#C98272"))
    o.append(ln("M78,-50 Q86,-42 86,-30 M84,-60 Q96,-48 96,-30", "#C9A07A", 1.2))
    for sx in (-1, 1):
        o.append(part(ell(sx * 50, -30, 15, 17), fur, s=(-3, -4)) + flat(ell(sx * 50, -30, 8, 10), face))
    head = ell(0, -32, 50, 46)
    tuft = "M-14,-74 C-10,-90 -2,-96 4,-94 C2,-86 4,-80 8,-76 C10,-86 18,-90 22,-86 C18,-80 18,-74 20,-70Z"
    o.append(part(tuft, fur, s=None))
    o.append(comp(head, fur, "", s=(-8, -8), hl=hi("M-30,-62 C-22,-72 -10,-76 2,-76", 5, .5)))
    mask = "M0,-52 C8,-66 38,-66 40,-40 C42,-16 24,6 0,8 C-24,6 -42,-16 -40,-40 C-38,-66 -8,-66 0,-52Z"
    o.append(part(mask, face, s=(-3, -4), ol="#C98272"))
    o.append(eye(-17, -36, 10, 12, .5, 1.5, ol="#5A3424"))
    o.append(eye(17, -36, 10, 12, .5, 1.5, ol="#5A3424"))
    o.append(flat(ell(-4, -16, 2.2, 3), "#7A3E2C") + flat(ell(4, -16, 2.2, 3), "#7A3E2C"))
    o.append(blush(-28, -14, 7, 4.5, "#FF7E8E") + blush(28, -14, 7, 4.5, "#FF7E8E"))
    o.append(smile(0, -6, 20, "#7A3E2C"))
    return "".join(o)


def _cow_head():
    o = []
    for sx in (-1, 1):
        o.append(g(part(ell(0, 0, 22, 11), "#FFFFFF", s=(-2, -3), ol="#7A7088") + flat(ell(2, 0, 12, 6), "#FFC2D1"),
                   f"translate({sx * 56} -26) rotate({sx * -18})"))
        o.append(part(f"M{sx * 22},-44 C{sx * 24},-58 {sx * 34},-62 {sx * 40},-58 C{sx * 34},-54 {sx * 32},-48 {sx * 32},-40 Z",
                      "#F3E2BE", s=None))
    head = ell(0, -8, 48, 46)
    o.append(comp(head, "#FFFFFF", flat("M-60,-60 L-6,-60 C-8,-40 -20,-24 -40,-22 C-52,-22 -60,-30 -60,-40Z", "#4A4250"),
                  s=(-7, -8), ol="#7A7088"))
    o.append(part(ell(0, 30, 40, 24), "#FFB6C6", s=(-4, -5)))
    o.append(flat(ell(-14, 30, 5, 6.5), "#C2607A") + flat(ell(14, 30, 5, 6.5), "#C2607A"))
    o.append(eye(-20, -12, 9, 11, .5, 1, ol="#3A3040") + eye(20, -12, 9, 11, .5, 1, ol="#3A3040"))
    o.append(ln("M-10,44 Q0,50 10,44", "#8A3A50", .9))
    o.append(blush(-34, 10, 7, 4.5))
    return "".join(o)


@thing((-124, -76, 96, 84))
def cow():
    wh, ol, spot, hoof = "#FFFFFF", "#7A7088", "#4A4250", "#6A5A60"
    o = []
    o.append(part(tube([(66, -18, 4), (84, 0, 3.5), (86, 30, 3.5)]), wh, s=None, ol=ol)
             + part("M80,26 C78,36 84,46 90,44 C96,40 94,30 90,24Z", spot, s=None))
    for x in (60, -22):
        o.append(part(tube([(x, 20, 11), (x, 60, 10.5)]), shd(wh), s=None, ol=ol) + part(rr(x - 11, 58, 22, 14, 5), hoof, s=None))
    body = ("M-56,-30 C-30,-40 40,-40 62,-28 C80,-18 82,14 70,30 C60,42 40,44 20,42 L-30,42 C-56,42 -70,30 -72,8 "
            "C-74,-12 -70,-24 -56,-30Z")
    spots = (flat(blob([(-6, -42), (24, -40), (32, -18), (14, -4), (-8, -14)]), spot)
             + flat(blob([(44, 4), (66, -2), (86, 16), (64, 40), (44, 30)]), spot)
             + flat(blob([(-28, 12), (-10, 8), (-4, 28), (-22, 32)]), spot))
    o.append(comp(body, wh, spots, s=(-9, -10), ol=ol, hl=hi("M-44,-24 C-14,-31 18,-32 44,-30", 5, .7)))
    for x in (42, -40):
        o.append(part(tube([(x, 24, 11), (x, 62, 10.5)]), wh, s=(-2, -3), ol=ol) + part(rr(x - 11, 60, 22, 14, 5), hoof, s=None))
    o.append(at(_cow_head, -64, -26, .78))
    o.append(part(rr(-73, 8, 18, 15, 5), GOLD, s=(-2, -3)))
    return "".join(o)


def _scallop(cx, cy, rx, ry, k, bump):
    """A woolly outline: k round bumps (each about `bump` high) around an ellipse."""
    pts = [(cx + rx * math.cos(2 * math.pi * i / k), cy + ry * math.sin(2 * math.pi * i / k)) for i in range(k)]
    d = f"M{n(pts[0][0])},{n(pts[0][1])}"
    for i in range(k):
        a, b = pts[i], pts[(i + 1) % k]
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        nx, ny = (mx - cx) / rx ** 2, (my - cy) / ry ** 2
        l_ = math.hypot(nx, ny) or 1
        d += f" Q{n(mx + nx / l_ * bump * 2)},{n(my + ny / l_ * bump * 2)} {n(b[0])},{n(b[1])}"
    return d + "Z"


@thing((-104, -76, 92, 68))
def sheep():
    wool, face, leg = "#FFFDF6", "#6A5A78", "#5E5468"
    o = []
    for x in (50, -18):
        o.append(part(tube([(x, 24, 6.5), (x, 54, 6.5)]), dk(leg, .2), s=None, ol="#3A3046"))
    o.append(part(_scallop(8, 0, 72, 42, 14, 12), wool, s=(-8, -9), ol=WHITE_OL, hl=hi("M-36,-30 C-16,-40 10,-42 30,-38", 5, .9)))
    for x in (36, -32):
        o.append(part(tube([(x, 28, 6.5), (x, 58, 6.5)]), leg, s=None, ol="#3A3046"))
    o.append(part(_scallop(78, -6, 14, 14, 6, 5), wool, s=None, ol=WHITE_OL, k=.8))
    # head (front-facing), ears out to the sides
    for sx in (-1, 1):
        o.append(g(part(ell(0, 0, 18, 8), face, s=None), f"translate({-62 + sx * 30} -26) rotate({sx * 20})"))
    o.append(part(ell(-62, -18, 28, 32), face, s=(-5, -6), hl=hi("M-80,-30 C-76,-40 -70,-46 -62,-48", 4, .4)))
    o.append(part(_scallop(-62, -50, 22, 11, 7, 6), wool, s=None, ol=WHITE_OL, k=.8))
    o.append(eye(-73, -18, 9, 11, .5, 1, pc="#2A2030", ol="#2A2030") + eye(-51, -18, 9, 11, .5, 1, pc="#2A2030", ol="#2A2030"))
    o.append(flat(ell(-66, 0, 2.2, 1.8), "#2A2030") + flat(ell(-58, 0, 2.2, 1.8), "#2A2030"))
    o.append(smile(-62, 4, 12, "#2A2030", 1.0) + blush(-82, -2, 6, 4, "#FF9AAE", .6) + blush(-42, -2, 6, 4, "#FF9AAE", .6))
    return "".join(o)


@thing((-104, -76, 102, 72))
def fish(col="#FF8A26"):
    o = []
    fin_c = "#FFC23D"
    tail = "M52,0 C70,-22 90,-44 102,-40 C96,-20 92,-8 92,0 C92,8 96,20 102,40 C90,44 70,22 52,0 Z"
    o.append(part(tail, fin_c, s=(-4, -5)) + ln("M60,0 L94,-26 M60,0 L94,26 M60,0 L96,0", "#E88A1E", .62))
    o.append(part("M-14,-40 C-6,-66 22,-74 40,-62 C34,-50 26,-42 18,-38 Z", fin_c, s=(-3, -4)))
    body = "M-78,4 C-78,-30 -40,-50 -2,-48 C34,-46 58,-24 62,0 C58,24 34,46 -2,48 C-40,50 -78,36 -78,4 Z"
    belly = "M-70,20 C-50,44 0,50 40,30 L60,60 L-90,60 Z"
    o.append(comp(body, col, flat(belly, "#FFC77A"), s=(-9, -10), hl=hi("M-56,-26 C-44,-38 -28,-42 -14,-42", 6, .7)))
    o.append(ln("M14,-36 C22,-20 22,20 14,36", "#D9631A", .62))
    o.append(part("M-6,18 C4,30 20,34 30,30 C24,20 10,14 -6,18 Z", fin_c, s=None))
    o.append(eye(-44, -10, 13, 15, -2, 1, ol="#8A3A10"))
    o.append(ln("M-72,12 Q-66,18 -58,14", "#8A3A10", .9))
    o.append(blush(-50, 12, 7, 4))
    for (bx, by, r) in ((-96, -38, 6), (-90, -60, 4.2), (-100, -72, 3)):
        o.append(part(ell(bx, by, r), "#DFF4FF", s=None, ol="#7FB8E0", k=.7, hl=hidot(bx - r * .35, by - r * .35, r * .3)))
    return "".join(o)


def _tentacle(pts, col):
    d = tube(pts, 8)
    o = part(d, col, s=(-2, -3))
    return o


@thing((-96, -90, 96, 92))
def octopus(col="#FF7E86"):
    o = []
    back = shd(col)
    for pts in ([(-20, 10, 13), (-46, 40, 10), (-70, 52, 7.5), (-86, 42, 5.5), (-80, 30, 4.5)],
                [(20, 10, 13), (46, 40, 10), (70, 52, 7.5), (86, 42, 5.5), (80, 30, 4.5)]):
        o.append(part(tube(pts, 8), back, s=None, ol=lin(col)))
    legs = ([(-34, 4, 14), (-62, 18, 11), (-84, 6, 8), (-90, -14, 6), (-78, -20, 5)],
            [(34, 4, 14), (62, 18, 11), (84, 6, 8), (90, -14, 6), (78, -20, 5)],
            [(-14, 16, 14), (-26, 50, 11), (-44, 74, 8), (-64, 80, 6), (-70, 70, 5)],
            [(14, 16, 14), (26, 50, 11), (44, 74, 8), (64, 80, 6), (70, 70, 5)],
            [(0, 18, 13), (-4, 54, 10), (6, 80, 7), (22, 84, 5.5), (24, 74, 4.5)])
    for pts in legs:
        o.append(_tentacle(pts, col))
    for x, y in ((-56, 20), (-74, 12), (56, 20), (74, 12), (-28, 52), (-42, 70), (28, 52), (42, 70), (-4, 58), (2, 74)):
        o.append(part(ell(x, y, 3.6, 3), lt(col, .5), s=None, ol=lin(col), k=.45))
    mantle = "M-52,8 C-62,-46 -34,-86 0,-86 C34,-86 62,-46 52,8 C40,22 -40,22 -52,8Z"
    spots = "".join(flat(ell(x, y, r), lt(col, .3)) for x, y, r in ((-30, -64, 7), (-42, -44, 4.5), (34, -60, 5)))
    o.append(comp(mantle, col, spots, s=(-10, -10), hl=hi("M-36,-56 C-30,-70 -18,-78 -6,-80", 6, .65)))
    o.append(eye(-20, -22, 13, 15, .5, 2, ol="#7A2A3A") + eye(20, -22, 13, 15, .5, 2, ol="#7A2A3A"))
    o.append(blush(-36, 0, 8, 5, "#FF5A78", .45) + blush(36, 0, 8, 5, "#FF5A78", .45))
    o.append(smile(0, 2, 18, "#7A2A3A"))
    return "".join(o)


# ---------------------------------------------------------------- 超市
APPLE_D = ("M0,-50 C20,-68 62,-66 76,-30 C88,6 68,58 36,70 C22,76 10,72 0,67 C-10,72 -22,76 -36,70 "
           "C-68,58 -88,6 -76,-30 C-62,-66 -20,-68 0,-50 Z")


@thing((-82, -98, 82, 76))
def apple(col=RED):
    o = part("M-3,-46 C-5,-62 -1,-76 7,-88 L15,-84 C8,-72 5,-60 5,-46 Z", "#8A5A35", s=(-1.5, -2))
    o += part(APPLE_D, col, s=(-12, -12), hl=hi("M-56,-26 C-52,-40 -40,-48 -28,-48", 9, .8) + hidot(-60, -8, 4.5))
    o += part("M8,-66 C18,-90 46,-96 60,-84 C48,-64 24,-58 8,-66 Z", "#5CC452", s=(-3, -3.5))
    o += ln("M14,-68 C28,-76 40,-80 50,-82", "#3E8C3A", .62)
    return o


def _one_banana(col=YELLOW):
    body = ("M-74,-38 C-66,8 -12,44 44,36 C64,33 80,20 90,4 L86,-2 C68,8 42,14 14,12 "
            "C-22,8 -48,-16 -58,-42 Z")
    o = part(body, col, s=(-4, -11), hl=hi("M-56,-22 C-40,0 -10,18 24,22", 5, .7))
    o += ln("M-66,-30 C-50,4 -10,30 44,28", "#E2A41E", .62)
    o += part("M86,-2 L92,6 L88,9 L82,3 Z", "#6B4A26", s=None)
    return o


@thing((-90, -78, 98, 64))
def banana():
    o = part("M-74,-38 L-80,-62 C-81,-68 -70,-70 -68,-64 L-60,-40 Z", "#8A6A35", s=(-1.5, -2))
    o += g(_one_banana(), "rotate(-16 -66 -42)")
    o += g(_one_banana(), "rotate(-2 -66 -42)")
    o += g(_one_banana(), "rotate(14 -66 -42)")
    return o


@thing((-90, -50, 90, 46))
def bread(col="#E39A4C"):
    loaf = ("M-84,20 C-86,-14 -60,-42 -10,-44 C40,-46 82,-26 86,8 C88,30 70,40 40,42 L-50,42 C-72,40 -84,34 -84,20Z")
    bottom = flat("M-100,22 C-60,30 40,32 100,20 L100,60 L-100,60Z", lt(col, .32))
    o = comp(loaf, col, bottom, s=(-9, -10), hl=hi("M-62,-14 C-50,-30 -30,-37 -10,-38", 6, .6))
    for cx, cy, a in ((-40, -18, -28), (0, -22, -24), (40, -14, -20)):
        o += g(part(ell(0, 0, 20, 6.5), "#FFE2A8", s=None, ol=lin(col), k=.7), f"translate({cx} {cy}) rotate({a})")
    o += "".join(flat(ell(x, y, 1.6), "#FFF6E0", op=.9) for x, y in ((-58, -4), (-20, 2), (18, 0), (54, -2), (-34, 12), (36, 14)))
    return o


@thing((-48, -86, 48, 82))
def carrot():
    o = ""
    for a in (-24, 0, 24):
        o += g(part("M0,-36 C-10,-50 -10,-70 0,-80 C10,-70 10,-50 0,-36 Z", GREEN, s=(-2, -3)), f"rotate({a} 0 -36)")
    body = "M-22,-34 C-24,-48 22,-48 22,-34 C20,0 8,40 2,62 C0,68 -4,68 -6,62 C-14,40 -22,0 -22,-34Z"
    o += part(body, "#FF8C2B", s=(-6, -7), hl=hi("M-14,-28 C-14,-10 -10,10 -6,24", 4, .6))
    o += ln("M-14,-12 L-4,-12 M6,4 L16,4 M-10,22 L0,22 M2,38 L8,38", "#D9631A", .9)
    return g(o, "rotate(18)")


@thing((-90, -68, 90, 72))
def cabbage():
    light, mid, dark = "#CDEFA0", "#9ADB6E", "#6EBF4A"
    o = part(ell(0, 2, 64, 58), light, s=(-8, -9), ol="#5FA03C", hl=hi("M-40,-30 C-30,-44 -14,-50 2,-51", 6, .7))
    o += ln("M-46,-26 C-24,-48 24,-48 46,-22 M-50,-6 C-30,-26 10,-30 30,-18", "#7FC255", .8)
    o += ln("M0,-50 C-6,-30 -4,-14 2,0", "#8FCB62", .7)
    left = "M-6,66 C-58,68 -88,36 -86,-4 C-84,-38 -64,-60 -40,-66 C-58,-40 -62,-4 -44,26 C-34,44 -20,56 -6,66Z"
    o += part(left, mid, s=(-4, -5), ol="#4E9A34")
    o += g(part(left, mid, s=(4, -5), ol="#4E9A34"), "scale(-1 1)")
    o += ln("M-30,56 C-62,40 -74,10 -70,-24 M-56,34 L-74,26 M-66,6 L-82,0 M-64,-20 L-78,-30", "#4E9A34", .62)
    o += ln("M30,56 C62,40 74,10 70,-24 M56,34 L74,26 M66,6 L82,0 M64,-20 L78,-30", "#4E9A34", .62)
    front = "M-56,34 C-34,58 34,58 56,34 C50,58 28,72 0,72 C-28,72 -50,58 -56,34Z"
    o += part(front, dark, s=(-3, -4), ol="#4E9A34")
    o += ln("M0,70 L0,52 M-20,66 L-10,52 M20,66 L10,52", "#3E8A2C", .6)
    return o


@thing((-72, -84, 72, 78))
def frozen_dumplings(col="#5AA9F0"):
    o = ""
    bag = rr(-62, -64, 124, 138, 12)
    frost = (flat(blob([(-70, 40), (-52, 46), (-40, 64), (-48, 80), (-72, 80)]), "#FFFFFF", .75)
             + flat(blob([(70, -40), (48, -52), (40, -70), (72, -74)]), "#FFFFFF", .75)
             + flat(blob([(52, 70), (64, 48), (76, 58), (74, 80)]), "#FFFFFF", .7))
    o += comp(bag, col, frost, s=(-8, -9), hl=hi("M-50,-46 L-50,30", 5, .45))
    win = ell(-2, 12, 46, 40)
    dump = ""
    for cx, cy, a in ((-22, 22, -8), (18, 26, 10), (-2, -2, 0)):
        d = "M-24,6 C-24,-14 -10,-22 0,-22 C10,-22 24,-14 24,6 C14,10 -14,10 -24,6Z"
        pleats = ln("M-12,-18 L-10,-12 M-4,-21 L-3,-14 M4,-21 L3,-14 M12,-18 L10,-12", "#C9A77A", .5)
        dump += g(part(d, "#FFF4DE", s=(-3, -4), ol="#C9A77A", k=.7) + pleats, f"translate({cx} {cy}) rotate({a})")
    o += comp(win, "#E3F3FF", dump + flat(ell(-30, -14, 10, 5), "#FFFFFF", .8), s=None, ol=lin(col), k=.8)
    o += part("M-66,-78 L66,-78 L66,-60 L-66,-60Z", lt(col, .5), s=None, ol=lin(col))
    o += ln("M" + " L".join(f"{x},{-66 if (x // 6) % 2 else -72}" for x in range(-60, 64, 6)), lin(col), .5)
    for a in (0, 60, 120):
        o += g(ln("M0,-12 L0,12 M-4,-8 L0,-4 L4,-8 M-4,8 L0,4 L4,8", "#FFFFFF", .8), f"translate(38 -38) rotate({a})")
    o += sparkle(-40, -40, 6) + sparkle(50, 40, 5)
    return o


# ---------------------------------------------------------------- 資源回收
@thing((-82, -86, 82, 86))
def newspaper():
    paper, ol, ink = "#F3F1F7", WHITE_OL, "#8E86A8"
    o = part(rr(-58, -72, 124, 150, 4), "#E2DEEC", s=None, ol=ol)
    page = rr(-66, -78, 124, 150, 4)
    inner = flat("M-4,-80 L60,-80 L60,80 L-4,80Z", "#E9E6F1")
    inner += flat(rr(-56, -66, 104, 14, 3), "#6E6880")
    inner += comp(rr(-56, -42, 46, 40, 3), "#BFE3FF", flat(ell(-34, 10, 34, 18), "#8ED48A") + flat(ell(-20, -28, 6), YELLOW), s=None, ol=ink, k=.6)
    for y in range(-42, 64, 9):
        inner += ln(f"M2,{y} L48,{y}", "#B9B3CC", .9)
    for y in range(8, 64, 9):
        inner += ln(f"M-56,{y} L-10,{y}", "#B9B3CC", .9)
    o += comp(page, paper, inner, s=(-6, -7), ol=ol)
    o += ln("M-4,-78 L-4,72", "#C9C2DD", .7)
    return g(o, "rotate(-7)")


@thing((-96, -70, 92, 78))
def cardboard(col="#D9A066"):
    o = ""
    o += part(poly([(-36, -32), (64, -32), (72, -62), (-28, -62)]), shd(col), s=None)
    o += part(poly([(-66, -10), (-36, -32), (64, -32), (34, -10)]), "#8A5A30", s=None, ol=lin(col))
    o += part(poly([(-66, -10), (-36, -32), (-64, -56), (-94, -32)]), lt(col, .12), s=None)
    o += part(poly([(34, -10), (64, -32), (90, -14), (60, 8)]), lt(col, .12), s=None)
    o += part(poly([(34, -10), (64, -32), (64, 48), (34, 70)]), shd(col), s=None)
    front = poly([(-66, -10), (34, -10), (34, 70), (-66, 70)])
    o += comp(front, col, flat(rr(-26, -12, 20, 84, 0), lt(col, .3)), s=(-6, -7), hl=hi("M-58,0 L-58,56", 4, .45))
    for x in (8, 22):
        o += ln(f"M{x},50 L{x},28 M{x - 5},34 L{x},27 L{x + 5},34", "#8A5A30", .7)
    o += ln("M-56,60 L-34,60", "#8A5A30", .7)
    return o


@thing((-38, -96, 38, 76))
def pet_bottle():
    ol = "#5A9BD5"
    o = part(rr(-14, -94, 28, 18, 4), BLUE, s=(-2, -3))
    o += "".join(ln(f"M{x},-92 L{x},-79", lin(BLUE), .5) for x in (-8, -3, 2, 7))
    o += part(rr(-17, -78, 34, 7, 3), lt(BLUE, .45), s=None, ol=lin(BLUE), k=.7)
    body = ("M-12,-71 L12,-71 C12,-58 32,-52 33,-30 L33,-10 C30,-4 30,4 33,10 L33,52 C33,62 26,70 14,72 "
            "C6,74 -6,74 -14,72 C-26,70 -33,62 -33,52 L-33,10 C-30,4 -30,-4 -33,-10 L-33,-30 C-32,-52 -12,-58 -12,-71Z")
    o += part(body, "#E2F3FF", s=(-7, -8), sh="#C6E3FA", ol=ol, hl=hi("M-22,-28 L-22,48", 6, .95) + hi("M22,20 L22,46", 3, .8))
    o += ln("M-31,-12 Q0,-6 31,-12 M-31,12 Q0,18 31,12 M-32,30 Q0,36 32,30", "#9CC8EC", .7)
    o += ln("M-10,72 L-6,64 M10,72 L6,64", "#9CC8EC", .7)
    return o


@thing((-44, -78, 44, 72))
def soda_can(col=RED):
    silver, sd = "#D5DAE4", "#AEB6C8"
    body = rr(-40, -54, 80, 112, 6)
    wave = flat("M-50,-10 C-20,-28 10,8 50,-12 L50,8 C10,28 -20,-8 -50,10Z", "#FFFFFF")
    o = comp(body, col, wave + flat("M24,-60 L34,-60 L34,62 L24,62Z", "#FFFFFF", .25), s=(-8, -9), hl=hi("M-28,-40 L-28,44", 6, .5))
    o += part("M-40,-50 C-40,-60 -34,-66 -28,-68 L28,-68 C34,-66 40,-60 40,-50Z", silver, s=None, ol="#7E869A")
    o += part(ell(0, -68, 28, 7), sd, s=None, ol="#7E869A", k=.8)
    o += part("M-6,-72 C-6,-76 8,-76 10,-72 L12,-66 C12,-63 -4,-63 -6,-66Z", silver, s=None, ol="#7E869A", k=.7)
    o += part("M-40,52 L40,52 C40,62 34,68 26,70 L-26,70 C-34,68 -40,62 -40,52Z", silver, s=None, ol="#7E869A")
    o += ln("M-32,60 L32,60", "#7E869A", .5)
    return o


@thing((-92, -74, 92, 70))
def banana_peel(col=YELLOW):
    inner, tip, spot = "#FFF3C2", "#7A5A2E", "#9A6A2E"
    o = ""
    back = "M-6,-34 C14,-48 44,-58 64,-56 C72,-54 72,-46 64,-44 C44,-40 22,-30 8,-22Z"
    o += part(back, inner, s=None, ol=lin(col)) + part("M60,-56 C68,-56 72,-50 66,-44 C62,-46 60,-50 60,-56Z", tip, s=None)
    left = "M-12,-30 C-40,-32 -70,-10 -84,26 C-86,34 -78,38 -72,32 C-56,8 -34,-6 -8,-12Z"
    right = "M12,-30 C40,-32 70,-10 84,26 C86,34 78,38 72,32 C56,8 34,-6 8,-12Z"
    o += comp(left, col, flat(ell(-56, 8, 4, 3), spot) + flat(ell(-38, -10, 3, 2.5), spot), s=(-3, -5),
              hl=hi("M-24,-26 C-44,-22 -60,-6 -70,12", 3.5, .6))
    o += part("M-84,26 C-86,34 -78,38 -72,32 C-76,30 -80,28 -84,26Z", tip, s=None)
    o += comp(right, col, flat(ell(52, 4, 4, 3), spot), s=(-3, -5))
    o += part("M84,26 C86,34 78,38 72,32 C76,30 80,28 84,26Z", tip, s=None)
    core = "M-16,-30 C-18,-48 -10,-60 0,-62 C10,-60 18,-48 16,-30 C18,-14 10,0 0,0 C-10,0 -18,-14 -16,-30Z"
    o += part(core, col, s=(-4, -5))
    o += part(rr(-4, -72, 8, 14, 3), "#8A6A35", s=None)
    front = "M-14,-20 C-22,6 -24,34 -16,58 C-12,66 -2,66 -2,58 C-4,34 2,8 12,-18 C6,-12 -6,-12 -14,-20Z"
    o += comp(front, col, flat(ell(-10, 20, 3.5, 3), spot) + flat(ell(-8, 40, 3, 2.5), spot), s=(-4, -6),
              hl=hi("M-12,-2 C-16,14 -16,30 -14,44", 3.5, .6))
    o += part("M-16,58 C-12,66 -2,66 -2,58 C-6,60 -12,60 -16,58Z", tip, s=None)
    return o


@thing((-66, -78, 66, 58))
def tissue():
    paper, sh_, ol, crease = "#FBFAFF", "#DCD5EE", WHITE_OL, "#B4AACF"
    o = part("M-8,-46 L4,-74 L24,-62 L20,-40Z", paper, s=None, ol=ol) + flat("M8,-66 L24,-62 L20,-40 L10,-48Z", sh_)
    body = blob([(-58, 10), (-52, -28), (-22, -50), (14, -46), (46, -34), (62, -4), (54, 30), (24, 52), (-14, 54), (-46, 40)])
    facets = (flat(poly([(-12, -4), (8, 6), (40, 46), (70, 40), (70, 70), (-10, 70)]), sh_, .9)
              + flat(poly([(20, -50), (30, -8), (70, -16), (70, -50)]), sh_, .7)
              + flat(poly([(-70, 20), (-36, 14), (-30, 60), (-70, 60)]), sh_, .6)
              + flat(poly([(-40, -40), (-14, -10), (-36, 2)]), "#FFFFFF"))
    o += comp(body, paper, facets, s=None, ol=ol)
    o += ln("M-38,-16 L-14,-4 L-6,-28 M10,-34 L24,-8 L46,-14 M-34,22 L-8,10 L8,34 M22,6 L34,30 M-14,-4 L8,6", crease, .7)
    return o


# ================================================================ WRITING
def write_things(only=None):
    sizes = {}
    for name, (fn, box) in THINGS.items():
        if only and name not in only:
            continue
        K.begin(K.OL_THING)
        sizes[name] = save(name, fit(fn, box))
    return sizes


# ================================================================ PREVIEW
RENDER = K.ROOT / "docs" / "mockups" / "render.js"


def render_html(html, out, w, h, scale=1):
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp) / "page.html"
        p.write_text(html)
        subprocess.run(["node", str(RENDER), str(p), str(out), str(w), str(h), str(scale)], check=True)


def _img(name, x, y, w, h=None):
    h = w if h is None else h
    return (f'<img src="file://{K.OUT / (name + ".svg")}" style="position:absolute;left:{x:.1f}px;top:{y:.1f}px;'
            f'width:{w:.1f}px;height:{h:.1f}px">')


def _label(s, x, y, w, size=13, col="#9C90AE"):
    return (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;text-align:center;font:{size}px sans-serif;'
            f'color:{col}">{s}</div>')


def sheet_things(names, cell, cols, y0=0, title=""):
    o, pad = [], 12
    if title:
        o.append(f'<div style="position:absolute;left:16px;top:{y0 + 8}px;font:bold 20px sans-serif;color:#4B3A5E">{title}</div>')
        y0 += 40
    for i, nm in enumerate(names):
        x, y = 16 + (i % cols) * (cell + pad), y0 + (i // cols) * (cell + pad + 18)
        o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{cell}px;height:{cell}px;background:#fff;'
                 f'border-radius:14px;box-shadow:0 0 0 1px #E4DEEE"></div>')
        o.append(_img(nm, x, y, cell))
        o.append(_label(nm, x, y + cell + 1, cell, 12))
    rows = (len(names) + cols - 1) // cols
    return "".join(o), y0 + rows * (cell + pad + 18)


def page(body, w, h, bg="#F6F2FB"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>*{{margin:0;padding:0}}'
            f'body{{width:{w}px;height:{h}px;position:relative;background:{bg};overflow:hidden}}</style></head><body>{body}</body></html>')


def main(argv):
    if argv and argv[0] == "things":
        out = pathlib.Path(argv[1])
        cell = int(argv[2]) if len(argv) > 2 else 200
        names = argv[3:] or list(THINGS)
        cols = max(1, 1500 // (cell + 12))
        body, h = sheet_things(names, cell, cols)
        render_html(page(body, 16 + cols * (cell + 12), h + 10), out, 16 + cols * (cell + 12), h + 10)
        return
    sizes = write_things()
    big = max(sizes.items(), key=lambda kv: kv[1])
    print(f"{len(sizes)} pictures written to {K.OUT} (largest {big[0]} {big[1]:.1f} KB)")


if __name__ == "__main__":
    main(sys.argv[1:])
