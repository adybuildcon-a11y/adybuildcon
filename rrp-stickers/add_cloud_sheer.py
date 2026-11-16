"""Osho Signature RRP stickers: add the Cloud Sheer sticker and fix Crom -> Croma.

The original sticker sheet is kept as-is.  The new Cloud Sheer sticker fills the
empty slot on page 2 (next to Drift Sheer) and is a copy of the Drift Sheer
sticker - same size, card colour, dashed cut line, rule and labels - with only
the book name, models and prices replaced.  Models and prices are set in
DejaVu Sans Bold and the book name in Times-Bold, the fonts the sheet uses.

RRP = the Osho Signature price list RRP (list rate x 2.5, rounded up to 10).

Run:  python3 add_cloud_sheer.py
"""

import os

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "original", "osho_signature_rrp_stickers_corrected.pdf")
OUT = os.path.join(HERE, "output", "Osho_Signature_RRP_Stickers.pdf")
DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

CLOUD_SHEER = [("ASTON", 720), ("ASTON STRIPE", 720), ("CANDID", 470), ("INTEL", 470),
               ("VISTARA", 470), ("PULSE", 790), ("CROWN", 400), ("VELORA", 530),
               ("MIST", 530), ("4216", 530), ("4218", 530), ("4202", 670), ("4205", 670),
               ("4210", 670), ("4213", 670), ("4221", 670)]

NAVY = (0x1B / 255, 0x28 / 255, 0x4C / 255)
DRIFT_BOX = pymupdf.Rect(40, 258, 297, 558)          # Drift Sheer sticker, page 2
FREE_BOX = pymupdf.Rect(315, 258, 572, 558)          # empty slot beside it
FIRST_BASELINE, PITCH, SIZE = 359.02, 12.3, 9.5      # model rows on the sticker
LEFT, RIGHT = 52.0, 285.01                           # model / price text edges


def spans(page, rect=None):
    for b in page.get_text("dict")["blocks"]:
        for line in b.get("lines", []):
            for s in line["spans"]:
                if rect is None or pymupdf.Rect(s["bbox"]).intersects(rect):
                    yield s


def redact(page, items):
    for s in items:
        page.add_redact_annot(pymupdf.Rect(s["bbox"]) + (0.3, 0.6, -0.3, -0.6), fill=False)
    page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                          graphics=pymupdf.PDF_REDACT_LINE_ART_NONE,
                          text=pymupdf.PDF_REDACT_TEXT_REMOVE)


def main():
    dejavu = pymupdf.Font(fontfile=DEJAVU_BOLD)
    doc = pymupdf.open(SRC)

    # --- Cloud Sheer sticker, built on a copy of page 2 then placed in the free slot
    wdoc = pymupdf.open(SRC)
    work = wdoc[1]
    old = [s for s in spans(work, DRIFT_BOX)
           if s["text"].startswith("BOOK:") or s["font"].endswith("DejaVuSans-Bold")]
    title = next(s for s in old if s["text"].startswith("BOOK:"))
    redact(work, old)
    work.insert_font(fontname="DJVB", fontfile=DEJAVU_BOLD)
    work.insert_text((title["bbox"][0], title["origin"][1]), "BOOK: CLOUD SHEER",
                     fontname="Times-Bold", fontsize=title["size"], color=NAVY)
    for i, (model, rrp) in enumerate(CLOUD_SHEER):
        y = FIRST_BASELINE + i * PITCH
        price = f"₹{rrp}"
        work.insert_text((LEFT, y), model, fontname="DJVB", fontsize=SIZE, color=NAVY)
        work.insert_text((RIGHT - dejavu.text_length(price, SIZE), y), price,
                         fontname="DJVB", fontsize=SIZE, color=NAVY)
    assert FIRST_BASELINE + (len(CLOUD_SHEER) - 1) * PITCH + 3 < DRIFT_BOX.y1 - 8

    clip = DRIFT_BOX + (-1, -1, 1, 1)                # include the dashed outline
    doc[1].show_pdf_page(FREE_BOX + (-1, -1, 1, 1), wdoc, 1, clip=clip)

    # --- Dark Shadow: CROM -> CROMA (as on the price lists)
    p1 = doc[0]
    crom = [s for s in spans(p1) if s["text"] == "CROM"]
    assert len(crom) == 1
    s = crom[0]
    redact(p1, crom)
    p1.insert_font(fontname="DJVB", fontfile=DEJAVU_BOLD)
    p1.insert_text((s["bbox"][0], s["origin"][1]), "CROMA", fontname="DJVB",
                   fontsize=s["size"], color=NAVY)

    doc.set_metadata(pymupdf.open(SRC).metadata)
    doc.save(OUT, garbage=4, deflate=True)
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
