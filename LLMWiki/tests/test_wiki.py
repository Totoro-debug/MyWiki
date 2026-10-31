"""通过公开接口验证来源准确性与更新行为；全部写入临时仓库。"""
import json
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from wiki import Wiki, contains


class WikiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.home = self.root / "LLMWiki"
        self.home.mkdir()
        shutil.copyfile(Path(__file__).resolve().parents[1] / "config.json", self.home / "config.json")
        self.wiki = Wiki(self.root)
        self.redis = "01-计算机基础/数据库/Redis.md"
        self.mysql = "01-计算机基础/数据库/MySQL.md"
        self.write(self.redis, "# Redis\n\n## 缓存击穿\n\n使用互斥锁保护缓存重建。\n\n## 缓存穿透\n\n使用布隆过滤器。\n")
        self.write(self.mysql, "# MySQL\n\n## MVCC\n\nMVCC 使用版本链和 ReadView。\n\n## 待补全\n")
        self.write("02-Java 后端/JUC.md", "# JUC\n\n## CAS\n\nCAS 是原子操作。\n\n```python\n# 不是真标题\nprint('case')\n```\n")

    def tearDown(self):
        self.temp.cleanup()

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        return path

    def catalogue(self):
        return json.loads((self.home / "generated/catalogue.json").read_text(encoding="utf-8"))

    def test_build_is_read_only_and_covers_source_lines(self):
        before = {p: p.read_bytes() for p in self.root.rglob("*.md")}
        result = self.wiki.update()
        self.assertEqual(3, result["notes"])
        self.assertTrue(self.wiki.verify()["ok"])
        for path, raw in before.items():
            self.assertEqual(raw, path.read_bytes())
        self.assertTrue(self.wiki.status()["fresh"])

    def test_chinese_query_returns_exact_source_lines(self):
        result = self.wiki.search("Redis 缓存击穿")
        self.assertEqual(1, len(result["hits"]))
        hit = result["hits"][0]
        self.assertEqual(self.redis, hit["path"])
        self.assertEqual(3, hit["start"])
        self.assertTrue(hit["verified"])
        self.assertIn("互斥锁", self.wiki.read(hit["id"])["text"])

    def test_alias_lookup_preserves_actual_evidence(self):
        hit = self.wiki.search("多版本并发控制")["hits"][0]
        self.assertEqual(self.mysql, hit["path"])
        self.assertIn("MVCC", hit["body_evidence"])
        self.assertNotIn("多版本并发控制", hit["body_evidence"])

    def test_identifier_boundaries_do_not_match_case_or_121(self):
        self.assertFalse(contains("case", "CAS"))
        self.assertFalse(contains("121", "1"))
        self.assertTrue(contains("CAS（原子操作）", "cas"))
        self.assertEqual([], self.wiki.search("caseMissing")["hits"])

    def test_code_headings_are_not_parsed_as_markdown(self):
        self.wiki.update()
        doc = next(d for d in self.catalogue() if d["path"].endswith("JUC.md"))
        self.assertEqual(["JUC", "CAS"], [s["heading"] for s in doc["sections"]])
        self.assertIn("print('case')", self.wiki.read("02-Java 后端/JUC.md")["text"])

    def test_same_size_and_mtime_change_still_refreshes(self):
        old_hit = self.wiki.search("互斥锁")["hits"][0]
        path = self.root / self.redis
        stat = path.stat()
        old = path.read_bytes()
        path.write_bytes(old.replace("互斥锁".encode(), "分布锁".encode()))
        os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        self.assertEqual(len(old), path.stat().st_size)
        self.assertFalse(self.wiki.status()["fresh"])
        self.assertEqual([], self.wiki.search("互斥锁")["hits"])
        self.assertEqual(1, len(self.wiki.search("分布锁")["hits"]))
        with self.assertRaises(ValueError):
            self.wiki.read(old_hit["id"])

    def test_add_rename_delete_updates_cards_and_fts(self):
        self.wiki.update()
        old = next(d for d in self.catalogue() if d["path"] == self.redis)
        moved = "01-计算机基础/数据库/Redis 新.md"
        (self.root / self.redis).rename(self.root / moved)
        result = self.wiki.update()
        self.assertIn(self.redis, result["deleted"])
        self.assertIn(moved, result["changed"])
        self.assertFalse((self.home / old["card"]).exists())
        self.assertEqual(moved, self.wiki.search("缓存击穿")["hits"][0]["path"])
        (self.root / moved).unlink()
        self.assertEqual([], self.wiki.search("缓存击穿")["hits"])
        self.assertTrue(self.wiki.verify()["ok"])

    def test_no_change_does_not_rewrite_generated_files(self):
        self.wiki.update()
        marker = self.home / "generated/manifest.json"
        previous = marker.stat().st_mtime_ns
        result = self.wiki.update()
        self.assertEqual([], result["changed"])
        self.assertEqual(previous, marker.stat().st_mtime_ns)

    def test_missing_generated_page_is_repaired(self):
        self.wiki.update()
        card = self.home / self.catalogue()[0]["card"]
        card.unlink()
        self.assertFalse(self.wiki.status()["fresh"])
        self.wiki.update()
        self.assertTrue(card.exists())

    def test_generated_tampering_is_detected_and_rebuild_repairs(self):
        self.wiki.update()
        card = self.home / self.catalogue()[0]["card"]
        card.write_text("wrong", encoding="utf-8")
        self.assertFalse(self.wiki.verify()["ok"])
        self.wiki.update(rebuild=True)
        self.assertTrue(self.wiki.verify()["ok"])

    def test_deleted_cache_can_be_rebuilt(self):
        self.wiki.update()
        self.wiki.db_path.unlink()
        self.assertFalse(self.wiki.status()["fresh"])
        self.assertTrue(self.wiki.search("MVCC")["hits"])
        self.assertTrue(self.wiki.verify()["ok"])

    def test_config_and_leetcode_metadata_changes_refresh(self):
        self.write("08-LeetCode/哈希表/1. 两数之和.md", "# 两数之和\n\n用哈希表记录下标。\n")
        self.write("08-LeetCode/.leetcode-index.json", json.dumps({"two-sum": [1, "两数之和", "哈希表/1. 两数之和.md"]}))
        self.assertTrue(self.wiki.search("two-sum")["hits"][0]["path"].endswith("1. 两数之和.md"))
        config = json.loads((self.home / "config.json").read_text(encoding="utf-8"))
        config["aliases"].append(["哈希表", "哈希映射"])
        (self.home / "config.json").write_text(json.dumps(config), encoding="utf-8")
        self.assertTrue(self.wiki.status()["config_changed"])
        self.assertTrue(self.wiki.search("哈希映射")["hits"])

    def test_frontmatter_bom_crlf_aliases_and_setext(self):
        raw = "---\r\ntitle: 正式标题\r\naliases:\r\n  - 特别别名\r\ntags: [数据, 技术]\r\n---\r\n章节\r\n====\r\n\r\n正文原样保留。\r\n"
        (self.root / "Meta.md").write_bytes(b"\xef\xbb\xbf" + raw.encode("utf-8"))
        hit = self.wiki.search("特别别名")["hits"][0]
        self.assertEqual("正式标题", hit["title"])
        self.assertIn("metadata_only", hit["match"])
        self.assertTrue(self.wiki.verify()["ok"])
        doc = next(d for d in self.catalogue() if d["path"] == "Meta.md")
        self.assertEqual("章节", doc["sections"][-1]["heading"])

    def test_empty_and_image_only_sections_are_explicit(self):
        self.write("图.md", "# 图片\n\n![[picture.webp]]\n\n## 待填写\n")
        self.write("00-resource/images/picture.webp", "placeholder")
        self.wiki.update()
        doc = next(d for d in self.catalogue() if d["path"] == "图.md")
        self.assertTrue(doc["sections"][0]["image_only"])
        self.assertTrue(doc["sections"][1]["empty"])
        links = json.loads((self.home / "generated/links.json").read_text(encoding="utf-8"))
        self.assertEqual("resolved", links[0]["status"])

    def test_ambiguous_wikilinks_are_not_silently_resolved(self):
        self.write("one/同名.md", "一\n")
        self.write("two/同名.md", "二\n")
        self.write("链接.md", "[[同名]]\n`[[不存在]]`\n输出：[[1]]\n输出：[[3],[9,20]]\n")
        self.wiki.update()
        links = json.loads((self.home / "generated/links.json").read_text(encoding="utf-8"))
        self.assertEqual(1, len(links))
        self.assertEqual("ambiguous", links[0]["status"])

    def test_long_code_section_retains_complete_line_coverage(self):
        self.write("long.md", "# Code\n```python\n" + "\n".join(f"variable_{i} = {i} # 注释" for i in range(600)) + "\n```\n")
        self.wiki.update()
        self.assertTrue(self.wiki.verify()["all_nonblank_source_lines_covered"])
        self.assertIn("variable_599", self.wiki.read(self.wiki.search("variable_599")["hits"][0]["id"])["text"])

    def test_literal_and_scope_and_query_syntax_are_safe(self):
        self.assertEqual([], self.wiki.search("多版本并发控制", literal=True)["hits"])
        self.assertEqual([], self.wiki.search("缓存击穿", scope="MySQL.md")["hits"])
        self.assertEqual([], self.wiki.search('" OR NEAR() * ; SELECT 1 --', scope="%_'")["hits"])
        with self.assertRaises(ValueError):
            self.wiki.read("../../outside.md")
        with self.assertRaises(ValueError):
            self.wiki.search("MVCC", limit=0)

    def test_partial_hits_are_explicit_and_full_hits_filter_noise(self):
        self.assertTrue(all(h["match"].startswith("all_terms") for h in self.wiki.search("Redis 缓存击穿")["hits"]))
        partial = self.wiki.search("缓存击穿 无此术语")["hits"]
        self.assertTrue(partial)
        self.assertTrue(all(h["match"].startswith("partial_terms") for h in partial))

    def test_empty_file_is_readable_without_inventing_lines(self):
        self.write("空白.md", "")
        self.assertEqual("", self.wiki.read("空白.md")["text"])
        self.assertTrue(self.wiki.verify()["ok"])

    def test_concurrent_searches_share_consistent_index(self):
        self.wiki.update()
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda q: self.wiki.search(q), ["MVCC", "缓存击穿", "CAS", "缓存穿透"]))
        self.assertTrue(all(r["hits"][0]["verified"] for r in results))
        self.assertFalse((self.wiki.cache / "update.lock").exists())
        self.assertTrue(self.wiki.verify()["ok"])

    def test_hidden_directories_and_instruction_files_are_not_indexed(self):
        self.write(".obsidian/秘密.md", "secret\n")
        self.write("AGENTS.md", "agent instructions\n")
        self.write("LLMWiki/custom.md", "derived content\n")
        self.assertEqual(3, self.wiki.update()["notes"])


if __name__ == "__main__":
    unittest.main()
