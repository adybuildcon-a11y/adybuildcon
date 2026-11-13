"""Render the 4-slide hiring carousel (1080 x 1350 PNG each): python3 render.py"""

import glob
import os

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    os.makedirs(os.path.join(HERE, "output"), exist_ok=True)
    exe = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=exe[-1] if exe else None)
        page = b.new_page(viewport={"width": 1200, "height": 1500})
        page.goto("file://" + os.path.join(HERE, "hiring.html"))
        page.wait_for_selector("body[data-ready='1']")
        for i in range(1, 5):
            out = os.path.join(HERE, "output", f"osho-decor-hiring-{i}.png")
            page.locator(f"#hiring-{i}").screenshot(path=out)
            print("wrote", out)
        out = os.path.join(HERE, "output", "osho-decor-hiring-single.png")
        page.locator("#hiring-single").screenshot(path=out)
        print("wrote", out)
        b.close()


if __name__ == "__main__":
    main()
