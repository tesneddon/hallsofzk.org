#!/usr/bin/env python3
"""Fetch the photos for the website's Photos page from Flickr.

    tools/fetch_photos.py

Reads the "The Halls of ZK" album on Flickr and writes, relative to the
site root:

    _data/photos.json                   title, caption and size of each photo
    assets/img/photos/<id>.jpg          1024 px, for the viewer
    assets/img/photos/small/<id>.jpg    400 px, for the grid
    assets/img/holodeck.jpg             the page backgrounds
    assets/img/cafeteria.jpg

Photos already downloaded are kept, so running it again only fetches what
has been added to the album.  Titles that are just the camera's file name
(IMG_4850) are left blank, and descriptions, which carry the photographers'
credits, become the captions.

Flickr only puts the first 25 photos in the album page and loads the rest
as the page is scrolled, so the album is opened in a headless browser and
scrolled to the end.  Needs Playwright for Python with its Chromium
(pip install playwright; playwright install chromium).
"""
import html
import json
import os
import re
import urllib.request

from playwright.sync_api import sync_playwright

ALBUM = 'https://www.flickr.com/photos/tesneddon/albums/72157634383159373'
PHOTO = 'https://www.flickr.com/photos/tesneddon/%s/'
BACKGROUNDS = {'9163061395': 'holodeck.jpg',      # The ZKO Holodeck
               '9163063193': 'cafeteria.jpg'}     # Cafeteria
AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
         '(KHTML, like Gecko) Chrome/130 Safari/537.36')


def model_export(page_html):
    """Return the JSON model Flickr embeds in its pages."""
    start = page_html.index('{', page_html.index('modelExport:'))
    return json.JSONDecoder().raw_decode(page_html[start:])[0]


def from_model(photo):
    """Turn a photo from the album page's model into an API-style record."""
    sizes = photo['sizes']['data']
    record = {'id': photo['id'], 'title': photo['title'], 'description': None,
              'datetaken': photo['stats']['data']['dateTaken']}
    for key, size in (('l', 'l'), ('w', 'w'), ('k', 'k')):
        if size in sizes:
            data = sizes[size]['data']
            record['url_' + key] = 'https:' + data['url']
            record['width_' + key] = data['width']
            record['height_' + key] = data['height']
    return record


def read_album():
    """Return every photo in the album, in album order."""
    found = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(user_agent=AGENT, viewport={'width': 1280, 'height': 900})

        def response(r):
            if 'method=flickr.photosets.getPhotos' not in r.url:
                return
            text = r.text()
            data = json.loads(text[text.index('{'):text.rindex('}') + 1])['photoset']
            first = (int(data['page']) - 1) * int(data['perpage'])
            for n, photo in enumerate(data['photo']):
                photo['description'] = photo['description']['_content']
                found[first + n] = photo
            found['total'] = int(data['total'])

        page.on('response', response)
        page.goto(ALBUM, wait_until='domcontentloaded')
        album = model_export(page.content())['main']['set-models'][0]['data']
        total = int(album['photoCount'])
        for n, photo in enumerate(album['photoPageList']['data']['_data']):
            if photo and n not in found:
                found[n] = from_model(photo['data'])
        for _ in range(60):
            if all(n in found for n in range(total)):
                break
            page.mouse.wheel(0, 4000)
            page.wait_for_timeout(1000)
        browser.close()
    missing = [n for n in range(total) if n not in found]
    if missing:
        raise SystemExit('Flickr did not load photos %s of the album' % missing)
    return [found[n] for n in range(total)]


def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': AGENT})
    with urllib.request.urlopen(request) as f:
        return f.read()


def description(photo_id):
    """Read a photo's description from its own page."""
    page = fetch(PHOTO % photo_id).decode('utf-8')
    m = re.search(r'<meta name="description" content="([^"]*)"', page)
    return html.unescape(m.group(1)) if m else ''


def caption(text):
    """Keep a description's links, drop any other markup, and break lines."""
    links = []

    def keep(m):
        links.append('<a href="%s" target="_blank">' % html.escape(m.group(1)))
        return '\0%d\0' % (len(links) - 1)

    text = re.sub(r'<a [^>]*href="([^"]+)"[^>]*>', keep, text.strip())
    text = re.sub(r'</a>', '\0end\0', text)
    text = html.escape(re.sub(r'<[^>]+>', '', html.unescape(text)), quote=False)
    text = re.sub(r'\0(\d+)\0', lambda m: links[int(m.group(1))], text)
    text = text.replace('\0end\0', '</a>')
    return re.sub(r'\n\s*\n', '<br><br>', text).replace('\n', '<br>')


def save(url, path):
    if not os.path.exists(path):
        with open(path, 'wb') as f:
            f.write(fetch(url))


def main():
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    large = os.path.join(root, 'assets', 'img', 'photos')
    small = os.path.join(large, 'small')
    os.makedirs(small, exist_ok=True)
    photos = []
    for photo in read_album():
        if photo['description'] is None:
            photo['description'] = description(photo['id'])
        save(photo['url_l'], os.path.join(large, photo['id'] + '.jpg'))
        save(photo['url_w'], os.path.join(small, photo['id'] + '.jpg'))
        if photo['id'] in BACKGROUNDS:
            save(photo['url_k'], os.path.join(root, 'assets', 'img', BACKGROUNDS[photo['id']]))
        title = photo['title'].strip()
        photos.append({
            'id': photo['id'],
            'title': '' if re.fullmatch(r'(IMG|DSC|DSCN|P\d{3})_?\d+', title) else title,
            'caption': caption(photo['description']),
            'taken': photo['datetaken'][:10],
            'width': int(photo['width_l']),
            'height': int(photo['height_l']),
            'flickr': PHOTO % photo['id'],
        })
        print(photo['id'], title)
    with open(os.path.join(root, '_data', 'photos.json'), 'w') as f:
        json.dump(photos, f, indent=1, ensure_ascii=False)
        f.write('\n')
    print('%d photos' % len(photos))


if __name__ == '__main__':
    main()
