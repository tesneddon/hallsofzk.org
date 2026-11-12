#!/usr/bin/env python3
"""Export a .pptx slide deck for the website's walkthrough page.

    tools/export_slides.py assets/slides/zk_walkthrough.odp

The deck can be .odp or .pptx.  Writes, relative to the site root:

    assets/pdf/zk_wizardry.pdf     the whole deck, rendered by LibreOffice
    assets/img/zk_walkthrough_NN.jpg
                                   one 1280x720 image per slide
    _data/zk_wizardry.yml          the carousel's list of images, with each
                                   slide's title as its alt text

Needs LibreOffice (brew install --cask libreoffice) and pdftoppm
(brew install poppler).  Fonts are whatever LibreOffice finds installed:
install the deck's fonts into ~/Library/Fonts first for a faithful render.
"""
import argparse
import glob
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOFFICE = ('soffice', '/Applications/LibreOffice.app/Contents/MacOS/soffice')


def find_tool(names):
    for name in names:
        path = shutil.which(name) or (name if os.access(name, os.X_OK) else None)
        if path:
            return path
    return None


def slide_titles(deck):
    """Each slide's title, in presentation order, from the title placeholder."""
    if deck.lower().endswith('.odp'):
        return odp_titles(deck)
    with zipfile.ZipFile(deck) as z:
        pres = z.read('ppt/presentation.xml').decode('utf-8')
        rels = z.read('ppt/_rels/presentation.xml.rels').decode('utf-8')
        targets = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', rels))
        targets.update({k: v for v, k in
                        re.findall(r'Target="([^"]+)"[^>]*Id="([^"]+)"', rels)})
        titles = []
        for rid in re.findall(r'<p:sldId [^>]*r:id="([^"]+)"', pres):
            xml = z.read('ppt/' + targets[rid].lstrip('/').replace('ppt/', '')).decode('utf-8')
            title = ''
            for sp in re.findall(r'<p:sp>.*?</p:sp>', xml, re.S):
                if re.search(r'<p:ph [^>]*type="(ctrTitle|title)"', sp):
                    title = ''.join(re.findall(r'<a:t>([^<]*)</a:t>', sp))
                    break
            titles.append(html.unescape(title).strip())
    return titles


def odp_titles(deck):
    """The same for an OpenDocument deck: each page's title frame."""
    with zipfile.ZipFile(deck) as z:
        xml = z.read('content.xml').decode('utf-8')
    titles = []
    for page in re.findall(r'<draw:page .*?</draw:page>', xml, re.S):
        # Speaker notes have their own frames; only look at the slide itself
        page = page.split('<presentation:notes', 1)[0]
        m = re.search(r'<draw:frame [^>]*presentation:class="title".*?</draw:frame>',
                      page, re.S)
        text = ''
        if m:
            frame = re.sub(r'</text:p>', ' ', m.group(0))
            frame = re.sub(r'<text:s[^>]*/>', ' ', frame)
            text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', frame))
        titles.append(html.unescape(text).strip())
    return titles


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('deck', help='the .odp or .pptx to export')
    parser.add_argument('--prefix', default='zk_walkthrough',
                        help='image file name prefix (default: zk_walkthrough)')
    parser.add_argument('--img', default='assets/img',
                        help='image directory in the site (default: assets/img)')
    parser.add_argument('--pdf', default='assets/pdf/zk_wizardry.pdf',
                        help='PDF path in the site (default: assets/pdf/zk_wizardry.pdf)')
    parser.add_argument('--data', default='_data/zk_wizardry.yml',
                        help='carousel data file (default: _data/zk_wizardry.yml)')
    args = parser.parse_args()

    soffice = find_tool(SOFFICE)
    pdftoppm = find_tool(('pdftoppm',))
    if not soffice or not pdftoppm:
        sys.exit('needs LibreOffice and pdftoppm: '
                 'brew install --cask libreoffice; brew install poppler')

    deck = os.path.abspath(args.deck)
    titles = slide_titles(deck)

    with tempfile.TemporaryDirectory() as work:
        # A private LibreOffice profile, so a running LibreOffice doesn't interfere
        profile = 'file://' + os.path.join(work, 'profile')
        subprocess.run([soffice, '-env:UserInstallation=' + profile, '--headless',
                        '--convert-to', 'pdf', '--outdir', work, deck],
                       check=True, stdout=subprocess.DEVNULL)
        pdf = os.path.join(work, os.path.splitext(os.path.basename(deck))[0] + '.pdf')

        subprocess.run([pdftoppm, '-jpeg', '-jpegopt', 'quality=85',
                        '-scale-to-x', '1280', '-scale-to-y', '720',
                        pdf, os.path.join(work, 'slide')], check=True)
        pages = sorted(glob.glob(os.path.join(work, 'slide-*.jpg')),
                       key=lambda p: int(re.search(r'-(\d+)\.jpg$', p).group(1)))
        if len(pages) != len(titles):
            sys.exit('%d pages rendered but the deck has %d slides'
                     % (len(pages), len(titles)))

        # Clear out images from a previous, longer export
        img = os.path.join(SITE, args.img)
        os.makedirs(img, exist_ok=True)
        for old in glob.glob(os.path.join(img, args.prefix + '_*.jpg')):
            os.remove(old)

        entries = []
        for n, (page, title) in enumerate(zip(pages, titles), 1):
            name = '%s_%02d.jpg' % (args.prefix, n)
            shutil.move(page, os.path.join(img, name))
            entries.append('- name: %s\n  alt: "%s"\n'
                           % (name, title.replace('\\', '\\\\').replace('"', '\\"')))

        os.makedirs(os.path.dirname(os.path.join(SITE, args.pdf)), exist_ok=True)
        shutil.move(pdf, os.path.join(SITE, args.pdf))

    with open(os.path.join(SITE, args.data), 'w') as f:
        f.write(''.join(entries))

    print('%d slides: %s/%s_01.jpg..%02d, %s, %s'
          % (len(titles), args.img, args.prefix, len(titles), args.pdf, args.data))


if __name__ == '__main__':
    main()
