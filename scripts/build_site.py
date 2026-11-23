"""Build a privacy-first, date × topic × kind static index from approved visual notes."""
from __future__ import annotations

from collections import Counter
from datetime import date
from html import escape
from html.parser import HTMLParser
from itertools import groupby
import json
from pathlib import Path, PurePosixPath
import shutil

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "posts"
SITE = ROOT / "site"
OUT = ROOT / "_site"
TAXONOMY = ROOT / "data" / "taxonomy.json"

REQUIRED = ("title", "date", "summary", "kind", "topics", "source", "visibility", "release")


class MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "meta":
            return
        values = dict(attrs)
        name = values.get("name", "") or ""
        if name.startswith("notes:"):
            self.meta[name.removeprefix("notes:")] = values.get("content", "") or ""


def read_taxonomy(path: Path = TAXONOMY) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("topics", "kinds"):
        values = data.get(key, [])
        slugs = [row["slug"] for row in values]
        if not values or len(set(slugs)) != len(slugs):
            raise ValueError("Taxonomy requires unique, nonempty " + key)
    return data


def checked_source(source: str, root: Path) -> Path:
    relative = PurePosixPath(source)
    if relative.is_absolute() or ".." in relative.parts or not source.startswith("notes/"):
        raise ValueError("Source must be a safe public notes/ path")
    resolved = (root / source).resolve()
    if not resolved.is_relative_to((root / "notes").resolve()) or resolved.suffix != ".md":
        raise ValueError("Source path escapes public notes")
    if not resolved.is_file():
        raise ValueError("Missing approved public source: " + source)
    return resolved


def extract_post_metadata(path: Path, posts_root: Path = POSTS, root: Path = ROOT,
                          taxonomy: dict | None = None) -> dict:
    """Fail closed: no publication without reviewed public metadata and evidence."""
    taxonomy = taxonomy if taxonomy is not None else read_taxonomy(root / "data" / "taxonomy.json")
    parser = MetadataParser()
    parser.feed(path.read_text(encoding="utf-8"))
    m = {key: value.strip() for key, value in parser.meta.items()}
    missing = [key for key in REQUIRED if not m.get(key)]
    if missing:
        raise ValueError(f"{path}: missing required metadata {missing}")
    try:
        dt = date.fromisoformat(m["date"])
    except ValueError as err:
        raise ValueError(f"{path}: invalid date") from err
    if dt.isoformat() != m["date"]:
        raise ValueError(f"{path}: date must use YYYY-MM-DD")

    rel = path.parent.relative_to(posts_root)
    parts = rel.parts
    if len(parts) != 3 or parts[0] != m["date"][:4] or parts[1] != m["date"][5:7] or not parts[2].startswith(m["date"] + "-") or len(parts[2]) <= 11:
        raise ValueError(f"{path}: path must be YYYY/MM/YYYY-MM-DD-slug/index.html")

    if m["visibility"] != "public" or m["release"] != "approved":
        raise ValueError(f"{path}: public publishing has not been approved")
    topics = [t.strip() for t in m["topics"].split(",") if t.strip()]
    allowed_topics = {t["slug"]: t["name"] for t in taxonomy["topics"]}
    allowed_kinds = {k["slug"]: k["name"] for k in taxonomy["kinds"]}
    if not topics or len(topics) > 3 or len(topics) != len(set(topics)) or any(t not in allowed_topics for t in topics):
        raise ValueError(f"{path}: topics must contain 1-3 distinct taxonomy slugs")
    if m["kind"] not in allowed_kinds:
        raise ValueError(f"{path}: invalid kind")
    checked_source(m["source"], root)

    evidence_path = path.parent / "evidence.json"
    if not evidence_path.is_file():
        raise ValueError(f"{path}: missing evidence.json")
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    approval = evidence.get("release", {})
    source = evidence.get("source", {})
    if approval.get("approved") is not True or approval.get("audience") != "public" or not str(approval.get("approval_record", "")).strip():
        raise ValueError(f"{path}: evidence missing explicit public release record")
    if source.get("path") != m["source"] or not source.get("id"):
        raise ValueError(f"{path}: evidence source mismatch")
    claims = evidence.get("claims", [])
    if not isinstance(claims, list) or any(not isinstance(c, dict) or c.get("source_id") != source["id"] for c in claims):
        raise ValueError(f"{path}: evidence claims must reference source id")
    cover = m.get("cover", "")
    if cover:
        cover_rel = PurePosixPath(cover)
        if cover_rel.is_absolute() or ".." in cover_rel.parts or not (path.parent / cover).is_file():
            raise ValueError(f"{path}: invalid cover path")
    return {
        "title": m["title"], "date": m["date"], "month": m["date"][:7],
        "summary": m["summary"], "kind": m["kind"], "kind_label": allowed_kinds[m["kind"]],
        "topics": topics, "topic_labels": [allowed_topics[t] for t in topics],
        "tags": [t.strip() for t in m.get("tags", "").split(",") if t.strip()],
        "cover": cover, "source": m["source"],
        "url": "posts/" + rel.as_posix() + "/",
    }


def discover_posts(posts_root: Path = POSTS, root: Path = ROOT, taxonomy: dict | None = None) -> list[dict]:
    if not posts_root.exists():
        return []
    taxonomy = taxonomy if taxonomy is not None else read_taxonomy(root / "data" / "taxonomy.json")
    records = [extract_post_metadata(p, posts_root, root, taxonomy) for p in posts_root.glob("**/index.html")]
    urls = [p["url"] for p in records]
    if len(urls) != len(set(urls)):
        raise ValueError("Duplicate article URL")
    return sorted(records, key=lambda p: (p["date"], p["title"]), reverse=True)


def render_card(post: dict) -> str:
    def e(value: str) -> str:
        return escape(str(value), quote=True)
    search = " ".join([post["title"], post["summary"], post["kind_label"],
                       *post["topic_labels"], *post["tags"]]).lower()
    chips = " · ".join(post["topic_labels"])
    cover = ""
    if post.get("cover"):
        cover = f'<img class="note-cover" alt="" loading="lazy" src="{e(post["url"] + post["cover"])}">'
    return (
        f'<article class="note-card" data-date="{e(post["date"])}" data-kind="{e(post["kind"])}" '
        f'data-topics="{e(" ".join(post["topics"]))}" data-search="{e(search)}">'
        f'<a href="{e(post["url"])}">{cover}'
        f'<div class="note-eyebrow"><span>{e(post["kind_label"])}</span><span>{e(post["date"])}</span></div>'
        f'<h4>{e(post["title"])}</h4><p>{e(post["summary"])}</p>'
        f'<div class="note-bottom"><span class="note-tags">{e(chips)}</span><span class="note-arrow" aria-hidden="true">↗</span></div>'
        f'</a></article>'
    )


def render_archive(posts: list[dict]) -> str:
    if not posts:
        return ('<div class="no-records"><div class="no-records-icon" aria-hidden="true">◇</div>'
                '<h3>还没有公开的工作笔记</h3><p>内部会议默认不发布。取得明确授权的脱敏视觉笔记，'
                '会按照时间自动出现在这里。</p>'
                '<a href="demo.html">先看一篇合成视觉示例 ↗</a></div>')
    chunks = []
    for month, records_iter in groupby(posts, key=lambda post: post["month"]):
        records = list(records_iter)
        parts = [f'<section class="month-group" data-month="{escape(month)}">'
                 f'<div class="month-heading"><h3>{escape(month[:4])}年{escape(month[5:])}月</h3>'
                 f'<span>{len(records):02d} ENTRIES</span></div>']
        for day, day_iter in groupby(records, key=lambda post: post["date"]):
            cards = "\n".join(render_card(post) for post in day_iter)
            parts.append(f'<div class="day-group"><div class="day-heading"><time datetime="{escape(day)}">'
                         f'{escape(day)}</time><span>工作记录</span></div><div class="note-list">{cards}</div></div>')
        parts.append('</section>')
        chunks.append("\n".join(parts))
    return "\n".join(chunks)


def render_topic_nav(posts: list[dict], taxonomy: dict) -> str:
    counts = Counter(t for post in posts for t in post["topics"])
    icons = ["◉", "⌘", "◇", "↗", "⌁", "◎"]
    chunks = []
    for i, item in enumerate(taxonomy["topics"]):
        slug = escape(item["slug"], quote=True)
        name = escape(item["name"])
        description = escape(item["description"])
        chunks.append(
            f'<button class="topic-card" type="button" data-topic-select="{slug}" aria-pressed="false" '
            f'aria-label="筛选主题：{name}">'
            f'<span class="topic-card-top"><span>TOPIC / {i + 1:02d}</span><span class="topic-card-icon" aria-hidden="true">{icons[i % len(icons)]}</span></span>'
            f'<h3>{name}</h3><span class="topic-card-bottom"><span>{description} · {counts[item["slug"]]} 篇</span>'
            '<span class="topic-card-arrow" aria-hidden="true">↗</span></span></button>'
        )
    return "\n".join(chunks)


def render_options(values: list[tuple[str, str]]) -> str:
    return "\n".join(f'<option value="{escape(k, quote=True)}">{escape(v)}</option>' for k, v in values)


def main() -> None:
    taxonomy = read_taxonomy()
    posts = discover_posts(taxonomy=taxonomy)  # Validate all content before touching output.
    template = (SITE / "index.html").read_text(encoding="utf-8")
    months = sorted({post["month"] for post in posts}, reverse=True)
    replacements = {
        "{{TOTAL_COUNT}}": str(len(posts)),
        "{{MEETING_COUNT}}": str(sum(p["kind"] == "meeting" for p in posts)),
        "{{ACTIVE_TOPIC_COUNT}}": str(len({t for p in posts for t in p["topics"]})),
        "{{TOPIC_NAV}}": render_topic_nav(posts, taxonomy),
        "{{ARCHIVE_CONTENT}}": render_archive(posts),
        "{{MONTH_OPTIONS}}": render_options([(m, m[:4] + "年" + m[5:] + "月") for m in months]),
        "{{TOPIC_OPTIONS}}": render_options([(t["slug"], t["name"]) for t in taxonomy["topics"]]),
        "{{KIND_OPTIONS}}": render_options([(k["slug"], k["name"]) for k in taxonomy["kinds"]]),
    }
    for token, replacement in replacements.items():
        if token not in template:
            raise ValueError("Missing homepage placeholder: " + token)
        template = template.replace(token, replacement)
    if "{{" in template:
        raise ValueError("Unresolved homepage template token")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    (OUT / "index.html").write_text(template, encoding="utf-8")
    shutil.copytree(SITE / "assets", OUT / "assets")
    shutil.copyfile(SITE / "demo.html", OUT / "demo.html")
    if POSTS.exists():
        shutil.copytree(POSTS, OUT / "posts", dirs_exist_ok=True)
    (OUT / "posts").mkdir(exist_ok=True)
    (OUT / "posts" / "index.json").write_text(
        json.dumps({"count": len(posts), "posts": posts}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built work-notes: {len(posts)} approved public articles -> {OUT}")


if __name__ == "__main__":
    main()
