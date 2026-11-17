# Changes

## 2026-11-17

- Track Bootstrap's `vendor/_rfs.scss` partial, which `.gitignore` had been
  skipping, so the site builds from a fresh checkout.
- Add an MIT license and this changelog.
- Add a favicon and home screen icons: "z" and "k" in boxes after
  Digital's logo, in Digital blue, drawn by `tools/make_icons.py`.
- Rename `bootstrap.bundle.min.js` and two PDFs so every file name fits
  OpenVMS's ODS-2 file system: one dot, no spaces, 39 characters at most.
- Replace the navbar's play icon with the zk logo.
- Add a Photos page under History: the 95 photographs from The Halls of ZK
  album on Flickr, fetched by `tools/fetch_photos.py`, on backgrounds of the
  ZKO Holodeck and the cafeteria.  The walkthrough's picture viewer is now
  shared by both pages.

## 2026-11-13

- Add a site footer with the copyright and a link to Endless Software
  Solutions.

## 2026-11-12

- Add hand-drawn floor maps of the Blue, Yellow and Red levels to the Map
  page, drawn by `tools/draw_map.py` from the game's room definitions, over
  a photo of the cubicles.
- Make the home page's intro and second section fill the screen on phones.
- Add a Digital Security patch to slide 4 of the walkthrough.
- Add blurbs and a much longer list of links to the History page: the game's
  source, Spit Brook Road, Stanley Rabinowitz, the Computer History Museum
  and news stories.
- Make all buttons the site's green.
- Remove the old Graphviz map.
- Add the Commands page and the walkthrough slide deck, with
  `tools/export_slides.py` to export it to images and a PDF.
- Rework the Play, Walkthrough, Barcode and History pages.
- Move images to `assets/img/` and the reference PDFs to `assets/pdf/`,
  stored with Git LFS.
- Remove the Other Offices page and unused images.

## 2026-10-25

- Stretch the home page's second section to the full screen width.

## 2026-10-24

- Split the website into its own repository, apart from the game source in
  [tesneddon/zk](https://github.com/tesneddon/zk).
- Replace the Grunt, Bower and LESS build with Jekyll 4.4 and Sass.
- Upgrade to Bootstrap 5.3.8 and Font Awesome 7, and drop jQuery.  The
  design is unchanged.
- Serve locally on port 8080.

## 2014-06

- First version of the site: the introduction page, how to play the game,
  the beginnings of the walkthrough and a shell for the Other Offices page.
- Host on GitHub Pages at hallsofzk.org.
