"""Render the Osho Decor Diwali greeting card.

Each design writes output/<name>.png (1500x2100 = 5x7 in at 300 dpi)
and output/<name>.pdf (print-ready 5x7 in, vector).
"""

import glob
import os

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
CARDS = [("diwali-card.html", "osho-decor-diwali-card"),
         ("diwali-card-2.html", "osho-decor-diwali-card-2"),
         ("diwali-card-3.html", "osho-decor-diwali-card-3-photo"),
         ("diwali-card-4.html", "osho-decor-diwali-card-4-full-photo"),
         ("diwali-card-4b.html", "osho-decor-diwali-card-4-full-photo-9810559026")]


def chromium():
    found = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))
    return found[-1] if found else None


def main():
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=chromium())
        for html, name in CARDS:
            page = browser.new_page(viewport={"width": 1500, "height": 2100})
            page.goto("file://" + os.path.join(HERE, html))
            page.wait_for_selector("body[data-ready='1']")
            page.wait_for_timeout(300)
            png = os.path.join(OUT, f"{name}.png")
            page.locator("#card").screenshot(path=png)
            pdf = os.path.join(OUT, f"{name}.pdf")
            # 1500 css px -> 5 in (480 css px): scale 0.32
            page.pdf(path=pdf, width="5in", height="7in", scale=0.32, print_background=True,
                     margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
            print("wrote", png, "| gap:", page.get_attribute("body", "data-gap"))
            print("wrote", pdf)
            page.close()
        browser.close()


if __name__ == "__main__":
    main()
