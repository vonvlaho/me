# vlahovits.com

The personal site of Frederic von Vlahovits, at [vlahovits.com](https://vlahovits.com). Three pages: a brief introduction, `/work` for product management and ventures, and `/research` for the research programme and detailed academic record.

Jekyll with kramdown, one layout, one stylesheet, no theme and no plugins. Pages are `.md` files containing semantic HTML where needed. Run `bundle install` once, then `bundle exec jekyll serve` for local development. The pages use system fonts and local assets: no CDN, analytics, cookies or JavaScript.

The design uses one system sans-serif typeface, a grayscale palette and spacing for hierarchy. Work and Research have a narrow column for labels and dates; on mobile everything becomes a single column. Section indexes use native disclosures. Deployment runs through GitHub Actions using the repo's Gemfile, so the Pages source must stay set to "GitHub Actions".

Before opening a PR, run `bundle exec jekyll build --trace` and `python3 scripts/check_site.py`. The checks cover local links, accessible labels, metadata, stylesheet versioning and sitemap coverage. They run on pull requests and before deployment. Publishing remains tied to pushes to `master`.

The text-only social card is generated with `python3 scripts/generate_social_card.py` on macOS (requires Pillow). Its PNG is committed; no image-generation dependency is needed to build the site.
