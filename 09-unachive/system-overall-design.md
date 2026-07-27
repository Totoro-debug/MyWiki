# nanobot 系统整体设计文档

生成日期：2026-05-28

## 1. 设计目标

nanobot 的目标是构建一个可长期运行、可扩展、低部署成本的个人 AI Agent 系统。系统需要同时支持命令行交互、WebUI、多聊天平台接入、OpenAI 兼容 API、工具调用、长期记忆、定时任务和外部能力扩展。

核心设计原则：

- 轻量内核：Agent 主循环保持清晰，避免把渠道、前端、部署细节耦合进核心推理流程。
- 统一消息模型：所有入口最终转换成统一的入站消息，所有响应转换成统一的出站消息。
- 可插拔能力：模型 Provider、聊天渠道、工具、MCP 服务、技能均可独立扩展。
- 文件优先持久化：使用配置文件、JSONL、Markdown 和本地 workspace 保存状态，降低部署复杂度。
- 长期运行可靠性：支持会话恢复、任务取消、定时唤醒、自动压缩、错误重试和安全边界保护。

## 2. 系统总体框架

系统分为七层：

```text
用户入口层
  CLI / WebUI / 聊天平台 / HTTP API / SDK

接入适配层
  Channel / WebSocket / API Server / CLI Adapter

消息总线层
  InboundMessage / OutboundMessage / MessageBus

Agent 编排层
  AgentLoop / Command Router / Session / Runtime State

Agent 执行层
  AgentRunner / LLM Provider / Tool Registry / Hook

能力扩展层
  Tools / MCP / Skills / Cron / Heartbeat / Memory / Subagent

持久化与安全层
  Config / Workspace / Sessions / Memory Files / Media / Security Policy
```

总体调用关系：

```text
用户请求
  -> 接入层解析协议和权限
  -> 转换为统一 InboundMessage
  -> AgentLoop 读取会话、构造上下文、分发命令或运行 Agent
  -> AgentRunner 调用模型，并按需执行工具
  -> 保存会话、更新记忆、输出 OutboundMessage
  -> 接入层按目标平台渲染和发送
```

## 3. 核心模块设计

### 3.1 用户入口层

系统提供多种入口，但入口层不直接实现 Agent 逻辑：

- CLI：用于本地交互、调试、初始化、状态检查和后台服务启动。
- WebUI：用于浏览器聊天、多会话管理、设置管理、媒体上传和流式展示。
- 聊天平台：用于 Telegram、Slack、飞书、Discord、邮件、WebSocket 等外部平台接入。
- HTTP API：对外提供 OpenAI-compatible 接口，方便第三方应用复用 nanobot。
- SDK：提供程序化接口，便于 Python 应用内嵌 Agent 能力。

实现思路：

- 每种入口只负责协议解析、认证、参数校验和消息封装。
- 用户内容、附件、平台 metadata 统一转换为内部消息。
- 响应渲染由对应入口适配，不进入 Agent 核心。

### 3.2 消息总线层

消息总线是系统的解耦边界。它定义两个方向：

- 入站消息：用户或系统事件进入 Agent。
- 出站消息：Agent 的回复、进度、流式片段和状态事件发回接入层。

实现思路：

- 定义统一的 `InboundMessage` 和 `OutboundMessage` 数据结构。
- 使用异步队列承载消息，避免渠道 I/O 阻塞 Agent。
- 所有聊天渠道只向 inbound 队列写消息，只从 outbound 队列取目标消息。
- CLI/API 可在简单场景下直接调用 Agent，也可通过消息总线复用长期运行模式。

收益：

- 新增渠道不需要修改 Agent 核心。
- Agent 只理解统一消息，不关心平台 SDK。
- 可支持跨会话并发和同会话串行。

### 3.3 Agent 编排层

Agent 编排层负责一次用户请求从恢复、构造上下文、运行、保存到响应的完整生命周期。

一次请求可以抽象为以下状态：

```text
恢复状态
  -> 自动压缩准备
  -> 命令识别
  -> 上下文构建
  -> Agent 执行
  -> 会话保存
  -> 响应组装
```

实现思路：

- 使用显式状态机描述 turn 生命周期。
- 每个会话使用独立锁，保证同一会话串行写入。
- 不同会话可并发执行，受全局并发限制控制。
- 长任务执行期间，同一会话的新消息进入 pending queue，作为 mid-turn follow-up 注入。
- 优先命令，例如停止、重启、状态查询，可绕过普通队列快速处理。
- 在关键阶段保存 runtime checkpoint，进程中断后可恢复未完成上下文。

核心职责：

- 管理运行时模型和 Provider。
- 管理工具上下文。
- 管理会话历史。
- 处理 slash command。
- 调用 Agent 执行层。
- 触发后台记忆压缩。
- 向消息总线发布进度和最终响应。

### 3.4 Agent 执行层

Agent 执行层负责 LLM 与工具调用循环。它不关心消息来自哪个平台，也不关心最终如何展示。

执行循环：

```text
准备 messages 和 tools
  -> 调用 LLM
  -> 判断是否有工具调用
  -> 执行工具并追加 tool result
  -> 再次调用 LLM
  -> 直到得到最终回答或达到停止条件
```

实现思路：

- 用统一的 Provider 接口屏蔽不同模型服务的 API 差异。
- 用统一工具注册表暴露工具 schema。
- 对工具参数做 schema 校验和安全检查。
- 只允许可并发工具并行执行，写文件、shell 等敏感工具默认串行。
- 对模型错误、空响应、长度截断、临时网络错误做恢复策略。
- 对工具结果做截断、落盘或摘要，防止上下文膨胀。
- 支持 hook，把 reasoning、stream delta、工具进度、文件编辑事件传给上层。

关键停止条件：

- 模型给出最终回答。
- 达到最大工具迭代次数。
- 工具出现不可恢复错误。
- 用户取消任务。
- sustained goal 明确完成。

### 3.5 Provider 层

Provider 层负责把统一的模型请求转换为具体服务调用。

设计要求：

- 支持 OpenAI-compatible 服务。
- 支持 Anthropic、Azure OpenAI、Bedrock 等非完全兼容服务。
- 支持 OAuth 型 Provider。
- 支持本地模型服务。
- 支持 fallback model。
- 支持流式输出、reasoning、thinking、tool calling 差异适配。

实现思路：

- 使用 Provider Registry 保存 Provider 元数据，例如名称、默认 base URL、匹配关键字、能力标记。
- Provider Factory 根据配置和模型名自动选择具体 Provider。
- 所有 Provider 输出统一的响应结构。
- 运行时使用 Provider Snapshot 判断配置是否变化，必要时切换模型。
- fallback Provider 包装主 Provider，在主模型失败时尝试备用模型。

### 3.6 Tool 层

Tool 层是 Agent 访问外部世界的主要方式。

工具类型：

- 文件读写和编辑。
- Shell 执行。
- Web 搜索和网页抓取。
- 消息发送。
- 定时任务管理。
- 子 Agent。
- 图片生成。
- MCP 工具。
- CLI App 调用。
- 运行时自省和设置。

实现思路：

- 每个工具声明名称、描述、参数 schema 和执行函数。
- 工具注册表负责工具发现、排序、校验和执行。
- 内置工具通过包扫描自动发现。
- 外部工具通过插件 entry point 注册。
- 工具执行前注入请求上下文，例如 channel、chat_id、session_key。
- 工具层强制执行路径限制、网络限制、参数校验和结果大小限制。

### 3.7 Channel 层

Channel 层用于接入聊天平台和 WebSocket。

通用职责：

- 建立与平台的连接。
- 解析用户消息、附件、回复上下文。
- 做 allowlist 或 pairing 授权。
- 将消息发布到消息总线。
- 接收出站消息并发送到对应平台。
- 支持进度、流式片段、reasoning、按钮或富文本时做平台适配。

实现思路：

- 定义统一 Channel 抽象。
- Channel Manager 负责发现、初始化、启动、停止和出站分发。
- 不启用的渠道不导入重型 SDK，降低启动成本和依赖风险。
- 出站发送统一经过重试、流式片段合并和重复回复抑制。

### 3.8 WebUI 层

WebUI 是一个浏览器端多会话聊天应用。

框架：

- 前端使用 React + TypeScript。
- 与后端通过 WebSocket 通信。
- 一个 WebSocket 连接复用多个 chat。
- 静态资源可由 WebSocketChannel 所在服务直接提供。

实现思路：

- 前端启动时获取短期 token 和 WebSocket 地址。
- WebSocket 建立后自动绑定默认 chat。
- 用户切换会话时发送 attach。
- 新建会话时请求服务端分配 chat_id。
- 聊天消息、流式 delta、turn end、goal state、runtime model update 都作为事件处理。
- 前端维护连接状态、重连、token 刷新和未订阅消息缓冲。
- 设置页通过后端 HTTP 辅助接口或 WebSocket 同域接口更新配置。

## 4. 数据与状态设计

### 4.1 Workspace

Workspace 是运行数据根目录，保存用户可编辑上下文和系统运行状态。

典型内容：

```text
workspace/
  AGENTS.md
  SOUL.md
  USER.md
  HEARTBEAT.md
  sessions/
  memory/
  cron/
  skills/
  media/
```

实现思路：

- 初始化时同步模板文件。
- 系统提示词会读取 workspace 内的 bootstrap 文件。
- 用户可直接编辑这些文件调整 Agent 行为。

### 4.2 Session

Session 保存短期对话历史。

设计要求：

- 每个渠道会话单独保存。
- 支持统一会话模式，多个渠道共享一个 session。
- 支持恢复损坏文件。
- 支持追加消息和保留合法上下文尾部。
- 支持 WebUI 会话列表快速读取。

实现思路：

- 每个 session 一个 JSONL 文件。
- 第一行保存 metadata，后续每行保存一条消息。
- 写入采用临时文件加原子替换。
- 读取时过滤内部控制信息，避免污染 LLM 上下文。
- 超过消息上限时归档旧消息。

### 4.3 Memory

Memory 保存长期记忆和人格/用户信息。

分层：

- 会话历史：短期上下文。
- history.jsonl：压缩后的长期对话摘要。
- MEMORY.md：长期事实。
- SOUL.md：Agent 人设或行为约束。
- USER.md：用户偏好和资料。

实现思路：

- 轻量压缩器在上下文超预算时把旧会话摘要写入 history。
- Dream 定时读取未处理 history，分析是否要更新 MEMORY/SOUL/USER 或创建技能。
- Dream 成功后推进游标，失败不推进，避免记忆丢失。
- 关键记忆文件可由本地 git store 自动版本化，支持审计和恢复。

### 4.4 Cron 和 Heartbeat

Cron 用于显式定时任务，Heartbeat 用于周期性主动检查。

Cron 实现思路：

- 定时任务持久化到 workspace。
- 支持一次性、固定间隔和 cron 表达式。
- 到期后通过 Agent 执行任务，并按配置决定是否投递给用户。

Heartbeat 实现思路：

- 周期性读取 HEARTBEAT.md。
- 先让模型用结构化工具调用判断是否需要执行。
- 只有需要执行时才进入完整 Agent 流程。
- 执行结果经过评估后再决定是否打扰用户。

## 5. 关键流程设计

### 5.1 普通聊天流程

```text
用户发送消息
  -> Channel 校验权限并解析附件
  -> 发布 InboundMessage
  -> AgentLoop 获取 session lock
  -> 恢复 checkpoint
  -> 读取 session history
  -> 构造 system prompt、history、runtime context
  -> AgentRunner 调用模型
  -> 如有工具调用则执行工具并继续循环
  -> 得到最终回答
  -> 保存用户消息、工具结果、助手回答
  -> 发布 OutboundMessage
  -> Channel 渲染并发送
```

### 5.2 流式输出流程

```text
模型产生 token delta
  -> Provider 回调 stream delta
  -> Agent Hook 转换为进度事件
  -> AgentLoop 发布 outbound stream_delta
  -> ChannelManager 合并连续 delta
  -> Channel/WebUI 增量展示
  -> 模型进入工具调用时发送 stream_end(resuming=true)
  -> 最终回答结束时发送 stream_end(resuming=false) 和 turn_end
```

### 5.3 工具调用流程

```text
模型返回 tool_calls
  -> AgentRunner 保存 awaiting_tools checkpoint
  -> ToolRegistry 查找工具
  -> 参数 cast 和 schema 校验
  -> 执行工具
  -> 工具结果大小控制和必要落盘
  -> 追加 tool result message
  -> 保存 tools_completed checkpoint
  -> 继续下一轮模型调用
```

### 5.4 长任务与中途追问流程

```text
用户发起长任务
  -> AgentLoop 创建活跃任务
  -> 同 session 新消息进入 pending queue
  -> AgentRunner 在工具执行后或恢复点 drain pending queue
  -> 把新消息作为 user follow-up 注入上下文
  -> 模型基于最新用户反馈继续执行
```

### 5.5 记忆压缩流程

```text
会话增长
  -> 估算 prompt token
  -> 超过预算时选取可压缩旧消息
  -> LLM 总结旧消息
  -> 摘要写入 memory/history.jsonl
  -> session 标记 last_consolidated
  -> Dream 定期处理 history
  -> 更新长期记忆文件
```

## 6. 安全设计

安全边界包括：

- 网络绑定默认本机地址。
- WebSocket 公网绑定必须启用认证。
- 渠道必须通过 allowlist 或 pairing。
- Web fetch 防 SSRF，默认阻止内网和私有地址。
- 文件与 shell 工具限制 workspace。
- 上传媒体限制 MIME、数量和大小。
- 工具结果限制大小，避免上下文或磁盘膨胀。
- cron store、session store 使用原子写，避免崩溃损坏。
- bridge 服务只监听本机并要求 token。

实现思路：

- 安全检查尽量放在工具和接入边界，而不是依赖模型自觉。
- 模型遇到安全边界时收到不可绕过说明，避免反复尝试绕过。
- 用户确实需要访问私有网络时，通过显式白名单配置放行。

## 7. 可扩展性设计

### 7.1 新增模型服务

实现思路：

- 优先通过 Provider Registry 增加元数据。
- 如果是 OpenAI-compatible 服务，复用通用 Provider。
- 如果协议特殊，实现新的 Provider 适配类。
- 所有 Provider 输出统一响应结构，避免影响 AgentRunner。

### 7.2 新增工具

实现思路：

- 工具实现只依赖 Tool 抽象和 ToolContext。
- 参数使用 JSON Schema 描述。
- 工具内部完成权限、路径、网络、大小限制。
- 注册后自动出现在模型可调用工具列表中。

### 7.3 新增聊天平台

实现思路：

- 实现 Channel 抽象。
- 平台消息转换为统一入站消息。
- 出站消息根据平台能力渲染为文本、富文本、卡片或流式更新。
- 配置项通过 channel 默认配置注入。

### 7.4 新增技能

实现思路：

- 技能以 Markdown 描述触发条件、工作流和注意事项。
- Agent 上下文按需加载技能摘要或全文。
- 技能可以携带脚本、参考文件或模板。

## 8. 部署架构

### 8.1 本地单用户部署

```text
nanobot onboard
nanobot agent
```

适合开发、调试、个人命令行使用。

### 8.2 长期运行 Gateway

```text
nanobot gateway
```

适合连接聊天平台、WebUI、定时任务和 heartbeat。Gateway 是完整系统运行模式。

### 8.3 HTTP API 服务

```text
nanobot serve
```

适合让其他应用通过 OpenAI-compatible API 调用 nanobot。

### 8.4 容器部署

实现思路：

- 容器内以非 root 用户运行。
- 挂载 `~/.nanobot` 保存配置和 workspace。
- Gateway 暴露 health 和 WebSocket 端口。
- API 端口默认只绑定宿主机本机地址。
- WhatsApp bridge 在同容器内构建并通过本机连接使用。

## 9. 可靠性设计

系统长期运行时需要处理以下问题：

- 模型请求失败：Provider 层做 transient retry 和 retry-after 解析。
- 工具执行失败：返回结构化错误给模型，允许重新规划。
- 进程中断：保存 runtime checkpoint 和 pending user turn。
- 会话文件损坏：读取时 repair，无法修复时保留可恢复数据。
- cron store 损坏：保留 corrupt backup，拒绝用空任务覆盖。
- 上下文超长：自动 snip、microcompact、consolidation。
- 渠道发送失败：ChannelManager 统一重试。
- WebSocket 断线：前端自动重连并重新 attach。
- 长任务取消：priority command 取消活跃任务和子 Agent。

## 10. 设计边界

本系统不把所有能力做成一个中心化服务，而是以本地 workspace 为核心。这带来几个边界：

- 文件持久化适合单用户或小规模部署，不适合高并发多租户 SaaS。
- 同一 workspace 内状态共享，隔离依赖不同 workspace 或配置文件。
- 模型能力差异由 Provider 层尽量抹平，但 tool calling、reasoning 和流式行为仍需适配。
- 聊天平台能力不一致，富文本、流式、按钮、媒体展示必须允许降级。

## 11. 后续演进方向

- 提供更标准的插件包结构，统一工具、渠道、技能的安装和启停。
- 为 WebUI 设置接口增加更完整的配置事务和回滚机制。
- 增强多 workspace 管理，支持更清晰的个人/项目隔离。
- 引入可选数据库后端，服务于多用户或高并发部署场景。
- 增强观测能力，统一 trace turn、tool、provider、channel delivery。
- 为长期目标增加更明确的任务计划、检查点和用户确认机制。
