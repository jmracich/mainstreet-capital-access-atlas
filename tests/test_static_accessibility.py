from html.parser import HTMLParser
from pathlib import Path

import pytest


class StructureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[str] = []
        self.ids: set[str] = set()
        self.h1_count = 0
        self.title_text = ""
        self._in_title = False
        self.meta_description = False
        self.og_title = False
        self.og_description = False
        self.og_site_name = False
        self.og_image: str | None = None
        self.og_image_alt = False
        self.twitter_card = False
        self.twitter_title = False
        self.twitter_description = False
        self.twitter_image: str | None = None
        self.nav_primary = False
        self.skip_link_target: str | None = None
        self.nav_toggle_controls: str | None = None
        self.nav_toggle_expanded: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        self.tags.append(tag)
        if "id" in attributes and attributes["id"]:
            self.ids.add(attributes["id"])
        if tag == "h1":
            self.h1_count += 1
        if tag == "title":
            self._in_title = True
        if tag == "meta" and attributes.get("name") == "description" and attributes.get("content"):
            self.meta_description = True
        if tag == "meta" and attributes.get("property") == "og:title" and attributes.get("content"):
            self.og_title = True
        if tag == "meta" and attributes.get("property") == "og:description" and attributes.get("content"):
            self.og_description = True
        if tag == "meta" and attributes.get("property") == "og:site_name" and attributes.get("content"):
            self.og_site_name = True
        if tag == "meta" and attributes.get("property") == "og:image" and attributes.get("content"):
            self.og_image = attributes["content"]
        if tag == "meta" and attributes.get("property") == "og:image:alt" and attributes.get("content"):
            self.og_image_alt = True
        if tag == "meta" and attributes.get("name") == "twitter:card":
            self.twitter_card = attributes.get("content") == "summary_large_image"
        if tag == "meta" and attributes.get("name") == "twitter:title" and attributes.get("content"):
            self.twitter_title = True
        if tag == "meta" and attributes.get("name") == "twitter:description" and attributes.get("content"):
            self.twitter_description = True
        if tag == "meta" and attributes.get("name") == "twitter:image" and attributes.get("content"):
            self.twitter_image = attributes["content"]
        if tag == "nav" and attributes.get("aria-label") == "Primary":
            self.nav_primary = True
        if tag == "a" and attributes.get("class") == "skip-link":
            self.skip_link_target = attributes.get("href", "").removeprefix("#")
        if tag == "button" and attributes.get("class") == "nav-toggle":
            self.nav_toggle_controls = attributes.get("aria-controls")
            self.nav_toggle_expanded = attributes.get("aria-expanded")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_text += data


def _representative_pages() -> list[Path]:
    root = Path("site/dist")
    pages = list(root.glob("*.html"))
    for fips in ["01001", "17031", "36005", "48201"]:
        page = root / "counties" / f"{fips}.html"
        if page.exists():
            pages.append(page)
    return pages


def test_representative_pages_have_accessible_landmarks_and_metadata():
    root = Path("site/dist")
    if not root.exists():
        pytest.skip("Generated site is not present.")

    failures: list[str] = []
    for page in _representative_pages():
        parser = StructureParser()
        parser.feed(page.read_text(encoding="utf-8"))

        if "main" not in parser.tags or "main" not in parser.ids:
            failures.append(f"{page}: missing main landmark with id='main'")
        if "header" not in parser.tags:
            failures.append(f"{page}: missing header")
        if "footer" not in parser.tags:
            failures.append(f"{page}: missing footer")
        if not parser.nav_primary:
            failures.append(f"{page}: missing primary navigation label")
        if parser.h1_count != 1:
            failures.append(f"{page}: expected exactly one h1, found {parser.h1_count}")
        if not parser.title_text.strip():
            failures.append(f"{page}: missing title")
        if not parser.meta_description:
            failures.append(f"{page}: missing meta description")
        if not parser.og_title or not parser.og_description:
            failures.append(f"{page}: missing Open Graph title/description")
        if not parser.og_site_name:
            failures.append(f"{page}: missing Open Graph site name")
        if not parser.og_image or not parser.og_image_alt:
            failures.append(f"{page}: missing Open Graph image metadata")
        if not parser.twitter_card or not parser.twitter_title or not parser.twitter_description:
            failures.append(f"{page}: missing Twitter card metadata")
        if not parser.twitter_image:
            failures.append(f"{page}: missing Twitter image metadata")
        if parser.og_image != parser.twitter_image:
            failures.append(f"{page}: social image metadata differs between Open Graph and Twitter")
        if parser.og_image and not (page.parent / parser.og_image).resolve().exists():
            failures.append(f"{page}: social image does not resolve")
        if parser.skip_link_target != "main" or "main" not in parser.ids:
            failures.append(f"{page}: skip link does not target main")
        if parser.nav_toggle_controls != "nav-links" or parser.nav_toggle_expanded != "false":
            failures.append(f"{page}: nav toggle ARIA state is incomplete")

    assert failures == []


def test_static_assets_include_keyboard_focus_and_escape_menu_support():
    root = Path("site/dist")
    if not root.exists():
        pytest.skip("Generated site is not present.")

    css = (root / "static" / "css" / "styles.css").read_text(encoding="utf-8")
    js = (root / "static" / "js" / "app.js").read_text(encoding="utf-8")

    assert ":focus-visible" in css
    assert 'event.key === "Escape"' in js
    assert "aria-expanded" in js
