"""Render the Osho Decor e-catalogue.

Writes output/Osho_Decor_E-Catalogue.pdf (A4) and output/pages/page-NN.jpg previews.
Usage: python3 render.py
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
    os.makedirs(os.path.join(OUT, "pages"), exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=chromium())
        page = browser.new_page(viewport={"width": 900, "height": 1200}, device_scale_factor=2)
        page.goto("file://" + os.path.join(HERE, "catalogue.html"))
        page.wait_for_selector("body[data-ready='1']")
        page.wait_for_timeout(300)
        pdf = os.path.join(OUT, "Osho_Decor_E-Catalogue.pdf")
        page.pdf(path=pdf, format="A4", print_background=True,
                 margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        pages = page.locator(".page")
        for i in range(pages.count()):
            pages.nth(i).screenshot(path=os.path.join(OUT, "pages", f"page-{i + 1:02d}.jpg"), quality=88)
        print("wrote", pdf, "-", pages.count(), "pages")
        browser.close()


if __name__ == "__main__":
    main()
