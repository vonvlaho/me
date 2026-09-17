"""Check the built site's local links, fragment targets and page metadata."""

import json
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urljoin, urlsplit


ROOT = Path(__file__).resolve().parents[1] / "_site"
ORIGIN = "https://vlahovits.com"


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.ids = set()
        self.links = []
        self.errors = []
        self.h1_count = 0
        self.description = False
        self.canonical = None
        self.stylesheets = []
        self.label_ids = set()
        self.json_text = None
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                self.errors.append(f"Duplicate id: {attrs['id']}")
            self.ids.add(attrs["id"])
        if tag == "h1":
            self.h1_count += 1
        if tag == "meta" and attrs.get("name") == "description":
            self.description = bool(attrs.get("content"))
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.stylesheets.append(attrs.get("href", ""))
        self.label_ids.update(attrs.get("aria-labelledby", "").split())
        for attr in ("href", "src"):
            if attrs.get(attr):
                self.links.append(attrs[attr])
        if tag == "meta" and attrs.get("property") == "og:image":
            self.links.append(attrs["content"])
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.json_text = ""

    def handle_data(self, data):
        if self.json_text is not None:
            self.json_text += data

    def handle_endtag(self, tag):
        if tag == "script" and self.json_text is not None:
            try:
                json.loads(self.json_text)
            except json.JSONDecodeError as exc:
                self.errors.append(f"Invalid JSON-LD: {exc}")
            self.json_text = None


def main():
    pages = {p.resolve(): Page(p) for p in ROOT.rglob("*.html")}
    if not pages:
        raise SystemExit("No HTML found. Run bundle exec jekyll build first.")
    for path, page in pages.items():
        relative = path.relative_to(ROOT)
        if page.h1_count != 1 or not page.description or not page.canonical:
            page.errors.append("Expected one h1, a description and a canonical URL")
        for missing in page.label_ids - page.ids:
            page.errors.append(f"Missing accessible label: {missing}")
        if not page.stylesheets or any(not parse_qs(urlsplit(url).query).get("v") for url in page.stylesheets):
            page.errors.append("Expected a versioned stylesheet URL")
        for link in page.links:
            target = urlsplit(urljoin(f"{ORIGIN}/{relative}", link))
            if target.scheme not in ("http", "https") or target.netloc != urlsplit(ORIGIN).netloc:
                continue
            local = (ROOT / unquote(target.path).lstrip("/")).resolve()
            if local.is_dir():
                local /= "index.html"
            if not local.exists():
                page.errors.append(f"Missing local target: {link}")
            elif target.fragment and local in pages and unquote(target.fragment) not in pages[local].ids:
                page.errors.append(f"Missing fragment: {link}")
        for error in page.errors:
            print(f"{relative}: {error}")
    sitemap_errors = []
    try:
        sitemap = ET.parse(ROOT / "sitemap.xml")
        urls = [node.text for node in sitemap.findall("{*}url/{*}loc")]
        expected = {page.canonical for page in pages.values()}
        if len(urls) != len(set(urls)) or set(urls) != expected:
            sitemap_errors.append("Sitemap must list every page's canonical URL exactly once")
    except (OSError, ET.ParseError) as exc:
        sitemap_errors.append(f"Invalid sitemap: {exc}")
    for error in sitemap_errors:
        print(error)
    if sitemap_errors or any(p.errors for p in pages.values()):
        raise SystemExit(1)
    print(f"Checked {len(pages)} pages: local links, labels, headings, metadata, JSON-LD, stylesheet versions and sitemap.")


if __name__ == "__main__":
    main()
