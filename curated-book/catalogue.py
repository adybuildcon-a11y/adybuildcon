"""Catalogue-book images (Neo Luna design, ../osho-books) printed on the curated book:

  assets/catalogue/board-<board-id>.png   4 tilted books on the back of every card, led by its own book(s)
  assets/catalogue/all-books.png          the 20 books, two rows of 10, on the back of the master binder
"""

import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(HERE, "assets", "catalogue")
_spec = importlib.util.spec_from_file_location("osho_books", os.path.join(HERE, "..", "osho-books", "build.py"))
osho_books = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(osho_books)


from art import board_img as board_png, all_img as all_png   # noqa: E402  (same paths the artwork reads)


def four_for(bd, books):
    """The board's own book(s) first, then the next books in book order."""
    own = list(bd["books"])
    order = [b for b in books if b not in own]
    start = max(b["seq"] for b in own)
    nxt = [b for b in order if b["seq"] > start] + [b for b in order if b["seq"] < start]
    return (own + nxt)[:4]


def build(books, bds):
    os.makedirs(DIR, exist_ok=True)
    jobs = []
    for bd in bds:
        html, w, h = osho_books.four_books_html(four_for(bd, books))
        jobs.append((board_png(bd), html, w, h))
    html, w, h = osho_books.twenty_books_html(books)
    jobs.append((all_png(), html, w, h))
    osho_books.render_pngs(jobs)
    return [j[0] for j in jobs]


if __name__ == "__main__":
    from layout import boards, ordered_books
    for p in build(ordered_books(), boards()):
        print("Wrote", p)
