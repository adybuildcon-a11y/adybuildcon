"""Render the Osho Decor Diwali greeting card.

Writes output/osho-decor-diwali-card.png (1500x2100 = 5x7 in at 300 dpi)
and output/osho-decor-diwali-card.pdf (print-ready 5x7 in, vector).
"""

import glob
import os

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")


def chromium():
    found = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))
    return found[-1] if found else None


def main():
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=chromium())
        page = browser.new_page(viewport={"width": 1500, "height": 2100})
        page.goto("file://" + os.path.join(HERE, "diwali-card.html"))
        page.wait_for_selector("body[data-ready='1']")
        page.wait_for_timeout(300)
        png = os.path.join(OUT, "osho-decor-diwali-card.png")
        page.locator("#card").screenshot(path=png)
        pdf = os.path.join(OUT, "osho-decor-diwali-card.pdf")
        # 1500 css px -> 5 in (480 css px): scale 0.32
        page.pdf(path=pdf, width="5in", height="7in", scale=0.32, print_background=True,
                 margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        print("wrote", png)
        print("wrote", pdf)
        browser.close()


if __name__ == "__main__":
    main()
