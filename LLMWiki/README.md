# LLMWiki

这是原 Obsidian 仓库的独立派生 Wiki，供 LLM 定位、读取和引用已有知识。所有新增内容都放在 `LLMWiki/`，工具对原笔记、附件及 Obsidian 配置只读。无需联网、API Key、外部模型或第三方 Python 包。

入口：[主题与领域导航](INDEX.md) · [LLM 使用规则](AGENTS.md) · [来源目录](generated/catalogue.json) · [资料质量报告](generated/audit.json)

## 使用

需要 Python 3.10+，以及带 FTS5 的 SQLite。以下命令在仓库根目录运行；也可以在任意目录使用脚本的绝对路径，仓库位置由脚本位置确定。

```powershell
# 首次构建，或手动增量更新
python LLMWiki/wiki.py update

# 建议使用 2–5 个关键词，可加入笔记名缩小范围
python LLMWiki/wiki.py search "Redis 缓存击穿"
python LLMWiki/wiki.py search "多版本并发控制"
python LLMWiki/wiki.py search "MCP" --scope "04-AI/Agent.md"
python LLMWiki/wiki.py search "LeetCode 146"

# 保留连续字串，不扩展术语别名
python LLMWiki/wiki.py search "ReadView" --literal

# 从 search 的 hits 中取 id，读取完整证据块
python LLMWiki/wiki.py read "c_替换为实际块ID" --context 3

# 也可以直接读取来源路径与行号
python LLMWiki/wiki.py read "01-计算机基础/数据库/Redis.md" --start 566 --end 582
```

输出统一为 UTF-8 JSON。`read` 的 `text` 是实际源文件在所列行号范围内的文本，仅将换行规范为 `\n`。`sha256` 是原始文件字节的 SHA-256，`verified: true` 表示读取时内容与索引匹配。一次查询最多返回 50 条，默认 5 条。

`search` 和 `read` 都会自动检查并更新索引，不必记得先执行 `update`。首次使用、删除缓存、工具或配置变化时会自动全量解析。源文件未变化时不会重写生成页面。

## 检索结果如何使用

| 字段 | 含义 |
| --- | --- |
| `path`、`start`、`end`、`citation` | 原文路径与从 1 开始的行号，允许直接回溯 |
| `heading` | 当前章节及其祖先标题，提供上下文 |
| `all_terms` | 每组查询词至少有一个别名在标题、正文或文档元数据中连续命中 |
| `partial_terms` | 只匹配部分查询词，仅在没有完整命中时返回，需要拆词或调整范围继续查找 |
| `*_metadata_only` | 查询词只命中标题、文件名、别名等，先作为导航，读取后判断是否包含答案 |
| `matched_groups`、`body_evidence` | 实际匹配的词组，以及在非标题正文中命中的原始术语 |
| `empty`、`image_only` | 原章节未填写或仅有图片，不据此补写事实 |
| `excerpt` | 定位用片段，可能从章节中部开始，并明确标记截断 |

检索命中与答案正确是两回事。回答时先 `read`，引用原笔记与行号；有冲突则保留各来源的不同说法。原文没有答案时明确说材料不足，不能将排序分数或别名扩展当作事实依据。

未命中时依次尝试：减少关键词、改用同义表达、按主题地图定位、指定来源范围。自然语言理解采用有限的术语表和疑问词处理；不具备任意语义改写或拼写纠错能力。必要时针对已定位的少量原文进行补充搜索。

## 文件布局

| 位置 | 作用 | 更新方式 |
| --- | --- | --- |
| `INDEX.md` | 主题和领域的总入口 | 自动生成 |
| `generated/notes/` | 每篇笔记的标题树、来源哈希、行号、原文摘录 | 自动生成 |
| `generated/concepts/` | 跨笔记主题地图，包含来源证据入口和相邻主题 | 自动生成 |
| `generated/domains/` | 各领域的笔记目录 | 自动生成 |
| `generated/catalogue.json` | 文档、章节、题号、英文 slug 与块 ID 的机器目录 | 自动生成 |
| `generated/links.json` | 笔记链接与附件引用的解析结果 | 自动生成 |
| `generated/audit.json` | 空章节、图片、重复标题及待检查链接 | 自动生成 |
| `generated/manifest.json` | 工具、配置、源文件和生成文件的哈希与构建清单 | 自动生成 |
| `config.json` | 检索别名、主题地图与排除规则 | 人工维护 |
| `evaluation.json` | 独立选择的检索回归样例与预期证据 | 人工维护 |
| `generated/evaluation-report.json` | 上次回归结果、对应源版本与耗时 | `eval --write-report` |
| `.cache/search.sqlite` | SQLite FTS5 倒排索引与精确原文分块 | 自动生成，可丢弃，Git 忽略 |
| `tests/` | 临时仓库中的行为验证 | 修改工具时运行 |

主题地图按文档名和章节术语归组，邻近主题只是导航关系。卡片摘录保留原文，不把自动归类写成技术结论。原文中的代码、图片引用和文章存档都保留自己的来源身份。

## 可持续更新

日常只需继续在原仓库写笔记。新增、修改、删除、移动会在下次检索时同步；已删除或移动笔记的旧卡片和索引会被清除。块 ID 包含路径、行号和原文内容，源文件变化后旧 ID 可能失效，应重新检索。

```powershell
python LLMWiki/wiki.py status
python LLMWiki/wiki.py update
python LLMWiki/wiki.py verify

# 修改检索工具或术语表之后
python -X utf8 -m unittest discover -s LLMWiki/tests -v
python LLMWiki/wiki.py eval --write-report

# 重新解析全部源文件、恢复手动改坏的生成页面
python LLMWiki/wiki.py update --rebuild
```

增加别名时编辑 `config.json` 的 `aliases`，每个数组为一组检索表达，允许只含一个词来帮助中文问题分词。别名只用于召回，不表示表达在所有技术上下文下完全等价。增加主题时编辑 `concepts`，给出稳定 `id`、中文 `title`、`terms` 和已有的 `related` ID。两者下次查询都会自动生效。

增加重要知识领域时，同时在 `evaluation.json` 加入真实查询、预期来源和可核对的章节/证据。用 `verify` 检查来源覆盖、精确行号、SQLite 一致性以及生成文件是否被改动；用 `eval` 检查查询能否找对证据。测试仅在系统临时目录创建示例仓库，不修改实际源文件。

不要手改自动生成页面，重建会覆盖它们。需要独立手写的补充说明可放在 `LLMWiki/` 下的新目录中；这些内容默认不进入来源索引，避免派生内容循环证明自身。调整解析逻辑时保留回归样例；如将来变更 SQLite 表结构，可删除 `.cache/search.sqlite` 后由 `update` 从原文重建。

## 准确性与速度

1. **内容校验**：每次检索都扫描源 Markdown 并校验 SHA-256，不仅依赖修改时间和文件大小，因此同大小、同时间戳的修改也能识别。返回结果前再次核对命中文档；候选与文档哈希来自同一个 SQLite 快照。
2. **少读原文**：按标题拆章，长章节保留重叠行；索引完整保留正文与代码。先读小规模导航，再只读取相关块，不把整个仓库塞进上下文。
3. **本地倒排**：中文单字/双字索引与英文标识符检索，结合标题、正文、文档名和别名重排。查询严格使用参数绑定；缩写、数字采用英文标识符边界，避免 `CAS` 命中 `case`、题号 `1` 命中 `121`。
4. **先完整匹配**：存在全部查询词命中的结果时不混入部分匹配；按完整文档名、题号或 slug 提供的定位意图优先。保留各章节出处，支持后续对比。
5. **不截断候选再重排**：先对符合倒排条件的候选检查真实连续词语，再选结果，避免中文双字散落或候选上限造成漏排。

耗时见[回归报告](generated/evaluation-report.json)。报告包含内容检查及命中核对的耗时，不包含 Python 进程启动。它只衡量固定样例，不能证明任意查询百分之百准确。未来仓库显著增大时，应先用同一批回归样例衡量，再决定是否加入向量召回；当前实现不依赖外部向量服务。

更新锁使多个进程的写入串行；SQLite 以事务更新，页面采用临时文件替换。异常退出若留下 `.cache/update.lock`，须先确认没有 `wiki.py` 进程再删除该锁。持续修改中的来源会触发重试或明确报错，工具不会悄悄返回已知过期的结果。

## 收录范围与资料缺口

- 收录仓库内非隐藏目录中的 `.md` / `.markdown`。`LLMWiki/`、各级隐藏目录、符号链接、`AGENTS.md` 和 Obsidian/代理配置不作为知识来源，避免自我索引和混入工具指令。
- 读取原有 LeetCode 索引，为题目补充题号和英文 slug；该索引本身保持只读。
- 附件和图片仅记录路径及引用，不做 OCR；外部 URL 不抓取、不验证可用性。
- Markdown 解析覆盖标题、常见 frontmatter、代码围栏、常见 Wiki/Markdown/HTML 链接。链接检查属于候选检查，不能替代完整 Obsidian 渲染；复杂语法和模板占位符可能需人工确认。
- 既有技术错误、未填章节、参考资料版本差异不会在派生 Wiki 中自动修正。可以查看质量报告定位原文，但本次任务不会回写源笔记。
