"""Render the six festival posts in posts.html to 1080x1350 PNG files.

Usage:  python3 render.py
Needs:  pip install playwright   (uses the Chromium already on the machine)
"""

import glob
import os

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
NAMES = ["osho-decor-dussehra", "osho-decor-dhanteras", "osho-decor-diwali",
         "osho-signature-dussehra", "osho-signature-dhanteras", "osho-signature-diwali"]


def chromium():
    found = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))
    return found[-1] if found else None


def main():
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=chromium())
        page = browser.new_page(viewport={"width": 1200, "height": 1500}, device_scale_factor=1)
        page.goto("file://" + os.path.join(HERE, "posts.html"))
        page.wait_for_selector("body[data-ready='1']")
        page.wait_for_timeout(300)
        for i, name in enumerate(NAMES, 1):
            path = os.path.join(OUT, f"{i}-{name}.png")
            page.locator(f"#{name}").screenshot(path=path)
            print("wrote", path)
        browser.close()


if __name__ == "__main__":
    main()
