#!/usr/bin/env python3
"""Draw the website's favicon and home screen icons.

    tools/make_icons.py

Draws "z" and "k" in boxes side by side, after Digital's logo: white
Montserrat bold on Digital blue.  Writes, relative to the site root:

    favicon.ico                            16, 32 and 48 px, for browser tabs
    favicon-32x32.png
    apple-touch-icon.png                   180 px, for phone home screens
    apple-touch-icon-precomposed.png
    apple-touch-icon-120x120.png           120 px, asked for by older iPhones
    apple-touch-icon-120x120-precomposed.png

Needs Playwright for Python with its Chromium (pip install playwright;
playwright install chromium), and a network connection for the Google Font.
"""
import os
import struct

from playwright.sync_api import sync_playwright

BLUE = '#1f3f8f'
WHITE = '#fff'
BLACK = '#000'

PAGE = """<!doctype html>
<html><head>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=block"
      rel="stylesheet">
<style>
  html, body {{ margin: 0; background: transparent; }}
  div {{
    width: {size}px; height: {size}px; padding: {pad}px;
    box-sizing: border-box;
    display: flex; gap: {gap}px;
    background: {background};
  }}
  span {{
    flex: 1;
    display: flex; align-items: center; justify-content: center;
    padding-bottom: {lift}px;
    background: {box}; color: {ink};
    font: 700 {font}px/1 Montserrat, sans-serif;
  }}
</style></head>
<body><div><span>z</span><span>k</span></div></body></html>
"""


def render(page, size, background):
    """Return a PNG of the icon, size pixels square.

    Tab icons have a transparent background and boxes the full height of
    the icon; home screen icons sit on black with a margin, as phones don't
    allow transparency.
    """
    pad = round(size * .08) if background else 0
    gap = max(1, round(size * .06))
    width = (size - 2 * pad - gap) / 2
    page.set_viewport_size({'width': size, 'height': size})
    page.set_content(PAGE.format(size=size, pad=pad, gap=gap,
                                 background=background or 'transparent',
                                 box=BLUE, ink=WHITE, font=round(width * 1.15),
                                 lift=round(width * .12)))
    page.evaluate('document.fonts.ready')
    return page.screenshot(omit_background=True)


def ico(pngs):
    """Pack PNGs, keyed by size, into a .ico file."""
    head = struct.pack('<HHH', 0, 1, len(pngs))
    offset = len(head) + 16 * len(pngs)
    entries, data = b'', b''
    for size, png in sorted(pngs.items()):
        entries += struct.pack('<BBBBHHII', size % 256, size % 256, 0, 0, 1, 32,
                               len(png), offset + len(data))
        data += png
    return head + entries + data


def main():
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    files = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        small = {size: render(page, size, None) for size in (16, 32, 48)}
        touch = {size: render(page, size, BLACK) for size in (120, 180)}
        browser.close()
    files['favicon.ico'] = ico(small)
    files['favicon-32x32.png'] = small[32]
    files['apple-touch-icon.png'] = touch[180]
    files['apple-touch-icon-precomposed.png'] = touch[180]
    files['apple-touch-icon-120x120.png'] = touch[120]
    files['apple-touch-icon-120x120-precomposed.png'] = touch[120]
    for name, data in files.items():
        with open(os.path.join(root, name), 'wb') as f:
            f.write(data)
        print(name)


if __name__ == '__main__':
    main()
