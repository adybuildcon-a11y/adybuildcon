"""Render the Junior Accountant (Panipat) hiring post: python3 render_accountant.py -> 1080 x 1350 PNG."""

import glob
import os

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    exe = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=exe[-1] if exe else None)
        page = b.new_page(viewport={"width": 1200, "height": 1500})
        page.goto("file://" + os.path.join(HERE, "accountant-panipat.html"))
        page.wait_for_selector("body[data-ready='1']")
        out = os.path.join(HERE, "output", "osho-decor-hiring-junior-accountant-panipat.png")
        page.locator("#accountant-panipat").screenshot(path=out)
        print("wrote", out)
        b.close()


if __name__ == "__main__":
    main()
