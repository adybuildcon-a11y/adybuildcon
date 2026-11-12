"""Build everything:  python3 make.py
  output/01_Instructions_Curated_Fabrics_Book.xlsx
  output/02_Instructions_Curated_Fabrics_Book.pdf
  output/03_Design_Guide_Curated_Fabrics_Book.pdf
  output/04_Print_Ready/  (CMYK print files)
  output/Curated_Fabrics_Book_Pack.zip
"""

import glob
import os
import shutil
import zipfile

import excel
from docs import design_guide, instructions
from layout import boards, layout_board, ordered_books
from printfiles import Renderer, board_files, master_files, spine_width

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
PR = os.path.join(OUT, "04_Print_Ready")


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(PR)
    books = ordered_books()
    bds = boards()
    for bd in bds:
        if bd["ready"]:
            layout_board(bd)
    spine_in, stack = spine_width(bds)
    hw = sorted(glob.glob(os.path.join(HERE, "assets", "reference", "handwritten-p*.jpg")))

    excel.build(os.path.join(OUT, "01_Instructions_Curated_Fabrics_Book.xlsx"), books, bds, spine_in, stack)
    with Renderer() as r:
        r.pdf(instructions(books, bds, spine_in, stack, hw), os.path.join(OUT, "02_Instructions_Curated_Fabrics_Book.pdf"), 8.27, 11.69)
        r.pdf(design_guide(books, bds, spine_in, stack), os.path.join(OUT, "03_Design_Guide_Curated_Fabrics_Book.pdf"), 11.69, 8.27)
        master, front_tmp, _, _ = master_files(r, bds, books, PR)
        os.replace(front_tmp, os.path.join(OUT, "Final_Book_Front_Proof_11x13.pdf"))
        for bd in bds:
            f, real = board_files(r, bd, PR)
            print("board", bd["no"], os.path.basename(f), "inside" if bd["ready"] else "cover only")
    with zipfile.ZipFile(os.path.join(OUT, "Curated_Fabrics_Book_Pack.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(glob.glob(os.path.join(OUT, "**", "*"), recursive=True)):
            if os.path.isfile(f) and not f.endswith(".zip"):
                z.write(f, os.path.join("Curated Fabrics Book", os.path.relpath(f, OUT)))
    print("spine", spine_in, "in  stack", stack, "mm")


if __name__ == "__main__":
    main()
