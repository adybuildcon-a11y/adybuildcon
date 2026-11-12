"""Vector artwork (SVG, inch units) for covers, inside liners and the master case."""

import os
from functools import lru_cache

from PIL import ImageFont

from data import LADDER, LEVEL, P
from layout import panel_widths, panel_x, content_box, ladder_color

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "assets", "fonts")

LINEN, LINEN_DK, INK, MUTED, BRASS = "#DCD2BF", "#CBBEA6", "#2B2723", "#6E655A", "#8C6B36"
PAPER, CELL, GUIDE, CREAM = "#F6F2EA", "#ECE5D8", "#B4A894", "#F4EEE3"
PT = 1 / 72

FONT_CSS = """
@font-face{font-family:CG;src:url(FONTDIR/CormorantGaramond-500.ttf);font-weight:500}
@font-face{font-family:CG;src:url(FONTDIR/CormorantGaramond-600.ttf);font-weight:600}
@font-face{font-family:CG;src:url(FONTDIR/CormorantGaramond-700.ttf);font-weight:700}
@font-face{font-family:CG;src:url(FONTDIR/CormorantGaramond-500i.ttf);font-weight:500;font-style:italic}
@font-face{font-family:CZ;src:url(FONTDIR/Cinzel-500.ttf);font-weight:500}
@font-face{font-family:CZ;src:url(FONTDIR/Cinzel-600.ttf);font-weight:600}
@font-face{font-family:PP;src:url(FONTDIR/Poppins-Light.ttf);font-weight:300}
@font-face{font-family:PP;src:url(FONTDIR/Poppins-Regular.ttf);font-weight:400}
@font-face{font-family:PP;src:url(FONTDIR/Poppins-Medium.ttf);font-weight:500}
@font-face{font-family:PP;src:url(FONTDIR/Poppins-SemiBold.ttf);font-weight:600}
""".replace("FONTDIR", "file://" + FONTS)

FONT_FILES = {("CG", 600): "CormorantGaramond-600.ttf", ("CG", 500): "CormorantGaramond-500.ttf",
              ("CZ", 500): "Cinzel-500.ttf", ("CZ", 600): "Cinzel-600.ttf",
              ("PP", 400): "Poppins-Regular.ttf", ("PP", 500): "Poppins-Medium.ttf"}


@lru_cache(None)
def _font(fam, wt):
    return ImageFont.truetype(os.path.join(FONTS, FONT_FILES[(fam, wt)]), 1000)


def text_w(s, fam, wt, size_in, track=0.0):
    """Advance width in inches of s at size_in (inches), track = letter-spacing in em."""
    return _font(fam, wt).getlength(s) / 1000 * size_in + track * size_in * max(len(s) - 1, 0)


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def T(x, y, s, fam="PP", wt=400, pt=8, fill=INK, anchor="start", track=0.0, italic=False, extra=""):
    st = "font-style:italic;" if italic else ""
    ls = f"letter-spacing:{track * pt * PT:.4f}px;" if track else ""
    return (f'<text x="{x:.4f}" y="{y:.4f}" font-family="{fam}" font-weight="{wt}" font-size="{pt * PT:.4f}" '
            f'fill="{fill}" text-anchor="{anchor}" style="{st}{ls}" {extra}>{esc(s)}</text>')


def Ttr(x, y, s, fam, wt, pt, fill, anchor, track):
    """Tracked text that stays truly centred / right aligned (SVG adds tracking after the last glyph)."""
    w = text_w(s, fam, wt, pt * PT, track)
    if anchor == "middle":
        x -= w / 2
    elif anchor == "end":
        x -= w
    return T(x, y, s, fam, wt, pt, fill, "start", track)


def mix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


_uid = [0]


def uid(p):
    _uid[0] += 1
    return f"{p}{_uid[0]}"


# ---------------------------------------------------------------- photo / drape placeholder
def photo_path(book_id):
    for ext in ("jpg", "jpeg", "png"):
        f = os.path.join(HERE, "assets", "photos", f"{book_id}.{ext}")
        if os.path.exists(f):
            return f
    return None


def drape(x, y, w, h, tone, sheer=False):
    """Vector curtain scene used until a real photo is supplied."""
    g1, g2, g3, g4, sh = uid("wall"), uid("fold"), uid("floor"), uid("glow"), uid("shadow")
    light, dark = mix(tone, "#FFFFFF", .55), mix(tone, "#000000", .28)
    stops, n = [], 9
    for k in range(n + 1):
        c = light if k % 2 == 0 else dark
        stops.append(f'<stop offset="{k / n:.3f}" stop-color="{c}"/>')
        if k < n:
            stops.append(f'<stop offset="{(k + .5) / n:.3f}" stop-color="{mix(light, dark, .45)}"/>')
    cx0, cx1, fy = x + w * .34, x + w * 1.02, y + h * .865
    step = (cx1 - cx0) / 9
    hem = " ".join(f"Q{cx1 - (i + .5) * step:.3f},{fy + (.07 if i % 2 else -.02):.3f} {cx1 - (i + 1) * step:.3f},{fy - .03:.3f}" for i in range(9))
    lx1 = x + w * .13
    op = .72 if sheer else 1
    return f"""<defs>
      <linearGradient id="{g1}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EFE9DF"/><stop offset="1" stop-color="#DED4C4"/></linearGradient>
      <linearGradient id="{g2}" x1="0" y1="0" x2="1" y2="0">{''.join(stops)}</linearGradient>
      <linearGradient id="{g3}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#CFC3AE"/><stop offset="1" stop-color="#B9AA92"/></linearGradient>
      <radialGradient id="{g4}" cx=".25" cy=".25" r=".7"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".75"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>
      <linearGradient id="{sh}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".16"/></linearGradient>
    </defs>
    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{g1})"/>
    <rect x="{x + w * .10}" y="{y + h * .10}" width="{w * .30}" height="{h * .62}" fill="#F7F4EE"/>
    <path d="M{x + w * .25},{y + h * .10} v{h * .62} M{x + w * .10},{y + h * .41} h{w * .30}" stroke="#E2DBCF" stroke-width=".03"/>
    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{g4})"/>
    <rect x="{x}" y="{fy}" width="{w}" height="{y + h - fy}" fill="url(#{g3})"/>
    <rect x="{x}" y="{fy - .03}" width="{w}" height=".03" fill="#C2B49C"/>
    <ellipse cx="{(cx0 + cx1) / 2}" cy="{fy + .05}" rx="{(cx1 - cx0) * .55}" ry=".09" fill="#000" opacity=".10"/>
    <rect x="{cx0 - .35}" y="{y}" width=".35" height="{fy - y}" fill="url(#{sh})"/>
    <g opacity="{op}">
      <path d="M{cx0},{y} H{cx1} V{fy - .03} {hem} Z" fill="url(#{g2})"/>
      <path d="M{x - .02},{y} H{lx1} V{fy - .02} H{x - .02} Z" fill="url(#{g2})"/>
      <rect x="{cx0}" y="{y}" width="{cx1 - cx0}" height=".16" fill="{dark}" opacity=".35"/>
    </g>"""


def photo_or_drape(book, x, y, w, h):
    p = photo_path(book["id"])
    if p:
        return f'<image href="file://{p}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/>', True
    tone = mix(ladder_color(book["cat"]), LINEN, .25 + (book["seq"] % 4) * .07)
    return drape(x, y, w, h, tone, sheer=book["cat"] == "sheer"), False


def arch_path(x0, y0, x1, y1):
    r = (x1 - x0) / 2
    return f"M{x0},{y1} L{x0},{y0 + r} A{r},{r} 0 0 1 {x1},{y0 + r} L{x1},{y1} Z"


# ---------------------------------------------------------------- small graphics
def ladder_mini(x, y, cat, scale=1.0):
    """6-step light-control scale; steps up to the book's level are filled."""
    lv, s = LEVEL[cat], scale
    out = [Ttr(x, y - .07 * s, "LIGHT CONTROL", "CZ", 500, 5.5 * s, MUTED, "start", .18)]
    for i, (k, *_r, col) in enumerate(LADDER):
        bx = x + i * .2 * s
        filled = i == lv
        out.append(f'<rect x="{bx:.3f}" y="{y:.3f}" width="{.16 * s:.3f}" height="{.07 * s:.3f}" '
                   f'fill="{col if filled else "none"}" stroke="{col}" stroke-width="{.012 * s:.3f}"/>')
    return "".join(out)


def ladder_full(x, y, w, cat):
    lv, n = LEVEL[cat], len(LADDER)
    cw = w / n
    out = []
    for i, (k, name, desc, col) in enumerate(LADDER):
        on = i == lv
        out.append(f'<rect x="{x + i * cw + .02:.3f}" y="{y:.3f}" width="{cw - .04:.3f}" height=".1" fill="{col}" opacity="{1 if on else .28}"/>')
        out.append(T(x + i * cw + cw / 2, y + .26, name.upper(), "CZ", 600 if on else 500, 5.6, INK if on else MUTED, "middle"))
    return "".join(out)


def fit_name(lines, max_w, max_pt, fam="CG", wt=600, track=.02):
    pt = max_pt
    while pt > 14 and max(text_w(l, fam, wt, pt * PT, track) for l in lines) > max_w:
        pt -= .5
    return pt


def name_lines(name):
    w = name.upper().split()
    if len(w) == 1:
        return w
    if len(w) == 2:
        return w
    return [" ".join(w[:2]), " ".join(w[2:])]


# ---------------------------------------------------------------- outside panels
def cover_panel(x0, pw, books, tab_right=True):
    """Front covering of a board: number, name, category, facts, light control, arch photo."""
    b0 = books[0]
    ax0, ax1, ay0, ay1 = x0 + pw * .475, x0 + pw - .62, .95, 10.6
    clip = uid("arch")
    photo, real = photo_or_drape(b0, ax0, ay0, ax1 - ax0, ay1 - ay0)
    col = ladder_color(b0["cat"])
    out = [f'<defs><clipPath id="{clip}"><path d="{arch_path(ax0, ay0, ax1, ay1)}"/></clipPath></defs>',
           f'<path d="{arch_path(ax0 - .13, ay0 - .13, ax1 + .13, ay1 + .13)}" fill="{CREAM}"/>',
           f'<g clip-path="url(#{clip})">{photo}</g>',
           f'<path d="{arch_path(ax0, ay0, ax1, ay1)}" fill="none" stroke="#FFFFFF" stroke-opacity=".55" stroke-width=".015"/>']
    lx, colw = x0 + .72, ax0 - .38 - (x0 + .72)
    nums = " · ".join(f"{b['seq']:02d}" for b in books)
    out.append(Ttr(lx, 1.32, f"NO. {nums}", "CZ", 500, 9, MUTED, "start", .3))
    # name block
    if len(books) == 1:
        lines = name_lines(b0["name"])
    else:
        lines = [books[0]["name"].upper(), "&", books[1]["name"].upper()]
    pt = fit_name([l for l in lines if l != "&"], colw, 46)
    y = 1.32 + .25 + pt * PT * .95
    for l in lines:
        if l == "&":
            out.append(T(lx, y - pt * PT * .25, "&", "CG", 500, pt * .6, BRASS, italic=True))
            y += pt * PT * .62
            continue
        out.append(T(lx, y, l, "CG", 600, pt, INK, track=.02))
        y += pt * PT * 1.0
    # rule + category
    cat_line = b0["line"] if len(books) == 1 else "Dimout"
    ry = y - pt * PT * .55 + .2
    cpt = 10.5
    while cpt > 7 and text_w(cat_line, "CZ", 600, cpt * PT, .06) > colw - .5:
        cpt -= .25
    cw = text_w(cat_line, "CZ", 600, cpt * PT, .06)
    out.append(f'<path d="M{lx},{ry} h{colw} M{lx},{ry + .05} h{colw}" stroke="{INK}" stroke-width=".008"/>')
    out.append(f'<rect x="{lx + (colw - cw) / 2 - .1}" y="{ry - .12}" width="{cw + .2}" height=".3" fill="{LINEN}"/>')
    out.append(Ttr(lx + colw / 2, ry + .025 + cpt * PT * .32, cat_line, "CZ", 600, cpt, INK, "middle", .06))
    # facts
    fy = 9.55
    shades = " + ".join(f"{b['shades']}" for b in books if b["shades"]) if any(b["shades"] for b in books) else None
    if shades:
        out.append(Ttr(lx, fy, f"{shades} SHADES", "CZ", 600, 9.5, INK, "start", .2))
    spec = [f'{b0["width"]}" WIDE' if b0["width"] else None, f'{b0["gsm"]} GSM' if b0["gsm"] and not b0.get("gsm_src") else None]
    spec = "  ·  ".join(s for s in spec if s)
    if spec and len(books) == 1:
        out.append(T(lx, fy + .2, spec, "PP", 400, 7.5, MUTED))
    out.append(ladder_mini(lx, 10.38, b0["cat"]))
    # index tab on the hinge edge
    tx = x0 + pw - .2 if tab_right else x0
    out.append(f'<rect x="{tx}" y="0" width=".2" height="{P["board_h"]}" fill="{col}"/>')
    out.append(T(tx + .1, 1.0, nums.replace(" · ", "·"), "CZ", 600, 7, "#FFFFFF", "middle",
                 extra=f'transform="rotate(90 {tx + .1} 1.0)" dominant-baseline="middle"'))
    return "".join(out), real


def back_panel(x0, pw, books, bind_right=True):
    """Outside of the binding panel: quiet spec plate (no brand)."""
    usable0, usable1 = (x0, x0 + pw - P["bind_margin"]) if bind_right else (x0 + P["bind_margin"], x0 + pw)
    cx = (usable0 + usable1) / 2
    out = [Ttr(cx, 4.2, "CURATED FABRICS COLLECTION", "CZ", 500, 7.5, MUTED, "middle", .35)]
    y = 4.95
    for b in books:
        out.append(T(cx, y, b["name"].upper(), "CG", 600, 26, INK, "middle", .02))
        out.append(Ttr(cx, y + .3, b["line"].upper(), "CZ", 500, 7.5, BRASS, "middle", .25))
        rows = [("Book", f'{b["seq"]:02d} of 20'), ("Shades", b["shades"] or "To be confirmed"),
                ("Main", ", ".join(s for s in b["mains"] if s) or "-"), ("Width", f'{b["width"]} in' if b["width"] else "-"),
                ("Weight", f'{b["gsm"]} GSM' if b["gsm"] else "-")]
        if b.get("comp"):
            rows.append(("Composition", b["comp"]))
        ty = y + .65
        for k, v in rows:
            out.append(T(cx - .08, ty, k.upper(), "PP", 500, 6.5, MUTED, "end"))
            out.append(T(cx + .08, ty, v, "PP", 400, 7.5, INK))
            ty += .21
        y = ty + .55
    out.append(f'<path d="M{cx - .5},{3.85} h1" stroke="{BRASS}" stroke-width=".01"/>')
    return "".join(out)


def plain_panel(x0, pw, books):
    b = books[0]
    return (f'<rect x="{x0 + pw / 2 - .4}" y="11.15" width=".8" height=".02" fill="{ladder_color(b["cat"])}"/>' +
            Ttr(x0 + pw / 2, 11.45, b["name"].upper(), "CZ", 500, 7, MUTED, "middle", .3))


def outside_art(bd):
    """Outside wrap viewed from outside: inside order reversed. Cover = outside of panel B."""
    fold = bd["fold"] or 2
    ws = panel_widths(fold)[::-1]
    xs, x = [], 0
    for w in ws:
        xs.append(x); x += w + P["hinge"]
    books = bd["books"]
    parts = []
    real = False
    if fold == 2:      # [B_out = cover | A_out = back]
        c, real = cover_panel(xs[0], ws[0], books)
        parts += [c, back_panel(xs[1], ws[1], books)]
    else:              # [C_out | B_out = cover | A_out = back]
        c, real = cover_panel(xs[1], ws[1], books)
        parts += [plain_panel(xs[0], ws[0], books), c, back_panel(xs[2], ws[2], books)]
    return "".join(parts), xs, ws, real


# ---------------------------------------------------------------- inside liner
def inside_art(bd):
    fold, books = bd["fold"], bd["books"]
    b = books[0]
    out, run = [], 0
    for i, pn in enumerate(bd["panels"]):
        x0 = panel_x(fold, i)
        pw = panel_widths(fold)[i]
        bx0, by0, bx1, by1 = content_box(fold, i)
        hy = P["margin"] + .5
        out.append(T(bx0, hy, b["name"].upper(), "CG", 600, 15, INK, track=.03))
        if pn["kind"] == "hero":
            tag = "MAIN FABRIC" if len(pn["shades"]) == 1 else "MAIN FABRICS"
        elif pn.get("title"):
            tag = pn["title"].upper()
        else:
            tag = f"SHADES {run + 1:02d} – {run + len(pn['shades']):02d}"
        if pn["kind"] == "swatch":
            run += len(pn["shades"])
        out.append(Ttr(bx1, hy, tag, "CZ", 600, 7, BRASS, "end", .25))
        out.append(f'<path d="M{bx0},{hy + .16} H{bx1}" stroke="{INK}" stroke-width=".006"/>')
        for k, ((cx, cy, cw, ch), shade) in enumerate(zip(pn["cells"], pn["shades"]), 1):
            out.append(f'<rect x="{cx:.3f}" y="{cy:.3f}" width="{cw:.3f}" height="{ch:.3f}" fill="{CELL}" stroke="{GUIDE}" stroke-width=".007"/>')
            ly = cy + ch + (.19 if pn["kind"] == "swatch" else .23)
            slot = f'{pn["letter"]}{k:02d}'
            if pn["kind"] == "hero":
                lab = f"MAIN · {shade}" if shade else "MAIN · NO. ______"
                out.append(T(cx, ly, lab, "CZ", 600, 8.5, INK, track=.12))
            else:
                if shade and shade in b["mains"]:
                    out.append(T(cx, ly, f"MAIN · {shade}", "CZ", 600, 7.5, INK, track=.08))
                elif shade:
                    out.append(T(cx, ly, shade, "PP", 500, 7.5, INK))
                else:
                    out.append(T(cx, ly, "No.", "PP", 400, 7, MUTED))
                    out.append(f'<path d="M{cx + .24},{ly + .015} h{min(.85, cw - .6):.3f}" stroke="{GUIDE}" stroke-width=".007"/>')
            out.append(T(cx + cw, ly, slot, "PP", 400, 5.5, GUIDE, "end"))
        if pn["kind"] == "hero":
            out.append(hero_spec(pn["spec_box"], b))
        fy = P["board_h"] - P["margin"] - .05
        out.append(T(bx0, fy, f'NO. {b["seq"]:02d}  ·  {b["name"].upper()}  ·  PANEL {pn["letter"]}', "PP", 400, 5.5, MUTED, track=.1))
    return "".join(out)


def hero_spec(box, b):
    x0, y0, x1, y1 = box
    out = [T(x0, y0 + .32, b["name"].upper(), "CG", 600, 24, INK, track=.02)]
    if b["line"].lower() != b["name"].lower():
        out.append(Ttr(x0, y0 + .58, b["line"].upper(), "CZ", 500, 7.5, BRASS, "start", .25))
    rows = [("Shades in book", b["shades"]), ("Main shade", ", ".join(s for s in b["mains"] if s) or "-"),
            ("Width", f'{b["width"]} in' if b["width"] else "-"), ("Weight", f'{b["gsm"]} GSM' if b["gsm"] else "-")]
    if b.get("comp"):
        rows.append(("Composition", b["comp"]))
    half = (x1 - x0) / 2
    for i, (k, v) in enumerate(rows):
        cx = x0 + (i % 2) * half
        ry = y0 + .92 + (i // 2) * .34
        out.append(T(cx, ry, k.upper(), "PP", 500, 5.8, MUTED, track=.1))
        out.append(T(cx, ry + .15, str(v), "PP", 400, 8, INK))
    out.append(ladder_full(x0, y1 - .52, x1 - x0, b["cat"]))
    return "".join(out)


# ---------------------------------------------------------------- master case
def master_front(x0, w, h, sample_books):
    cx = x0 + w / 2
    out = [Ttr(cx, 1.45, "TRENDING EDIT", "CZ", 600, 11, BRASS, "middle", .5),
           T(cx, 2.35, "Curated Fabrics", "CG", 600, 58, INK, "middle"),
           T(cx, 3.12, "Collection", "CG", 600, 58, INK, "middle"),
           T(cx, 3.62, "The most-demanded curtain fabrics, curated in one book", "CG", 500, 16, MUTED, "middle", italic=True)]
    ax0, ax1, ay0, ay1 = cx - 2.55, cx + 2.55, 4.05, 11.0
    clip = uid("march")
    p = photo_path("master")
    if p:
        photo = f'<image href="file://{p}" x="{ax0}" y="{ay0}" width="{ax1 - ax0}" height="{ay1 - ay0}" preserveAspectRatio="xMidYMid slice"/>'
    else:
        photo = drape(ax0, ay0, ax1 - ax0, ay1 - ay0, mix("#B79C7A", LINEN, .2))
    out += [f'<defs><clipPath id="{clip}"><path d="{arch_path(ax0, ay0, ax1, ay1)}"/></clipPath></defs>',
            f'<path d="{arch_path(ax0 - .15, ay0 - .15, ax1 + .15, ay1 + .15)}" fill="{CREAM}"/>',
            f'<g clip-path="url(#{clip})">{photo}</g>']
    out.append(Ttr(cx, 11.68, "20 COLLECTIONS  ·  SHEER TO BLACKOUT", "CZ", 600, 9, INK, "middle", .3))
    n, cw = len(LADDER), .95
    sx = cx - n * cw / 2
    for i, (k, name, desc, col) in enumerate(LADDER):
        out.append(f'<rect x="{sx + i * cw + .06}" y="11.9" width="{cw - .12}" height=".09" fill="{col}"/>')
        out.append(T(sx + i * cw + cw / 2, 12.17, name.upper(), "CZ", 500, 5.5, MUTED, "middle"))
    return "".join(out), bool(p)


def master_back(x0, w, h, books):
    cx = x0 + w / 2
    out = [Ttr(cx, 1.5, "THE COLLECTIONS", "CZ", 600, 10, BRASS, "middle", .45),
           T(cx, 2.15, "Sheer to Blackout", "CG", 600, 30, INK, "middle"),
           T(cx, 2.5, "Arranged by light control, then by fabric weight", "CG", 500, 13, MUTED, "middle", italic=True)]
    y, lx = 3.2, x0 + 1.6
    last = None
    for b in books:
        if b["cat"] != last:
            name = [n for k, n, *_ in LADDER if k == b["cat"]][0]
            y += .16
            out.append(f'<rect x="{lx}" y="{y - .11}" width=".18" height=".12" fill="{ladder_color(b["cat"])}"/>')
            out.append(Ttr(lx + .3, y, name.upper(), "CZ", 600, 7, MUTED, "start", .3))
            y += .3
            last = b["cat"]
        out.append(T(lx + .3, y, f'{b["seq"]:02d}', "CZ", 600, 9, BRASS))
        out.append(T(lx + .75, y, b["name"], "CG", 600, 15, INK))
        out.append(T(x0 + w - 1.6, y, b["line"], "PP", 400, 7.5, MUTED, "end"))
        y += .33
    return "".join(out)


def spine_art(x0, w, h):
    cx = x0 + w / 2
    out = [T(cx, h / 2, "CURATED FABRICS COLLECTION", "CZ", 600, 16 if w > 1.5 else 11, INK, "middle",
             extra=f'transform="rotate(90 {cx} {h / 2})" dominant-baseline="middle" style="letter-spacing:{.3 * 16 * PT:.4f}px"')]
    n = len(LADDER)
    for i, (k, *_r, col) in enumerate(LADDER):
        out.append(f'<rect x="{x0 + w * .2}" y="{h - 2.2 + i * .2}" width="{w * .6}" height=".12" fill="{col}"/>')
    return "".join(out)
