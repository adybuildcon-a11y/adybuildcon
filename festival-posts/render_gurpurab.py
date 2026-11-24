"""Render guru-nanak-jayanti.html to a 1080x1350 PNG (Osho Decor, +91 98105 59026)."""

import glob
import os

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "osho-decor-guru-nanak-jayanti-9810559026"


def main():
    exe = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=exe[-1] if exe else None)
        page = browser.new_page(viewport={"width": 1200, "height": 1500})
        page.goto("file://" + os.path.join(HERE, "guru-nanak-jayanti.html"))
        page.wait_for_selector("body[data-ready='1']")
        page.wait_for_timeout(300)
        path = os.path.join(HERE, "output", f"9-{NAME}.png")
        page.locator(f"#{NAME}").screenshot(path=path)
        print("wrote", path)
        browser.close()


if __name__ == "__main__":
    main()
