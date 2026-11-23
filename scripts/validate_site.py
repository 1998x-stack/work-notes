"""Audit site structure, local links, figures and approval metadata after build."""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

from build_site import OUT, ROOT, POSTS, discover_posts


class PageAudit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h1 = 0
        self.ids: set[str] = set()
        self.duplicates: list[str] = []
        self.links: list[tuple[str, str]] = []
        self.errors: list[str] = []
        self.svg_depth = 0
        self.svg_stack: list[dict] = []

    def handle_starttag(self, tag, attrs):
        vals = dict(attrs)
        identity = vals.get("id")
        if identity:
            if identity in self.ids:
                self.duplicates.append(identity)
            self.ids.add(identity)
        if tag == "h1":
            self.h1 += 1
        if tag in ("a", "link", "script", "img", "source"):
            attr = "href" if tag in ("a", "link") else "src"
            value = vals.get(attr, "")
            if value:
                self.links.append((tag, value))
                url = urlsplit(value)
                if tag in ("script", "link", "img", "source") and (url.scheme in ("http", "https") or url.netloc):
                    self.errors.append("Remote runtime asset blocked: " + value)
                if value.lower().startswith("javascript:"):
                    self.errors.append("javascript: URL is not allowed")
            if tag == "img" and vals.get("alt") is None:
                self.errors.append("Image without alt")
        if tag == "iframe":
            self.errors.append("iframes forbidden in public notes")
        if tag == "svg":
            if not vals.get("viewbox"):
                self.errors.append("Inline SVG missing viewBox")
            self.svg_stack.append({"title": False, "desc": False})
        elif self.svg_stack and tag in ("title", "desc"):
            self.svg_stack[-1][tag] = True

    def handle_endtag(self, tag):
        if tag == "svg" and self.svg_stack:
            item = self.svg_stack.pop()
            if not item["title"] or not item["desc"]:
                self.errors.append("Inline SVG missing title/desc")


def resolve_local_url(page: Path, raw: str) -> Path | None:
    url = urlsplit(raw)
    if url.scheme in ("http", "https", "mailto", "tel") or url.netloc:
        return None
    if raw.startswith(("data:", "blob:")):
        return None
    if url.scheme:
        raise ValueError("Forbidden link scheme: " + url.scheme)
    target = unquote(url.path)
    if not target and url.fragment:
        return page
    if not target:
        return None
    resolved = (OUT / target.lstrip("/")) if target.startswith("/") else (page.parent / target)
    if resolved.is_dir():
        resolved = resolved / "index.html"
    resolved = resolved.resolve()
    if not resolved.is_relative_to(OUT.resolve()):
        raise ValueError("Local link escapes output: " + raw)
    return resolved


def audit_html(page: Path) -> list[str]:
    parser = PageAudit()
    parser.feed(page.read_text(encoding="utf-8"))
    issues: list[str] = []
    if parser.h1 != 1:
        issues.append(f"{page}: expected one h1; got {parser.h1}")
    for identity in parser.duplicates:
        issues.append(f"{page}: duplicate id {identity}")
    for reason in parser.errors:
        issues.append(f"{page}: {reason}")
    for tag, raw in parser.links:
        try:
            target = resolve_local_url(page, raw)
        except ValueError as exc:
            issues.append(f"{page}: {exc}")
            continue
        if target is None:
            continue
        if not target.exists():
            issues.append(f"{page}: broken {tag} link: {raw}")
            continue
        fragment = urlsplit(raw).fragment
        if fragment and target.suffix.lower() == ".html":
            reference = PageAudit()
            reference.feed(target.read_text(encoding="utf-8"))
            if fragment not in reference.ids:
                issues.append(f"{page}: missing fragment target: {raw}")
    return issues


def audit_svg(path: Path) -> list[str]:
    issues = []
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        if "viewBox" not in root.attrib:
            issues.append(f"{path}: missing viewBox")
        names = [tag.tag.split("}")[-1] for tag in root.iter()]
        if "title" not in names or "desc" not in names:
            issues.append(f"{path}: missing title or desc")
        ids = [tag.get("id") for tag in root.iter() if tag.get("id")]
        if len(ids) != len(set(ids)):
            issues.append(f"{path}: duplicate svg ids")
    except ET.ParseError as exc:
        issues.append(f"{path}: invalid SVG XML: {exc}")
    return issues


def main() -> int:
    problems = []
    if not (OUT / "index.html").exists():
        print("Build output missing. Run python scripts/build_site.py first.", file=sys.stderr)
        return 1
    try:
        posts = discover_posts()
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("Publishing gate failed: " + str(exc), file=sys.stderr)
        return 1
    index = json.loads((OUT / "posts" / "index.json").read_text(encoding="utf-8"))
    if index.get("count") != len(posts) or index.get("posts") != posts:
        problems.append("Generated index does not match approved source posts")

    all_pages = sorted(OUT.rglob("*.html"))
    if len(all_pages) != len(posts) + 2:  # Homepage + synthetic demo + approved posts.
        problems.append("Unexpected number of published HTML pages")
    for page in all_pages:
        problems.extend(audit_html(page))
    for svg in OUT.rglob("*.svg"):
        problems.extend(audit_svg(svg))
    for item in list(POSTS.glob("**/*")) if POSTS.exists() else []:
        if item.is_file() and item.suffix.lower() in (".mp3", ".wav", ".m4a", ".mp4", ".srt", ".vtt"):
            problems.append(f"Raw media/transcript file forbidden in public posts: {item}")

    secret_pattern = re.compile(r"(?:-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|ghp_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{30,})")
    for folder in (ROOT / "notes", ROOT / "posts"):
        if folder.is_dir():
            for path in folder.rglob("*"):
                if path.is_file() and path.suffix.lower() in (".md", ".json", ".html", ".svg"):
                    if secret_pattern.search(path.read_text(encoding="utf-8")):
                        problems.append(f"Secret-like token in public source: {path}")

    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    print(f"Validation passed: homepage, demo, {len(posts)} approved note(s), local assets, links and SVG.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
