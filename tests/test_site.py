"""Unit tests use synthetic temporary records; no real meeting content."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_site import discover_posts, extract_post_metadata, render_archive, render_card, read_taxonomy


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "data").mkdir()
        (self.root / "data" / "taxonomy.json").write_text(
            (Path(__file__).resolve().parents[1] / "data" / "taxonomy.json").read_text(encoding="utf-8"), encoding="utf-8")
        self.posts = self.root / "posts"
        self.item = self.posts / "2026/11/2026-11-24-example"
        self.item.mkdir(parents=True)
        self.source = self.root / "notes/meetings/2026/11/2026-11-24-example.md"
        self.source.parent.mkdir(parents=True)
        self.source.write_text("# 合成示例，非真实会议\n", encoding="utf-8")
        self.metadata = {
            "title": "合成示例：架构讨论", "date": "2026-11-24", "summary": "一个纯虚构的产品讨论",
            "kind": "meeting", "topics": "product,engineering", "source": "notes/meetings/2026/11/2026-11-24-example.md",
            "visibility": "public", "release": "approved",
        }
        self.evidence = {
            "schema_version": 1,
            "source": {"id": "fixture", "type": "synthetic", "path": self.metadata["source"]},
            "release": {"approved": True, "audience": "public", "approval_record": "测试专用合成数据"},
            "claims": [{"id": "c1", "kind": "user-statement", "source_id": "fixture"}],
        }

    def write_page(self):
        from html import escape
        html = "<!doctype html><html lang='zh'><head>"
        for key, value in self.metadata.items():
            html += f'<meta name="notes:{key}" content="{escape(value, quote=True)}">'
        html += "</head><body><main><h1>合成会议演示</h1></main></body></html>"
        (self.item / "index.html").write_text(html, encoding="utf-8")
        (self.item / "evidence.json").write_text(json.dumps(self.evidence, ensure_ascii=False), encoding="utf-8")

    def test_valid_approved_record_discovered(self):
        self.write_page()
        results = discover_posts(self.posts, self.root)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["kind"], "meeting")
        self.assertEqual(results[0]["topics"], ["product", "engineering"])
        self.assertIn("month-group", render_archive(results))

    def test_unapproved_html_is_rejected(self):
        self.metadata["visibility"] = "private"
        self.write_page()
        with self.assertRaisesRegex(ValueError, "not been approved"):
            extract_post_metadata(self.item / "index.html", self.posts, self.root)

    def test_evidence_must_match_source(self):
        self.evidence["source"]["path"] = "notes/meetings/other.md"
        self.write_page()
        with self.assertRaisesRegex(ValueError, "source mismatch"):
            extract_post_metadata(self.item / "index.html", self.posts, self.root)

    def test_no_outside_path_allowed(self):
        self.metadata["source"] = "notes/../../secret.md"
        self.evidence["source"]["path"] = self.metadata["source"]
        self.write_page()
        with self.assertRaisesRegex(ValueError, "safe public notes"):
            extract_post_metadata(self.item / "index.html", self.posts, self.root)

    def test_unknown_topic_rejected(self):
        self.metadata["topics"] = "project-unknown"
        self.write_page()
        with self.assertRaisesRegex(ValueError, "taxonomy"):
            extract_post_metadata(self.item / "index.html", self.posts, self.root)

    def test_html_escapes_hostile_metadata(self):
        self.metadata["title"] = "<script>alert(1)</script>"
        self.write_page()
        record = discover_posts(self.posts, self.root)[0]
        rendered = render_card(record)
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)

    def test_empty_posts_is_honest(self):
        results = discover_posts(self.posts / "not-found", self.root)
        self.assertEqual(results, [])
        self.assertIn("还没有公开", render_archive(results))

    def test_taxonomy_has_separate_kinds_and_topics(self):
        taxonomy = read_taxonomy(self.root / "data" / "taxonomy.json")
        self.assertGreaterEqual(len(taxonomy["topics"]), 6)
        self.assertIn("meeting", [item["slug"] for item in taxonomy["kinds"]])


if __name__ == "__main__":
    unittest.main()
