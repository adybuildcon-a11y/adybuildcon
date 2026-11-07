#!/usr/bin/env python3
"""Build the SARTA B.Tech Minor Project Presentation II deck (22 slides, 16:9).

Usage:  python build_sarta_deck.py [--icons DIR] [--out FILE]

Produces a native .pptx (python-pptx) with an executive dark theme, native
PowerPoint tables, a native bar chart, and replaceable image placeholders
(each placeholder is a real picture: right-click -> Change Picture).
The ChatGPT / DALL-E prompt for every placeholder is in the speaker notes.
"""
import argparse
import os
import copy

from lxml import etree
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt, Emu

HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------
# Theme
# ----------------------------------------------------------------------------
BG = "0B1120"       # slide background
BG2 = "0F172A"      # alt background / table rows
CARD = "1E293B"     # card fill
BORDER = "334155"   # subtle borders
TEXT = "F8FAFC"     # primary text
MUTED = "94A3B8"    # secondary text
EM = "10B981"       # tech emerald
CY = "38BDF8"       # electric cyan
IN = "6366F1"       # indigo (fills)
IN_T = "818CF8"     # indigo tuned for text on dark
RED = "F87171"
AMBER = "FBBF24"

HEAD = "Segoe UI"
BODY = "Calibri"
MONO = "Consolas"
MATH = "Cambria Math"

SW, SH = 13.333, 7.5
M = 0.6                      # side margin
CW = SW - 2 * M              # content width
TOP = 1.65                   # content top
BOTTOM = 6.75                # content bottom
TOTAL = 22

ACCENT_NAME = {EM: "emerald", CY: "cyan", IN: "indigo", IN_T: "indigo",
               TEXT: "white", RED: "red", AMBER: "amber", MUTED: "muted"}


def rgb(h):
    return RGBColor.from_string(h)


def blend(fg, bg, a):
    """Alpha-blend hex fg over hex bg (a = opacity of fg)."""
    f = [int(fg[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(bg[i:i + 2], 16) for i in (0, 2, 4)]
    return "".join(f"{round(f[i] * a + b[i] * (1 - a)):02X}" for i in range(3))


# ----------------------------------------------------------------------------
# Low-level helpers
# ----------------------------------------------------------------------------
def _style_run(run, font=BODY, size=14, color=TEXT, bold=False, italic=False,
               spc=None, baseline=None):
    f = run.font
    f.name = font
    f.size = Pt(size)
    f.bold = bold
    f.italic = italic
    f.color.rgb = rgb(color)
    rPr = run._r.get_or_add_rPr()
    if spc is not None:
        rPr.set("spc", str(int(spc)))
    if baseline is not None:
        rPr.set("baseline", str(int(baseline)))
    # East-Asian / complex-script fallbacks so symbols resolve sensibly
    for tag in ("a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set("typeface", font)


def _set_bullet(p, char="•", color=EM, marL=0.22, indent=-0.2, size_pct=100):
    pPr = p._p.get_or_add_pPr()
    pPr.set("marL", str(int(Inches(marL))))
    pPr.set("indent", str(int(Inches(indent))))
    for tag in ("a:buClr", "a:buSzPct", "a:buFont", "a:buChar", "a:buNone"):
        for el in pPr.findall(qn(tag)):
            pPr.remove(el)
    buClr = etree.SubElement(pPr, qn("a:buClr"))
    etree.SubElement(buClr, qn("a:srgbClr")).set("val", color)
    etree.SubElement(pPr, qn("a:buSzPct")).set("val", str(size_pct * 1000))
    etree.SubElement(pPr, qn("a:buFont")).set("typeface", "Arial")
    etree.SubElement(pPr, qn("a:buChar")).set("char", char)


def _no_bullet(p):
    pPr = p._p.get_or_add_pPr()
    if pPr.find(qn("a:buNone")) is None:
        etree.SubElement(pPr, qn("a:buNone"))


def R(text, **style):
    """A run spec."""
    return (text, style)


def P(*runs, align="l", after=0, before=0, bullet=None, bullet_color=EM,
      line=None, marL=0.22, **default):
    """A paragraph spec. runs may be plain strings or R(...) tuples."""
    rr = []
    for r in runs:
        if isinstance(r, str):
            rr.append((r, {}))
        else:
            rr.append(r)
    return dict(runs=rr, align=align, after=after, before=before, bullet=bullet,
                bullet_color=bullet_color, line=line, marL=marL, default=default)


ALIGN = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}
ANCHOR = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}


def fill_tf(tf, paras, anchor="t", margin=(0, 0, 0, 0), wrap=True):
    tf.word_wrap = wrap
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.vertical_anchor = ANCHOR[anchor]
    tf.margin_left, tf.margin_top, tf.margin_right, tf.margin_bottom = [Inches(v) for v in margin]
    if isinstance(paras, dict):
        paras = [paras]
    for i, pd in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = ALIGN[pd["align"]]
        if pd["after"]:
            p.space_after = Pt(pd["after"])
        if pd["before"]:
            p.space_before = Pt(pd["before"])
        if pd["line"]:
            p.line_spacing = pd["line"]
        if pd["bullet"]:
            _set_bullet(p, pd["bullet"], pd["bullet_color"], marL=pd["marL"],
                        indent=-(pd["marL"] - 0.02))
        else:
            _no_bullet(p)
        for text, st in pd["runs"]:
            s = dict(pd["default"])
            s.update(st)
            run = p.add_run()
            run.text = text
            _style_run(run, **s)


def text(slide, x, y, w, h, paras, anchor="t", margin=(0, 0, 0, 0), name=None, wrap=True):
    shp = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    fill_tf(shp.text_frame, paras, anchor=anchor, margin=margin, wrap=wrap)
    if name:
        shp.name = name
    return shp


def shape(slide, kind, x, y, w, h, fill=CARD, line=None, line_w=0.75, radius=0.1,
          name=None, dash=None):
    shp = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.shadow.inherit = False
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = rgb(fill)
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = rgb(line)
        shp.line.width = Pt(line_w)
        if dash:
            shp.line.dash_style = dash
    if kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        shp.adjustments[0] = min(0.5, radius / min(w, h))
    if name:
        shp.name = name
    # Remove theme text colouring from the shape's own (empty) text frame
    shp.text_frame.margin_left = shp.text_frame.margin_right = Inches(0)
    return shp


def card(slide, x, y, w, h, fill=CARD, line=BORDER, radius=0.12, name=None):
    return shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=fill,
                 line=line, radius=radius, name=name)


class Ctx:
    icons = None


def icon(slide, x, y, size, name, color=EM):
    path = os.path.join(Ctx.icons, f"{name}_{ACCENT_NAME[color]}.png")
    pic = slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(size), Inches(size))
    pic.name = f"Icon {name}"
    return pic


def icon_badge(slide, x, y, d, name, color=EM, on=CARD, alpha=0.18, square=False):
    kind = MSO_SHAPE.ROUNDED_RECTANGLE if square else MSO_SHAPE.OVAL
    shape(slide, kind, x, y, d, d, fill=blend(color, on, alpha), radius=d * 0.28,
          name=f"Badge {name}")
    inset = d * 0.24
    icon(slide, x + inset, y + inset, d - 2 * inset, name, color)


def pill(slide, x, y, label, color=EM, on=BG, h=0.34, size=12, font=MONO, w=None,
         bold=False, alpha=0.16, border=True):
    if w is None:
        w = len(label) * size * 0.0082 + 0.36
    shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=blend(color, on, alpha),
          line=blend(color, on, 0.55) if border else None, line_w=0.75, radius=h / 2,
          name=f"Pill {label}")
    text(slide, x, y, w, h, P(R(label, font=font, size=size, color=color, bold=bold), align="c"),
         anchor="m")
    return w


def label(slide, x, y, w, s, color=EM, size=11, h=0.28):
    """Small uppercase section label."""
    return text(slide, x, y, w, h, P(R(s.upper(), font=HEAD, size=size, color=color, bold=True,
                                       spc=150)), anchor="m")


def notes(slide, s):
    slide.notes_slide.notes_text_frame.text = s


# ----------------------------------------------------------------------------
# Slide frame
# ----------------------------------------------------------------------------
def new_slide(prs, n, category, title, footer, chip=None):
    s = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(BG)
    # category + title
    label(s, M, 0.42, 9.0, category, color=EM, size=11, h=0.3)
    t = text(s, M, 0.74, CW if not chip else CW, 0.7,
             P(R(title, font=HEAD, size=28, bold=True, color=TEXT, spc=-10)), anchor="t",
             name="Title")
    # make the title discoverable as the slide title for accessibility
    t.name = "Title"
    if chip:
        w = len(chip) * 11 * 0.0083 + 0.5
        x = SW - M - w
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, 0.4, w, 0.34, fill=CARD, line=BORDER,
              radius=0.17, name="Module chip")
        text(s, x, 0.4, w, 0.34, P(R("</> ", font=MONO, size=11, color=MUTED),
                                   R(chip, font=MONO, size=11, color=CY), align="c"),
             anchor="m")
    # footer
    text(s, M, 7.0, 8.0, 0.28, P(R(footer, font=BODY, size=10, color=MUTED)), anchor="m",
         name="Footer")
    text(s, SW - M - 2.0, 7.0, 2.0, 0.28,
         P(R(f"Slide {n}", font=MONO, size=10, color=MUTED),
           R(f" / {TOTAL}", font=MONO, size=10, color=blend(MUTED, BG, 0.55)), align="r"),
         anchor="m", name="Slide number")
    return s


# ----------------------------------------------------------------------------
# Image placeholders (real pictures -> right-click > Change Picture)
# ----------------------------------------------------------------------------
def _font(paths, size):
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


FONT_BOLD = ["/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf",
             "C:/Windows/Fonts/calibrib.ttf", "/Library/Fonts/Arial Bold.ttf"]
FONT_REG = ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf",
            "C:/Windows/Fonts/calibri.ttf", "/Library/Fonts/Arial.ttf"]


def _wrap(draw, s, font, maxw):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def make_placeholder_png(path, name, w_in, h_in, dpi=150):
    W, H = int(w_in * dpi), int(h_in * dpi)
    sc = 3  # supersample
    img = Image.new("RGBA", (W * sc, H * sc), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rad = int(0.16 * dpi * sc)
    fill = tuple(int(BG2[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    d.rounded_rectangle([0, 0, W * sc - 1, H * sc - 1], radius=rad, fill=fill)
    # dashed border
    col = tuple(int(blend(CY, BG2, 0.55)[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    lw = int(2.2 * sc)
    inset = int(0.09 * dpi * sc)
    x0, y0, x1, y1 = inset, inset, W * sc - inset, H * sc - inset
    dash, gap = int(14 * sc), int(9 * sc)

    def dashed(p0, p1):
        (ax, ay), (bx, by) = p0, p1
        length = ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5
        n = int(length // (dash + gap)) + 1
        for k in range(n):
            s0 = k * (dash + gap) / length
            s1 = min(1, (k * (dash + gap) + dash) / length)
            d.line([(ax + (bx - ax) * s0, ay + (by - ay) * s0),
                    (ax + (bx - ax) * s1, ay + (by - ay) * s1)], fill=col, width=lw)
    r2 = rad - inset
    dashed((x0 + r2, y0), (x1 - r2, y0))
    dashed((x0 + r2, y1), (x1 - r2, y1))
    dashed((x0, y0 + r2), (x0, y1 - r2))
    dashed((x1, y0 + r2), (x1, y1 - r2))
    for (cx, cy_, a0) in ((x0 + r2, y0 + r2, 180), (x1 - r2, y0 + r2, 270),
                          (x1 - r2, y1 - r2, 0), (x0 + r2, y1 - r2, 90)):
        d.arc([cx - r2, cy_ - r2, cx + r2, cy_ + r2], a0, a0 + 90, fill=col, width=lw)
    # icon
    ic = Image.open(os.path.join(Ctx.icons, "LuImage_cyan.png")).convert("RGBA")
    isz = int(0.62 * dpi * sc)
    ic = ic.resize((isz, isz), Image.LANCZOS)
    # circle behind icon
    cxp, cyp = W * sc // 2, int(H * sc * 0.36)
    cr = int(isz * 0.85)
    d.ellipse([cxp - cr, cyp - cr, cxp + cr, cyp + cr],
              fill=tuple(int(blend(CY, BG2, 0.12)[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
    img.alpha_composite(ic, (cxp - isz // 2, cyp - isz // 2))
    # text
    maxw = W * sc * 0.80
    f1 = _font(FONT_BOLD, int(0.15 * dpi * sc))
    f2 = _font(FONT_BOLD, int(0.19 * dpi * sc))
    f3 = _font(FONT_REG, int(0.12 * dpi * sc))
    yy = cyp + cr + int(0.22 * dpi * sc)
    tcol = tuple(int(CY[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    wcol = tuple(int(TEXT[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    mcol = tuple(int(MUTED[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    for ln in ["[INSERT GENERATED IMAGE HERE:"]:
        tw = d.textlength(ln, font=f1)
        d.text(((W * sc - tw) / 2, yy), ln, font=f1, fill=tcol)
        yy += int(f1.size * 1.35)
    for ln in _wrap(d, name + "]", f2, maxw):
        tw = d.textlength(ln, font=f2)
        d.text(((W * sc - tw) / 2, yy), ln, font=f2, fill=wcol)
        yy += int(f2.size * 1.3)
    yy += int(0.12 * dpi * sc)
    for ln in _wrap(d, "Right-click  >  Change Picture  >  From a File", f3, maxw):
        tw = d.textlength(ln, font=f3)
        d.text(((W * sc - tw) / 2, yy), ln, font=f3, fill=mcol)
        yy += int(f3.size * 1.35)
    img = img.resize((W, H), Image.LANCZOS)
    img.save(path)


def image_placeholder(slide, x, y, w, h, name, prompt, slide_no):
    fn = os.path.join(HERE, "assets", "placeholders", f"slide{slide_no:02d}_placeholder.png")
    make_placeholder_png(fn, name, w, h)
    pic = slide.shapes.add_picture(fn, Inches(x), Inches(y), Inches(w), Inches(h))
    pic.name = f"Image Placeholder - {name}"
    # alt text
    cNvPr = pic._element.find(".//" + qn("p:cNvPr"))
    cNvPr.set("descr", f"Placeholder for generated image: {name}")
    ratio = w / h
    aspect = "square (1024x1024)" if ratio < 1.25 else "landscape (1536x1024)"
    notes(slide,
          f"IMAGE PLACEHOLDER: {name}\n"
          f"Replace: right-click the placeholder > Change Picture > From a File. "
          f"If the new image does not fill the frame, use Picture Format > Crop > Fill.\n"
          f"Placeholder size: {w:.2f}\" x {h:.2f}\" - generate at {aspect}.\n\n"
          f"ChatGPT / DALL-E prompt:\n{prompt}")
    return pic


# ----------------------------------------------------------------------------
# Native tables
# ----------------------------------------------------------------------------
NO_STYLE = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"


def _cell_border(cell, color=BORDER, w_pt=0.75, sides=("B",)):
    tcPr = cell._tc.get_or_add_tcPr()
    for side in ("L", "R", "T", "B"):
        tag = qn(f"a:ln{side}")
        for el in tcPr.findall(tag):
            tcPr.remove(el)
    order = ["L", "R", "T", "B"]
    for i, side in enumerate(order):
        ln = etree.Element(qn(f"a:ln{side}"))
        if side in sides:
            ln.set("w", str(int(Pt(w_pt))))
            sf = etree.SubElement(ln, qn("a:solidFill"))
            etree.SubElement(sf, qn("a:srgbClr")).set("val", color)
        else:
            ln.set("w", "0")
            etree.SubElement(ln, qn("a:noFill"))
        tcPr.insert(i, ln)


def native_table(slide, x, y, col_ws, rows, header_h=0.5, row_h=0.5, header_size=13,
                 body_size=14, highlight_last=False, col_styles=None, cell_fn=None,
                 name="Table", col_fills=None):
    """rows[0] is the header. Cells may be strings or lists of P(...) specs."""
    nr, nc = len(rows), len(col_ws)
    gf = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(sum(col_ws)),
                                Inches(header_h + row_h * (nr - 1)))
    gf.name = name
    tbl = gf.table
    tblPr = tbl._tbl.tblPr
    for a in ("firstRow", "bandRow", "firstCol", "lastRow", "lastCol", "bandCol"):
        tblPr.set(a, "0")
    sid = tblPr.find(qn("a:tableStyleId"))
    if sid is None:
        sid = etree.SubElement(tblPr, qn("a:tableStyleId"))
    sid.text = NO_STYLE
    for j, cw in enumerate(col_ws):
        tbl.columns[j].width = Inches(cw)
    for i in range(nr):
        tbl.rows[i].height = Inches(header_h if i == 0 else row_h)
    col_styles = col_styles or {}
    for i, row in enumerate(rows):
        is_head = i == 0
        is_hl = highlight_last and i == nr - 1
        if is_head:
            fillc = CARD
        elif is_hl:
            fillc = blend(EM, BG, 0.14)
        else:
            fillc = BG2 if i % 2 == 1 else "131D33"
        for j, val in enumerate(row):
            cell = tbl.cell(i, j)
            fc = fillc
            if col_fills and j in col_fills and not is_head:
                fc = blend(col_fills[j], fillc, 0.10)
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(fc)
            cell.margin_left = cell.margin_right = Inches(0.12)
            cell.margin_top = cell.margin_bottom = Inches(0.05)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            if isinstance(val, (list, dict)):
                paras = val
            elif is_head:
                hc = col_styles.get(j, {}).get("head_color", EM)
                paras = P(R(val, font=HEAD, size=header_size, bold=True, color=hc))
            else:
                st = dict(font=BODY, size=body_size, color=TEXT)
                st.update(col_styles.get(j, {}).get("body", {}))
                if is_hl:
                    st.update(dict(bold=True, color=EM if j > 0 else TEXT))
                paras = P(R(val, **st))
            if cell_fn:
                paras = cell_fn(i, j, val, paras)
            # clear default paragraph then fill
            fill_tf(tf, paras, anchor="m", margin=(0.12, 0.05, 0.12, 0.05))
            cell.margin_left = cell.margin_right = Inches(0.12)
            cell.margin_top = cell.margin_bottom = Inches(0.05)
            sides = ("B",) if not is_head else ("B",)
            _cell_border(cell, color=EM if is_head else BORDER,
                         w_pt=1.25 if is_head else 0.75, sides=sides)
    return gf


# ----------------------------------------------------------------------------
# Slides
# ----------------------------------------------------------------------------
def s01_title(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(BG)
    x = 0.8
    label(s, x, 0.75, 7.6, "Jamia Millia Islamia · Department of Computer Engineering",
          color=EM, size=12, h=0.3)
    label(s, x, 1.1, 7.6, "B.Tech Minor Project · Presentation II (Mid-Term Implementation)",
          color=CY, size=11, h=0.3)
    text(s, x, 1.7, 7.6, 1.75,
         P(R("SARTA: ", color=EM), R("Implementation & Empirical Evaluation"),
           font=HEAD, size=42, bold=True, color=TEXT, spc=-20, line=0.95), name="Title")
    text(s, x, 3.6, 7.3, 0.85,
         P(R("End-to-End Prototype, Adaptive Testing Engine, Sandboxed Grading & "
             "Benchmark Results", font=BODY, size=18, color=MUTED)))
    # team card
    y = 4.75
    card(s, x, y, 3.95, 1.6, name="Team card")
    label(s, x + 0.25, y + 0.18, 3.5, "Presented by", color=MUTED, size=10)
    for k, (nm, roll) in enumerate((("Syed Anas Ahmed", "23BCS020"),
                                    ("Md Shahid Rasool", "23BCS021"))):
        yy = y + 0.55 + k * 0.48
        icon_badge(s, x + 0.25, yy, 0.38, "LuUser", CY)
        text(s, x + 0.75, yy - 0.02, 3.1, 0.42,
             P(R(nm, font=BODY, size=16, bold=True, color=TEXT),
               R(f"   {roll}", font=MONO, size=12, color=CY)), anchor="m")
    # supervisor card
    x2 = x + 4.25
    card(s, x2, y, 3.35, 1.6, name="Supervisor card")
    label(s, x2 + 0.25, y + 0.18, 3.0, "Supervisor", color=MUTED, size=10)
    icon_badge(s, x2 + 0.25, y + 0.58, 0.5, "LuGraduationCap", EM)
    text(s, x2 + 0.9, y + 0.52, 2.35, 0.95,
         [P(R("Dr. S M Faisal Malik", font=BODY, size=16, bold=True, color=TEXT)),
          P(R("Department of Computer Engineering", font=BODY, size=12, color=MUTED))])
    # acronym column
    ax, ay, aw, ah = 9.05, 0.75, 3.6, 5.6
    card(s, ax, ay, aw, ah, fill=blend(CARD, BG, 0.75), name="Acronym card")
    label(s, ax + 0.3, ay + 0.22, 3.0, "What SARTA stands for", color=MUTED, size=10)
    items = [("S", "Semantic", "SBERT skill alignment", EM),
             ("A", "Adaptive", "streak-based CAT engine", CY),
             ("R", "Recruitment", "JD-aware gap analysis", IN_T),
             ("T", "Technical", "sandboxed code grading", EM),
             ("A", "Assessment", "explainable skill report", CY)]
    for k, (L, word, desc, c) in enumerate(items):
        yy = ay + 0.68 + k * 0.96
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, ax + 0.3, yy, 0.66, 0.66,
              fill=blend(c, CARD, 0.2), radius=0.16, name=f"Letter {L}")
        text(s, ax + 0.3, yy, 0.66, 0.66, P(R(L, font=HEAD, size=24, bold=True, color=c),
                                           align="c"), anchor="m")
        text(s, ax + 1.15, yy + 0.02, 2.35, 0.66,
             [P(R(word, font=HEAD, size=17, bold=True, color=TEXT)),
              P(R(desc, font=BODY, size=12, color=MUTED))], anchor="m")
    text(s, M + 0.2, 7.0, 8.0, 0.28,
         P(R("SARTA · Semantic Adaptive Recruitment & Technical Assessment",
             font=BODY, size=10, color=MUTED)), anchor="m", name="Footer")
    text(s, SW - M - 2.0, 7.0, 2.0, 0.28,
         P(R("Slide 1", font=MONO, size=10, color=MUTED),
           R(f" / {TOTAL}", font=MONO, size=10, color=blend(MUTED, BG, 0.55)), align="r"),
         anchor="m")
    notes(s, "Title slide. Introduce the team, supervisor and the scope of Presentation II: "
             "the working prototype, its algorithms and the empirical benchmarks.")


def s02_problem(prs):
    s = new_slide(prs, 2, "Recap · Problem & Motivation",
                  "Traditional Screening Fails Modern Technical Hiring", "SARTA · Recap")
    label(s, M, TOP, 6, "Three critical industry bottlenecks", color=MUTED, size=10)
    cards = [
        ("LuSearch", "01", "Fragile Keyword ATS", RED,
         ["Matches literal character sequences rather than semantic competency.",
          "Fails on equivalent technologies (e.g., rejects “PostgreSQL” when looking "
          "for “SQL Relational DB”)."]),
        ("LuClipboardList", "02", "Static One-Size Assessments", AMBER,
         ["Administers the exact same fixed 20-question quiz to all candidates "
          "regardless of ability.",
          "Fails to establish upper limits for senior talent and causes disengagement "
          "for junior candidates."]),
        ("LuFileText", "03", "Resumes Evaluated in Complete Isolation", IN_T,
         ["Existing systems score resumes against generic job categories rather than "
          "tailoring testing to the specific target Job Description (JD)."]),
    ]
    cw, gap, y, h = (CW - 0.6) / 3, 0.3, TOP + 0.32, 3.15
    for k, (ic, num, title, c, bullets) in enumerate(cards):
        x = M + k * (cw + gap)
        card(s, x, y, cw, h, name=f"Bottleneck {num}")
        icon_badge(s, x + 0.25, y + 0.25, 0.5, ic, c)
        text(s, x + cw - 0.85, y + 0.28, 0.6, 0.45,
             P(R(num, font=MONO, size=18, bold=True, color=blend(c, CARD, 0.6)), align="r"),
             anchor="m")
        text(s, x + 0.25, y + 0.82, cw - 0.5, 0.62,
             P(R(title, font=HEAD, size=15, bold=True, color=TEXT), line=0.95), anchor="b")
        text(s, x + 0.25, y + 1.52, cw - 0.45, h - 1.6,
             [P(R(b, font=BODY, size=14, color=MUTED), bullet="•", bullet_color=c, after=4)
              for b in bullets])
    # pipelines
    py = y + h + 0.1
    label(s, M, py, 6, "The SARTA solution", color=MUTED, size=10)
    rows = [("Traditional", ["Resume", "Keyword Match", "Static Quiz", "Single Opaque Score"],
             MUTED, blend(MUTED, BG, 0.10)),
            ("SARTA", ["Resume + JD", "Semantic Alignment & Gap Analysis",
                       "Adaptive Dynamic Test", "Explainable Skill-Wise Report"],
             EM, blend(EM, BG, 0.14))]
    lab_w = 1.55
    for r, (name, steps, c, fillc) in enumerate(rows):
        yy = py + 0.3 + r * 0.68
        text(s, M, yy, lab_w, 0.56,
             P(R(name, font=HEAD, size=14, bold=True, color=c if r else MUTED)), anchor="m")
        n = len(steps)
        sx0 = M + lab_w
        arrow_w = 0.38
        sw_ = (CW - lab_w - arrow_w * (n - 1)) / n
        for k, st in enumerate(steps):
            sx = sx0 + k * (sw_ + arrow_w)
            shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, sx, yy, sw_, 0.56, fill=fillc,
                  line=blend(c, BG, 0.45), radius=0.1, name=f"{name} step {k+1}")
            text(s, sx + 0.1, yy, sw_ - 0.2, 0.56,
                 P(R(st, font=BODY, size=14, bold=bool(r), color=TEXT if r else MUTED),
                   align="c"), anchor="m")
            if k < n - 1:
                text(s, sx + sw_, yy, arrow_w, 0.56,
                     P(R("→", font=BODY, size=18, bold=True, color=c), align="c"), anchor="m")
    notes(s, "Recap of PPT 1: the three bottlenecks of current screening, and how the SARTA "
             "pipeline replaces keyword matching and static quizzes with semantic, JD-aware, "
             "adaptive and explainable assessment.")


def s03_arch(prs):
    s = new_slide(prs, 3, "Recap · System Architecture",
                  "Five Layers: From Document Ingestion to Explainable Verdict", "SARTA · Recap")
    iw = 5.45
    image_placeholder(s, M, TOP, iw, BOTTOM - TOP, "SARTA 5-Layer Architecture Diagram",
                      "A sleek, dark-themed 3D isometric diagram of a 5-layer software "
                      "architecture stack floating in space. Deep slate background (#0B1120). "
                      "Layers from top to bottom: 1. User Interface Layer (glowing neon blue "
                      "icons of Resume and Job Description), 2. Processing Layer (NLP vectors and "
                      "matching engine), 3. Assessment Layer (parallel branches of MCQ and Code "
                      "Editor), 4. Intelligence Layer (glowing green adaptive controller chip and "
                      "analytics engine), 5. Output Layer (holographic radar chart and report "
                      "card). Minimalist, modern UI design style, high resolution, 8k render.", 3)
    rx = M + iw + 0.35
    rw = SW - M - rx
    layers = [("User Layer", "Unified reactive interface accepting candidate resume (PDF/DOCX) "
               "and target JD.", CY, "LuMonitor"),
              ("Processing Layer", "Dual text parsing, spaCy technical NER, Sentence-BERT "
               "embedding, and Hungarian gap analysis.", CY, "LuCpu"),
              ("Assessment Layer", "Parallel item delivery: dynamic adaptive MCQs and sandboxed "
               "coding challenge.", IN_T, "LuCodeXml"),
              ("Intelligence Layer", "Streak-based adaptive difficulty controller and "
               "multidimensional scoring engine.", EM, "LuBrain"),
              ("Output Layer", "Granular skill scores, peak difficulty tags, and explainable "
               "hiring recommendation.", EM, "LuChartColumn")]
    gap = 0.14
    h = (BOTTOM - TOP - gap * 4) / 5
    for k, (nm, desc, c, ic) in enumerate(layers):
        y = TOP + k * (h + gap)
        card(s, rx, y, rw, h, name=f"Layer {k+1}")
        icon_badge(s, rx + 0.2, y + (h - 0.52) / 2, 0.52, ic, c, square=True)
        text(s, rx + 0.9, y + 0.1, rw - 1.05, h - 0.2,
             [P(R(f"LAYER {k+1}  ", font=MONO, size=11, bold=True, color=c),
                R(nm, font=HEAD, size=14, bold=True, color=TEXT), after=2),
              P(R(desc, font=BODY, size=14, color=MUTED))], anchor="m")


def s04_status(prs):
    s = new_slide(prs, 4, "Project Status · Milestones",
                  "From Proposed Blueprint to Operational System",
                  "SARTA · Implementation Status")
    pillars = [("LuFileSearch", "Extraction & Matching", EM,
                "Dual PDF/DOCX parsers, 150+ canonical skill taxonomy, SBERT embeddings, "
                "Hungarian bipartite matching."),
               ("LuDatabase", "Question Bank & Data Model", CY,
                "MongoDB Atlas repository populated with 9 technical domains across Easy, "
                "Medium, and Hard tiers."),
               ("LuGauge", "Adaptive Testing & Sandbox", IN_T,
                "Dynamic streak-based CAT controller and Judge0 CE execution sandbox with "
                "hidden test cases."),
               ("LuLayoutDashboard", "Explainable Analytics & UI", EM,
                "Reactive Next.js 16 interface, Microsoft Monaco Editor, and SVG Competency "
                "Radar chart.")]
    gap = 0.3
    cw = (CW - 3 * gap) / 4
    y, h = TOP, BOTTOM - TOP
    for k, (ic, title, c, desc) in enumerate(pillars):
        x = M + k * (cw + gap)
        card(s, x, y, cw, h, name=f"Pillar {k+1}")
        icon_badge(s, x + 0.25, y + 0.3, 0.62, ic, c)
        text(s, x + cw - 1.3, y + 0.38, 1.05, 0.45,
             P(R(f"PILLAR {k+1:02d}", font=MONO, size=10, bold=True, color=MUTED), align="r"),
             anchor="m")
        text(s, x + 0.25, y + 1.1, cw - 0.5, 0.8,
             P(R(title, font=HEAD, size=17, bold=True, color=TEXT), line=0.95), anchor="t")
        text(s, x + 0.25, y + 1.95, cw - 0.5, 0.75,
             P(R("100", font=MONO, size=40, bold=True, color=c),
               R("%", font=MONO, size=22, bold=True, color=c)), anchor="m")
        # progress bar
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + 0.25, y + 2.78, cw - 0.5, 0.1,
              fill=blend(c, CARD, 0.25), radius=0.05, name="Progress track")
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + 0.25, y + 2.78, cw - 0.5, 0.1, fill=c,
              radius=0.05, name="Progress fill")
        text(s, x + 0.25, y + 2.95, cw - 0.5, 0.3,
             P(R("OPERATIONAL", font=HEAD, size=10, bold=True, color=c, spc=150)), anchor="m")
        text(s, x + 0.25, y + 3.45, cw - 0.5, h - 3.6,
             P(R(desc, font=BODY, size=14, color=MUTED), line=1.05))


def s05_stack(prs):
    s = new_slide(prs, 5, "System Design · Architectural Decisions",
                  "Upgrades from Initial Synopsis to Final Implementation",
                  "SARTA · System Design")
    label(s, M, TOP - 0.02, 8, "Technology Stack Evolution Matrix", color=MUTED, size=10)
    rows = [["Component", "Synopsis Proposal", "Implemented Evolution", "Academic Justification"],
            ["Frontend UI", "Streamlit", "Next.js 16 + React 19 + Tailwind v4",
             "Eliminates full-page re-execution; provides sub-50ms reactive state transitions "
             "during adaptive item delivery."],
            ["In-Browser IDE", "Streamlit Ace", "Microsoft Monaco Editor (@monaco-editor/react)",
             "Industry-standard VS Code web core with syntax highlighting, autocomplete, and "
             "multi-language support."],
            ["Backend API", "FastAPI / Flask", "FastAPI 0.110 (Async Python 3.11)",
             "High-concurrency async endpoints with Pydantic type safety."],
            ["Database", "SQLite / Postgres", "MongoDB Atlas + In-Memory Fallback",
             "Document structure natively represents hierarchical skill prerequisites and "
             "nested test-case arrays."],
            ["Semantic Vectors", "spaCy + SBERT", "spaCy en_core_web_sm + all-MiniLM-L6-v2",
             "384-dimensional dense vectors with local caching and low inference overhead."]]
    cs = {0: {"body": dict(bold=True, font=HEAD, size=13)},
          1: {"body": dict(color=MUTED)},
          2: {"body": dict(color=CY, bold=True)},
          3: {"body": dict(color=TEXT)}}
    native_table(s, M, TOP + 0.3, [1.85, 1.75, 3.2, CW - 6.8], rows, header_h=0.5,
                 row_h=0.82, col_styles=cs, name="Technology Stack Evolution Matrix")


def s06_parser(prs):
    s = new_slide(prs, 6, "Module Implementation · Processing Layer",
                  "Deterministic Document Parsing", "SARTA · Module 1: Document Parsing",
                  chip="parser.py")
    iw = 5.45
    image_placeholder(s, M, TOP, iw, BOTTOM - TOP, "Document Parsing Dataflow Diagram",
                      "A modern tech vector illustration showing two glowing digital documents "
                      "(PDF and DOCX) feeding into a central glowing processing core labeled "
                      "'Document Sanitizer'. The core splits into two streams: 'Layout-Aware "
                      "pdfplumber' and 'python-docx XML Run Parser'. Both merge into a clean "
                      "stream of illuminated binary data leading to a clean white sheet of "
                      "'Normalized Text Buffer'. Minimalist, dark slate background, glowing "
                      "emerald and cyan vectors.", 6)
    rx = M + iw + 0.4
    rw = SW - M - rx
    label(s, rx, TOP - 0.02, rw, "Engineering implementation", color=MUTED, size=10)
    items = [("LuFileCode", "Dual Format Support", CY,
              "Robust ingestion of both PDF and DOCX files without external OCR overhead."),
             ("LuTable", "Layout-Aware PDF Extraction", EM,
              "Implemented via pdfplumber to maintain logical document layout and extract "
              "tabular skill matrices cleanly."),
             ("LuFileJson", "DOCX XML Run Parsing", IN_T,
              "Traverses document paragraphs and table XML runs via python-docx."),
             ("LuSparkles", "Text Normalization", EM,
              "Strips non-standard whitespace, unicode bullets, and artifacts, achieving "
              "average parse latency under 42ms.")]
    y0 = TOP + 0.38
    pitch = 0.86
    for k, (ic, t, c, d) in enumerate(items):
        y = y0 + k * pitch
        icon_badge(s, rx, y + 0.02, 0.5, ic, c, on=BG)
        text(s, rx + 0.7, y - 0.03, rw - 0.7, pitch - 0.05,
             [P(R(t, font=HEAD, size=14, bold=True, color=TEXT), after=1),
              P(R(d, font=BODY, size=14, color=MUTED))])
    # stat
    sy = y0 + 4 * pitch + 0.1
    sh = BOTTOM - sy
    card(s, rx, sy, rw, sh, fill=blend(EM, BG, 0.10), line=blend(EM, BG, 0.4), name="Latency stat")
    text(s, rx + 0.3, sy, 2.4, sh,
         P(R("< 42", font=MONO, size=34, bold=True, color=EM),
           R(" ms", font=MONO, size=18, bold=True, color=EM)), anchor="m")
    text(s, rx + 2.65, sy, rw - 2.85, sh,
         [P(R("Average parse latency", font=HEAD, size=14, bold=True, color=TEXT)),
          P(R("PDF + DOCX → normalized text buffer, no OCR", font=BODY, size=13, color=MUTED))],
         anchor="m")


def s07_nlp(prs):
    s = new_slide(prs, 7, "Module Implementation · NLP Engine",
                  "Two-Pass Skill Extraction & Dense Normalization",
                  "SARTA · Module 2: Skill Extraction", chip="nlp_engine.py")
    lw = 4.3
    # challenge card
    h1 = 2.75
    card(s, M, TOP, lw, h1, fill=blend(RED, BG, 0.07), line=blend(RED, BG, 0.35),
         name="Challenge card")
    icon_badge(s, M + 0.25, TOP + 0.25, 0.48, "LuTriangleAlert", RED, on=blend(RED, BG, 0.07))
    text(s, M + 0.85, TOP + 0.25, lw - 1.0, 0.48,
         P(R("The Extraction Challenge", font=HEAD, size=15, bold=True, color=TEXT)), anchor="m")
    text(s, M + 0.25, TOP + 0.88, lw - 0.5, 1.0,
         P(R("Standard off-the-shelf NER models fail on technical terms (misclassifying "
             "“Docker” or “Next.js” as generic nouns).", font=BODY, size=14, color=MUTED)))
    px = M + 0.25
    for tok in ("Docker", "Next.js"):
        w = pill(s, px, TOP + 2.05, f"{tok} → NOUN", color=RED, on=blend(RED, BG, 0.07), size=12)
        px += w + 0.15
    # stats
    sy = TOP + h1 + 0.3
    sh = BOTTOM - sy
    sw_ = (lw - 0.3) / 2
    for k, (big, small, c) in enumerate((("150+", "canonical tech skills in taxonomy", EM),
                                         ("384-d", "SBERT dense vectors (all-MiniLM-L6-v2)",
                                          CY))):
        x = M + k * (sw_ + 0.3)
        card(s, x, sy, sw_, sh, name=f"Stat {big}")
        text(s, x + 0.2, sy + 0.2, sw_ - 0.4, 0.75,
             P(R(big, font=MONO, size=32, bold=True, color=c)), anchor="m")
        text(s, x + 0.2, sy + 0.98, sw_ - 0.4, sh - 1.1,
             P(R(small, font=BODY, size=13, color=MUTED)))
    # steps
    rx = M + lw + 0.45
    rw = SW - M - rx
    label(s, rx, TOP - 0.02, rw, "The SARTA two-pass solution", color=MUTED, size=10)
    steps = [("Pass 1", "spaCy PhraseMatcher", EM,
              "Fast lexical scan over a curated canonical taxonomy of 150+ tech skills "
              "(Languages, Frontend, Backend, ML, Cloud)."),
             ("Pass 2", "Delimited Token Splitter", CY,
              "Regex-based parser targeting comma-separated, pipe-delimited, and bulleted "
              "resume skill lists."),
             ("Step 3", "Subsumption & Deduplication", IN_T,
              "Resolves sub-string overlap (e.g., collapses “Python 3” and “Python "
              "Programming” into canonical “Python”)."),
             ("Step 4", "Dense SBERT Embedding", EM,
              "Encodes normalized tokens into 384-dimensional vectors using Sentence-BERT "
              "(all-MiniLM-L6-v2) for semantic distance evaluation.")]
    y0 = TOP + 0.35
    gap = 0.14
    h = (BOTTOM - y0 - 3 * gap) / 4
    for k, (tag, t, c, d) in enumerate(steps):
        y = y0 + k * (h + gap)
        card(s, rx, y, rw, h, name=f"Step {k+1}")
        shape(s, MSO_SHAPE.OVAL, rx + 0.22, y + (h - 0.56) / 2, 0.56, 0.56,
              fill=blend(c, CARD, 0.2), name=f"Step num {k+1}")
        text(s, rx + 0.22, y + (h - 0.56) / 2, 0.56, 0.56,
             P(R(str(k + 1), font=MONO, size=18, bold=True, color=c), align="c"), anchor="m")
        text(s, rx + 1.0, y + 0.06, rw - 1.2, h - 0.12,
             [P(R(f"{tag.upper()}  ", font=MONO, size=11, bold=True, color=c),
                R(t, font=HEAD, size=14, bold=True, color=TEXT), after=2),
              P(R(d, font=BODY, size=14, color=MUTED))], anchor="m")


def _math(s, size=16, color=TEXT, font=MATH):
    """Mini-markup: a_{b} -> subscript run."""
    runs, i, buf = [], 0, ""
    while i < len(s):
        if s.startswith("_{", i):
            if buf:
                runs.append(R(buf, font=font, size=size, color=color))
                buf = ""
            j = s.index("}", i)
            runs.append(R(s[i + 2:j], font=font, size=size, color=color, baseline=-25000))
            i = j + 1
        else:
            buf += s[i]
            i += 1
    if buf:
        runs.append(R(buf, font=font, size=size, color=color))
    return runs


def s08_matcher(prs):
    s = new_slide(prs, 8, "Module Implementation · Matcher",
                  "Hungarian Alignment & Three-Way Gap Classification",
                  "SARTA · Module 3: Gap Analysis", chip="matcher.py")
    iw = 5.45
    image_placeholder(s, M, TOP, iw, BOTTOM - TOP, "Bipartite Hungarian Matching Graph",
                      "A digital bipartite graph on a dark slate background (#0B1120). On the "
                      "left column, glowing cyan nodes labeled 'Resume Skills' (Python, SQL, "
                      "Docker, React). On the right column, glowing purple nodes labeled 'JD "
                      "Requirements' (Python, PostgreSQL, Kubernetes, AWS). Luminous green lines "
                      "connect optimal 1-to-1 pairs with decimal weights (1.0, 0.88). One "
                      "unmatched JD node glows red with a dashed halo labeled 'Skill Gap'. "
                      "High-tech graph theory illustration.", 8)
    rx = M + iw + 0.4
    rw = SW - M - rx
    # formulation
    fh = 2.05
    card(s, rx, TOP, rw, fh, name="Mathematical formulation")
    label(s, rx + 0.25, TOP + 0.14, rw - 0.5, "Mathematical formulation", color=MUTED, size=10)
    text(s, rx + 0.25, TOP + 0.48, rw - 0.5, 1.5,
         [P(*_math("C = {c_{1}, …, c_{m}},   J = {j_{1}, …, j_{n}}", 15), after=5),
          P(*_math("Sim(c_{i}, j_{j}) = (c_{i} · j_{j}) / (||c_{i}|| ||j_{j}||)", 15, CY),
            after=6),
          P(R("Minimum-weight bipartite assignment on ", font=BODY, size=13, color=MUTED),
            R("−Sim", font=MATH, size=13, color=TEXT),
            R(" via the Hungarian Algorithm ", font=BODY, size=13, color=MUTED),
            R("scipy.optimize.linear_sum_assignment", font=MONO, size=12, color=EM))])
    # three-way
    ty = TOP + fh + 0.22
    text(s, rx, ty, rw, 0.3,
         P(R("THREE-WAY CLASSIFICATION ", font=HEAD, size=10, bold=True, color=MUTED, spc=150),
           R("  cosine threshold τ = 0.35", font=MATH, size=12, color=CY)), anchor="m")
    cy0 = ty + 0.4
    ch = 1.55
    cw = (rw - 0.3) / 3
    cats = [("Verified Matches", "C ∩ J", EM, "Overlapping competencies tested first."),
            ("Skill Gaps", "J \\ C", RED, "Required skills absent on resume (targeted for "
             "adaptive verification)."),
            ("Bonus Skills", "C \\ J", IN_T, "Candidate strengths not requested by job.")]
    for k, (t, sym, c, d) in enumerate(cats):
        x = rx + k * (cw + 0.15)
        card(s, x, cy0, cw, ch, fill=blend(c, BG, 0.10), line=blend(c, BG, 0.4), name=t)
        text(s, x + 0.15, cy0 + 0.1, cw - 0.3, ch - 0.15,
             [P(R(sym, font=MATH, size=16, color=c), after=1),
              P(R(t, font=HEAD, size=13, bold=True, color=TEXT), after=2),
              P(R(d, font=BODY, size=12, color=MUTED))])
    # score
    sy = cy0 + ch + 0.2
    sh = BOTTOM - sy
    card(s, rx, sy, rw, sh, fill=blend(EM, BG, 0.12), line=blend(EM, BG, 0.45), name="Score")
    text(s, rx + 0.25, sy, rw - 0.5, sh,
         P(R("Match Compatibility Score  ", font=HEAD, size=13, bold=True, color=TEXT),
           R("= (|C ∩ J| / |J|) × 100%", font=MATH, size=16, color=EM)), anchor="m")


def s09_roles(prs):
    s = new_slide(prs, 9, "Module Implementation · Assessment Blueprint",
                  "Automated Role Identification & Blueprint Generation",
                  "SARTA · Module 4: Role & Blueprint")
    lw = 7.0
    text(s, M, TOP - 0.05, lw, 0.34,
         P(R("ROLE MAPPING ENGINE  ", font=HEAD, size=10, bold=True, color=MUTED, spc=150),
           R("role_mapper.py", font=MONO, size=11, color=CY)), anchor="m")
    text(s, M, TOP + 0.3, lw, 0.55,
         P(R("Profiles candidate skill vectors against 5 primary industry archetypes, computes "
             "a role-match confidence % and prioritizes assessment targets.",
             font=BODY, size=14, color=MUTED)))
    roles = [("LuPalette", "Frontend Developer", "React, Next.js, TypeScript, TailwindCSS, HTML/CSS", CY),
             ("LuServer", "Backend Developer", "Python, FastAPI, Django, Node.js, SQL, Docker", EM),
             ("LuLayers", "Full Stack Developer", "Combined client/server proficiencies, REST APIs, Git", IN_T),
             ("LuBrain", "Data Scientist / ML Engineer", "Python, Pandas, Scikit-learn, PyTorch, SQL", CY),
             ("LuCloud", "DevOps / Cloud Engineer", "AWS, Docker, Kubernetes, CI/CD, Linux", EM)]
    y0 = TOP + 0.98
    gap = 0.1
    h = (BOTTOM - y0 - 4 * gap) / 5
    for k, (ic, t, d, c) in enumerate(roles):
        y = y0 + k * (h + gap)
        card(s, M, y, lw, h, name=t)
        icon_badge(s, M + 0.18, y + (h - 0.46) / 2, 0.46, ic, c)
        text(s, M + 0.82, y, lw - 1.0, h,
             [P(R(t, font=HEAD, size=14, bold=True, color=TEXT)),
              P(R(d, font=BODY, size=13, color=MUTED))], anchor="m")
    # blueprint
    rx = M + lw + 0.45
    rw = SW - M - rx
    text(s, rx, TOP - 0.05, rw, 0.34,
         P(R("ASSESSMENT BLUEPRINT  ", font=HEAD, size=10, bold=True, color=MUTED, spc=150),
           R("blueprint_generator.py", font=MONO, size=11, color=CY)), anchor="m")
    tiers = [("Tier 1", "Core Skills", "Top intersecting skills between candidate and target role.", EM),
             ("Tier 2", "Skill Gap Verification", "Highest-priority skills required by job but "
              "absent from resume.", AMBER),
             ("Tier 3", "CS Fundamentals", "Role-agnostic foundations (Data Structures, OOP, "
              "OS, Networks).", IN_T)]
    ty0 = TOP + 0.38
    tgap = 0.18
    th = (BOTTOM - ty0 - 2 * tgap) / 3
    for k, (tag, t, d, c) in enumerate(tiers):
        y = ty0 + k * (th + tgap)
        card(s, rx, y, rw, th, fill=blend(c, BG, 0.10), line=blend(c, BG, 0.42), name=tag)
        text(s, rx + 0.25, y + 0.15, 1.3, 0.4,
             P(R(tag.upper(), font=MONO, size=12, bold=True, color=c)), anchor="m")
        text(s, rx + 0.25, y + 0.52, rw - 0.5, th - 0.6,
             [P(R(t, font=HEAD, size=15, bold=True, color=TEXT), after=2),
              P(R(d, font=BODY, size=14, color=MUTED))])
        if k < 2:
            text(s, rx + rw / 2 - 0.3, y + th - 0.03, 0.6, tgap + 0.06,
                 P(R("▼", font=BODY, size=10, color=blend(MUTED, BG, 0.6)), align="c"),
                 anchor="m")


def s10_qbank(prs):
    s = new_slide(prs, 10, "Module Implementation · Data Layer",
                  "Multi-Domain Knowledge Base & MongoDB Schema",
                  "SARTA · Module 5: Question Bank")
    lw = 7.4
    label(s, M, TOP - 0.02, lw, "Question bank coverage across 9 technical domains",
          color=MUTED, size=10)
    doms = [("LuGlobe", "Web Technologies", "JavaScript, React, Node.js, Frontend Architecture.", CY),
            ("LuServer", "Backend & Systems", "Python, SQL, REST APIs, Microservices.", EM),
            ("LuFlaskConical", "Data Science & ML", "Supervised Learning, Lasso Regularization, "
             "Bias-Variance Tradeoff.", IN_T),
            ("LuBookOpen", "Computer Science Fundamentals", "Operating Systems (paging, deadlocks), "
             "Computer Networks (TCP/IP, ARP), OOP (SOLID principles), Data Structures (LIFO, "
             "Quicksort, Disjoint Sets).", AMBER)]
    gy0 = TOP + 0.42
    g = 0.25
    cw = (lw - g) / 2
    ch = (BOTTOM - gy0 - g) / 2
    for k, (ic, t, d, c) in enumerate(doms):
        x = M + (k % 2) * (cw + g)
        y = gy0 + (k // 2) * (ch + g)
        card(s, x, y, cw, ch, name=t)
        icon_badge(s, x + 0.22, y + 0.22, 0.48, ic, c)
        text(s, x + 0.85, y + 0.16, cw - 1.0, 0.6,
             P(R(t, font=HEAD, size=14, bold=True, color=TEXT), line=0.95), anchor="m")
        text(s, x + 0.22, y + 0.92, cw - 0.4, ch - 1.0, P(R(d, font=BODY, size=14, color=MUTED)))
    # database
    rx = M + lw + 0.4
    rw = SW - M - rx
    label(s, rx, TOP - 0.02, rw, "Database architecture & fault tolerance", color=MUTED, size=10)
    dy = gy0
    dh = 2.75
    card(s, rx, dy, rw, dh, name="MongoDB card")
    icon_badge(s, rx + 0.22, dy + 0.22, 0.48, "LuDatabase", EM)
    text(s, rx + 0.85, dy + 0.22, rw - 1.0, 0.48,
         [P(R("Document Database", font=HEAD, size=14, bold=True, color=TEXT)),
          P(R("MongoDB Atlas", font=BODY, size=12, color=MUTED))], anchor="m")
    cols = [("skills", "taxonomy nodes"), ("questions", "difficulty-tagged MCQs"),
            ("coding_questions", "algorithmic challenges")]
    for k, (cn, cd) in enumerate(cols):
        y = dy + 0.95 + k * 0.58
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, rx + 0.22, y, rw - 0.44, 0.48, fill=BG2,
              line=BORDER, radius=0.08, name=f"Collection {cn}")
        text(s, rx + 0.38, y, rw - 0.7, 0.48,
             P(R(f"'{cn}'", font=MONO, size=12, bold=True, color=CY),
               R(f"   {cd}", font=BODY, size=13, color=MUTED)), anchor="m")
    fy = dy + dh + g
    fh = BOTTOM - fy
    card(s, rx, fy, rw, fh, fill=blend(EM, BG, 0.10), line=blend(EM, BG, 0.42),
         name="Fallback card")
    icon_badge(s, rx + 0.22, fy + 0.22, 0.48, "LuWifiOff", EM, on=blend(EM, BG, 0.10))
    text(s, rx + 0.85, fy + 0.22, rw - 1.0, 0.48,
         P(R("Zero-Downtime Offline Fallback", font=HEAD, size=14, bold=True, color=TEXT)),
         anchor="m")
    text(s, rx + 0.22, fy + 0.8, rw - 0.44, fh - 0.85,
         P(R("In-memory curated question repository ensures complete assessment execution "
             "even during network interruption or database downtime.",
             font=BODY, size=14, color=MUTED)))


def s11_adaptive(prs):
    s = new_slide(prs, 11, "Module Implementation · Intelligence Layer",
                  "Lightweight CAT Dynamic State Machine", "SARTA · Module 6: Adaptive Controller",
                  chip="adaptive_controller.py")
    iw = 5.45
    image_placeholder(s, M, TOP, iw, BOTTOM - TOP, "Adaptive Difficulty State Transition Diagram",
                      "A futuristic state machine diagram on a dark background. Three glowing "
                      "horizontal capsules labeled 'EASY' (emerald green), 'MEDIUM' (sky blue, "
                      "marked with a pulsing 'START' badge), and 'HARD' (violet). Upward glowing "
                      "neon arrows labeled '+2 Correct Streak' connect Easy to Medium and Medium "
                      "to Hard. Downward curved amber arrows labeled 'Incorrect Answer' connect "
                      "Hard to Medium and Medium to Easy. Sleek, clean vector diagram, "
                      "cybernetic aesthetic.", 11)
    rx = M + iw + 0.4
    rw = SW - M - rx
    label(s, rx, TOP - 0.02, rw, "Lightweight adaptive logic", color=MUTED, size=10)
    rules = [("LuPlay", "Initialization", CY,
              "Candidate begins each skill topic at Medium difficulty.", None),
             ("LuTrendingUp", "Promotion Rule", EM,
              "If candidate achieves 2 consecutive correct answers (streak ≥ 2), promote "
              "difficulty:", "Level = min(Hard, Level + 1)"),
             ("LuTrendingDown", "Demotion Rule", AMBER,
              "Upon any incorrect response, immediately drop difficulty:",
              "Level = max(Easy, Level − 1)"),
             ("LuCircleStop", "Stopping Criterion", IN_T,
              "Evaluates 2 questions per skill area to calibrate demonstrated competence "
              "without examinee fatigue.", None)]
    g = 0.25
    y0 = TOP + 0.38
    cw = (rw - g) / 2
    ch = (BOTTOM - y0 - g) / 2
    for k, (ic, t, c, d, f) in enumerate(rules):
        x = rx + (k % 2) * (cw + g)
        y = y0 + (k // 2) * (ch + g)
        card(s, x, y, cw, ch, name=t)
        icon_badge(s, x + 0.2, y + 0.2, 0.46, ic, c)
        text(s, x + 0.78, y + 0.2, cw - 0.9, 0.46,
             P(R(t, font=HEAD, size=14, bold=True, color=TEXT)), anchor="m")
        text(s, x + 0.2, y + 0.8, cw - 0.4, 1.2, P(R(d, font=BODY, size=14, color=MUTED)))
        if f:
            fy = y + ch - 0.62
            shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + 0.15, fy, cw - 0.3, 0.42, fill=BG2,
                  line=blend(c, BG, 0.45), radius=0.08, name=f"Formula {t}")
            text(s, x + 0.15, fy, cw - 0.3, 0.42,
                 P(R(f, font=MONO, size=11, bold=True, color=c), align="c"), anchor="m",
                 wrap=False)


def s12_sandbox(prs):
    s = new_slide(prs, 12, "Module Implementation · Execution Sandbox",
                  "Automated Multi-Language Code Grading", "SARTA · Module 7: Coding Sandbox",
                  chip="judge0_client.py")
    label(s, M, TOP - 0.02, 6, "Execution architecture", color=MUTED, size=10)
    flow = [("LuCodeXml", "Embedded Editor", CY,
             "Microsoft Monaco Editor integrated inside the assessment dashboard."),
            ("LuBinary", "Payload Transmission", IN_T,
             "Source code, inputs, and outputs Base64-encoded to preserve formatting and "
             "indentation."),
            ("LuShieldCheck", "Execution Sandbox", EM,
             "Self-hosted Judge0 CE container executing submitted code in isolated "
             "environments.")]
    aw = 0.45
    fw = (CW - 2 * aw) / 3
    fy, fh = TOP + 0.35, 1.55
    for k, (ic, t, c, d) in enumerate(flow):
        x = M + k * (fw + aw)
        card(s, x, fy, fw, fh, name=t)
        icon_badge(s, x + 0.22, fy + 0.22, 0.46, ic, c)
        text(s, x + 0.82, fy + 0.22, fw - 1.0, 0.46,
             P(R(t, font=HEAD, size=14, bold=True, color=TEXT)), anchor="m")
        text(s, x + 0.22, fy + 0.78, fw - 0.44, fh - 0.82, P(R(d, font=BODY, size=14, color=MUTED)))
        if k < 2:
            text(s, x + fw, fy, aw, fh, P(R("→", font=BODY, size=22, bold=True, color=c),
                                          align="c"), anchor="m")
    by = fy + fh + 0.38
    label(s, M, by - 0.02, 8, "Hidden test case verification", color=MUTED, size=10)
    ry = by + 0.35
    rh = BOTTOM - ry
    g = 0.25
    wA, wB, wC = 3.06, 3.06, 2.35
    wD = CW - wA - wB - wC - 3 * g
    tc = [("LuEye", "Sample Test Cases", CY,
           "Visible to examinee for problem clarification and initial debugging."),
          ("LuEyeOff", "Hidden Algorithmic Test Cases", EM,
           "Evaluates edge cases, boundary inputs, and algorithmic complexity limits.")]
    x = M
    for (ic, t, c, d), w in zip(tc, (wA, wB)):
        card(s, x, ry, w, rh, name=t)
        icon_badge(s, x + 0.2, ry + 0.2, 0.44, ic, c)
        text(s, x + 0.78, ry + 0.12, w - 0.93, 0.6,
             P(R(t, font=HEAD, size=14, bold=True, color=TEXT), line=0.95), anchor="m")
        text(s, x + 0.2, ry + 0.9, w - 0.4, rh - 0.95, P(R(d, font=BODY, size=14, color=MUTED)))
        x += w + g
    # quotas
    qh = (rh - 0.2) / 2
    for k, (big, unit, lab) in enumerate((("2.0", "s", "Strict CPU time limit"),
                                          ("128", "MB", "Strict memory ceiling"))):
        y = ry + k * (qh + 0.2)
        card(s, x, y, wC, qh, fill=blend(AMBER, BG, 0.08), line=blend(AMBER, BG, 0.38),
             name=lab)
        text(s, x + 0.22, y + 0.08, wC - 0.4, qh * 0.55,
             P(R(big, font=MONO, size=24, bold=True, color=AMBER),
               R(" " + unit, font=MONO, size=14, bold=True, color=AMBER)), anchor="m")
        text(s, x + 0.22, y + qh * 0.55, wC - 0.4, qh * 0.4,
             P(R(lab, font=BODY, size=13, color=TEXT)), anchor="t")
    x += wC + g
    card(s, x, ry, wD, rh, name="Languages")
    icon_badge(s, x + 0.2, ry + 0.2, 0.44, "LuLanguages", IN_T)
    text(s, x + 0.75, ry + 0.12, wD - 0.9, 0.6,
         P(R("Multi-Language Support", font=HEAD, size=14, bold=True, color=TEXT), line=0.95),
         anchor="m")
    langs = ["Python 3", "JavaScript (Node.js)", "Java (OpenJDK)", "C++ (GCC)"]
    for k, ln in enumerate(langs):
        pill(s, x + 0.2, ry + 0.8 + k * 0.4, ln, color=CY, on=CARD, size=11, h=0.32,
             w=wD - 0.4)


def s13_xai(prs):
    s = new_slide(prs, 13, "Module Implementation · Output Layer",
                  "Multidimensional Performance Analytics & Radar Visualization",
                  "SARTA · Module 8: Analytics & XAI", chip="performance_analytics.py")
    iw = 5.45
    image_placeholder(s, M, TOP, iw, BOTTOM - TOP,
                      "Candidate Skill Radar Visualization & Scorecard",
                      "A high-tech holographic UI dashboard widget floating on dark slate. "
                      "Centered is an illuminated pentagonal radar chart with 5 glowing axes: "
                      "Python, React, SQL, OOP, Data Structures. An emerald green shaded polygon "
                      "highlights candidate proficiency. Around the radar are sleek metric "
                      "badges: 'Composite Score: 82.5%', 'Peak: Hard', and 'Recommendation: "
                      "Suitable'. Modern glassmorphism UI design, clean typography, 8k render.", 13)
    rx = M + iw + 0.4
    rw = SW - M - rx
    # composite formula bar
    ch = 1.45
    card(s, rx, TOP, rw, ch, name="Composite score")
    label(s, rx + 0.25, TOP + 0.14, rw - 0.5, "Composite score formula", color=MUTED, size=10)
    bx, by, bw, bh = rx + 0.25, TOP + 0.55, rw - 0.5, 0.48
    w1 = bw * 0.6
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, bx, by, w1 - 0.03, bh, fill=EM, radius=0.08,
          name="MCQ share")
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, bx + w1 + 0.03, by, bw - w1 - 0.03, bh, fill=CY,
          radius=0.08, name="Coding share")
    text(s, bx, by, w1, bh,
         P(R("60%", font=MONO, size=15, bold=True, color=BG), align="c"), anchor="m")
    text(s, bx + w1, by, bw - w1, bh,
         P(R("40%", font=MONO, size=15, bold=True, color=BG), align="c"), anchor="m")
    text(s, bx, by + bh + 0.04, w1, 0.3,
         P(R("Adaptive MCQ Performance", font=BODY, size=13, bold=True, color=EM), align="c"),
         anchor="m")
    text(s, bx + w1, by + bh + 0.04, bw - w1, 0.3,
         P(R("Coding Auto-Grading", font=BODY, size=13, bold=True, color=CY), align="c"),
         anchor="m")
    items = [("LuChartColumn", "Granular Competency Breakdown", CY,
              "Individual accuracy meters and peak difficulty passed (Easy, Medium, Hard) for "
              "each skill."),
             ("LuAward", "Strengths Identification", EM,
              "Proficiencies where accuracy ≥ 66% with Hard difficulty clearance."),
             ("LuTarget", "Areas for Improvement", AMBER,
              "Proficiencies where accuracy < 50% or persistent demotions occurred."),
             ("LuRadar", "SVG Competency Radar", IN_T,
              "Responsive vector graphic displaying multi-axial candidate proficiency.")]
    y0 = TOP + ch + 0.3
    pitch = (BOTTOM - y0) / 4
    for k, (ic, t, c, d) in enumerate(items):
        y = y0 + k * pitch
        icon_badge(s, rx, y + 0.02, 0.46, ic, c, on=BG)
        text(s, rx + 0.66, y - 0.03, rw - 0.66, pitch,
             [P(R(t, font=HEAD, size=14, bold=True, color=TEXT), after=1),
              P(R(d, font=BODY, size=14, color=MUTED))])


def _walk_slide(prs, n, category, title, footer, ph_name, prompt, blocks):
    s = new_slide(prs, n, category, title, footer)
    iw = (CW - 0.4) / 2
    image_placeholder(s, M, TOP, iw, BOTTOM - TOP, ph_name, prompt, n)
    return s, M + iw + 0.4, CW - iw - 0.4


def s14_walk1(prs):
    s, rx, rw = _walk_slide(
        prs, 14, "Prototype Walkthrough · User Interface",
        "Document Parsing & Semantic Gap Dashboard", "SARTA · Walkthrough: Screens 1 & 2",
        "Screenshot / Mockup of Step 1 & Step 2 UI",
        "A split-screen view of a web application in dark mode. Top section shows two sleek "
        "glassmorphic file upload dropzones labeled 'Candidate Resume' and 'Job Description'. "
        "Bottom section shows a detailed dashboard featuring a glowing circular percentage gauge "
        "(85% Match), a purple role banner 'Backend Developer (85% Confidence)', and three "
        "columns of glowing pill tags: Red 'Skill Gaps', Green 'Verified Matches', and Blue "
        "'Bonus Skills'. High fidelity UI mockup.", None)
    label(s, rx, TOP - 0.02, rw, "User experience flow", color=MUTED, size=10)
    y1 = TOP + 0.38
    h1 = 1.65
    card(s, rx, y1, rw, h1, name="Step 1")
    pill(s, rx + 0.22, y1 + 0.2, "STEP 1", color=CY, on=CARD, size=11, h=0.32, bold=True)
    icon(s, rx + rw - 0.62, y1 + 0.18, 0.38, "LuUpload", CY)
    text(s, rx + 1.2, y1 + 0.18, rw - 2.0, 0.36,
         P(R("Upload Interface", font=HEAD, size=15, bold=True, color=TEXT)), anchor="m")
    text(s, rx + 0.22, y1 + 0.66, rw - 0.44, h1 - 0.7,
         [P(R("Dual dropzone accepting candidate resume and target job description "
              "(.pdf/.docx).", font=BODY, size=14, color=MUTED), bullet="•", bullet_color=CY,
            after=3),
          P(R("Real-time file validation with instant parse status indicators.", font=BODY,
              size=14, color=MUTED), bullet="•", bullet_color=CY)])
    y2 = y1 + h1 + 0.25
    h2 = BOTTOM - y2
    card(s, rx, y2, rw, h2, name="Step 2")
    pill(s, rx + 0.22, y2 + 0.2, "STEP 2", color=EM, on=CARD, size=11, h=0.32, bold=True)
    icon(s, rx + rw - 0.62, y2 + 0.18, 0.38, "LuGauge", EM)
    text(s, rx + 1.2, y2 + 0.18, rw - 2.0, 0.36,
         P(R("Semantic Compatibility Dashboard", font=HEAD, size=15, bold=True, color=TEXT)),
         anchor="m")
    items = [("Match Compatibility Gauge", "Circular percentage display derived from bipartite "
              "matching.", EM),
             ("Inferred Role Banner", "Displays detected role and recommended assessment "
              "targets.", IN_T),
             ("Three-Way Skill Distribution", "Visual separation of gaps, matches, and bonus "
              "skills.", CY)]
    text(s, rx + 0.22, y2 + 0.68, rw - 0.44, h2 - 0.72,
         [P(R(f"{t}: ", font=BODY, size=14, bold=True, color=TEXT),
            R(d, font=BODY, size=14, color=MUTED), bullet="•", bullet_color=c, after=6)
          for t, d, c in items])


def s15_walk2(prs):
    s, rx, rw = _walk_slide(
        prs, 15, "Prototype Walkthrough · Assessment",
        "Dynamic Adaptive Testing & Coding Workspace", "SARTA · Walkthrough: Screen 3",
        "Screenshot / Mockup of Adaptive MCQ & IDE",
        "A split-view UI of a technical assessment interface in dark mode. Left pane shows an "
        "MCQ question card with a green difficulty badge 'Adaptive: Hard', a countdown timer "
        "'⏱ 42:15', and four selectable options. Right pane shows a Monaco code editor with dark "
        "syntax highlighting, a language dropdown selecting 'Python 3', and a console below "
        "showing green checkmarks: '✓ Test 1: Passed', '✓ Test 2 (Hidden): Passed'. Sleek, "
        "modern developer IDE design.", None)
    label(s, rx, TOP - 0.02, rw, "Real-time adaptive assessment features", color=MUTED, size=10)
    blocks = [("LuGauge", "Adaptive MCQ Interface", EM,
               ["Dynamic difficulty badge that shifts in real time based on observed response "
                "accuracy.",
                "Question progress bar, topic competency indicator, and countdown timer.",
                "Immediate feedback displaying correct answers and updating streak tracking."],
               2.55),
              ("LuTerminal", "Sandboxed Coding IDE", CY,
               ["Monaco editor with multi-language syntax highlighting.",
                "Test case verification pane displaying stdout and hidden test results upon "
                "submission."], None)]
    y = TOP + 0.38
    for ic, t, c, bl, h in blocks:
        if h is None:
            h = BOTTOM - y
        card(s, rx, y, rw, h, name=t)
        icon_badge(s, rx + 0.22, y + 0.2, 0.48, ic, c)
        text(s, rx + 0.85, y + 0.2, rw - 1.0, 0.48,
             P(R(t, font=HEAD, size=15, bold=True, color=TEXT)), anchor="m")
        text(s, rx + 0.22, y + 0.85, rw - 0.44, h - 0.9,
             [P(R(b, font=BODY, size=14, color=MUTED), bullet="•", bullet_color=c, after=4)
              for b in bl])
        y += h + 0.25


def s16_walk3(prs):
    s, rx, rw = _walk_slide(
        prs, 16, "Prototype Walkthrough · Evaluation Report",
        "The Explainable Candidate Performance Report", "SARTA · Walkthrough: Screen 4",
        "Screenshot / Mockup of Final Evaluation Report",
        "A comprehensive candidate evaluation report screen in dark mode. At the top, a "
        "prominent green badge reads 'RECOMMENDATION: SUITABLE' alongside a circular gauge "
        "showing '82.5% Composite Score'. Below, a 5-axis competency radar chart sits next to "
        "individual skill progress bars labeled Python (100%, Peak: Hard), SQL (50%, Peak: "
        "Medium), and React (100%, Peak: Hard). Two bottom cards highlight 'Strengths' in green "
        "and 'Areas for Improvement' in red. Clean executive dashboard.", None)
    label(s, rx, TOP - 0.02, rw, "Explainable candidate report highlights", color=MUTED, size=10)
    items = [("LuBadgeCheck", "Objective Hiring Verdict", EM,
              "Clear recommendation badge (Suitable, Needs Improvement, Not Suitable)."),
             ("LuScale", "Score Decomposition", CY,
              "Explicit breakdown between Adaptive MCQ Accuracy and Coding Auto-Grading."),
             ("LuRadar", "Multi-Axial Radar Visualization", IN_T,
              "Demonstrates candidate balance across core topics."),
             ("LuChartColumn", "Granular Competency Breakdown", CY,
              "Individual accuracy meters and peak difficulty passed for every skill."),
             ("LuTarget", "Targeted Action Items", AMBER,
              "Identifies specific learning gaps for recruiters and candidates.")]
    y0 = TOP + 0.38
    g = 0.12
    h = (BOTTOM - y0 - 4 * g) / 5
    for k, (ic, t, c, d) in enumerate(items):
        y = y0 + k * (h + g)
        card(s, rx, y, rw, h, name=t)
        icon_badge(s, rx + 0.18, y + (h - 0.44) / 2, 0.44, ic, c)
        text(s, rx + 0.8, y, rw - 0.95, h,
             [P(R(t, font=HEAD, size=13, bold=True, color=TEXT)),
              P(R(d, font=BODY, size=13, color=MUTED))], anchor="m")
    # verdict pills on Objective hiring verdict? kept textual for fidelity


def _method_line(s, ic, label_, txt, c=CY, w=None):
    w = w or CW
    icon_badge(s, M, TOP - 0.02, 0.42, ic, c, on=BG)
    text(s, M + 0.6, TOP - 0.06, w - 0.6, 0.52,
         P(R(f"{label_}  ", font=HEAD, size=13, bold=True, color=TEXT),
           R(txt, font=BODY, size=14, color=MUTED)), anchor="m")


def s17_extract(prs):
    s = new_slide(prs, 17, "Empirical Evaluation · Results",
                  "Skill Extraction Quality Benchmarked Against Ground Truth",
                  "SARTA · Empirical Results")
    _method_line(s, "LuFlaskConical", "Evaluation Methodology",
                 "Validated against manually annotated sample resumes and job specifications "
                 "across Web Development, Backend Systems, and Data Science.")
    rows = [["Dataset Profile", "Extracted Count", "Ground Truth Count", "Precision", "Recall",
             "F1-Score"],
            ["Sample 1 (Backend Systems)", "6", "6", "1.00 (100.0%)", "1.00 (100.0%)", "1.00 (100.0%)"],
            ["Sample 2 (Frontend Architecture)", "7", "7", "0.86 (85.7%)", "0.86 (85.7%)", "0.86 (85.7%)"],
            ["Sample 3 (Data Science & ML)", "6", "6", "1.00 (100.0%)", "1.00 (100.0%)", "1.00 (100.0%)"],
            ["Overall Micro-Average", "19", "19", "94.74%", "94.74%", "94.74%"]]
    mono = {"body": dict(font=MONO, size=13)}
    cs = {0: {"body": dict(bold=True)}, 1: mono, 2: mono, 3: mono, 4: mono, 5: mono}

    def fn(i, j, v, p):
        if i > 0 and j > 0:
            p["align"] = "c"
        if i == 0 and j > 0:
            p["align"] = "c"
        return p
    ty = TOP + 0.6
    native_table(s, M, ty, [3.53, 1.6, 1.8, 1.75, 1.7, 1.75], rows, header_h=0.5, row_h=0.5,
                 col_styles=cs, highlight_last=True, cell_fn=fn,
                 name="Skill Extraction Benchmark Results")
    by = ty + 0.5 + 4 * 0.5 + 0.4
    bh = BOTTOM - by
    sw_ = 3.2
    card(s, M, by, sw_, bh, fill=blend(EM, BG, 0.12), line=blend(EM, BG, 0.45), name="F1 stat")
    text(s, M + 0.25, by + 0.1, sw_ - 0.5, bh * 0.6,
         P(R("94.74", font=MONO, size=40, bold=True, color=EM),
           R("%", font=MONO, size=22, bold=True, color=EM)), anchor="m")
    text(s, M + 0.25, by + bh * 0.6, sw_ - 0.5, bh * 0.35,
         P(R("Micro-averaged F1-score", font=BODY, size=13, color=TEXT)), anchor="t")
    x2 = M + sw_ + 0.3
    w2 = CW - sw_ - 0.3
    card(s, x2, by, w2, bh, name="Benchmark insight")
    icon_badge(s, x2 + 0.25, by + 0.25, 0.48, "LuLightbulb", AMBER)
    text(s, x2 + 0.9, by + 0.2, w2 - 1.15, bh - 0.4,
         [P(R("Benchmark Insights", font=HEAD, size=14, bold=True, color=TEXT), after=3),
          P(R("The two-pass architecture (spaCy PhraseMatcher + SBERT dense embedding alignment) "
              "virtually eliminates false positive hallucinations while capturing multi-word "
              "technical tokens.", font=BODY, size=14, color=MUTED))], anchor="m")


def _style_chart_text(chart, size=11, color=MUTED):
    chart.font.size = Pt(size)
    chart.font.color.rgb = rgb(color)
    chart.font.name = BODY


def _nofill_spPr(parent_el, line=False):
    spPr = parent_el.find(qn("c:spPr"))
    if spPr is None:
        spPr = etree.SubElement(parent_el, qn("c:spPr"))
    for ch in list(spPr):
        spPr.remove(ch)
    etree.SubElement(spPr, qn("a:noFill"))
    ln = etree.SubElement(spPr, qn("a:ln"))
    etree.SubElement(ln, qn("a:noFill"))
    return spPr


def s18_adaptive_bench(prs):
    s = new_slide(prs, 18, "Empirical Evaluation · Results",
                  "Adaptive CAT Efficiency vs Static Quiz Baseline", "SARTA · Empirical Results")
    _method_line(s, "LuUsers", "Experimental Setup",
                 "Simulated candidate response trajectories across Junior (Easy ability), "
                 "Mid-level (Medium ability), and Senior (Hard ability) competence levels.")
    rows = [["Candidate Ability Profile", "Target True Difficulty",
             "Adaptive Questions to Stabilize", "Static Baseline Questions",
             "Question Reduction %"],
            ["Senior Candidate Profile", "Hard", "10 questions", "10 questions",
             "0.0% (Explored Ceiling)"],
            ["Mid-Level Candidate Profile", "Medium", "9 questions", "10 questions",
             "10.0% Reduction"],
            ["Junior Candidate Profile", "Easy", "4 questions", "10 questions", "60.0% Reduction"],
            ["Empirical Mean Summary", "Overall Calibration", "7.7 questions", "10.0 questions",
             "23.3% Overall Reduction"]]
    mono = {"body": dict(font=MONO, size=13)}
    cs = {0: {"body": dict(bold=True)}, 2: mono, 3: mono, 4: mono}

    def fn(i, j, v, p):
        if j > 0:
            p["align"] = "c"
        return p
    ty = TOP + 0.6
    native_table(s, M, ty, [2.9, 1.95, 2.3, 2.0, 2.983], rows, header_h=0.62, row_h=0.46,
                 col_styles=cs, highlight_last=True, cell_fn=fn,
                 name="Adaptive Calibration Speed Benchmark")
    by = ty + 0.62 + 4 * 0.46 + 0.35
    bh = BOTTOM - by
    # chart
    cw_ = 6.7
    card(s, M, by, cw_, bh, name="Chart card")
    cd = CategoryChartData()
    cd.categories = ["Senior", "Mid-Level", "Junior"]
    cd.add_series("SARTA adaptive", (10, 9, 4))
    cd.add_series("Static baseline", (10, 10, 10))
    gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(M + 0.15), Inches(by + 0.05),
                            Inches(cw_ - 0.3), Inches(bh - 0.1), cd)
    gf.name = "Questions to stabilize chart"
    ch = gf.chart
    _style_chart_text(ch)
    ch.has_legend = True
    ch.legend.position = XL_LEGEND_POSITION.RIGHT
    ch.legend.include_in_layout = False
    ch.legend.font.size = Pt(11)
    ch.legend.font.color.rgb = rgb(MUTED)
    plot = ch.plots[0]
    plot.gap_width = 45
    plot.overlap = -10
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.font.size = Pt(11)
    dl.font.bold = True
    dl.font.color.rgb = rgb(TEXT)
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    dl.number_format = "0"
    dl.number_format_is_linked = False
    for ser, c in zip(plot.series, (EM, "475569")):
        ser.format.fill.solid()
        ser.format.fill.fore_color.rgb = rgb(c)
        ser.format.line.fill.background()
    va = ch.value_axis
    va.maximum_scale = 12
    va.minimum_scale = 0
    va.has_major_gridlines = False
    va.visible = False
    ca = ch.category_axis
    ca.reverse_order = True
    ca.format.line.fill.background()
    ca.tick_labels.font.size = Pt(11)
    ca.tick_labels.font.color.rgb = rgb(MUTED)
    from pptx.enum.chart import XL_TICK_MARK
    ca.major_tick_mark = XL_TICK_MARK.NONE
    cs_el = ch._chartSpace
    _nofill_spPr(cs_el)
    _nofill_spPr(cs_el.find(qn("c:chart")).find(qn("c:plotArea")))
    # takeaway
    x2 = M + cw_ + 0.3
    w2 = CW - cw_ - 0.3
    card(s, x2, by, w2, bh, fill=blend(EM, BG, 0.12), line=blend(EM, BG, 0.45), name="Takeaway")
    text(s, x2 + 0.25, by + 0.12, 2.0, 0.75,
         P(R("23.3", font=MONO, size=34, bold=True, color=EM),
           R("%", font=MONO, size=20, bold=True, color=EM)), anchor="m")
    text(s, x2 + 2.2, by + 0.12, w2 - 2.4, 0.75,
         P(R("KEY TAKEAWAY", font=HEAD, size=10, bold=True, color=EM, spc=150)), anchor="m")
    text(s, x2 + 0.25, by + 0.88, w2 - 0.5, bh - 0.95,
         P(R("The streak-based adaptive engine converges on true candidate ability 23.3% faster "
             "than fixed-length quizzes, minimizing candidate fatigue and testing time.",
             font=BODY, size=14, color=TEXT)))


def s19_coding(prs):
    s = new_slide(prs, 19, "Empirical Evaluation · Results",
                  "Sandboxed Auto-Grading & Test-Case Verification", "SARTA · Empirical Results")
    _method_line(s, "LuCodeXml", "Experimental Setup",
                 "Evaluated 5 benchmark code submissions (correct implementations, logic errors, "
                 "syntax errors) against verified ground-truth answer keys.")
    rows = [["Evaluation Metric", "Tested Benchmark Target", "Observed Result",
             "Agreement / Accuracy"],
            ["Test-Case Pass/Fail Agreement", "5 Verification Submissions",
             "5 / 5 Correct Classifications", "100.0% Accuracy"],
            ["Syntax / Runtime Error Trapping", "2 Malformed Submissions",
             "2 / 2 Clean Error Catches", "100.0% Reliability"],
            ["Execution Sandbox Latency", "Time to Result", "0.042 seconds average",
             "Real-Time Response"],
            ["Memory Ceiling Enforcement", "128MB Buffer", "8,420 KB average consumption",
             "Zero Host Leakage"]]
    cs = {0: {"body": dict(bold=True)}, 1: {"body": dict(color=MUTED)},
          2: {"body": dict(font=MONO, size=13, color=CY)},
          3: {"body": dict(bold=True, color=EM)}}
    ty = TOP + 0.6
    native_table(s, M, ty, [3.2, 2.7, 3.73, 2.5], rows, header_h=0.5, row_h=0.52,
                 col_styles=cs, name="Code Auto-Grading Benchmark Results")
    by = ty + 0.5 + 4 * 0.52 + 0.4
    label(s, M, by - 0.04, 6, "Key observations", color=MUTED, size=10)
    by += 0.3
    bh = BOTTOM - by
    obs = [("LuSplit", "Sandbox accurately differentiated between semantic logic errors and "
            "runtime exceptions.", CY),
           ("LuLock", "Zero host environment leakage or unhandled execution timeouts.", EM)]
    w = (CW - 0.3) / 2
    for k, (ic, t, c) in enumerate(obs):
        x = M + k * (w + 0.3)
        card(s, x, by, w, bh, name=f"Observation {k+1}")
        icon_badge(s, x + 0.25, by + (bh - 0.5) / 2, 0.5, ic, c)
        text(s, x + 0.95, by, w - 1.15, bh, P(R(t, font=BODY, size=15, color=TEXT)), anchor="m")


def s20_survey(prs):
    s = new_slide(prs, 20, "Empirical Evaluation · Results",
                  "User Study Survey Metrics (Candidate & Peer Feedback)",
                  "SARTA · Empirical Results")
    _method_line(s, "LuMessageSquare", "Survey Methodology",
                 "Structured survey administered to volunteer candidates and peer evaluators "
                 "using a standard 1 to 5 Likert scale.", w=CW - 3.0)
    # likert scale visual
    lx = SW - M - 2.75
    for k in range(5):
        c = blend(EM, BG, 0.25 + 0.17 * k)
        shape(s, MSO_SHAPE.OVAL, lx + k * 0.56, TOP - 0.05, 0.44, 0.44, fill=c, name=f"Likert {k+1}")
        text(s, lx + k * 0.56, TOP - 0.05, 0.44, 0.44,
             P(R(str(k + 1), font=MONO, size=12, bold=True, color=TEXT if k < 3 else BG),
               align="c"), anchor="m")
    rows = [["Survey Evaluation Dimension", "Mean Score (1–5 Scale)", "Approval %",
             "Key Participant Observation"],
            ["Clarity of Skill-Wise Breakdown (XAI)", "4.7 / 5.0", "94.0%",
             "Provided actionable learning feedback over generic rejection notices."],
            ["Relevance of Inferred Role Profile", "4.5 / 5.0", "90.0%",
             "Accurately captured full-stack and specialized skill clusters."],
            ["Perceived Fairness of Adaptive Difficulty", "4.6 / 5.0", "92.0%",
             "Questions felt calibrated to personal competence."],
            ["Recruitment Decision Utility for Evaluators", "4.8 / 5.0", "96.0%",
             "Addressed the blind spot of verifying missing resume skills."],
            ["Composite User Satisfaction Index", "4.65 / 5.0", "93.0%",
             "Strong validation of end-to-end usability and transparency."]]
    mono = {"body": dict(font=MONO, size=14, color=CY, bold=True)}
    cs = {0: {"body": dict(bold=True)}, 1: mono, 2: {"body": dict(font=MONO, size=14, color=EM,
                                                                 bold=True)},
          3: {"body": dict(color=MUTED)}}

    def fn(i, j, v, p):
        if j in (1, 2):
            p["align"] = "c"
        return p
    native_table(s, M, TOP + 0.65, [3.9, 2.0, 1.45, CW - 7.35], rows, header_h=0.5,
                 row_h=0.72, col_styles=cs, highlight_last=True, cell_fn=fn,
                 name="User Study Survey Ratings")


def s21_compare(prs):
    s = new_slide(prs, 21, "Discussion · Comparative Analysis",
                  "SARTA Feature Comparison Matrix", "SARTA · Comparative Analysis")
    data = [
        ("Semantic Skill Extraction", ("No", "Exact keyword search"), ("No", "None"),
         ("No", "None"), ("YES", "spaCy NER + SBERT vectors")),
        ("JD-Aware Gap Analysis", ("No", "Evaluates resumes in isolation"),
         ("No", "Fixed problem sets"), ("No", "Generic quizzes"),
         ("YES", "Hungarian bipartite matching")),
        ("Dynamic Adaptive Difficulty", ("No", "None"), ("No", "Fixed item difficulty"),
         ("No", "Static order"), ("YES", "Lightweight CAT controller")),
        ("Sandboxed Code Assessment", ("No", "No coding environment"),
         ("YES", "Proprietary sandbox"), ("No", "None"), ("YES", "Judge0 CE open-source")),
        ("Explainable Reporting (XAI)", ("No", "Opaque binary filtering"),
         ("Partial", "Test counts only"), ("No", "Single aggregate %"),
         ("YES", "Multi-axial breakdown & radar")),
        ("Open-Source & Zero Cost", ("No", "Costly enterprise license"),
         ("No", "Paywalled subscription"), ("Varies", "Basic tiers only"),
         ("YES", "100% free and open-source")),
    ]
    head = ["Capability", "Traditional ATS", "Coding Platforms", "Static Quiz Systems",
            "SARTA (This Work)"]
    GL = {"No": ("✕", RED), "YES": ("✓", EM), "Partial": ("◐", AMBER), "Varies": ("◐", AMBER)}

    def verdict(v, d, sarta=False):
        g, c = GL[v]
        return [P(R(g + "  ", font="Segoe UI Symbol", size=13, bold=True, color=c),
                  R(v if v != "YES" else "Yes", font=HEAD, size=13, bold=True, color=c)),
                P(R(d, font=BODY, size=12, color=TEXT if sarta else MUTED))]
    rows = [head]
    for cap, *cells in data:
        r = [P(R(cap, font=HEAD, size=13, bold=True, color=TEXT))]
        for k, (v, d) in enumerate(cells):
            r.append(verdict(v, d, sarta=(k == 3)))
        rows.append(r)
    cs = {4: {"head_color": TEXT}}
    gf = native_table(s, M, TOP + 0.05, [2.75, 2.3, 2.3, 2.3, CW - 9.65], rows, header_h=0.5,
                      row_h=0.74, col_styles=cs, col_fills={4: EM},
                      name="Platform Feature Comparison Matrix")
    # SARTA header cell emphasis
    cell = gf.table.cell(0, 4)
    cell.fill.solid()
    cell.fill.fore_color.rgb = rgb(blend(EM, CARD, 0.45))
    _cell_border(cell, color=EM, w_pt=1.25, sides=("B",))


def s22_conclusion(prs):
    s = new_slide(prs, 22, "Conclusion · References", "Summary of Deliverables & References",
                  "SARTA · Jamia Millia Islamia")
    lw = 4.75
    label(s, M, TOP - 0.02, lw, "Summary of accomplishments", color=MUTED, size=10)
    sy = TOP + 0.35
    sh = 1.3
    sw_ = (lw - 0.25) / 2
    for k, (big, unit, lab, c) in enumerate((("94.74", "%", "Skill extraction F1-score", EM),
                                             ("23.3", "%", "Efficiency gain vs static test", CY))):
        x = M + k * (sw_ + 0.25)
        card(s, x, sy, sw_, sh, fill=blend(c, BG, 0.10), line=blend(c, BG, 0.42), name=lab)
        text(s, x + 0.2, sy + 0.1, sw_ - 0.4, 0.7,
             P(R(big, font=MONO, size=28, bold=True, color=c),
               R(unit, font=MONO, size=16, bold=True, color=c)), anchor="m")
        text(s, x + 0.2, sy + 0.78, sw_ - 0.4, 0.45, P(R(lab, font=BODY, size=12, color=TEXT)))
    bullets = ["Delivered a fully functional, end-to-end prototype of SARTA with 0 architectural "
               "gaps.",
               "Demonstrated 94.74% skill extraction F1-score and 23.3% assessment efficiency "
               "gain over static testing.",
               "Unified semantic resume analysis, adaptive item calibration, and sandboxed coding "
               "into a single open-source platform."]
    by = sy + sh + 0.3
    text(s, M, by, lw, BOTTOM - by,
         [P(R(b, font=BODY, size=14, color=TEXT), bullet="✓", bullet_color=EM, after=8, marL=0.3)
          for b in bullets])
    # references
    rx = M + lw + 0.4
    rw = SW - M - rx
    card(s, rx, TOP - 0.05, rw, BOTTOM - TOP + 0.05, name="References")
    label(s, rx + 0.3, TOP + 0.1, rw - 0.6, "IEEE References (2024–2026)", color=EM, size=10)
    refs = [
        "M.-H. Ajjam and H. Al-Raweshidy, “AI-Driven Semantic Similarity-Based Job Matching "
        "Framework for Recruitment Systems,” Information Sciences, vol. 724, p. 121890, 2025.",
        "J. Rosenberger et al., “CareerBERT: Matching Resumes to ESCO Jobs in a Shared Embedding "
        "Space,” arXiv preprint arXiv:2503.02056, 2025.",
        "X. Yu, J. Zhang, and Z. Yu, “ConFit: Improving Resume-Job Matching using Data "
        "Augmentation and Contrastive Learning,” in Proc. AAAI Conf. Human Computation and "
        "Crowdsourcing, arXiv:2401.16349, 2024.",
        "S. Modak et al., “A Review of Resume Analysis and Job Description Matching Using Machine "
        "Learning,” International Journal of Recent Technology and Engineering (IJRITCC), "
        "vol. 12, no. 5, pp. 112–126, 2024.",
        "N. Reimers and I. Gurevych, “Sentence-BERT: Sentence Embeddings using Siamese "
        "BERT-Networks,” in Proc. EMNLP-IJCNLP, 2019, pp. 3982–3992.",
        "A. Barredo Arrieta et al., “Explainable Artificial Intelligence (XAI): Concepts, "
        "taxonomies, opportunities and challenges toward responsible AI,” Information Fusion, "
        "vol. 58, pp. 82–115, 2020.",
    ]
    paras = []
    for k, r in enumerate(refs):
        paras.append(P(R(f"[{k+1}]  ", font=MONO, size=11, bold=True, color=CY),
                       R(r, font=BODY, size=13, color=MUTED), after=9))
    text(s, rx + 0.3, TOP + 0.45, rw - 0.6, BOTTOM - TOP - 0.55, paras)
    notes(s, "Close with the three deliverables and invite questions. References follow IEEE "
             "style; [5] and [6] are foundational works cited for SBERT and XAI.")


def build(out):
    prs = Presentation()
    prs.slide_width = Inches(SW)
    prs.slide_height = Inches(SH)
    prs.core_properties.title = "SARTA: Implementation & Empirical Evaluation"
    prs.core_properties.author = "Syed Anas Ahmed, Md Shahid Rasool"
    prs.core_properties.subject = "B.Tech Minor Project Presentation II - Jamia Millia Islamia"
    for fn in (s01_title, s02_problem, s03_arch, s04_status, s05_stack, s06_parser, s07_nlp,
               s08_matcher, s09_roles, s10_qbank, s11_adaptive, s12_sandbox, s13_xai,
               s14_walk1, s15_walk2, s16_walk3, s17_extract, s18_adaptive_bench, s19_coding,
               s20_survey, s21_compare, s22_conclusion):
        fn(prs)
    assert len(prs.slides) == TOTAL, len(prs.slides)
    prs.save(out)
    print("saved", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--icons", default=os.path.join(HERE, "assets", "icons"))
    ap.add_argument("--out", default=os.path.join(HERE, "SARTA_Presentation_II.pptx"))
    a = ap.parse_args()
    Ctx.icons = a.icons
    build(a.out)
