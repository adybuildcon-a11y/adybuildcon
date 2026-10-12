"""Correct the two original Textura Homes price-list PDFs in place.

The original pages are reused as-is (same fonts, colours, lines and spacing);
only the affected rows are moved, duplicated or have their text replaced.

Corrections
  * Premiere Texture-1 and Premiere Texture-2 each list
        Cera  - Rate Rs. 365 / RRP 920
        Clare - Rate Rs. 285 / RRP 720
    (Osho Signature list), and Cera / Clare at the existing Your Price, Cut and
    Roll rates (Textura Homes list). Later serial numbers shift accordingly.
  * Textura Homes list: "Crom" -> "Croma".
  * Osho Signature list: Jute Craft RRP "990" set in Arial like every other cell
    (it was the only cell in Calibri).

Run:  python3 correct_price_lists.py
"""

import os

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_SIG = os.path.join(HERE, "original", "SIGNATURE_PRICE_LIST_1.pdf")
SRC_TEX = os.path.join(HERE, "original", "Textura_Homes_Price_List_Final.pdf")
OUT_SIG = os.path.join(HERE, "SIGNATURE_PRICE_LIST.pdf")
OUT_TEX = os.path.join(HERE, "Textura_Homes_Price_List.pdf")


def spans(page):
    for b in page.get_text("dict")["blocks"]:
        for line in b.get("lines", []):
            for s in line["spans"]:
                yield s


def find(page, text, near_y=None):
    """Span with exactly this text (closest to near_y if several)."""
    hits = [s for s in spans(page) if s["text"].strip() == text]
    if near_y is not None:
        hits = [s for s in hits if abs(s["bbox"][1] - near_y) < 4]
    if len(hits) != 1:
        raise ValueError(f"{text!r} near {near_y}: {len(hits)} matches on page {page.number}")
    return hits[0]


def replace(page, edits, font, fontbuffer=None):
    """edits: list of (span, new_text, align). Removes old glyphs, writes new text
    with the same font, size, colour and baseline."""
    edits = [e if len(e) == 4 else (*e, {}) for e in edits]
    for s, _, _, _ in edits:
        r = pymupdf.Rect(s["bbox"])
        page.add_redact_annot(r + (0.3, 0.6, -0.3, -0.6), fill=False)
    page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                          graphics=pymupdf.PDF_REDACT_LINE_ART_NONE,
                          text=pymupdf.PDF_REDACT_TEXT_REMOVE)
    if fontbuffer:
        page.insert_font(fontname="ArialMT", fontbuffer=fontbuffer)
    for s, new, align, opt in edits:
        fname, fobj, size = font(s)
        x0, x1 = s["bbox"][0], s["bbox"][2]
        width = fobj.text_length(new, size)
        x = {"left": x0, "center": (x0 + x1 - width) / 2, "right": x1 - width}[align]
        c = s["color"]
        color = ((c >> 16 & 255) / 255, (c >> 8 & 255) / 255, (c & 255) / 255)
        page.insert_text((x, opt.get("y", s["origin"][1])), new, fontname=fname, fontsize=size,
                         color=opt.get("color", color))


def place(dst_page, src_doc, pno, y0, y1, dst_y):
    w = dst_page.rect.width
    dst_page.show_pdf_page(pymupdf.Rect(0, dst_y, w, dst_y + (y1 - y0)), src_doc, pno,
                           clip=pymupdf.Rect(0, y0, w, y1))


# ---------------------------------------------------------------------------
def correct_signature():
    src = pymupdf.open(SRC_SIG)
    arial_xref = next(f[0] for f in src.get_page_fonts(1) if f[3].endswith("+ArialMT"))
    arial_buf = src.extract_font(arial_xref)[3]
    arial = pymupdf.Font(fontbuffer=arial_buf)

    def font_for(page):
        return lambda s: ("ArialMT", arial, 10.35 if s["font"].endswith("Calibri") else s["size"])

    work = pymupdf.open(SRC_SIG)
    work.fullcopy_page(1)                     # page 3: second copy of page 2 (for Premiere Texture-2 rows)
    p2, p3, p2b = work[1], work[2], work[3]

    pitch = 14.1166
    row = lambda k: 71.28 + k * pitch        # top of row k on pages 2/3
    # page 2 rows: 41 PT-1 group, 42 "62", 43 PT-2 group, 44 "63", 45 Natural group, 46 "64",
    #              47 Foldscape group, 48 "65", end 49
    calibri = next(s for s in spans(p2) if s["font"].endswith("Calibri"))
    jute = find(p2, "Rs. 395", calibri["bbox"][1])            # Jute Craft row
    replace(p2, [
        (find(p2, "1", row(42) + 1.9), "Cera", "left"),
        (find(p2, "2", row(44) + 1.9), "Clare", "left"),
        (find(p2, "64"), "66", "center"),
        (find(p2, "65"), "67", "center"),
        # Jute Craft RRP: Calibri/black on its own baseline -> Arial/#333333 on the row baseline
        (calibri, "990", "left",
         {"y": jute["origin"][1], "color": (0.2, 0.2, 0.2)}),
    ], font_for(p2), arial_buf)
    replace(p2b, [
        (find(p2b, "62"), "64", "center"),
        (find(p2b, "1", row(42) + 1.9), "Cera", "left"),
        (find(p2b, "63"), "65", "center"),
        (find(p2b, "2", row(44) + 1.9), "Clare", "left"),
    ], font_for(p2b), arial_buf)
    replace(p3, [(find(p3, "66"), "68", "center"),
                 (find(p3, "67"), "69", "center"),
                 (find(p3, "68"), "70", "center")], font_for(p3), arial_buf)

    out = pymupdf.open()
    out.insert_pdf(work, from_page=0, to_page=0)
    W, H = work[1].rect.width, work[1].rect.height

    # page 2: unchanged down to "62 Cera", then the new order, same table bottom
    pg = out.new_page(width=W, height=H)
    place(pg, work, 1, 0, row(43), 0)                       # ... PT-1 group, 62 Cera
    place(pg, work, 1, row(44), row(45), row(43))           # 63 Clare
    place(pg, work, 1, row(43), row(44), row(44))           # PT-2 group
    place(pg, work, 3, row(42), row(43), row(45))           # 64 Cera
    place(pg, work, 3, row(44), row(45), row(46))           # 65 Clare
    place(pg, work, 1, row(45), row(46), row(47))           # Natural Theory group
    place(pg, work, 1, row(46), row(47), row(48))           # 66 Natural Base
    place(pg, work, 1, row(49), H, row(49))                 # bottom border

    # page 3: Foldscape group + 67 Kenya moved over, rest pushed down two rows
    pg = out.new_page(width=W, height=H)
    edge = 0.75                                             # top border line thickness
    place(pg, work, 2, 0, row(0) + edge, 0)                 # page-3 top border, as original
    place(pg, work, 1, row(47) + edge, row(49), row(0) + edge)  # Foldscape group, 67 Kenya
    place(pg, work, 2, row(0), H - 2 * pitch, row(2))       # 68 Cera ... terms & notes

    out.set_metadata(src.metadata)
    out.save(OUT_SIG, garbage=4, deflate=True)


# ---------------------------------------------------------------------------
def correct_textura():
    src = pymupdf.open(SRC_TEX)
    helv = pymupdf.Font("helv")
    font = lambda s: ("helv", helv, s["size"])

    work = pymupdf.open(SRC_TEX)
    work.fullcopy_page(1)                     # page 2 copy for Premiere Texture-2 rows
    p1, p2, p2b = work[0], work[1], work[2]

    replace(p1, [(find(p1, "Crom"), "Croma", "left")], font)

    row = lambda k: 51 + k * 17               # page 2: row k top (header is 34-51)
    # rows 20 Cera(9), 21 Clare(9), 22 Natural(10), 23-24 Foldscape(11), 25-26 Thread(12), end 27
    pt = [s for s in spans(p2) if s["text"] == "Premiere Texture-1/2"]
    replace(p2, [(pt[0], "Premiere Texture-1", "left"), (pt[1], "Premiere Texture-1", "left"),
                 (find(p2, "10"), "11", "center")]
            + [(s, "12", "center") for s in spans(p2) if s["text"] == "11"]
            + [(s, "13", "center") for s in spans(p2) if s["text"] == "12"], font)
    pt = [s for s in spans(p2b) if s["text"] == "Premiere Texture-1/2"]
    replace(p2b, [(pt[0], "Premiere Texture-2", "left"), (pt[1], "Premiere Texture-2", "left"),
                  (find(p2b, "9", row(20) + 1.9), "10", "center"),
                  (find(p2b, "9", row(21) + 1.9), "10", "center")], font)

    out = pymupdf.open()
    out.insert_pdf(work, from_page=0, to_page=0)
    W, H = p2.rect.width, p2.rect.height
    pg = out.new_page(width=W, height=H)
    place(pg, work, 1, 0, row(22), 0)                       # ... Premiere Texture-1 Cera, Clare
    place(pg, work, 2, row(20), row(22), row(22))           # Premiere Texture-2 Cera, Clare
    place(pg, work, 1, row(22), row(27) + 1, row(24))       # Natural Theory ... Thread Touch

    out.set_metadata(src.metadata)
    out.save(OUT_TEX, garbage=4, deflate=True)


if __name__ == "__main__":
    correct_signature()
    correct_textura()
    print("Wrote", OUT_SIG)
    print("Wrote", OUT_TEX)
