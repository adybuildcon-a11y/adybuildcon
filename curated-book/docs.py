"""Design Guide (A4 landscape) and Instructions (A4 portrait) as HTML for Chromium."""

import os

from art import (outside_art, FONT_CSS, LINEN, INK, MUTED, BRASS, PAPER, CREAM, cover_panel, inside_art, master_front,
                 master_back, spine_art, T, esc)
from data import LADDER, P, TRANSCRIPT, EXTRA
from layout import panel_widths, panel_x, content_box, open_size, ladder_color
from printfiles import draft_src

HERE = os.path.dirname(os.path.abspath(__file__))
CATNAME = {k: n for k, n, *_ in LADDER}

CSS = FONT_CSS + """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:PP;color:#2B2723;background:#888}
.pg{position:relative;overflow:hidden;background:#FBF8F2;page-break-after:always;break-after:page}
.L{width:11.69in;height:8.27in;padding:.55in .6in}
.Pt{width:8.27in;height:11.69in;padding:.6in .6in}
.k{font-family:CZ;font-weight:600;font-size:8pt;letter-spacing:.32em;color:#8C6B36;text-transform:uppercase}
h1{font-family:CG;font-weight:600;font-size:30pt;line-height:1.05;margin:.06in 0 .12in}
h2{font-family:CG;font-weight:600;font-size:17pt;margin:.14in 0 .06in}
p,li{font-size:8.6pt;line-height:1.55;color:#3E3933}
.lead{font-family:CG;font-style:italic;font-size:13pt;line-height:1.4;color:#6E655A;max-width:7.2in}
ul{padding-left:.18in}
table{border-collapse:collapse;width:100%;font-size:7.6pt}
th{background:#2B2723;color:#fff;font-weight:500;text-align:left;padding:4px 6px;font-size:7pt;letter-spacing:.04em}
td{border-bottom:1px solid #E2DACB;padding:3.5px 6px;vertical-align:top;line-height:1.4}
tr:nth-child(even) td{background:#F5F0E6}
.foot{position:absolute;left:.6in;right:.6in;bottom:.3in;display:flex;justify-content:space-between;font-size:6.5pt;color:#9A9083;letter-spacing:.06em}
.cols{display:flex;gap:.35in}
.tile{flex:1;border-top:2px solid #2B2723;padding-top:.08in}
.tile b{display:block;font-family:CG;font-weight:600;font-size:30pt;line-height:1}
.tile span{font-size:7.5pt;color:#6E655A}
.chip{display:inline-block;width:.16in;height:.1in;margin-right:5px;vertical-align:middle}
.st{display:inline-block;padding:1px 6px;border-radius:2px;font-size:6.8pt;font-weight:500}
.Confirmed{background:#E3EDD9}.Pending{background:#FBE9C9}.Reconsider,.Details{background:#F6D6D0}
svg{display:block}
.note{border-left:2px solid #8C6B36;padding:.04in .12in;background:#F3EEE5;font-size:8pt;margin:.1in 0}
"""


def page(cls, inner, n, total_label):
    return f'<section class="pg {cls}">{inner}<div class="foot"><span>CURATED FABRICS COLLECTION  ·  {total_label}</span><span>{n:02d}</span></div></section>'


def svgbox(content, vw, vh, w_in, bg=None):
    h_in = w_in * vh / vw
    bgr = f'<rect width="{vw}" height="{vh}" fill="{bg}"/>' if bg else ""
    return f'<svg width="{w_in}in" height="{h_in}in" viewBox="0 0 {vw} {vh}">{bgr}{content}</svg>'


def callouts(points, r=.18, pt=9):
    out = []
    for i, (x, y) in enumerate(points, 1):
        out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#C0392B"/>' + T(x, y + r * .38, str(i), "PP", 600, pt, "#fff", "middle"))
    return "".join(out)


def dim(x1, y1, x2, y2, label, off=.0, vertical=False, size=7):
    """Dimension line with end ticks and label."""
    if vertical:
        return (f'<path d="M{x1},{y1} V{y2} M{x1 - .08},{y1} h.16 M{x1 - .08},{y2} h.16" stroke="#C0392B" stroke-width=".015"/>' +
                T(x1 + .12 + off, (y1 + y2) / 2 + .04, label, "PP", 500, size, "#C0392B"))
    return (f'<path d="M{x1},{y1} H{x2} M{x1},{y1 - .08} v.16 M{x2},{y1 - .08} v.16" stroke="#C0392B" stroke-width=".015"/>' +
            T((x1 + x2) / 2, y1 - .1 + off, label, "PP", 500, size, "#C0392B", "middle"))


# ==================================================================== DESIGN GUIDE
def design_guide(books, bds, spine_in, stack_mm):
    pages, n = [], 0
    ready = [bd for bd in bds if bd["ready"]]

    def add(inner, cls="L"):
        nonlocal n
        n += 1
        pages.append(page(cls, inner, n, "DESIGN GUIDE"))

    # 1 cover
    mf, _ = master_front(0, P["cover_w"], P["cover_h"], books)
    add(f'''<div style="display:flex;height:100%;gap:.6in;align-items:center">
      <div style="flex:1"><div class="k">Design Guide</div><h1 style="font-size:44pt">Curated Fabrics<br>Collection</h1>
      <p class="lead">How the book is built: format, folds, grid, swatches, covers, colour, type, photography and print - measured, not eyeballed.</p>
      <p style="margin-top:.3in">20 collections · 19 mood-boards · 4-ring master binder 11 × 13 in · leaves 9 × 12 in</p></div>
      <div>{svgbox(mf, P["cover_w"], P["cover_h"], 4.9, LINEN)}</div></div>''')

    # 2 overview
    pend = [bd for bd in bds if not bd["ready"]]
    add(f'''<div class="k">01 · At a glance</div><h1>One book, twenty mood-boards</h1>
      <p class="lead">A 4-ring master binder holds one fold-out mood-board leaf per collection, as in the reference binder. Each board opens on a hero swatch of the main fabric and a measured grid of every curated shade. The front of each board carries a photo and the collection name - and no company branding anywhere.</p>
      <div class="cols" style="margin:.3in 0">
        <div class="tile"><b>20</b><span>collections from the book list</span></div>
        <div class="tile"><b>19</b><span>boards (Eeco Dimout + Double Shade share one)</span></div>
        <div class="tile"><b>{len([b for b in ready if not b.get("draft")])}</b><span>inside layouts confirmed from the notes</span></div>
        <div class="tile"><b>{len([b for b in ready if b.get("draft")])}</b><span>draft layouts (count from price list / catalogue)</span></div>
        <div class="tile"><b>{len(pend)}</b><span>leaves waiting on shade lists (covers ready)</span></div>
        <div class="tile"><b>{stack_mm / 10:.1f}<small style="font-size:14pt"> cm</small></b><span>leaf stack (350 GSM card + fabric)</span></div></div>
      <h2>Design principles</h2>
      <div class="cols"><ul style="flex:1">
        <li><b>No branding.</b> No logo, company name or contact on any leaf or the binder.</li>
        <li><b>Mood-board per collection.</b> Photo + name outside; hero swatch, specs and shade grid inside.</li>
        <li><b>Ordered by light control.</b> Sheer → Curtain → Texture Dimout → Dimout → Blackout → Lining, then by weight (GSM).</li></ul>
        <ul style="flex:1"><li><b>Measured layout.</b> Every grid is solved for the largest legible swatch; one grid per board.</li>
        <li><b>Traceable.</b> Each swatch slot has an ID (A01, B07 …) that matches the Shade Register in the Excel.</li>
        <li><b>Print-true.</b> CMYK PDFs with bleed, turn-ins, fold ticks, TrimBox and BleedBox.</li></ul></div>''')

    # 3 sequence ladder
    colw = 10.4 / len(LADDER)
    cols_html = ""
    for k, name, desc, col in LADDER:
        items = "".join(f'<div style="font-family:CG;font-weight:600;font-size:12.5pt;line-height:1.35"><span style="font-family:CZ;font-size:7pt;color:#8C6B36;margin-right:6px">{b["seq"]:02d}</span>{esc(b["name"])}</div>' for b in books if b["cat"] == k)
        cols_html += f'<div style="width:{colw}in"><div style="height:.14in;background:{col}"></div><div class="k" style="margin:.1in 0 .02in;color:#2B2723">{name}</div><p style="font-size:7.3pt;min-height:.4in">{desc}</p>{items}</div>'
    add(f'''<div class="k">02 · Sequence</div><h1>Sheer to blackout - the order is the logic</h1>
      <p class="lead">Customers decide on light first, texture second. The book follows that decision: it opens airy and closes room-darkening. Inside each level, lighter fabrics (lower GSM) come first; unknown weights follow, alphabetically.</p>
      <div style="display:flex;gap:.06in;margin-top:.35in">{cols_html}</div>
      <div class="note" style="margin-top:.35in">Colour code: each level has one colour. It appears as the index tab on the board edge, the light-control scale on covers and liners, and the key on the binder back - so a collection can be found without leafing through.</div>''')

    # 4 formats
    cw, ch, bw, bh = P["cover_w"], P["cover_h"], P["board_w"], P["board_h"]
    fmt = (f'<rect x="0" y="0" width="{cw}" height="{ch}" fill="{LINEN}" stroke="{INK}" stroke-width=".02"/>'
           f'<rect x="1" y=".5" width="{bw}" height="{bh}" fill="{PAPER}" stroke="{BRASS}" stroke-width=".02" stroke-dasharray=".12 .06"/>'
           + dim(0, -.25, cw, -.25, f'Master binder {cw} in') + dim(cw + .3, 0, 0, ch, f'{ch} in', vertical=True).replace(f"M{cw + .3},0 V0", f"M{cw + .3},0 V{ch}")
           + dim(1, 6, 1 + bw, 6, f'Board panel {bw} in') + dim(5.5, .5, 0, .5 + bh, "", vertical=True).replace("M5.5,.5 V0", f"M5.5,.5 V{.5 + bh}")
           + T(5.65, 6.6, f'{bh} in', "PP", 500, 7, "#C0392B") + T(1.15, 12.2, "1 in clearance each side - board lifts out freely", "PP", 400, 6, MUTED))
    fw2, fw3 = open_size(2)[0], open_size(3)[0]
    folds = ""
    y = 0
    for f, w in ((2, fw2), (3, fw3)):
        for i in range(f):
            x, pw = panel_x(f, i), panel_widths(f)[i]
            folds += f'<rect x="{x}" y="{y}" width="{pw}" height="{bh}" fill="{PAPER}" stroke="{INK}" stroke-width=".04"/>' + T(x + pw / 2, y + bh / 2, "ABC"[i], "CG", 600, 60, "#CFC4B2", "middle")
        folds += dim(0, y - .4, w, y - .4, f'{f}-fold open: {w:.3f} × {bh} in', size=22)
        y += bh + 3
    add(f'''<div class="k">03 · Formats</div><h1>Sizes, to scale</h1>
      <div class="cols"><div>{svgbox(f'<g transform="translate(.5 .6)">{fmt}</g>', cw + 1.6, ch + 1.0, 3.6)}</div>
      <div style="flex:1"><p class="lead" style="font-size:12pt">From the notes: cover 11 × 13 in, inside boards 9 × 12 in. Leaves fold to 9 × 12 and hang on 4 rings, with 1 in clearance all round.</p>
      <div style="margin:.1in 0">{svgbox(f'<g transform="translate(.5 1.5)">{folds}</g>', fw3 + 1, 2 * bh + 5, 3.9)}</div>
      <table><tr><th>Item</th><th>Size</th><th>Why</th></tr>
      <tr><td>Fold allowance</td><td>{P["hinge"]} in double score</td><td>Room for two fabric layers when a leaf closes</td></tr>
      <tr><td>3-fold panel C</td><td>{bw - P["roll_fold"]} in</td><td>Folds inside B; 3 mm narrower avoids buckling</td></tr>
      <tr><td>Binder</td><td>{P["ring_mm"]} mm 4-D-ring · spine {spine_in} in</td><td>Stack {stack_mm:.0f} mm = Σ folds × ({P["board_mm"]} mm card + {P["fabric_mm"]} mm fabric); ring = smallest size with 25% headroom</td></tr></table></div></div>''')

    # 5 fold anatomy
    def fold_diag(f):
        s, ow = "", open_size(f)[0]
        for i in range(f):
            x, pw = panel_x(f, i), panel_widths(f)[i]
            s += f'<rect x="{x}" y="0" width="{pw}" height="{bh}" fill="{PAPER}" stroke="{INK}" stroke-width=".04"/>'
            role = {0: "Hero" if f == 2 else "Shades", 1: "Shades", 2: "Hero"}[i]
            s += T(x + pw / 2, 5.5, "ABC"[i], "CG", 600, 70, "#CFC4B2", "middle") + T(x + pw / 2, 7.3, f"inside {role}", "PP", 500, 22, MUTED, "middle")
        s += f'<rect x="0" y="0" width="{P["bind_margin"]}" height="{bh}" fill="#C0392B" opacity=".12"/>' + T(.5, 11.3, "bind", "PP", 500, 16, "#C0392B", "middle")
        ox = ow + 1.2
        ws = panel_widths(f)[::-1]
        x = ox
        for i, pw in enumerate(ws):
            lab = "ABC"[f - 1 - i]
            cov = (f == 2 and i == 0) or (f == 3 and i == 1)
            s += f'<rect x="{x}" y="0" width="{pw}" height="{bh}" fill="{LINEN if cov else CREAM}" stroke="{INK}" stroke-width=".04"/>'
            s += T(x + pw / 2, 5.5, lab, "CG", 600, 70, "#B5A68C", "middle") + T(x + pw / 2, 7.3, "COVER" if cov else "outside", "PP", 600 if cov else 500, 22, INK if cov else MUTED, "middle")
            x += pw + P["hinge"]
        s += T(ow / 2, -0.6, "INSIDE (liner)", "CZ", 600, 26, INK, "middle") + T(ox + ow / 2, -0.6, "OUTSIDE (wrap)", "CZ", 600, 26, INK, "middle")
        return s, 2 * ow + 1.2
    d2, w2 = fold_diag(2)
    d3, w3 = fold_diag(3)
    add(f'''<div class="k">04 · Fold anatomy</div><h1>Which panel does what</h1>
      <div style="margin:.15in 0">{svgbox(f'<g transform="translate(.3 1.4)">{d2}</g>', w3 + .6, bh + 2, 6.0)}</div>
      <div>{svgbox(f'<g transform="translate(.3 1.4)">{d3}</g>', w3 + .6, bh + 2, 10.2)}</div>
      <div class="cols" style="margin-top:.15in"><p style="flex:1"><b>2-fold:</b> inside A = hero main fabric + specs, B = shade grid. B folds onto A; the outside of B is the cover.</p>
      <p style="flex:1"><b>3-fold (roll fold):</b> inside A + B = shade grid, C = hero (as in the reference trifold). C folds in first, then B over A; the outside of B is the cover.</p>
      <p style="flex:1"><b>Binding edge:</b> 1 in on panel A is kept clear for the 4-ring punch, as in the reference binder. Index tab prints on the hinge edge of the cover.</p></div>''')

    # 6 grid
    bx0, by0, bx1, by1 = content_box(2, 1)
    px = panel_x(2, 1)
    g = (f'<rect x="0" y="0" width="{bw}" height="{bh}" fill="{PAPER}" stroke="{INK}" stroke-width=".02"/>'
         f'<rect x="{bx0 - px}" y="{by0}" width="{bx1 - bx0}" height="{by1 - by0}" fill="#E8DFCF" opacity=".6"/>'
         f'<rect x="{P["margin"]}" y="{P["margin"]}" width="{bw - 2 * P["margin"]}" height="{P["header"]}" fill="#D9CDB7" opacity=".7"/>'
         + T(bw / 2, P["margin"] + .55, "HEADER - name + panel tag", "PP", 500, 9, INK, "middle")
         + T(bw / 2, (by0 + by1) / 2, "CONTENT - swatch grid / hero", "PP", 500, 10, INK, "middle")
         + T(bw / 2, bh - P["margin"] - .1, "FOOTER - book · panel ID", "PP", 500, 8, INK, "middle")
         + dim(0, 3, P["margin"], 3, f'{P["margin"]}', size=8) + dim(bx1 - px, 3, bw, 3, f'{P["margin"]}', size=8)
         + dim(bw + .35, 0, 0, P["margin"], f'{P["margin"]} margin', vertical=True).replace(f"M{bw + .35},0 V0", f"M{bw + .35},0 V{P['margin']}")
         + dim(bw + .35, P["margin"], 0, by0, f'{P["header"]} header', vertical=True).replace(f"M{bw + .35},{P['margin']} V0", f"M{bw + .35},{P['margin']} V{by0}")
         + dim(bw + .35, by0, 0, by1, f'{by1 - by0:.2f} content', vertical=True).replace(f"M{bw + .35},{by0} V0", f"M{bw + .35},{by0} V{by1}")
         + dim(bx0 - px, 9.9, bx1 - px, 9.9, f'{bx1 - bx0:.2f} in content width', size=8))
    add(f'''<div class="k">05 · Grid</div><h1>Panel grid and margins</h1>
      <div class="cols"><div>{svgbox(f'<g transform="translate(.4 .4)">{g}</g>', bw + 2.2, bh + .8, 4.6)}</div>
      <div style="flex:1"><table><tr><th>Zone</th><th>Value</th><th>Rule</th></tr>
      <tr><td>Panel</td><td>{bw} × {bh} in</td><td>From the notes</td></tr>
      <tr><td>Outer margin</td><td>{P["margin"]} in</td><td>Safe zone - nothing printed outside except background</td></tr>
      <tr><td>Binding margin (panel A)</td><td>{P["bind_margin"]} in</td><td>Clear for punching / screw-post</td></tr>
      <tr><td>Header</td><td>{P["header"]} in</td><td>Book name (Cormorant 15 pt) + panel tag (Cinzel 7 pt) + hairline</td></tr>
      <tr><td>Footer</td><td>{P["footer"]} in</td><td>Book No. · name · panel letter (Poppins 5.5 pt)</td></tr>
      <tr><td>Gutter</td><td>{P["gutter"]} in</td><td>Between swatches - enough for pinked edges</td></tr>
      <tr><td>Label band</td><td>{P["label_h"]} in</td><td>Shade No. left, slot ID right</td></tr>
      <tr><td>Minimum swatch</td><td>{P["min_sw_w"]} × {P["min_sw_h"]} in</td><td>Smallest size where weave & colour still read</td></tr>
      <tr><td>Maximum per panel</td><td>{P["cap_per_panel"]}</td><td>3 × 6 grid at minimum size; decides 2- vs 3-fold</td></tr></table>
      <div class="note">Fold rule when the notes don't give one: panels = 1 (hero, if a main is named) + ⌈other shades ÷ 18⌉, minimum 2.</div></div></div>''')

    # 7 swatch system
    rows = []
    for bd in ready:
        b = bd["books"][0]
        for pn in bd["panels"]:
            gr = pn["grid"]
            rows.append(f'<tr><td>{bd["no"]:02d}</td><td>{esc(b["name"])}</td><td>{pn["letter"]}</td><td>{"Hero" if pn["kind"] == "hero" else (pn.get("title") or "Shades")}</td><td>{len(pn["shades"])}</td><td>{("waterfall " + str(gr["rows"])) if gr.get("waterfall") else (str(gr["cols"]) + " × " + str(gr["rows"]))}</td><td>{gr["w"]:.2f} × {gr["h"]:.2f}{" avg" if gr.get("waterfall") else ""}</td></tr>')
    th = '<tr><th>Bd</th><th>Book</th><th>Pnl</th><th>Content</th><th>Qty</th><th>Grid</th><th>Swatch in</th></tr>'
    mid = (len(rows) + 1) // 2
    halves = "".join(f'<table style="flex:1;font-size:6.6pt">{th}{"".join(part)}</table>' for part in (rows[:mid], rows[mid:]))
    vir = [bd for bd in bds if bd["books"][0]["id"] == "virinche"][0]
    tex = [bd for bd in bds if bd["books"][0]["id"] == "texture-dimout"][0]
    ow3 = open_size(3)[0]
    rng_r = f'<rect width="{ow3}" height="{P["board_h"]}" fill="{PAPER}"/>' + inside_art(vir)
    mix_r = f'<rect width="{ow3}" height="{P["board_h"]}" fill="{PAPER}"/>' + inside_art(tex)
    mixed_names = ", ".join(b["name"] for b in books if b["mode"] == "mixed")
    add(f'''<div class="k">06 · The swatch rule</div><h1>Main big, cuttings small - unless the designs differ</h1>
      <div class="cols"><div style="flex:1"><h2 style="margin-top:0">Colour range → main fabric big</h2>
      <p>One design / texture offered in many colours: the main fabric gets a full panel so the hand and texture can be felt; every other shade is a small cutting (max {2.5} × {1.6} in) - the eye compares colour, not texture.</p>
      <div style="margin-top:.1in">{svgbox(rng_r, ow3, P["board_h"], 5.1)}</div><p><b>Example: Virinche</b> - main 705 big, 20 colour cuttings.</p></div>
      <div style="flex:1"><h2 style="margin-top:0">Different designs → all the same size</h2>
      <p>When every fabric is a different design or texture, no swatch is "main": all are cut to one larger, near-square size so each texture reads equally. Mains, if named, go first and are marked MAIN.</p>
      <div style="margin-top:.1in">{svgbox(mix_r, ow3, P["board_h"], 5.1)}</div><p><b>Example: Texture Dimout</b> - 27 qualities, all equal.</p></div></div>
      <div class="note"><b>Main fabrics are always a waterfall:</b> full-width pieces, each stepped down by one band (max 1.6 in), all ending at the same bottom edge - every main shows a band and the last one shows the most, like the layered cards in the e-catalogue. Same-size books: {mixed_names}. All others: colour range. Mode is a column in the Excel Book_List - change it and re-run to switch a book.</div>''')

    add(f'''<div class="k">07 · Swatch sizes</div><h1>Swatch sizes are solved, not guessed</h1>
      <div class="cols"><div style="flex:1"><p>For every panel the layout engine tries 1-6 columns and keeps the grid with the largest swatch area, biased to a 1.6 : 1 landscape swatch for colour cuttings (1.15 : 1 for mixed designs), never below the minimum size. All swatch panels on one board share the same grid so the board looks even.</p>
      <h2>Swatch rules</h2><ul>
      <li>Cut each swatch <b>1 mm larger</b> than its printed frame, pinked edge (zig-zag) as in the reference cards.</li>
      <li>Glue inside the frame; the shade No. prints under the swatch, slot ID at right in grey.</li>
      <li>Within a panel, order light → dark, grouped by hue family (neutrals first). Where the notes give an order, keep it.</li>
      <li>Main fabric(s): waterfall on the hero panel - band = min(1.6 in, height ÷ (mains + 1)); one main = one full piece.</li>
      <li>Colour-range books: other shades small cuttings ≤ 2.5 × 1.6 in.</li>
      <li>Mixed-design books: one equal size for every swatch, biased near-square (1.15 : 1).</li></ul></div>
      <div style="flex:1.6;display:flex;gap:.15in">{halves}</div></div>''')

    # 8 type & colour
    pal = [("Linen board", LINEN, "C14 M15 Y26 K0"), ("Liner paper", PAPER, "C3 M4 Y8 K0"), ("Ink", INK, "C0 M10 Y20 K90"),
           ("Muted text", MUTED, "C0 M10 Y22 K62"), ("Brass", BRASS, "C0 M30 Y70 K40"), ("Arch frame", CREAM, "C3 M5 Y11 K0")]
    pal_html = "".join(f'<div style="flex:1"><div style="height:.55in;background:{c};border:1px solid #ddd"></div><p style="margin-top:4px"><b>{nm}</b><br>{c}<br>{cm}</p></div>' for nm, c, cm in pal)
    lad_html = "".join(f'<div style="flex:1"><div style="height:.3in;background:{c}"></div><p style="margin-top:4px"><b>{nm}</b><br>{c}</p></div>' for k, nm, d, c in LADDER)
    add(f'''<div class="k">08 · Type & colour</div><h1>Quiet, natural, neutral</h1>
      <div class="cols"><div style="flex:1">
      <p style="font-family:CG;font-weight:600;font-size:34pt;line-height:1">VIRINCHE</p><p>Cormorant Garamond SemiBold - collection names. Covers 30-46 pt (auto-fitted), liners 15 pt, hero 24 pt.</p>
      <p style="font-family:CZ;font-weight:600;font-size:13pt;letter-spacing:.25em;margin-top:.15in">COTTON-BLEND CURTAIN FABRIC</p><p>Cinzel - category lines, tags, numbers. 7-11 pt, tracked 0.06-0.3 em.</p>
      <p style="font-size:11pt;margin-top:.15in">Poppins - specs, shade numbers, labels</p><p>Poppins 5.5-8 pt. Shade numbers Poppins Medium 7.5 pt.</p>
      <div class="note">All fonts are free (SIL Open Font License) and embedded in every PDF.</div></div>
      <div style="flex:1.2"><h2>Base palette (CMYK approximate - match to printer proof)</h2><div style="display:flex;gap:.1in">{pal_html}</div>
      <h2>Light-control code</h2><div style="display:flex;gap:.1in">{lad_html}</div></div></div>''')

    # 9 cover anatomy
    vir = [bd for bd in bds if bd["books"][0]["id"] == "virinche"][0]
    cov, _ = cover_panel(0, bw, vir["books"])
    pts = [(.9, 1.25), (2.0, 2.0), (2.4, 2.75), (6.4, 5.5), (.9, 9.5), (.9, 10.3), (8.9, 1.2)]
    add(f'''<div class="k">09 · Board cover</div><h1>Front covering - photo and name only</h1>
      <div class="cols"><div>{svgbox(f'<rect width="{bw}" height="{bh}" fill="{LINEN}"/>' + cov + callouts(pts), bw, bh, 4.9)}</div>
      <div style="flex:1"><table><tr><th>#</th><th>Element</th><th>Spec</th></tr>
      <tr><td>1</td><td>Book number</td><td>Cinzel 9 pt, tracked 0.3 em - position in the master book</td></tr>
      <tr><td>2</td><td>Collection name</td><td>Cormorant SemiBold caps, auto-fitted to the column, max 46 pt; long names break by word</td></tr>
      <tr><td>3</td><td>Category line</td><td>Cinzel 10.5 pt between double rules (as on the Neo Luna sample)</td></tr>
      <tr><td>4</td><td>Arch photo window</td><td>{bw * .525 - .62:.2f} × 9.65 in, cream frame 0.13 in. Lifestyle photo; vector curtain illustration (final), or a lifestyle photo if supplied</td></tr>
      <tr><td>5</td><td>Facts</td><td>Shade count, width, GSM - only values from the notes / price list</td></tr>
      <tr><td>6</td><td>Light-control scale</td><td>6 steps, this book's level filled</td></tr>
      <tr><td>7</td><td>Index tab</td><td>0.2 in strip in the level colour on the hinge edge, book No. in white</td></tr></table>
      <div class="note">No logo, company name, phone, address or website - by design. Metal corner protectors and a rope handle can be added as in the Neo Luna sample.</div></div></div>''')

    # 10 inside anatomy
    tex = [bd for bd in bds if bd["books"][0]["id"] == "texture-dimout"][0]
    ow3 = open_size(3)[0]
    ins = f'<rect width="{ow3}" height="{bh}" fill="{PAPER}"/>' + inside_art(tex)
    hero_box = tex["panels"][2]["cells"][0]
    pts = [(.9, .7), (8.6, .7), (1.2, 2.2), (1.3, 3.05), (2.9, 3.05), (hero_box[0] + .3, hero_box[1] + .3), (hero_box[0] + .3, 8.6), (hero_box[0] + .3, 10.8)]
    add(f'''<div class="k">10 · Inside</div><h1>Inside (side 2) - the mood-board</h1>
      <div>{svgbox(ins + callouts(pts, r=.22, pt=10), ow3, bh, 10.4)}</div>
      <div class="cols" style="margin-top:.12in"><p style="flex:1">1 Header name · 2 Panel tag (shade range / group / main) · 3 Swatch frame = glue guide</p>
      <p style="flex:1">4 Shade No. (blank line until confirmed) · 5 Slot ID → Shade Register · 6 Hero main swatch(es)</p>
      <p style="flex:1">7 Spec block - only known values · 8 Light-control scale with the book's level highlighted</p></div>''')

    # 11 master case
    W, H, j = P["cover_w"], P["cover_h"], P["joint"]
    total = W + j + spine_in + j + W
    case = (f'<rect width="{total}" height="{H}" fill="{LINEN}"/>' + master_back(0, W, H, books) + spine_art(W + j, spine_in, H)
            + master_front(W + j + spine_in + j, W, H, books)[0]
            + f'<path d="M{W},0 V{H} M{W + j},0 V{H} M{W + j + spine_in},0 V{H} M{W + 2 * j + spine_in},0 V{H}" stroke="#C0392B" stroke-width=".02" stroke-dasharray=".15 .1"/>')
    add(f'''<div class="k">11 · Master binder</div><h1>Final book front - Trending Curated Fabrics Collection</h1>
      <div>{svgbox(case, total, H, 10.4)}</div>
      <p style="margin-top:.1in">Back (index of all 20 by light control) · spine {spine_in} in ({P["ring_mm"]} mm 4-D-ring for a {stack_mm:.0f} mm leaf stack) · front. Dashed lines = joints, {j} in each. Title wording from the brief: "most demanding / trending curated fabrics collection".</p>''')

    # 12 photo direction
    aw = bw * .525 - .62
    add(f'''<div class="k">12 · Photography</div><h1>Cover art: illustration now, photo optional</h1>
      <div class="cols"><div style="flex:1"><table><tr><th>Spec</th><th>Value</th></tr>
      <tr><td>Window</td><td>Arch {aw:.2f} × 9.65 in (board cover) · 5.1 × 6.95 in (master front)</td></tr>
      <tr><td>Minimum size</td><td>{int(aw * 300)} × {int(9.65 * 300)} px (300 dpi) · master 1530 × 2085 px</td></tr>
      <tr><td>Orientation</td><td>Portrait, ~1 : 2.3; subject centred - the arch crops the top corners</td></tr>
      <tr><td>File</td><td>JPG, sRGB, saved as assets/photos/&lt;book-id&gt;.jpg (e.g. virinche.jpg); master.jpg for the binder front</td></tr>
      <tr><td>Content</td><td>The collection's main shade as a full-height curtain in a calm room, daylight from the side</td></tr></table>
      <h2>Do</h2><ul><li>Real fabric of that collection, main shade</li><li>Soft side light, neutral walls, wooden or stone floor</li><li>Same camera height and white balance for all 20</li></ul>
      <h2>Don't</h2><ul><li>No logos, text, watermarks or supplier branding in the photo</li><li>No stock image you have no licence for</li><li>No heavy filters - colour must match the swatch</li></ul></div>
      <div style="flex:1"><table><tr><th>No.</th><th>Book</th><th>File name</th><th>Photo</th></tr>
      {"".join(f'<tr><td>{b["seq"]:02d}</td><td>{esc(b["name"])}</td><td>{b["id"]}.jpg</td><td>Optional</td></tr>' for b in books)}</table></div></div>''')

    # 13 print spec
    add(f'''<div class="k">13 · Print & finishing</div><h1>Production specification</h1>
      <div class="cols"><div style="flex:1"><table><tr><th>Item</th><th>Specification</th></tr>
      <tr><td>Files</td><td>CMYK PDF, fonts embedded, TrimBox + BleedBox set, crop marks, fold ticks, slug</td></tr>
      <tr><td>Leaves</td><td>350 GSM card, printed both sides: side 1 outside (cover + spec), side 2 inside (swatch layout); turn on the long edge. Matt laminate, double-scored folds ({P["hinge"]} in); 3-fold panel C {bw - P["roll_fold"]} in wide</td></tr>
      <tr><td>Punching</td><td>4 holes in the 1 in binding zone of panel A, matched to the binder mechanism</td></tr>
      <tr><td>Master binder</td><td>{P["ring_mm"]} mm 4-D-ring binder, 2.5 mm boards, cover wrap 00_Master_Binder_Cover ({P["turn_in"]} in turn-in)</td></tr>
      <tr><td>Rigid option</td><td>Stand-alone boards (like the Neo Luna hanger) at 1.5 mm greyboard would make a 10 cm stack - too thick for rings; use card leaves in the binder</td></tr>
      <tr><td>Fittings</td><td>Black metal corner protectors (as Neo Luna sample), optional rope handle</td></tr>
      <tr><td>Colour</td><td>Hard proof one board before the run; match linen and ladder colours to proof</td></tr></table></div>
      <div style="flex:1"><h2 style="margin-top:0">QC checklist</h2><ul>
      <li>No branding anywhere (logo, name, phone, address, website)</li>
      <li>Board sequence 01-20 matches the binder back index</li>
      <li>Every swatch sits inside its frame; shade No. matches the fabric</li>
      <li>Slot IDs match the Shade Register; blank lines filled or labelled</li>
      <li>Cover art approved - illustrated curtain or supplied photo</li>
      <li>Boards close flat; panel C folds inside without buckling</li>
      <li>Index tabs visible on the hinge edge, colours correct per level</li>
      <li>Binder closes with all 19 leaves; rings turn freely</li></ul></div></div>''')

    # 14-15 contact sheets
    for chunk in (bds[:10], bds[10:]):
        cells = ""
        for bd in chunk:
            c, _ = cover_panel(0, bw, bd["books"])
            names = " & ".join(b["name"] for b in bd["books"])
            st = bd["books"][0]["status"]
            bgrect = f'<rect width="{bw}" height="{bh}" fill="{LINEN}"/>'
            thumb = svgbox(bgrect + c, bw, bh, 1.95)
            cells += f'<div style="width:1.95in">{thumb}<p style="font-size:7pt;margin-top:3px"><b>Board {bd["no"]:02d}</b> {esc(names)} <span class="st {st.split()[0]}">{st}</span></p></div>'
        add(f'<div class="k">14 · All covers</div><h1 style="font-size:22pt">Board covers {chunk[0]["no"]:02d}-{chunk[-1]["no"]:02d}</h1><div style="display:flex;flex-wrap:wrap;gap:.12in .14in">{cells}</div>')

    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}@page{{size:11.69in 8.27in;margin:0}}</style></head><body>{"".join(pages)}</body></html>'


# ==================================================================== INSTRUCTIONS
def fabric_rows(bds):
    from excel import fabric_entries
    rows, a = [], .04
    for bd in bds:
        if not bd["ready"]:
            continue
        b = bd["books"][0]
        for label, n, g, noted in fabric_entries(bd):
            area = (g["w"] + 2 * a) * (g["h"] + 2 * a)
            per = area * P["copies"] * (1 + P["wastage"]) / (P["fabric_width_in"] * 39.37)
            possible = int(noted * P["fabric_width_in"] * 39.37 / (area * (1 + P["wastage"]))) if noted else None
            rows.append((bd["no"], " & ".join(x["name"] for x in bd["books"]), label, n, g["w"], g["h"], per, per * n, noted, possible))
    return rows


def instructions(books, bds, spine_in, stack_mm, hw_pages):
    pages, n = [], 0

    def add(inner):
        nonlocal n
        n += 1
        pages.append(page("Pt", inner, n, "BOOK PRODUCTION INSTRUCTIONS"))

    ready = [bd for bd in bds if bd["ready"]]
    add(f'''<div class="k">Instructions</div><h1 style="font-size:36pt">Curated Fabrics Collection<br>Book Production Instructions</h1>
      <p class="lead">Everything needed to build the book, taken from the handwritten notes and cross-checked against the Sep 2026 price list and the e-catalogue. Open questions are listed - nothing is guessed.</p>
      <h2>The book</h2><table><tr><th>Item</th><th>Specification</th><th>Source</th></tr>
      <tr><td>Master binder cover</td><td>{P["cover_w"]} × {P["cover_h"]} in, {P["ring_mm"]} mm 4-D-ring, spine {spine_in} in</td><td>Notes p.4; reference binder; spine from leaf stack</td></tr>
      <tr><td>Inside boards</td><td>{P["board_w"]} × {P["board_h"]} in per panel; 2-fold or 3-fold</td><td>Notes p.4</td></tr>
      <tr><td>Collections</td><td>20 on 19 boards (Eeco Dimout + Double Shade share one, 1 page each)</td><td>Notes p.1, p.3</td></tr>
      <tr><td>Front covering</td><td>Photo + book name on every board; final book front "Trending - Curated Fabrics Collection"</td><td>Brief</td></tr>
      <tr><td>Branding</td><td>None - no logo, company name or contact anywhere</td><td>Brief</td></tr>
      <tr><td>Order</td><td>By light control (sheer → lining), then fabric weight</td><td>Design Guide p.3</td></tr>
      <tr><td>Status</td><td>{len([b for b in ready if not b.get("draft")])} leaves confirmed · {len([b for b in ready if b.get("draft")])} draft layouts to confirm · {len(bds) - len(ready)} covers only, inside waits for shade lists</td><td>-</td></tr></table>
      <h2>Files in this pack</h2><table><tr><th>File</th><th>Use</th></tr>
      <tr><td>01_Instructions_Curated_Fabrics_Book.xlsx</td><td>Working sheet - parameters, book list, board plan, shade register, fabric metres (live formulas), steps, questions</td></tr>
      <tr><td>02_Instructions_Curated_Fabrics_Book.pdf</td><td>This document, with the handwritten notes as an appendix</td></tr>
      <tr><td>03_Design_Guide_Curated_Fabrics_Book.pdf</td><td>How the book looks and why</td></tr>
      <tr><td>04_Print_Ready/</td><td>CMYK print files - master binder cover + one duplex file per leaf</td></tr></table>''')

    # book list
    rows = ""
    board_of = {b["id"]: bd for bd in bds for b in bd["books"]}
    for b in books:
        bd = board_of[b["id"]]
        mains = ", ".join(m for m in b["mains"] if m) or (f'{len(b["mains"])} TBC' if b["mains"] else "-")
        rows += (f'<tr><td>{b["seq"]:02d}</td><td><b>{esc(b["name"])}</b></td><td><span class="chip" style="background:{ladder_color(b["cat"])}"></span>{CATNAME[b["cat"]]}</td>'
                 f'<td>{bd["fold"] or "-"}{" *" if bd["fold_src"] == "derived" else ""}</td><td>{b["shades"] or "-"}</td><td>{mains}</td>'
                 f'<td>{b["gsm"] or "-"}</td><td><span class="st {b["status"].split()[0]}">{b["status"]}</span></td></tr>')
    add(f'''<div class="k">Book list</div><h1>20 collections, in book order</h1>
      <table><tr><th>No.</th><th>Book</th><th>Light control</th><th>Fold</th><th>Shades</th><th>Main</th><th>GSM</th><th>Status</th></tr>{rows}</table>
      <p style="margin-top:.1in">* Fold not written in the notes - derived from the shade count (1 hero panel + ⌈others ÷ 18⌉ swatch panels, minimum 2).</p>
      <div class="note">Also in the notes but not on the book list: <b>{EXTRA["name"]}</b> - 803 main, 14 shades (price list: 3 Pass Plain Blackout 801-830, 14 colours). Add as a 21st book?</div>''')

    # board cards, 3 per page
    cards = []
    for bd in bds:
        names = " & ".join(b["name"] for b in bd["books"])
        b = bd["books"][0]
        fold = bd["fold"]
        if bd["ready"]:
            ow = open_size(fold)[0]
            pan = "".join(f'<tr><td>{pn["letter"]}</td><td>{"Hero - main " + ", ".join(s or "TBC" for s in pn["shades"]) if pn["kind"] == "hero" else (pn.get("title") or "Shades") + " - " + str(len(pn["shades"])) + " swatches"}</td>'
                          f'<td>{("waterfall of " + str(pn["grid"]["rows"])) if pn["grid"].get("waterfall") else (str(pn["grid"]["cols"]) + " × " + str(pn["grid"]["rows"]))}</td><td>{pn["grid"]["w"]:.2f} × {pn["grid"]["h"]:.2f} in</td></tr>' for pn in bd["panels"])
            dnote = f'<div class="note"><b>DRAFT layout</b> - provisional count from {esc(draft_src(bd))}. Confirm before print.</div>' if bd.get("draft") else ""
            body = f'{dnote}<p>Open size {ow:.3f} × {P["board_h"]} in · {fold}-fold ({bd["fold_src"]}) · cover = outside of panel B</p><table><tr><th>Panel</th><th>Content</th><th>Grid</th><th>Cut each swatch</th></tr>{pan}</table>'
        else:
            body = f'<p>Fold: {fold or "not written"} · Cover printed now. Inside layout is generated as soon as the shade list is confirmed in the Excel.</p>'
        issues = "".join(f"<li>{esc(q)}</li>" for bk in bd["books"] for q in bk["issues"])
        notes = " / ".join(esc(bk["notes"]) for bk in bd["books"])
        cards.append(f'''<div style="border-top:2px solid {ladder_color(b["cat"])};padding-top:.08in;margin-bottom:.16in">
          <div style="display:flex;justify-content:space-between;align-items:baseline"><h2 style="margin:0">Board {bd["no"]:02d} · {esc(names)}</h2><span class="st {b["status"].split()[0]}">{b["status"]}</span></div>
          <p style="color:#6E655A"><i>Notes:</i> {notes}</p>{body}{f"<ul>{issues}</ul>" if issues else ""}</div>''')
    for i in range(0, len(cards), 3):
        add(f'<div class="k">Board-by-board</div><h1 style="font-size:20pt">What to make</h1>{"".join(cards[i:i + 3])}')

    # fabric
    fr = fabric_rows(bds)
    trs = "".join(f'<tr><td>{r[0]:02d}</td><td>{esc(r[1])}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]:.2f} × {r[5]:.2f}</td><td>{r[6]:.2f}</td><td>{r[7]:.2f}</td>'
                  f'<td>{r[8] if r[8] else "-"}</td><td>{r[9] if r[9] else "-"}</td></tr>' for r in fr)
    total = sum(r[7] for r in fr)
    add(f'''<div class="k">Fabric</div><h1>Fabric needed for {P["copies"]} books</h1>
      <p>Metres per shade = (W + 2 mm) × (H + 2 mm) × {P["copies"]} books × {1 + P["wastage"]:.2f} wastage ÷ ({P["fabric_width_in"]} in × 39.37). Change copies or wastage in the Excel Parameters sheet - all figures update.</p>
      <table style="margin-top:.1in"><tr><th>Board</th><th>Book</th><th>Role</th><th>Qty</th><th>Swatch (in)</th><th>m / shade</th><th>m total</th><th>m noted / shade</th><th>Books from noted m</th></tr>{trs}
      <tr><td></td><td><b>Total</b></td><td></td><td></td><td></td><td></td><td><b>{total:.1f}</b></td><td></td><td></td></tr></table>
      <div class="note">Reading the check: Texture Dimout notes give 1 m per shade - enough for the number of books shown. Where noted metres are far above need, the extra is buffer for re-makes and showroom hangers.</div>''')

    # questions
    qs = [(b["name"], q) for b in books for q in b["issues"]]
    qs.append(("3 Pass Blackout", EXTRA["issue"]))
    qs.append(("All", f"Binder: 19 leaves stack to {stack_mm:.0f} mm on 350 GSM card -> {P['ring_mm']} mm 4-D-ring binder. Confirm card leaves (as in the reference binder) rather than rigid greyboard (10 cm, too thick for rings)."))
    qs.append(("All", "Covers use illustrated curtain art (final). Optional: supply a lifestyle photo per collection to replace it."))
    trs = "".join(f"<tr><td>{i}</td><td><b>{esc(bk)}</b></td><td>{esc(q)}</td></tr>" for i, (bk, q) in enumerate(qs, 1))
    add(f'<div class="k">Decisions needed</div><h1>Open questions</h1><table><tr><th>#</th><th>Book</th><th>Question</th></tr>{trs}</table>')

    # transcription
    trs = "".join(f'<h2 style="font-size:12pt">{esc(pg)}</h2><p>{esc(t)}</p>' for pg, t in TRANSCRIPT)
    add(f'<div class="k">Appendix A</div><h1>Handwritten notes - transcription</h1>{trs}')

    # handwritten pages
    for i, p in enumerate(hw_pages, 1):
        add(f'<div class="k">Appendix B · handwritten notes page {i} of {len(hw_pages)}</div>'
            f'<div style="text-align:center;margin-top:.15in"><img src="file://{p}" style="width:6.9in;height:9.6in;object-fit:contain"></div>')

    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}@page{{size:8.27in 11.69in;margin:0}}</style></head><body>{"".join(pages)}</body></html>'


# ==================================================================== BOOK PROOF
def book_proof(books, bds, spine_in):
    """A3 landscape preview of the finished book: binder, then every leaf closed, inside and outside."""
    pages, n = [], 0
    PW, PH = 16.54, 11.69

    def add(inner):
        nonlocal n
        n += 1
        pages.append(f'<section class="pg" style="width:{PW}in;height:{PH}in;padding:.5in .6in">{inner}'
                     f'<div class="foot"><span>CURATED FABRICS COLLECTION  ·  BOOK PROOF - FOR APPROVAL, NOT FOR PRINT</span><span>{n:02d}</span></div></section>')

    W, H, j = P["cover_w"], P["cover_h"], P["joint"]
    front, _ = master_front(0, W, H, books)
    total = W + j + spine_in + j + W
    wrap = (f'<rect width="{total}" height="{H}" fill="{LINEN}"/>' + master_back(0, W, H, books) + spine_art(W + j, spine_in, H)
            + master_front(W + j + spine_in + j, W, H, books)[0])
    add(f'''<div style="display:flex;gap:.6in;align-items:center;height:100%">
      <div>{svgbox(f'<rect width="{W}" height="{H}" fill="{LINEN}"/>' + front, W, H, 8.4)}</div>
      <div style="flex:1"><div class="k">Book proof</div><h1 style="font-size:40pt">Curated Fabrics<br>Collection</h1>
      <p class="lead">The finished book as a customer sees it: the binder front, then every collection leaf - closed (photo + name), opened (the mood-board) and its back.</p>
      <p style="margin-top:.25in">4-D-ring binder {W} × {H} in · {len(bds)} fold-out leaves 9 × 12 in · ordered sheer → lining.<br>
      Cover arches carry illustrated curtain art; a lifestyle photo can replace any of them without changing the layout.</p></div></div>''')
    add(f'''<div class="k">Binder - back · spine · front</div><h1 style="font-size:22pt">Closed binder, opened flat</h1>
      <div style="margin-top:.2in">{svgbox(wrap, total, H, 15.3)}</div>''')

    for bd in bds:
        names = " & ".join(b["name"] for b in bd["books"])
        fold = bd["fold"] or 2
        ow = open_size(fold)[0]
        cov, _ = cover_panel(0, P["board_w"], bd["books"])
        cov_svg = svgbox(f'<rect width="{P["board_w"]}" height="{P["board_h"]}" fill="{LINEN}"/>' + cov, P["board_w"], P["board_h"], 4.6)
        out_art, *_r = outside_art(bd)
        out_svg = svgbox(f'<rect width="{ow}" height="{P["board_h"]}" fill="{LINEN}"/>' + out_art, ow, P["board_h"], 10.2 * ow / open_size(3)[0])
        if bd["ready"]:
            in_svg = svgbox(f'<rect width="{ow}" height="{P["board_h"]}" fill="{PAPER}"/>' + inside_art(bd), ow, P["board_h"], 10.2 * ow / open_size(3)[0])
        else:
            in_svg = (f'<div style="width:{10.2 * ow / open_size(3)[0]:.2f}in;height:{10.2 * P["board_h"] / open_size(3)[0]:.2f}in;border:1px dashed #B4A894;'
                      f'display:flex;align-items:center;justify-content:center;background:{PAPER}"><p class="lead" style="text-align:center">Inside layout waits for the shade list<br>'
                      f'<span style="font-size:10pt">{esc("; ".join(q for b in bd["books"] for q in b["issues"][:1]))}</span></p></div>')
        st = bd["books"][0]["status"]
        badge = '<span class="st Pending">DRAFT layout - provisional count</span>' if bd.get("draft") else f'<span class="st {st.split()[0]}">{st}</span>'
        add(f'''<div style="display:flex;justify-content:space-between;align-items:baseline">
          <div><div class="k">Leaf {bd["no"]:02d} of {len(bds)} · {fold}-fold · {CATNAME[bd["books"][0]["cat"]]}</div><h1 style="font-size:24pt;margin-bottom:.1in">{esc(names)}</h1></div>{badge}</div>
          <div style="display:flex;gap:.4in">
            <div>{cov_svg}<p style="margin-top:4px"><b>Closed</b> - front covering (photo + name)</p></div>
            <div><div>{in_svg}</div><p style="margin:4px 0 .18in"><b>Opened</b> - inside, the mood-board</p>
                 <div>{out_svg}</div><p style="margin-top:4px"><b>Back</b> - outside of the leaf (cover + spec plate)</p></div></div>''')
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}@page{{size:{PW}in {PH}in;margin:0}}</style></head><body>{"".join(pages)}</body></html>'


# ==================================================================== FILL-IN FORM
def missing_form(books, bds):
    """Printable hand-fill form: every missing value, every blank swatch slot."""
    pages, n = [], 0

    def add(inner):
        nonlocal n
        n += 1
        pages.append(page("Pt", inner, n, "MISSING DATA FORM - FILL BY HAND, PHOTOGRAPH, SEND BACK"))

    line = '<span style="display:inline-block;border-bottom:1px solid #8C8273;min-width:{w}in;height:.2in"></span>'
    blocks = []
    for bd in bds:
        names = " & ".join(b["name"] for b in bd["books"])
        qs = [q for b in bd["books"] for q in b["issues"]]
        blanks = []
        if bd["ready"]:
            for pn in bd["panels"]:
                for k, s in enumerate(pn["shades"], 1):
                    if not s:
                        blanks.append(f'{pn["letter"]}{k:02d}')
        conf = ""
        if bd.get("draft") or not bd["ready"]:
            conf = (f'<p><b>Confirm or correct:</b> Fold {line.format(w=.6)} &nbsp; Total shades {line.format(w=.6)} &nbsp; '
                    f'Main shade(s) {line.format(w=1.8)}</p>')
            if not bd["ready"]:
                conf += f'<p>Shade numbers (in book order):</p><p style="line-height:2.1">' + " ".join(line.format(w=.62) for _ in range(30)) + "</p>"
        if not (qs or blanks or conf):
            continue
        qhtml = "".join(f'<li>{esc(q)}<br>Answer: {line.format(w=5.6)}</li>' for q in qs)
        bhtml = ""
        if blanks:
            bhtml = ('<p><b>Shade No. for each blank slot</b> (slot ID is printed next to the swatch frame):</p><div style="display:flex;flex-wrap:wrap;gap:.06in .18in">' +
                     "".join(f'<span style="width:1.55in;font-size:8pt">{sid}&nbsp; No. {line.format(w=.85)}</span>' for sid in blanks) + "</div>")
        st = "DRAFT" if bd.get("draft") else bd["books"][0]["status"]
        blocks.append(f'''<div style="border-top:2px solid {ladder_color(bd["books"][0]["cat"])};padding-top:.06in;margin-bottom:.18in;break-inside:avoid">
          <div style="display:flex;justify-content:space-between"><h2 style="margin:0">Leaf {bd["no"]:02d} · {esc(names)}</h2><span class="st {st.split()[0]}">{st}</span></div>
          {conf}<ul>{qhtml}</ul>{bhtml}</div>''')
    add(f'''<div class="k">Missing data form</div><h1>What we still need from you</h1>
      <p class="lead">Fill this in by hand - like the notebook - photograph the pages and send them back. Every answer drops straight into the Excel and the print files are regenerated.</p>
      <div class="note">Also decide: add <b>{EXTRA["name"]}</b> (803 main, 14 shades) as a 21st book? &nbsp; YES / NO</div>''')
    # flow blocks into pages by a rough height budget
    cur, h = [], 0
    for b in blocks:
        est = 1.0 + b.count("<li>") * .45 + b.count("No. ") * .045 + (2.4 if "in book order" in b else 0) + (.4 if "Confirm or correct" in b else 0)
        if cur and h + est > 9.6:
            add("".join(cur)); cur, h = [], 0
        cur.append(b); h += est
    if cur:
        add("".join(cur))
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}@page{{size:8.27in 11.69in;margin:0}}</style></head><body>{"".join(pages)}</body></html>'
