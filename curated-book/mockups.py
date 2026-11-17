"""Presentation PNGs of the finished book, built from the real print artwork.

  output/08_Mockups/01_Back_Cover.png           back of the master binder, flat (11 x 13 in)
  output/08_Mockups/02_Front_Cover.png          front of the master binder, flat
  output/08_Mockups/03_Catalogue_Set.png        4 binders in a studio scene (front, back, spine, open board)
  output/08_Mockups/04_All_Collections_In_One.png  the binder with all board covers laid out

Run on its own (python3 mockups.py) or from make.py.
"""

import os

from art import FONT_CSS, LINEN, master_back, master_front, outside_art, spine_art, all_img, board_img
from data import P
from layout import boards, layout_board, ordered_books
from printfiles import chromium, spine_width

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "output", "07_Mockups")


# ---------------------------------------------------------------- artwork as inline SVG
def svg(art, w, h, vx=0, bg=LINEN):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx} 0 {w} {h}" preserveAspectRatio="none" '
            f'style="width:100%;height:100%;display:block"><rect x="{vx}" width="{w}" height="{h}" fill="{bg}"/>{art}</svg>')


def board_cover(bd):
    """The cover panel (front of the folded board) of one board, 9 x 12 in."""
    art, xs, ws, _ = outside_art(bd, image=board_img(bd))
    i = 0 if (bd["fold"] or 2) == 2 else 1
    return svg(art, ws[i], P["board_h"], vx=xs[i])


def page(body, w, h, extra_css=""):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}
html,body{{margin:0;padding:0}} body{{width:{w}px;height:{h}px;overflow:hidden;position:relative}}
{extra_css}</style></head><body>{body}</body></html>"""


# ---------------------------------------------------------------- 3D binder
BOOK_CSS = """
.scene{position:absolute;inset:0;perspective:5200px;perspective-origin:50% 30%}
.book{position:absolute;transform-style:preserve-3d}
.face{position:absolute;left:0;top:0;backface-visibility:hidden;overflow:hidden}
.face::after{content:"";position:absolute;inset:0;pointer-events:none}
.front::after{background:linear-gradient(90deg,rgba(0,0,0,.10) 0,rgba(0,0,0,.10) 2.6%,rgba(255,255,255,.18) 2.8%,rgba(0,0,0,.12) 3.2%,rgba(0,0,0,0) 3.6%),linear-gradient(105deg,rgba(255,255,255,.10),rgba(255,255,255,0) 35%,rgba(0,0,0,.06))}
.back::after{background:linear-gradient(270deg,rgba(0,0,0,.10) 0,rgba(0,0,0,.10) 2.6%,rgba(255,255,255,.18) 2.8%,rgba(0,0,0,.12) 3.2%,rgba(0,0,0,0) 3.6%),linear-gradient(75deg,rgba(0,0,0,.05),rgba(255,255,255,0) 60%,rgba(255,255,255,.08))}
.spine::after{background:linear-gradient(90deg,rgba(0,0,0,.20),rgba(255,255,255,.10) 28%,rgba(255,255,255,0) 50%,rgba(0,0,0,.10) 82%,rgba(0,0,0,.24))}
.edge{background:linear-gradient(90deg,#CDBFA8,#E5DBCB 40%,#D3C6B1)}
.edge::after{background:repeating-linear-gradient(0deg,rgba(0,0,0,.05) 0 2px,transparent 2px 6px)}
.top{background:linear-gradient(0deg,#C9BBA3,#DCD1BF)}
.shadow{position:absolute;border-radius:50%;background:rgba(40,30,20,.38);filter:blur(28px)}
.leaf{position:absolute;overflow:hidden;box-shadow:0 30px 60px rgba(40,30,20,.28),0 6px 14px rgba(40,30,20,.18)}
.leaf::after{content:"";position:absolute;inset:0;background:linear-gradient(120deg,rgba(255,255,255,.12),rgba(255,255,255,0) 40%,rgba(0,0,0,.05))}
"""


def binder(front, back, spine, W, H, D, x, y, ry, rx=0):
    """Closed ring binder: W x H cover, D deep (px); spine on the left of the front cover."""
    return f"""<div class="book" style="left:{x}px;top:{y}px;width:{W}px;height:{H}px;transform:rotateX({rx}deg) rotateY({ry}deg)">
  <div class="face front" style="width:{W}px;height:{H}px;transform:translateZ({D / 2}px)">{front}</div>
  <div class="face back" style="width:{W}px;height:{H}px;transform:rotateY(180deg) translateZ({D / 2}px)">{back}</div>
  <div class="face spine" style="width:{D}px;height:{H}px;left:{(W - D) / 2}px;transform:rotateY(-90deg) translateZ({W / 2}px)">{spine}</div>
  <div class="face edge" style="width:{D}px;height:{H}px;left:{(W - D) / 2}px;transform:rotateY(90deg) translateZ({W / 2}px)"></div>
  <div class="face top" style="width:{W}px;height:{D}px;top:{(H - D) / 2}px;transform:rotateX(90deg) translateZ({H / 2}px)"></div>
</div>"""


def wall_and_floor(Wpx, Hpx, horizon):
    return (f'<div style="position:absolute;left:0;top:0;width:{Wpx}px;height:{horizon}px;'
            f'background:radial-gradient(ellipse at 45% 35%,#F3EFE8,#E6DFD3 60%,#D9D0C2)"></div>'
            f'<div style="position:absolute;left:0;top:{horizon}px;width:{Wpx}px;height:{Hpx - horizon}px;'
            f'background:linear-gradient(180deg,#CFC5B5,#DDD5C8 30%,#E6DFD4)"></div>'
            f'<div style="position:absolute;left:0;top:{horizon - 1}px;width:{Wpx}px;height:3px;background:rgba(0,0,0,.06);filter:blur(1px)"></div>')


def catalogue_set(front, back, spine, covers, sw):
    """Four binders: back cover, front cover, spine-out, and a board standing beside them."""
    Wpx, Hpx, horizon = 3200, 1800, 1330
    s = 74                                     # px per inch
    W, H, D = 11 * s, 13 * s, sw * s
    floor = horizon + 40
    top = floor - H
    parts = [wall_and_floor(Wpx, Hpx, horizon), '<div class="scene">']
    # soft contact shadows
    for cx, w in ((580, 960), (1550, 960), (2370, 440), (2840, 700)):
        parts.append(f'<div class="shadow" style="left:{cx - w / 2}px;top:{floor - 40}px;width:{w}px;height:80px"></div>')
    parts.append(binder(front, back, spine, W, H, D, 170, top, 158))          # 1: back cover
    parts.append(binder(front, back, spine, W, H, D, 1140, top, 24))          # 2: front cover
    parts.append(binder(front, back, spine, W, H, D, 1960, top, 80))          # 3: spine out
    parts.append("</div>")
    # 4: a board (9 x 12) leaning on the right, front cover visible
    bw, bh = 9 * s * .86, 12 * s * .86
    parts.append(f'<div class="leaf" style="left:2550px;top:{floor - bh - 6}px;width:{bw}px;height:{bh}px;'
                 f'transform:perspective(3000px) rotateY(-14deg);transform-origin:left bottom">{covers[14]}</div>')
    return page("".join(parts), Wpx, Hpx, BOOK_CSS)


def all_in_one(front, covers, nb):
    """Flat-lay: the binder front with every board cover laid out beside it."""
    Wpx, Hpx = 3200, 2000
    s = 104                                    # px per inch for the binder
    W, H = 11 * s, 13 * s
    bx, by = 140, (Hpx - H) / 2 + 30
    parts = [f'<div style="position:absolute;inset:0;background:radial-gradient(ellipse at 40% 40%,#F2EDE5,#E2DACE 70%,#D6CCBC)"></div>',
             f'<div class="leaf" style="left:{bx}px;top:{by}px;width:{W}px;height:{H}px;box-shadow:0 40px 80px rgba(40,30,20,.32),0 8px 18px rgba(40,30,20,.2)">{front}</div>']
    # grid of board covers
    cols, gap = 5, 26
    gx0, gx1 = bx + W + 120, Wpx - 120
    tw = (gx1 - gx0 - (cols - 1) * gap) / cols
    th = tw * 12 / 9
    rows = -(-len(covers) // cols)
    gy0 = (Hpx - (rows * th + (rows - 1) * gap)) / 2 + 30
    for i, c in enumerate(covers):
        x = gx0 + (i % cols) * (tw + gap)
        y = gy0 + (i // cols) * (th + gap)
        parts.append(f'<div class="leaf" style="left:{x}px;top:{y}px;width:{tw}px;height:{th}px;'
                     f'box-shadow:0 14px 28px rgba(40,30,20,.24),0 3px 8px rgba(40,30,20,.16)">{c}</div>')
    # the last cell: what is inside
    i = len(covers)
    x, y = gx0 + (i % cols) * (tw + gap), gy0 + (i // cols) * (th + gap)
    parts.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{tw}px;height:{th}px;border:2px solid #B4A894;'
                 f'box-sizing:border-box;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;'
                 f'font-family:CG;color:#2B2723">'
                 f'<div style="font-family:CZ;font-weight:600;font-size:22px;letter-spacing:5px;color:#8C6B36">ALL IN ONE BOOK</div>'
                 f'<div style="font-weight:600;font-size:96px;line-height:1;margin-top:18px">{nb}</div>'
                 f'<div style="font-weight:500;font-style:italic;font-size:34px;color:#6E655A">collections</div>'
                 f'<div style="font-family:CZ;font-weight:500;font-size:19px;letter-spacing:3px;color:#6E655A;margin-top:22px">'
                 f'{len(covers)} BOARDS<br>SHEER TO BLACKOUT</div></div>')
    return page("".join(parts), Wpx, Hpx, BOOK_CSS)


def flat(art_svg, w_in, h_in, dpi=150):
    Wpx, Hpx = round(w_in * dpi), round(h_in * dpi)
    return page(f'<div style="width:{Wpx}px;height:{Hpx}px">{art_svg}</div>', Wpx, Hpx), Wpx, Hpx


# ---------------------------------------------------------------- build
def build(outdir=OUTDIR):
    from playwright.sync_api import sync_playwright
    os.makedirs(outdir, exist_ok=True)
    books = ordered_books()
    bds = boards()
    for bd in bds:
        if bd["ready"]:
            layout_board(bd)
    sw, _ = spine_width(bds)
    W, H = P["cover_w"], P["cover_h"]
    front = svg(master_front(0, W, H, books)[0], W, H)
    back = svg(master_back(0, W, H, books, image=all_img()), W, H)
    spine = svg(spine_art(0, sw, H), sw, H)
    covers = [board_cover(bd) for bd in bds]

    jobs = []
    html, w, h = flat(back, W, H); jobs.append(("01_Back_Cover.png", html, w, h))
    html, w, h = flat(front, W, H); jobs.append(("02_Front_Cover.png", html, w, h))
    jobs.append(("03_Catalogue_Set.png", catalogue_set(front, back, spine, covers, sw), 3200, 1800))
    jobs.append(("04_All_Collections_In_One.png", all_in_one(front, covers, len(books)), 3200, 2000))

    out = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=chromium())
        for name, html, w, h in jobs:
            pg = b.new_page(viewport={"width": int(w), "height": int(h)}, device_scale_factor=1)
            tmp = os.path.join(outdir, name + ".html")
            open(tmp, "w").write(html)
            pg.goto("file://" + tmp)
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(300)
            path = os.path.join(outdir, name)
            pg.screenshot(path=path, full_page=False)
            os.remove(tmp)
            pg.close()
            out.append(path)
        b.close()
    return out


if __name__ == "__main__":
    for p in build():
        print("Wrote", p)
