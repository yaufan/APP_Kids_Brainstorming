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

from forest_kit import (begin, blob, clip_convex, dot, ell, finish, heart_d, lgrad, line, mix, paper, poly, rect_fill, rr,
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


def EXTRA_JOBS():
    return {}


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
