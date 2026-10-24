# hallsofzk.org

Source for the [Halls of ZK](https://hallsofzk.org) website. The game itself
lives in [tesneddon/zk](https://github.com/tesneddon/zk).

## Building

Requires Ruby (see `.ruby-version`) and Bundler.

    bundle install
    bundle exec jekyll serve                         # http://localhost:8080
    JEKYLL_ENV=production bundle exec jekyll build   # static site in _site/

## Layout

| Path            | Contents                                                |
|-----------------|---------------------------------------------------------|
| `*.html`        | Pages                                                   |
| `_layouts/`, `_includes/` | Page templates                                |
| `_data/`        | Data files (e.g. walkthrough slides)                    |
| `_sass/`        | Site styles (`_settings.scss`, `_custom.scss`) and vendored Bootstrap / Font Awesome sources |
| `css/styles.scss` | Stylesheet entry point, compiled by Jekyll            |
| `js/`, `fonts/` | Vendored libraries and site scripts                     |
| `img/`          | Images                                                  |

## Vendored libraries

| Library      | Version | Location |
|--------------|---------|----------|
| Bootstrap    | 5.3.8   | `_sass/bootstrap/`, `js/bootstrap.bundle.min.js` |
| Font Awesome Free | 7.3.1 | `_sass/font-awesome/`, `fonts/fa-solid-900.woff2` |
| Glyphicons Halflings (from Bootstrap 3.4.1) | — | `fonts/glyphicons-halflings-regular.*`, carousel arrows only |

`_sass/_settings.scss` sets Bootstrap 5's variables to Bootstrap 3's metrics
and `_sass/_custom.scss` restores the Bootstrap 3 styles the design depends
on, so the site looks as it did under Bootstrap 3.
