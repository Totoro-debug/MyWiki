# 缓存、淘汰与一致性

自动主题地图：按标题/章节中的术语归组。关联仅表示主题邻近，不表示技术等价。

路由词：缓存、Cache、LRU、LFU、Buffer Pool、MESI

## 来源入口

### [146. LRU 缓存](../notes/d_793fe9dbe18314ecf125295d.md)

来源：`08-LeetCode/链表/146. LRU 缓存.md` · SHA-256 `8a7a9e5b5c6a`

- L1-L120 · 146. LRU 缓存

  摘录（原文）：

  ```text
  **原题链接**：[146. LRU 缓存](https://leetcode.cn/problems/lru-cache/description/?envType=study-plan-v2&envId=top-100-liked)
  ```


### [操作系统](../notes/d_30c43c00efdd876efcdd627e.md)

来源：`01-计算机基础/操作系统.md` · SHA-256 `3099a35b4b68`

- L7-L11 · 一、系统结构 > (一) CPU 高速缓存 > 1. Cache 与内存一致性

  摘录（原文）：

  ```text
  - **写直达 (Write Through)**：每次写操作都将数据同时写入 Cache 和内存。
  ```

- L25-L32 · 一、系统结构 > (一) CPU 高速缓存 > 4. MESI 协议

  摘录（原文）：

  ```text
  - MESI 协议将缓存行分为 4 个状态：**修改 Modified、独占 Exclusive、共享 Shared、失效 Invalid**。
  ```

- L3-L6 · 一、系统结构 > (一) CPU 高速缓存

  摘录（原文）：

  ```text
  - Cache：L1 缓存分为指令缓存、数据缓存，L2 CPU 核心 独占，L3 共享。
  ```

- L12-L19 · 一、系统结构 > (一) CPU 高速缓存 > 2. 缓存一致性问题

  摘录（原文）：

  ```text
  - 因为 L1 和 L2 Cache 是核心独有的，一个核心修改了缓存中某个数据，但是没有将数据写回，其他核心读取内存中的数据时就会导致读取数据不一致。
  ```

- 其余 2 个相关章节见来源卡片。

### [Redis](../notes/d_7d7f123eef9acac2e14eb914.md)

来源：`01-计算机基础/数据库/Redis.md` · SHA-256 `2f901c5fe849`

- L88-L104 · 一、Redis 基础 > (五) 缓存 > 2. Cache Aside

  摘录（原文）：

  ```text
  1. 为什么更新时**删除缓存**而不是更新缓存？
  ```

- L74-L78 · 一、Redis 基础 > (五) 缓存

  摘录（原文）：

  ```text
  - 内存淘汰、内存过期：一致性差，但是维护成本低。
  ```

- L79-L87 · 一、Redis 基础 > (五) 缓存 > 1. 主动更新策略

  摘录（原文）：

  ```text
  |   |   |   |
  ```

- L105-L112 · 一、Redis 基础 > (五) 缓存 > 3. 缓存一致性的最佳实践

  摘录（原文）：

  ```text
  - **低一致性**需求：Redis 的内存过期+内存淘汰。
  ```

- 其余 3 个相关章节见来源卡片。

### [MySQL](../notes/d_e2efd3502aca378b01a130c4.md)

来源：`01-计算机基础/数据库/MySQL.md` · SHA-256 `160f2e5aeae1`

- L584-L592 · 六、InnoDB > (三) Buffer Pool

  摘录（原文）：

  ```text
  - 缓存了索引页、数据页、undo页、插入缓存页、自适应哈希索引、锁信息等。
  ```


### [JUC](../notes/d_687c3a4e82e8a330fa6e68de.md)

来源：`02-Java 后端/JUC.md` · SHA-256 `94f6e2c71cb7`

- L265-L269 · 三、Java 内存模型（JMM） > (一) 缓存一致性协议

  摘录（原文）：

  ```text
  - 多个处理器从主内存读取同一个数据，如果某个处理器修改了工作内存中的数据，该数据会立即同步到主内存，其他处理器通过总线嗅探机制感知变化并使自己的数据无效。
  ```


### [Java 基础](../notes/d_1c6c8977e2110f25f6baa9de.md)

来源：`02-Java 后端/Java 基础.md` · SHA-256 `f551310fcb69`

- L30-L35 · 一、数据类型 > (二) 包装类 > 3. 包装类的常量池缓存

  摘录（原文）：

  ```text
  - `Byte`、`Short`、`Integer`、`Long` 通过静态内部类缓存了值在 **[-128,127]** 之间的实例。
  ```

- L349-L352 · 三、String > 2. 哈希值缓存

  摘录（原文）：

  ```text
  - 首次调用 hashCode() 时使用**滚动哈希**算法计算哈希值，并存储到 **hash** 字段，后续调用可以直接返回。因为 String 不可变，所以 **hash** 字段永远不会失效。
  ```


### [Spring](../notes/d_aeac005e2a534eb58b3eeb1d.md)

来源：`02-Java 后端/Spring.md` · SHA-256 `19e910c663fe`

- L68-L91 · 一、Spring 框架 > (二) Bean > 4. 三级缓存

  摘录（原文）：

  ```text
  - 三级缓存不能解决构造器注入的循环依赖，可以解决 Setter、字段注入。
  ```


### [高可用](../notes/d_64b48337945366bf84a5a51a.md)

来源：`03-系统设计/高可用.md` · SHA-256 `fc2c64c72b7d`

- L36-L41 · 二、预防措施 > (三) 多级缓存

  摘录（原文）：

  ```text
  - 前端/客户端缓存
  ```


### [DeepSeek Super-agent 设计解读](../notes/d_b1545aad8cfdb3030977d192.md)

来源：`04-AI/DeepSeek Super-agent 设计解读.md` · SHA-256 `de5b86c1ecc1`

- L52-L59 · DeepSeek Super-agent 设计解读 > 二、核心设计 > 3. 上下文按缓存组织：Inline、Spill 与链式召回

  摘录（原文）：

  ```text
  近期大概率用到的内容直接放进上下文，称为 Inline；长正文或低频信息保存在窗口外，只留摘要、ID 和续读入口，称为 Spill。
  ```


### [LLM 与 RAG](../notes/d_fcc04285c9673f6c94c4fdb6.md)

来源：`04-AI/LLM 与 RAG.md` · SHA-256 `d93ce8348aa0`

- L9-L18 · 一、大模型 > (二) KV Cache

  摘录（原文）：

  ```text
  - 生成第一个 Token 时，计算结果如下：
  ```


### [12306](../notes/d_c99987c928888eb8c0611500.md)

来源：`05-项目/12306.md` · SHA-256 `059873d2d21a`

- L133-L137 · 二、项目实现 > (一) 用户模块 > 3. 用户注册、登录的缓存穿透问题

  摘录（原文）：

  ```text
  - 使用布隆过滤器存储已注册用户名，注册和登录时都要检查是否存在该用户名。
  ```

- L175-L178 · 二、项目实现 > (二) 查票 > 4. 查票防止缓存击穿

  摘录（原文）：

  ```text
  - 如果用户输入的条件，缓存未命中。通过 Redisson 的分布式锁 + 双重检查锁，保证同一时刻只有一个线程在重建缓存，避免大量请求同时打到数据库。
  ```

- L283-L288 · 三、 Q & A > (四) 缓存一致性

  摘录（原文）：

  ```text
  - 缓存双删
  ```

- L289-L293 · 三、 Q & A > (四) 缓存一致性 > 1. 介绍一下 Canal

  摘录（原文）：

  ```text
  - Canal 将自己伪装为 Mysql 的从节点，并向 Mysql 发送 dump 请求，Mysql 会向 Canal 推送 binlog 的增量更新。然后 Canal 解析 binlog 后，向下游的 RocketMQ、Kafka 等推送数据。
  ```

- 其余 4 个相关章节见来源卡片。

## 相邻主题

- [数据库、事务与持久化](database.md)
- [分布式、消息与项目实践](distributed.md)
- [线程、锁与并发控制](concurrency.md)

## 检索入口

```powershell
python LLMWiki/wiki.py search "缓存"
```
