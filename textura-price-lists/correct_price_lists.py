"""Correct the two original Textura Homes price-list PDFs in place.

The original pages are reused as-is (same fonts, colours, lines and spacing);
only the affected rows are moved, duplicated or have their text replaced.

Corrections
  * Osho Signature list: Cloud Sheer book (16 designs) added to the Elite
    Edition after Thread Touch, S.No 71-86.
    Rate = dealer cut rate + 15 (above 200) / + 10 (below 200), rounded up to
    the next multiple of 5; RRP = rate x 2.5 rounded up to the next 10.
  * Textura Homes list: Cloud Sheer added as Elite Edition book 14 after
    Thread Touch; Your Price = the dealer cut rate on the Cloud Sheer card, Cut and
    Roll by the list's own rule.
  * Premiere Texture-1 and Premiere Texture-2 each list
        Cera  - Rate Rs. 365 / RRP 920
        Clare - Rate Rs. 285 / RRP 720
    (Osho Signature list), and Cera Rs.365 / Clare Rs.285 Your Price with matching
    Cut and Roll rates (Textura Homes list). Later serial numbers shift accordingly.
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


def replace(page, edits, font, fontbuffer=None, fontbuffers=None):
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
    for name, buf in (fontbuffers or {}).items():
        page.insert_font(fontname=name, fontbuffer=buf)
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
# Cloud Sheer (Elite Edition, after Thread Touch).  Dealer cut rates from the
# Cloud Sheer card; list rate = dealer + 15 (above 200) or + 10 (below 200), then
# rounded UP to the next multiple of 5.  RRP follows the list's own rule
# (rate x 2.5, rounded up to the next 10 - matches the list's rows).
CLOUD_SHEER = [("Aston", 270), ("Aston Stripe", 270), ("Candid", 175), ("Intel", 175),
               ("Vistara", 175), ("Pulse", 299), ("Crown", 149), ("Velora", 199),
               ("Mist", 199), ("4216", 199), ("4218", 199), ("4202", 249), ("4205", 249),
               ("4210", 249), ("4213", 249), ("4221", 249)]


def list_rate(dealer):
    up = dealer + (15 if dealer > 200 else 10)
    return -(-up // 5) * 5


def rrp(rate):
    return -(-rate * 25 // 100) * 10


def correct_signature():
    """Rebuilds the Osho Signature list from the original by moving whole table rows
    (same fonts, colours, lines and spacing) and replacing only the text that changes.

      * Cloud Sheer (16 designs) added to the Elite Edition after Thread Touch,
        S.No 71-86.
      * Premiere Texture-1 and -2 each list Cera Rs.365 / 920 and Clare Rs.285 / 720.
      * Jute Craft RRP "990" set in Arial like every other cell (was Calibri).
    """
    src = pymupdf.open(SRC_SIG)
    bufs = {}
    for f in src.get_page_fonts(1):
        for name in ("ArialMT", "Arial-BoldMT"):
            if f[3].endswith("+" + name):
                bufs[name] = src.extract_font(f[0])[3]
    fonts = {n: pymupdf.Font(fontbuffer=b) for n, b in bufs.items()}

    def font(s):
        bold = "Bold" in s["font"]
        name = "Arial-BoldMT" if bold else "ArialMT"
        return name, fonts[name], 10.35 if s["font"].endswith("Calibri") else s["size"]

    def edit(page, edits):
        replace(page, edits, font, fontbuffers=bufs)

    pitch = 14.1166
    row = lambda k: 71.28 + k * pitch        # top of table row k on pages 2/3
    y_text = lambda k: row(k) + 1.9          # top of the text in row k

    def cell(page, k, x0):
        """Span in row k whose left edge is at x0 (column)."""
        hits = [s for s in spans(page) if abs(s["bbox"][1] - y_text(k)) < 4
                and abs(s["bbox"][0] - x0) < 3.5]
        if len(hits) != 1:
            raise ValueError(f"row {k} x {x0}: {len(hits)} spans on page {page.number}")
        return hits[0]

    SNO, COLL, DESIGN, RATE = 101.5, 145.39, 230.09, 353.94

    def rrp_cell(page, k):
        hits = [s for s in spans(page) if abs(s["bbox"][1] - y_text(k)) < 4 and s["bbox"][0] > 470]
        assert len(hits) == 1, (page.number, k, hits)
        return hits[0]

    work = pymupdf.open(SRC_SIG)
    P1, P2 = 1, 2
    work.fullcopy_page(P1)                         # pages 4, 5: copies of page 2 for
    work.fullcopy_page(P1)                         # Cloud Sheer rows and header
    A, D = work[P1], work[P2]                      # original pages 2 and 3, renumbered
    B, C = work[3], work[4]

    # original page 2 rows: 0-11 Drift Sheer 31-42, 12 blank, 13 ELITE, 14 Tweed hdr,
    # 15-18 (43-46) ... 41 PT-1 hdr, 42 "62 .. 1", 43 PT-2 hdr, 44 "63 .. 2",
    # 45 Natural hdr, 46 "64", 47 Foldscape hdr, 48 "65 Kenya"; table ends at row 49.
    # original page 3 rows: 0 "66 Foldscape Cera", 1 Thread hdr, 2 "67", 3 "68", 4 blank,
    # 5 TERMS, ...
    # Cloud Sheer is an Elite Edition book: it follows Thread Touch, S.No 71-86.
    first_cloud = 71
    calibri = next(s for s in spans(A) if s["font"].endswith("Calibri"))
    jute = find(A, "Rs. 395", calibri["bbox"][1])
    edit(A, [(cell(A, 42, DESIGN), "Cera", "left"),                  # 62 PT-1 Cera
             (cell(A, 44, DESIGN), "Clare", "left"),                 # 63 PT-1 Clare
             (cell(A, 46, SNO), "66", "center"),                     # Natural Base
             (cell(A, 48, SNO), "67", "center"),                     # Foldscape Kenya
             (calibri, "990", "left", {"y": jute["origin"][1], "color": (0.2, 0.2, 0.2)})])

    def cloud_row(page, k, i):
        name, dealer = CLOUD_SHEER[i]
        rate = list_rate(dealer)
        return [(cell(page, k, SNO), str(first_cloud + i), "center"),
                (cell(page, k, COLL), "Cloud Sheer", "left"),
                (cell(page, k, DESIGN), name, "left"),
                (cell(page, k, RATE), f"Rs. {rate}", "right"),
                (rrp_cell(page, k), str(rrp(rate)), "center")]

    n = len(CLOUD_SHEER)
    edits = [e for k in range(12) for e in cloud_row(B, k, k)]
    edits += [(cell(B, 14, 74.11), "Cloud Sheer", "left"),
              (cell(B, 42, SNO), "64", "center"), (cell(B, 42, DESIGN), "Cera", "left"),
              (cell(B, 44, SNO), "65", "center"), (cell(B, 44, DESIGN), "Clare", "left")]
    edit(B, edits)
    edit(C, [e for k in range(n - 12) for e in cloud_row(C, k, 12 + k)])
    edit(D, [(cell(D, 0, SNO), "68", "center"),
             (cell(D, 2, SNO), "69", "center"),
             (cell(D, 3, SNO), "70", "center")])

    pa, pb, pc, pd = (p.number for p in (A, B, C, D))
    seq = ([(pa, k) for k in range(42)]                       # Drift Sheer 31-42 ... PT-1 hdr
           + [(pa, 42), (pa, 44), (pa, 43), (pb, 42), (pb, 44)]   # PT-1 Cera/Clare, PT-2 ...
           + [(pa, k) for k in range(45, 49)]                 # Natural Theory 66, Foldscape 67
           + [(pd, k) for k in range(4)]                      # 68 Cera, Thread Touch 69-70
           + [(pb, 14)]                                       # Cloud Sheer header
           + [(pb, k) for k in range(12)] + [(pc, k) for k in range(n - 12)])   # 71-86
    per_page = 49

    out = pymupdf.open()
    out.insert_pdf(work, from_page=0, to_page=0)
    W, H = A.rect.width, A.rect.height
    first, rest = seq[:per_page], seq[per_page:]

    pg = out.new_page(width=W, height=H)
    place(pg, work, pa, 0, row(0), 0)                         # page top, table top border
    for i, (pn, k) in enumerate(first):
        place(pg, work, pn, row(k), row(k + 1), row(i))
    place(pg, work, pa, row(49), H, row(len(first)))          # table bottom border

    pg = out.new_page(width=W, height=H)
    place(pg, work, pd, 0, row(0), 0)
    for i, (pn, k) in enumerate(rest):
        place(pg, work, pn, row(k), row(k + 1), row(i))
    place(pg, work, pd, row(4), H, row(len(rest)))            # blank row, terms & notes

    out.set_metadata(src.metadata)
    out.save(OUT_SIG, garbage=4, deflate=True)


# ---------------------------------------------------------------------------
def correct_textura():
    src = pymupdf.open(SRC_TEX)
    helv = pymupdf.Font("helv")
    font = lambda s: ("helv", helv, s["size"])

    work = pymupdf.open(SRC_TEX)
    work.fullcopy_page(1)                     # page 2 copy for Premiere Texture-2 rows
    work.fullcopy_page(1)                     # page 2 copy for the Cloud Sheer rows
    p1, p2, p2b, p2c = work[0], work[1], work[2], work[3]

    replace(p1, [(find(p1, "Crom"), "Croma", "left")], font)

    row = lambda k: 51 + k * 17               # page 2: row k top (header is 34-51)
    # rows 20 Cera(9), 21 Clare(9), 22 Natural(10), 23-24 Foldscape(11), 25-26 Thread(12), end 27
    # Premiere Texture Cera / Clare: new Your Price; Cut and Roll follow the list's own
    # rule (Cut = Your x 0.8075, Roll = Your x 0.7125, rounded) - matches every row.
    def prices(page):
        out = []
        for k, (old, your) in {20: (("Rs.350", "Rs.283", "Rs.249"), 365),
                               21: (("Rs.275", "Rs.222", "Rs.196"), 285)}.items():
            new = (your, int(your * 0.8075 + 0.5), int(your * 0.7125 + 0.5))
            out += [(find(page, o, row(k) + 1.9), f"Rs.{n}", "right") for o, n in zip(old, new)]
        return out

    pt = [s for s in spans(p2) if s["text"] == "Premiere Texture-1/2"]
    replace(p2, [(pt[0], "Premiere Texture-1", "left"), (pt[1], "Premiere Texture-1", "left"),
                 (find(p2, "10"), "11", "center")] + prices(p2)
            + [(s, "12", "center") for s in spans(p2) if s["text"] == "11"]
            + [(s, "13", "center") for s in spans(p2) if s["text"] == "12"], font)
    pt = [s for s in spans(p2b) if s["text"] == "Premiere Texture-1/2"]
    replace(p2b, [(pt[0], "Premiere Texture-2", "left"), (pt[1], "Premiere Texture-2", "left"),
                  (find(p2b, "9", row(20) + 1.9), "10", "center"),
                  (find(p2b, "9", row(21) + 1.9), "10", "center")] + prices(p2b), font)

    # Cloud Sheer = Elite Edition book 14, after Thread Touch (rows 29-44 of the new
    # page 2).  Your Price = the dealer cut rate on the Cloud Sheer card; Cut and Roll
    # follow the list's rule above.  Rows 1-16 of the page-2 copy are the templates,
    # which keeps the white / grey row stripes in step (29 - 1 = even).
    def cells(page, k):
        found = sorted((s for s in spans(page) if abs(s["bbox"][1] - (row(k) + 1.9)) < 3),
                       key=lambda s: s["bbox"][0])
        assert len(found) == 7, (k, [x["text"] for x in found])
        return found
    edits = []
    for i, (name, your) in enumerate(CLOUD_SHEER):
        new = ["14", "Elite Edition", "Cloud Sheer", name, f"Rs.{your}",
               f"Rs.{int(your * 0.8075 + 0.5)}", f"Rs.{int(your * 0.7125 + 0.5)}"]
        align = ["center", "left", "left", "left", "right", "right", "right"]
        edits += list(zip(cells(p2c, 1 + i), new, align))
    replace(p2c, edits, font)
    n = len(CLOUD_SHEER)

    out = pymupdf.open()
    out.insert_pdf(work, from_page=0, to_page=0)
    W, H = p2.rect.width, p2.rect.height
    pg = out.new_page(width=W, height=H)
    place(pg, work, 1, 0, row(22), 0)                       # ... Premiere Texture-1 Cera, Clare
    place(pg, work, 2, row(20), row(22), row(22))           # Premiere Texture-2 Cera, Clare
    place(pg, work, 1, row(22), row(27), row(24))           # Natural Theory ... Thread Touch
    place(pg, work, 3, row(1), row(1 + n), row(29))         # 14 Cloud Sheer (16 rows)
    place(pg, work, 1, row(27), row(27) + 1, row(29 + n))   # table bottom line

    out.set_metadata(src.metadata)
    out.save(OUT_TEX, garbage=4, deflate=True)


if __name__ == "__main__":
    correct_signature()
    correct_textura()
    print("Wrote", OUT_SIG)
    print("Wrote", OUT_TEX)
