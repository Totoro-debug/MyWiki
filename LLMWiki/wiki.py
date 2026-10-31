#!/usr/bin/env python3
"""可重建、只读源文件的本地 LLMWiki。仅依赖 Python 标准库。"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import statistics
import sys
import time
import unicodedata
from urllib.parse import quote, unquote, urlsplit

SCHEMA = 1
HERE = Path(__file__).resolve().parent
WORD = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\U00020000-\U0002fa1f]+|[a-z0-9_]+", re.I)
CJK = re.compile(r"^[\u3400-\u4dbf\u4e00-\u9fff\U00020000-\U0002fa1f]+$")
HEADING = re.compile(r"^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".bmp", ".avif"}


def norm(text):
    return unicodedata.normalize("NFKC", text).casefold()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def short_id(prefix, text):
    return prefix + hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]


def terms(text):
    """中文单字/双字倒排 + 英文完整标识符；避免额外分词依赖。"""
    result = []
    for match in WORD.finditer(norm(text)):
        word = match.group()
        if CJK.fullmatch(word):
            result.extend(word)
            result.extend(word[i:i + 2] for i in range(len(word) - 1))
        else:
            result.append(word)
    return result


def query_terms(text):
    result = []
    for word in WORD.findall(norm(text)):
        if CJK.fullmatch(word) and len(word) > 1:
            result.extend(word[i:i + 2] for i in range(len(word) - 1))
        else:
            result.append(word)
    return list(dict.fromkeys(result))


@lru_cache(maxsize=4096)
def term_pattern(term):
    left = r"(?<![a-z0-9_])" if re.match(r"[a-z0-9_]", term) else ""
    right = r"(?![a-z0-9_])" if re.search(r"[a-z0-9_]$", term) else ""
    return re.compile(left + re.escape(term) + right)


def contains(text, term):
    """英文/数字要求标识符边界，CAS 不会命中 case，1 不会命中 121。"""
    return bool(term and term_pattern(norm(term)).search(norm(text)))


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def excerpt_block(text):
    # 摘录以纯文本呈现，原文中的相对链接/HTML 不会在新目录里被误执行或误解析。
    runs = [len(m[0]) for m in re.finditer(r"`+", text)]
    fence = "`" * max(3, max(runs, default=0) + 1)
    return ["", "  摘录（原文）：", "", "  " + fence + "text", "  " + text, "  " + fence, ""]


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return
    temp = path.with_name(path.name + ".tmp")
    try:
        temp.write_text(text, encoding="utf-8", newline="\n")
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def frontmatter(lines):
    """只提取 title/aliases/tags 的常见 YAML 标量/列表，不执行 YAML。"""
    if not lines or lines[0].strip() != "---":
        return {}, 0
    end = next((i for i in range(1, len(lines)) if lines[i].strip() in {"---", "..."}), None)
    if end is None:
        return {}, 0
    data, active = {}, None
    for line in lines[1:end]:
        m = re.match(r"^(title|aliases|alias|tags):\s*(.*)$", line)
        if m:
            active, value = m.groups()
            active = "aliases" if active == "alias" else active
            if value.startswith("[") and value.endswith("]"):
                data[active] = [v.strip().strip("\"'") for v in value[1:-1].split(",") if v.strip()]
            elif value:
                data[active] = [value.strip().strip("\"'")]
            else:
                data[active] = []
        elif active and re.match(r"^\s+-\s+", line):
            data[active].append(re.sub(r"^\s+-\s+", "", line).strip().strip("\"'"))
        elif line.strip():
            active = None
    return data, end + 1


def parse_note(path, raw, config, leetcode=None):
    text = raw.decode("utf-8-sig")
    lines = text.splitlines()
    meta, first = frontmatter(lines)
    title = (meta.get("title") or [Path(path).stem])[0]
    aliases = list(dict.fromkeys([Path(path).stem, *meta.get("aliases", [])]))
    if leetcode:
        aliases.extend([str(leetcode["id"]), leetcode["slug"], leetcode["title"], "LeetCode " + str(leetcode["id"])])
    outline, masked, issues = [], [], []
    stack, fence, fence_line = [], None, None
    for i, line in enumerate(lines):
        if i < first:
            masked.append("")
            continue
        marker = FENCE.match(line)
        if fence:
            masked.append("")
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            continue
        if marker:
            fence, fence_line = marker[1], i + 1
            masked.append("")
            continue
        masked.append(line)
        heading = HEADING.match(line)
        setext = (i > first and line.strip() and re.fullmatch(r" {0,3}(?:=+|-+)\s*", line)
                  and masked[i - 1].strip() and not HEADING.match(masked[i - 1]))
        if not heading and not setext:
            continue
        level = len(heading[1]) if heading else (1 if line.lstrip().startswith("=") else 2)
        label = heading[2].strip() if heading else lines[i - 1].strip()
        number = i + 1 if heading else i
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, label))
        outline.append({"heading": label, "level": level, "start": number,
                        "breadcrumb": " > ".join(h for _, h in stack)})
    if fence:
        issues.append({"kind": "unclosed_fence", "line": fence_line})
    seen = Counter(norm(h["heading"]) for h in outline)
    for h in outline:
        if seen[norm(h["heading"])] > 1:
            issues.append({"kind": "duplicate_heading", "line": h["start"], "heading": h["heading"]})
    sections = []
    if not outline or outline[0]["start"] > 1:
        sections.append({"heading": "前言", "breadcrumb": title, "level": 0, "start": 1})
    sections.extend(outline)
    chunks = []
    for i, section in enumerate(sections):
        section["end"] = sections[i + 1]["start"] - 1 if i + 1 < len(sections) else len(lines)
        following_child = i + 1 < len(sections) and sections[i + 1]["level"] > section["level"]
        body_start = section["start"] if section["level"] else max(section["start"] - 1, first)
        prose = [s for s in masked[body_start:section["end"]] if s.strip()]
        section["empty"] = not any(s.strip() for s in lines[body_start:section["end"]]) and not following_child
        section["image_only"] = bool(prose) and all(
            re.match(r"^\s*(?:!\[|<img\b)", s, re.I) for s in prose)
        # 逐字摘录，不生成未在原笔记中出现的事实。截断明确标记。
        excerpt = next((s.strip() for s in prose if not re.match(r"^\s*(?:!\[|<img\b|---$)", s, re.I)), "")
        section["excerpt"] = excerpt[:180] + (" …〔截断〕" if len(excerpt) > 180 else "")
        if section["empty"] and section["level"]:
            issues.append({"kind": "empty_section", "line": section["start"], "heading": section["heading"]})
        if section["image_only"]:
            issues.append({"kind": "image_only_section", "line": section["start"], "heading": section["heading"]})
        start = section["start"]
        while start <= section["end"]:
            end, size, in_code = start - 1, 0, None
            for number in range(start, section["end"] + 1):
                line = lines[number - 1]
                size += len(line) + 1
                end = number
                marker = FENCE.match(line)
                if marker:
                    if not in_code:
                        in_code = marker[1]
                    elif marker[1][0] == in_code[0] and len(marker[1]) >= len(in_code) and not marker[2].strip():
                        in_code = None
                if size >= config["chunk_max_chars"] or (size >= config["chunk_target_chars"] and not in_code and not line.strip()):
                    break
            body = "\n".join(lines[start - 1:end])
            if body.strip():
                chunk_id = short_id("c_", f"{path}\0{start}\0{end}\0{body}")
                chunks.append({"id": chunk_id, "start": start, "end": end,
                               "heading": section["breadcrumb"], "body": body,
                               "empty": section["empty"], "image_only": section["image_only"]})
            if end == section["end"]:
                break
            start = max(start + 1, end - 1)  # 长章节保留两行重叠。
    links = []
    for i, line in enumerate(masked, 1):
        # 内联代码及算法样例中的嵌套数组不是 Obsidian 链接。
        line = re.sub(r"(`+)(.+?)\1", lambda m: " " * len(m[0]), line)
        for match in re.finditer(r"(!?)\[\[([^\[\]]+)\]\]", line):
            if re.fullmatch(r"[\d\s,+.\-]+", match[2]):
                continue
            links.append({"line": i, "target": match[2].split("|", 1)[0], "embed": bool(match[1]), "syntax": "wiki"})
        for match in re.finditer(r"(!?)\[[^\[\]]*\]\(\s*(<[^>]*>|[^\s)]+)(?:\s+\"[^\"]*\")?\s*\)", line):
            links.append({"line": i, "target": match[2].strip("<>"), "embed": bool(match[1]), "syntax": "markdown"})
        for match in re.finditer(r"<(?:img|a)\b[^>]*?\b(?:src|href)=[\"']([^\"']+)[\"']", line, re.I):
            links.append({"line": i, "target": match[1], "embed": True, "syntax": "html"})
    return {"id": short_id("d_", path), "path": path, "title": title,
            "domain": path.split("/")[0] if "/" in path else "根目录",
            "sha256": digest(raw), "bytes": len(raw), "lines": len(lines),
            "aliases": list(dict.fromkeys(aliases)), "tags": meta.get("tags", []),
            "leetcode": leetcode, "sections": sections, "chunks": chunks, "links": links, "issues": issues}


class Wiki:
    """唯一外部接口：update / search / read / status / verify。源路径只用于读取。"""

    def __init__(self, root=None):
        self.root = Path(root).resolve() if root else HERE.parent
        self.home = self.root / "LLMWiki"
        self.generated = self.home / "generated"
        self.cache = self.home / ".cache"
        self.db_path = self.cache / "search.sqlite"

    @contextmanager
    def lock(self):
        self.cache.mkdir(parents=True, exist_ok=True)
        path = self.cache / "update.lock"
        deadline = time.monotonic() + 30
        while True:
            try:
                fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                break
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise RuntimeError("等待更新锁超时。确认没有 wiki.py 进程后，才可删除 LLMWiki/.cache/update.lock。")
                time.sleep(0.05)
        try:
            os.write(fd, str(os.getpid()).encode("ascii"))
            yield
        finally:
            os.close(fd)
            path.unlink(missing_ok=True)

    def snapshot(self):
        config_raw = (self.home / "config.json").read_bytes()
        config = json.loads(config_raw)
        if config.get("version") != 1 or not (0 < config["chunk_target_chars"] <= config["chunk_max_chars"]):
            raise ValueError("config.json 版本或分块长度无效")
        sources, assets = {}, []
        for base, dirs, files in os.walk(self.root, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not d.startswith(".") and d not in config["exclude_directories"]
                             and not (Path(base) / d).is_symlink())
            for name in sorted(files):
                p = Path(base) / name
                if name.startswith(".") or name in config["exclude_files"] or p.is_symlink():
                    continue
                rel = p.relative_to(self.root).as_posix()
                if p.suffix.lower() in {".md", ".markdown"}:
                    sources[rel] = p.read_bytes()
                else:
                    assets.append(rel)
        lc_path = self.root / "08-LeetCode" / ".leetcode-index.json"
        lc_raw = lc_path.read_bytes() if lc_path.exists() else b"{}"
        lc = json.loads(lc_raw)
        metadata_issues, lc_by_path = [], {}
        for slug, entry in lc.items():
            if not isinstance(entry, list) or len(entry) != 3:
                metadata_issues.append({"kind": "invalid_leetcode_entry", "slug": slug})
                continue
            number, title, path = entry
            rel = "08-LeetCode/" + str(path).replace("\\", "/")
            if rel not in sources:
                metadata_issues.append({"kind": "missing_leetcode_note", "slug": slug, "path": rel})
            elif rel in lc_by_path:
                metadata_issues.append({"kind": "duplicate_leetcode_path", "slug": slug, "path": rel})
            else:
                lc_by_path[rel] = {"id": number, "title": title, "slug": slug}
        signature = {"schema": SCHEMA, "engine": digest(Path(__file__).read_bytes()),
                     "config": digest(config_raw), "leetcode": digest(lc_raw),
                     "sources": {p: digest(raw) for p, raw in sorted(sources.items())}, "assets": sorted(assets)}
        return config, sources, lc_by_path, metadata_issues, signature

    def connect(self):
        con = sqlite3.connect(self.db_path, timeout=30)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        con.executescript("""
            CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS docs(path TEXT PRIMARY KEY, sha256 TEXT NOT NULL, data TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS chunks(
                rowid INTEGER PRIMARY KEY, id TEXT UNIQUE NOT NULL,
                path TEXT NOT NULL REFERENCES docs(path) ON DELETE CASCADE,
                title TEXT NOT NULL, heading TEXT NOT NULL, aliases TEXT NOT NULL,
                start INTEGER NOT NULL, end INTEGER NOT NULL, body TEXT NOT NULL,
                empty INTEGER NOT NULL, image_only INTEGER NOT NULL);
            CREATE INDEX IF NOT EXISTS chunks_path ON chunks(path);
            CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(title, heading, aliases, body);
            CREATE TRIGGER IF NOT EXISTS chunks_delete AFTER DELETE ON chunks BEGIN
                DELETE FROM search WHERE rowid=old.rowid;
            END;
        """)
        return con

    def update(self, rebuild=False):
        started = time.perf_counter()
        with self.lock():
            config, sources, lc, metadata_issues, signature = self.snapshot()
            con = self.connect()
            try:
                old = con.execute("SELECT value FROM meta WHERE key='signature'").fetchone()
                previous = json.loads(old[0]) if old else {}
                full = rebuild or any(previous.get(k) != signature[k] for k in ("schema", "engine", "config", "leetcode"))
                known = {r[0]: r[1] for r in con.execute("SELECT path,sha256 FROM docs")}
                changed = [p for p in sources if full or known.get(p) != signature["sources"][p]]
                deleted = sorted(set(known) - set(sources))
                generated_ok = self.generated_ok(signature)
                needs_export = bool(changed or deleted or signature != previous or not generated_ok or rebuild)
                if needs_export:
                    with con:
                        for path in [*deleted, *changed]:
                            con.execute("DELETE FROM docs WHERE path=?", (path,))
                        for path in changed:
                            doc = parse_note(path, sources[path], config, lc.get(path))
                            chunks = doc.pop("chunks")
                            con.execute("INSERT INTO docs VALUES(?,?,?)", (path, doc["sha256"], json.dumps(doc, ensure_ascii=False)))
                            alias_text = " ".join([*doc["aliases"], *doc["tags"], path])
                            for chunk in chunks:
                                cur = con.execute("""INSERT INTO chunks
                                    (id,path,title,heading,aliases,start,end,body,empty,image_only)
                                    VALUES(?,?,?,?,?,?,?,?,?,?)""",
                                    (chunk["id"], path, doc["title"], chunk["heading"], alias_text,
                                     chunk["start"], chunk["end"], chunk["body"], chunk["empty"], chunk["image_only"]))
                                con.execute("INSERT INTO search(rowid,title,heading,aliases,body) VALUES(?,?,?,?,?)",
                                            (cur.lastrowid, *[" ".join(terms(s)) for s in
                                                              (doc["title"], chunk["heading"], alias_text, chunk["body"])]))
                        con.execute("INSERT OR REPLACE INTO meta VALUES('signature',?)", (json.dumps(signature, sort_keys=True),))
                        con.execute("INSERT INTO search(search) VALUES('optimize')")
                    self.export(con, config, metadata_issues, signature)
                return {"changed": changed, "deleted": deleted, "rebuilt": full,
                        "notes": con.execute("SELECT count(*) FROM docs").fetchone()[0],
                        "chunks": con.execute("SELECT count(*) FROM chunks").fetchone()[0],
                        "elapsed_ms": round((time.perf_counter() - started) * 1000, 2)}
            finally:
                con.close()

    def generated_ok(self, signature):
        marker = self.generated / "manifest.json"
        try:
            manifest = json.loads(marker.read_text(encoding="utf-8"))
            return manifest["signature"] == signature and all(
                (self.home / path).is_file() for path in manifest["generated_files"])
        except (FileNotFoundError, ValueError, KeyError):
            return False

    def resolve_links(self, docs, assets):
        paths = {d["path"] for d in docs} | set(assets)
        by_name = defaultdict(list)
        by_path = {d["path"]: d for d in docs}
        for path in sorted(paths):
            by_name[norm(Path(path).name)].append(path)
        links, warnings = [], []
        for doc in docs:
            for original in doc["links"]:
                item = {"source": doc["path"], **original}
                target = unquote(original["target"])
                if urlsplit(target).scheme or target.startswith("//"):
                    item["status"] = "external_unchecked"
                    links.append(item)
                    continue
                target, _, anchor = target.partition("#")
                variants = [target] if Path(target).suffix else [target, target + ".md"]
                resolved = []
                if not target:
                    resolved = [doc["path"]]
                else:
                    for variant in variants:
                        relative = os.path.normpath(str(Path(doc["path"]).parent / variant)).replace("\\", "/")
                        if relative in paths:
                            resolved = [relative]
                            break
                        if variant.lstrip("/") in paths:
                            resolved = [variant.lstrip("/")]
                            break
                    if not resolved and original["syntax"] == "wiki" and "/" not in target:
                        resolved = sorted({p for v in variants for p in by_name.get(norm(v), [])})
                item["resolved"] = resolved
                item["anchor"] = anchor
                item["status"] = "resolved" if len(resolved) == 1 else ("ambiguous" if resolved else "missing")
                if len(resolved) == 1 and anchor and resolved[0] in by_path:
                    headings = [h["heading"] for h in by_path[resolved[0]]["sections"]]
                    def anchor_key(value):
                        return re.sub(r"[^\w\s\-]", "", norm(value)).replace(" ", "-")
                    if anchor.startswith("^"):
                        item["status"] = "block_anchor_unchecked"
                    elif not any(norm(anchor) == norm(h) or norm(anchor) == anchor_key(h) for h in headings):
                        item["status"] = "missing_heading"
                if item["status"] not in {"resolved", "external_unchecked"}:
                    warnings.append(item)
                links.append(item)
        return links, warnings

    def export(self, con, config, metadata_issues, signature):
        docs = [json.loads(r[0]) for r in con.execute("SELECT data FROM docs ORDER BY path")]
        links, link_warnings = self.resolve_links(docs, signature["assets"])
        files, catalogue = {}, []
        domains = defaultdict(list)
        for doc in docs:
            domains[doc["domain"]].append(doc)
            card = f"generated/notes/{doc['id']}.md"
            chunks = [dict(r) for r in con.execute("SELECT id,start,end,heading FROM chunks WHERE path=? ORDER BY start", (doc["path"],))]
            item = {k: doc[k] for k in ("id", "path", "title", "domain", "sha256", "bytes", "lines", "aliases", "tags", "leetcode", "sections")}
            item.update(card=card, chunks=chunks)
            catalogue.append(item)
            source_url = "../../../" + quote(doc["path"], safe="/")
            out = [f"# {doc['title']}", "", f"原文：[{doc['path']}]({source_url})",
                   f"SHA-256：`{doc['sha256']}`", "", "本卡为自动导航与逐字摘录；回答前使用 `wiki.py read` 核对原文。", ""]
            if doc["leetcode"]:
                out += [f"LeetCode：{doc['leetcode']['id']} / `{doc['leetcode']['slug']}`", ""]
            for section in doc["sections"]:
                state = "〔未填写〕" if section["empty"] else ("〔仅图片，未识别〕" if section["image_only"] else "")
                out += [f"- L{section['start']}-L{section['end']} · {section['breadcrumb']} {state}".rstrip()]
                if section["excerpt"]:
                    out += excerpt_block(section["excerpt"])
            read_range = f' --start 1 --end {min(80, doc["lines"])}' if doc["lines"] else ""
            out += ["", "## 读取入口", "", "```powershell", f'python LLMWiki/wiki.py read "{doc["path"]}"{read_range}', "```", ""]
            files[card] = "\n".join(out)
        index = ["# LLMWiki 导航", "", f"覆盖 {len(docs)} 篇 Markdown 笔记；原笔记是唯一事实来源。", "",
                 "入口：[使用与维护](README.md) · [检索规则](AGENTS.md) · [机器目录](generated/catalogue.json) · [质量报告](generated/audit.json)", "",
                 "先查主题或检索，命中后读取源章节。自动页面是定位材料，不作为独立证据。", "", "## 主题地图", ""]
        for concept in config["concepts"]:
            index.append(f"- [{concept['title']}](generated/concepts/{concept['id']}.md)")
            candidates = []
            for doc in docs:
                for section in doc["sections"]:
                    heading_hits = [t for t in concept["terms"] if contains(section["breadcrumb"], t)]
                    title_hits = [t for t in concept["terms"] if contains(doc["title"], t)]
                    if not heading_hits and not title_hits:
                        continue
                    score = 3 * len(heading_hits) + len(title_hits)
                    candidates.append((score, doc, section, list(dict.fromkeys(heading_hits + title_hits))))
            out = [f"# {concept['title']}", "", "自动主题地图：按标题/章节中的术语归组。关联仅表示主题邻近，不表示技术等价。", "",
                   "路由词：" + "、".join(concept["terms"]), "", "## 来源入口", ""]
            grouped = defaultdict(list)
            for candidate in sorted(candidates, key=lambda c: (-c[0], c[1]["path"], c[2]["start"])):
                grouped[candidate[1]["path"]].append(candidate)
            for path, matches in grouped.items():
                doc = matches[0][1]
                out += [f"### [{doc['title']}](../notes/{doc['id']}.md)", "", f"来源：`{path}` · SHA-256 `{doc['sha256'][:12]}`", ""]
                for _, _, section, hits in matches[:4]:
                    label = "〔未填写〕" if section["empty"] else ""
                    out += [f"- L{section['start']}-L{section['end']} · {section['breadcrumb']} {label}".rstrip()]
                    if section["excerpt"]:
                        out += excerpt_block(section["excerpt"])
                if len(matches) > 4:
                    out += [f"- 其余 {len(matches) - 4} 个相关章节见来源卡片。"]
                out += [""]
            out += ["## 相邻主题", ""]
            titles = {c["id"]: c["title"] for c in config["concepts"]}
            out += [f"- [{titles[c]}]({c}.md)" for c in concept["related"]]
            out += ["", "## 检索入口", "", "```powershell",
                    f'python LLMWiki/wiki.py search "{concept["terms"][0]}"', "```", ""]
            files[f"generated/concepts/{concept['id']}.md"] = "\n".join(out)
        index += ["", "## 按领域定位", ""]
        for domain, members in sorted(domains.items()):
            domain_id = short_id("area_", domain)
            index += [f"- [{domain}](generated/domains/{domain_id}.md)：{len(members)} 篇"]
            out = [f"# {domain}", "", "所有条目均链接到来源卡片。", ""]
            for doc in members:
                overview = "；".join(s["heading"] for s in doc["sections"] if s["level"] in {1, 2})[:200].rstrip()
                out += [f"- [{doc['title']}](../notes/{doc['id']}.md) · {len(doc['sections'])} 个章节",
                        f"  - `{doc['path']}`", f"  - 目录摘录：{overview}"]
            files[f"generated/domains/{domain_id}.md"] = "\n".join(out) + "\n"
        files["INDEX.md"] = "\n".join(index) + "\n"
        files["generated/catalogue.json"] = json_text(catalogue)
        files["generated/links.json"] = json_text(links)
        issues = [{"path": d["path"], **issue} for d in docs for issue in d["issues"]]
        audit = {"notes": len(docs), "sections": sum(len(d["sections"]) for d in docs),
                 "chunks": con.execute("SELECT count(*) FROM chunks").fetchone()[0],
                 "source_bytes": sum(d["bytes"] for d in docs),
                 "local_images": sum(Path(a).suffix.lower() in IMAGE_EXT for a in signature["assets"]),
                 "issue_counts": dict(Counter(i["kind"] for i in issues)), "source_issues": issues,
                 "metadata_issues": metadata_issues, "link_warnings": link_warnings,
                 "limitations": ["图片/附件仅索引引用和路径，不做 OCR，不推断图中事实。",
                                 "不检查外部 URL 内容或可用性。", "原笔记的技术断言未经外部事实核查。",
                                 "源文档有冲突时保留各自证据，检索排序不裁决真伪。"]}
        files["generated/audit.json"] = json_text(audit)
        # 只删除此前由本模块拥有的生成文件；绝不扫描删除源笔记或手写页面。
        old_marker = self.generated / "manifest.json"
        old_files = []
        if old_marker.exists():
            try:
                old_files = json.loads(old_marker.read_text(encoding="utf-8"))["generated_files"]
            except (ValueError, KeyError):
                pass
        for path, text in files.items():
            destination = self.home / path
            if not destination.resolve().is_relative_to(self.home.resolve()):
                raise ValueError("生成路径越界")
            atomic_write(destination, text)
        for rel in set(old_files) - set(files):
            p = self.home / rel
            if p.resolve().is_relative_to(self.generated.resolve()):
                p.unlink(missing_ok=True)
        manifest = {"signature": signature, "built_at_utc": datetime.now(timezone.utc).isoformat(),
                    "generated_files": sorted(files),
                    "generated_hashes": {p: digest(t.encode("utf-8")) for p, t in sorted(files.items())},
                    "notes": len(docs), "chunks": audit["chunks"]}
        atomic_write(old_marker, json_text(manifest))  # 最后发布，失败时下一次会重新导出。

    def groups(self, query, config):
        """最长术语优先；未识别词保留。只移除少量疑问句连接词。"""
        remaining = norm(query)
        found = []
        variants = sorted(((norm(v), group) for group in config["aliases"] for v in group), key=lambda v: -len(v[0]))
        for variant, group in variants:
            if not contains(remaining, variant):
                continue
            left = r"(?<![a-z0-9_])" if re.match(r"[a-z0-9_]", variant) else ""
            right = r"(?![a-z0-9_])" if re.search(r"[a-z0-9_]$", variant) else ""
            remaining, count = re.subn(left + re.escape(variant) + right, " ", remaining)
            if count and group not in found:
                found.append(group)
        stop = r"^(?:请问|请|为什么|什么是|如何|怎么|的|与|和|及|有什么|一个|在|中)+|(?:怎么解决|的区别|有什么区别|是什么|怎么办|如何解决|吗|呢|的)+$"
        for word in WORD.findall(remaining):
            word = re.sub(stop, "", word)
            if word and word not in {"what", "is", "how", "the", "and"}:
                found.append([word])
        return found

    def _search(self, query, limit, scope, literal):
        config = json.loads((self.home / "config.json").read_text(encoding="utf-8"))
        groups = [[norm(query)]] if literal else self.groups(query, config)
        if not groups:
            return {"query": query, "groups": [], "hits": [], "message": "查询没有可检索的词。"}
        con = self.connect()
        try:
            con.execute("BEGIN")  # 候选和来源哈希必须来自同一 SQLite 快照。
            docs_meta = {r[0]: json.loads(r[1]) for r in con.execute("SELECT path,data FROM docs")}
            patterns = {v: term_pattern(norm(v)) for group in groups for v in group}
            scoped = " AND instr(c.path, ?) > 0" if scope else ""
            if literal:
                rows = con.execute("SELECT c.*, 0.0 AS rank FROM chunks c WHERE 1=1" + scoped, (scope,) if scope else ()).fetchall()
            else:
                group_expr = []
                for group in groups:
                    variants = []
                    for variant in group:
                        tokens = query_terms(variant)
                        if tokens:
                            variants.append("(" + " AND ".join('"' + t.replace('"', '""') + '"' for t in tokens) + ")")
                    if variants:
                        group_expr.append("(" + " OR ".join(variants) + ")")
                if not group_expr:
                    return {"query": query, "groups": groups, "hits": []}
                # 严格召回优先，随后显式部分召回；不在重排前截断候选，避免漏掉精确证据。
                expression = " OR ".join(group_expr)
                rows = con.execute("""SELECT c.*, bm25(search,2,5,3,1) AS rank
                    FROM search JOIN chunks c ON c.rowid=search.rowid WHERE search MATCH ?""" + scoped,
                                   (expression, scope) if scope else (expression,)).fetchall()
            hits = []
            for row in rows:
                item = dict(row)
                body_lines = item["body"].splitlines()
                _, fm_end = frontmatter(body_lines) if item["start"] == 1 else ({}, 0)
                prose_body = norm("\n".join(line for line in body_lines[fm_end:] if not HEADING.match(line)))
                fields = [norm(item[name]) for name in ("heading", "body", "title", "aliases")]
                matched, evidence, points = [], [], 0
                for group in groups:
                    matches = [v for v in group if any(patterns[v].search(field) for field in fields)]
                    if not matches:
                        continue
                    matched.append(group[0])
                    direct = [v for v in matches if patterns[v].search(prose_body)]
                    evidence.extend(direct)
                    points += max((12 if patterns[v].search(fields[0]) else 0)
                                  + (6 if patterns[v].search(prose_body) else 0)
                                  + (3 if patterns[v].search(fields[2]) else 0) for v in matches)
                if not matched:
                    continue  # 双字散落出现不等同于词语证据。
                full = len(matched) == len(groups)
                if literal and not full:
                    continue
                body = item["body"]
                snippet_start = 0
                for line in body.splitlines(keepends=True):
                    if any(patterns[v].search(norm(line)) for v in evidence):
                        break
                    snippet_start += len(line)
                if snippet_start >= len(body):
                    snippet_start = 0
                excerpt = body[snippet_start:snippet_start + 420]
                reason = "all_terms" if full else "partial_terms"
                if not evidence:
                    reason += "_metadata_only"
                doc = docs_meta[item["path"]]
                names = {norm(a) for a in [doc["title"], *doc["aliases"]]}
                # 完整文件名/题号/slug 优先；限定了笔记名的查询在该笔记内优先查找。
                route = 2 if norm(query) in names else int(any(norm(v) in names for group in groups for v in group))
                hits.append({"id": item["id"], "path": item["path"], "title": item["title"], "heading": item["heading"],
                             "start": item["start"], "end": item["end"], "match": reason,
                             "matched_groups": matched, "body_evidence": list(dict.fromkeys(evidence)),
                             "empty": bool(item["empty"]), "image_only": bool(item["image_only"]),
                             "excerpt": excerpt + (" …〔截断〕" if snippet_start + 420 < len(body) else ""),
                             "_sort": (int(full), len(matched) / len(groups), route, int(bool(evidence)),
                                       int(not item["empty"]), points, -item["rank"])})
            # 有完整命中时不填入仅命中一部分查询词的噪声结果。
            if any(h["_sort"][0] for h in hits):
                hits = [h for h in hits if h["_sort"][0]]
            hits.sort(key=lambda h: (tuple(-v for v in h["_sort"]), h["path"], h["start"]))
            selected = []
            for hit in hits:
                # 邻接重叠块去重；同一文件的不同章节仍可同时出现。
                if any(hit["path"] == prev["path"] and min(hit["end"], prev["end"]) - max(hit["start"], prev["start"]) >= 0
                       for prev in selected):
                    continue
                selected.append(hit)
                if len(selected) >= limit:
                    break
            for hit in selected:
                hit.pop("_sort")
                sha = docs_meta[hit["path"]]["sha256"]
                if digest((self.root / hit["path"]).read_bytes()) != sha:
                    raise RuntimeError("SOURCE_CHANGED")
                hit["sha256"] = sha
                hit["citation"] = f"{hit['path']}:L{hit['start']}-L{hit['end']}"
                hit["verified"] = True
            return {"query": query, "groups": groups, "candidate_chunks": len(rows), "hits": selected,
                    "message": "partial_terms 仅供继续查找；metadata_only 仅是导航。未找到不代表知识不存在。"}
        finally:
            con.close()

    def search(self, query, limit=5, scope=None, literal=False):
        if not query.strip() or not 1 <= limit <= 50:
            raise ValueError("查询不能为空，limit 必须在 1 到 50 之间")
        if len(query) > 500:
            raise ValueError("查询过长；请拆成几个主题，每次使用 2–5 个关键词")
        started = time.perf_counter()
        for attempt in range(2):
            refresh = self.update()
            try:
                result = self._search(query, limit, scope, literal)
                result["refresh"] = {"changed": len(refresh["changed"]), "deleted": len(refresh["deleted"])}
                result["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 2)
                return result
            except (FileNotFoundError, RuntimeError) as error:
                if attempt or (isinstance(error, RuntimeError) and str(error) != "SOURCE_CHANGED"):
                    raise
        raise RuntimeError("源文件持续变化，请稍后重试")

    def read(self, target, start=None, end=None, context=0):
        self.update()
        con = self.connect()
        try:
            con.execute("BEGIN")
            row = con.execute("SELECT * FROM chunks WHERE id=?", (target,)).fetchone()
            path = row["path"] if row else target.replace("\\", "/")
            doc_row = con.execute("SELECT data FROM docs WHERE path=?", (path,)).fetchone()
            if not doc_row:
                raise ValueError("找不到此来源或块 ID。源文件修改后旧 ID 可能失效，请重新 search。")
            doc = json.loads(doc_row[0])
            raw = (self.root / path).read_bytes()
            if digest(raw) != doc["sha256"]:
                raise RuntimeError("读取时源文件发生变化，请重新执行 read。")
            lines = raw.decode("utf-8-sig").splitlines()
            if not lines and start is None and end is None and context >= 0:
                return {"path": path, "start": 0, "end": 0, "sha256": doc["sha256"], "verified": True,
                        "citation": path + "〔空文件〕", "text": "", "total_lines": 0}
            first = start if start is not None else (row["start"] if row else 1)
            last = end if end is not None else (row["end"] if row else min(len(lines), first + 119))
            if context < 0 or first < 1 or last < first or last > len(lines):
                raise ValueError(f"行号超出范围，文件共 {len(lines)} 行")
            first, last = max(1, first - context), min(len(lines), last + context)
            return {"path": path, "start": first, "end": last, "sha256": doc["sha256"], "verified": True,
                    "citation": f"{path}:L{first}-L{last}",
                    "text": "\n".join(lines[first - 1:last]), "total_lines": len(lines)}
        finally:
            con.close()

    def status(self):
        _, sources, _, _, signature = self.snapshot()
        path = self.generated / "manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        previous = manifest.get("signature", {})
        return {"fresh": signature == previous and self.db_path.exists() and self.generated_ok(signature),
                "notes": len(sources), "changed": [p for p, sha in signature["sources"].items() if previous.get("sources", {}).get(p) != sha],
                "deleted": sorted(set(previous.get("sources", {})) - set(sources)),
                "config_changed": signature.get("config") != previous.get("config"),
                "engine_changed": signature.get("engine") != previous.get("engine"),
                "metadata_changed": signature.get("leetcode") != previous.get("leetcode"),
                "built_at_utc": manifest.get("built_at_utc")}

    def verify(self):
        self.update()
        con = self.connect()
        try:
            errors, coverage = [], defaultdict(set)
            integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
            if integrity != "ok":
                errors.append(integrity)
            con.execute("INSERT INTO search(search) VALUES('integrity-check')")
            docs = {r[0]: json.loads(r[1]) for r in con.execute("SELECT path,data FROM docs")}
            sources = {p: (self.root / p).read_bytes() for p in docs}
            lines = {p: raw.decode("utf-8-sig").splitlines() for p, raw in sources.items()}
            for p, doc in docs.items():
                if digest(sources[p]) != doc["sha256"]:
                    errors.append("source_changed:" + p)
            count = 0
            for row in con.execute("SELECT * FROM chunks"):
                count += 1
                original = "\n".join(lines[row["path"]][row["start"] - 1:row["end"]])
                if original != row["body"]:
                    errors.append("chunk_mismatch:" + row["id"])
                coverage[row["path"]].update(range(row["start"], row["end"] + 1))
            for path, content in lines.items():
                if any(line.strip() and i not in coverage[path] for i, line in enumerate(content, 1)):
                    errors.append("uncovered_lines:" + path)
            search_count = con.execute("SELECT count(*) FROM search").fetchone()[0]
            if search_count != count:
                errors.append("fts_count_mismatch")
            manifest = json.loads((self.generated / "manifest.json").read_text(encoding="utf-8"))
            for rel in manifest["generated_files"]:
                file = self.home / rel
                if not file.exists():
                    errors.append("missing_generated:" + rel)
                elif file.suffix == ".json":
                    json.loads(file.read_text(encoding="utf-8"))
                if file.exists() and digest(file.read_bytes()) != manifest["generated_hashes"].get(rel):
                    errors.append("generated_content_changed:" + rel)
            return {"ok": not errors, "notes": len(docs), "verified_chunks": count,
                    "all_nonblank_source_lines_covered": not any(e.startswith("uncovered_lines:") for e in errors), "errors": errors}
        finally:
            con.close()


def evaluate(wiki, write_report=False):
    cases = json.loads((wiki.home / "evaluation.json").read_text(encoding="utf-8"))
    outcomes, times = [], []
    for case in cases:
        result = wiki.search(case["query"], limit=5, scope=case.get("scope"))
        def correct(hit):
            return (hit["path"].endswith(case["path"]) and
                    (not case.get("heading") or case["heading"] in hit["heading"]) and
                    (not case.get("evidence") or case["evidence"] in wiki.read(hit["id"])["text"]))
        rank = next((i for i, hit in enumerate(result["hits"], 1) if correct(hit)), None)
        passed = not result["hits"] if case.get("absent") else rank is not None
        times.append(result["elapsed_ms"])
        outcomes.append({"query": case["query"], "pass": passed, "rank": rank,
                         "top": [{"path": h["path"], "heading": h["heading"], "match": h["match"]} for h in result["hits"]]})
    sorted_times = sorted(times)
    report = {"cases": len(cases), "passed": sum(r["pass"] for r in outcomes),
              "positive_cases": sum(not c.get("absent") for c in cases),
              "top1": sum(r["rank"] == 1 for r in outcomes),
              "top5": sum(r["rank"] is not None for r in outcomes),
              "latency_ms_including_refresh_and_source_verification": {
                  "median": round(statistics.median(times), 2),
                  "p95": sorted_times[max(0, math.ceil(len(times) * 0.95) - 1)], "max": max(times)},
              "limitations": "固定本地回归样例，不代表所有自然语言问题的准确率；计时不含 Python 进程启动。",
              "source_signature": json.loads((wiki.generated / "manifest.json").read_text(encoding="utf-8"))["signature"],
              "outcomes": outcomes}
    if write_report:
        with wiki.lock():
            atomic_write(wiki.generated / "evaluation-report.json", json_text(report))
    return report


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    update = commands.add_parser("update", help="增量更新；始终校验内容哈希")
    update.add_argument("--rebuild", action="store_true", help="重新解析全部源文件")
    search = commands.add_parser("search", help="检索来源章节；自动更新并验证命中内容")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=5)
    search.add_argument("--scope", help="来源路径的字面子串，例如 04-AI 或 Redis.md")
    search.add_argument("--literal", action="store_true", help="只返回含完整连续字串的来源，不扩展同义词")
    read = commands.add_parser("read", help="按块 ID 或源文件相对路径读取真实原文")
    read.add_argument("target")
    read.add_argument("--start", type=int)
    read.add_argument("--end", type=int)
    read.add_argument("--context", type=int, default=0)
    commands.add_parser("status", help="检查是否需要更新，不创建或更新索引")
    commands.add_parser("verify", help="检查 SQLite、原文行号、分块覆盖和生成文件")
    evaluation = commands.add_parser("eval", help="运行人工选择的检索回归样例")
    evaluation.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    wiki = Wiki()
    try:
        if args.command == "update":
            result = wiki.update(args.rebuild)
        elif args.command == "search":
            result = wiki.search(args.query, args.limit, args.scope, args.literal)
        elif args.command == "read":
            result = wiki.read(args.target, args.start, args.end, args.context)
        elif args.command == "status":
            result = wiki.status()
        elif args.command == "verify":
            result = wiki.verify()
        else:
            report = evaluate(wiki, args.write_report)
            result = {k: v for k, v in report.items() if k not in {"source_signature", "outcomes"}}
            result["failures"] = [r for r in report["outcomes"] if not r["pass"]]
            if args.write_report:
                result["report"] = "LLMWiki/generated/evaluation-report.json"
        print(json_text(result), end="")
        return int((args.command == "verify" and not result["ok"]) or
                   (args.command == "eval" and result["passed"] != result["cases"]))
    except (ValueError, OSError, RuntimeError, sqlite3.Error) as error:
        print(json_text({"error": str(error)}), file=sys.stderr, end="")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
