"""Osho Decor swatch books in the Neo Luna design: covers + presentation mockups (PNG).

The Neo Luna sample book sets the design for every book: linen cloth cover, foil serif
title with the category between double rules, an arched room photo on the right, four
feature icons, black metal corner protectors and a black rope handle.

  output/01_Neo_Luna_Back_Cover.png      back cover, flat 11 x 13 in
  output/02_Neo_Luna_Front_Cover.png     front cover, flat (redrawn from the sample)
  output/03_Catalogue_Set.png            4 books, each with its own cover, tilted one way
  output/04_All_Collections_In_One.png   all 20 books on shelves, each with its own cover

Run:  python3 build.py
"""

import os
import sys
from functools import lru_cache

from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "curated-book"))
from art import drape, mix                      # noqa: E402  vector curtain scene
from layout import ladder_color, ordered_books  # noqa: E402  the 20 books, in order
from printfiles import chromium                 # noqa: E402

FONTS = os.path.join(HERE, "assets", "fonts")
PHOTOS = os.path.join(HERE, "assets", "photos")
OUT = os.path.join(HERE, "output")

W, H = 11.0, 13.0                     # cover, inches
LINEN, LINEN_DK, LINEN_LT = "#C9C1A9", "#B3AB92", "#D8D1BC"
PLUM, LABEL, INK = "#5B4246", "#4F4A45", "#2C2F33"
PT = 1 / 72

CSS = f"""
@font-face{{font-family:BD;src:url(file://{FONTS}/LibreBodoni-600.ttf)}}
@font-face{{font-family:FR;src:url(file://{FONTS}/Fraunces-700.ttf)}}
@font-face{{font-family:PP;src:url(file://{FONTS}/Poppins-Regular.ttf);font-weight:400}}
@font-face{{font-family:PP;src:url(file://{FONTS}/Poppins-Medium.ttf);font-weight:500}}
@font-face{{font-family:PP;src:url(file://{FONTS}/Poppins-SemiBold.ttf);font-weight:600}}
@font-face{{font-family:PP;src:url(file://{FONTS}/Poppins-Light.ttf);font-weight:300}}
@font-face{{font-family:CGI;src:url(file://{FONTS}/CormorantGaramond-500i.ttf)}}
"""
FILES = {"BD": "LibreBodoni-600.ttf", "FR": "Fraunces-700.ttf", "PP5": "Poppins-Medium.ttf", "PP4": "Poppins-Regular.ttf"}

# Subtitle under each book name.  Neo Luna as printed on the sample; the rest from the book list.
SUBTITLE = {"neo-luna": "100% Blackout", "texture-coated": "100% Blackout"}
FEATURES = [("kid", "KIDS", "FRIENDLY"), ("eco", "ECO", "FRIENDLY"), ("soft", "SOFT", "ON SKIN"),
            ("star", "EXCELLENT COLOURS", "FASTNESS TO LIGHT")]


@lru_cache(None)
def font(key):
    return ImageFont.truetype(os.path.join(FONTS, FILES[key]), 1000)


def tw(s, key, pt, track=0.0):
    return font(key).getlength(s) / 1000 * pt * PT + track * pt * PT * max(len(s) - 1, 0)


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, fam, pt, fill, anchor="start", weight=400, track=0.0, extra=""):
    ls = f'letter-spacing="{track * pt * PT:.4f}"' if track else ""
    return (f'<text x="{x:.4f}" y="{y:.4f}" font-family="{fam}" font-weight="{weight}" font-size="{pt * PT:.4f}" '
            f'fill="{fill}" text-anchor="{anchor}" {ls} {extra}>{esc(s)}</text>')


# ---------------------------------------------------------------- shared cover pieces
def defs(uid):
    return f"""<defs>
  <pattern id="weave{uid}" width=".034" height=".034" patternUnits="userSpaceOnUse">
    <path d="M0,.017 H.034" stroke="#FFFFFF" stroke-opacity=".20" stroke-width=".011"/>
    <path d="M.017,0 V.034" stroke="#000000" stroke-opacity=".07" stroke-width=".011"/>
  </pattern>
  <filter id="grain{uid}" x="0" y="0" width="1" height="1">
    <feTurbulence type="fractalNoise" baseFrequency="42 7" numOctaves="2" seed="3"/>
    <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .55 0"/>
  </filter>
  <linearGradient id="foil{uid}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#3A3F45"/><stop offset=".45" stop-color="#5A616A"/>
    <stop offset=".55" stop-color="#2E3237"/><stop offset="1" stop-color="#1F2226"/></linearGradient>
  <linearGradient id="metal{uid}" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#3B3B3B"/><stop offset=".35" stop-color="#141414"/>
    <stop offset=".7" stop-color="#262626"/><stop offset="1" stop-color="#0B0B0B"/></linearGradient>
  <radialGradient id="light{uid}" cx=".3" cy=".25" r=".9">
    <stop offset="0" stop-color="#FFFFFF" stop-opacity=".10"/><stop offset="1" stop-color="#000000" stop-opacity=".10"/></radialGradient>
</defs>"""


def linen(uid, w=W, h=H):
    return (f'<rect width="{w}" height="{h}" fill="{LINEN}"/>'
            f'<rect width="{w}" height="{h}" fill="url(#weave{uid})"/>'
            f'<rect width="{w}" height="{h}" filter="url(#grain{uid})" opacity=".13"/>'
            f'<rect width="{w}" height="{h}" fill="url(#light{uid})"/>')


def corner(uid, right=False):
    d = ("M0,12.1 L.13,12.1 C.23,12.1 .28,12.18 .28,12.27 C.28,12.35 .33,12.4 .42,12.4 "
         "C.52,12.4 .57,12.47 .57,12.56 C.57,12.64 .62,12.69 .71,12.69 C.81,12.69 .86,12.77 .86,12.87 "
         "L.86,13 L0,13 Z")
    t = f' transform="translate({W} 0) scale(-1 1)"' if right else ""
    return (f'<g{t}><path d="{d}" fill="url(#metal{uid})"/>'
            f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-opacity=".18" stroke-width=".012"/></g>')


def icon(kind, cx, cy, r=.3):
    s = f'stroke="#FFFFFF" stroke-width="{r * .07:.4f}" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    k = r / .3
    g = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{PLUM}"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{r * .86:.3f}" fill="none" stroke="#FFFFFF" stroke-opacity=".35" stroke-width="{r * .025:.4f}"/>']
    if kind == "kid":
        g += [f'<circle cx="{cx}" cy="{cy}" r="{.13 * k:.3f}" {s}/>',
              f'<circle cx="{cx - .045 * k:.3f}" cy="{cy - .02 * k:.3f}" r="{.012 * k:.3f}" fill="#FFF"/>',
              f'<circle cx="{cx + .045 * k:.3f}" cy="{cy - .02 * k:.3f}" r="{.012 * k:.3f}" fill="#FFF"/>',
              f'<path d="M{cx - .05 * k:.3f},{cy + .04 * k:.3f} Q{cx},{cy + .09 * k:.3f} {cx + .05 * k:.3f},{cy + .04 * k:.3f}" {s}/>',
              f'<path d="M{cx - .02 * k:.3f},{cy - .13 * k:.3f} Q{cx + .03 * k:.3f},{cy - .2 * k:.3f} {cx + .06 * k:.3f},{cy - .15 * k:.3f}" {s}/>']
    elif kind == "eco":
        g += [f'<path d="M{cx - .13 * k:.3f},{cy + .12 * k:.3f} C{cx - .15 * k:.3f},{cy - .06 * k:.3f} {cx - .02 * k:.3f},{cy - .15 * k:.3f} {cx + .15 * k:.3f},{cy - .15 * k:.3f} '
              f'C{cx + .15 * k:.3f},{cy + .02 * k:.3f} {cx + .04 * k:.3f},{cy + .13 * k:.3f} {cx - .13 * k:.3f},{cy + .12 * k:.3f} Z" {s}/>',
              f'<path d="M{cx - .13 * k:.3f},{cy + .12 * k:.3f} L{cx + .08 * k:.3f},{cy - .08 * k:.3f}" {s}/>']
    elif kind == "soft":
        g += [f'<path d="M{cx - .17 * k:.3f},{cy + .1 * k:.3f} Q{cx - .05 * k:.3f},{cy + .16 * k:.3f} {cx + .12 * k:.3f},{cy + .08 * k:.3f} '
              f'L{cx + .17 * k:.3f},{cy + .02 * k:.3f}" {s}/>',
              f'<path d="M{cx - .17 * k:.3f},{cy + .03 * k:.3f} Q{cx - .02 * k:.3f},{cy + .06 * k:.3f} {cx + .06 * k:.3f},{cy + .03 * k:.3f}" {s}/>',
              f'<path d="M{cx - .02 * k:.3f},{cy - .02 * k:.3f} C{cx - .04 * k:.3f},{cy - .12 * k:.3f} {cx + .06 * k:.3f},{cy - .17 * k:.3f} {cx + .12 * k:.3f},{cy - .15 * k:.3f} '
              f'C{cx + .12 * k:.3f},{cy - .07 * k:.3f} {cx + .05 * k:.3f},{cy - .02 * k:.3f} {cx - .02 * k:.3f},{cy - .02 * k:.3f} Z" {s}/>']
    else:
        a = .14 * k
        g += [f'<rect x="{cx - a:.3f}" y="{cy - a:.3f}" width="{2 * a:.3f}" height="{2 * a:.3f}" {s}/>',
              f'<rect x="{cx - a:.3f}" y="{cy - a:.3f}" width="{2 * a:.3f}" height="{2 * a:.3f}" transform="rotate(45 {cx} {cy})" {s}/>',
              f'<circle cx="{cx}" cy="{cy}" r="{.06 * k:.3f}" {s}/>']
    return "".join(g)


def features(xs, cy, r=.3, label_pt=6.2):
    out = []
    for (kind, l1, l2), x in zip(FEATURES, xs):
        out.append(icon(kind, x, cy, r))
        out.append(text(x, cy + r + .17, l1, "PP", label_pt, LABEL, "middle", 500, .04))
        out.append(text(x, cy + r + .28, l2, "PP", label_pt, LABEL, "middle", 500, .04))
    return "".join(out)


def title_block(name, sub, uid, cx, y, max_w, max_pt=68, min_pt=42):
    """Foil title (one or two lines) + subtitle between double rules, centred on cx."""
    up = name.upper()
    pt, lines = max_pt, [up]
    while pt > min_pt and tw(up, "BD", pt, .02) > max_w:
        pt -= 1
    if tw(up, "BD", pt, .02) > max_w and " " in up:          # two lines
        words = up.split()
        best = min(range(1, len(words)), key=lambda i: abs(len(" ".join(words[:i])) - len(" ".join(words[i:]))))
        lines = [" ".join(words[:best]), " ".join(words[best:])]
        pt = max_pt
        while pt > 30 and max(tw(l, "BD", pt, .02) for l in lines) > max_w:
            pt -= 1
    out = []
    for i, l in enumerate(lines):
        out.append(text(cx, y + i * pt * PT * 1.02, l, "BD", pt, f"url(#foil{uid})", "middle", 600, .02))
    y += (len(lines) - 1) * pt * PT * 1.02
    width = max(tw(l, "BD", pt, .02) for l in lines)
    sp = 21
    while tw(sub, "FR", sp) > width * .8 and sp > 12:
        sp -= .5
    sy = y + .5
    sw = tw(sub, "FR", sp)
    out.append(text(cx, sy, sub, "FR", sp, f"url(#foil{uid})", "middle", 700))
    x0, x1 = cx - width / 2, cx + width / 2
    gap = .1
    for dy, inset in ((-.07, .25), (-.025, 0)):
        ry = sy + dy
        out.append(f'<path d="M{x0 + inset:.3f},{ry:.3f} H{cx - sw / 2 - gap:.3f} M{cx + sw / 2 + gap:.3f},{ry:.3f} H{x1 - inset:.3f}" '
                   f'stroke="{INK}" stroke-width=".014"/>')
    return "".join(out), sy


def photo_panel(book, uid, x0=5.53, y0=.86, x1=10.35, y1=11.66):
    clip = f"panel{uid}"
    out = [f'<defs><clipPath id="{clip}"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx=".1"/></clipPath></defs>']
    photo = os.path.join(PHOTOS, f"{book['id']}.jpg")
    if os.path.exists(photo):
        inner = f'<image href="file://{photo}" x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" preserveAspectRatio="xMidYMid slice"/>'
    else:   # room wall with an arched opening and the curtain, in the book's own colour
        tone = mix(ladder_color(book["cat"]), "#C9C1A9", .12 + (book["seq"] % 5) * .06)
        ax0, ax1, ay0 = x0 + .32, x1 + .75, y0 + .35
        r = (ax1 - ax0) / 2
        arch = f"M{ax0},{y1} L{ax0},{ay0 + r} A{r},{r} 0 0 1 {ax1},{ay0 + r} L{ax1},{y1} Z"
        aclip = f"arch{uid}"
        inner = (f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#E4DDD2"/>'
                 f'<defs><clipPath id="{aclip}"><path d="{arch}"/></clipPath></defs>'
                 f'<g clip-path="url(#{aclip})">{drape(ax0, ay0, ax1 - ax0, y1 - ay0, tone, sheer=book["cat"] == "sheer")}</g>'
                 f'<path d="{arch}" fill="none" stroke="#F3EEE6" stroke-width=".09"/>'
                 f'<path d="{arch}" fill="none" stroke="#000" stroke-opacity=".08" stroke-width=".02" transform="translate(.05 0)"/>')
    out.append(f'<g clip-path="url(#{clip})">{inner}'
               f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#light{uid})"/></g>')
    out.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx=".1" fill="none" stroke="#FFFFFF" stroke-opacity=".5" stroke-width=".02"/>')
    return "".join(out)


def subtitle(book):
    return SUBTITLE.get(book["id"], book["line"])


# ---------------------------------------------------------------- covers
def front_svg(book):
    uid = book["id"].replace("-", "")
    tb, _ = title_block(book["name"], subtitle(book), uid, 2.85, 2.05, 4.55)
    art = (defs(uid) + linen(uid) + tb + photo_panel(book, uid) +
           features([1.09, 2.14, 3.1, 4.12], 11.12) + corner(uid) + corner(uid, True))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" style="width:100%;height:100%;display:block">{art}</svg>'


def back_svg(book, about, rows):
    uid = book["id"].replace("-", "") + "b"
    cx = W / 2
    out = [defs(uid), linen(uid)]
    out.append(text(cx, 1.15, "THE COLLECTION", "PP", 8.5, PLUM, "middle", 600, .35))
    tb, sy = title_block(book["name"], subtitle(book), uid, cx, 2.0, 5.2, max_pt=50)
    out.append(tb)
    # about
    y = sy + .75
    for line in about:
        out.append(text(cx, y, line, "CGI", 17, INK, "middle"))
        y += .3
    # specification plate
    py0 = y + .25
    ph = .55 + len(rows) * .42
    out.append(f'<rect x="1.55" y="{py0}" width="{W - 3.1}" height="{ph}" rx=".08" fill="{LINEN_LT}" fill-opacity=".55" stroke="{INK}" stroke-opacity=".25" stroke-width=".01"/>')
    out.append(text(cx, py0 + .38, "SPECIFICATIONS", "PP", 7.5, PLUM, "middle", 600, .35))
    ry = py0 + .82
    for i, (k, v) in enumerate(rows):
        out.append(text(cx - .15, ry, k.upper(), "PP", 7.2, LABEL, "end", 500, .12))
        out.append(text(cx + .15, ry, v, "PP", 10, INK, "start", 400))
        if i < len(rows) - 1:
            out.append(f'<path d="M2.0,{ry + .16:.3f} H{W - 2.0}" stroke="{INK}" stroke-opacity=".15" stroke-width=".008"/>')
        ry += .42
    # features
    fy = py0 + ph + .9
    out.append(features([cx - 3.0, cx - 1.0, cx + 1.0, cx + 3.0], fy, .33, 6.6))
    # shade-number note + dealer stamp
    ny = fy + 1.15
    out.append(text(cx, ny, "Every shade is numbered on its swatch - quote the shade number when you order.", "PP", 8.5, LABEL, "middle", 400))
    out.append(text(cx, ny + .22, "Colours may vary slightly in print; always choose from the actual swatch.", "PP", 8.5, LABEL, "middle", 400))
    out.append(f'<rect x="{cx - 1.9}" y="{ny + .5:.3f}" width="3.8" height="{12.25 - ny - .5:.3f}" rx=".08" fill="none" '
               f'stroke="{INK}" stroke-opacity=".45" stroke-width=".012" stroke-dasharray=".06 .05"/>')
    out.append(text(cx, ny + .78, "DEALER / SHOWROOM STAMP", "PP", 6.8, LABEL, "middle", 500, .3))
    out.append(corner(uid) + corner(uid, True))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" style="width:100%;height:100%;display:block">{"".join(out)}</svg>'


def spine_svg(book, d_in):
    uid = book["id"].replace("-", "") + "s"
    t = text(d_in / 2, H / 2, book["name"].upper(), "BD", 13, f"url(#foil{uid})", "middle", 600, .15,
             extra=f'transform="rotate(90 {d_in / 2} {H / 2})" dominant-baseline="middle"')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {d_in} {H}" preserveAspectRatio="none" style="width:100%;height:100%;display:block">'
            f'{defs(uid)}{linen(uid, d_in, H)}<rect width="{d_in}" height="{H}" fill="#000" opacity=".06"/>{t}</svg>')


# ---------------------------------------------------------------- 3D scenes
SCENE_CSS = """
html,body{margin:0;padding:0}
.scene{position:absolute;inset:0;perspective:4200px}
.book{position:absolute;transform-style:preserve-3d}
.face{position:absolute;left:0;top:0;backface-visibility:hidden;overflow:hidden}
.face.front::after{content:"";position:absolute;inset:0;background:linear-gradient(100deg,rgba(255,255,255,.10),rgba(255,255,255,0) 40%,rgba(0,0,0,.08))}
.face.spine::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.30),rgba(0,0,0,.12) 40%,rgba(0,0,0,.22))}
.edge{background:linear-gradient(90deg,#E9E2D4,#F6F1E8 40%,#DCD3C2)}
.edge::after{content:"";position:absolute;inset:0;background:repeating-linear-gradient(90deg,rgba(0,0,0,.07) 0 1px,transparent 1px 5px)}
.top{background:linear-gradient(90deg,#EEE8DC,#F7F3EC 50%,#E4DCCD);box-shadow:inset 0 0 0 3px #B3AB92}
.rope{position:absolute;overflow:visible}
.shadow{position:absolute;border-radius:50%;background:rgba(35,28,20,.42);filter:blur(26px)}
"""


def rope_svg(w_px, h_px):
    a, b = w_px * .37, w_px * .63
    d = f"M{a},{h_px} C{a - w_px * .02},{h_px * .15} {b + w_px * .02},{h_px * .15} {b},{h_px}"
    sw = max(w_px * .016, 3)
    return (f'<svg width="{w_px}" height="{h_px}" style="overflow:visible">'
            f'<path d="{d}" fill="none" stroke="#0E0E0E" stroke-width="{sw:.1f}" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="#5A5A5A" stroke-width="{sw * .35:.1f}" stroke-dasharray="{sw * .5:.1f} {sw * .7:.1f}" stroke-linecap="round"/>'
            f'</svg>')


def book3d(book, x, y, s, ry, d_in=1.0, rope=True):
    Wp, Hp, D = W * s, H * s, d_in * s
    rh = 1.7 * s
    rope_html = (f'<div class="rope" style="left:0;top:{-rh}px;width:{Wp}px;height:{rh}px;transform:translateZ(0px)">{rope_svg(Wp, rh)}</div>'
                 if rope else "")
    return f"""<div class="book" style="left:{x}px;top:{y}px;width:{Wp}px;height:{Hp}px;transform:rotateY({ry}deg)">
  {rope_html}
  <div class="face front" style="width:{Wp}px;height:{Hp}px;transform:translateZ({D / 2}px)">{front_svg(book)}</div>
  <div class="face spine" style="width:{D}px;height:{Hp}px;left:{(Wp - D) / 2}px;transform:rotateY(-90deg) translateZ({Wp / 2}px)">{spine_svg(book, d_in)}</div>
  <div class="face edge" style="width:{D}px;height:{Hp}px;left:{(Wp - D) / 2}px;transform:rotateY(90deg) translateZ({Wp / 2 - 2}px)"></div>
  <div class="face top" style="width:{Wp}px;height:{D}px;top:{(Hp - D) / 2}px;transform:rotateX(90deg) translateZ({Hp / 2}px)"></div>
</div>"""


def html(body, w, h, extra=""):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}{SCENE_CSS}{extra}'
            f'body{{width:{w}px;height:{h}px;overflow:hidden;position:relative}}</style></head><body>{body}</body></html>')


def backdrop(w, h, horizon):
    return (f'<div style="position:absolute;left:0;top:0;width:{w}px;height:{horizon}px;'
            f'background:radial-gradient(ellipse at 40% 30%,#F4F0E9,#E7E0D5 55%,#D8CFC1)"></div>'
            f'<div style="position:absolute;left:0;top:{horizon}px;width:{w}px;height:{h - horizon}px;'
            f'background:linear-gradient(180deg,#CBBFAC,#DDD4C6 35%,#E9E3D9)"></div>')


RY = 26          # every book turned the same way


def catalogue_set(books):
    w, h, horizon = 3200, 1800, 1400
    s = 68
    Hp = H * s
    floor = horizon + 30
    parts = [backdrop(w, h, horizon), '<div class="scene" style="perspective-origin:50% 8%">']
    xs = [230, 930, 1630, 2330]
    for x in xs:
        parts.append(f'<div class="shadow" style="left:{x - 10}px;top:{floor - 34}px;width:{W * s * .98}px;height:70px"></div>')
    for b, x in zip(books, xs):
        parts.append(book3d(b, x, floor - Hp, s, RY))
    parts.append("</div>")
    return html("".join(parts), w, h)


def all_in_one(books):
    w, h = 3200, 2200
    s = 30
    Wp, Hp = W * s, H * s
    per_row, gap = 7, 92
    rows = [books[i:i + per_row] for i in range(0, len(books), per_row)]
    row_h = Hp + 1.7 * s + 150
    top0 = (h - len(rows) * row_h) / 2 + 1.7 * s + 40
    parts = [f'<div style="position:absolute;inset:0;background:radial-gradient(ellipse at 45% 35%,#F3EFE8,#E3DBCF 65%,#D4CABA)"></div>']
    for r, row in enumerate(rows):
        base = top0 + r * row_h + Hp
        total = len(row) * Wp + (len(row) - 1) * gap
        x0 = (w - (per_row * Wp + (per_row - 1) * gap)) / 2
        # shelf
        parts.append(f'<div style="position:absolute;left:{x0 - 90}px;top:{base}px;width:{per_row * Wp + (per_row - 1) * gap + 180}px;height:26px;'
                     f'background:linear-gradient(180deg,#F7F3EC,#E2D9CA);box-shadow:0 22px 34px rgba(40,30,20,.28)"></div>')
        parts.append(f'<div class="scene" style="perspective-origin:50% {(base - Hp) / h * 100 - 6:.1f}%">')
        for i, b in enumerate(row):
            x = x0 + i * (Wp + gap)
            parts.append(f'<div class="shadow" style="left:{x}px;top:{base - 16}px;width:{Wp}px;height:30px;filter:blur(14px)"></div>')
            parts.append(book3d(b, x, base - Hp, s, RY))
        parts.append("</div>")
    return html("".join(parts), w, h)


def flat(svg_markup, dpi=150):
    w, h = round(W * dpi), round(H * dpi)
    return html(f'<div style="width:{w}px;height:{h}px">{svg_markup}</div>', w, h), w, h


NEO_LUNA_ABOUT = ["A 100% blackout curtain fabric with a soft, textured face.",
                  "It shuts out light completely for restful bedrooms, media rooms",
                  "and nurseries, and drapes as gracefully as a decorative curtain."]
NEO_LUNA_ROWS = [("Category", "100% Blackout Curtain"), ("Light control", "Blocks light completely"),
                 ("Main shades", "101 - 106"), ("Book", "3-fold swatch book"),
                 ("Ideal for", "Bedrooms  ·  Media rooms  ·  Nurseries")]


def main():
    from playwright.sync_api import sync_playwright
    os.makedirs(OUT, exist_ok=True)
    books = ordered_books()
    by_id = {b["id"]: b for b in books}
    neo = by_id["neo-luna"]
    jobs = []
    page_, w, h = flat(back_svg(neo, NEO_LUNA_ABOUT, NEO_LUNA_ROWS)); jobs.append(("01_Neo_Luna_Back_Cover.png", page_, w, h))
    page_, w, h = flat(front_svg(neo)); jobs.append(("02_Neo_Luna_Front_Cover.png", page_, w, h))
    four = [by_id[i] for i in ("neo-luna", "virinche", "texture-coated", "breeze")]
    jobs.append(("03_Catalogue_Set.png", catalogue_set(four), 3200, 1800))
    jobs.append(("04_All_Collections_In_One.png", all_in_one(books), 3200, 2200))
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=chromium())
        for name, markup, w, h in jobs:
            pg = br.new_page(viewport={"width": w, "height": h})
            tmp = os.path.join(OUT, name + ".html")
            open(tmp, "w").write(markup)
            pg.goto("file://" + tmp)
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(400)
            pg.screenshot(path=os.path.join(OUT, name))
            os.remove(tmp)
            pg.close()
            print("Wrote", os.path.join(OUT, name))
        br.close()


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------- transparent strips for print
def strip_html(rows, w, h, s):
    """rows = [(floor_y, [(book, x), ...]), ...] on a transparent page, all books tilted RY."""
    Hp = H * s
    parts = []
    k = 0
    for ri, (floor, items) in enumerate(rows):
        parts.append('<div class="scene" style="perspective:14000px;perspective-origin:50% 5%">')
        for b, x in items:
            parts.append(f'<div class="shadow" data-i="{k}" style="left:{x + W * s * .04}px;top:{floor - s * .45}px;width:{W * s * .92}px;'
                         f'height:{s * .9}px;filter:blur({s * .35}px);background:rgba(35,28,20,.32)"></div>')
            parts.append(book3d(b, x, floor - Hp, s, RY).replace('<div class="book"', f'<div class="book" data-i="{k}" data-row="{ri}"', 1))
            k += 1
        parts.append("</div>")
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}{SCENE_CSS}'
            f'html,body{{background:transparent}} body{{width:{w}px;height:{h}px;overflow:hidden;position:relative}}</style></head>'
            f'<body>{"".join(parts)}</body></html>')


def four_books_html(books4):
    """4 catalogue books in one row, tilted one way: 2400 x 860 px (2.79 : 1)."""
    s, floor = 48, 812
    xs = [70, 620, 1170, 1720]
    return strip_html([(floor, list(zip(books4, xs)))], 2400, 860, s), 2400, 860


def twenty_books_html(books20):
    """Two rows of 10 books, tilted one way: 3000 x 950 px (3.16 : 1)."""
    s = 24
    xs = [70 + i * 284 for i in range(10)]
    rows = [(430, list(zip(books20[:10], xs))), (915, list(zip(books20[10:20], xs)))]
    return strip_html(rows, 3000, 950, s), 3000, 950


MEASURE_JS = """() => {
  const out = [];
  document.querySelectorAll('.book').forEach(b => {
    let r = null;
    b.querySelectorAll('.face.front, .face.spine, .face.top, .rope svg').forEach(el => {
      const q = el.getBoundingClientRect();
      if (!q.width) return;
      r = r ? {l: Math.min(r.l, q.left), t: Math.min(r.t, q.top), r: Math.max(r.r, q.right), b: Math.max(r.b, q.bottom)}
            : {l: q.left, t: q.top, r: q.right, b: q.bottom};
    });
    out.push({i: +b.dataset.i, row: +b.dataset.row, l: r.l, t: r.t, r: r.r, b: r.b});
  });
  return out;
}"""

SHIFT_JS = """(moves) => {
  for (const m of moves) {
    document.querySelectorAll('[data-i="' + m.i + '"]').forEach(el => {
      el.style.left = (parseFloat(el.style.left) + m.dx) + 'px';
      el.style.top = (parseFloat(el.style.top) + m.dy) + 'px';
    });
  }
}"""


def even_out(pg, w, h, gap_ratio=.07):
    """Equal gaps between the tilted books of every row, each row centred; the whole
    picture centred vertically.  Two passes (perspective makes a shift slightly non-linear)."""
    for _ in range(3):
        boxes = pg.evaluate(MEASURE_JS)
        moves = []
        for row in sorted({b["row"] for b in boxes}):
            items = sorted([b for b in boxes if b["row"] == row], key=lambda b: b["l"])
            widths = [b["r"] - b["l"] for b in items]
            gap = gap_ratio * sum(widths) / len(widths)
            total = sum(widths) + gap * (len(items) - 1)
            x = (w - total) / 2
            for b, bw in zip(items, widths):
                moves.append(dict(i=b["i"], dx=x - b["l"], dy=0))
                x += bw + gap
        top, bottom = min(b["t"] for b in boxes), max(b["b"] for b in boxes)
        dy = (h - (bottom - top)) / 2 - top
        for m in moves:
            m["dy"] = dy
        pg.evaluate(SHIFT_JS, moves)
    boxes = pg.evaluate(MEASURE_JS)
    return boxes


def render_pngs(jobs):
    """jobs = [(path, html, w, h)] -> transparent PNGs; tilted-book strips are evened out,
    centred and cropped to the books with equal padding on every side."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=chromium())
        for path, markup, w, h in jobs:
            pg = br.new_page(viewport={"width": w, "height": h})
            tmp = path + ".html"
            open(tmp, "w").write(markup)
            pg.goto("file://" + tmp)
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(300)
            boxes = even_out(pg, w, h)
            pg.wait_for_timeout(150)
            l, t = min(b["l"] for b in boxes), min(b["t"] for b in boxes)
            r, bt = max(b["r"] for b in boxes), max(b["b"] for b in boxes)
            pad = max(24, min(60, (r - l) * .02))
            clip = dict(x=max(0, l - pad), y=max(0, t - pad), width=min(w, r + pad) - max(0, l - pad), height=min(h, bt + pad) - max(0, t - pad))
            pg.screenshot(path=path, omit_background=True, clip=clip)
            os.remove(tmp)
            pg.close()
        br.close()
