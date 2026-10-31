# 数据库、事务与持久化

自动主题地图：按标题/章节中的术语归组。关联仅表示主题邻近，不表示技术等价。

路由词：事务、MVCC、InnoDB、Redo、binlog、持久化、索引

## 来源入口

### [MySQL](../notes/d_e2efd3502aca378b01a130c4.md)

来源：`01-计算机基础/数据库/MySQL.md` · SHA-256 `160f2e5aeae1`

- L541-L551 · 六、InnoDB > (二) MVCC > 1. 聚簇索引记录的隐藏列

  摘录（原文）：

  ```text
  - 旧版本数据写入 Undo log 中，聚簇索引中最新记录的 roll_ptr 指向 Undo log 中的旧版本，每个版本不断指向前一个旧版本形成版本链。
  ```

- L537-L540 · 六、InnoDB > (二) MVCC

  摘录（原文）：

  ```text
  - 多版本并发控制指维护一个数据的多个版本，使得快照读和写操作之间没有冲突。MVCC 的实现依赖于数据库记录的 3 个隐藏字段、Undo log 日志、ReadView。
  ```

- L552-L570 · 六、InnoDB > (二) MVCC > 2. ReadView

  摘录（原文）：

  ```text
  - 只由快照读生成，ReadView 中只有 4 个字段。每次查询记录时，根据记录的 trx_id 和字段值按如下规则判断是否可见。如果不可见，则顺着版本链向前找到第一个 trx_id<min_trx_id 的旧版本。
  ```

- L571-L583 · 六、InnoDB > (二) MVCC > 3. Undo log

  摘录（原文）：

  ```text
  - Undo log 是**逻辑日志**，记录事务修改前的数据状态，作用包含两个 : 支持**回滚**（保证事务的**原子性**）和 **MVCC** (多版本并发控制) 。
  ```

- 其余 44 个相关章节见来源卡片。

### [Redis](../notes/d_7d7f123eef9acac2e14eb914.md)

来源：`01-计算机基础/数据库/Redis.md` · SHA-256 `2f901c5fe849`

- L35-L36 · 一、Redis 基础 > (三) 事务
- L37-L42 · 一、Redis 基础 > (三) 事务 > 1. 原子性

  摘录（原文）：

  ```text
  - Redis 执行单个命令是原子性的，执行多个命令可以通过 Lua 脚本实现原子性。
  ```

- L43-L56 · 一、Redis 基础 > (三) 事务 > 2. 事务

  摘录（原文）：

  ```text
  - Redis 可以用通过在一组命令前后增加`MULTI`、`EXEC`命令开启事务。
  ```

- L349-L350 · 四、Redis 持久化
- 其余 3 个相关章节见来源卡片。

### [Java 集合](../notes/d_d407c5c86714794b939abcf9.md)

来源：`02-Java 后端/Java 集合.md` · SHA-256 `b3fdb2e3a407`

- L17-L18 · 二、单列集合 Collection > (二) List：有序、可重复、有索引
- L19-L22 · 二、单列集合 Collection > (二) List：有序、可重复、有索引 > 1. 遍历 List

  摘录（原文）：

  ```text
  ① Iterator；② ListIterator；③ 增强 for；④ forEach；⑤ 普通 for。
  ```

- L23-L27 · 二、单列集合 Collection > (二) List：有序、可重复、有索引 > 1. 遍历 List > 一、列表迭代器 ListIterator

  摘录（原文）：

  ```text
  - 可以正向遍历，也能反向遍历，游标默认初始化。
  ```

- L28-L33 · 二、单列集合 Collection > (二) List：有序、可重复、有索引 > 1. 遍历 List > 二、List 遍历的最佳实践

  摘录（原文）：

  ```text
  - 简单读取：增强 for、普通 for（只适合实现了 RandomAccess 接口的类如 ArrayList、Vector）。
  ```

- 其余 23 个相关章节见来源卡片。

### [Spring](../notes/d_aeac005e2a534eb58b3eeb1d.md)

来源：`02-Java 后端/Spring.md` · SHA-256 `19e910c663fe`

- L104-L108 · 一、Spring 框架 > (四) Spring 事务

  摘录（原文）：

  ```text
  1. 编程式事务：基于 TranasctionTemplate、PlatformTransactionManager 等接口，在代码中手动实现事务的开启、提交、回滚等。
  ```

- L109-L120 · 一、Spring 框架 > (四) Spring 事务 > 1. 事务传播行为

  摘录（原文）：

  ```text
  - 控制多个**事务方法嵌套**调用时的事务行为，避免事务不⼀致、数据丢失、重复提交等问题，保证一致性、完整性。
  ```

- L121-L131 · 一、Spring 框架 > (四) Spring 事务 > 2. 事务失效

  摘录（原文）：

  ```text
  1. **数据库引擎不支持事务**：Mysql 的 InnoDB 支持事务，但是 MyISAM 等不支持事务。
  ```


### [分布式系统](../notes/d_3b0a4e7f68c3a64106febc8b.md)

来源：`03-系统设计/分布式系统.md` · SHA-256 `0d1959eeec2e`

- L124-L125 · 四、分布式事务

  摘录（原文）：

  ```text
  - 简单来说，业务代码涉及到跨多台服务器或多个微服务，就必须保证**跨节点**的操作：要么全部成功，要么全部失败。
  ```

- L126-L133 · 四、分布式事务 > (一) AT 模式 (Automatic Transaction)

  摘录（原文）：

  ```text
  - 核心目标是尽量少的改动业务代码，提供最终一致性。简单理解就是“自动补偿”：业务仍然执行本地事务，但是框架会记录回滚需要的信息。
  ```

- L134-L138 · 四、分布式事务 > (二) XA 模式

  摘录（原文）：

  ```text
  - **AP (Application Program)**：应用程序，负责**发起**分布式事务。
  ```

- L139-L154 · 四、分布式事务 > (二) XA 模式 > 1. 二阶段提交 2PC (强一致性)

  摘录（原文）：

  ```text
  1. 2PC 过程
  ```

- 其余 3 个相关章节见来源卡片。

### [消息队列](../notes/d_958bc15a9d31ad77abe7545d.md)

来源：`03-系统设计/消息队列.md` · SHA-256 `79b64b6c2e32`

- L89-L96 · 四、事务消息

  摘录（原文）：

  ```text
  - RocketMQ 事务消息通过 **TransactionListener** 接口实现事务消息。
  ```


### [LLM 与 RAG](../notes/d_fcc04285c9673f6c94c4fdb6.md)

来源：`04-AI/LLM 与 RAG.md` · SHA-256 `d93ce8348aa0`

- L205-L228 · 二、RAG (**Retrieval-Augmented Generation 检索增强生成**) > (五) 向量数据库 > 1. ANN 索引(Approximate Nearest Neighbor，近似最近邻搜索)

  摘录（原文）：

  ```text
  1. **分层可导航小世界图 HNSW**
  ```


### [design](../notes/d_00a19d84e16555709c696358.md)

来源：`09-unachive/design.md` · SHA-256 `9b98ffc79a81`

- L735-L769 · nanobot 精简复现版设计文档 > 12. 持久化设计

  摘录（原文）：

  ```text
  目录结构：
  ```


### [detailed-design](../notes/d_92b442e574fb14453e3673eb.md)

来源：`09-unachive/detailed-design.md` · SHA-256 `067bc65c6044`

- L739-L770 · nanobot 详细设计文档 > 17. 持久化数据清单

## 相邻主题

- [缓存、淘汰与一致性](cache.md)
- [分布式、消息与项目实践](distributed.md)

## 检索入口

```powershell
python LLMWiki/wiki.py search "事务"
```
