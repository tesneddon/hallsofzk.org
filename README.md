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

| Library      | Version |
|--------------|---------|
| Bootstrap (Sass port) | 3.4.1 |
| Font Awesome | 4.7.0   |
| jQuery       | 3.7.1   |
| jQuery UI    | 1.13.3  |
| jQuery Easing | 1.4.1  |
