"""Vector artwork (SVG, inch units) for covers, inside liners and the master case."""

import os
from functools import lru_cache

from PIL import ImageFont

from data import LADDER, LEVEL, P
from layout import panel_widths, panel_x, content_box, ladder_color, WF_LABEL

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
    elif len(books) == 2:
        lines = [books[0]["name"].upper(), "&", books[1]["name"].upper()]
    else:                                                  # Stand A: three books
        lines = [b["name"].upper() for b in books[:-1]] + ["&", books[-1]["name"].upper()]
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
    cat_line = b0["line"] if len(books) == 1 else ("Three Collections" if len(books) > 2 else "Dimout")
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


CAT_DIR = os.path.join(HERE, "assets", "catalogue")


def board_img(bd):
    return os.path.join(CAT_DIR, f"board-{bd['id']}.png")


def all_img():
    return os.path.join(CAT_DIR, "all-books.png")


def catalogue_image(x, y, w, h, path, caption=True):
    """Tilted catalogue-book picture (transparent PNG) with a small caption."""
    if not path or not os.path.exists(path):
        return ""
    out = f'<image href="file://{path}" x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" preserveAspectRatio="xMidYMid meet"/>'
    if caption:
        out = Ttr(x + w / 2, y - .08, "THE CATALOGUE BOOKS", "CZ", 600, 6.5, MUTED, "middle", .3) + out
    return out


def back_panel(x0, pw, books, bind_right=True, image=None):
    """Outside of the binding panel: quiet spec plate (no brand) + 4 tilted catalogue books."""
    usable0, usable1 = (x0, x0 + pw - P["bind_margin"]) if bind_right else (x0 + P["bind_margin"], x0 + pw)
    cx = (usable0 + usable1) / 2
    top = 4.2 if len(books) < 3 else 1.25
    out = [Ttr(cx, top, "CURATED FABRICS COLLECTION", "CZ", 500, 7.5, MUTED, "middle", .35)]
    y = top + .75
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
        y = ty + (.55 if len(books) < 3 else .4)
    out.append(f'<path d="M{cx - .5},{top - .35} h1" stroke="{BRASS}" stroke-width=".01"/>')
    if image:                                             # 2400 x 860 px picture, 2.79 : 1
        ih = 2.7 if len(books) < 3 else 1.95
        iy = max(y + .2, 11.35 - ih)
        ih = 11.35 - iy
        iw = min(ih * 2400 / 860, usable1 - usable0 - .3)
        ih = iw * 860 / 2400
        out.append(catalogue_image(cx - iw / 2, 11.35 - ih, iw, ih, image))
    return "".join(out)


def plain_panel(x0, pw, books):
    b = books[0]
    return (f'<rect x="{x0 + pw / 2 - .4}" y="11.15" width=".8" height=".02" fill="{ladder_color(b["cat"])}"/>' +
            Ttr(x0 + pw / 2, 11.45, b["name"].upper(), "CZ", 500, 7, MUTED, "middle", .3))


def outside_art(bd, image=None):
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
        parts += [c, back_panel(xs[1], ws[1], books, image=image)]
    else:              # [C_out | B_out = cover | A_out = back]
        c, real = cover_panel(xs[1], ws[1], books)
        parts += [plain_panel(xs[0], ws[0], books), c, back_panel(xs[2], ws[2], books, image=image)]
    return "".join(parts), xs, ws, real


# ---------------------------------------------------------------- inside liner
def inside_art(bd, guides=True):
    """Inside liner of a board.  guides=False is the PRINT version (owner, 17 Nov): no swatch
    placement boxes or slot labels - only the panel headers, the spec block and the footer.
    guides=True draws the placement (5 x 7 mains, cuttings, shade numbers) for the proof / assembly."""
    fold, books = bd["fold"], bd["books"]
    out, run = [], 0
    for i, pn in enumerate(bd["panels"]):
        b = pn.get("book") or bd["eff"]
        bx0, by0, bx1, by1 = content_box(fold, i)
        hy = P["margin"] + .5
        out.append(T(bx0, hy, b["name"].upper(), "CG", 600, 15, INK, track=.03))
        if pn["kind"] == "hero":
            tag = "MAIN FABRIC" if len(pn["shades"]) == 1 else f"MAIN FABRICS · WATERFALL OF {len(pn['shades'])}"
        elif pn.get("book"):
            tag = f"STAND {bd['stand']} · {len(pn['shades'])} SHADES" if bd.get("stand") else f"{len(pn['shades'])} SHADES"
        elif pn.get("title"):
            tag = pn["title"].upper()
        else:
            tag = f"SHADES {run + 1:02d} – {run + len(pn['shades']):02d}"
        if pn["kind"] == "swatch" and not pn.get("book"):
            run += len(pn["shades"])
        out.append(Ttr(bx1, hy, tag, "CZ", 600, 7, BRASS, "end", .25))
        out.append(f'<path d="M{bx0},{hy + .16} H{bx1}" stroke="{INK}" stroke-width=".006"/>')
        mains = set(m for m in b["mains"] if m)
        if guides:
            if pn["kind"] == "hero":                      # waterfall of 5 x 7 main pieces
                step = max(pn["grid"].get("dy", 0), .5)
                for k, ((cx, cy, cw, ch), shade) in enumerate(zip(pn["cells"], pn["shades"]), 1):
                    out.append(f'<rect x="{cx:.3f}" y="{cy:.3f}" width="{cw:.3f}" height="{ch:.3f}" fill="{mix(CELL, GUIDE, (k - 1) * .08)}" stroke="{GUIDE}" stroke-width=".007"/>')
                    lx, ly = bx0, pn["cells"][0][1] + (k - 1) * step
                    out.append(T(lx, ly + .2, "MAIN", "CZ", 600, 6, BRASS, track=.15))
                    out.append(T(lx, ly + .4, shade or "No. ____", "PP", 500, 8 if shade else 7, INK if shade else MUTED))
                x, y, w, h = pn["cells"][-1]
                out.append(T(x + w / 2, y + h / 2, "5 × 7 in READY-CUT", "CZ", 600, 6.5, MUTED, "middle", .15))
            else:
                for k, ((cx, cy, cw, ch), shade) in enumerate(zip(pn["cells"], pn["shades"]), 1):
                    is_main = pn.get("book") and k <= len(pn.get("mains", []))
                    out.append(f'<rect x="{cx:.3f}" y="{cy:.3f}" width="{cw:.3f}" height="{ch:.3f}" fill="{CELL}" stroke="{GUIDE}" stroke-width=".007"/>')
                    ly = cy + ch + .19
                    if is_main:
                        out.append(T(cx + cw / 2, cy + ch / 2, "5 × 7 in READY-CUT", "CZ", 600, 6.5, MUTED, "middle", .15))
                        out.append(T(cx, ly, f"MAIN · {shade}" if shade else "MAIN · NO. ______", "CZ", 600, 7.5, INK, track=.08))
                    elif shade and shade in mains:
                        out.append(T(cx, ly, f"MAIN · {shade}", "CZ", 600, 7.5 if cw > 1.3 else 5.5, INK, track=.08))
                    elif shade:
                        out.append(T(cx, ly, shade, "PP", 500, 7.5 if cw > 1.3 else 6, INK))
                    else:
                        out.append(T(cx, ly, "No.", "PP", 400, 7 if cw > 1.3 else 5.5, MUTED))
                    if cw > 1.3:
                        out.append(T(cx + cw, ly, f'{pn["letter"]}{k:02d}', "PP", 400, 5.5, GUIDE, "end"))
        if pn["kind"] == "hero":
            out.append(hero_spec(pn["spec_box"], b, compact=len(pn["shades"]) > 1))
        fy = P["board_h"] - P["margin"] - .05
        out.append(T(bx0, fy, f'NO. {b["seq"]:02d}  ·  {b["name"].upper()}  ·  PANEL {pn["letter"]}', "PP", 400, 5.5, MUTED, track=.1))
    return "".join(out)


def hero_spec(box, b, compact=False):
    x0, y0, x1, y1 = box
    if compact:                                           # several mains: name, line, one spec row
        out = [T(x0, y0 + .3, b["name"].upper(), "CG", 600, 20, INK, track=.02)]
        bits = [b["line"].upper()] + [f'{b["shades"]} SHADES' if b["shades"] else None,
                                      f'{b["width"]} IN' if b["width"] else None, f'{b["gsm"]} GSM' if b["gsm"] else None]
        out.append(Ttr(x0, y0 + .55, "  ·  ".join(x for x in bits if x), "CZ", 500, 7, BRASS, "start", .2))
        out.append(ladder_full(x0, y1 - .42, x1 - x0, b["cat"]))
        return "".join(out)
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


def master_back(x0, w, h, books, image=None):
    """Back of the master binder: the 20 catalogue books tilted in two rows of 10, the
    light-control scale and the collections in two columns.  No brand anywhere."""
    cx = x0 + w / 2
    out = [Ttr(cx, 1.05, "THE COLLECTIONS", "CZ", 600, 10, BRASS, "middle", .45),
           T(cx, 1.62, "Sheer to Blackout", "CG", 600, 30, INK, "middle"),
           T(cx, 1.94, "Twenty collections, arranged by light control, then by fabric weight", "CG", 500, 13, MUTED, "middle", italic=True)]
    # 20 books, two rows of 10 (3000 x 950 px picture)
    iw = w - 1.0
    ih = iw * 950 / 3000
    if image and os.path.exists(image):
        out.append(f'<image href="file://{image}" x="{x0 + .5:.3f}" y="2.2" width="{iw:.3f}" height="{ih:.3f}" preserveAspectRatio="xMidYMid meet"/>')
    # light-control scale
    n, sx0, sx1, sy = len(LADDER), x0 + 1.0, x0 + w - 1.0, 2.2 + ih + .45
    cw = (sx1 - sx0) / n
    out.append(Ttr(sx0, sy - .14, "MORE LIGHT", "CZ", 600, 6, MUTED, "start", .3))
    out.append(Ttr(sx1, sy - .14, "MORE PRIVACY & DARKNESS", "CZ", 600, 6, MUTED, "end", .3))
    for i, (k, name, desc, col) in enumerate(LADDER):
        bx = sx0 + i * cw
        out.append(f'<rect x="{bx + .03:.3f}" y="{sy:.3f}" width="{cw - .06:.3f}" height=".14" fill="{col}"/>')
        out.append(Ttr(bx + cw / 2, sy + .34, name.upper(), "CZ", 600, 6.5, INK, "middle", .2))
    # collections in two columns (category groups kept together)
    groups, last = [], None
    for b in books:
        if b["cat"] != last:
            groups.append((b["cat"], []))
            last = b["cat"]
        groups[-1][1].append(b)
    rows = lambda g: 1 + len(g[1])
    total = sum(rows(g) for g in groups)
    split, acc = 0, 0
    for i, g in enumerate(groups):
        if acc + rows(g) > total / 2 + 1:
            break
        acc += rows(g); split = i + 1
    cols = [groups[:split], groups[split:]]
    top, colw = sy + .95, (w - 2.0 - .6) / 2
    for ci, col in enumerate(cols):
        lx = x0 + 1.0 + ci * (colw + .6)
        y = top
        for cat, bs in col:
            name = [nm for k, nm, *_ in LADDER if k == cat][0]
            out.append(f'<rect x="{lx}" y="{y - .1}" width=".2" height=".11" fill="{ladder_color(cat)}"/>')
            out.append(Ttr(lx + .32, y, name.upper(), "CZ", 600, 7, MUTED, "start", .3))
            out.append(f'<path d="M{lx + .32 + text_w(name.upper(), "CZ", 600, 7 * PT, .3) + .12},{y - .04} H{lx + colw}" stroke="{GUIDE}" stroke-width=".006"/>')
            y += .36
            for b in bs:
                out.append(T(lx, y, f'{b["seq"]:02d}', "CZ", 600, 9, BRASS))
                out.append(T(lx + .4, y, b["name"], "CG", 600, 14.5, INK))
                out.append(T(lx + colw, y, b["line"], "PP", 400, 6.5, MUTED, "end"))
                y += .31
            y += .2
    out.append(Ttr(cx, 12.45, f"{len(books)} COLLECTIONS  ·  ONE BOOK", "CZ", 600, 8, INK, "middle", .35))
    return "".join(out)


def spine_art(x0, w, h):
    cx = x0 + w / 2
    out = [T(cx, h / 2, "CURATED FABRICS COLLECTION", "CZ", 600, 16 if w > 1.5 else 11, INK, "middle",
             extra=f'transform="rotate(90 {cx} {h / 2})" dominant-baseline="middle" style="letter-spacing:{.3 * 16 * PT:.4f}px"')]
    n = len(LADDER)
    for i, (k, *_r, col) in enumerate(LADDER):
        out.append(f'<rect x="{x0 + w * .2}" y="{h - 2.2 + i * .2}" width="{w * .6}" height=".12" fill="{col}"/>')
    return "".join(out)
