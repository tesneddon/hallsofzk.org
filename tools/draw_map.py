#!/usr/bin/env python3
"""Draw the map of The Halls of ZK for the website's map page.

    tools/draw_map.py ~/zk

Reads the rooms from zk/zkroom.room in a checkout of
github.com/tesneddon/zk and draws each floor as a hand-drawn master plan on
graph paper, in the style of Usborne's "Write Your Own Adventure Programs
for Your Microcomputer" (1983).  Writes, relative to the site root:

    assets/img/map_blue.png        one image per floor
    assets/img/map_yellow.png
    assets/img/map_red.png

Room positions are set by hand in FLOORS below, as the game's geography
(the twisty maze in particular) does not fit a grid on its own; exits that
don't lead to the square next door are written into the room as notes.
The script stops if a room is added to the game without a position here.
What lies about at the start of the game is listed in ITEMS.

Needs Playwright for Python with its Chromium (pip install playwright;
playwright install chromium), and a network connection for the Google
Fonts used for the lettering.  --html also keeps the page that is rendered.
"""
import argparse
import html
import math
import os
import random
import re
import sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = {}                       # rooms, read from zkroom.room by load_rooms()
STEP_NAMES = ('north', 'south', 'east', 'west')
C = 160                      # one room = 2 x 2 big squares
SQ = 16                      # small graph square
MARGIN = 2 * C // 2          # paper around the plan
TOP = 150                    # room for the title

# Grid positions (column, row) per floor.  Worked out from the exits, with
# the twisty maze placed by hand.
FLOORS = [
  ('blue', 'Blue Level', 'Upper floor, with the way in', {
    'top_of_stairs_1': (1, 0), 'top_of_stairs_2': (4, 0), 'top_of_stairs_3': (6, 0), 'top_of_stairs_4': (9, 0),
    'cafe': (0, 1), 'blue_hall_5': (1, 1), 'blue_hall_6': (2, 1), 'blue_hall_7': (3, 1), 'end_of_blue_hall': (4, 1),
    'health_services': (5, 1), 'blue_hall_8': (6, 1), 'maze_7': (7, 1), 'maze_8': (8, 1), 'maze_9': (9, 1),
    'elevator_blue': (0, 2), 'non_descript_hall_1': (1, 2), 'non_descript_hall_2': (3, 2), 'petty_cash': (4, 2),
    'personnel': (5, 2), 'blue_hall_4': (6, 2), 'maze_4': (7, 2), 'maze_5': (8, 2), 'maze_6': (9, 2),
    'blue_hall_1': (1, 3), 'blue_hall_2': (2, 3), 'lobby': (3, 3), 'catwalk_west_1': (4, 3), 'catwalk_east_1': (5, 3),
    'blue_hall_3': (6, 3), 'maze_1': (7, 3), 'maze_2': (8, 3), 'maze_3': (9, 3),
    'rsx_dev_1': (1, 4), 'rsx_dev_2': (2, 4), 'anti_chamber': (3, 4), 'dcu': (4, 4),
    'entrance': (3, 5),
    'pad': (1, 6), 'woods': (2, 6), 'clearing': (3, 6)}),
  ('yellow', 'Yellow Level', 'Middle floor', {
    'will_office': (3, 0), 'yellow_corridor_6': (4, 0),
    'middle_of_stairs_1': (1, 1), 'ed_office': (3, 1), 'yellow_corridor_5': (4, 1), 'middle_of_stairs_2': (5, 1),
    'middle_of_stairs_3': (8, 1), 'dtr_dev': (9, 1), 'cdd_dev': (10, 1), 'middle_of_stairs_4': (11, 1),
    'end_of_yellow_corridor': (1, 2), 'yellow_corridor_8': (2, 2), 'yellow_corridor_1': (3, 2), 'yellow_corridor_2': (4, 2),
    'yellow_corridor_3': (5, 2), 'catwalk_west_2': (6, 2), 'catwalk_east_2': (7, 2), 'yellow_corridor_4': (8, 2),
    'maze_16': (9, 2), 'maze_17': (10, 2), 'maze_18': (11, 2),
    'elevator_yellow': (0, 3), 'stub_yellow': (1, 3), 'tape_library': (2, 3), 'lab_of_implementors': (3, 3),
    'yellow_corridor_7': (4, 3), 'rest_room': (5, 3), 'stall': (6, 3), 'stub': (8, 3),
    'maze_13': (9, 3), 'maze_14': (10, 3), 'maze_15': (11, 3),
    'maze_10': (9, 4), 'maze_11': (10, 4), 'maze_12': (11, 4)}),
  ('red', 'Red Level', 'Lower floor', {
    'vms_dev_3': (2, 0), 'vms_dev_4': (3, 0),
    'bottom_of_stairs_1': (1, 1), 'vms_dev_1': (2, 1), 'vms_dev_2': (3, 1), 'bottom_of_stairs_2': (4, 1),
    'end_of_red_passage_1': (1, 2), 'red_passage_1': (2, 2), 'red_passage_2': (3, 2), 'end_of_red_passage_2': (4, 2),
    'elevator_red': (0, 3), 'stub_red': (1, 3), 'vms_lab_1': (2, 3), 'vms_lab_2': (3, 3),
    'operators_room': (3, 4)}),
]

# What you find lying about at the start (signs, buttons and the like left out)
ITEMS = {
  'woods': 'Sword, lamp, sack', 'lobby': 'Guard, rug', 'anti_chamber': 'Newspapers',
  'rsx_dev_2': 'Documentation', 'ed_office': 'Listings, fluorescent ball', 'will_office': 'Neon ball',
  'operators_room': 'Notes, scratch disk', 'stall': 'Blank card', 'health_services': 'Nurse, tidbit',
  'personnel': 'Personnel rep', 'petty_cash': 'Officer, safe', 'cdd_dev': 'CDD developer',
  'vms_dev_2': 'VMS developer', 'vms_dev_3': 'Product manager', 'dtr_dev': 'Plant',
  'maze_6': 'Stan', 'maze_4': 'Coin machine', 'stub': 'Coke machine', 'cafe': 'Table',
  'vms_lab_2': 'VAX, tape & disk drives', 'tape_library': 'Strange light', 'rest_room': 'Mirror',
  'entrance': 'Barred wall', 'non_descript_hall_1': 'Lift lock', 'yellow_corridor_5': 'Coin machine',
}
OUTSIDE = set()
SHORT = {'Bottom of Stairwell': 'Bottom of Stairs', 'Middle of Stairwell': 'Middle of Stairs',
         'Top of Stairwell': 'Top of Stairs', 'Maze of Twisty Cubicles': 'Twisty Cubicles',
         'Unisex Rest Room': 'Rest Room'}

STEP = {'north': (0, -1), 'south': (0, 1), 'east': (1, 0), 'west': (-1, 0),
        'north_east': (1, -1), 'north_west': (-1, -1), 'south_east': (1, 1), 'south_west': (-1, 1)}
ABBR = {'north': 'N', 'south': 'S', 'east': 'E', 'west': 'W', 'north_east': 'NE', 'north_west': 'NW',
        'south_east': 'SE', 'south_west': 'SW', 'up': 'Up', 'down': 'Down', 'in': 'In', 'out': 'Out'}

# Number the rooms in reading order, floor by floor, as the book does
NUM = {}
for _, _, _, pos in FLOORS:
    for r in sorted(pos, key=lambda r: (pos[r][1], pos[r][0])):
        NUM[r] = len(NUM) + 1

DIRS = ('north south east west north_east north_west south_east south_west '
        'up down in out').split()


def load_rooms(path):
    """Each room's name, classes, exits and doors from an IFC room file."""
    rooms, cur, last = {}, None, None
    for line in open(path):
        line = line.split('--')[0].rstrip()
        t = line.split()
        if not t:
            continue
        if t[0] == 'room':
            cur = rooms[t[1]] = {'name': '', 'class': [], 'exits': {}, 'doors': {}}
        elif cur is None or t[0] in ('description', 'end'):
            continue
        elif t[0] == 'name':
            cur['name'] = re.search(r'<(.*)>', line).group(1)
        elif t[0] == 'class':
            cur['class'] = [int(x) for x in t[1:]]
        else:
            # "north lobby in lobby door zk$obj_glass_door", the door
            # sometimes on a line of its own
            i = 0
            while i + 1 < len(t):
                if t[i] in DIRS:
                    cur['exits'][t[i]] = t[i + 1]; last = t[i]
                elif t[i] == 'door':
                    cur['doors'][last] = t[i + 1]
                else:
                    sys.exit('%s: cannot read "%s"' % (path, line.strip()))
                i += 2
    # Doors are given against IN or OUT; the map draws them on the compass exit
    for v in rooms.values():
        for d, door in list(v['doors'].items()):
            for d2, t in v['exits'].items():
                if t == v['exits'][d] and d2 in STEP_NAMES:
                    v['doors'][d2] = door
    return rooms

rnd = random.Random(1985)

def wobble(x1, y1, x2, y2, amp=1.2, seg=40):
    """A pen line: slightly wavy, overshooting the ends a little."""
    dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L; a, b = rnd.uniform(1, 3), rnd.uniform(1, 3)
    x1, y1, x2, y2 = x1 - ux * a, y1 - uy * a, x2 + ux * b, y2 + uy * b
    dx, dy = x2 - x1, y2 - y1
    n = max(2, int(L / seg)); pts = []
    for i in range(n + 1):
        t = i / n; j = 0 if i in (0, n) else rnd.uniform(-amp, amp)
        pts.append('%.1f,%.1f' % (x1 + dx * t - uy * j, y1 + dy * t + ux * j))
    return 'M' + ' L'.join(pts)

def esc(s): return html.escape(s)

def wrap(s, n):
    words, lines, cur = s.split(), [], ''
    for w in words:
        if cur and len(cur) + 1 + len(w) > n: lines.append(cur); cur = w
        else: cur = (cur + ' ' + w).strip()
    return lines + [cur]

def tri(x, y, d, s=7):
    """A small filled arrowhead at x,y pointing d (N/S/E/W or diagonal unit step)."""
    ang = math.atan2(d[1], d[0]); pts = []
    for a, r in ((0, s), (2.5, s * .8), (-2.5, s * .8)):
        pts.append('%.1f,%.1f' % (x + r * math.cos(ang + a), y + r * math.sin(ang + a)))
    return '<polygon class="ink" points="%s"/>' % ' '.join(pts)

def floor_svg(key, title, sub, pos):
    cols = max(p[0] for p in pos.values()) + 1; rows = max(p[1] for p in pos.values()) + 1
    W = cols * C + 2 * MARGIN; H = rows * C + MARGIN + TOP + 70
    ox, oy = MARGIN, TOP
    at = {p: r for r, p in pos.items()}
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" class="plan">' % (W, H)]
    # graph paper
    out.append('<rect width="%d" height="%d" class="paper"/>' % (W, H))
    for i in range(0, W + 1, SQ):
        out.append('<line x1="%d" y1="0" x2="%d" y2="%d" class="%s"/>' % (i, i, H, 'major' if (i - ox) % (5 * SQ) == 0 else 'minor'))
    for i in range(0, H + 1, SQ):
        out.append('<line x1="0" y1="%d" x2="%d" y2="%d" class="%s"/>' % (i, W, i, 'major' if (i - oy) % (5 * SQ) == 0 else 'minor'))
    # title, hand-lettered
    out.append('<text x="%d" y="%d" class="title">THE HALLS OF ZK: %s</text>' % (ox, 72, esc(title.upper())))
    out.append('<text x="%d" y="%d" class="subtitle">%s</text>' % (ox, 108, esc(sub)))
    def cell(r): x, y = pos[r]; return ox + x * C, oy + y * C
    # rooms: pencil boxes, number tabs, names, items
    for r in pos:
        x, y = cell(r)
        if r in OUTSIDE:
            out.append('<rect x="%d" y="%d" width="%d" height="%d" class="grass"/>' % (x, y, C, C))
        for a, b, c, d in ((x, y, x + C, y), (x, y + C, x + C, y + C), (x, y, x, y + C), (x + C, y, x + C, y + C)):
            out.append('<path d="%s" class="pencil"/>' % wobble(a, b, c, d, .6))
        out.append('<path d="M%d,%d l34,0 l-34,34 z" class="tab"/>' % (x + 2, y + 2))
        out.append('<text x="%d" y="%d" class="num">%d</text>' % (x + 6, y + 19, NUM[r]))
        if 'stairs' in r:   # a few treads, as the book draws its staircase
            for i in range(4):
                yy = y + 14 + i * 8
                out.append('<path d="%s" class="treads"/>' % wobble(x + 112 + i * 7, yy, x + 146, yy, .3))
    # solid ground: an empty square with rooms all round gets pencil hatching
    for gx in range(cols):
        for gy in range(rows):
            if (gx, gy) in at: continue
            if sum((gx + dx, gy + dy) in at for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0))) == 4:
                x, y = ox + gx * C, oy + gy * C
                for i in range(1, 12):
                    k = i * C / 6
                    out.append('<path d="%s" class="treads"/>' % wobble(x + max(0, k - C), y + min(C, k), x + min(C, k), y + max(0, k - C), .4))
    # walls and exits on each shared or outer edge
    for r in pos:
        x, y = cell(r); px, py = pos[r]
        for d, (dx, dy) in (('north', (0, -1)), ('south', (0, 1)), ('east', (1, 0)), ('west', (-1, 0))):
            n = at.get((px + dx, py + dy))
            here = R[r]['exits'].get(d) == n and n is not None
            back = n is not None and R[n]['exits'].get({'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}[d]) == r
            if d == 'north': seg = (x, y, x + C, y)
            elif d == 'south': seg = (x, y + C, x + C, y + C)
            elif d == 'east': seg = (x + C, y, x + C, y + C)
            else: seg = (x, y, x, y + C)
            if not (here or back) and not (r in OUTSIDE and (n is None or n in OUTSIDE)):
                if d in ('north', 'west') or n is None:   # draw each shared wall once
                    out.append('<path d="%s" class="wall"/>' % wobble(*seg, amp=1.5))
            if here:
                m = C // 2
                if d == 'east':
                    out.append('<text x="%d" y="%d" class="dir" text-anchor="end">E</text>' % (x + C - 20, y + C - 34) + tri(x + C - 11, y + C - 40, (1, 0)))
                elif d == 'west':
                    out.append(tri(x + 11, y + C - 40, (-1, 0)) + '<text x="%d" y="%d" class="dir">W</text>' % (x + 20, y + C - 34))
                elif d == 'north':
                    out.append(tri(x + m, y + 11, (0, -1)) + '<text x="%d" y="%d" class="dir" text-anchor="middle">N</text>' % (x + m, y + 34))
                else:
                    out.append('<text x="%d" y="%d" class="dir" text-anchor="middle">S</text>' % (x + m, y + C - 22) + tri(x + m, y + C - 11, (0, 1)))
                if d in R[r]['doors'] and d in ('north', 'west', 'south', 'east'):
                    if d in ('north', 'south'):
                        yy = y if d == 'north' else y + C
                        out.append('<rect x="%d" y="%d" width="40" height="9" class="door"/>' % (x + m + 16, yy - 4))
                    else:
                        xx = x + C if d == 'east' else x
                        out.append('<rect x="%d" y="%d" width="9" height="40" class="door"/>' % (xx - 4, y + 34))
        # diagonal neighbours get a corner arrow
        for d in ('north_east', 'north_west', 'south_east', 'south_west'):
            t = R[r]['exits'].get(d); s = STEP[d]
            if t is not None and t != r and pos.get(t) == (px + s[0], py + s[1]):
                # arrowhead in the corner, label tucked beside it (NW clears the number tab)
                cx = x + (C - 10 if s[0] > 0 else 10); cy = y + (C - 10 if s[1] > 0 else 10)
                if d == 'north_west': cx = x + 44
                lx = cx - 12 if s[0] > 0 else cx + 10
                ly = cy + 5 if s[1] < 0 else cy + 2
                out.append(tri(cx, cy, s, 7))
                out.append('<text x="%d" y="%d" class="dir small" text-anchor="%s">%s</text>' % (lx, ly, 'end' if s[0] > 0 else 'start', ABBR[d]))
    # names, items and notes for exits that don't go to the square next door
    for r in pos:
        x, y = cell(r); px, py = pos[r]
        notes = {}
        for d, t in R[r]['exits'].items():
            if d in STEP and t != r and pos.get(t) == (px + STEP[d][0], py + STEP[d][1]): continue
            if d in ('in', 'out') and any(t == t2 for d2, t2 in R[r]['exits'].items() if d2 not in ('in', 'out')): continue
            notes.setdefault('here' if t == r else str(NUM[t]), []).append(ABBR[d])
        lines = ['%s ▸ %s' % (','.join(ds), t) for t, ds in notes.items()]
        if r.startswith('elevator_'):
            mine = r.split('_')[1]
            lines = ['%s button ▸ %d' % (c.title(), NUM['elevator_' + c]) for c in ('blue', 'yellow', 'red') if c != mine]
            lines.append('Orange? Don’t!')
        name = SHORT.get(R[r]['name'], R[r]['name'])
        nl = wrap(name.upper(), 11)
        item = ITEMS.get(r)
        il = wrap(item, 17) if item else []
        # centred in the band between the N and S arrows
        block = len(nl) * 19 + len(il) * 16 + len(lines) * 14
        ty = y + 40 + (82 - block) / 2 + 14
        for s in nl:
            out.append('<text x="%d" y="%d" class="name" text-anchor="middle">%s</text>' % (x + C / 2, ty, esc(s))); ty += 19
        for s in il:
            out.append('<text x="%d" y="%d" class="item" text-anchor="middle">%s</text>' % (x + C / 2, ty, esc(s))); ty += 16
        for s in lines:
            out.append('<text x="%d" y="%d" class="note" text-anchor="middle">%s</text>' % (x + C / 2, ty, esc(s))); ty += 14
    # key, bottom left
    ky = oy + rows * C + 52
    out.append('<path d="%s" class="wall"/>' % wobble(ox, ky - 6, ox + 40, ky - 6, 1))
    out.append('<text x="%d" y="%d" class="key">Wall</text>' % (ox + 50, ky))
    out.append(tri(ox + 130, ky - 6, (1, 0)) + '<text x="%d" y="%d" class="key">Exit</text>' % (ox + 145, ky))
    out.append('<rect x="%d" y="%d" width="40" height="9" class="door"/><text x="%d" y="%d" class="key">Door</text>' % (ox + 215, ky - 10, ox + 265, ky))
    out.append('<text x="%d" y="%d" class="key"><tspan class="note">SE ▸ 14</tspan>  Goes to room 14</text>' % (ox + 335, ky))
    out.append('<text x="%d" y="%d" class="key"><tspan class="item">Sword</tspan>  Found here</text>' % (ox + 560, ky))
    out.append('</svg>')
    return '\n'.join(out), W, H

STYLE = """
@import url('https://fonts.googleapis.com/css2?family=Architects+Daughter&family=Patrick+Hand&display=block');
body { margin: 0; background: #ddd; }
svg.plan { display: block; width: 100%; height: auto; }
.paper { fill: #fbfaf3; }
.minor { stroke: #b9d3e6; stroke-width: .6; }
.major { stroke: #8fb6d6; stroke-width: 1.1; }
.grass { fill: #a6d18a; opacity: .35; }
.pencil { fill: none; stroke: #5a6e8c; stroke-width: 1.4; opacity: .8; stroke-linecap: round; }
.wall { fill: none; stroke: #d6262b; stroke-width: 7; stroke-linecap: round; stroke-linejoin: round; opacity: .9; }
.tab { fill: #ffe14d; opacity: .9; }
.treads { fill: none; stroke: #5a6e8c; stroke-width: 1.4; }
.door { fill: #a8692e; stroke: #5b3613; stroke-width: 1.2; }
.ink { fill: #1d2433; }
text { font-family: 'Architects Daughter', cursive; fill: #1d2433; }
.num { font-size: 16px; font-weight: bold; }
.name { font-size: 17px; letter-spacing: .5px; }
.item { font-family: 'Patrick Hand', cursive; font-size: 16px; fill: #0b7a3b; }
.note { font-family: 'Patrick Hand', cursive; font-size: 15px; fill: #a01e5a; }
.dir { font-size: 16px; font-weight: bold; }
.dir.small { font-size: 12px; }
.title { font-size: 46px; }
.subtitle { font-family: 'Patrick Hand', cursive; font-size: 24px; fill: #4a5568; }
.key { font-family: 'Patrick Hand', cursive; font-size: 19px; }
"""

def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1].strip())
    ap.add_argument('zk', help='checkout of the zk repository')
    ap.add_argument('--img', default='assets/img', help='where the images go')
    ap.add_argument('--scale', type=float, default=2, help='pixels per drawing unit')
    ap.add_argument('--html', help='also keep the rendered page here')
    args = ap.parse_args()

    R.update(load_rooms(os.path.join(args.zk, 'zk', 'zkroom.room')))
    OUTSIDE.update(r for r, v in R.items() if 2 in v['class'])
    missing = set(R) - set(NUM)
    if missing:
        sys.exit('No place on the map for: ' + ', '.join(sorted(missing)))

    parts = []
    for key, title, sub, pos in FLOORS:
        svg, W, H = floor_svg(key, title, sub, pos)
        parts.append('<div id="%s" style="width:%dpx">%s</div>' % (key, W, svg))
    page = ('<!doctype html><meta charset="utf-8"><style>%s</style>%s'
            % (STYLE, '\n'.join(parts)))
    out = os.path.join(SITE, args.html or 'map.tmp.html')
    with open(out, 'w') as f:
        f.write(page)

    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            pg = browser.new_page(device_scale_factor=args.scale)
            pg.goto('file://' + out, wait_until='networkidle')
            pg.evaluate('document.fonts.ready')
            for key, _, _, _ in FLOORS:
                img = os.path.join(SITE, args.img, 'map_%s.png' % key)
                pg.locator('#%s svg' % key).screenshot(path=img)
                print(os.path.relpath(img, SITE))
            browser.close()
    finally:
        if not args.html:
            os.remove(out)


if __name__ == '__main__':
    main()
