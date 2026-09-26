"""Generate the Osho Decor border (trims) price list PDF.

Selling price = dealing price + 10% margin, rounded UP to the next multiple of ₹5
(so every price ends in 0 or 5 and is never below dealing + 10%).
Edit COLLECTIONS / MARGIN below and run:  python3 build_price_list.py
"""

import os
from datetime import date
from fractions import Fraction
from math import ceil

from PIL import Image as PILImage
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, Image, KeepTogether,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "Osho_Decor_Border_Price_List.pdf")

MARGIN = Fraction(10, 100)          # 10% over dealing price
ROUND_TO = 5                        # prices end in 0 or 5
LIST_DATE = date(2026, 9, 26)
LIST_REF = "OD/BPL/01"

# ---- Company -----------------------------------------------------------------
COMPANY = "OSHO INTERNATIONAL"
GSTIN = "07ABNPA1669F2ZQ"
PHONES = ["+91 98105 59233", "+91 96757 55635"]
EMAIL = "oshodecor@gmail.com"
ADDRESS = ["House No. 29, Block-1, 2nd Floor, WHS Timber Market,",
           "Kirti Nagar, New Delhi - 110015",
           "Landmark: Near Richi Rich Banquet Hall"]

# ---- Brand palette (sampled from the Osho Decor logo) --------------------------
PINK = HexColor("#E20886")
INK = HexColor("#1B1B1F")
GREY = HexColor("#6E6E73")
LIGHT = HexColor("#A8A8A8")
RULE = HexColor("#E4E1DE")
TINT = HexColor("#FBF3F7")
PAPER = HexColor("#F7F5F3")

# ---- Collections: (name, dealing price per metre, [(design no, fabric base, art no), ...])
# Swatch images: assets/swatches/<sl no, 2 digits>_<n>.jpg, in the same order.
COLLECTIONS = [
    ("Newry", 285, [("BV9446F/01", "Belford Linen-C1", "TR-08-24-C1"),
                    ("BV9446F/02", "Belford Linen-C2", "TR-08-24-C2"),
                    ("BV9446F/03", "Belford Linen-C6", "TR-08-24-C3"),
                    ("BV9446F/05", "Belford Linen-C7", "TR-08-24-C5")]),
    ("Belfast", 265, [("BV9447 YS-01", "Castleford1-C1", "TR-09-24-C1"),
                      ("BV9447 YS-02", "Castleford1-C2", "TR-09-24-C2"),
                      ("BV9447 YS-03", "Castleford1-C3", "TR-09-24-C3"),
                      ("BV9447 YS-04", "Castleford1-C5", "TR-09-24-C4")]),
    ("Leeds", 165, [("8628 BV (Leaf Emb)", "Jaipur Satin", "TR-07-24-C3"),
                    ("8628 BV (Leaf Emb)", "Jaipur Satin", "TR-07-24-C2"),
                    ("8628 BV (Leaf Emb)", "Jaipur Satin", "TR-07-24-C4"),
                    ("8628 BV (Leaf Emb)", "Jaipur Satin", "TR-07-24-C5")]),
    ("Tucson", 235, [("BV-9448-F/01", "Belford Linen-C1", "TR-10-24-C1"),
                     ("BV-9448-F/02", "Belford Linen-C2", "TR-10-24-C2"),
                     ("BV-9448-F/03", "Belford Linen-C6", "TR-10-24-C3"),
                     ("BV-9448-F/04", "Belford Linen-C7", "TR-10-24-C4")]),
    ("Swansea", 285, [("BV8827", "Daisy-C45", "TR-02-24-C3"),
                      ("BV8827", "Daisy-C31", "TR-02-24-C1"),
                      ("BV8827", "Daisy-C03", "TR-02-24-C2")]),
    ("Dixon", 195, [("BV8831V3", "Daisy-C03", "TR-04-24-C2"),
                    ("BV8831V3", "Daisy-C45", "TR-04-24-C3"),
                    ("BV8831V3", "Daisy-C31", "TR-04-24-C1")]),
    ("Athens", 285, [("BV8824V3", "Daisy-C03", "TR-01-24-C2"),
                     ("BV8824V3", "Daisy-C31", "TR-01-24-C1"),
                     ("BV8824V3", "Daisy-C45", "TR-01-24-C3")]),
    ("Peru", 265, [("BV9449 V2YS-OPT1", "Stretford1-C1", "TR-11-24-C1"),
                   ("BV9449 V2YS-OPT2", "Castleford1-C2", "TR-11-24-C2"),
                   ("BV9449 V2YS-OPT3", "Castleford1-C3", "TR-11-24-C3"),
                   ("BV9449 V2YS-OPT4", "Castleford1-C5", "TR-11-24-C4")]),
    ("Richmond", 195, [("BV-9450 S/01", "Castleford1-C1", "TR-12-24-C1"),
                       ("BV-9450 S/02", "Castleford1-C2", "TR-12-24-C2"),
                       ("BV-9450 S/03", "Castleford1-C3", "TR-12-24-C3")]),
    ("Zion", 300, [("BV8320V2", "Daisy-C03", "TR-06-24-C2"),
                   ("BV8320V2", "Daisy-C31", "TR-06-24-C1"),
                   ("BV8320V2", "Daisy-C45", "TR-06-24-C3")]),
]


def selling_price(dealing):
    """Dealing price + margin, always rounded UP to the next multiple of 5 (ends in 0 or 5)."""
    return ceil(Fraction(dealing) * (1 + MARGIN) / ROUND_TO) * ROUND_TO


def inr(v):
    return f"₹{v:,}"


# ---- Fonts & styles ----------------------------------------------------------------
for name in ("Light", "Regular", "Medium", "SemiBold"):
    pdfmetrics.registerFont(TTFont(f"Poppins-{name}", os.path.join(ASSETS, "fonts", f"Poppins-{name}.ttf")))


def style(name, font="Poppins-Regular", size=8, color=INK, align=TA_LEFT, leading=None, **kw):
    return ParagraphStyle(name, fontName=font, fontSize=size, textColor=color, alignment=align,
                          leading=leading or size * 1.3, **kw)


S_TITLE = style("title", "Poppins-SemiBold", 20, INK, leading=24)
S_SUB = style("sub", "Poppins-Regular", 8.5, GREY)
S_META_R = style("metar", "Poppins-Regular", 8, GREY, TA_RIGHT)
S_SECTION = style("section", "Poppins-SemiBold", 9, PINK, leading=12)
S_TH = style("th", "Poppins-Medium", 7.5, white)
S_TH_R = style("thr", "Poppins-Medium", 7.5, white, TA_RIGHT)
S_TD = style("td", "Poppins-Regular", 8.5, INK)
S_TD_C = style("tdc", "Poppins-Regular", 8.5, INK, TA_CENTER)
S_TD_B = style("tdb", "Poppins-Medium", 8.5, INK)
S_TD_R = style("tdr", "Poppins-SemiBold", 9, INK, TA_RIGHT)
S_CAP_ART = style("capart", "Poppins-SemiBold", 8, INK, TA_CENTER, leading=10)
S_CAP = style("cap", "Poppins-Regular", 6.8, GREY, TA_CENTER, leading=8.8)
S_NOTE = style("note", "Poppins-Regular", 7.5, GREY, leading=11)

PAGE_W, PAGE_H = A4
SIDE = 16 * mm
CONTENT_W = PAGE_W - 2 * SIDE


# ---- Header / footer drawn on every page ----------------------------------------------
def draw_first_header(c):
    top = PAGE_H - 14 * mm
    logo = os.path.join(ASSETS, "osho-decor-logo.png")
    lw = 62 * mm
    lh = lw * 268 / 1400
    c.drawImage(logo, SIDE - 1.2 * mm, top - lh, lw, lh, mask="auto")

    x = PAGE_W - SIDE
    c.setFillColor(INK)
    c.setFont("Poppins-SemiBold", 10.5)
    c.drawRightString(x, top - 9, COMPANY)
    c.setFont("Poppins-Medium", 7.5)
    c.setFillColor(PINK)
    c.drawRightString(x, top - 20, f"GSTIN: {GSTIN}")
    c.setFont("Poppins-Regular", 7.2)
    c.setFillColor(GREY)
    y = top - 31
    for line in ADDRESS:
        c.drawRightString(x, y, line)
        y -= 9.5
    c.drawRightString(x, y, f"M: {'  |  '.join(PHONES)}")
    y -= 9.5
    c.drawRightString(x, y, f"E: {EMAIL}")

    c.setStrokeColor(PINK)
    c.setLineWidth(1.6)
    c.line(SIDE, y - 9, PAGE_W - SIDE, y - 9)


def draw_running_header(c):
    top = PAGE_H - 11 * mm
    logo = os.path.join(ASSETS, "osho-decor-logo.png")
    lw = 38 * mm
    lh = lw * 268 / 1400
    c.drawImage(logo, SIDE - 0.8 * mm, top - lh, lw, lh, mask="auto")
    c.setFont("Poppins-Medium", 8)
    c.setFillColor(INK)
    c.drawRightString(PAGE_W - SIDE, top - 7, "Border Price List")
    c.setFont("Poppins-Regular", 7)
    c.setFillColor(GREY)
    c.drawRightString(PAGE_W - SIDE, top - 16, f"{LIST_REF}  ·  {LIST_DATE:%d %b %Y}")
    c.setStrokeColor(RULE)
    c.setLineWidth(0.8)
    c.line(SIDE, top - lh - 5, PAGE_W - SIDE, top - lh - 5)


def draw_footer(c, doc):
    y = 10 * mm
    c.setStrokeColor(RULE)
    c.setLineWidth(0.8)
    c.line(SIDE, y + 9, PAGE_W - SIDE, y + 9)
    c.setFont("Poppins-Medium", 7)
    c.setFillColor(PINK)
    c.drawString(SIDE, y, "OSHO DECOR")
    c.setFillColor(LIGHT)
    c.setFont("Poppins-Regular", 7)
    c.drawString(SIDE + c.stringWidth("OSHO DECOR ", "Poppins-Medium", 7), y, "·  Always Vibrant.")
    c.setFillColor(GREY)
    c.drawCentredString(PAGE_W / 2, y, f"{EMAIL}   ·   {PHONES[0]}")
    c.drawRightString(PAGE_W - SIDE, y, f"Page {doc.page}")


def on_first(c, doc):
    c.saveState()
    draw_first_header(c)
    draw_footer(c, doc)
    c.restoreState()


def on_later(c, doc):
    c.saveState()
    draw_running_header(c)
    draw_footer(c, doc)
    c.restoreState()


# ---- Flowables -------------------------------------------------------------------
class CollectionBar(Flowable):
    """Tinted bar: number badge + collection name on the left, price on the right."""

    def __init__(self, no, name, count, price, width, height=30):
        super().__init__()
        self.no, self.name, self.count, self.price = no, name, count, price
        self.width, self.height = width, height

    def wrap(self, *_):
        return self.width, self.height

    def draw(self):
        c, w, h = self.canv, self.width, self.height
        c.setFillColor(TINT)
        c.roundRect(0, 0, w, h, 4, stroke=0, fill=1)
        c.setFillColor(PINK)
        c.roundRect(0, 0, 3, h, 1.5, stroke=0, fill=1)

        c.setFillColor(PINK)
        c.setFont("Poppins-SemiBold", 11)
        c.drawString(12, h / 2 - 4, f"{self.no:02d}")
        c.setFillColor(INK)
        c.setFont("Poppins-SemiBold", 12)
        c.drawString(34, h / 2 - 4.2, self.name.upper())
        nx = 34 + c.stringWidth(self.name.upper(), "Poppins-SemiBold", 12) + 10
        c.setFillColor(GREY)
        c.setFont("Poppins-Regular", 7.5)
        c.drawString(nx, h / 2 - 3, f"{self.count} shades")

        price = inr(self.price)
        c.setFont("Poppins-Regular", 7.5)
        unit = " / metre"
        uw = c.stringWidth(unit, "Poppins-Regular", 7.5)
        c.drawString(w - 12 - uw, h / 2 - 3, unit)
        c.setFillColor(PINK)
        c.setFont("Poppins-SemiBold", 13)
        c.drawRightString(w - 12 - uw, h / 2 - 4.5, price)


def cover_crop(path, box_w, box_h, dpi=300):
    """Centre-crop a swatch to the frame aspect ratio so every photo lines up."""
    im = PILImage.open(path).convert("RGB")
    target = box_w / box_h
    w, h = im.size
    if w / h > target:
        nw = int(h * target)
        im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / target)
        im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    out_dir = os.path.join(HERE, ".build")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, os.path.basename(path))
    im.save(out, quality=90)
    return out


def collection_block(no, name, dealing, items):
    price = selling_price(dealing)
    gap = 8
    cols = 4
    cell_w = (CONTENT_W - gap * (cols - 1)) / cols
    img_h = cell_w * 1.18

    cells = []
    for k, (design, fabric, art) in enumerate(items):
        src = os.path.join(ASSETS, "swatches", f"{no:02d}_{k + 1}.jpg")
        img = Image(cover_crop(src, cell_w, img_h), width=cell_w, height=img_h)
        cap = [Spacer(1, 4),
               Paragraph(art, S_CAP_ART),
               Paragraph(f"Design: {design}", S_CAP),
               Paragraph(f"Fabric: {fabric}", S_CAP)]
        cells.append([img] + cap)
    while len(cells) < cols:
        cells.append("")

    grid = Table([cells], colWidths=[cell_w + gap] * (cols - 1) + [cell_w])
    grid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-2, -1), gap),
        ("RIGHTPADDING", (-1, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return KeepTogether([CollectionBar(no, name, len(items), price, CONTENT_W),
                         Spacer(1, 7), grid, Spacer(1, 14)])


def summary_table():
    head = [Paragraph(t, s) for t, s in (("SL.", S_TH), ("COLLECTION", S_TH), ("ART SERIES", S_TH),
                                         ("FABRIC BASE", S_TH), ("SHADES", S_TH),
                                         ("PRICE / METRE", S_TH_R))]
    rows = [head]
    for no, (name, dealing, items) in enumerate(COLLECTIONS, 1):
        series = items[0][2].rsplit("-", 1)[0]
        bases = []
        for _, fabric, _ in items:
            base = fabric.rsplit("-", 1)[0] if "-C" in fabric else fabric
            if base not in bases:
                bases.append(base)
        rows.append([Paragraph(f"{no:02d}", S_TD), Paragraph(name.upper(), S_TD_B),
                     Paragraph(series, S_TD), Paragraph(" / ".join(bases), S_TD),
                     Paragraph(str(len(items)), S_TD_C), Paragraph(inr(selling_price(dealing)), S_TD_R)])
    widths = [0.07, 0.20, 0.17, 0.26, 0.13, 0.17]
    t = Table(rows, colWidths=[w * CONTENT_W for w in widths], repeatRows=1)
    ts = [
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, RULE),
    ]
    for r in range(2, len(rows), 2):
        ts.append(("BACKGROUND", (0, r), (-1, r), PAPER))
    t.setStyle(TableStyle(ts))
    return t


def title_block():
    left = [Paragraph("Border Price List", S_TITLE),
            Paragraph("Embroidered borders &amp; trims  ·  Rates per running metre", S_SUB)]
    right = [Paragraph(f"Date: <font name='Poppins-Medium' color='#1B1B1F'>{LIST_DATE:%d %B %Y}</font>", S_META_R),
             Paragraph(f"Ref: <font name='Poppins-Medium' color='#1B1B1F'>{LIST_REF}</font>", S_META_R)]
    t = Table([[left, right]], colWidths=[CONTENT_W * 0.65, CONTENT_W * 0.35])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    return t


def notes():
    lines = [
        "All rates are per running metre.",
        "Colours in photographs may vary slightly from the actual product; please confirm with a physical swatch.",
        "Rates are subject to change without prior notice.",
    ]
    body = [Paragraph("TERMS &amp; NOTES", S_SECTION), Spacer(1, 3)]
    body += [Paragraph(f"•&nbsp;&nbsp;{l}", S_NOTE) for l in lines]
    return KeepTogether(body)


def build():
    doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=SIDE, rightMargin=SIDE,
                          title="Osho Decor - Border Price List", author="Osho Decor",
                          subject="Border & trims price list", creator="Osho Decor")
    first = Frame(SIDE, 16 * mm, CONTENT_W, PAGE_H - 16 * mm - 47 * mm, id="first",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    later = Frame(SIDE, 16 * mm, CONTENT_W, PAGE_H - 16 * mm - 26 * mm, id="later",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate("first", [first], onPage=on_first, autoNextPageTemplate="later"),
                          PageTemplate("later", [later], onPage=on_later)])

    story = [title_block(), Spacer(1, 12),
             Paragraph("COLLECTIONS AT A GLANCE", S_SECTION), Spacer(1, 5),
             summary_table(), Spacer(1, 10), notes(), Spacer(1, 14)]
    for no, (name, dealing, items) in enumerate(COLLECTIONS, 1):
        story.append(collection_block(no, name, dealing, items))
    doc.build(story)
    print("Wrote", OUT)
    for no, (name, dealing, _) in enumerate(COLLECTIONS, 1):
        print(f"  {no:02d} {name:<10} {dealing:>4} -> {selling_price(dealing)}")


if __name__ == "__main__":
    build()
