"""Rebuild the two Textura Homes allover-series price lists from the CSVs in this folder.

  osho_signature.csv  -> Osho_Signature_Price_List.pdf   (Rate / Width / RRP)
  textura_homes.csv   -> Textura_Homes_Price_List.pdf    (Your Price / Cut Rate / Roll Rate)

Edit a CSV and run:  python3 build_price_lists.py
"""

import csv
import os

from reportlab.lib.colors import Color, HexColor, black, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE_W, PAGE_H = A4


def read(name):
    with open(os.path.join(HERE, name), newline="") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# Osho Signature list (same look as the original sheet export)
# ---------------------------------------------------------------------------
GREY_BAND = HexColor("#666666")
NAVY = HexColor("#1F2A44")
GOLD = HexColor("#8C6D1F")
GROUP_FILL = HexColor("#F2F0EA")
ROW_FILL = HexColor("#FBFAF7")
TEXT = HexColor("#333333")

X0, X1 = 71.3, 523.7
# S No | Collection | Design Name | Rate | Width | RRP
COLS = [X0, 128.0, 228.0, 318.7, 392.0, 458.0, X1]
ROW_H = 14.1
FS = 10.3
TOP = 71.3
BOTTOM = 770.0


class SignatureList:
    def __init__(self, path):
        self.c = canvas.Canvas(path, pagesize=A4)
        self.c.setTitle("Textura Homes - Osho Signature Allover Series Price List")
        self.c.setAuthor("Textura Homes")
        self.y = TOP

    # canvas uses bottom-left origin; work in top-down y and flip here
    def _rect(self, x0, y0, x1, y1, fill, stroke=False):
        self.c.setFillColor(fill)
        self.c.rect(x0, PAGE_H - y1, x1 - x0, y1 - y0, stroke=0, fill=1)
        if stroke:
            self.c.setStrokeColor(black)
            self.c.setLineWidth(0.7)
            self.c.rect(x0, PAGE_H - y1, x1 - x0, y1 - y0, stroke=1, fill=0)

    def _text(self, txt, x, y, font="Helvetica", size=FS, color=TEXT, align="left"):
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        draw = {"left": self.c.drawString, "right": self.c.drawRightString,
                "center": self.c.drawCentredString}[align]
        draw(x, PAGE_H - y, txt)

    def _outline(self, y0, y1):
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.7)
        self.c.line(X0, PAGE_H - y0, X0, PAGE_H - y1)
        self.c.line(X1, PAGE_H - y0, X1, PAGE_H - y1)

    def need(self, rows):
        if self.y + rows * ROW_H > BOTTOM:
            self._close_page()
            self.c.showPage()
            self.y = TOP
            self.c.setStrokeColor(black)
            self.c.setLineWidth(0.7)
            self.c.line(X0, PAGE_H - self.y, X1, PAGE_H - self.y)

    def _close_page(self):
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.7)
        self.c.line(X0, PAGE_H - self.y, X1, PAGE_H - self.y)

    def header(self):
        y = TOP
        self._rect(X0, y, X1, y + 24.7, GREY_BAND)
        self._text("TEXTURA HOMES", PAGE_W / 2, y + 19.5, "Helvetica-Bold", 19.8, white, "center")
        y += 24.7
        self._rect(X0, y, X1, y + 39.5, NAVY)
        self._text("OSHO SIGNATURE", PAGE_W / 2, y + 20, "Helvetica-Bold", 19.8, white, "center")
        y += 39.5
        self._text("ALLOVER SERIES - PRICE LIST", PAGE_W / 2, y + 12.8, "Helvetica-Bold", 13.2, NAVY, "center")
        y += 17
        self._text("(Millennium Edition & Elite Edition)", PAGE_W / 2, y + 10, "Helvetica", FS, GOLD, "center")
        y += 13
        # two empty grid rows, as in the original
        for _ in range(2):
            self._grid_row(y, white)
            y += ROW_H
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.7)
        self.c.line(X0, PAGE_H - (TOP + 24.7 + 39.5), X1, PAGE_H - (TOP + 24.7 + 39.5))
        self._outline(TOP, y)
        self.c.line(X0, PAGE_H - TOP, X1, PAGE_H - TOP)
        # column headings
        self._rect(X0, y, X1, y + ROW_H, NAVY)
        labels = ["S No", "Collection", "Design Name", "Rate (Rs./mtr)", "Width (Inch)", "RRP"]
        for i, lab in enumerate(labels):
            self._text(lab, (COLS[i] + COLS[i + 1]) / 2, y + 10.6, "Helvetica-Bold", FS, white, "center")
        self.y = y + ROW_H

    def _grid_row(self, y, fill):
        self._rect(X0, y, X1, y + ROW_H, fill)
        self.c.setStrokeColor(black)
        self.c.setLineWidth(0.5)
        for x in COLS:
            self.c.line(x, PAGE_H - y, x, PAGE_H - y - ROW_H)
        self.c.line(X0, PAGE_H - y - ROW_H, X1, PAGE_H - y - ROW_H)

    def band(self, label):
        y = self.y
        self._rect(X0, y, X1, y + ROW_H, GOLD)
        self._text(label, PAGE_W / 2, y + 10.8, "Helvetica-Bold", 11.3, white, "center")
        self._outline(y, y + ROW_H)
        self.y += ROW_H

    def group(self, label):
        y = self.y
        self._rect(X0, y, X1, y + ROW_H, GROUP_FILL)
        self._text(label, X0 + 3, y + 10.6, "Helvetica-Bold", FS, NAVY)
        self._outline(y, y + ROW_H)
        self.c.line(X0, PAGE_H - y - ROW_H, X1, PAGE_H - y - ROW_H)
        self.y += ROW_H

    def item(self, no, coll, design, rate, width, rrp, shade):
        y = self.y
        self._grid_row(y, ROW_FILL if shade else white)
        b = y + 10.6
        self._text(str(no), (COLS[0] + COLS[1]) / 2, b, align="center")
        self._text(coll, COLS[1] + 3, b)
        self._text(design, COLS[2] + 3, b)
        self._text(f"Rs. {rate}", COLS[4] - 4, b, align="right")
        self._text(width, (COLS[4] + COLS[5]) / 2, b, align="center")
        self._text(rrp, (COLS[5] + COLS[6]) / 2, b, align="center")
        self._outline(y, y + ROW_H)
        self.y += ROW_H

    def blank(self):
        self._grid_row(self.y, white)
        self._outline(self.y, self.y + ROW_H)
        self.y += ROW_H

    def terms(self, lines):
        self.need(len(lines) + 2)
        y = self.y
        self._rect(X0, y, X1, y + ROW_H + 1, NAVY)
        self._text("TERMS & NOTES", X0 + 3, y + 11.2, "Helvetica-Bold", 11.3, white)
        self.y += ROW_H + 1
        for line in lines + [""]:
            y = self.y
            self._rect(X0, y, X1, y + ROW_H, GROUP_FILL)
            if line:
                self._text(f"• {line}", X0 + 3, y + 10.6)
            self.c.setStrokeColor(black)
            self.c.setLineWidth(0.5)
            self.c.line(X0, PAGE_H - y - ROW_H, X1, PAGE_H - y - ROW_H)
            self._outline(y, y + ROW_H)
            self.y += ROW_H

    def build(self, rows):
        self.header()
        edition = coll = None
        no = 0
        for r in rows:
            if r["Edition"] != edition:
                if edition is not None:
                    self.need(1)
                    self.blank()
                self.need(3)
                edition = r["Edition"]
                self.band(edition.upper())
            if r["Collection"] != coll:
                self.need(2)
                coll = r["Collection"]
                self.group(coll)
            self.need(1)
            no += 1
            self.item(no, r["Collection"], r["Design Name"], r["Rate (Rs./mtr)"],
                      r["Width (Inch)"], r["RRP"], no % 2 == 1)
        self.need(1)
        self.blank()
        self.terms(["GST as applicable.",
                    "For cut orders, surface courier is free.",
                    "Roll rate is 10% less from the cut rate.",
                    "All fabric widths are 54 inches."])
        self._close_page()
        self.c.save()


# ---------------------------------------------------------------------------
# Textura Homes list (Your Price / Cut Rate / Roll Rate)
# ---------------------------------------------------------------------------
def build_textura(rows, path):
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=30.8, rightMargin=30.8,
                            topMargin=30, bottomMargin=30,
                            title="Textura Homes - Allover Series Price List", author="Textura Homes")
    title = ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=16, leading=20, alignment=TA_CENTER)
    sub = ParagraphStyle("s", fontName="Helvetica", fontSize=10, leading=13, alignment=TA_CENTER)

    head = ["S.No", "Book Name", "Collection", "Shade / Design Name", "Your Price", "Cut Rate", "Roll Rate"]
    data = [head]
    book = coll = None
    sno = 0
    for r in rows:
        if r["Book Name"] != book:
            book, sno, coll = r["Book Name"], 0, None
        if r["Collection"] != coll:
            coll = r["Collection"]
            sno += 1
        data.append([str(sno), r["Book Name"], r["Collection"], r["Shade / Design Name"],
                     r["Your Price"], r["Cut Rate"], r["Roll Rate"]])

    widths = [32.0, 92.3, 110.0, 119.8, 60.2, 59.6, 59.6]
    t = Table(data, colWidths=widths, rowHeights=17, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1F2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (4, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#9CA3AF")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    for i in range(2, len(data), 2):
        style.append(("BACKGROUND", (0, i), (-1, i), HexColor("#F3F4F6")))
    t.setStyle(TableStyle(style))
    doc.build([Paragraph("TEXTURA HOMES", title), Paragraph("Allover Series Price List", sub),
               Spacer(1, 8), t])


if __name__ == "__main__":
    SignatureList(os.path.join(HERE, "Osho_Signature_Price_List.pdf")).build(read("osho_signature.csv"))
    build_textura(read("textura_homes.csv"), os.path.join(HERE, "Textura_Homes_Price_List.pdf"))
    print("Built both price lists.")
