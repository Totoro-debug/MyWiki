# 网络、协议与通信

自动主题地图：按标题/章节中的术语归组。关联仅表示主题邻近，不表示技术等价。

路由词：TCP、HTTP、TLS、WebSocket、SSE、网络、RPC

## 来源入口

### [计算机网络](../notes/d_772d6befcfc792ed02c8d26d.md)

来源：`01-计算机基础/计算机网络.md` · SHA-256 `39d8ce895618`

- L488-L497 · 九、WebSocket > (三) HTTP 长连接、长轮询、WebSocket 对比

  摘录（原文）：

  ```text
  | 特性      | HTTP 长连接 | HTTP 长轮询    | WebSocket |
  ```

- L1-L3 · 计算机网络
- L12-L15 · 二、网络层

  摘录（原文）：

  ```text
  - 网络层主要实现主机间通信，点对点通信。
  ```

- L16-L17 · 二、网络层 > (一) IP 基础
- 其余 92 个相关章节见来源卡片。

### [操作系统](../notes/d_30c43c00efdd876efcdd627e.md)

来源：`01-计算机基础/操作系统.md` · SHA-256 `3099a35b4b68`

- L265-L282 · 四、IO > (五) 零拷贝 > 2. 网络传输的零拷贝

  摘录（原文）：

  ```text
  1. **mmap + write**（3 次拷贝、4 次模式切换）
  ```


### [分布式系统](../notes/d_3b0a4e7f68c3a64106febc8b.md)

来源：`03-系统设计/分布式系统.md` · SHA-256 `0d1959eeec2e`

- L280-L283 · 八、RPC

  摘录（原文）：

  ```text
  - RPC（Remote Procedure Call） 即远程过程调用，可以帮助调用远程服务器上某个服务的方法，使得调用远程方法就像调用本地方法一样简单。
  ```

- L284-L291 · 八、RPC > (一) RPC 调用过程

  摘录（原文）：

  ```text
  1. **客户端**：客户端以本地调用的方式调用远程服务。
  ```

- L292-L308 · 八、RPC > (二) RPC 核心能力

  摘录（原文）：

  ```text
  1. **代理调用**
  ```

- L309-L310 · 八、RPC > (三) 常见的 RPC 框架
- 其余 4 个相关章节见来源卡片。

### [system-overall-design](../notes/d_faf5d2081ba5a11865b45895.md)

来源：`09-unachive/system-overall-design.md` · SHA-256 `293146e77920`

- L480-L487 · nanobot 系统整体设计文档 > 8. 部署架构 > 8.3 HTTP API 服务

  摘录（原文）：

  ```text
  适合让其他应用通过 OpenAI-compatible API 调用 nanobot。
  ```


## 相邻主题

- [分布式、消息与项目实践](distributed.md)
- [Agent、工具与记忆](agent.md)

## 检索入口

```powershell
python LLMWiki/wiki.py search "TCP"
```
