"""Render the visiting card: output/*.png (3x, 3825x2148) and a vector PDF (same page size as the original scan)."""

import glob
import os
import sys

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")


def main(plain=False):
    os.makedirs(OUT, exist_ok=True)
    exe = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=exe[-1] if exe else None)
        page = browser.new_page(viewport={"width": 1300, "height": 1500}, device_scale_factor=3)
        page.goto("file://" + os.path.join(HERE, "card.html") + ("#plain" if plain else ""))
        page.wait_for_selector("body[data-ready='1']")
        page.wait_for_timeout(200)
        tag = "-plain" if plain else ""
        for t in page.evaluate("window.ext"): print(t)
        for side in ("front", "back"):
            page.locator(f"#{side}").screenshot(path=os.path.join(OUT, f"card-{side}{tag}.png"))
        if not plain:
            page.pdf(path=os.path.join(OUT, "The_Furnish_Atelier_Kamlesh_Agrawal_Osho.pdf"),
                     width="8.5in", height="4.7708in", scale=0.64, print_background=True,
                     margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        browser.close()
    print("rendered", "plain" if plain else "final")


if __name__ == "__main__":
    main(plain="--plain" in sys.argv)
