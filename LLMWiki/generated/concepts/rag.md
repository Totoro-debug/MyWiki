# LLM、RAG 与检索

自动主题地图：按标题/章节中的术语归组。关联仅表示主题邻近，不表示技术等价。

路由词：LLM、RAG、Embedding、检索、分块、Rerank、幻觉、向量

## 来源入口

### [LLM 与 RAG](../notes/d_fcc04285c9673f6c94c4fdb6.md)

来源：`04-AI/LLM 与 RAG.md` · SHA-256 `d93ce8348aa0`

- L179-L180 · 二、RAG (**Retrieval-Augmented Generation 检索增强生成**) > (四) 向量化与 Embedding 模型
- L181-L184 · 二、RAG (**Retrieval-Augmented Generation 检索增强生成**) > (四) 向量化与 Embedding 模型 > 1. 向量化

  摘录（原文）：

  ```text
  - 向量化就是将一段自然语言文本映射成一个固定长度的浮点数向量（1024、1536、2048）。
  ```

- L185-L196 · 二、RAG (**Retrieval-Augmented Generation 检索增强生成**) > (四) 向量化与 Embedding 模型 > 2. Embedding 模型

  摘录（原文）：

  ```text
  - 语言支持
  ```

- L197-L200 · 二、RAG (**Retrieval-Augmented Generation 检索增强生成**) > (四) 向量化与 Embedding 模型 > 3. 评测 Embedding 模型

  摘录（原文）：

  ```text
  - `**Hit@K**`：准备 <问题, 正确 chunk> 数据集，用候选模型测试，看正确的 chunk 是否出现在前 K 条结果中。
  ```

- 其余 59 个相关章节见来源卡片。

## 相邻主题

- [Agent、工具与记忆](agent.md)
- [缓存、淘汰与一致性](cache.md)

## 检索入口

```powershell
python LLMWiki/wiki.py search "LLM"
```
