#!/usr/bin/env python3
"""Draw the ZKO1 entrance barcodes for the website's barcode page.

    tools/draw_barcode.py

Each character is a group of seven bars, its 7-bit ASCII code with the
most significant bit on the left: black for 1, white for 0.  Writes,
relative to the site root:

    assets/img/barcode-old.svg     the original orange wall
    assets/img/barcode-win.svg     the grey wall as it was repainted
    assets/img/barcode-new.svg     the grey wall after the repairs

The repairs are listed in DAMAGE as (line, character, bit), counting bit 0
as the least significant (the rightmost bar of a group), with what was put
there: 1 or 0 for a black or white bar, None for no bar at all.
"""
import html
import os

BLACK = '#000'
WHITE = '#fff'
ORANGE = '#ff6633'
GREY = '#c0c0c0'

DAMAGE = {
    (1, 0, 2): None,    # W -> ?, a bar missing
    (1, 6, 1): 1,       # D -> F, a black bar in place of a white one
}

BARCODES = {
    'barcode-old.svg': (ORANGE, ['digitalsoftwa', 'reengineering'], {}),
    'barcode-win.svg': (GREY, ['Customers Win', 'WhenWeDeliver'], {}),
    'barcode-new.svg': (GREY, ['Customers Win', 'WhenWeDeliver'], DAMAGE),
}

BAR = 3         # width of a bar
PITCH = 5.5     # from one bar to the next
GROUP = 46.5    # from one character to the next
HEIGHT = 74
MARGIN = 4


def bars(lines, damage):
    """Yield the line, character, position and value of every bar."""
    for row, text in enumerate(lines):
        for col, char in enumerate(text):
            for pos in range(7):
                bit = 6 - pos
                value = damage.get((row, col, bit), ord(char) >> bit & 1)
                if value is not None:
                    yield row, col, pos, value


def reading(lines, damage):
    """Return how the damaged wall reads, ? for a character with a bar missing."""
    out = []
    for row, text in enumerate(lines):
        line = ''
        for col, char in enumerate(text):
            code = ord(char)
            for bit in range(7):
                if (row, col, bit) in damage:
                    value = damage[(row, col, bit)]
                    if value is None:
                        code = None
                        break
                    code = code & ~(1 << bit) | value << bit
            line += '?' if code is None else chr(code)
        out.append(line)
    return ' '.join(out)


def svg(background, lines, damage):
    width = MARGIN * 2 + GROUP * (len(lines[0]) - 1) + PITCH * 6 + BAR
    height = MARGIN * (len(lines) + 1) + HEIGHT * len(lines)
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%g" height="%g" '
           'viewBox="0 0 %g %g" role="img">' % (width, height, width, height),
           '<title>%s</title>' % html.escape(reading(lines, damage)),
           '<rect width="100%%" height="100%%" fill="%s"/>' % background]
    for row, col, pos, value in bars(lines, damage):
        out.append('<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>' % (
            MARGIN + col * GROUP + pos * PITCH, MARGIN + row * (HEIGHT + MARGIN),
            BAR, HEIGHT, BLACK if value else WHITE))
    out.append('</svg>')
    return '\n'.join(out) + '\n'


def main():
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    for name, (background, lines, damage) in BARCODES.items():
        with open(os.path.join(root, 'assets', 'img', name), 'w') as f:
            f.write(svg(background, lines, damage))
        print(name, reading(lines, damage))


if __name__ == '__main__':
    main()
