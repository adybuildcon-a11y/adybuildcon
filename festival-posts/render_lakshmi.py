"""Render the Dhanteras Lakshmi posts in lakshmi-dhanteras.html to 1080x1350 PNGs."""

import glob
import os

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = ["osho-decor-dhanteras-lakshmi", "osho-signature-dhanteras-lakshmi"]


def main():
    exe = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=exe[-1] if exe else None)
        page = browser.new_page(viewport={"width": 1200, "height": 1500})
        page.goto("file://" + os.path.join(HERE, "lakshmi-dhanteras.html"))
        page.wait_for_selector("body[data-ready='1']")
        page.wait_for_timeout(300)
        for i, name in enumerate(NAMES, 7):
            path = os.path.join(HERE, "output", f"{i}-{name}.png")
            page.locator(f"#{name}").screenshot(path=path)
            print("wrote", path)
        browser.close()


if __name__ == "__main__":
    main()
