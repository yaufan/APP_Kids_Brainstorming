"""The pictures of 紙片森林 (style B 剪紙拼貼風), drawn with forest_kit.py.

    python3 forest_art.py                    # writes every picture to app/assets/art/forest/
    python3 forest_art.py bee hen            # only these
    python3 forest_art.py preview out.png    # a contact sheet of every picture (Node.js + Playwright)

What is drawn (ids as in app/lib/core/content.dart):
  - the 30 things of 連連看 (pairs → pairThings), 200 x 200;
  - the 16 suspects of 小偵探, suspect_<species>_<wear>.svg: four animals (rabbit, squirrel,
    hedgehog, bear) in the same pose and size, each with nothing / a red scarf / a green hat /
    round glasses, 200 x 200 with the feet on the same line;
  - the three missing things of the mysteries (strawberries, honey, pinecones), 200 x 200;
  - two backgrounds, 390 x 844: scene_meadow (連連看) and scene_woods (小偵探).
"""
import math
import pathlib
import subprocess
import sys
import tempfile

from forest_kit import (_apply, _tfm, parse, begin, blob, clip_convex, dot, ell, finish, heart_d, lgrad, line, mix, paper, poly, rect_fill, rr,
                        spline, star_d, sym, tf, tube, write, OUT, HERE)

INK = "#4A3346"        # eyes' pupils, mouths
CREAM = "#FFF6EA"
WHITE = "#F7F3EC"      # white paper (a little warm, so it shows on a light card)


# ---------------------------------------------------------------- faces
def eye(cx, cy, rx, ry, lx=.5, ly=1.0, pc="#2E2230"):
    paper(ell(cx, cy, rx, ry), "#FFFFFF", shadow=.6, grain=False, rough=.35)
    px, py, prx, pry = cx + lx, cy + ly, rx * .7, ry * .72
    paper(ell(px, py, prx, pry), pc, shadow=.35, grain=False, rough=.25)
    dot(px - prx * .32, py - pry * .36, prx * .42)
    dot(px + prx * .38, py + pry * .3, prx * .17)


def bead_eye(cx, cy, r, pc="#2E2230"):
    """A small dark eye with a shine (birds, bugs)."""
    paper(ell(cx, cy, r), pc, shadow=.4, grain=False, rough=.25)
    dot(cx - r * .3, cy - r * .35, r * .38)


def blush(cx, cy, rx=9, ry=5.5, col="#FF8E9A"):
    paper(ell(cx, cy, rx, ry), col, shadow=.25, grain=False, rough=.4, op=.85)


def mouth(d, col=INK, w=3.4):
    line(d, col, w=w, shadow=.5, rough=.25)


# ================================================================ 連連看: the pair things
THINGS = {}


def thing(f):
    THINGS[f.__name__.rstrip("_")] = f
    return f


@thing
def bee():
    for (cx, cy, rx, ry, a) in ((-2, -30, 15, 22, -24), (20, -30, 14, 20, 22)):
        with tf(f"translate({cx} {cy}) rotate({a})"):
            paper(ell(0, 0, rx, ry), "#CFE9F7")
            paper(ell(0, 3, rx * .55, ry * .62), "#E8F5FC", shadow=0, grain=False)
    body = ell(4, 10, 42, 31)
    paper(body, "#FFD43B")
    for x in (6, 28):
        paper(clip_convex(rr(x, -40, 11, 100, 2), body, .985), "#4A3426", shadow=.6)
    paper("M44,4 L58,10 L44,16 Z", "#4A3426")
    line("M-22,-14 C-26,-30 -32,-40 -38,-46", "#4A3426", w=3.6)
    line("M-12,-18 C-12,-34 -10,-44 -6,-52", "#4A3426", w=3.6)
    paper(ell(-38, -47, 4.5), "#4A3426", shadow=.5)
    paper(ell(-6, -53, 4.5), "#4A3426", shadow=.5)
    eye(-24, 4, 7.5, 9, -1, 1)
    eye(-6, 4, 7.5, 9, -1, 1)
    mouth("M-22,20 Q-15,26 -8,20")
    blush(-32, 18, 5, 3.5)
    blush(3, 18, 5, 3.5)


@thing
def flower():
    paper(tube([(0, 0, 4), (2, 36, 4), (0, 70, 4)]), "#4FB45A")
    paper("M2,44 C14,30 34,30 42,38 C30,50 14,52 2,44 Z", "#4FC461")
    paper("M-2,58 C-14,44 -34,44 -42,52 C-30,64 -14,66 -2,58 Z", "#4FC461")
    for i in range(6):
        with tf(f"translate(0 -16) rotate({i * 60 - 90})"):
            paper(ell(0, -26, 15, 22), "#FF8FB1")
    for i in range(6):
        with tf(f"translate(0 -16) rotate({i * 60 - 60})"):
            paper(ell(0, -20, 6, 9), "#FFC2D3", shadow=.4, grain=False)
    paper(ell(0, -16, 17), "#FFD43B")
    paper(ell(-3, -19, 8), "#FFE680", shadow=0, grain=False)


@thing
def hen():
    for x in (-6, 14):
        line(f"M{x},36 L{x},54 M{x - 8},59 L{x},54 L{x + 8},59", "#F29A2E", w=4.2)
    for a, c in ((-28, "#E9E1D4"), (-8, WHITE), (14, "#EFE8DC")):
        with tf(f"translate(40 0) rotate({a})"):
            paper("M-6,6 C-4,-22 8,-40 20,-44 C26,-30 22,-10 10,10 Z", c)
    body = "M-44,-8 C-44,-40 -8,-44 18,-28 C40,-16 56,4 48,24 C40,44 8,48 -14,42 C-36,36 -46,16 -44,-8 Z"
    paper(body, WHITE)
    paper("M-2,4 C10,-8 32,-4 36,10 C32,26 10,28 -2,4 Z", "#E6DED2")
    paper("M6,8 C14,2 26,4 30,12 C22,18 12,18 6,8 Z", "#D9CFC0", shadow=.5, grain=False)
    paper("M-42,-36 C-46,-48 -40,-56 -34,-52 C-34,-62 -24,-64 -22,-54 C-18,-62 -8,-58 -12,-46 Z", "#F2463F")
    paper(ell(-30, -26, 22, 21), WHITE)
    paper("M-50,-27 L-65,-20 L-50,-14 Z", "#FFB020")
    paper("M-50,-12 C-55,-4 -50,6 -44,-1 C-43,-6 -46,-10 -50,-12 Z", "#F2463F")
    eye(-34, -30, 6.5, 7.5, -1, .5)
    blush(-22, -16, 5, 3.5)


@thing
def egg():
    with tf("translate(26 6) rotate(18) scale(.78)"):
        paper("M0,-44 C18,-44 30,-14 30,6 C30,24 16,34 0,34 C-16,34 -30,24 -30,6 C-30,-14 -18,-44 0,-44 Z", "#F6E9D6")
    with tf("translate(-14 0) rotate(-8)"):
        paper("M0,-44 C18,-44 30,-14 30,6 C30,24 16,34 0,34 C-16,34 -30,24 -30,6 C-30,-14 -18,-44 0,-44 Z", "#EBC79B")
        paper("M-14,-22 C-12,-30 -8,-35 -4,-37 C-6,-30 -8,-24 -9,-18 Z", "#F6E3C8", shadow=0, grain=False)


@thing
def cow():
    for sx in (-1, 1):
        with tf(f"translate({sx * 56} -26) rotate({sx * -18})"):
            paper(ell(0, 0, 22, 11), "#3E3A44" if sx < 0 else WHITE)
            paper(ell(sx * 2, 0, 12, 6), "#FFC2D1", shadow=.4, grain=False)
        paper(f"M{sx * 22},-44 C{sx * 24},-58 {sx * 34},-63 {sx * 41},-58 C{sx * 35},-54 {sx * 32},-48 {sx * 33},-40 Z", "#F1DDB2")
    head = ell(0, -8, 48, 46)
    paper(head, WHITE)
    paper(clip_convex("M-60,-60 L-4,-60 C-6,-40 -18,-26 -36,-22 C-50,-20 -60,-30 -60,-40Z", head, .985), "#3E3A44")
    paper(clip_convex(blob([(22, 0), (40, -12), (56, 0), (52, 16), (36, 18)]), head, .985), "#3E3A44")
    paper("M-8,-56 C-4,-66 4,-66 8,-56 C4,-52 -4,-52 -8,-56Z", "#3E3A44", shadow=.5)
    paper(rr(-34, 46, 68, 9, 4), "#E5484D")
    paper(ell(0, 30, 40, 24), "#FFB6C6")
    paper(ell(-14, 30, 5, 6.5), "#C2607A", shadow=.4, grain=False)
    paper(ell(14, 30, 5, 6.5), "#C2607A", shadow=.4, grain=False)
    eye(-20, -12, 9, 11, .5, 1)
    eye(20, -12, 9, 11, .5, 1)
    mouth("M-10,44 Q0,49 10,44", "#8A3A50")
    paper("M-11,54 C-11,48 11,48 11,54 L13,68 L-13,68 Z", "#FFC233")
    paper(ell(0, 68, 4), "#B77F1E", shadow=.4, grain=False)


@thing
def milk():
    bottle = ("M-17,-84 L17,-84 L17,-56 C17,-38 38,-32 38,-8 L38,72 C38,82 30,88 20,88 L-20,88 C-30,88 -38,82 -38,72 "
              "L-38,-8 C-38,-32 -17,-38 -17,-56 Z")
    paper(bottle, "#BCD7E6")
    paper("M-31,-18 C-18,-24 -8,-12 4,-17 C16,-22 24,-14 31,-19 L31,70 C31,77 26,81 19,81 L-19,81 C-26,81 -31,77 -31,70 Z", "#FBF9F4")
    paper(rr(-24, -8, 6, 70, 3), "#E9F3F7", shadow=0, grain=False)
    band = rr(-35, 8, 70, 46, 6)
    paper(band, "#F7F3EC")
    paper(clip_convex(blob([(-40, 4), (-20, 6), (-14, 20), (-24, 32), (-40, 28)]), band, .985), "#3E3A44", shadow=.4)
    paper(clip_convex(blob([(2, 20), (14, 14), (24, 22), (20, 34), (6, 34)]), band, .985), "#3E3A44", shadow=.4)
    paper(clip_convex(blob([(26, 40), (40, 38), (42, 58), (28, 58)]), band, .985), "#3E3A44", shadow=.4)
    paper(clip_convex(blob([(-16, 44), (-6, 42), (-4, 50), (-14, 52)]), band, .985), "#3E3A44", shadow=.4)
    paper(rr(-21, -98, 42, 18, 5), "#4F86D9")
    paper(rr(-19, -86, 38, 6, 3), "#3E6FBF", shadow=.4, grain=False)


@thing
def rain_cloud():
    cl = ("M-54,12 C-72,12 -74,-14 -56,-18 C-58,-42 -28,-50 -16,-36 C-8,-56 28,-56 34,-32 C52,-40 72,-24 62,-6 "
          "C76,0 72,22 56,22 L-50,22 C-52,22 -53,17 -54,12 Z")
    for x, y in ((-40, 44), (-12, 56), (16, 44), (44, 56), (-26, 76), (30, 78)):
        paper(f"M{x},{y - 14} C{x + 4},{y - 5} {x + 8},{y + 1} {x + 8},{y + 5} C{x + 8},{y + 10} {x + 4},{y + 13} {x},{y + 13} "
              f"C{x - 4},{y + 13} {x - 8},{y + 10} {x - 8},{y + 5} C{x - 8},{y + 1} {x - 4},{y - 5} {x},{y - 14}Z", "#4FA8F5")
    with tf("translate(8 -8) scale(1.04)"):
        paper(cl, "#C9D5E4")
    paper(cl, "#9FB4CF")
    paper("M-40,6 C-44,-6 -34,-14 -24,-10 C-20,-22 0,-24 6,-12 C14,-16 24,-8 20,2 Z", "#B6C7DC", shadow=0, grain=False)


@thing
def umbrella():
    line("M0,-4 L0,50 C0,66 -20,66 -20,52", "#8A5A35", w=8, final=False)
    can = ("M-68,0 C-66,-40 -36,-64 0,-64 C36,-64 66,-40 68,0 Q56.5,-10 45,0 Q33.5,-10 22,0 Q11,-10 0,0 "
           "Q-11,-10 -22,0 Q-33.5,-10 -45,0 Q-56.5,-10 -68,0Z")
    paper(can, "#FF6F91")
    xs = [-68, -45, -22, 0, 22, 45, 68]
    for i in (0, 2, 4):
        a, b = xs[i], xs[i + 1]
        if i == 0:
            d = f"M-68,0 C-66,-40 -36,-64 0,-64 Q{b * .6:.1f},-34 {b},0 Q{(a + b) / 2},-10 {a},0 Z"
        else:
            d = f"M0,-64 Q{a * .6:.1f},-34 {a},0 Q{(a + b) / 2},-10 {b},0 Q{b * .6:.1f},-34 0,-64 Z"
        paper(d, "#FFD43B", shadow=.5)
    for x in xs[1:-1]:
        line(f"M0,-62 Q{x * .6:.1f},-34 {x},-1", "#C2406A", w=2.2, shadow=.3)
    paper(rr(-3, -78, 6, 16, 3), "#8A5A35")
    paper(ell(0, -64, 5), "#FF6F91", shadow=.4)


@thing
def bird():
    for x in (-8, 10):
        line(f"M{x},40 L{x},54 M{x - 7},58 L{x},54 L{x + 7},58", "#F29A2E", w=4)
    paper("M30,-4 L74,-26 L68,-8 L78,4 L36,16 Z", "#3E7FBF")
    body = ell(2, 8, 44, 38)
    paper(body, "#6CB4E4")
    paper(clip_convex(ell(-12, 26, 30, 24), body, .97), "#FBE8C8")
    paper("M-6,-34 C-10,-46 -4,-54 2,-50 C2,-58 12,-58 10,-46 Z", "#3E7FBF")
    paper(ell(-22, -18, 27, 25), "#6CB4E4")
    paper("M-2,0 C14,-14 44,-12 52,6 C44,22 18,26 -2,0 Z", "#4E95CC")
    paper("M8,4 C18,-2 34,-2 40,8 C30,14 18,14 8,4 Z", "#3E7FBF", shadow=.4, grain=False)
    paper("M-46,-24 L-64,-16 L-46,-9 Z", "#FFB020")
    eye(-30, -24, 7, 8, -1.5, .5)
    blush(-22, -8, 6, 4)


@thing
def nest():
    paper(ell(0, -8, 74, 22), "#6E4A2C")
    for x, y, a, c in ((-28, -18, -16, "#B9DDF0"), (28, -18, 16, "#B9DDF0"), (0, -24, 0, "#A9D3EC")):
        with tf(f"translate({x} {y}) rotate({a})"):
            paper(ell(0, 0, 17, 22), c)
            for dx, dy in ((-6, -6), (5, -10), (7, 3), (-3, 8)):
                paper(ell(dx, dy, 2, 1.6), "#7FA6C2", shadow=0, grain=False)
    front = "M-80,-10 C-78,30 -42,48 0,48 C42,48 78,30 80,-10 C52,6 -52,6 -80,-10 Z"
    paper(front, "#A8743F")
    for i, y in enumerate((4, 18, 32)):
        k = 1 - i * .16
        line(f"M{-74 * k:.0f},{y - 8} C{-40 * k:.0f},{y + 10} {40 * k:.0f},{y + 10} {74 * k:.0f},{y - 8}",
             "#C9955A" if i % 2 == 0 else "#7E5230", w=4.5, shadow=.5)
    for x0, x1, y0 in ((-60, -30, 2), (-20, 12, 16), (24, 56, 4), (-44, -10, 30), (10, 40, 32)):
        line(f"M{x0},{y0} L{x1},{y0 + 12}", "#8C5A30", w=3, shadow=.4)
    line("M-78,-12 L-96,-24", "#8C5A30", w=4)
    line("M76,-6 L96,-18 M88,-13 L94,-4", "#8C5A30", w=4)


@thing
def toothbrush():
    with tf("rotate(-32)"):
        handle = ("M-96,4 C-96,-3 -92,-6 -86,-6 L26,-4 C34,-4 40,-8 48,-8 L102,-8 C108,-8 110,-4 110,0 L110,8 "
                  "C110,12 108,14 102,14 L48,14 C40,14 34,10 26,10 L-86,12 C-92,12 -96,10 -96,4 Z")
        for i, x in enumerate(range(54, 104, 10)):
            paper(rr(x, -32, 9, 28, 3), "#EAF5FA" if i % 2 == 0 else "#B9E0F2", shadow=.7)
        paper(handle, "#2EC4C0")
        paper(rr(-74, -1, 70, 8, 4), "#9FE3DE", shadow=.5)
        paper(ell(-84, 3, 4), "#1E8F8B", shadow=.3, grain=False)


@thing
def toothpaste():
    with tf("rotate(-16)"):
        body = "M-70,-22 L-70,22 L-62,22 C-30,24 20,26 46,16 L46,-16 C20,-26 -30,-24 -62,-22 Z"
        paper(tube([(56, 0, 11), (74, -2, 11), (90, -12, 11), (96, -28, 10.5), (86, -38, 10)]), "#F4F7FA")
        line("M58,-4 C68,-6 80,-10 88,-18 C93,-26 92,-34 86,-37", "#4F86D9", w=4, shadow=.3)
        line("M58,5 C70,4 84,-2 94,-12", "#7FB8EE", w=3, shadow=.2)
        paper("M-80,-25 L-66,-25 L-66,25 L-80,25 Z", "#DCE6F0")
        for y in (-16, -6, 4, 14):
            line(f"M-78,{y} L-68,{y}", "#AFC0D2", w=1.8, shadow=0)
        paper(body, "#EEF3F8")
        paper(clip_convex(rr(-34, -40, 52, 80, 0), body, .97), "#4F86D9")
        paper(clip_convex("M-34,-6 C-20,-14 -6,4 8,-6 C12,-9 16,-8 20,-6 L20,6 C12,2 6,10 -6,8 C-20,6 -26,0 -34,8Z", body, .97),
              "#FFFFFF", shadow=.4)
        paper(clip_convex(rr(28, -40, 7, 80, 0), body, .97), "#E5484D", shadow=.4)
        paper("M46,-16 L58,-10 L58,10 L46,16 Z", "#DCE6F0")


@thing
def key():
    with tf("rotate(-28)"):
        col = "#F2C14E"
        paper("M-22,-8 L66,-8 C70,-8 73,-5 73,-1 L73,7 L65,7 L65,22 L55,22 L55,7 L51,7 L51,17 L41,17 L41,7 L-22,7 Z", col)
        paper(ell(-44, 0, 30) + ell(-44, 0, 11), col, evenodd=True)
        paper(ell(-44, 0, 21) + ell(-44, 0, 13.5), "#E0A93A", evenodd=True, shadow=.4, grain=False)
        line("M-6,0 L60,0", "#D49A2E", w=2.2, shadow=.3)


@thing
def lock():
    line("M-22,-6 L-22,-32 A22,22 0 0 1 22,-32 L22,-6", "#AEB6C6", w=11, final=False)
    line("M-22,-10 L-22,-32 A22,22 0 0 1 22,-32", "#C9D0DC", w=4, final=False, shadow=0)
    paper(rr(-40, -14, 80, 62, 14), "#E9A23B")
    paper(rr(-31, -6, 62, 46, 10), "#F4BE55", shadow=.5)
    paper("M0,2 C7,2 10,8 7,13 L11,30 L-11,30 L-7,13 C-10,8 -7,2 0,2Z", "#5A3A1A", shadow=.4)


@thing
def sock():
    leg = ("M-30,-60 L26,-60 L26,10 C26,18 32,22 42,24 L64,28 C84,32 86,62 64,66 L4,68 C-22,68 -32,50 -30,24 Z")
    paper(leg, "#FF8FB1")
    for y in (-38, -20, -2):
        paper(rr(-29, y, 54, 9, 2), "#FFD0DE", shadow=.4)
    paper("M-30,30 C-26,44 -18,60 2,66 C-14,68 -30,58 -31,40 Z", "#E4628C", shadow=.4)
    paper("M64,28 C84,32 86,62 64,66 L56,66 C66,58 66,36 56,28 Z", "#E4628C", shadow=.4)
    paper(rr(-34, -76, 64, 22, 6), "#F6EFE8")
    for x in range(-26, 26, 8):
        line(f"M{x},-71 L{x},-59", "#DCCFC4", w=2, shadow=0)


@thing
def shoe():
    col = "#F2545B"
    up = "M-66,-6 C-66,-30 -56,-46 -40,-46 L-12,-46 C-2,-46 4,-38 10,-28 L40,-18 C62,-12 76,-2 76,14 L-66,14 Z"
    paper(up, col)
    paper("M40,-18 C62,-12 76,-2 76,14 L46,14 C48,2 46,-8 40,-18Z", "#F6EFE8", shadow=.5)
    paper("M-56,-40 C-48,-48 -26,-48 -16,-42 C-24,-34 -46,-34 -56,-40Z", "#5A2E3A", shadow=.5)
    paper(rr(-72, 8, 156, 18, 9), "#F2ECE2")
    line("M-62,18 L76,18", "#D3C8B8", w=2, shadow=0)
    paper(ell(-30, -10, 13), "#FFD43B", shadow=.6)
    paper(star_d(7.5, 3.4, cx=-30, cy=-10, round_=.15), "#FFFFFF", shadow=.3, grain=False)
    for i in range(3):
        x = 0 + i * 12
        line(f"M{x - 4},{-34 + i * 4} L{x + 8},{-26 + i * 4}", "#FFF6EA", w=3.6, shadow=.4)


@thing
def bowl():
    for x in (-22, 18):
        line(f"M{x},-58 C{x - 8},-68 {x + 8},-76 {x},-88", "#C9D3DE", w=4.5, shadow=0)
    paper("M-76,-8 C-72,-56 72,-56 76,-8 Z", "#FBF8F1")
    for i, (x, y) in enumerate(((-50, -18), (-30, -30), (-8, -38), (14, -34), (36, -26), (54, -16), (-40, -12), (-18, -22),
                                (4, -24), (26, -16), (-60, -10), (44, -10), (-4, -12), (18, -44), (-28, -44))):
        with tf(f"translate({x} {y}) rotate({(i * 47) % 180})"):
            paper(ell(0, 0, 4.5, 2.4), "#E9DFCB", shadow=.3, grain=False)
    body = "M-82,-10 C-80,30 -46,56 0,56 C46,56 80,30 82,-10 Z"
    paper(rr(-28, 50, 56, 14, 5), "#3E6FBF")
    paper(body, "#5B8FD6")
    paper(clip_convex(rr(-90, 8, 180, 14, 0), body, .985), "#F4EFE4", shadow=.4)
    for x in range(-60, 61, 20):
        paper(ell(x, 15, 3.6), "#5B8FD6", shadow=0, grain=False)


@thing
def chopsticks():
    with tf("rotate(-38)"):
        paper(rr(-34, 40, 68, 20, 10), "#BFD8EE")
        paper(ell(0, 45, 24, 5), "#D9E8F6", shadow=0, grain=False)
        for dx in (-11, 11):
            with tf(f"translate({dx} 0) rotate({dx * .3})"):
                paper(tube([(0, -92, 6.4), (0, 62, 3.2)], 2), "#C8925A")
                paper(tube([(0, -92, 6.5), (0, -60, 5.8)], 2), "#D9534F", shadow=.4)


def hand(skin="#E9B48C", sleeve="#7EC8E3", dipped=(1, 2)):
    """A child's hand, palm to us, fingers up, thumb to the right (mirror it for the other hand);
    the fingers in `dipped` have muddy tips."""
    for i, (x, top, w) in enumerate(((-21, -38, 6.6), (-7, -50, 7.4), (7, -54, 7.6), (21, -46, 7.2))):
        f = tube([(x * .9, 8, w), (x, (top + 8) / 2, w), (x * 1.06, top, w * .95)], 4)
        paper(f, skin)
        if i in dipped:
            paper(clip_convex(f"M{x - 12},{top - 12} L{x + 14},{top - 12} L{x + 14},{top + 10} C{x + 4},{top + 14} {x - 4},{top + 6} {x - 12},{top + 12} Z",
                              f, .97), "#7A5638", shadow=.4, grain=False)
    paper(tube([(18, 30, 8.5), (34, 18, 8), (42, 6, 7.5)], 4), skin)
    paper(rr(-28, -8, 56, 62, 22), skin)
    paper(rr(-31, 46, 62, 24, 7), sleeve)
    line("M-26,52 L26,52", "#FFFFFF", w=2.4, shadow=0, op=.6)


def mud(points, col="#7A5638"):
    for i, (x, y, r) in enumerate(points):
        n = 7
        pts = [(x + math.cos(2 * math.pi * k / n) * r * (1 + .28 * math.sin(k * 2.7 + i)),
                y + math.sin(2 * math.pi * k / n) * r * (1 + .28 * math.cos(k * 1.9 + i))) for k in range(n)]
        paper(blob(pts), col, shadow=.4, grain=False)


@thing
def dirty_hands():
    for sx in (-1, 1):
        with tf(f"translate({sx * 50} 0) rotate({sx * 12}) scale({-sx} 1)"):
            hand()
            mud([(-8, 12, 9), (12, 30, 6.5), (-20, -26, 3.8), (-4, 38, 4.5), (16, 6, 3.6), (34, 14, 4.2), (24, -4, 2.4), (-16, 32, 2.6)])
            mud([(-16, 24, 5), (2, 20, 3.2), (22, -30, 3.5), (-2, -20, 2.6)], "#9C7350")


@thing
def soap():
    paper(rr(-58, -6, 116, 50, 22), "#D98AAE")
    paper(rr(-58, -20, 116, 48, 22), "#F4A6C0")
    paper(ell(0, 4, 32, 13), "#EC93B4", shadow=.3)
    paper(ell(-2, 2, 26, 9), "#F8BCD1", shadow=0, grain=False)
    for x, y, r in ((-44, -42, 13), (-12, -54, 9), (22, -46, 16), (54, -24, 9), (-66, -14, 8), (52, 46, 8), (-56, 48, 6), (38, -74, 7)):
        paper(ell(x, y, r), "#BFE3F6", shadow=.6)
        paper(ell(x + r * .12, y + r * .12, r * .66), "#DDF1FA", shadow=0, grain=False)
        dot(x - r * .42, y - r * .42, max(1.4, r * .2))


def snowflake(cx, cy, r, a=0, col="#8EC3E8"):
    with tf(f"translate({cx} {cy}) rotate({a})"):
        d = ""
        for k in range(6):
            t = math.radians(k * 60)
            ex, ey = math.cos(t) * r, math.sin(t) * r
            d += f"M0,0 L{ex:.1f},{ey:.1f} "
            for f, bl in ((.55, .34),):
                bx, by = math.cos(t) * r * f, math.sin(t) * r * f
                for s in (-1, 1):
                    u = t + s * math.radians(50)
                    d += f"M{bx:.1f},{by:.1f} L{bx + math.cos(u) * r * bl:.1f},{by + math.sin(u) * r * bl:.1f} "
        line(d, col, w=max(2.6, r * .2), shadow=.6, rough=.3)
        paper(ell(0, 0, r * .22), col, shadow=.3, grain=False)


@thing
def snow():
    cl = ("M-54,12 C-72,12 -74,-14 -56,-18 C-58,-42 -28,-50 -16,-36 C-8,-56 28,-56 34,-32 C52,-40 72,-24 62,-6 "
          "C76,0 72,22 56,22 L-50,22 C-52,22 -53,17 -54,12 Z")
    for x, y, r, a in ((-42, 50, 13, 10), (-2, 64, 15, 0), (40, 48, 13, 20), (-26, 86, 10, 15), (24, 88, 11, 5)):
        snowflake(x, y, r, a)
    with tf("translate(8 -8) scale(1.04)"):
        paper(cl, "#DDE6F0")
    paper(cl, "#C2D2E6")
    paper("M-40,6 C-44,-6 -34,-14 -24,-10 C-20,-22 0,-24 6,-12 C14,-16 24,-8 20,2 Z", "#D3DFEE", shadow=0, grain=False)


def mitten(col="#E0504A"):
    """A mitten, thumb to the right."""
    paper(tube([(14, 18, 9), (28, 6, 8.5), (32, -8, 8)], 4), col)
    paper("M-26,30 L-26,-16 C-26,-50 26,-50 26,-16 L26,30 Z", col)
    paper(heart_d(1.15, 0, -10), "#F7F3EC", shadow=.4)
    paper(rr(-30, 26, 60, 24, 7), "#F2ECE2")
    for x in range(-22, 26, 8):
        line(f"M{x},31 L{x},45", "#DCD1C1", w=2, shadow=0)


@thing
def gloves():
    for sx, c in ((-1, "#E0504A"), (1, "#E0504A")):
        with tf(f"translate({sx * 38} 0) rotate({sx * 12}) scale({-sx} 1)"):
            mitten(c)


@thing
def sun():
    for k in range(12):
        a = k * 30
        R = 92 if k % 2 == 0 else 80
        with tf(f"rotate({a})"):
            paper(f"M-11,-50 L0,-{R} L11,-50 Z", "#FFB13B" if k % 2 == 0 else "#FFD43B")
    paper(ell(0, 0, 60), "#FFB13B")
    paper(ell(0, 0, 51), "#FFD43B")
    eye(-19, -8, 8, 9.5, .5, 1)
    eye(19, -8, 8, 9.5, .5, 1)
    mouth("M-17,15 Q0,31 17,15", INK, 4)
    blush(-34, 12, 8, 5)
    blush(34, 12, 8, 5)


@thing
def sun_hat():
    straw = "#E8C77A"
    paper(ell(0, 18, 94, 34), straw)
    for rx, ry in ((84, 28), (72, 22)):
        line(f"M{-rx},18 A{rx},{ry} 0 0 0 {rx},18", "#CDA758", w=1.8, shadow=0)
    crown = "M-46,22 C-48,-26 -28,-48 0,-48 C28,-48 48,-26 46,22 C30,30 -30,30 -46,22 Z"
    paper(crown, "#E2BC6A")
    for y in (-30, -14):
        line(f"M{-40 + (y + 30) * -.2:.0f},{y} C-20,{y + 5} 20,{y + 5} {40 - (y + 30) * -.2:.0f},{y}", "#C9A257", w=1.8, shadow=0)
    paper(clip_convex(rr(-60, 2, 120, 17, 0), crown, .985), "#E0605A", shadow=.6)
    with tf("translate(36 10)"):
        paper("M0,0 L10,26 L3,24 L-2,30 Z", "#E0605A", shadow=.6)
        paper("M0,0 C10,-14 26,-12 26,-2 C26,8 10,8 0,0 Z", "#E0605A")
        paper("M0,0 C-10,-14 -26,-12 -26,-2 C-26,8 -10,8 0,0 Z", "#E0605A")
        paper(ell(0, 0, 6), "#C2453F", shadow=.5)


@thing
def squirrel():
    tail = blob([(26, 66), (60, 62), (84, 34), (88, -6), (78, -48), (54, -74), (28, -70), (22, -50), (42, -38), (54, -12),
                 (50, 18), (34, 40)])
    paper(tail, "#C9763D")
    paper(blob([(52, -56), (68, -36), (72, -6), (66, 24), (56, 40), (60, 8), (58, -22), (46, -46)]), "#E6A56A", shadow=.4)
    body = "M-30,6 C-40,30 -38,60 -24,70 C-8,80 22,78 32,64 C42,46 34,14 18,0 C6,-8 -20,-8 -30,6 Z"
    paper(body, "#D9874A")
    paper("M-24,24 C-28,40 -24,60 -12,66 C0,70 10,62 8,46 C6,30 -6,18 -24,24 Z", "#FBE3C4", shadow=.5)
    paper(ell(-22, 70, 18, 8), "#C9763D")
    paper(ell(10, 72, 18, 8), "#C9763D")
    paper("M2,-50 C0,-66 8,-80 16,-86 C20,-74 20,-60 14,-48 Z", "#D9874A")
    paper("M6,-52 C6,-62 10,-70 14,-74 C16,-66 16,-58 12,-50 Z", "#FFC2D1", shadow=.3, grain=False)
    paper("M14,-84 C18,-92 22,-94 24,-100 C24,-90 22,-84 18,-78 Z", "#B4642F", shadow=.4)
    paper(ell(-10, -32, 31, 28), "#D9874A")
    paper(ell(-32, -22, 15, 12), "#FBE3C4", shadow=.5)
    paper(ell(-46, -27, 4.5, 3.8), "#5A3424", shadow=.4, grain=False)
    eye(-20, -38, 7.5, 8.5, -1.5, .5)
    blush(-12, -20, 6, 4)
    mouth("M-42,-16 Q-38,-12 -34,-16", INK, 2.8)
    paper(tube([(-8, 14, 7), (-22, 26, 6.5), (-32, 24, 6.5)], 4), "#C9763D")


def pinecone(cx=0, cy=0, s=1.0, a=0, needles=True, big=1.0):
    """A pinecone hanging tip down: rows of pointed scales, each row over the one below."""
    with tf(f"translate({cx} {cy}) rotate({a}) scale({s})"):
        if needles:
            for ang in (-34, -12, 12, 34):
                line(f"M0,-50 L{math.sin(math.radians(ang)) * 34:.1f},{-50 - math.cos(math.radians(ang)) * 34:.1f}", "#5E9E5A",
                     w=3, shadow=.4)
        paper(rr(-4, -60, 8, 14, 3), "#6E4A2C")
        paper(blob([(0, -50), (26, -42), (34, -14), (28, 22), (14, 48), (0, 56), (-14, 48), (-28, 22), (-34, -14), (-26, -42)]), "#5E3A22")
        rows = []
        gap = 11.5 * big
        for r in range(int(92 / gap) + 1):
            y = -42 + r * gap
            u = (y + 6) / 56
            hw = 33 * math.sqrt(max(0.0, 1 - u * u)) * (1.0 if y < -6 else 1 - .25 * u) + 4
            n = max(2, round(2 * hw / (15 * big)))
            rows.append((y, hw, n, r))
        for y, hw, n, r in reversed(rows):
            w = 2 * hw / n
            for k in range(n):
                x = -hw + w * (k + .5) + (w * .22 if r % 2 else -w * .22)
                edge = (x / hw) if hw else 0
                rot = edge * 28
                sw = w * .62
                c = "#A86B3C" if (k + r) % 2 == 0 else "#B97B48"
                with tf(f"translate({x:.1f} {y:.1f}) rotate({-rot:.1f})"):
                    paper(f"M{-sw:.1f},-8 L{sw:.1f},-8 C{sw:.1f},2 4,10 0,13 C-4,10 {-sw:.1f},2 {-sw:.1f},-8 Z", c, shadow=.8, grain=False)
                    paper(f"M{-sw * .55:.1f},3 C{-sw * .3:.1f},7 -2,10 0,11.5 C2,10 {sw * .3:.1f},7 {sw * .55:.1f},3 Z", "#D9A26A",
                          shadow=0, grain=False)


@thing
def pinecone_():
    pinecone()


@thing
def caterpillar():
    segs = [(66, 10, 17), (44, 0, 19), (20, 8, 20), (-4, 0, 21)]
    for i, (x, y, r) in enumerate(segs):
        paper(ell(x - 4, y + r - 2, 5, 4), "#3E7A34", shadow=.4, grain=False)
        paper(ell(x + 6, y + r - 1, 5, 4), "#3E7A34", shadow=.4, grain=False)
    for i, (x, y, r) in enumerate(segs):
        paper(ell(x, y, r), "#8BC34A" if i % 2 == 0 else "#6FB040")
        paper(ell(x + 2, y - r * .45, r * .26), "#FFD43B", shadow=.3, grain=False)
    line("M-40,-34 C-44,-48 -50,-54 -56,-58", "#3E7A34", w=3.4)
    line("M-22,-36 C-20,-50 -16,-56 -10,-60", "#3E7A34", w=3.4)
    paper(ell(-56, -59, 5), "#F2785A", shadow=.4)
    paper(ell(-10, -61, 5), "#F2785A", shadow=.4)
    paper(ell(-32, -8, 30, 28), "#9CD35A")
    eye(-44, -14, 7, 8.5, -1, 1)
    eye(-24, -14, 7, 8.5, -1, 1)
    mouth("M-42,4 Q-34,10 -26,4")
    blush(-52, 2, 5, 3.5)
    blush(-16, 2, 5, 3.5)


@thing
def butterfly():
    for sx in (-1, 1):
        with tf(f"scale({sx} 1)"):
            paper(blob([(6, -6), (26, -50), (60, -66), (78, -50), (72, -16), (46, 2), (12, 4)]), "#FF8FB1")
            paper(blob([(8, 6), (40, 8), (62, 26), (58, 52), (36, 60), (16, 44)]), "#FFB84D")
            paper(ell(50, -36, 12), "#FFE3EC", shadow=.4)
            paper(ell(32, -14, 7), "#FFE3EC", shadow=.4)
            paper(ell(38, 34, 9), "#FFE9B8", shadow=.4)
    paper(tube([(0, -26, 7.5), (0, 10, 8.5), (0, 44, 6)], 4), "#5A3A5E")
    line("M-4,-40 C-10,-58 -22,-66 -30,-64", "#5A3A5E", w=3.2)
    line("M4,-40 C10,-58 22,-66 30,-64", "#5A3A5E", w=3.2)
    paper(ell(-31, -64, 4.5), "#5A3A5E", shadow=.4)
    paper(ell(31, -64, 4.5), "#5A3A5E", shadow=.4)
    paper(ell(0, -36, 11), "#6E4A72")
    dot(-4, -38, 2.4)
    dot(4, -38, 2.4)


def tadpole_(s=1.0, cx=0, cy=0, a=0, face=True):
    with tf(f"translate({cx} {cy}) rotate({a}) scale({s})"):
        fin = tube([(16, 0, 15), (40, -8, 12), (62, 4, 8), (84, -6, 4), (100, -2, 1.5)], 6)
        paper(fin, "#8E8F76")
        line("M18,0 C34,-8 50,6 66,0 C78,-4 88,-4 96,-3", "#6A6A54", w=3, shadow=0)
        paper(ell(-12, 0, 36, 32), "#55574A")
        paper(ell(-16, 12, 22, 14), "#7A7C66", shadow=.4)
        if face:
            eye(-30, -10, 8, 9, -1.5, .5)
            eye(-8, -12, 7, 8, -1, .5)
            mouth("M-32,10 Q-24,16 -16,10", "#2E2E26", 3)
        else:
            bead_eye(-26, -8, 6)


@thing
def tadpole():
    for x, y, r in ((-70, -42, 7), (-58, -62, 5), (-76, -76, 4), (60, 40, 6)):
        paper(ell(x, y, r), "#BFE3F6", shadow=.5)
        dot(x - r * .35, y - r * .35, max(1.2, r * .25))
    tadpole_(.5, 34, -44, -12, face=False)
    tadpole_(1.0, -6, 18, 4)


def lily_pad(cx, cy, rx, ry, col="#4E9A52"):
    pts = []
    for k in range(60):
        t = math.radians(-70 + k * (340 / 59))
        pts.append((cx + math.cos(t) * rx, cy + math.sin(t) * ry))
    pts.append((cx, cy))
    paper(pts, col)


@thing
def frog():
    lily_pad(0, 66, 92, 22)
    for sx in (-1, 1):
        paper(ell(sx * 46, 46, 28, 20), "#5FA84A")
        paper(ell(sx * 60, 64, 14, 6), "#5FA84A")
    paper(ell(0, 26, 44, 40), "#7CC456")
    paper(ell(0, 36, 28, 26), "#D8EBA8", shadow=.5)
    for sx in (-1, 1):
        paper(ell(sx * 20, 62, 11, 7), "#6DB54E")
    paper(ell(0, -14, 58, 38), "#7CC456")
    for sx in (-1, 1):
        paper(ell(sx * 28, -44, 21), "#7CC456")
        eye(sx * 28, -44, 13, 14, sx * -.5, 1)
    mouth("M-30,-4 Q0,16 30,-4", "#2F5E2A", 4)
    blush(-42, -2, 8, 5)
    blush(42, -2, 8, 5)


# ================================================================ 小偵探: the suspects
SPECIES = {
    # fur, light (belly, muzzle), nose
    "rabbit": ("#F1EBE5", "#FFFFFF", "#FF8FAB"),
    "squirrel": ("#D9874A", "#FBE3C4", "#5A3424"),
    "hedgehog": ("#EBD3B4", "#F6E6CF", "#3A2418"),
    "bear": ("#B98252", "#EBC9A0", "#3A2418"),
}
WEARS = ("none", "scarf", "hat", "glasses")
SCARF = "#D9443C"
HAT = "#5E9E5A"
FRAME = "#34497A"


def _bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])


def spikes(cx, cy, rx, ry, a0, a1, n, depth, col):
    """A zigzag fringe of spikes along an ellipse from angle a0 to a1 (degrees, 0 = right, 90 = up),
    closed through the centre."""
    pts = []
    for k in range(2 * n + 1):
        t = math.radians(a0 + (a1 - a0) * k / (2 * n))
        f = 1.0 if k % 2 else 1 - depth
        pts.append((cx + math.cos(t) * rx * f, cy - math.sin(t) * ry * f))
    pts.append((cx, cy + ry * .2))
    paper(pts, col)


HAT_AT = "translate(0 -63) rotate(-7) scale(.86)"


def tpts(d, t):
    """The points of path d after transform t (in the current drawing units)."""
    M = _tfm(t)
    return [_apply(M, p) for p in parse(d)[0][0]]


def rabbit_ears(fur, cut=None):
    """Long ears; with `cut`, only the part above that line (coming out from under a hat)."""
    for sx in (-1, 1):
        t = f"translate({sx * 21} 0) rotate({sx * 17} 0 -60)"
        outer, inner = tpts(ell(0, -88, 15, 36), t), tpts(ell(0, -85, 7, 26), t)
        if cut is not None:
            box = [(-300, -400), (300, -400), (300, cut), (-300, cut)]
            outer, inner = clip_convex(outer, box, 1), clip_convex(inner, box, 1)
        paper(outer, fur)
        paper(inner, "#FFC2D1", shadow=.4)


def critter(kind, wear="none"):
    fur, light, nose = SPECIES[kind]
    paw = {"rabbit": fur, "squirrel": "#C9763D", "hedgehog": "#C9A07A", "bear": "#A87444"}[kind]
    if kind == "squirrel":
        paper(blob([(18, 82), (56, 86), (88, 62), (102, 22), (102, -24), (90, -62), (66, -82), (42, -78), (32, -58), (50, -42),
                    (62, -10), (56, 24), (40, 52)]), "#C9763D")
        paper(blob([(54, -62), (76, -50), (88, -18), (88, 20), (76, 50), (62, 66), (70, 30), (72, -6), (66, -36)]), "#E6A56A", shadow=.5)
    if kind == "hedgehog":
        spikes(0, 2, 82, 92, 232, -52, 15, .2, "#6E4A30")
        spikes(0, 2, 74, 84, 228, -48, 15, .22, "#9A6E48")
    # body
    body = "M-32,14 C-44,36 -46,70 -36,86 C-24,98 24,98 36,86 C46,70 44,36 32,14 Z"
    paper(body, fur if kind != "hedgehog" else "#E2C49E")
    paper(ell(0, 62, 21, 25), light, shadow=.5)
    for sx in (-1, 1):
        paper(ell(sx * 19, 95, 18 if kind == "rabbit" else 16, 9), paw)
        paper(tube([(sx * 30, 30, 8.5), (sx * 40, 50, 8), (sx * 42, 64, 8)]), paw)
    if wear == "scarf":
        T = ((-46, 8), (-22, 24), (22, 24), (46, 8))
        B = ((-48, 26), (-24, 44), (24, 44), (48, 26))
        paper("M-46,8 C-22,24 22,24 46,8 L48,26 C24,44 -24,44 -48,26 Z", SCARF)
        d = ""
        for k in range(1, 12):
            t = k / 12
            a, b = _bez(*T, t), _bez(*B, t)
            d += f"M{a[0] + (b[0] - a[0]) * .22:.1f},{a[1] + (b[1] - a[1]) * .22:.1f} L{a[0] + (b[0] - a[0]) * .78:.1f},{a[1] + (b[1] - a[1]) * .78:.1f} "
        line(d, "#B8352F", w=2.2, shadow=0)
        with tf("translate(22 32) rotate(-6)"):
            paper("M-10,-4 L10,-4 L12,46 L-12,46 Z", SCARF)
            line(" ".join(f"M-8,{y} L8,{y}" for y in (6, 16, 26, 36)), "#B8352F", w=2.2, shadow=0)
            line(" ".join(f"M{x},46 L{x * 1.1:.1f},56" for x in (-9, -3, 3, 9)), SCARF, w=3.2, shadow=.5)
        paper(ell(14, 30, 11, 9), "#C93C35")
    # ears
    if kind == "rabbit":
        if wear != "hat":
            rabbit_ears(fur)
    elif kind == "bear":
        for sx in (-1, 1):
            paper(ell(sx * 40, -62, 17), fur)
            paper(ell(sx * 40, -62, 8.5), light, shadow=.4)
    elif kind == "squirrel":
        for sx in (-1, 1):
            with tf(f"translate({sx * 34} -60) rotate({sx * 12})"):
                paper("M-13,8 C-15,-12 -6,-28 2,-34 C9,-22 13,-6 13,8 Z", fur)
                paper("M-6,4 C-7,-8 -2,-18 2,-22 C5,-14 6,-4 5,4 Z", "#FFC2D1", shadow=.4)
                paper("M-1,-30 C2,-40 6,-44 6,-50 C10,-42 8,-34 4,-26 Z", "#B4642F", shadow=.4)
    elif kind == "hedgehog":
        for sx in (-1, 1):
            paper(ell(sx * 44, -52, 11), fur)
            paper(ell(sx * 44, -52, 5.5), "#F2B5B5", shadow=.4)
    # head
    paper(ell(0, -24, 54, 46), fur)
    if kind == "hedgehog":
        spikes(0, -24, 56, 48, 152, 28, 7, -.32, "#9A6E48")
        paper(ell(0, -24, 50, 40), fur, shadow=0)
        spikes(0, -26, 50, 44, 140, 40, 5, -.28, "#7A5236")
    if kind != "rabbit":
        paper(ell(0, -8, 20, 15), light, shadow=.5)
    eye(-21, -26, 11, 13, .5, 1.5)
    eye(21, -26, 11, 13, .5, 1.5)
    blush(-37, -6, 8, 5)
    blush(37, -6, 8, 5)
    big = kind in ("bear", "hedgehog")
    paper("M-6,-12 C-6,-16 6,-16 6,-12 C6,-8 2,-5 0,-5 C-2,-5 -6,-8 -6,-12Z" if not big else
          "M-8,-14 C-8,-19 8,-19 8,-14 C8,-9 3,-5 0,-5 C-3,-5 -8,-9 -8,-14Z", nose, shadow=.5)
    if kind == "rabbit":
        paper(rr(-5, 1, 10, 9, 2.5), "#FFFFFF", shadow=.6, grain=False)
        line("M0,2 L0,9", "#D8CFC8", w=1.4, shadow=0)
    mouth("M-9,0 Q-4,5 0,-3 Q4,5 9,0", INK, 3)
    if wear == "glasses":
        for sx in (-1, 1):
            paper(ell(sx * 21, -26, 14, 15.5), "#CFE8F7", shadow=0, grain=False, op=.3)
            paper(ell(sx * 21, -26, 19.5, 21) + ell(sx * 21, -26, 14, 15.5), FRAME, evenodd=True, shadow=.6, grain=False)
            line(f"M{sx * 39.5},-31 L{sx * 54},-36", FRAME, w=4.5, shadow=.5)
            line(f"M{sx * 21 - 9},-33 Q{sx * 21 - 6},-38 {sx * 21 - 1},-39", "#FFFFFF", w=2.4, shadow=0, op=.8)
        line("M-6,-31 Q0,-37 6,-31", FRAME, w=4.5, shadow=.5)
    if wear == "hat":
        with tf(HAT_AT):
            paper(ell(0, 0, 52, 12), "#4E8A4B")
        if kind == "rabbit":
            rabbit_ears(fur, cut=-60)
        with tf(HAT_AT):
            crown = "M-31,2 C-33,-26 -23,-42 0,-42 C23,-42 33,-26 31,2 Z"
            paper(crown, HAT)
            paper(clip_convex(rr(-40, -13, 80, 11, 0), crown, .985), "#7A4E2C", shadow=.6)
            line("M-9,-40 Q0,-31 9,-40", "#4E8A4B", w=2.6, shadow=0)
            paper("M20,-8 C28,-28 40,-42 48,-48 C46,-32 36,-16 25,-4 Z", "#F2B33D")
            line("M22,-7 C30,-22 40,-36 46,-44", "#D99A2B", w=1.6, shadow=0)


_SUS_FIX = []


def suspect_fixed():
    """One transform for all 16 suspects: same size, feet on the same line, body in the middle."""
    if not _SUS_FIX:
        from forest_kit import LAYERS, _bbox
        x0 = y0 = 1e9
        x1 = y1 = -1e9
        for kind in SPECIES:
            for w in WEARS:
                begin()
                critter(kind, w)
                a, b, c, d = _bbox(LAYERS)
                x0, y0, x1, y1 = min(x0, a), min(y0, b), max(x1, c), max(y1, d)
        half = max(-x0, x1)
        s = min(184 / (2 * half), 182 / (y1 - y0))
        # drawing point that goes to the centre of the box: x 0, y so that the feet sit 9 above the bottom
        cy = y1 - (91 - 4) / s
        _SUS_FIX.append((s, 0.0, cy))
        begin()
    return _SUS_FIX[0]


def suspect_job(kind, w):
    def f():
        fx = suspect_fixed()
        begin()
        critter(kind, w)
        return lambda name: finish(name, fixed=fx, lift=0)
    return f


def EXTRA_JOBS():
    jobs = {}
    for kind in SPECIES:
        for w in WEARS:
            jobs[f"suspect_{kind}_{w}"] = (suspect_job(kind, w), {})
    return jobs


# ================================================================ 小偵探: what went missing
def strawberry(cx, cy, s=1.0, a=0):
    with tf(f"translate({cx} {cy}) rotate({a}) scale({s})"):
        paper("M0,24 C-14,16 -20,0 -16,-10 C-12,-19 12,-19 16,-10 C20,0 14,16 0,24 Z", "#E8414F")
        for x, y in ((-8, -4), (0, -8), (8, -4), (-5, 6), (5, 6), (0, 14), (-10, -11), (10, -11)):
            paper(ell(x, y, 1.3, 1.9), "#FFE08A", shadow=0, grain=False)
        paper(star_d(11, 4.5, n=5, cy=-15, round_=.2), "#4FB45A", shadow=.6)
        paper(rr(-1.5, -26, 3, 9, 1.5), "#3E8C3A", shadow=.4, grain=False)


@thing
def strawberries():
    line("M-58,-4 C-58,-86 58,-86 58,-4", "#B9874C", w=9, final=False)
    for x, y, a in ((-34, -30, -20), (32, -30, 18), (-12, -46, -6), (14, -48, 10), (0, -24, 0), (-44, -14, -30), (46, -14, 28)):
        strawberry(x, y, 1.15, a)
    body = "M-66,-6 L66,-6 C64,30 52,54 36,58 L-36,58 C-52,54 -64,30 -66,-6 Z"
    paper(body, "#D9A766")
    for y in (8, 26, 42):
        paper(clip_convex(rr(-80, y, 160, 8, 0), body, .985), "#E9C38A", shadow=.4, grain=False)
    for i, y in enumerate((0, 16, 34)):
        for k in range(-3, 4):
            x = k * 18 + (9 if i % 2 else 0)
            if abs(x) < 60 - i * 6:
                paper(rr(x - 3, y, 6, 10, 2), "#B9874C", shadow=.3, grain=False)
    paper(rr(-72, -14, 144, 14, 7), "#B9874C")


@thing
def honey():
    jar = ("M-46,-30 C-50,-30 -54,-26 -54,-20 L-54,46 C-54,58 -44,66 -30,66 L30,66 C44,66 54,58 54,46 L54,-20 "
           "C54,-26 50,-30 46,-30 Z")
    paper(jar, "#F2CF8A")
    paper("M-47,-14 C-30,-20 -14,-10 0,-14 C14,-18 30,-10 47,-14 L47,46 C47,54 40,59 30,59 L-30,59 C-40,59 -47,54 -47,46 Z", "#E8A93A")
    paper(rr(-40, -2, 6, 50, 3), "#F2C46A", shadow=0, grain=False)
    label = rr(-34, 8, 68, 38, 8)
    paper(label, "#FFF4DC")
    for hx, hy in ((-11, 21), (11, 21), (0, 33)):
        pts = [(hx + 9 * math.cos(math.radians(60 * k + 30)), hy + 9 * math.sin(math.radians(60 * k + 30))) for k in range(6)]
        paper(pts, "#F2B33D", shadow=.4, grain=False)
    paper(rr(-44, -42, 88, 14, 5), "#F2CF8A")
    cloth = ("M-42,-62 C-20,-68 20,-68 42,-62 L56,-34 C46,-28 38,-36 28,-30 C18,-36 10,-28 0,-34 C-10,-28 -18,-36 -28,-30 "
             "C-38,-36 -46,-28 -56,-34 Z")
    paper(cloth, "#FFF1E0")
    from forest_kit import _inside
    cl = parse(cloth)[0][0]
    for gx in range(-60, 61, 12):
        for gy in range(-72, -24, 12):
            if (gx // 12 + gy // 12) % 2 == 0:
                corners = [(gx + .5, gy + .5), (gx + 11.5, gy + .5), (gx + 11.5, gy + 11.5), (gx + .5, gy + 11.5)]
                if all(_inside(c, [cl]) for c in corners):
                    paper(rr(gx + 1, gy + 1, 10, 10, 1.5), "#E5484D", shadow=0, grain=False, op=.8)
    line("M-48,-44 C-20,-38 20,-38 48,-44", "#9C6A3A", w=3.4, shadow=.6)
    line("M30,-41 C26,-30 22,-26 18,-20 M32,-41 C38,-32 42,-28 46,-22", "#9C6A3A", w=3, shadow=.5)
    for x, ln_ in ((-40, 22), (-22, 10), (14, 30), (38, 16)):
        paper(f"M{x - 6},-30 L{x + 6},-30 L{x + 6},{-30 + ln_} C{x + 6},{-22 + ln_} {x - 6},{-22 + ln_} {x - 6},{-30 + ln_} Z", "#F2B740", shadow=.6)
    with tf("translate(56 -70) rotate(8) scale(.42)"):
        bee()


@thing
def pinecones():
    pinecone(-34, 34, .82, -64, needles=False, big=1.4)
    pinecone(36, 36, .82, 66, needles=False, big=1.4)
    pinecone(0, -12, .92, -8, big=1.3)


# ================================================================ writing and the contact sheet
# (drawings above this line)
def build(only=None):
    jobs = {}
    for k, f in THINGS.items():
        jobs[k] = (f, {})
    for k, (f, kw) in EXTRA_JOBS().items():
        jobs[k] = (f, kw)
    sizes = {}
    for name, (f, kw) in jobs.items():
        if only and name not in only:
            continue
        begin()
        fin = f()
        svg = fin(name) if callable(fin) else finish(name)
        sizes[name] = write(name, svg)
    return sizes


CARD = "#FFFBF2"


def preview(out, only=None):
    names = sorted(p.stem for p in OUT.glob("*.svg"))
    things = [n for n in THINGS if n in names]
    sus = [n for n in names if n.startswith("suspect_")]
    rest = [n for n in names if n not in things and n not in sus and not n.startswith("scene_")]
    scenes = [n for n in names if n.startswith("scene_")]
    u = lambda n: (OUT / f"{n}.svg").as_uri()

    def tile(n, s):
        return (f'<div class="t"><div class="c" style="width:{s + 16}px;height:{s + 16}px"><img src="{u(n)}" width="{s}" height="{s}"></div>'
                f'<div class="n">{n}</div></div>')

    h = ['<html><head><meta charset="utf-8"><style>body{margin:0;padding:16px;background:#EFE2C8;font:12px sans-serif;color:#4B3A5E}'
         '.row{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:14px}.t{text-align:center}'
         f'.c{{background:{CARD};border-radius:10px;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 4px #0002}}'
         'h2{margin:6px 0}.n{margin-top:2px}</style></head><body>']
    h.append("<h2>full size (200 px)</h2><div class='row'>" + "".join(tile(n, 200) for n in things + rest) + "</div>")
    h.append("<h2>120 px</h2><div class='row'>" + "".join(tile(n, 120) for n in things + rest) + "</div>")
    if sus:
        h.append("<h2>suspects</h2>")
        for sp in ("rabbit", "squirrel", "hedgehog", "bear"):
            h.append("<div class='row'>" + "".join(tile(f"suspect_{sp}_{w}", 200) for w in ("none", "scarf", "hat", "glasses")
                                                   if f"suspect_{sp}_{w}" in names)
                     + "".join(tile(f"suspect_{sp}_{w}", 110) for w in ("none", "scarf", "hat", "glasses") if f"suspect_{sp}_{w}" in names)
                     + "</div>")
    if scenes:
        h.append("<h2>scenes</h2><div class='row'>")
        for n in scenes:
            h.append(f'<div class="t"><img src="{u(n)}" width="390" height="844"><div class="n">{n}</div></div>')
        for n in scenes:
            h.append(f'<div class="t"><img src="{u(n)}" width="195" height="422"><div class="n">{n}</div></div>')
        h.append("</div>")
    h.append("</body></html>")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="forest_prev_", dir="/dev/shm"))
    html = tmp / "p.html"
    html.write_text("".join(h))
    js = tmp / "r.js"
    js.write_text("""const { chromium } = require('playwright');
(async () => { const [inp, out] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1900, height: 800 } });
  await p.goto('file://' + inp); await p.waitForTimeout(400);
  await p.screenshot({ path: out, fullPage: true }); await b.close(); })();""")
    subprocess.run(["node", str(js), str(html), str(out)], check=True)
    html.unlink()
    js.unlink()
    tmp.rmdir()
    print(out)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "preview":
        preview(pathlib.Path(a[1]).resolve())
    else:
        for k, v in build(set(a) or None).items():
            print(f"{k}: {v:.1f} KB")
