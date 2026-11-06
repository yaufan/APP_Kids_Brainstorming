"""The pictures of 「是誰的？」 in 卡通城 (style A 動畫片風), drawn with the shared kit city_kit.py.

    python3 city_people.py                    # writes every picture to app/assets/art/city/
    python3 city_people.py dog hose           # only these
    python3 city_people.py preview out.png    # contact sheet + a check of 4 people on the street

What is drawn (ids as in app/lib/core/content.dart → owners and ownerThings):
  - the 14 owners, 200 x 200: full body, standing (the baby and the animals sit), facing the viewer,
    friendly, with EMPTY hands (they get their thing in the game). All are drawn at one scale with
    their feet on one ground line (GY), so they line up side by side under their thought bubbles;
  - their 14 things, 200 x 200, big and simple; each also reads as a flat silhouette (the app shows
    a pale lilac silhouette of the wanted thing in the thought bubble), so lenses, the coil of the
    hose and the scissors' rings stay open;
  - scene_street, 390 x 600: a calm 卡通城 street (shops, a fire station, a little clinic) with a
    pavement on the lower part where the owners stand and a plain sky where the bubbles float.

The look comes from city_kit.py (shared with 放哪裡？; this module only adds to it, never changes it):
flat fills, one hard cel shadow, a small highlight, thin outlines in a darker shade of each fill.
"""
import base64
import math
import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import city_kit as K  # noqa: E402
from city_kit import (GOLD, GREEN, RED, WHITE_OL, at, begin, blob, blush, clipped, cloud_d, comp, dk, ell, eye,  # noqa: E402
                      fit, flat, g, ground, happy_eye, heart_d, hi, hidot, hose, lg, lin, ln, lt, mix, n, open_mouth,
                      part, poly, rg, rr, save, shd, sparkle, spline, star_d, stroke, tube, calm, OUT, OL_THING, OL_SCENE)

ROOT = HERE.parents[1]

# ---------------------------------------------------------------- sizes
OL_PEOPLE = 3.6     # outline of the owners (units of the 200 picture): they show 90-190 px wide
PS = .72            # every grown-up is drawn at this scale (person units -> picture units)
GY = 192            # the ground line of every owner picture: feet / bottoms stand here
FOOT = 107          # the ground line in person units

PUPIL = "#2E1C14"
EYE_OL = "#3A2A30"
MOUTH = "#6A3030"


def skol(skin):
    """Outline of skin: a soft warm brown a little darker than the skin (like the mockup's #B97B5C)."""
    h, L, S = K._hls(skin)
    return K._hex(h - .01, L * .62, min(1, S * .62))


def owner_picture(fn, s=PS, foot=FOOT, shadow=(48, 8), **kw):
    """fn draws in person units, x = 0 in the middle, feet on y = `foot`; it is put in the picture
    at scale s with its feet on GY, over a soft ground shadow."""
    return ground(100, GY - 1, shadow[0], shadow[1], op=.2) + at(fn, 100, GY - foot * s, s, **kw)


# ================================================================ people (person units)
def legs(pants, shoe, top=50, bot=96, w=22, gap=16, boots=None, cuff=None):
    """Two legs and their shoes; boots: colour of tall boots over the shins; cuff: rolled-up hem."""
    o = ""
    for sx in (-1, 1):
        o += part(rr(sx * gap - w / 2, top, w, bot - top, 8), pants, s=(-3, -4))
        if cuff:
            o += part(rr(sx * gap - w / 2 - 1.5, bot - 22, w + 3, 9, 4), cuff, s=None)
        if boots:
            o += part(rr(sx * gap - w / 2 - 1, bot - 16, w + 2, 22, 6), boots, s=(-3, -3),
                      hl=hi(f"M{n(sx * gap - 5)},{n(bot - 11)} L{n(sx * gap - 5)},{n(bot - 2)}", 2.5, .6))
            o += part(ell(sx * (gap + 2), bot + 2, 16, 8.5), boots, s=(-2, -3))
        else:
            o += part(ell(sx * (gap + 2), bot + 2, 17, 9), shoe, s=(-2, -3),
                      hl=hi(f"M{n(sx * (gap + 2) - 10)},{n(bot - 1)} Q{n(sx * (gap + 2) - 4)},{n(bot - 5)} {n(sx * (gap + 2) + 2)},{n(bot - 5)}", 2.5, .55))
    return o


def torso_d(bottom=56, flare=2):
    return (f"M-34,-20 C-40,-20 -44,-14 -44,-6 L{n(-44 - flare)},{n(bottom - 4)} Q{n(-44 - flare)},{n(bottom)} {n(-40 - flare)},{n(bottom)} "
            f"L{n(40 + flare)},{n(bottom)} Q{n(44 + flare)},{n(bottom)} {n(44 + flare)},{n(bottom - 4)} L44,-6 C44,-14 40,-20 34,-20 Z")


def arms(col, skin, sko, ol=None, short=False, cuff=None, pattern=""):
    """Both arms hanging a little away from the body, hands open and empty (pattern: drawn inside
    short sleeves)."""
    o = ""
    for sx in (-1, 1):
        A = tube([(sx * 38, -10, 10), (sx * 50, 14, 9.5), (sx * 54, 34, 9.5)])
        if short:
            o += part(A, skin, s=(-2, -3), ol=sko)
            sl = tube([(sx * 37, -11, 11.5), (sx * 44, 4, 11)])
            o += comp(sl, col, pattern, s=(-2, -3), ol=ol) if pattern else part(sl, col, s=(-2, -3), ol=ol)
        else:
            o += part(A, col, s=(-2, -3), ol=ol)
            if cuff:
                o += part(tube([(sx * 52.5, 27, 10.5), (sx * 54, 33, 10.5)]), cuff, s=None, ol=lin(cuff))
        o += part(ell(sx * 55, 42, 9), skin, s=None, ol=sko)
    return o


def neck(skin, sko):
    return part(rr(-9, -32, 18, 16, 6), shd(skin), s=None, ol=sko)


def head(skin, sko, ears=True):
    o = ""
    if ears:
        for sx in (-1, 1):
            o += part(ell(sx * 39, -58, 7.5, 9.5), skin, s=None, ol=sko)
            o += ln(f"M{sx * 41},-63 Q{sx * 37},-58 {sx * 40},-53", sko, .55)
    o += part(ell(0, -64, 40, 38), skin, s=(-6, -7), ol=sko)
    return o


def face(mouth="smile", lx=.5, ly=1.2, brows=None, wrinkles=False, cheek=True, ey=-60):
    o = eye(-15, ey, 8, 10, lx, ly, pc=PUPIL, ol=EYE_OL) + eye(15, ey, 8, 10, lx, ly, pc=PUPIL, ol=EYE_OL)
    if cheek:
        o += blush(-26, -46, 6.5, 4, op=.55) + blush(26, -46, 6.5, 4, op=.55)
    if brows:
        o += ln("M-22,-76 Q-15,-80 -8,-77", brows, .9) + ln("M8,-77 Q15,-80 22,-76", brows, .9)
    if wrinkles:
        o += ln("M-27,-63 L-31,-65 M-27,-59 L-31,-58", "#B98A6E", .5) + ln("M27,-63 L31,-65 M27,-59 L31,-58", "#B98A6E", .5)
    if mouth == "smile":
        o += ln("M-10,-42 Q0,-34 10,-42", MOUTH, .9)
    elif mouth == "open":
        o += open_mouth(0, -44, 17, col="#8A2F2F", ol=MOUTH)
    elif mouth == "grin":
        o += open_mouth(0, -43, 14, col="#8A2F2F", ol=MOUTH)
    return o


def person(skin, top, pants, shoe="#3B3446", hair_back="", hair_front="", hat="", behind="", sleeve=None,
           short=False, cuff=None, top_ol=None, inner="", over="", length=56, flare=2, mouth="smile", brows=None,
           wrinkles=False, boots=None, leg_cuff=None, ears=True, hands_over="", sleeve_pattern=""):
    """A grown-up in person units (feet on y = FOOT). The hooks add clothes and hair:
    hair_back (behind the head), behind (behind the head, in front of the back hair: a comb),
    inner (clipped to the top: pockets, stripes), over (on the top: apron, bag), hair_front, hat."""
    sko = skol(skin)
    o = hair_back
    o += legs(pants, shoe, boots=boots, cuff=leg_cuff)
    o += comp(torso_d(length, flare), top, inner, s=(-8, -9), ol=top_ol)
    o += over
    o += arms(sleeve or top, skin, sko, ol=top_ol, short=short, cuff=cuff, pattern=sleeve_pattern)
    o += hands_over
    o += neck(skin, sko)
    o += behind
    o += head(skin, sko, ears)
    o += face(mouth, brows=brows, wrinkles=wrinkles)
    o += hair_front + hat
    return o


# ---------------------------------------------------------------- hair
def hair_short(col, part_x=-8):
    """Short hair: a cap over the top of the head with a soft fringe."""
    d = (f"M-43,-56 C-48,-92 -22,-110 2,-109 C30,-108 48,-90 43,-56 C41,-68 36,-76 28,-80 "
         f"C22,-74 12,-74 {part_x + 6},-82 C{part_x - 4},-74 -24,-74 -34,-72 C-38,-68 -41,-62 -43,-56Z")
    return part(d, col, s=(-3, -4), hl=hi("M-24,-98 C-14,-104 -2,-105 8,-104", 3.5, .45))


def hair_bun(col):
    o = part(ell(0, -108, 17, 16), col, s=(-3, -3), hl=hi("M-8,-117 C-4,-121 2,-121 6,-119", 3, .45))
    o += part(rr(-12, -97, 24, 7, 3.5), "#FF7FA3", s=None)
    return o


def hair_cap_f(col):
    """Hair combed back to a bun (the doctor): parted in the middle."""
    d = "M-43,-58 C-47,-92 -20,-106 0,-104 C20,-106 47,-92 43,-58 C38,-74 22,-86 0,-84 C-22,-86 -38,-74 -43,-58 Z"
    return part(d, col, s=(-3, -4), hl=hi("M-26,-94 C-18,-99 -10,-101 -4,-101", 3.5, .45)) + ln("M0,-104 L0,-86", lin(col), .6)


# ---------------------------------------------------------------- the owners
def firefighter():
    skin, coat = "#A86B45", "#F4B63A"
    band = "#E3E8F0"
    inner = part(rr(-60, 30, 120, 9, 0), band, s=None, ol="#B9C0CE")
    inner += part(rr(-60, 4, 120, 6, 0), band, s=None, ol="#B9C0CE")
    inner += ln("M0,-20 L0,56", lin(coat), .8)
    inner += part(rr(-4, -10, 8, 8, 2), "#5A4A3A", s=None) + part(rr(-4, 16, 8, 8, 2), "#5A4A3A", s=None)
    collar = part("M-24,-22 L-6,-22 L0,-8 L-18,-6 Z", coat, s=None) + part("M24,-22 L6,-22 L0,-8 L18,-6 Z", coat, s=None)
    o = person(skin, coat, "#3E4A6B", shoe="#2E2A3A", inner=inner, over=collar, boots="#2E2A3A",
               cuff=band, mouth="open", hat=g(helmet(), "translate(0 -100) scale(.78)"),
               hair_front=part("M-40,-74 C-40,-84 -30,-90 -22,-90 L-30,-74Z", "#2E2230", s=None)
               + part("M40,-74 C40,-84 30,-90 22,-90 L30,-74Z", "#2E2230", s=None))
    return o


def helmet(col="#F04A3E"):
    """The fire helmet of the mockup (its own units, about 150 x 90)."""
    brim = "M-66,6 C-40,15 30,15 62,4 C74,0 80,8 72,17 C46,31 -40,29 -68,17 C-76,13 -74,4 -66,6 Z"
    dome = "M-50,10 C-52,-28 -28,-58 4,-58 C36,-58 56,-34 56,8 C24,16 -18,16 -50,10 Z"
    o = part(brim, shd(col), s=(-3, -4))
    o += part(dome, col, s=(-9, -10), hl=hi("M-36,-18 C-32,-36 -18,-48 -4,-50", 6, .7))
    o += ln("M4,-58 C2,-40 2,-20 4,12", lin(col), .8)
    shield = "M-14,-38 L22,-38 L22,-12 C22,0 12,8 4,12 C-4,8 -14,0 -14,-12 Z"
    o += part(shield, GOLD, s=(-2, -3)) + part(star_d(9, 4, cx=4, cy=-17, round_=.15), "#FFFFFF", s=None, ol=lin(GOLD))
    return o


def doctor():
    skin, coat = "#F8D2B4", "#FFFFFF"
    scrub = "#7ED3E6"
    inner = part("M-15,-22 L0,8 L15,-22 Z", scrub, s=None, ol=lin(scrub))
    inner += ln("M-15,-21 L-3,10 L-3,74", WHITE_OL, .8) + ln("M15,-21 L3,10", WHITE_OL, .8)
    inner += part(rr(14, 20, 22, 18, 3), "#F3F0FA", s=None, ol=WHITE_OL)            # pocket with a plus
    inner += part("M23,23 h4 v4.5 h4.5 v4 h-4.5 v4.5 h-4 v-4.5 h-4.5 v-4 h4.5 Z", "#2EC4B6", s=None, ol=False)
    inner += part(rr(-34, 40, 18, 14, 3), "#F3F0FA", s=None, ol=WHITE_OL)
    inner += part(ell(-8, 26, 2.6), "#D6D0E6", s=None, ol=WHITE_OL, k=.5) + part(ell(-8, 46, 2.6), "#D6D0E6", s=None, ol=WHITE_OL, k=.5)
    return person(skin, coat, "#5A86D6", shoe="#3B3446", top_ol=WHITE_OL, inner=inner, length=74, flare=5,
                  hair_back=hair_bun("#2E2A3A"), hair_front=hair_cap_f("#2E2A3A"), mouth="smile")


def chef():
    skin, coat = "#E8B08A", "#FFFFFF"
    inner = ""
    for x in (-12, 12):
        for y in (-2, 14):
            inner += part(ell(x, y, 3), "#D9D3EA", s=None, ol=WHITE_OL, k=.5)
    apron = "M-30,22 L30,22 L36,72 Q36,76 32,76 L-32,76 Q-36,76 -36,72 Z"
    over = part(apron, "#FFFFFF", s=(-5, -6), ol=WHITE_OL, sh="#E1DCF0")
    over += part(rr(-34, 18, 68, 8, 4), "#FFFFFF", s=None, ol=WHITE_OL)          # apron band
    over += part(rr(-12, 40, 24, 16, 4), "#F3F0FA", s=None, ol=WHITE_OL)          # pocket
    scarf = "#F2463F"
    over += part("M-20,-24 C-10,-16 10,-16 20,-24 L22,-16 C10,-6 -10,-6 -22,-16 Z", scarf, s=None)
    over += part("M-6,-12 L6,-12 L10,4 L0,0 L-10,4 Z", scarf, s=(-2, -2))
    pants = "#3E3B4F"
    checks = ""
    for sx in (-1, 1):
        for i, y in enumerate((54, 66, 78, 90)):
            for j, x in enumerate((-8, 0)):
                if (i + j) % 2 == 0:
                    checks += flat(rr(sx * 16 + x - 3, y, 8, 6, 0), "#FFFFFF", op=.55)
    hair = (part("M-41,-70 C-42,-80 -36,-88 -30,-88 L-30,-66 Z", "#4A2E22", s=None)
            + part("M41,-70 C42,-80 36,-88 30,-88 L30,-66 Z", "#4A2E22", s=None))
    stache = part("M0,-47 C-4,-52 -14,-53 -18,-47 C-20,-43 -14,-42 -11,-44 C-7,-46 -3,-46 0,-44 C3,-46 7,-46 11,-44 "
                  "C14,-42 20,-43 18,-47 C14,-53 4,-52 0,-47Z", "#5A3424", s=None)
    o = person(skin, coat, pants, shoe="#2E2A3A", top_ol=WHITE_OL, inner=inner, over=over, hair_front=hair,
               mouth="grin", hat=toque())
    # the checks go on the legs below the apron (which stops at y = 76)
    return o + clipped_checks(checks, pants) + stache


def clipped_checks(checks, pants):
    """Black-and-white chef trousers: little white checks clipped to the two legs below the apron."""
    d = " ".join(rr(sx * 16 - 11, 76, 22, 20, 0) for sx in (-1, 1))
    return clipped(d, checks)


def toque():
    puff = ("M-32,-104 C-58,-106 -60,-130 -40,-136 C-38,-152 -14,-156 0,-146 C14,-156 38,-152 40,-136 "
            "C60,-130 58,-106 32,-104 Z")
    o = part(puff, "#FFFFFF", s=(-6, -7), ol=WHITE_OL, sh="#E1DCF0", hl=hi("M-42,-122 C-42,-130 -36,-136 -28,-138", 4, .9))
    o += ln("M-14,-108 C-16,-120 -14,-132 -10,-140 M14,-108 C16,-120 14,-132 10,-140", WHITE_OL, .6)
    o += part(rr(-36, -110, 72, 18, 6), "#FFFFFF", s=(-3, -3), ol=WHITE_OL, sh="#E1DCF0")
    return o


def police():
    skin, shirt, navy = "#F2C6A0", "#A8D4F7", "#2F3F73"
    inner = ""
    for sx in (-1, 1):
        inner += part(rr(sx * 22 - 10, -4, 20, 16, 3), shirt, s=None, ol=lin(shirt))                # breast pockets
        inner += part(rr(sx * 22 - 10, -6, 20, 6, 2), lt(shirt, .2), s=None, ol=lin(shirt))
    inner += part("M-30,-4 L-14,-4 L-14,12 C-14,18 -22,22 -22,22 C-22,22 -30,18 -30,12Z", GOLD, s=None)  # badge
    inner += part(star_d(4.5, 2, cx=-22, cy=6, round_=.15), "#FFFFFF", s=None, ol=False)
    inner += part(rr(-48, 44, 96, 10, 0), "#2A2A3A", s=None) + part(rr(-6, 43, 12, 12, 2), GOLD, s=None)
    tie = part("M-6,-22 L6,-22 L4,-14 L8,22 L0,30 L-8,22 L-4,-14 Z", navy, s=(-2, -2))
    collar = part("M-20,-24 L-2,-22 L-8,-8 Z", lt(shirt, .3), s=None) + part("M20,-24 L2,-22 L8,-8 Z", lt(shirt, .3), s=None)
    eps = "".join(part(rr(sx * 36 - 9, -20, 18, 7, 3), navy, s=None) for sx in (-1, 1))
    bob = "M-45,-80 C-52,-52 -50,-36 -42,-30 C-34,-26 -30,-34 -30,-40 L30,-40 C30,-34 34,-26 42,-30 C50,-36 52,-52 45,-80 Z"
    fringe = "M-38,-78 C-30,-86 -10,-90 4,-88 C20,-88 34,-84 40,-76 C30,-80 12,-76 4,-72 C-6,-78 -24,-76 -38,-70Z"
    o = person(skin, shirt, navy, shoe="#22222E", short=True, inner=inner, over=tie + collar + eps,
               hair_back=part(bob, "#2A2433", s=(-3, -4)), hair_front=part(fringe, "#2A2433", s=None),
               hat=police_cap(navy), mouth="smile")
    return o


def police_cap(navy):
    crown = "M-46,-90 C-56,-110 -34,-124 0,-124 C34,-124 56,-110 46,-90 Z"
    o = part(crown, navy, s=(-5, -5), hl=hi("M-34,-114 C-24,-120 -12,-121 -2,-121", 3.5, .4))
    o += part(rr(-40, -96, 80, 13, 4), dk(navy, .3), s=None)
    o += part(rr(-40, -92, 80, 3.5, 1.5), GOLD, s=None, ol=False)
    o += part("M-40,-84 C-28,-72 28,-72 40,-84 C30,-89 -30,-89 -40,-84Z", "#1E2233", s=None, ol="#11131D")
    o += part("M-10,-118 L10,-118 L12,-104 C10,-98 4,-95 0,-94 C-4,-95 -10,-98 -12,-104 Z", GOLD, s=(-2, -2))
    o += part(star_d(5, 2.2, cx=0, cy=-106, round_=.15), "#FFFFFF", s=None, ol=False)
    return o


def mail_carrier():
    skin, green, dark = "#D9A07A", "#3DAA62", "#2C6E4A"
    bag, strap = "#E3B04B", "#C98A2E"
    inner = ln("M0,-20 L0,56", lin(green), .8)
    inner += part(rr(10, -4, 20, 16, 3), lt(green, .15), s=None, ol=lin(green))
    inner += "".join(part(ell(-4, y, 2.4), "#F1EEE4", s=None, ol=lin(green), k=.5) for y in (-6, 12, 30))
    over = hose("M30,-20 C10,0 -14,18 -30,30", strap, 7)
    bagd = "M-50,24 L-6,24 Q-4,24 -4,28 L-4,56 Q-4,62 -10,62 L-46,62 Q-52,62 -52,56 L-52,28 Q-52,24 -50,24 Z"
    over += part(bagd, bag, s=(-4, -5), hl=hi("M-46,32 L-46,52", 2.5, .5))
    over += part("M-52,26 Q-52,22 -48,22 L-8,22 Q-4,22 -4,26 L-4,40 Q-4,44 -10,44 L-46,44 Q-52,44 -52,40 Z", lt(bag, .12), s=(-2, -3))
    over += part(rr(-32, 38, 10, 10, 2), "#8E95A6", s=None, ol=lin("#8E95A6"))
    collar = part("M-22,-24 L-4,-22 L-10,-6 Z", lt(green, .2), s=None) + part("M22,-24 L4,-22 L10,-6 Z", lt(green, .2), s=None)
    hair = (part("M-41,-72 C-42,-82 -36,-88 -28,-90 L-30,-68 Z", "#2A2433", s=None)
            + part("M41,-72 C42,-82 36,-88 28,-90 L30,-68 Z", "#2A2433", s=None))
    return person(skin, green, dark, shoe="#3B3446", inner=inner, over=collar + over, hair_front=hair,
                  hat=mail_cap(green), mouth="open", cuff=lt(green, .15))


def mail_cap(col):
    crown = "M-42,-84 C-46,-112 -24,-122 0,-122 C24,-122 46,-112 42,-84 Z"
    o = part(crown, col, s=(-5, -6), hl=hi("M-28,-110 C-20,-116 -10,-118 -2,-118", 3.5, .45))
    o += ln("M0,-122 L0,-86", lin(col), .6)
    o += part(rr(-42, -90, 84, 9, 3), "#FFD24A", s=None)
    o += part("M-40,-82 C-26,-70 26,-70 40,-82 C30,-88 -30,-88 -40,-82Z", dk(col, .25), s=None)
    o += part(ell(0, -122, 4.5, 3), dk(col, .2), s=None)
    return o


def farmer():
    skin, shirt = "#C98B5E", "#F27B8A"
    flowers = ""
    for x, y in ((-30, -8), (-6, 6), (20, -6), (32, 22), (-24, 30), (6, 40), (-38, 50), (28, 50), (-10, -14)):
        flowers += flat(ell(x, y, 3.2), "#FFFFFF", op=.85) + flat(ell(x, y, 1.3), "#FFD43B")
    towel = "M-26,-24 C-14,-16 14,-16 26,-24 L30,-14 C14,-4 -14,-4 -30,-14 Z"
    over = part(towel, "#FFFFFF", s=None, ol=WHITE_OL)
    over += part(rr(-28, -14, 13, 34, 4), "#FFFFFF", s=(-2, -3), ol=WHITE_OL, sh="#E1DCF0")
    over += part(rr(-28, 12, 13, 5, 0), "#6FB3F2", s=None, ol=False)
    over += part(rr(-12, 44, 24, 6, 0), "#7A5638", s=None)
    hair = "M-42,-72 C-46,-60 -46,-44 -40,-36 L-34,-60 Z M42,-72 C46,-60 46,-44 40,-36 L34,-60 Z"
    o = person(skin, shirt, "#B58A5A", inner=flowers, over=over, cuff=lt(shirt, .25), boots="#3E8E5E",
               leg_cuff=lt("#B58A5A", .2), hair_back=part(hair, "#2A2433", s=None), hat=bamboo_hat(), mouth="open")
    return o


def bamboo_hat():
    """斗笠: a wide shallow cone of woven bamboo, with a chin strap."""
    col = "#E9C46A"
    d = "M-78,-84 L-6,-130 C-2,-133 2,-133 6,-130 L78,-84 C52,-72 -52,-72 -78,-84 Z"
    weave = ""
    for t in (-.8, -.55, -.3, -.08, .14, .36, .6, .84):
        x = 78 * t
        weave += ln(f"M0,-130 L{n(x)},{n(-78 + 4 * t * t)}", "#C99A3A", .5)
    weave += ln("M-56,-96 C-30,-90 30,-90 56,-96 M-32,-112 C-16,-109 16,-109 32,-112", "#C99A3A", .5)
    o = ln("M-36,-78 C-36,-50 -26,-38 -14,-36 M36,-78 C36,-50 26,-38 14,-36", "#9A6A3A", .6)
    o += comp(d, col, weave, s=(-5, -6), hl=hi("M-50,-92 L-12,-118", 3.5, .55))
    o += part(ell(0, -131, 5, 3.5), "#C99A3A", s=None)
    return o


def grandpa():
    skin, card = "#F6D3B8", "#C9844E"
    shirt = "#BFE3F7"
    inner = part("M-18,-22 L0,16 L18,-22 Z", shirt, s=None, ol=lin(shirt))
    inner += part("M-16,-22 L-2,-20 L-8,-10 Z", lt(shirt, .4), s=None, ol=lin(shirt)) + part("M16,-22 L2,-20 L8,-10 Z", lt(shirt, .4), s=None, ol=lin(shirt))
    inner += ln("M-18,-21 L-1,18 L-1,56 M18,-21 L1,18", lin(card), .8)
    inner += "".join(part(ell(-6, y, 2.6), "#F3E1C8", s=None, ol=lin(card), k=.5) for y in (24, 36, 48))
    for sx in (-1, 1):
        inner += part(rr(sx * 26 - 10, 30, 20, 16, 3), shd(card), s=None, ol=lin(card))
    inner += part(rr(-60, 50, 120, 6, 0), shd(card), s=None, ol=False)
    grey = "#D9D6E0"
    capd = ("M-43,-54 C-52,-66 -48,-80 -42,-86 C-44,-98 -30,-108 -18,-104 C-10,-114 8,-114 14,-106 "
            "C28,-110 42,-100 40,-88 C50,-80 52,-66 43,-54 C41,-66 38,-76 32,-82 "
            "C22,-90 10,-92 -2,-92 C-14,-92 -26,-88 -32,-82 C-38,-76 -41,-66 -43,-54Z")
    tufts = part(capd, grey, s=(-3, -4), sh="#BDB8C9", ol="#9C97AE", hl=hi("M-22,-100 C-12,-105 0,-106 10,-105", 3.5, .8))
    tufts += ln("M-20,-100 C-10,-96 0,-96 8,-100 M-6,-106 C2,-100 12,-100 22,-104", "#AFA9C0", .6)
    stache = part("M0,-46 C-4,-51 -14,-52 -17,-46 C-18,-42 -12,-41 -9,-43 C-6,-45 -2,-45 0,-43 C2,-45 6,-45 9,-43 "
                  "C12,-41 18,-42 17,-46 C14,-52 4,-51 0,-46Z", grey, s=None, ol="#9C97AE")
    o = person(skin, card, "#8C7B6B", shoe="#6E4A32", inner=inner, cuff=shd(card), hair_front=tufts,
               brows="#A9A4B8", mouth="none")
    o += ln("M-8,-38 Q0,-33 8,-38", MOUTH, .8) + stache
    return o


def sister():
    """A school-age girl: her own shorter body (feet on y = 92), the same head."""
    skin, sko = "#F7CFAE", skol("#F7CFAE")
    hair, ribbon = "#2E2433", "#F2463F"
    shirt, skirt = "#FFFFFF", "#3E5BA8"
    o = ""
    # pigtails
    for sx in (-1, 1):
        o += part(blob([(sx * 40, -60), (sx * 58, -54), (sx * 64, -34), (sx * 56, -14), (sx * 46, -24), (sx * 44, -44)]), hair, s=(-3, -3))
    # legs, socks and shoes
    for sx in (-1, 1):
        o += part(rr(sx * 13 - 8, 40, 16, 44, 7), skin, s=(-2, -3), ol=sko)
        o += part(rr(sx * 13 - 8.5, 64, 17, 20, 5), "#FFFFFF", s=None, ol=WHITE_OL)
        o += part(ell(sx * 15, 86, 14, 7.5), ribbon, s=(-2, -2), hl=hi(f"M{sx * 15 - 8},{83} Q{sx * 15 - 3},{80} {sx * 15 + 2},{80}", 2.2, .6))
    # skirt (pleats)
    sk = "M-30,22 L30,22 L42,52 Q42,56 38,56 L-38,56 Q-42,56 -42,52 Z"
    pleats = ln("M-14,24 L-20,56 M0,24 L0,56 M14,24 L20,56", lin(skirt), .7)
    o += comp(sk, skirt, pleats, s=(-6, -6))
    # shirt
    body = "M-26,-14 C-32,-14 -34,-10 -34,-4 L-32,26 L32,26 L34,-4 C34,-10 32,-14 26,-14 Z"
    o += part(body, shirt, s=(-6, -7), ol=WHITE_OL, sh="#E1DCF0")
    for sx in (-1, 1):
        A = tube([(sx * 30, -8, 8), (sx * 40, 10, 7.5), (sx * 43, 26, 7.5)])
        o += part(A, skin, s=(-2, -3), ol=sko)
        o += part(tube([(sx * 29, -9, 9.5), (sx * 35, 2, 9)]), shirt, s=(-2, -2), ol=WHITE_OL, sh="#E1DCF0")
        o += part(ell(sx * 44, 32, 7.5), skin, s=None, ol=sko)
    # sailor collar and bow
    o += part("M-24,-16 L-2,-14 L0,4 L-22,-4 Z", skirt, s=None) + part("M24,-16 L2,-14 L0,4 L22,-4 Z", skirt, s=None)
    o += ln("M-20,-11 L-4,-1 M20,-11 L4,-1", "#FFFFFF", .5)
    o += part("M0,2 L-14,-4 L-14,10 Z", ribbon, s=None) + part("M0,2 L14,-4 L14,10 Z", ribbon, s=None) + part(ell(0, 2, 4), ribbon, s=None)
    o += part(rr(-7, -22, 14, 12, 5), shd(skin), s=None, ol=sko)
    # head
    for sx in (-1, 1):
        o += part(ell(sx * 37, -44, 7, 9), skin, s=None, ol=sko)
    o += part(ell(0, -50, 38, 36), skin, s=(-6, -7), ol=sko)
    o += eye(-14, -46, 8, 10, .5, 1.2, pc=PUPIL, ol=EYE_OL) + eye(14, -46, 8, 10, .5, 1.2, pc=PUPIL, ol=EYE_OL)
    o += blush(-25, -33, 6.5, 4, op=.55) + blush(25, -33, 6.5, 4, op=.55)
    o += open_mouth(0, -30, 14, col="#8A2F2F", ol=MOUTH)
    cap = ("M-41,-42 C-46,-78 -20,-92 2,-90 C26,-90 46,-76 41,-42 C40,-52 36,-60 30,-64 C22,-58 10,-60 4,-66 "
           "C-4,-58 -18,-58 -28,-62 C-34,-56 -38,-50 -41,-42Z")
    o += part(cap, hair, s=(-3, -4), hl=hi("M-22,-82 C-12,-87 -2,-88 8,-87", 3.5, .45))
    for sx in (-1, 1):
        o += part(f"M{sx * 38},-66 L{sx * 52},-78 L{sx * 54},-58 Z", ribbon, s=None)
        o += part(f"M{sx * 38},-66 L{sx * 30},-82 L{sx * 50},-80 Z", ribbon, s=None)
        o += part(ell(sx * 40, -68, 4.5), ribbon, s=None)
    return o


def hairdresser():
    skin, apron = "#B9805A", "#4A4F6A"
    stripes = "".join(flat(rr(x, -30, 6, 100, 0), "#F2463F", op=.9) for x in (-61, -49, -37, -25, -13, -1, 11, 23, 35, 47, 59))
    a = "M-26,-14 L26,-14 L28,10 L36,14 L38,70 Q38,74 34,74 L-34,74 Q-38,74 -38,70 L-36,14 L-28,10 Z"
    over = ln("M-24,-14 C-24,-22 -20,-26 -16,-30 M24,-14 C24,-22 20,-26 16,-30", apron, 1.6)
    over += part(a, apron, s=(-5, -6), hl=hi("M-30,20 L-30,60", 3, .25))
    for sx in (-1, 1):
        over += part(rr(sx * 18 - 13, 34, 26, 22, 4), lt(apron, .12), s=None, ol=lin(apron))
    over += ln("M0,34 L0,56", lin(apron), .7)
    comb = combd(46, -86, -40, "#FF7FA3")
    hair = ("M-43,-56 C-48,-90 -26,-108 -2,-108 C10,-122 40,-118 46,-98 C50,-86 46,-70 43,-56 C40,-68 34,-78 22,-84 "
            "C10,-78 -14,-80 -26,-86 C-34,-78 -40,-68 -43,-56Z")
    hfront = part(hair, "#3A2626", s=(-3, -4), hl=hi("M-18,-100 C-6,-106 6,-110 18,-110", 4, .45))
    return person(skin, "#FFFFFF", "#3B3446", shoe="#2E2A3A", sleeve="#FFFFFF", top_ol=WHITE_OL, inner=stripes,
                  short=True, over=over, behind=comb, hair_front=hfront, mouth="open", sleeve_pattern=stripes)


def combd(cx, cy, rot, col="#2EC4B6"):
    """A comb (behind the ear), centred on (cx, cy), turned rot degrees: a bar and seven fat teeth."""
    back = rr(-26, -8, 52, 11, 5)
    teeth = "".join(rr(-23 + i * 7.2, 0, 4.4, 15, 2.2) for i in range(7))
    o = part(teeth, col, s=None, ol=lin(col), k=.7) + part(back, col, s=None, ol=lin(col), hl=hi("M-20,-4 L18,-4", 2.2, .7))
    return g(o, f"translate({cx} {cy}) rotate({rot})")


def painter():
    skin, smock = "#8A5A3C", "#FFF3D6"
    blots = ""
    for x, y, r, c in ((-28, 4, 6, "#F2463F"), (22, 14, 5, "#3D8BF2"), (-10, 34, 5.5, "#FFC233"), (30, 46, 6, "#4FC461"),
                       (-34, 58, 4.5, "#9B5DE5"), (8, 62, 4, "#FF7FA3"), (34, -6, 4, "#FF8C2B"), (-18, 18, 3, "#3D8BF2")):
        blots += flat(blob([(x + r * math.cos(a) * (1 + .25 * math.sin(3 * a)), y + r * math.sin(a) * (1 + .25 * math.sin(3 * a)))
                            for a in [i * math.pi / 4 for i in range(8)]]), c)
    bow = (part("M0,-14 L-20,-24 L-18,-2 Z", "#3D8BF2", s=None) + part("M0,-14 L20,-24 L18,-2 Z", "#3D8BF2", s=None)
           + part(ell(0, -14, 5), "#3D8BF2", s=None))
    curls = ""
    for a in range(-200, 21, 22):
        r = math.radians(a)
        curls += part(ell(46 * math.cos(r), -64 + 40 * math.sin(r), 13, 13), "#2E2230", s=None, ol=lin("#4A3A40"))
    hair_back = curls
    pal = palette_d()
    hands = g(part(pal[0], "#E3B074", s=(-3, -4), fr=True, hl=hi("M-16,-8 C-10,-14 0,-16 10,-14", 3, .6)) + pal[1],
              "translate(-66 34) rotate(-18)")
    hands += part(ell(-55, 42, 9), skin, s=None, ol=skol(skin))
    o = person(skin, smock, "#3E5BA8", shoe="#E8434F", top_ol=lin("#E8C98F"), inner=blots, over=bow, length=72, flare=6,
               hair_back=hair_back, hands_over=hands, hat=beret(), mouth="open")
    return o


def palette_d():
    d = ("M-22,-12 C-14,-22 14,-24 24,-12 C32,-2 28,14 14,16 C8,17 6,10 0,10 C-6,10 -6,18 -14,18 C-26,18 -30,-2 -22,-12 Z "
         + ell(-12, 8, 4.5))
    dots = "".join(part(ell(x, y, 4.2), c, s=None, k=.6) for x, y, c in ((-10, -8, "#F2463F"), (2, -12, "#FFC233"), (14, -8, "#3D8BF2"), (18, 4, "#4FC461")))
    return d, dots


def beret():
    col = "#E8434F"
    d = "M-44,-86 C-50,-104 -24,-118 6,-116 C34,-114 52,-104 46,-90 C40,-82 20,-84 0,-84 C-20,-84 -40,-80 -44,-86 Z"
    o = part(d, col, s=(-5, -6), hl=hi("M-30,-104 C-20,-110 -8,-112 4,-112", 3.5, .5))
    o += part("M4,-116 C2,-124 8,-128 12,-124 C14,-120 10,-116 8,-115 Z", col, s=None)
    return o


# ---------------------------------------------------------------- the baby and the animals (their own units)
def baby():
    """A baby sitting on the ground (bottom on y = 60), arms open."""
    skin, sko = "#F2C29C", skol("#F2C29C")
    suit = "#FFE27A"
    o = ""
    # legs forward: the soles face us
    for sx in (-1, 1):
        o += part(tube([(sx * 16, 30, 13), (sx * 30, 46, 13), (sx * 34, 52, 13)]), suit, s=(-2, -3))
        o += part(ell(sx * 40, 50, 10, 13), skin, s=(-2, -2), ol=sko)
        o += flat(ell(sx * 40, 53, 5.5, 7), lt(skin, .35))
    body = "M-30,-16 C-40,-14 -44,10 -42,30 C-40,48 -20,56 0,56 C20,56 40,48 42,30 C44,10 40,-14 30,-16 Z"
    o += part(body, suit, s=(-7, -8), hl=hi("M-32,4 C-32,-6 -28,-12 -22,-14", 3.5, .5))
    o += ln("M0,4 L0,52", lin(suit), .7)
    o += "".join(part(ell(0, y, 2.4), "#FFFFFF", s=None, ol=lin(suit), k=.5) for y in (16, 30, 44))
    # bib
    bib = "M-20,-16 C-22,0 -12,12 0,12 C12,12 22,0 20,-16 Z"
    o += part(bib, "#FFFFFF", s=(-2, -3), ol=WHITE_OL, sh="#E1DCF0")
    o += part(heart_d(.55, 0, 0), "#FF7FA3", s=None, ol=lin("#FF7FA3"), k=.6)
    # arms up and open
    for sx in (-1, 1):
        o += part(tube([(sx * 30, -6, 9.5), (sx * 46, -14, 9), (sx * 54, -28, 9)]), suit, s=(-2, -3))
        o += part(ell(sx * 56, -34, 10, 10), skin, s=None, ol=sko)
    # head (big)
    for sx in (-1, 1):
        o += part(ell(sx * 46, -58, 8, 10), skin, s=None, ol=sko)
    o += part(ell(0, -62, 47, 44), skin, s=(-7, -8), ol=sko)
    curl = "M-12,-102 C-14,-114 -2,-124 8,-118 C14,-114 12,-104 4,-104 C0,-104 -2,-110 2,-112 C-4,-112 -6,-104 -4,-100 Z"
    o += part(curl, "#8A5A3A", s=None)
    o += eye(-17, -58, 9.5, 11.5, .5, 1.5, pc=PUPIL, ol=EYE_OL) + eye(17, -58, 9.5, 11.5, .5, 1.5, pc=PUPIL, ol=EYE_OL)
    o += blush(-30, -42, 8, 5, op=.6) + blush(30, -42, 8, 5, op=.6)
    o += open_mouth(0, -38, 13, col="#8A2F2F", ol=MOUTH)
    return o


def dog():
    """A puppy sitting, looking at us (the mockup's dog, without the bone)."""
    fur, ear, ol = "#F8E6C8", "#B9773F", "#B98A56"
    o = part(tube([(36, 60, 9), (62, 46, 8), (74, 20, 7)]), fur, s=(-2, -3), ol=ol)
    body = "M-34,0 C-50,30 -54,66 -44,84 L44,84 C54,66 50,30 34,0 Z"
    o += part(body, fur, s=(-7, -8), ol=ol)
    o += part(ell(0, 52, 20, 26), "#FFFFFF", s=None, ol=False, op=.7)
    for sx in (-1, 1):
        o += part(tube([(sx * 14, 30, 9), (sx * 15, 62, 9), (sx * 16, 80, 10)]), fur, s=(-2, -3), ol=ol)
        o += ln(f"M{sx * 16 - 4},86 L{sx * 16 - 4},80 M{sx * 16 + 3},86 L{sx * 16 + 3},80", ol, .55)
    o += part(rr(-30, -6, 60, 12, 6), RED, s=None) + part(ell(0, 10, 7), GOLD, s=None, hl=hidot(-2, 8, 2))
    for sx in (-1, 1):
        o += part(f"M{sx * 34},-74 C{sx * 62},-76 {sx * 70},-50 {sx * 64},-22 C{sx * 60},-8 {sx * 48},-12 {sx * 44},-26 "
                  f"C{sx * 40},-40 {sx * 36},-54 {sx * 34},-74Z", ear, s=(-3, -4))
    head_d = ell(0, -42, 50, 44)
    o += comp(head_d, fur, part(ell(22, -56, 18, 16), "#E8C08E", s=None, ol=False), s=(-8, -8), ol=ol,
              hl=hi("M-30,-70 C-20,-80 -6,-84 8,-83", 5, .6))
    o += part(ell(0, -20, 26, 18), "#FFFFFF", s=None, ol=ol)
    o += eye(-20, -50, 9, 10.5, .5, 1.5, pc=PUPIL, ol="#5A3424") + eye(20, -50, 9, 10.5, .5, 1.5, pc=PUPIL, ol="#5A3424")
    o += blush(-36, -28, 8, 5) + blush(36, -28, 8, 5)
    o += part("M-9,-30 C-9,-36 9,-36 9,-30 C9,-24 3,-21 0,-21 C-3,-21 -9,-24 -9,-30Z", "#3A2418", s=None, hl=hidot(-3, -31, 2))
    o += ln("M0,-21 L0,-15", "#5A3424", .7)
    tongue = "M-7,-12 C-7,-4 -4,0 0,0 C4,0 7,-4 7,-12 Z"
    o += part(tongue, "#FF8A93", s=None, ol="#C24F5A", k=.7) + ln("M0,-11 L0,-5", "#C24F5A", .5)
    o += ln("M-14,-16 Q-7,-10 0,-15 Q7,-10 14,-16", "#5A3424", .8)
    return o


def rabbit():
    """A white rabbit sitting up, long ears."""
    fur, sh, ol = "#FBF8FF", "#DCD3EA", "#9A90B4"
    pink = "#FFB3C4"
    o = ""
    for sx in (-1, 1):
        ear = f"M{sx * 8},-78 C{sx * 0},-110 {sx * 4},-138 {sx * 22},-142 C{sx * 40},-142 {sx * 40},-110 {sx * 30},-76 Z"
        o += part(ear, fur, s=(-3, -4), sh=sh, ol=ol)
        o += part(f"M{sx * 13},-84 C{sx * 8},-110 {sx * 12},-128 {sx * 22},-131 C{sx * 32},-129 {sx * 32},-108 {sx * 25},-84 Z", pink, s=None, ol=False)
    body = "M-34,-14 C-52,10 -54,52 -42,72 C-34,84 34,84 42,72 C54,52 52,10 34,-14 Z"
    o += part(body, fur, s=(-7, -8), sh=sh, ol=ol)
    o += part(ell(0, 40, 22, 28), "#FFFFFF", s=None, ol=False)
    for sx in (-1, 1):
        o += part(ell(sx * 24, 76, 18, 10), fur, s=(-2, -3), sh=sh, ol=ol)
        o += flat(ell(sx * 24, 78, 8, 4.5), pink, op=.8)
        o += part(ell(sx * 16, 14, 9, 11), fur, s=(-2, -2), sh=sh, ol=ol)
    head_d = ell(0, -44, 46, 40)
    o += part(head_d, fur, s=(-7, -8), sh=sh, ol=ol, hl=hi("M-28,-70 C-18,-78 -6,-82 6,-81", 5, .9))
    o += eye(-18, -48, 9, 10.5, .5, 1.5, pc=PUPIL, ol="#5A4A6A") + eye(18, -48, 9, 10.5, .5, 1.5, pc=PUPIL, ol="#5A4A6A")
    o += blush(-30, -30, 8, 5, op=.6) + blush(30, -30, 8, 5, op=.6)
    o += part("M-6,-32 C-6,-36 6,-36 6,-32 C6,-28 2,-26 0,-26 C-2,-26 -6,-28 -6,-32Z", "#FF7FA3", s=None, ol="#D9566F", k=.6)
    o += ln("M0,-26 L0,-21 M-9,-18 Q-4,-14 0,-20 Q4,-14 9,-18", "#7A4A5A", .8)
    o += part(rr(-4.5, -20, 9, 7, 1.5), "#FFFFFF", s=None, ol="#9A90B4", k=.5)
    return o


def cat():
    """An orange tabby cat sitting, tail curled round."""
    fur, ol = "#FFB25B", lin("#FFB25B")
    stripe = shd(shd(fur))
    o = part(tube([(30, 78, 9), (56, 74, 8.5), (70, 54, 8), (66, 34, 7.5)]), fur, s=(-2, -3), ol=ol)
    o += clipped(tube([(30, 78, 9), (56, 74, 8.5), (70, 54, 8), (66, 34, 7.5)]),
                 flat(rr(52, 60, 30, 6, 0), stripe) + flat(rr(56, 44, 30, 6, 0), stripe))
    body = "M-30,-10 C-48,14 -52,56 -40,78 C-32,88 32,88 40,78 C52,56 48,14 30,-10 Z"
    inner = flat(ell(0, 44, 22, 32), "#FFF1DE")
    inner += "".join(flat(f"M{sx * 52},{y} Q{sx * 38},{y + 4} {sx * 32},{y + 10} Q{sx * 40},{y + 10} {sx * 52},{y + 8}Z", stripe)
                     for sx in (-1, 1) for y in (20, 38, 56))
    o += comp(body, fur, inner, s=(-7, -8), ol=ol)
    for sx in (-1, 1):
        o += part(tube([(sx * 14, 30, 8.5), (sx * 15, 60, 8.5), (sx * 16, 78, 9.5)]), fur, s=(-2, -3), ol=ol)
        o += part(ell(sx * 16, 82, 11, 7), "#FFF1DE", s=None, ol=ol)
    for sx in (-1, 1):
        ear = f"M{sx * 18},-74 L{sx * 42},-96 L{sx * 46},-52 Z"
        o += part(ear, fur, s=(-2, -3), ol=ol)
        o += part(f"M{sx * 24},-70 L{sx * 40},-86 L{sx * 42},-58 Z", "#FFB3C4", s=None, ol=False)
    head_d = ell(0, -42, 50, 42)
    stripes = "".join(flat(f"M{x - 3},-84 L{x + 3},-84 L{x + 1.5},-68 L{x - 1.5},-68Z", stripe) for x in (-11, 0, 11))
    stripes += "".join(flat(f"M{sx * 52},{y} Q{sx * 42},{y + 2} {sx * 38},{y + 6} Q{sx * 44},{y + 7} {sx * 52},{y + 6}Z", stripe)
                       for sx in (-1, 1) for y in (-50, -38))
    stripes += flat(ell(0, -22, 24, 16), "#FFF1DE")
    o += comp(head_d, fur, stripes, s=(-8, -8), ol=ol, hl=hi("M-32,-66 C-22,-76 -10,-80 2,-80", 5, .55))
    o += eye(-20, -46, 10, 11.5, .5, 1.5, pc=PUPIL, ol="#6E3B22") + eye(20, -46, 10, 11.5, .5, 1.5, pc=PUPIL, ol="#6E3B22")
    o += blush(-34, -26, 8, 5, op=.55) + blush(34, -26, 8, 5, op=.55)
    o += part("M-5,-28 L5,-28 L0,-22 Z", "#FF7FA3", s=None, ol="#D9566F", k=.6)
    o += ln("M0,-22 L0,-18 M-9,-15 Q-4,-11 0,-17 Q4,-11 9,-15", "#6E3B22", .8)
    o += ln("M-26,-24 L-48,-28 M-26,-18 L-48,-16 M26,-24 L48,-28 M26,-18 L48,-16", "#B5733A", .55)
    return o


# ---------------------------------------------------------------- registry of owners
OWNERS = {
    "firefighter": lambda: owner_picture(firefighter),
    "doctor": lambda: owner_picture(doctor),
    "chef": lambda: owner_picture(chef),
    "police": lambda: owner_picture(police),
    "mail_carrier": lambda: owner_picture(mail_carrier),
    "farmer": lambda: owner_picture(farmer, shadow=(52, 8)),
    "grandpa": lambda: owner_picture(grandpa),
    "sister": lambda: owner_picture(sister, foot=92, shadow=(42, 7)),
    "hairdresser": lambda: owner_picture(hairdresser),
    "painter": lambda: owner_picture(painter),
    "baby": lambda: owner_picture(baby, s=.86, foot=60, shadow=(54, 8)),
    "dog": lambda: owner_picture(dog, s=.82, foot=88, shadow=(52, 8)),
    "rabbit": lambda: owner_picture(rabbit, s=.78, foot=86, shadow=(46, 8)),
    "cat": lambda: owner_picture(cat, s=.82, foot=88, shadow=(52, 8)),
}


# ================================================================ THINGS (each in its own units, fitted to 85 % of 200 x 200)
THINGS = {}
STEEL, STEEL_D = "#C9CED9", "#8E95A6"


# The ids 放哪裡？ also uses (sortThings in content.dart): one file serves both games, and city_sort.py
# (the 放哪裡？ helper) writes it. These are written only when named on the command line.
SHARED = {"fish", "carrot"}


def thing(name, box, rot=0, k=1.0, dx=0.0, dy=0.0):
    """Register a thing drawing: `box` = (x0, y0, x1, y1) is how far it reaches in its own units.
    A turned drawing (rot) is fitted by its box before turning, so k (scale) and dx, dy (shift, in
    picture units) bring what is seen back to 85 % of the picture and to its middle; they were
    measured from the rendered pictures."""
    def reg(fn):
        THINGS[name] = lambda: fit(fn, box, rot=rot, fill=K.FILL * k, cx=100 + dx, cy=100 + dy)
        return fn
    return reg


@thing("hose", (-74, -64, 78, 52), k=1.062, dx=-4.2, dy=-0.5)
def hose_coil(col="#F04A3E"):
    """A coiled fire hose with a nozzle (the mockup's)."""
    o = ""
    for y in (22, 8, -6):
        o += hose(ell(-4, y, 52, 22), col, 12)
        o += hi(f"M-30,{y + 18} C-14,{y + 22} 8,{y + 22} 24,{y + 19}", 2.6, .45)
    o += hi("M-44,-14 C-30,-26 -10,-29 10,-28", 3, .7)
    o += hose("M48,-6 C60,-14 62,-32 54,-40", col, 12)
    o += part(rr(42, -16, 14, 14, 3), GOLD, s=None)
    noz = "M44,-42 L60,-54 C64,-57 70,-52 67,-48 L56,-34 Z"
    o += part(noz, STEEL, s=(-2, -2.5), hl=hi("M50,-42 L60,-50", 2, .8))
    o += part("M59,-52 L70,-62 C72,-64 76,-60 74,-58 L66,-46 Z", GOLD, s=None)
    return o


@thing("stethoscope", (-60, -72, 64, 70), k=1.012, dx=-12.1, dy=-2.0)
def stethoscope(col="#3D7FE0"):
    o = hose("M0,-6 C0,24 -34,36 -26,54 C-18,70 30,66 34,40", col, 8)
    o += hose("M-24,-60 C-30,-30 -16,-12 0,-6 M24,-60 C30,-30 16,-12 0,-6", "#B9C0CE", 5)
    o += part(ell(-24, -62, 6, 5), "#4B4560", s=None) + part(ell(24, -62, 6, 5), "#4B4560", s=None)
    o += part(ell(0, -6, 6), "#B9C0CE", s=None)
    o += part(ell(38, 30, 19), STEEL, s=(-3, -4), hl=hi("M26,24 A12,12 0 0 1 34,16", 3, .9))
    o += part(ell(38, 30, 11), STEEL_D, s=None)
    return o


@thing("spatula", (-40, -118, 40, 96), rot=38, k=1.104, dx=-8.8, dy=6.6)
def spatula():
    """A Chinese wok spatula 鍋鏟: a broad steel scoop, a steel shaft, a wooden handle."""
    o = part(tube([(0, -44, 4.5), (0, 24, 4.5)]), STEEL, s=None, hl=hi("M-1.5,-34 L-1.5,18", 1.6, .8))
    blade = ("M-34,-112 Q0,-118 34,-112 Q38,-111 37,-106 L32,-52 Q31,-46 25,-46 L-25,-46 Q-31,-46 -32,-52 "
             "L-37,-106 Q-38,-111 -34,-112 Z")
    o += part(blade, STEEL, s=(-6, -7), hl=hi("M-26,-104 L-23,-64", 4, .75))
    o += part("M-31,-60 Q0,-56 31,-60 L30,-50 Q29,-46 24,-46 L-24,-46 Q-29,-46 -30,-50 Z", "#AEB5C4", s=None, k=.7)
    o += part(rr(-8, -50, 16, 14, 4), STEEL_D, s=None)
    o += part(rr(-9, 18, 18, 10, 3), STEEL_D, s=None)
    handle = rr(-10, 26, 20, 70, 10)
    o += part(handle, "#C27A42", s=(-3, -4), hl=hi("M-4,34 L-4,84", 3, .45))
    o += ln("M-10,50 L10,50 M-10,70 L10,70", lin("#C27A42"), .5)
    return o


@thing("baby_bottle", (-36, -100, 36, 92), rot=14, k=1.006, dx=2.0, dy=-2.5)
def baby_bottle():
    o = ""
    teat = "M-14,-66 C-16,-80 -9,-86 -6,-90 C-4,-98 4,-98 6,-90 C9,-86 16,-80 14,-66 Z"
    o += part(teat, "#F6C98A", s=(-3, -3), hl=hi("M-6,-84 C-8,-78 -8,-74 -8,-70", 2.5, .7))
    o += part(rr(-30, -68, 60, 22, 8), "#5BC0F8", s=(-4, -4), hl=hi("M-22,-62 L18,-62", 2.5, .55))
    body = "M-26,-46 L26,-46 L28,74 Q28,90 12,90 L-12,90 Q-28,90 -28,74 Z"
    milk = flat("M-40,-12 Q0,-4 40,-12 L40,100 L-40,100 Z", "#FFFFFF")
    milk += flat("M-40,-12 Q0,-4 40,-12 L40,-6 Q0,2 -40,-6 Z", "#EDF3FF")
    ticks = ln("M12,4 L24,4 M16,22 L24,22 M12,40 L24,40 M16,58 L24,58", "#7FB2E0", .6)
    o += comp(body, "#D8EEFF", milk + ticks, s=(-6, -6), ol="#7FA6D6", hl=hi("M-18,-38 L-18,70", 4, .8))
    o += part(heart_d(.75, -4, 40), "#FF7FA3", s=None, k=.6)
    return o


BONE = ("M-38.3,-9 L38.3,-9 A14,14 0 1 1 59.2,0 A14,14 0 1 1 38.3,9 L-38.3,9 "
        "A14,14 0 1 1 -59.2,0 A14,14 0 1 1 -38.3,-9 Z")


@thing("bone", (-74, -30, 74, 30), rot=-20, k=1.076, dx=0, dy=0)
def bone():
    return part(BONE, "#FFF0D4", s=(-4, -5), ol="#B98A56", hl=hi("M-56,-16 A10,10 0 0 1 -46,-24", 3, .9))


@thing("carrot", (-40, -82, 42, 74), rot=18, k=1.069, dx=-6.4, dy=4.8)
def carrot():
    o = ""
    for a in (-24, 0, 24):
        o += g(part("M0,-36 C-10,-50 -10,-70 0,-80 C10,-70 10,-50 0,-36 Z", GREEN, s=(-2, -3)), f"rotate({a} 0 -36)")
    body = "M-22,-34 C-24,-48 22,-48 22,-34 C20,0 8,40 2,62 C0,68 -4,68 -6,62 C-14,40 -22,0 -22,-34Z"
    o += part(body, "#FF8C2B", s=(-6, -7), hl=hi("M-14,-28 C-14,-10 -10,10 -6,24", 4, .6))
    o += ln("M-14,-12 L-4,-12 M6,4 L16,4 M-10,22 L0,22 M2,38 L8,38", "#D9631A", .8)
    return o


@thing("fish", (-90, -44, 92, 44), rot=-12, k=0.983, dx=-4.4, dy=7.4)
def fish():
    """A whole blue-silver fish (food for the cat, not a pet goldfish)."""
    back, belly = "#5B8FC9", "#E8F0F8"
    o = ""
    o += part("M-14,-30 C-6,-46 18,-48 32,-30 Z", "#4A7AB4", s=(-2, -2))                      # top fin
    o += part("M-4,28 C2,40 16,40 20,28 Z", "#4A7AB4", s=None)                                   # bottom fin
    tail = "M50,-2 C62,-16 74,-34 90,-38 C84,-18 84,14 90,38 C74,34 62,16 50,2 Z"
    o += part(tail, back, s=(-3, -4))
    o += ln("M62,-6 L82,-26 M64,0 L84,0 M62,6 L82,26", "#3F6EA6", .55)
    body = "M-86,0 C-78,-26 -40,-36 -6,-34 C24,-32 46,-14 56,0 C46,14 24,32 -6,34 C-40,36 -78,26 -86,0 Z"
    inner = flat("M-100,2 C-60,10 0,16 70,0 L70,60 L-100,60 Z", belly)
    inner += "".join(ln(f"M{x},-18 Q{x + 6},-12 {x},-6", "#4A7AB4", .5) + ln(f"M{x + 8},-8 Q{x + 14},-2 {x + 8},4", "#4A7AB4", .5)
                     for x in (-12, 4, 20))
    o += comp(body, back, inner, s=(-6, -7), hl=hi("M-66,-14 C-50,-26 -26,-30 -4,-28", 4, .55))
    o += ln("M-48,-20 C-40,-8 -40,8 -48,20", "#3F6EA6", .8)
    o += part(ell(-64, -6, 8.5), "#FFFFFF", s=None, ol="#3F6EA6", k=.7)
    o += flat(ell(-63, -5, 5), "#1F2A3A") + hidot(-65, -8, 1.8, 1)
    o += part("M-38,6 C-30,6 -22,14 -26,20 C-32,20 -38,14 -38,6 Z", "#4A7AB4", s=None, k=.7)    # side fin
    o += ln("M-86,2 L-80,3", "#3F6EA6", .7)
    return o


@thing("whistle", (-74, -60, 70, 46), k=0.983, dx=3.4, dy=3.4)
def whistle():
    """A steel whistle on a red cord."""
    o = hose("M30,-24 C28,-46 46,-58 58,-46 C68,-36 60,-20 44,-20", "#F2463F", 5)
    o += part(ell(32, -22, 7), STEEL_D, s=None, fr=False)
    o += flat(ell(32, -22, 3.5), "#FFFFFF")
    d = ("M-72,-16 L-6,-16 C2,-30 22,-36 36,-28 C54,-18 56,10 42,24 C28,38 2,38 -10,24 C-14,18 -14,10 -14,6 "
         "L-72,6 Q-76,6 -76,2 L-76,-12 Q-76,-16 -72,-16 Z")
    o += part(d, STEEL, s=(-6, -7), hl=hi("M-66,-10 L-24,-10", 3.5, .85) + hi("M6,-18 C14,-24 24,-26 32,-22", 3.5, .85))
    o += part("M-24,-16 L-8,-16 L-12,-8 L-24,-8 Z", "#4B4560", s=None, k=.6)
    o += ln("M-72,-5 L-30,-5", STEEL_D, .5)
    return o


@thing("letter", (-82, -58, 82, 58), rot=-8, k=0.934, dx=0, dy=0)
def letter():
    """An envelope with a stamp (airmail edge, no writing)."""
    w, h = 160, 108
    env = rr(-w / 2, -h / 2, w, h, 8)
    edge = ""
    k = 0
    for x in range(-90, 90, 14):
        c = "#F2463F" if k % 2 == 0 else "#3D8BF2"
        edge += flat(f"M{x},{-h / 2 - 2} l8,0 l-6,9 l-8,0 Z", c) + flat(f"M{x},{h / 2 + 2} l8,0 l-6,-9 l-8,0 Z", c)
        k += 1
    for y in range(-60, 62, 14):
        c = "#F2463F" if k % 2 == 0 else "#3D8BF2"
        edge += flat(f"M{-w / 2 - 2},{y} l0,8 l9,-6 l0,-8 Z", c) + flat(f"M{w / 2 + 2},{y} l0,8 l-9,-6 l0,-8 Z", c)
        k += 1
    inner = edge
    inner += ln(f"M{-w / 2 + 6},{-h / 2 + 8} L0,8 L{w / 2 - 6},{-h / 2 + 8}", WHITE_OL, .8)
    o = comp(env, "#FFFFFF", inner, s=(-6, -7), ol=WHITE_OL, sh="#E1DCF0")
    # the stamp: a white zigzag edge round a picture of a little sun and hill
    st = ""
    sx0, sy0, sw_, sh_ = 34, -40, 34, 40
    pts = []
    for i in range(8):
        pts += [(sx0 + i * sw_ / 8, sy0), (sx0 + (i + .5) * sw_ / 8, sy0 + 2.5)]
    for i in range(8):
        pts += [(sx0 + sw_, sy0 + i * sh_ / 8), (sx0 + sw_ - 2.5, sy0 + (i + .5) * sh_ / 8)]
    for i in range(8):
        pts += [(sx0 + sw_ - i * sw_ / 8, sy0 + sh_), (sx0 + sw_ - (i + .5) * sw_ / 8, sy0 + sh_ - 2.5)]
    for i in range(8):
        pts += [(sx0, sy0 + sh_ - i * sh_ / 8), (sx0 + 2.5, sy0 + sh_ - (i + .5) * sh_ / 8)]
    st += part(poly(pts), "#FFFFFF", s=None, ol=WHITE_OL, k=.6)
    pic = rr(sx0 + 5, sy0 + 5, sw_ - 10, sh_ - 10, 2)
    st += comp(pic, "#7FD0F5", flat(ell(sx0 + 17, sy0 + 40, 20, 12), "#4FC461") + flat(ell(sx0 + 22, sy0 + 14, 5), GOLD),
               s=None, ol="#4A8FC0", k=.6)
    o += st
    o += ln("M-6,-30 C0,-34 6,-26 12,-30 C18,-34 24,-26 30,-30 M-6,-22 C0,-26 6,-18 12,-22 C18,-26 24,-18 30,-22", "#B1A9C9", .6)
    o += part(heart_d(.8, 0, 12), RED, s=None, k=.6)
    return o


@thing("hoe", (-60, -100, 100, 98), k=1.018, dx=13.2, dy=-5.6)
def hoe():
    """鋤頭: a long wooden handle and a broad flat iron blade hanging from its top end."""
    o = part(tube([(-56, 92, 7.5), (14, -74, 7.5)]), "#C68A4E", s=(-2, -3), hl=hi("M-52,72 L4,-56", 2.5, .45))
    # the blade, drawn hanging down in its own frame from the socket, then turned a little
    blade = "M-10,0 L10,0 L14,10 L32,14 Q36,15 36,20 L34,58 Q34,62 30,62 L-6,62 Q-10,62 -10,58 Z"
    bl = part(blade, "#8E95A6", s=(-5, -6), hl=hi("M4,20 L4,48", 3, .55))
    bl += part("M-10,50 L34,50 L34,58 Q34,62 30,62 L-6,62 Q-10,62 -10,58 Z", "#D6DAE3", s=None, k=.7)
    o += g(bl, "translate(18 -78) rotate(-24)")
    o += part(ell(16, -76, 13, 13), "#6E7486", s=None)
    o += flat(ell(16, -76, 6.5), "#C68A4E")
    return o


@thing("glasses", (-84, -34, 84, 40), k=0.944, dx=0, dy=3.8)
def glasses():
    """Reading glasses: brown frames, see-through lenses (pale in the thought bubble's silhouette)."""
    fr = "#8A4F2B"
    o = ""
    for sx in (-1, 1):
        o += hose(f"M{sx * 74},-14 L{sx * 82},-30", fr, 6)
    lens = lambda sx: rr(sx * 44 - 32, -24, 64, 52, 22)
    for sx in (-1, 1):
        o += flat(lens(sx), "#CDEEFF", op=.45)
        o += hi(f"M{sx * 44 - 18},-6 L{sx * 44 - 6},-16 M{sx * 44 - 14},6 L{sx * 44 + 6},-12", 4, .9)
    for sx in (-1, 1):
        o += hose(lens(sx), fr, 7)
    o += hose("M-12,-4 Q0,-14 12,-4", fr, 6)
    return o


@thing("schoolbag", (-64, -86, 64, 86), k=0.950, dx=0, dy=3.3)
def schoolbag():
    """A child's backpack: a carry loop on top, straps, a big front pocket."""
    col, strap, pk = "#3D8BF2", "#2A5FB0", "#FFC233"
    o = hose("M-20,-68 C-20,-92 20,-92 20,-68", strap, 7)
    for sx in (-1, 1):
        o += part(rr(sx * 58 - 7, -50, 14, 112, 6), strap, s=None)
    body = "M-50,-56 C-50,-74 -34,-78 0,-78 C34,-78 50,-74 50,-56 L52,64 C52,80 40,84 0,84 C-40,84 -52,80 -52,64 Z"
    o += part(body, col, s=(-8, -9), hl=hi("M-40,-60 C-34,-70 -20,-72 -6,-72", 4, .6))
    pocket = "M-38,10 C-38,0 -30,-2 0,-2 C30,-2 38,0 38,10 L38,58 C38,70 30,72 0,72 C-30,72 -38,70 -38,58 Z"
    o += part(pocket, pk, s=(-5, -6), hl=hi("M-28,10 L-28,52", 3, .55))
    o += ln("M-32,12 Q0,6 32,12", lin(pk), .7)
    o += part(rr(18, 4, 8, 16, 3), "#FFFFFF", s=None, ol=lin(pk), k=.6)
    o += part(star_d(14, 6.5, cx=0, cy=40, round_=.18), "#FFFFFF", s=None, ol=lin(pk), k=.7)
    o += part(rr(-30, -40, 60, 10, 5), "#BFE3FF", s=None, ol=lin(col), k=.7)
    return o


@thing("scissors", (-46, -108, 46, 78), rot=-28, k=0.983, dx=-10.3, dy=-1.5)
def scissors():
    """Hairdresser's scissors: long steel blades, two finger rings (one with a finger rest)."""
    ring = "#9B5DE5"
    o = ""
    for sx in (-1, 1):
        o += part(tube([(0, 0, 6.5), (sx * 16, 30, 6.5), (sx * 22, 42, 6.5)]), ring, s=None)
    for sx in (-1, 1):
        o += part(ell(sx * 26, 56, 19, 19) + " " + ell(sx * 26, 56, 10.5, 10.5), ring, s=(-3, -4), fr=True)
    o += part("M42,66 C50,72 50,82 42,84 C38,78 36,74 34,72 Z", ring, s=None)
    for sx in (-1, 1):
        blade = f"M{sx * -3},6 L{sx * 24},-104 C{sx * 30},-74 {sx * 26},-30 {sx * 13},2 Z"
        o += part(blade, STEEL, s=(-2, -3), hl=hi(f"M{sx * 17},-20 L{sx * 24},-74", 2.4, .85))
    o += part(ell(0, 2, 7), GOLD, s=None, hl=hidot(-2, 0, 2))
    return o


@thing("paintbrush", (-22, -106, 22, 94), rot=36, k=1.181, dx=2.4, dy=-1.2)
def paintbrush():
    """A paintbrush with a red handle and a tip dipped in bright paint."""
    o = ""
    handle = "M-13,-14 L13,-14 L9,84 Q9,94 0,94 Q-9,94 -9,84 Z"
    o += part(handle, "#F2463F", s=(-3, -4), hl=hi("M-5,-4 L-4,80", 3, .55))
    tuft = "M-17,-40 C-24,-58 -16,-84 0,-106 C16,-84 24,-58 17,-40 Z"
    paint = flat("M-40,-82 C-20,-90 10,-74 40,-84 L40,-130 L-40,-130 Z", "#3D8BF2")
    paint += flat("M-40,-82 C-20,-90 10,-74 40,-84 L40,-74 C10,-64 -20,-80 -40,-72 Z", "#4FC461")
    paint += flat("M-40,-72 C-20,-80 10,-64 40,-74 L40,-64 C10,-54 -20,-70 -40,-62 Z", "#FFC233")
    o += comp(tuft, "#EBC98F", paint, s=(-3, -4), ol="#2F64B5", hl=hi("M-8,-56 C-10,-70 -6,-84 -2,-94", 3, .6))
    o += part(rr(-16, -44, 32, 32, 4), STEEL, s=(-2, -3), hl=hi("M-10,-38 L-10,-18", 2.5, .8))
    o += ln("M-16,-26 L16,-26 M-16,-20 L16,-20", STEEL_D, .6)
    return o


def drop_d(x, y, s=1.0):
    p = lambda a, b: f"{n(x + a * s)},{n(y + b * s)}"
    return (f"M{p(0, 0)} C{p(4, 9)} {p(8, 15)} {p(8, 19)} C{p(8, 24)} {p(4, 27)} {p(0, 27)} "
            f"C{p(-4, 27)} {p(-8, 24)} {p(-8, 19)} C{p(-8, 15)} {p(-4, 9)} {p(0, 0)}Z")


# ================================================================ writing and checking
def build(only=None):
    """Write the pictures (all, or the names in `only`); returns {name: KB}."""
    out = {}
    for name, fn in OWNERS.items():
        if only and name not in only:
            continue
        begin(ol=OL_PEOPLE)
        out[name] = save(name, fn())
    for name, fn in THINGS.items():
        if (only and name not in only) or (not only and name in SHARED):
            continue
        begin(ol=OL_THING)
        out[name] = save(name, fn())
    if not only or "scene_street" in only:
        begin(ol=OL_SCENE)
        out["scene_street"] = save("scene_street", scene_street(), K.SCENE_W, K.SCENE_H)
    return out


def scene_street():
    return ""
