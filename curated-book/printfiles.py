"""Print-ready PDF sheets: crop marks, bleed, turn-ins, fold ticks, slug, TrimBox/BleedBox, CMYK."""

import glob
import os
import subprocess

import pymupdf

from art import FONT_CSS, LINEN, PAPER, INK, T, inside_art, outside_art, master_front, master_back, spine_art
from data import P
from layout import open_size, panel_widths, panel_x

SLUG = 0.5
VERSION = "v1"


def chromium():
    found = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))
    return found[-1] if found else None


def html_page(svg, w, h):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}
@page{{size:{w}in {h}in;margin:0}} html,body{{margin:0;padding:0}} svg{{display:block}}</style></head>
<body><svg xmlns="http://www.w3.org/2000/svg" width="{w}in" height="{h}in" viewBox="0 0 {w} {h}">{svg}</svg></body></html>"""


def sheet(art, art_w, art_h, ext, bg, ticks, slug):
    """art drawn in a (art_w x art_h) coordinate box; ext = turn-in (wrap) or -inset (liner) beyond it."""
    cut_w, cut_h = art_w + 2 * ext, art_h + 2 * ext
    b = P["bleed"]
    pw, ph = cut_w + 2 * (b + SLUG), cut_h + 2 * (b + SLUG)
    ox = oy = SLUG + b + ext                     # art origin on the page
    cx0, cy0 = SLUG + b, SLUG + b               # cut rectangle
    marks = []
    for x in (cx0, cx0 + cut_w):
        for y in (cy0, cy0 + cut_h):
            dx = -1 if x == cx0 else 1
            dy = -1 if y == cy0 else 1
            marks.append(f'<path d="M{x},{y + dy * (b + .06)} v{dy * .3} M{x + dx * (b + .06)},{y} h{dx * .3}" stroke="#000" stroke-width=".005"/>')
    for t in ticks:                              # board edges & hinges (fold lines)
        x = ox + t
        marks.append(f'<path d="M{x},{cy0 - b - .06} v-.3 M{x},{cy0 + cut_h + b + .06} v.3" stroke="#000" stroke-width=".005" stroke-dasharray=".04 .03"/>')
    marks.append(T(cx0, ph - .2, slug, "PP", 400, 6, "#000"))
    svg = (f'<rect x="{cx0 - b}" y="{cy0 - b}" width="{cut_w + 2 * b}" height="{cut_h + 2 * b}" fill="{bg}"/>'
           f'<g transform="translate({ox} {oy})">{art}</g>' + "".join(marks))
    boxes = dict(trim=(cx0, cy0, cx0 + cut_w, cy0 + cut_h), bleed=(cx0 - b, cy0 - b, cx0 + cut_w + b, cy0 + cut_h + b))
    return svg, pw, ph, boxes


class Renderer:
    def __enter__(self):
        from playwright.sync_api import sync_playwright
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(executable_path=chromium())
        self.page = self.browser.new_page()
        return self

    def __exit__(self, *a):
        self.browser.close()
        self.pw.stop()

    def pdf(self, html, path, w, h):
        tmp = path + ".html"
        open(tmp, "w").write(html)
        self.page.goto("file://" + tmp)
        self.page.evaluate("document.fonts.ready")
        self.page.wait_for_timeout(150)
        self.page.pdf(path=path, width=f"{w}in", height=f"{h}in", print_background=True,
                      margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        os.remove(tmp)


def to_cmyk(src, dst, boxes_list):
    subprocess.run(["gs", "-q", "-o", dst, "-sDEVICE=pdfwrite", "-sColorConversionStrategy=CMYK",
                    "-sProcessColorModel=DeviceCMYK", "-dPDFSETTINGS=/prepress", "-dAutoRotatePages=/None",
                    "-dEmbedAllFonts=true", src], check=True)
    d = pymupdf.open(dst)
    for page, boxes in zip(d, boxes_list):
        for name, (x0, y0, x1, y1) in boxes.items():
            r = pymupdf.Rect(x0 * 72, y0 * 72, x1 * 72, y1 * 72)
            (page.set_bleedbox if name == "bleed" else page.set_trimbox)(r)
    d.save(dst + ".tmp", garbage=3, deflate=True)
    d.close()
    os.replace(dst + ".tmp", dst)


def draft_src(bd):
    return "; ".join(b["draft"]["src"] for b in bd["books"] if b.get("draft") and b["status"] != "Confirmed")


def board_files(r, bd, outdir):
    """Board PDF: page 1 outside wrap (with cover), page 2 inside liner (when layout is confirmed)."""
    fold = bd["fold"] or 2
    ow, oh = open_size(fold)
    names = " & ".join(b["name"] for b in bd["books"])
    ticks = [0, ow] + [panel_x(fold, i) - P["hinge"] for i in range(1, fold)] + [panel_x(fold, i) for i in range(1, fold)]
    art, xs, ws, real = outside_art(bd)
    photo_note = "COVER: lifestyle photo" if real else "COVER: illustrated curtain art (final) - a photo saved as assets/photos/<book-id>.jpg replaces it"
    pages, boxes = [], []
    svg, pw, ph, bx = sheet(art, ow, oh, 0, LINEN, ticks,
                            f"BOARD {bd['no']:02d}  {names.upper()}  |  SIDE 1 OUTSIDE  |  leaf {ow:.3f} x {oh} in, {fold}-fold, 350 GSM card, "
                            f"bleed {P['bleed']} in  |  dashed ticks = score/fold lines  |  4-ring punch on the right 1 in of this side  |  {photo_note}  |  {VERSION}")
    tmp = []
    p1 = os.path.join(outdir, f".b{bd['no']}-out.pdf")
    r.pdf(html_page(svg, pw, ph), p1, pw, ph)
    tmp.append(p1); boxes.append(bx)
    if bd["ready"]:
        lt = [t for t in ticks if 0 < t < ow]
        svg, pw, ph, bx = sheet(inside_art(bd), ow, oh, 0, PAPER, lt,
                                f"BOARD {bd['no']:02d}  {names.upper()}  |  SIDE 2 INSIDE (back-up, turn on long edge)  |  leaf {ow:.3f} x {oh} in  |  "
                                f"grey frames = swatch glue guides, cut swatches 1 mm larger  |  "
                                + (f"DRAFT LAYOUT - provisional count ({draft_src(bd)}) - confirm before print  |  " if bd.get("draft") else "")
                                + VERSION)
        p2 = os.path.join(outdir, f".b{bd['no']}-in.pdf")
        r.pdf(html_page(svg, pw, ph), p2, pw, ph)
        tmp.append(p2); boxes.append(bx)
    merged = os.path.join(outdir, f".b{bd['no']}-rgb.pdf")
    m = pymupdf.open()
    for t in tmp:
        m.insert_pdf(pymupdf.open(t))
    m.save(merged)
    slug = "_".join(b["name"].replace(" ", "-") for b in bd["books"])
    final = os.path.join(outdir, f"Board_{bd['no']:02d}_{slug}.pdf")
    to_cmyk(merged, final, boxes)
    for t in tmp + [merged]:
        os.remove(t)
    return final, real


def spine_width(bds):
    """Leaf stack -> smallest standard 4-D-ring that holds it with 25 % headroom -> binder spine."""
    stack = sum((bd["fold"] or 3) * (P["board_mm"] + P["fabric_mm"]) for bd in bds)
    ring = next((r for r in P["rings_mm"] if r >= stack * 1.25), P["rings_mm"][-1])
    P["ring_mm"] = ring
    return round((ring + 2 * P["case_board_mm"] + 12) / 25.4, 3), stack   # + boards + mechanism


def master_files(r, bds, books, outdir):
    sw, stack = spine_width(bds)
    W, H, j = P["cover_w"], P["cover_h"], P["joint"]
    total = W + j + sw + j + W
    back = master_back(0, W, H, books)
    front, real = master_front(W + j + sw + j, W, H, books)
    spine = spine_art(W + j, sw, H)
    art = back + spine + front
    ticks = [0, W, W + j, W + j + sw, W + j + sw + j, total]
    svg, pw, ph, bx = sheet(art, total, H, P["turn_in"], LINEN, ticks,
                            f"MASTER BINDER COVER WRAP  |  back {W} + joint {j} + spine {sw} + joint {j} + front {W} = {total:.3f} x {H} in  |  "
                            f"{P['ring_mm']} mm 4-D-ring for a {stack:.0f} mm stack of {len(bds)} leaves  |  turn-in {P['turn_in']} in  |  {VERSION}")
    tmp = os.path.join(outdir, ".master-rgb.pdf")
    r.pdf(html_page(svg, pw, ph), tmp, pw, ph)
    final = os.path.join(outdir, "00_Master_Binder_Cover_Front-Spine-Back.pdf")
    to_cmyk(tmp, final, [bx])
    os.remove(tmp)
    # front-only proof at 11 x 13 for approvals / digital use
    fsvg = f'<rect width="{W}" height="{H}" fill="{LINEN}"/>' + master_front(0, W, H, books)[0]
    tmp = os.path.join(outdir, ".front.pdf")
    r.pdf(html_page(fsvg, W, H), tmp, W, H)
    return final, tmp, sw, stack
