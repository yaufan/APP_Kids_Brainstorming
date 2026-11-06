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


# ================================================================ PLACES (200 x 200, drawn in picture units)
def read_places():
    """{place id: (scene id, x, y, w)} from content.dart's sortScenes."""
    places, scene = {}, None
    for line in CONTENT.read_text().splitlines():
        m = re.search(r"SortScene\('(\w+)'", line)
        if m:
            scene = m.group(1)
        m = re.search(r"Place\('(\w+)', '[^']*', x: ([\d.]+), y: ([\d.]+), w: ([\d.]+)", line)
        if m and scene:
            places[m.group(1)] = (scene, float(m.group(2)), float(m.group(3)), float(m.group(4)))
    return places


PLACES = {}
U = 1.0     # drawing-unit factor of the place being drawn: offsets and highlights times U look the same on screen


def place(f):
    PLACES[f.__name__] = f
    return f


def S(a=6, b=7):
    """A cel-shadow offset that looks the same on screen in every place."""
    return (-a * U, -b * U)


def H(d, w=5, op=.75):
    return hi(d, w * U, op)


def fit_bottom(fn, box, fill, bottom=194, cx=100, **kw):
    """fit() with the drawing's lowest point at `bottom` (standing on the floor)."""
    x0, y0, x1, y1 = box
    s = fill / max(x1 - x0, y1 - y0)
    return fit(fn, box, fill=fill, cx=cx, cy=bottom - (y1 - y0) * s / 2, **kw)


# ---------------------------------------------------------------- 房間
def _teddy_head(col="#C98A52"):
    li = "#F3D2A6"
    o = ""
    for sx in (-1, 1):
        o += part(ell(sx * 40, -66, 17), col, s=(-3, -4)) + part(ell(sx * 40, -66, 8.5), li, s=None)
    o += part(ell(0, -28, 48, 42), col, s=(-9, -9), hl=hi("M-30,-56 C-20,-64 -6,-67 6,-66", 5, .55))
    o += part(ell(0, -12, 19, 14), li, s=None, ol=lin(col))
    o += part(ell(0, -18, 7.5, 5.5), "#3A2418", s=None, hl=hidot(-2, -20, 1.8))
    o += ln("M0,-12 L0,-6 M-6,-4 Q0,0 6,-4", "#3A2418", .9)
    for sx in (-1, 1):
        o += dot_eye(sx * 20, -32, 7.5)
    return o


def _toybox(col="#4FB3F6"):
    o = []
    lid = "M-72,-26 L-62,-74 C-60,-80 -56,-82 -50,-82 L50,-82 C56,-82 60,-80 62,-74 L72,-26 Z"
    o.append(part(lid, shd(col), s=(-4, -5)) + part(rr(-56, -90, 112, 12, 5), YELLOW, s=None)
             + part(rr(-30, -60, 60, 14, 7), lt(col, .35), s=None, ol=lin(col)))
    o.append(flat("M-66,-26 L66,-26 L60,-14 L-60,-14 Z", "#3A3150"))
    o.append(g(_teddy_head(), "translate(-30 -2) scale(.5) rotate(-10)"))
    o.append(g(part(rr(-20, -20, 40, 40, 6), YELLOW, s=(-4, -5)) + part(star_d(12, 5.5, round_=.18), "#FF8A3D", s=None),
               "translate(26 -36) rotate(12)"))
    o.append(part("M48,-38 C48,-58 66,-62 68,-46 L68,-20 L48,-20Z", GREEN, s=(-3, -4)))
    front = "M-74,-26 L74,-26 L74,48 C74,56 68,62 60,62 L-60,62 C-68,62 -74,56 -74,48 Z"
    trim = "M-80,-30 L80,-30 L80,-12 L-80,-12 Z"
    o.append(comp(front, col, part(trim, YELLOW, s=None, ol=lin(YELLOW))
                  + part(star_d(17, 8, round_=.18, cx=0, cy=20), "#FFFFFF", s=(-2, -3), ol=lin(col)), s=(-9, -10)))
    o.append(ln("M-74,-12 L74,-12", lin(col), .9))
    o.append(part(ell(-44, 20, 7), "#FF7FA3", s=None) + part(ell(44, 20, 7), "#FF7FA3", s=None))
    return "".join(o)


@place
def toy_box():
    return ground(100, 192, 84, 8) + fit_bottom(_toybox, (-84, -98, 84, 64), 180)


def _bookshelf(wd=200):
    """A bookcase wd wide (its own units), three shelves of books with a clear gap on the middle one."""
    wood, back = "#D08E57", "#9E6339"
    hw, iw = wd / 2, wd / 2 - 10
    o = part(rr(-hw + 14, -150, 28, 26, 6), "#E8735A", s=(-2, -3)) + part(ell(-hw + 28, -150, 16, 12), GREEN, s=(-2, -3))
    o += part(rr(-hw, -126, wd, 252, 9), wood, s=(-7, -8))
    shelves = [(-114, -44), (-32, 40), (52, 114)]
    rng = random.Random(4)
    cols = [RED, BLUE, YELLOW, GREEN, PURPLE, PINK, TEAL, "#FF8A3D"]
    for si, (y0, y1) in enumerate(shelves):
        o += part(f"M{n(-iw)},{y0} L{n(iw)},{y0} L{n(iw)},{y1} L{n(-iw)},{y1} Z", back, s=None, ol=lin(wood))
        x, k = -iw + 2, 0
        while x < iw - 6:
            if si == 1 and k == 3:
                x += 44
                k += 1
                continue
            bw = rng.choice([14, 16, 18, 20])
            if x + bw > iw - 2:
                break
            bh = rng.randint(int((y1 - y0) * .62), int((y1 - y0) * .9))
            c = cols[(si * 3 + k) % len(cols)]
            if si == 2 and k == 5:
                o += g(part(rr(-bw / 2, -bh, bw, bh, 3), c, s=(-2, -2.5)), f"translate({n(x + bw / 2 + 6)} {y1}) rotate(14)")
                x += bw + 14
            else:
                o += part(rr(x, y1 - bh, bw, bh, 3), c, s=(-2, -2.5))
                o += ln(f"M{n(x + 3)},{y1 - bh + 10} L{n(x + bw - 3)},{y1 - bh + 10}", lt(c, .55), .62)
                x += bw + 2
            k += 1
        o += part(rr(-hw + 2, y1, wd - 4, 9, 3), lt(wood, .12), s=None, ol=lin(wood))
    o += part(rr(-hw + 6, 124, 14, 8, 3), shd(wood), s=None) + part(rr(hw - 20, 124, 14, 8, 3), shd(wood), s=None)
    return o


@place
def bookshelf():
    return ground(100, 193, 70, 6) + fit_bottom(_bookshelf, (-100, -162, 100, 132), 192)


def _basket(col="#E9B866"):
    body = "M-58,-36 L58,-36 L48,56 C47,61 43,64 38,64 L-38,64 C-43,64 -47,61 -48,56 Z"
    weave = "".join(ln(f"M-70,{y} L70,{y}", shd(col), .62) for y in (-14, 8, 30, 50))
    for r_, y in enumerate((-36, -14, 8, 30)):
        for x in range(-64 + (r_ % 2) * 9, 70, 18):
            weave += ln(f"M{x},{y + 3} L{x},{y + 19}", shd(col), .62)
    o = part(ell(0, -38, 60, 13), "#8C5A2C", s=None)
    o += part("M-30,-44 C-24,-60 -2,-64 10,-52 C18,-62 34,-58 36,-44 L30,-34 L-26,-36Z", "#FF8FB1", s=(-2, -3))
    o += comp(body, col, weave, s=(-8, -9))
    o += part("M-60,-40 C-60,-48 60,-48 60,-40 C60,-31 -60,-31 -60,-40Z", shd(col), s=None, ol=lin(col))
    o += part(rr(-46, -26, 22, 9, 4.5), "#8C5A2C", s=None) + part(rr(24, -26, 22, 9, 4.5), "#8C5A2C", s=None)
    towel = "M-48,-44 C-40,-48 -18,-48 -8,-44 L-10,0 C-15,7 -21,1 -27,7 C-33,13 -40,7 -47,3 Z"
    o += comp(towel, "#7CC7FF", flat("M-60,-10 L0,-10 L0,-4 L-60,-4Z", "#FFFFFF"), s=(-3, -4))
    return o


@place
def laundry():
    return ground(100, 192, 66, 7) + fit_bottom(_basket, (-66, -64, 70, 66), 172)


def _bed(col="#7C8CF8"):
    wood = "#C9834F"
    o = part("M-100,60 L-100,-56 C-100,-74 -72,-80 -72,-62 L-72,60 Z", wood, s=(-4, -5))
    o += part(rr(-96, 44, 12, 18, 3), shd(wood), s=None) + part(rr(84, 44, 12, 18, 3), shd(wood), s=None)
    o += part(rr(-78, -10, 162, 30, 10), "#FFFFFF", s=(-3, -4))
    o += part(rr(-76, 18, 160, 30, 6), "#B98B6A", s=None)
    o += ln("M-66,-2 C-56,-6 -40,-7 -28,-6", "#D9D3EA", .7)
    blanket = ("M-16,-24 C10,-30 50,-30 82,-22 C90,-20 92,-12 92,-4 L90,40 C90,46 86,48 80,48 L-16,48 "
               "C-22,48 -24,44 -24,38 L-24,-14 C-24,-20 -22,-23 -16,-24Z")
    dots = "".join(part(star_d(6, 3, cx=x, cy=y, round_=.15), "#FFFFFF", s=None, ol=False) for x, y in
                   ((0, -6), (30, 10), (60, -8), (8, 28), (44, 34), (74, 22)))
    o += comp(blanket, col, dots, s=(-6, -7))
    o += ln("M-24,-4 C10,-12 50,-12 92,-6", lin(col), .62)
    o += part("M76,60 L76,-14 C76,-28 104,-28 104,-14 L104,60 Z", wood, s=(-3, -4))
    return o


@place
def bed():
    return ground(100, 192, 92, 8) + fit_bottom(_bed, (-104, -82, 104, 62), 194)


# ---------------------------------------------------------------- 浴室
def _wall_shelf(x0, x1, y, col="#FFFFFF", ol=WHITE_OL):
    """A little wall shelf: a board at y with two brackets under it."""
    o = ""
    for bx in (x0 + 18, x1 - 18):
        o += part(f"M{n(bx - 5)},{n(y + 10)} L{n(bx + 5)},{n(y + 10)} L{n(bx + 5)},{n(y + 34)} L{n(bx - 5)},{n(y + 22)}Z", col, s=None, ol=ol)
    o += part(rr(x0, y, x1 - x0, 13, 6), col, s=S(3, 4), ol=ol, hl=H(f"M{n(x0 + 10)},{n(y + 4)} L{n(x1 - 30)},{n(y + 4)}", 3, .9))
    return o


@place
def brush_cup():
    col = "#FFD43B"
    o = _wall_shelf(18, 182, 150)
    o += flat(ell(100, 148, 48, 5), K.SHADOW, .18)
    body = "M50,62 L150,62 L138,140 C137,146 132,150 126,150 L74,150 C68,150 63,146 62,140Z"
    o += comp(body, col, part(star_d(16, 7.5, cx=100, cy=108, round_=.18), "#FFFFFF", s=None, ol=lin(col), k=.8)
              + flat("M30,76 L170,76 L170,84 L30,84Z", lt(col, .45)), s=S(9, 10), hl=H("M64,92 L70,134", 6, .6))
    o += part(ell(100, 62, 50, 13), lt(col, .2), s=None)
    o += flat(ell(100, 64, 42, 9), "#7A5A20", .55)
    o += K.stroke(ell(100, 62, 50, 13), lin(col))
    return o


@place
def towel_rack():
    bar, plate = "#5BB8E8", "#FFFFFF"
    o = flat("M30,126 L170,126 L166,134 L34,134Z", K.SHADOW, .08)
    for x in (24, 176):
        o += part(rr(x - 10, 30, 20, 100, 10), plate, s=S(3, 4), ol=WHITE_OL)
        o += part(ell(x, 42, 3.5), "#D9E6F2", s=None, ol=WHITE_OL, k=.7) + part(ell(x, 118, 3.5), "#D9E6F2", s=None, ol=WHITE_OL, k=.7)
    for y in (48, 96):
        o += part(rr(16, y, 168, 16, 8), bar, s=S(3, 4), hl=H(f"M28,{y + 5} L170,{y + 5}", 4, .8))
        for x in (24, 176):
            o += part(rr(x - 8, y - 3, 16, 22, 6), lt(bar, .3), s=None, ol=lin(bar), k=.9)
    return o


@place
def bathtub():
    tub, ol, water, foot = "#FFFFFF", "#7E84B8", "#7FD0FF", GOLD
    o = ground(100, 193, 90, 7)
    for x in (34, 166):
        o += part(f"M{x - 10},170 L{x + 10},170 L{x + 8},184 C{x + 8},192 {x - 8},192 {x - 8},184Z", foot, s=None)
    o += K.hose("M174,96 L174,50 C174,38 158,36 154,48", "#C9D2E0", 9 * U, ol="#7E869A")
    o += part(ell(152, 56, 7, 5), "#C9D2E0", s=None, ol="#7E869A")
    o += part("M14,92 C40,76 160,76 186,92Z", water, s=None, ol=lin(water))
    for x, y, r in ((30, 82, 12), (48, 70, 16), (70, 76, 11), (132, 76, 12), (152, 68, 15), (170, 80, 10), (92, 82, 8), (60, 56, 8)):
        o += part(ell(x, y, r), "#F4FBFF", s=None, ol="#8EC6E8", k=.8, hl=hidot(x - r * .35, y - r * .4, r * .25))
    body = "M12,96 L188,96 L180,148 C176,168 158,176 138,176 L62,176 C42,176 24,168 20,148Z"
    o += comp(body, tub, flat("M0,96 L200,96 L200,104 L0,104Z", lt(water, .55)), s=S(9, 10), ol=ol, hl=H("M30,112 C32,132 40,150 54,160", 6, .9))
    o += part(rr(4, 88, 192, 14, 7), tub, s=None, ol=ol)
    return o


@place
def soap_dish():
    col = "#7ED6A8"
    o = _wall_shelf(10, 190, 136)
    o += flat(ell(100, 134, 70, 6), K.SHADOW, .16)
    o += part("M24,112 C24,136 176,136 176,112 Z", shd(col), s=None, ol=lin(col))
    o += part(ell(100, 112, 76, 22), col, s=S(4, 5))
    o += part(ell(100, 110, 62, 14), lt(col, .4), s=None, ol=lin(col), k=.8)
    o += ln("M60,104 L60,116 M80,100 L80,120 M100,98 L100,122 M120,100 L120,120 M140,104 L140,116", lt(col, .1), 1.2)
    o += H("M40,104 C52,98 70,95 86,94", 4, .8)
    return o


# ---------------------------------------------------------------- 廚房
FRIDGE, FRIDGE_OL, COLD = "#CFE9FF", "#6F86B8", "#EEF8FF"


@place
def fridge():
    o = ground(76, 193, 64, 6)
    o += part(rr(26, 186, 14, 9, 3), "#6E6880", s=None) + part(rr(108, 186, 14, 9, 3), "#6E6880", s=None)
    body = rr(16, 0, 116, 190, 12)
    inside = rr(26, 10, 96, 170, 8)
    o += part(body, FRIDGE, s=S(8, 9), ol=FRIDGE_OL)
    glow = flat(ell(74, 14, 60, 30), "#FFFFFF", .8)
    shelves = "".join(part(rr(26, y, 96, 6, 2), "#FFFFFF", s=None, ol="#9DB6DA", k=.8) for y in (64, 114))
    crisper = part(rr(32, 144, 84, 32, 6), "#E4F3FF", s=None, ol="#9DB6DA", k=.8) + ln("M44,160 L104,160", "#B8CDEB", .8)
    o += comp(inside, COLD, glow + shelves + crisper + flat("M26,12 L36,12 L36,180 L26,180Z", "#DCEEFF"), s=None, ol=FRIDGE_OL, k=.9)
    o += part(ell(74, 20, 9, 4), "#FFF6C2", s=None, ol="#E0C860", k=.6)
    door = "M132,6 L190,26 C194,27 196,30 196,34 L196,168 C196,172 194,175 190,176 L132,190Z"
    o += part(door, FRIDGE, s=S(4, 5), ol=FRIDGE_OL)
    o += part("M138,18 L188,34 L188,166 L138,180Z", COLD, s=None, ol=FRIDGE_OL, k=.8)
    for y0 in (70, 128):
        o += part(f"M138,{y0} L188,{y0 + 6} L188,{y0 + 18} L138,{y0 + 16}Z", "#FFFFFF", s=None, ol="#9DB6DA", k=.8)
    return o


@place
def freezer():
    o = ""
    body = rr(16, 58, 116, 138, 12)
    o += part(body, FRIDGE, s=S(8, 9), ol=FRIDGE_OL)
    o += part(rr(26, 68, 96, 46, 7), "#3A4A6A", s=None, ol=FRIDGE_OL, k=.8)
    o += flat("M28,70 C40,78 50,70 60,78 C70,70 84,78 96,70 C104,76 112,70 120,72 L120,82 L28,82Z", "#FFFFFF", .85)
    for x, h in ((40, 12), (58, 8), (80, 14), (104, 9)):
        o += part(f"M{x - 4},76 L{x + 4},76 L{x},{76 + h}Z", "#EAF6FF", s=None, ol="#9DB6DA", k=.6)
    inside = poly([(10, 132), (138, 132), (126, 102), (22, 102)])
    ice = ""
    for x, y in ((44, 112), (64, 118), (88, 110), (108, 120), (54, 126), (96, 126)):
        ice += part(rr(x - 8, y - 7, 16, 14, 3), "#DDF2FF", s=None, ol="#8EB4DE", k=.6, hl=hidot(x - 3, y - 3, 1.6))
    frost = flat("M20,104 C34,98 44,108 58,100 C70,108 84,98 98,106 C110,98 120,106 128,102 L130,110 L18,110Z", "#FFFFFF", .9)
    o += comp(inside, "#B9DDF8", frost + ice, s=None, ol=FRIDGE_OL, k=.9)
    front = rr(8, 130, 132, 62, 10)
    o += comp(front, FRIDGE, flat(blob([(4, 160), (16, 150), (30, 156), (36, 176), (20, 196), (0, 196)]), "#FFFFFF", .8)
              + flat(blob([(144, 136), (128, 140), (118, 132), (130, 124), (146, 124)]), "#FFFFFF", .8), s=S(6, 7), ol=FRIDGE_OL)
    o += part(rr(50, 142, 48, 10, 5), "#9DB6DA", s=None, ol=FRIDGE_OL, k=.8)
    for a in (0, 60, 120):
        o += g(ln("M0,-11 L0,11 M-4,-8 L0,-4 L4,-8 M-4,8 L0,4 L4,8", "#5A86D6", .9), f"translate(74 172) rotate({a})")
    o += sparkle(140, 104, 7, "#FFFFFF") + sparkle(12, 120, 5, "#FFFFFF")
    return o


@place
def cupboard():
    wood, inner, ol = "#F2C48A", "#FFF3DF", "#B9864E"
    o = flat(rr(30, 182, 140, 8, 4), K.SHADOW, .1)
    o += part("M30,24 L6,8 L6,188 L30,176Z", wood, s=S(3, 4), ol=ol) + part(ell(14, 100, 3.5), "#8C5A2C", s=None)
    o += part("M170,24 L194,8 L194,188 L170,176Z", wood, s=S(3, 4), ol=ol) + part(ell(186, 100, 3.5), "#8C5A2C", s=None)
    body = rr(26, 16, 148, 166, 10)
    o += part(body, wood, s=S(7, 8), ol=ol)
    shelves = "".join(part(rr(36, y, 128, 7, 2), lt(wood, .25), s=None, ol=ol, k=.8) for y in (74, 126))
    o += comp(rr(36, 26, 128, 146, 6), inner, flat("M36,26 L164,26 L164,40 L36,40Z", "#F2DCC0") + shelves, s=None, ol=ol, k=.9)
    o += part(rr(20, 8, 160, 14, 6), lt(wood, .15), s=None, ol=ol)
    return o


@place
def sink():
    top, cab, ol = "#E9EEF6", "#8FD0C0", "#5E9E90"
    o = ground(100, 193, 96, 7)
    o += K.hose("M100,40 L100,14 C100,4 120,2 122,14 L122,20", "#C9D2E0", 8 * U, ol="#7E869A")
    o += part(rr(92, 36, 16, 8, 3), "#C9D2E0", s=None, ol="#7E869A")
    o += part(drop_d(122, 26, .6), "#7FD0FF", s=None, ol="#4F9AD0", k=.7)
    o += part(poly([(4, 64), (196, 64), (190, 40), (10, 40)]), top, s=None, ol="#8E96B8")
    o += part(rr(40, 42, 120, 22, 10), "#B7C6DE", s=None, ol="#7E8CB0")
    o += part(rr(46, 46, 108, 16, 8), "#D6E6F7", s=None, ol=False)
    for x, y, r in ((70, 50, 5), (82, 47, 4), (126, 52, 4.5)):
        o += part(ell(x, y, r), "#FFFFFF", s=None, ol="#8EC6E8", k=.6)
    o += part(rr(2, 62, 196, 14, 5), top, s=S(2, 3), ol="#8E96B8")
    o += part(rr(10, 74, 180, 116, 6), cab, s=S(7, 8), ol=ol)
    for x in (18, 104):
        o += part(rr(x, 84, 78, 96, 6), lt(cab, .2), s=None, ol=ol, k=.8)
    o += part(rr(84, 118, 6, 22, 3), "#FFFFFF", s=None, ol=ol, k=.8) + part(rr(110, 118, 6, 22, 3), "#FFFFFF", s=None, ol=ol, k=.8)
    o += part(rr(150, 36, 24, 12, 4), "#FFD43B", s=None) + part(rr(150, 30, 24, 7, 3), "#4FC461", s=None)
    return o


# ---------------------------------------------------------------- 大自然
@place
def sky():
    blue, ol = "#7CC8FF", "#A3CCEA"
    puffs = [(x, 70, 13 if i % 2 else 15) for i, x in enumerate(range(34, 168, 19))]
    puffs += [(x, 136, 12 if i % 2 else 14) for i, x in enumerate(range(38, 166, 21))]
    puffs += [(20, 90, 14), (18, 114, 14), (182, 90, 14), (184, 114, 14), (26, 74, 12), (174, 74, 12), (28, 132, 12), (172, 132, 12)]
    o = "".join(part(ell(x, y, r), "#FFFFFF", s=None, ol=ol) for x, y, r in puffs)
    o += flat(rr(16, 70, 168, 66, 30), "#FFFFFF")
    patch = rr(26, 78, 148, 50, 22)
    o += comp(patch, blue, flat(rr(20, 106, 170, 30, 0), lt(blue, .22)) + flat(ell(150, 94, 26), "#FFE27A", .4),
              s=None, ol="#5AA6E0")
    o += part(ell(150, 96, 12), YELLOW, s=S(2, 2.5), ol=lin(YELLOW))
    for a in range(0, 360, 45):
        o += g(ln("M0,-16 L0,-21", "#F2B91E", 1.1), f"translate(150 96) rotate({a})")
    o += part(cloud_d(76, 106, .5), "#FFFFFF", s=S(3, 3.5), ol=ol)
    o += part(cloud_d(116, 120, .26), "#FFFFFF", s=None, ol=ol, k=.8)
    return g(o, "translate(0 5)")


@place
def tree():
    trunk, leaf, ol = "#A8693D", "#5DBB63", "#3E8A44"
    o = ground(96, 193, 46, 6)
    o += part("M88,196 C92,170 90,140 88,110 L108,110 C106,140 104,170 112,196 C104,198 94,198 88,196Z", trunk, s=S(4, 5))
    o += part("M90,134 C70,128 46,126 20,128 C14,128 12,138 18,140 C44,140 68,142 90,148Z", trunk, s=S(3, 4))
    o += part("M106,118 C126,110 150,104 178,104 C184,104 186,114 180,116 C154,118 130,124 106,132Z", trunk, s=S(3, 4))
    o += part(ell(98, 162, 7, 10), "#5A3420", s=None, ol=lin(trunk))
    for cx, cy, r in ((14, 126, 12), (186, 102, 12)):
        o += part(ell(cx, cy, r), leaf, s=S(2, 3), ol=ol)
    blobs = [(54, 72, 34, leaf), (146, 70, 34, leaf), (100, 40, 40, lt(leaf, .12)), (70, 34, 26, lt(leaf, .12)),
             (132, 34, 26, lt(leaf, .12)), (100, 88, 36, shd(leaf))]
    for cx, cy, r, c in blobs:
        o += part(ell(cx, cy, r), c, s=S(5, 6), ol=ol)
    for x, y in ((80, 50), (120, 62), (60, 80), (140, 84), (100, 22)):
        o += part(ell(x, y, 4), RED, s=None, ol="#A8262A", k=.7)
    o += part("M78,196 C82,186 86,186 88,190 C90,182 96,182 98,192 C100,184 108,186 110,192 L114,196Z", "#7ED957", s=None, ol=ol)
    return o


@place
def grass():
    gr, ol, wood = "#7ED957", "#4E9A34", "#E0A866"
    o = ""
    for x in range(22, 186, 32):
        o += part(f"M{x - 5},112 L{x - 5},68 L{x},60 L{x + 5},68 L{x + 5},112Z", wood, s=S(2, 2.5), ol=lin(wood))
    o += part(rr(12, 74, 176, 8, 3), wood, s=None, ol=lin(wood)) + part(rr(12, 94, 176, 8, 3), wood, s=None, ol=lin(wood))
    mound = "M6,150 C6,112 40,98 100,98 C160,98 194,112 194,150 C194,166 170,174 100,174 C30,174 6,166 6,150Z"
    blades = "".join(flat(f"M{x - 4},178 L{x},160 L{x + 4},178Z", shd(gr)) for x in range(8, 196, 10))
    o += comp(mound, gr, flat(ell(100, 108, 80, 12), lt(gr, .3)) + blades, s=S(6, 7), ol=ol, hl=H("M30,118 C50,108 80,104 110,104", 4, .6))
    for x, y in ((40, 128), (150, 124), (96, 140), (126, 152), (64, 150)):
        o += g(ln("M0,8 L0,0 M-4,8 L-6,2 M4,8 L6,2", "#3E8A2C", .8), f"translate({x} {y})")
    for x, y, c in ((52, 122, "#FFFFFF"), (140, 118, YELLOW), (110, 132, PINK), (76, 144, YELLOW), (160, 140, "#FFFFFF")):
        o += part(star_d(5, 2.6, n_=5, cx=x, cy=y, round_=.3), c, s=None, ol=lin(c) if c != "#FFFFFF" else "#C9C2DD", k=.6)
        o += flat(ell(x, y, 1.6), "#FFB020")
    return o


@place
def sea():
    top, deep = "#4FB4F5", "#2E86D8"
    waves = "M0,80 " + " ".join(f"Q{x + 10},{68} {x + 20},{80}" for x in range(0, 200, 20))
    body = waves + " L200,147 L0,147Z"
    inner = flat("M0,110 L200,110 L200,150 L0,150Z", lg([(0, top), (1, deep)]))
    o = comp(body, top, inner, s=None, ol="#2A78C0")
    for x in range(0, 200, 20):
        o += flat(f"M{x + 2},79 Q{x + 10},70 {x + 18},79 Q{x + 10},75 {x + 2},79Z", "#FFFFFF", .9)
    for x, y, r in ((30, 120, 4), (36, 108, 2.5), (150, 128, 3.5), (156, 116, 2.4), (96, 134, 3)):
        o += part(ell(x, y, r), "#DFF4FF", s=None, ol="#8EC6E8", k=.8)
    for x in (12, 184):
        o += part(tube([(x, 148, 3.5), (x - 4, 132, 3), (x + 3, 118, 2.6), (x - 1, 106, 2)], 6), "#3FAE6A", s=None, ol="#2E7A4A")
    o += part(star_d(10, 5, cx=70, cy=136, round_=.3), "#FF9A6B", s=None, ol="#D0603A")
    o += part("M122,146 C120,136 128,128 136,128 C144,128 152,136 150,146Z", "#FFC2D1", s=None, ol="#E07A9A")
    o += ln("M136,146 L136,132 M130,146 L127,134 M142,146 L145,134", "#E07A9A", .7)
    return o


# ---------------------------------------------------------------- 超市
def _awning(col, y=44, h=30):
    o = ""
    for i, x in enumerate(range(10, 190, 20)):
        c = col if i % 2 == 0 else "#FFFFFF"
        o += part(f"M{x},{y} L{x + 20},{y} L{x + 20},{y + h - 8} Q{x + 10},{y + h + 4} {x},{y + h - 8}Z", c, s=None,
                  ol=lin(col), k=.8)
    o += part(rr(6, y - 8, 188, 12, 5), shd(col), s=None, ol=lin(col))
    return o


def _sign(icon, col):
    o = part(rr(60, 2, 80, 38, 12), "#FFFFFF", s=S(3, 4), ol=lin(col))
    o += ln("M80,40 L80,36 M120,40 L120,36", lin(col), .8)
    return o + icon


def _stand_base(col):
    wood = "#D9A066"
    o = ground(100, 193, 90, 7)
    for x in (22, 178):
        o += part(rr(x - 4, 70, 8, 64, 3), wood, s=None, ol=lin(wood))
    o += part(rr(10, 128, 180, 62, 8), wood, s=S(6, 7), ol=lin(wood), hl=H("M20,140 L180,140", 3, .4))
    o += ln("M10,150 L190,150 M10,170 L190,170", shd(wood), .7)
    o += part(rr(18, 186, 14, 9, 3), shd(wood), s=None) + part(rr(168, 186, 14, 9, 3), shd(wood), s=None)
    o += part(rr(6, 122, 188, 10, 4), lt(wood, .2), s=None, ol=lin(wood))
    return o


def _crate(x, y, w, h, fill=""):
    wood = "#E8B57A"
    o = fill
    o += part(rr(x, y, w, h, 3), wood, s=S(2, 3), ol=lin(wood))
    o += ln(f"M{x + 3},{y + h / 2} L{x + w - 3},{y + h / 2}", shd(wood), .6)
    return o


def _ball_pile(x, y, w, col, r, rows=2):
    o = ""
    for j in range(rows):
        k = int(w // (2 * r))
        for i in range(k - j):
            cx = x + r + j * r + i * 2 * r + (w - k * 2 * r) / 2
            cy = y - j * r * 1.5
            o += part(ell(cx, cy, r), col, s=S(1.5, 2), ol=lin(col), k=.7, hl=hidot(cx - r * .35, cy - r * .35, r * .25))
    return o


def _grapes_icon(cx, cy, s=1.0, col=PURPLE):
    o = ""
    for dx, dy in ((-8, -8), (0, -8), (8, -8), (-4, 0), (4, 0), (0, 8)):
        o += part(ell(cx + dx * s, cy + dy * s, 5 * s), col, s=None, ol=lin(col), k=.6)
    o += part(f"M{n(cx)},{n(cy - 13 * s)} C{n(cx + 4 * s)},{n(cy - 20 * s)} {n(cx + 12 * s)},{n(cy - 20 * s)} {n(cx + 14 * s)},{n(cy - 16 * s)} "
              f"C{n(cx + 10 * s)},{n(cy - 11 * s)} {n(cx + 4 * s)},{n(cy - 11 * s)} {n(cx)},{n(cy - 13 * s)}Z", GREEN, s=None, ol=lin(GREEN), k=.6)
    return o


def _strawberry(cx, cy, s=1.0):
    d = (f"M{n(cx)},{n(cy - 10 * s)} C{n(cx + 12 * s)},{n(cy - 12 * s)} {n(cx + 14 * s)},{n(cy)} {n(cx + 8 * s)},{n(cy + 8 * s)} "
         f"C{n(cx + 4 * s)},{n(cy + 13 * s)} {n(cx - 4 * s)},{n(cy + 13 * s)} {n(cx - 8 * s)},{n(cy + 8 * s)} "
         f"C{n(cx - 14 * s)},{n(cy)} {n(cx - 12 * s)},{n(cy - 12 * s)} {n(cx)},{n(cy - 10 * s)}Z")
    o = part(d, "#F0394F", s=None, ol=lin("#F0394F"), k=.7)
    o += "".join(flat(ell(cx + dx * s, cy + dy * s, 1.1 * s, 1.5 * s), "#FFE48A") for dx, dy in ((-4, -2), (4, -1), (0, 4), (-5, 5), (5, 6)))
    o += part(star_d(7 * s, 3 * s, n_=5, cx=cx, cy=cy - 11 * s, round_=.2), GREEN, s=None, ol=lin(GREEN), k=.6)
    return o


@place
def fruit_stand():
    awn = "#F2463F"
    o = _stand_base(awn)
    o += _crate(16, 104, 54, 24, _ball_pile(18, 100, 50, "#FF9A1F", 8.5))
    o += _crate(73, 104, 54, 24)
    o += _crate(130, 104, 54, 24, "".join(_grapes_icon(x, 92, 1.0) for x in (144, 168)))
    o += _awning(awn)
    o += _sign(_strawberry(100, 22, 1.3), awn)
    return o


def _croissant(cx, cy, s=1.0, rot=0):
    """A croissant: five puffy segments along an arc, small at the tips."""
    col = "#E8A04C"
    segs = [(-80, 6, 5), (80, 6, 5), (-42, 8.5, 7.5), (42, 8.5, 7.5), (0, 10.5, 9.5)]
    o = ""
    for a, rx, ry in segs:
        x, y = 15 * math.sin(math.radians(a)), 9 - 15 * math.cos(math.radians(a)) + 6
        o += g(part(ell(0, 0, rx, ry), col if a else lt(col, .12), s=(-1.5, -2), ol=lin(col), k=.7), f"translate({n(x)} {n(y)}) rotate({a})")
    return g(o, f"translate({n(cx)} {n(cy)}) rotate({rot}) scale({s})")


@place
def bakery():
    awn = "#FF9A3D"
    o = _stand_base(awn)
    o += _crate(16, 104, 54, 24, _croissant(36, 98, 1.0, -8) + _croissant(52, 100, .9, 10))
    o += _crate(73, 104, 54, 24)
    bag = part("M134,104 L146,62 L164,62 L176,104Z", "#F3E2BE", s=None, ol="#C9A77A", k=.8)
    bag += part("M144,66 C140,58 146,48 154,50 C160,52 164,60 160,70 L152,96 C150,100 146,100 146,96Z", "#E39A4C", s=None, ol=lin("#E39A4C"), k=.8)
    bag += part("M156,70 C156,60 164,52 172,56 C176,60 174,70 170,76 L160,98 C158,102 154,100 154,96Z", "#D98E46", s=None, ol=lin("#E39A4C"), k=.8)
    o += _crate(130, 104, 54, 24, bag)
    o += _awning(awn)
    o += _sign(_croissant(100, 18, 1.15), awn)
    return o


def _broccoli(cx, cy, s=1.0):
    o = part(f"M{n(cx - 4 * s)},{n(cy)} L{n(cx + 4 * s)},{n(cy)} L{n(cx + 5 * s)},{n(cy + 14 * s)} L{n(cx - 5 * s)},{n(cy + 14 * s)}Z",
             "#9BD46A", s=None, ol="#4E9A34", k=.6)
    for dx, dy, r in ((-8, -2, 7), (8, -2, 7), (0, -8, 8), (-3, 0, 6), (4, 1, 6)):
        o += part(ell(cx + dx * s, cy + dy * s, r * s), "#3FAE4A", s=None, ol="#2E7A34", k=.6)
    return o


def _eggplant(cx, cy, s=1.0, rot=0):
    o = part("M-14,0 C-14,-10 -6,-14 0,-12 C10,-10 22,-6 24,4 C26,14 14,18 4,14 C-4,12 -14,10 -14,0Z", "#8E4FD8", s=(-1.5, -2), k=.7)
    o += part("M-14,-2 L-20,-8 L-12,-10 L-8,-14 L-6,-6Z", GREEN, s=None, k=.6)
    return g(o, f"translate({n(cx)} {n(cy)}) rotate({rot}) scale({s})")


def _corn(cx, cy, s=1.0, rot=0):
    o = part("M-6,-18 C-6,-24 6,-24 6,-18 L6,14 C6,20 -6,20 -6,14Z", YELLOW, s=None, k=.7)
    o += part("M-6,18 C-14,8 -14,-6 -10,-14 C-6,-4 -4,8 0,20Z", GREEN, s=None, k=.6)
    o += part("M6,18 C14,8 14,-6 10,-14 C6,-4 4,8 0,20Z", GREEN, s=None, k=.6)
    return g(o, f"translate({n(cx)} {n(cy)}) rotate({rot}) scale({s})")


@place
def veggie_stand():
    awn = "#3FB55A"
    o = _stand_base(awn)
    o += _crate(16, 104, 54, 24, _broccoli(30, 96, 1.1) + _broccoli(54, 98, 1.0))
    o += _crate(73, 104, 54, 24)
    o += _crate(130, 104, 54, 24, _eggplant(146, 98, .9, -20) + _corn(170, 92, 1.0, 14))
    o += _awning(awn)
    o += _sign(_broccoli(100, 22, 1.25), awn)
    return o


@place
def frozen_case():
    body, ol, ice = "#DCEFFF", "#5E86C0", "#B9DDF8"
    o = ground(100, 193, 92, 7)
    o += part(rr(20, 184, 14, 10, 3), "#6E6880", s=None) + part(rr(166, 184, 14, 10, 3), "#6E6880", s=None)
    inside = poly([(10, 104), (190, 104), (176, 76), (24, 76)])
    stuff = flat("M20,82 C40,74 60,86 80,78 C100,86 130,74 150,82 C164,76 176,84 182,80 L184,92 L16,92Z", "#FFFFFF", .9)
    for x, y, c in ((44, 92, "#FF8FB1"), (70, 96, "#FFD43B"), (126, 94, "#7ED957"), (150, 92, "#FF8FB1")):
        stuff += part(rr(x - 10, y - 8, 20, 14, 3), c, s=None, ol=lin(c), k=.6) + flat(rr(x - 6, y - 5, 12, 4, 2), "#FFFFFF", .8)
    o += comp(inside, ice, stuff, s=None, ol=ol)
    o += part(poly([(30, 76), (100, 76), (98, 66), (36, 66)]), "#EAF6FF", s=None, ol=ol, op=.85)
    front = rr(6, 102, 188, 90, 14)
    frost = flat(blob([(0, 150), (16, 140), (30, 150), (24, 176), (0, 196)]), "#FFFFFF", .85)
    frost += flat(blob([(200, 116), (184, 112), (172, 120), (180, 140), (200, 146)]), "#FFFFFF", .85)
    o += comp(front, body, frost + flat(rr(6, 102, 188, 14, 0), lt(body, .4)), s=S(7, 8), ol=ol)
    for a in (0, 60, 120):
        o += g(ln("M0,-16 L0,16 M-5,-11 L0,-6 L5,-11 M-5,11 L0,6 L5,11", "#5A86D6", 1.0), f"translate(100 150) rotate({a})")
    o += part(rr(60, 2, 80, 38, 12), "#FFFFFF", s=S(3, 4), ol=ol)
    for a in (0, 60, 120):
        o += g(ln("M0,-13 L0,13 M-4,-9 L0,-5 L4,-9 M-4,9 L0,5 L4,9", "#3D8BF2", 1.0), f"translate(100 21) rotate({a})")
    o += part(rr(96, 40, 8, 26, 3), "#C9D2E0", s=None, ol=ol, k=.8)
    o += sparkle(170, 64, 7, "#FFFFFF") + sparkle(28, 60, 5, "#FFFFFF")
    return o


# ---------------------------------------------------------------- 資源回收
BINS = {
    "bin_paper": "#3D8BF2",
    "bin_bottle": "#FFC233",
    "bin_can": "#F2463F",
    "bin_food": "#4FC461",
    "bin_trash": "#9A94B0",
}


def _bin(col, icon):
    o = ground(100, 193, 64, 6)
    o += part(poly([(38, 62), (162, 62), (150, 8), (50, 8)]), shd(col), s=None, ol=lin(col))
    o += part(poly([(48, 56), (152, 56), (144, 18), (56, 18)]), dk(col, .25), s=None, ol=False, op=.35)
    o += part(rr(80, 2, 40, 9, 4), lt(col, .2), s=None, ol=lin(col), k=.8)
    o += part(rr(26, 50, 148, 34, 15), "#3A3150", s=None, ol=lin(col))
    o += flat(rr(34, 54, 132, 12, 6), "#5A4C78")
    o += part("M22,72 L178,72 L176,86 L24,86Z", lt(col, .25), s=None, ol=lin(col))
    body = "M30,82 L170,82 L158,180 C157,187 152,190 146,190 L54,190 C48,190 43,187 42,180Z"
    o += part(body, col, s=S(8, 9), hl=H("M44,98 L52,170", 6, .5))
    for x in (56, 144):
        o += part(ell(x, 188, 9), "#4B4560", s=None, ol="#2A2436") + part(ell(x, 188, 3.5), "#C9C4D6", s=None, ol=False)
    o += part(ell(100, 132, 36), "#FFFFFF", s=S(2, 3), ol=lin(col))
    return o + icon


def _icon_paper(c):
    o = part("M84,110 L108,110 L118,120 L118,154 L84,154Z", "#FFFFFF", s=None, ol=c)
    o += part("M108,110 L108,120 L118,120Z", lt(c, .6), s=None, ol=c, k=.8)
    o += ln("M90,126 L110,126 M90,134 L112,134 M90,142 L106,142", c, .8)
    return o


def _icon_bottle(c):
    return (part("M95,108 L105,108 L105,114 C114,118 116,124 116,130 L116,154 C116,158 113,160 110,160 L90,160 C87,160 84,158 84,154 "
                 "L84,130 C84,124 86,118 95,114Z", lt(c, .75), s=None, ol=c)
            + part(rr(93, 104, 14, 7, 2), c, s=None, ol=c) + ln("M86,136 L114,136 M86,146 L114,146", c, .7))


def _icon_can(c):
    o = part(rr(86, 112, 28, 42, 5), lt(c, .7), s=None, ol=c)
    o += part(ell(100, 114, 14, 4), "#FFFFFF", s=None, ol=c, k=.8) + ln("M86,124 L114,124 M86,144 L114,144", c, .7)
    o += part(rr(96, 107, 10, 5, 2), "#FFFFFF", s=None, ol=c, k=.7)
    return o


def _icon_food(c):
    core = ("M92,116 C84,118 82,126 88,130 C84,136 84,144 90,148 C84,152 86,160 96,160 L104,160 C114,160 116,152 110,148 "
            "C116,144 116,136 112,130 C118,126 116,118 108,116Z")
    o = part(core, "#FFF3C8", s=None, ol=c)
    o += part("M92,116 C96,120 104,120 108,116 C104,112 96,112 92,116Z", "#F2463F", s=None, ol="#A8262A", k=.7)
    o += part("M92,160 C96,156 104,156 108,160 C104,164 96,164 92,160Z", "#F2463F", s=None, ol="#A8262A", k=.7)
    o += ln("M100,114 L102,104", "#6B4A26", 1.0)
    o += part("M102,108 C106,100 114,100 116,104 C112,108 106,110 102,108Z", GREEN, s=None, ol=lin(GREEN), k=.7)
    o += flat(ell(97, 138, 1.6, 2.6), "#6B4A26") + flat(ell(103, 138, 1.6, 2.6), "#6B4A26")
    return o


def _icon_trash(c):
    ball_ = blob([(82, 140), (86, 122), (100, 114), (114, 120), (120, 136), (114, 152), (98, 158), (86, 152)])
    o = part(ball_, "#FFFFFF", s=None, ol=c)
    o += ln("M88,130 L98,136 L102,124 M104,140 L114,134 M92,148 L102,142 L106,152", c, .7)
    return o


@place
def bin_paper():
    c = BINS["bin_paper"]
    return _bin(c, _icon_paper(lin(c)))


@place
def bin_bottle():
    c = BINS["bin_bottle"]
    return _bin(c, _icon_bottle(lin(c)))


@place
def bin_can():
    c = BINS["bin_can"]
    return _bin(c, _icon_can(lin(c)))


@place
def bin_food():
    c = BINS["bin_food"]
    return _bin(c, _icon_food(lin(c)))


@place
def bin_trash():
    c = BINS["bin_trash"]
    return _bin(c, _icon_trash(dk(c, .3)))


# ================================================================ SCENES (390 x 600 backdrops)
SCENES = {}
W_, H_ = K.SCENE_W, K.SCENE_H


def scene(f):
    SCENES[f.__name__] = f
    return f


def rect(x, y, w, h, fill, op=None):
    o_ = f' opacity="{op}"' if op is not None else ""
    return f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="{fill}"{o_}/>'


def hline(y, col, k=1.0, x0=0, x1=W_, op=None):
    return ln(f"M{n(x0)},{n(y)} L{n(x1)},{n(y)}", col, k, op)


def _floor_planks(y0, y1, col, line):
    o = rect(0, y0, W_, y1 - y0, col)
    ys, y, h = [], y0, 34
    while y < y1:
        ys.append(y)
        y += h
        h *= 1.18
    rng = random.Random(7)
    for i, y in enumerate(ys[1:], 1):
        o += hline(y, line, .9)
    for i in range(len(ys)):
        top = ys[i]
        bot = ys[i + 1] if i + 1 < len(ys) else y1
        x = rng.uniform(20, 120)
        while x < W_:
            o += ln(f"M{n(x)},{n(top)} L{n(x)},{n(bot)}", line, .9)
            x += rng.uniform(130, 190)
    return o


def _window(x, y, w, h, frame="#FFFFFF", fol="#C9B8A0", glass="#CBEBFF", sun=True):
    o = part(rr(x, y, w, h, 12), frame, s=None, ol=fol)
    inner = rr(x + 9, y + 9, w - 18, h - 18, 7)
    sky_in = flat(rr(x, y + h * .55, w, h, 0), lt(glass, .35)) + flat(cloud_d(x + w * .36, y + h * .5, .38), "#FFFFFF", .95)
    if sun:
        sky_in += flat(ell(x + w * .75, y + h * .3, 9), "#FFE58A")
    o += comp(inner, glass, sky_in, s=None, ol=lt(fol, .2), k=.8)
    o += ln(f"M{n(x + w / 2)},{n(y + 9)} L{n(x + w / 2)},{n(y + h - 9)} M{n(x + 9)},{n(y + h / 2)} L{n(x + w - 9)},{n(y + h / 2)}",
            frame, 3.2) + ln(f"M{n(x + w / 2)},{n(y + 9)} L{n(x + w / 2)},{n(y + h - 9)} M{n(x + 9)},{n(y + h / 2)} L{n(x + w - 9)},{n(y + h / 2)}",
                             lt(fol, .45), .6)
    return o


@scene
def scene_room():
    wall, stripe, floor, line = "#FFF3DE", "#FFE9C6", "#F4D5A8", "#E6BF8A"
    o = rect(0, 0, W_, 244, wall)
    o += "".join(rect(x, 0, 16, 244, stripe, .8) for x in range(12, W_, 42))
    # a garland of little flags
    o += ln("M0,14 Q98,40 195,24 Q292,40 390,14", "#D9C3A0", .8)
    for i, x in enumerate(range(18, W_, 30)):
        t = x / W_
        y = 14 + 26 * math.sin(math.pi * (2 * t if t < .5 else 2 * t - 1)) * .9 - (4 if abs(t - .5) < .05 else 0)
        c = calm(["#FF9FB8", "#8ECDF6", "#FFD66B", "#9EDB8E"][i % 4], .35)
        o += part(f"M{n(x - 9)},{n(y)} L{n(x + 9)},{n(y)} L{n(x)},{n(y + 16)}Z", c, s=None, ol=lin(c), k=.6)
    # window with curtains
    o += part(rr(166, 40, 132, 9, 4.5), calm("#C9834F", .3), s=None)
    o += _window(176, 48, 112, 92, fol="#D2BFA4")
    for x0, x1, xb in ((164, 188, 182), (300, 276, 282)):
        c = calm("#FF9FB8", .35)
        o += part(f"M{x0},46 C{x0},80 {x0 + (x1 - x0) * .2},120 {x0 - (x1 - x0) * .2},150 L{xb},150 C{xb + (x1 - xb) * .3},120 {x1},80 {x1},46Z",
                  c, s=None, ol=lin(c), k=.8)
    # a little framed star above the shelf
    o += part(rr(36, 40, 50, 42, 6), calm("#C9834F", .35), s=None) + part(rr(42, 46, 38, 30, 4), "#FFFDF6", s=None, ol=False)
    o += flat(star_d(10, 4.6, cx=61, cy=62, round_=.2), calm(YELLOW, .3))
    o += rect(0, 236, W_, 12, "#FFFFFF") + hline(236, "#E9D6B6", .8) + hline(248, line, .8)
    o += _floor_planks(248, H_, floor, line)
    rug = ell(195, 532, 156, 44)
    o += part(rug, calm("#C9B6F2", .45), s=None, ol=calm("#A08BD6", .4)) + K.stroke(ell(195, 532, 138, 36), "#FFFFFF", 1.2, extra=' opacity=".7"')
    return o


@scene
def scene_bathroom():
    wall, grout, floor = "#E2F4F6", "#CDE8EC", "#EEF1F6"
    o = rect(0, 0, W_, 446, wall)
    for x in range(0, W_ + 1, 39):
        o += ln(f"M{x},0 L{x},446", grout, .9)
    for y in range(39, 446, 39):
        o += hline(y, grout, .9)
    o += rect(0, 300, W_, 12, calm(TEAL, .5)) + hline(300, calm(TEAL, .3), .6) + hline(312, calm(TEAL, .3), .6)
    # mirror
    o += part(ell(94, 70, 52, 46), "#FFFFFF", s=None, ol="#A9C9D3")
    o += comp(ell(94, 70, 44, 38), "#D3EEF8", flat("M60,40 L80,30 L130,90 L110,104Z", "#FFFFFF", .6)
              + flat("M86,34 L94,30 L138,80 L132,88Z", "#FFFFFF", .5), s=None, ol="#A9C9D3", k=.8)
    # small frosted window
    o += _window(264, 26, 96, 64, fol="#A9C9D3", glass="#D9F0FA", sun=False)
    o += rect(0, 446, W_, H_ - 446, floor)
    for x in range(0, W_ + 40, 52):
        for y, k in ((446, 0), (498, 1), (550, 0)):
            if (x // 52 + k) % 2 == 0:
                o += rect(x, y, 52, 52, "#E2E8F1")
    o += hline(446, "#C9D3E2", .9)
    mat = rr(30, 512, 150, 52, 22)
    o += comp(mat, calm("#9EDBB8", .4), "".join(flat(f"M{x},500 L{x + 10},500 L{x + 10},580 L{x},580Z", "#FFFFFF", .45) for x in (60, 100, 140)),
              s=None, ol=calm("#6FBF92", .4))
    return o


@scene
def scene_kitchen():
    wall, floor_a, floor_b = "#FFF6DA", "#F6ECDC", "#EADBC4"
    o = rect(0, 0, W_, 452, wall)
    o += "".join(rect(x, 0, 2, 452, "#FBEBC5", .8) for x in range(20, W_, 36))
    # tiles behind the counter
    o += rect(186, 236, W_ - 186, 92, "#FFFFFF")
    for x in range(186, W_ + 1, 26):
        o += ln(f"M{x},236 L{x},328", "#E9DEC7", .8)
    for y in range(236, 330, 23):
        o += hline(y, "#E9DEC7", .8, 186, W_)
    # window with a little plant
    o += _window(28, 34, 112, 92, fol="#D7C29C")
    o += part("M24,30 L144,30 L140,46 C128,40 118,52 106,44 C94,52 84,40 72,48 C60,40 50,52 38,44 C30,50 26,40 24,46Z",
              calm("#FF8A8A", .35), s=None, ol=calm("#D86B6B", .3), k=.8)
    o += part(rr(22, 124, 124, 8, 4), calm("#C9834F", .35), s=None)
    o += part("M74,124 L70,108 L94,108 L90,124Z", calm("#E8735A", .35), s=None) + flat(ell(82, 102, 14, 9), calm(GREEN, .35))
    # clock above the cupboard
    o += part(ell(282, 40, 22), "#FFFFFF", s=None, ol=calm("#8E86A8", .2))
    o += ln("M282,40 L282,26 M282,40 L292,46", calm("#4B3A5E", .35), 1.0)
    o += rect(0, 452, W_, H_ - 452, floor_a)
    for i, x in enumerate(range(0, W_ + 40, 39)):
        for j, y in enumerate(range(452, H_, 37)):
            if (i + j) % 2 == 0:
                o += rect(x, y, 39, 37, floor_b, .55)
    o += hline(452, "#E2CFAE", 1.0)
    return o


@scene
def scene_nature():
    o = rect(0, 0, W_, 260, lg([(0, "#BEE6FF"), (1, "#E8F7FF")]))
    o += flat(cloud_d(330, 196, .5), "#FFFFFF", .8) + flat(cloud_d(56, 200, .42), "#FFFFFF", .8)
    o += part("M0,236 C40,196 80,186 120,206 C150,180 200,172 240,200 C280,176 330,180 390,214 L390,260 L0,260Z",
              calm("#8FC9B8", .35), s=None, ol=False)
    o += part("M0,250 C60,226 120,230 170,244 C230,222 300,220 390,240 L390,470 L0,470Z", lg([(0, "#CFEDB0"), (1, "#B8E49A")]),
              s=None, ol=calm("#7FBF6A", .35))
    o += ln("M0,310 C80,296 160,300 240,312 M140,380 C220,370 300,372 390,384", "#A9DA88", 1.0, op=.7)
    rng = random.Random(11)
    for _ in range(26):
        x, y = rng.uniform(10, 380), rng.uniform(266, 456)
        c = rng.choice(["#FFFFFF", "#FFE58A", "#FFC2D1"])
        o += flat(ell(x, y, 2.6), c, .85)
    o += part("M0,462 C80,450 160,456 230,450 C300,446 350,452 390,448 L390,500 L0,500Z", "#F6E3B8", s=None, ol=calm("#D9B87A", .35))
    o += rect(0, 486, W_, H_ - 486, lg([(0, "#A9DBF7"), (1, "#8CCDF2")]))
    o += hline(486, calm("#6FB3E0", .3), .9)
    for y in (520, 556, 588):
        o += ln(" ".join(("M" if i == 0 else "Q" if i % 2 else "") for i in range(1)) + f"M12,{y} " + " ".join(
            f"Q{x + 12},{y - 6} {x + 24},{y}" for x in range(12, 370, 24)), "#FFFFFF", .8, op=.45)
    return o


@scene
def scene_market():
    wall, floor = "#FFF5E8", "#F3EFF6"
    o = rect(0, 0, W_, 180, wall)
    o += rect(0, 0, W_, 16, calm("#B9A6D6", .45))
    for x in (70, 195, 320):
        o += ln(f"M{x},16 L{x},30", "#C9BFD8", .8) + part(f"M{x - 18},42 C{x - 18},30 {x + 18},30 {x + 18},42Z", calm("#FFD66B", .3), s=None)
        o += flat(ell(x, 46, 26, 8), "#FFF6C8", .55)
    for x0, x1 in ((8, 186), (204, 382)):
        o += part(rr(x0, 60, x1 - x0, 120, 6), calm("#D9A066", .5), s=None)
        rng = random.Random(x0)
        for y in (86, 122, 158):
            o += rect(x0 + 6, y - 22, x1 - x0 - 12, 22, calm("#B98B6A", .55))
            x = x0 + 10
            while x < x1 - 22:
                w = rng.choice([12, 14, 16, 18])
                h = rng.choice([12, 14, 16, 18])
                c = calm(rng.choice([RED, BLUE, YELLOW, GREEN, PINK, "#FF8A3D"]), .55)
                o += part(rr(x, y - h, w, h, 2), c, s=None, ol=False)
                x += w + 3
            o += rect(x0 + 2, y, x1 - x0 - 4, 5, calm("#C9834F", .5))
    for x, c in ((97, "#FF9FB8"), (293, "#8ECDF6")):
        o += ln(f"M{x - 30},16 L{x - 30},26 M{x + 30},16 L{x + 30},26", "#C9BFD8", .7)
        o += part(rr(x - 40, 24, 80, 22, 8), calm(c, .35), s=None, ol=calm(lin(c), .45))
    o += rect(0, 180, W_, H_ - 180, floor)
    for i in range(-6, 7):
        o += ln(f"M{n(195 + i * 34)},180 L{n(195 + i * 110)},600", "#E1DAE9", .9)
    y, h = 180, 22
    while y < H_:
        o += hline(y, "#E1DAE9", .9)
        y += h
        h *= 1.16
    o += rect(0, 176, W_, 6, calm("#B9A6D6", .5))
    return o


@scene
def scene_recycling():
    wall, brick, floor = "#E9F3E6", "#DCEBD8", "#EFECE6"
    o = rect(0, 0, W_, 200, wall)
    for j, y in enumerate(range(40, 200, 20)):
        o += hline(y, brick, .9)
        for x in range(0 if j % 2 else 24, W_, 48):
            o += ln(f"M{x},{y} L{x},{y + 20}", brick, .9)
    for i, x in enumerate(range(0, W_, 30)):
        c = calm("#4FC461", .4) if i % 2 == 0 else "#FFFFFF"
        o += part(f"M{x},0 L{x + 30},0 L{x + 30},26 Q{x + 15},40 {x},26Z", c, s=None, ol=calm("#3E8C3A", .45), k=.7)
    o += rect(0, 196, W_, 8, "#D9D2C8") + rect(0, 204, W_, H_ - 204, floor)
    o += part(rr(18, 232, 354, 330, 18), "none", s=None, ol=False)
    o += K.stroke(rr(14, 226, 362, 340, 20), calm("#FFC233", .35), 2.4, extra=' stroke-dasharray="14 10"')
    for x in (34, 356):
        o += part(f"M{x - 16},198 L{x - 12},176 L{x + 12},176 L{x + 16},198Z", calm("#E8735A", .35), s=None)
        o += flat(ell(x - 8, 166, 12, 14), calm(GREEN, .35)) + flat(ell(x + 8, 162, 11, 16), calm(GREEN, .3)) + flat(ell(x, 154, 10, 14), calm(GREEN, .28))
    o += part(rr(178, 530, 34, 12, 4), "#D2CCC2", s=None, ol=False) + "".join(ln(f"M{x},532 L{x},540", "#BDB5AA", .6) for x in range(184, 210, 6))
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


def write_places(only=None):
    global U
    where = read_places()
    missing = set(where) ^ set(PLACES)
    if missing:
        raise SystemExit(f"places in content.dart and here differ: {sorted(missing)}")
    sizes = {}
    for name, fn in PLACES.items():
        if only and name not in only:
            continue
        shown = where[name][3] * K.SCENE_W
        K.begin(K.ol_for(shown))
        U = 140 / shown
        try:
            sizes[name] = save(name, fn())
        finally:
            U = 1.0
    return sizes


def write_scenes(only=None):
    sizes = {}
    for name, fn in SCENES.items():
        if only and name not in only:
            continue
        K.begin(K.OL_SCENE)
        sizes[name] = save(name, fn(), W_, H_)
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


LOOSE = {   # a few things lying about in each composite (where the app might scatter them)
    "room": [("ball", .2, .88), ("sock", .44, .9), ("book", .66, .86), ("pillow", .86, .9)],
    "bathroom": [("toothbrush", .14, .88), ("rubber_duck", .36, .9), ("towel", .6, .88), ("soap", .84, .9)],
    "kitchen": [("milk", .12, .88), ("vegetables", .34, .9), ("dirty_cup", .58, .88), ("ice_cream", .82, .88)],
    "nature": [("bird", .16, .62), ("cow", .4, .64), ("fish", .2, .76), ("monkey", .88, .78)],
    "market": [("apple", .14, .9), ("banana", .38, .9), ("bread", .62, .9), ("frozen_dumplings", .86, .9)],
    "recycling": [("newspaper", .12, .88), ("pet_bottle", .34, .9), ("soda_can", .56, .88), ("banana_peel", .8, .9)],
}


def composite(sid, x0, y0, thing_w=.22):
    """One scene with its places at their content.dart positions (all of them, freezer too) and a few things."""
    where = read_places()
    o = [f'<div style="position:absolute;left:{x0}px;top:{y0}px;width:{W_}px;height:{H_}px;overflow:hidden;'
         f'border-radius:6px;box-shadow:0 0 0 1px #D9D0E8">']
    o.append(_img(f"scene_{sid}", 0, 0, W_, H_))
    for pid, (sc, x, y, w) in where.items():
        if sc == sid:
            o.append(_img(pid, x * W_ - w * W_ / 2, y * H_ - w * W_ / 2, w * W_))
    for tid, x, y in LOOSE[sid]:
        o.append(_img(tid, x * W_ - thing_w * W_ / 2, y * H_ - thing_w * W_ / 2, thing_w * W_))
    o.append("</div>")
    return "".join(o)


def full_preview(out):
    things = list(THINGS)
    body, y = [], 0
    b, y = sheet_things(things, 200, 7, y, "Things, 200 px")
    body.append(b)
    b, y = sheet_things(things, 120, 11, y, "Things, 120 px")
    body.append(b)
    b, y = sheet_things(list(PLACES), 120, 11, y, "Places, 120 px")
    body.append(b)
    body.append(f'<div style="position:absolute;left:16px;top:{y + 8}px;font:bold 20px sans-serif;color:#4B3A5E">'
                f'Scenes with their places (content.dart positions) and a few things</div>')
    y += 44
    for i, sid in enumerate(["room", "bathroom", "kitchen", "nature", "market", "recycling"]):
        x = 16 + (i % 3) * (W_ + 24)
        yy = y + (i // 3) * (H_ + 40)
        body.append(composite(sid, x, yy))
        body.append(_label(sid, x, yy + H_ + 6, W_, 14))
    h = y + 2 * (H_ + 40) + 10
    w = 16 + 7 * 212
    render_html(page("".join(body), w, h), out, w, h)


def main(argv):
    if argv and argv[0] == "preview":
        full_preview(pathlib.Path(argv[1]))
        return
    if argv and argv[0] == "scenes":
        out = pathlib.Path(argv[1])
        body = "".join(composite(sid, 16 + i * (W_ + 24), 16) for i, sid in enumerate(argv[2:] or ["room", "bathroom", "kitchen"]))
        n_ = len(argv[2:] or [1, 2, 3])
        render_html(page(body, 16 + n_ * (W_ + 24), H_ + 32), out, 16 + n_ * (W_ + 24), H_ + 32)
        return
    if argv and argv[0] == "things":
        out = pathlib.Path(argv[1])
        cell = int(argv[2]) if len(argv) > 2 else 200
        names = argv[3:] or list(THINGS)
        cols = max(1, 1500 // (cell + 12))
        body, h = sheet_things(names, cell, cols)
        render_html(page(body, 16 + cols * (cell + 12), h + 10), out, 16 + cols * (cell + 12), h + 10)
        return
    sizes = write_things()
    sizes.update(write_places())
    sizes.update(write_scenes())
    big = max(sizes.items(), key=lambda kv: kv[1])
    print(f"{len(sizes)} pictures written to {K.OUT} (largest {big[0]} {big[1]:.1f} KB)")


if __name__ == "__main__":
    main(sys.argv[1:])
