# nanobot 精简复现版 PRD

生成日期：2026-05-28

## 1. 背景

当前 nanobot 项目是一个功能完整的个人 AI Agent 框架，包含 CLI、WebUI、OpenAI-compatible API、多聊天平台、MCP、技能、记忆、定时任务、Heartbeat、图片生成、SubAgent、容器部署等能力。

本次复现目标不是完整迁移当前项目，而是构建一个只保留必须功能的精简版本。精简版应优先保证 Agent 核心链路清晰、可运行、可扩展，暂不保留 WebUI、HTTP API、Cron/Heartbeat、图片生成和大量聊天渠道。

## 2. 产品目标

精简版 nanobot 要实现一个可通过命令行和外部聊天平台使用的个人 Agent 系统，具备以下核心能力：

- 通过 CLI 与 Agent 交互。
- 通过 FeiShu、WeiXin 与 Agent 交互。
- 保留聊天渠道扩展接口，便于后续新增其他平台。
- 支持 OpenAI-compatible 模型服务，并允许动态添加兼容 OpenAI 协议的 Provider。
- 支持 Agent 主循环、工具调用、MCP 工具接入、双层记忆和 SubAgent。
- 使用本地文件持久化配置、会话、记忆和运行状态。

## 3. 用户与场景

目标用户：

- 个人用户：需要一个可长期积累上下文的 AI 助手。
- 开发者用户：需要通过 CLI 调用 Agent 完成文件、代码、搜索、MCP 等任务。
- 企业 IM 用户：希望在 FeiShu 或 WeiXin 中接入个人/团队助手。
- 扩展开发者：希望新增 Provider、Channel、Tool 或 MCP 服务。

核心场景：

- 用户在命令行中输入任务，Agent 调用模型与工具完成任务并返回结果。
- 用户在 FeiShu 或 WeiXin 中发送消息，Agent 读取会话上下文并回复。
- 用户配置 OpenAI-compatible Provider 后切换模型或新增兼容端点。
- 用户配置 MCP Server，让 Agent 调用外部工具。
- Agent 在长任务中派生 SubAgent 执行子任务，子任务完成后回传主会话。
- 会话内容在上下文增长后被压缩沉淀到长期记忆。

## 4. 范围

### 4.1 保留功能

P0 必须实现：

- CLI 入口：
  - 初始化配置和 workspace。
  - 单轮对话。
  - 交互式对话。
  - 查看运行状态。
  - 渠道状态与登录命令。
- Gateway 入口：
  - 启动 AgentLoop。
  - 启动 ChannelManager。
  - 启动 FeiShu、WeiXin 和外部 Channel 插件。
  - 分发 inbound/outbound 消息。
- Agent 核心：
  - AgentLoop turn 状态机。
  - AgentRunner 模型与工具调用循环。
  - 同会话串行、跨会话并发。
  - 中途追问注入。
  - checkpoint 恢复。
- 双层记忆：
  - 短期会话记忆：session JSONL。
  - 长期记忆：MEMORY.md、history.jsonl、SOUL.md、USER.md。
  - 会话压缩到长期历史。
  - Dream 式长期记忆整理可作为后台/手动能力保留。
- 工具调用：
  - Tool 抽象、ToolRegistry、ToolLoader。
  - 文件读写/编辑工具。
  - Shell/执行工具。
  - Web 搜索和网页读取工具。
  - MCP 工具接入。
  - 消息发送工具。
  - SubAgent 工具。
- SubAgent：
  - 主 Agent 可创建后台子任务。
  - SubAgent 使用独立工具 registry。
  - 子任务完成后通过消息总线回传主会话。
  - 支持按 session 取消 SubAgent。
- Provider：
  - 只支持 OpenAI-compatible 调用协议。
  - 支持配置 api_key、api_base、model、extra_headers、extra_body。
  - 支持内置 ProviderSpec registry。
  - 支持运行时动态添加 OpenAI-compatible Provider 配置。
- Channel：
  - BaseChannel 抽象。
  - ChannelManager。
  - FeiShu Channel。
  - WeiXin Channel。
  - 外部 Channel 插件 entry point。
- 配置与持久化：
  - Pydantic 配置模型。
  - 支持 JSON 配置和环境变量覆盖。
  - workspace 模板初始化。
  - 原子写 session 和 memory 文件。
- 安全：
  - 默认本地文件持久化。
  - allow_from/pairing 授权。
  - 文件和 Shell 工具可限制在 workspace 内。
  - Web 工具 SSRF 防护。
  - 媒体文件安全文件名与大小限制。

P1 建议实现：

- Provider 配置热加载。
- Channel 插件列表命令。
- 模型 preset。
- 工具结果落盘和上下文预算治理。
- 记忆文件 git 版本化。
- FeiShu 富文本、卡片、流式更新降级。
- WeiXin 媒体收发和 typing 状态。

### 4.2 不保留功能

精简版暂不保留：

- React WebUI。
- WebSocketChannel 作为 WebUI 后端。
- OpenAI-compatible HTTP API Server。
- Telegram、Slack、Discord、DingTalk、QQ、Matrix、Email、WhatsApp、WeCom、MSTeams 等非 FeiShu/WeiXin 内置渠道。
- CronService 定时任务。
- Heartbeat 主动唤醒。
- Sustained Goal 长期目标状态机。
- 图片生成工具与图片生成 Provider。
- Anthropic、Azure OpenAI、Bedrock、OpenAI Codex、GitHub Copilot 等非 OpenAI-compatible 简化目标之外的 Provider 后端。
- OAuth Provider 登录。
- 前端设置页、MCP presets UI、CLI apps UI、多语言 UI。
- Docker/Compose 作为 P0 交付内容。

## 5. 功能需求

### 5.1 CLI

CLI 应提供以下命令：

- `onboard`：创建配置文件、初始化 workspace、写入 FeiShu/WeiXin 默认配置。
- `agent`：运行单轮或交互式 Agent。
- `gateway`：启动长期运行服务，接入 FeiShu、WeiXin 和插件渠道。
- `channels status`：显示渠道启用状态。
- `channels login <channel>`：执行渠道登录，至少支持 WeiXin QR 登录。
- `plugins list`：列出内置和外部 Channel 插件。
- `status`：显示配置、workspace、Provider 和模型状态。

验收标准：

- 新用户能通过 `onboard` 生成可编辑配置。
- 配置 OpenAI-compatible Provider 后，`agent -m "hello"` 可返回模型响应。
- 交互式 CLI 可连续对话并保存 session。
- `gateway` 能启动已启用渠道。

### 5.2 FeiShu Channel

FeiShu Channel 应支持：

- 通过 FeiShu/Lark WebSocket 长连接收消息。
- 支持私聊和群聊。
- 群聊支持 mention-only 或 open 策略。
- 支持 allow_from 或 pairing 授权。
- 支持文本、图片、文件、音频消息解析。
- 支持回复上下文和 topic/session 隔离。
- 支持发送文本、富文本、交互卡片和媒体。
- 流式能力可降级为卡片更新或最终消息。

验收标准：

- 未授权私聊用户收到 pairing code。
- 群聊未 mention 时默认不触发 Agent。
- 授权用户消息能进入正确 session。
- Agent 回复能发送回原 FeiShu 会话。

### 5.3 WeiXin Channel

WeiXin Channel 应支持：

- QR 登录并持久化 token。
- HTTP long-poll 拉取消息。
- 支持文本、图片、语音、文件、视频消息解析。
- 支持媒体下载到本地 media 目录。
- 支持文本和媒体回复。
- 支持 allow_from 或 pairing 授权。
- 在平台不支持原生 streaming 时，流式输出降级为最终回复。

验收标准：

- `channels login weixin` 能完成登录并保存状态。
- Gateway 启动后可持续拉取 WeiXin 消息。
- 授权用户消息能触发 Agent 回复。
- Token 过期或轮询失败时有重试和日志。

### 5.4 Channel 扩展接口

系统应保留 Channel 插件接口：

- 插件继承 BaseChannel。
- 插件实现 `start()`、`stop()`、`send()`。
- 可选实现 `send_delta()`、`send_reasoning_delta()`、`login()`。
- 插件通过 Python entry point `nanobot.channels` 注册。
- ChannelManager 只加载启用的渠道。

验收标准：

- 外部包注册一个 Channel 后，可通过配置启用。
- 未启用插件不会被导入。
- 插件和内置渠道命名冲突时，内置渠道优先。

### 5.5 OpenAI-compatible Provider

Provider 模块应只面向 OpenAI-compatible API：

- 使用统一 LLMProvider 抽象。
- 使用 OpenAI Chat Completions 或 Responses 兼容协议。
- 支持 tool calling。
- 支持 streaming。
- 支持 reasoning 字段的兼容透传或忽略。
- 支持 api_base、api_key、extra_headers、extra_body。
- ProviderSpec registry 用于声明默认 base URL、模型关键字、显示名、能力标记。
- 用户可通过配置动态添加兼容 OpenAI 协议的 Provider。

验收标准：

- OpenAI 官方 API 可用。
- OpenRouter、DeepSeek、DashScope、Ollama/vLLM 等兼容端点可通过配置接入。
- 新增兼容 Provider 不需要新增 Provider 子类。
- 模型返回 tool_calls 时 AgentRunner 能正确执行工具。

### 5.6 Agent 核心

AgentLoop 应负责产品层 turn 生命周期：

- 恢复 checkpoint。
- 处理媒体和文档提取。
- 处理 slash command。
- 构造上下文。
- 调用 AgentRunner。
- 保存 session。
- 组装 outbound。

AgentRunner 应负责模型与工具循环：

- 请求模型。
- 解析工具调用。
- 校验工具参数。
- 执行工具。
- 追加 tool result。
- 继续模型调用直到最终回答。
- 管理上下文预算和工具结果大小。
- 处理空响应、长度截断、工具错误和 transient retry。

验收标准：

- 单轮消息能完成无工具回复。
- 模型调用工具后能继续生成最终回复。
- 工具错误不会直接崩溃主进程。
- 同一 session 不并发写入历史。

### 5.7 工具与 MCP

工具系统应支持：

- 内置工具包扫描注册。
- 外部工具 entry point 注册。
- 工具 JSON Schema 参数声明。
- 工具执行前参数 cast 和 validate。
- 工具结果截断或落盘。
- 工具权限和安全边界。

MCP 支持：

- stdio MCP server。
- HTTP/SSE 或 streamable HTTP MCP server。
- 配置 server name、command、args、env、cwd、url、headers、timeout、enabled_tools。
- MCP 工具注册为 `mcp_<server>_<tool>`。

验收标准：

- 配置 MCP server 后，工具列表包含对应 MCP 工具。
- MCP 工具调用超时可控。
- 禁用工具不会暴露给模型。

### 5.8 双层记忆

短期记忆：

- 每个 session 一个 JSONL 文件。
- 保存用户消息、助手消息、工具调用和工具结果。
- 读取时过滤内部控制消息。
- 支持损坏文件修复或降级读取。

长期记忆：

- `memory/MEMORY.md` 保存长期事实。
- `memory/history.jsonl` 保存压缩历史。
- `SOUL.md` 保存 Agent 行为/人格约束。
- `USER.md` 保存用户偏好与资料。
- Consolidator 在上下文接近预算时压缩旧消息到 history。
- Dream 可分析 history 并编辑 MEMORY/SOUL/USER。

验收标准：

- 会话重启后能读取历史。
- 长对话不会无限扩大 prompt。
- 压缩失败时可 raw archive，不丢失原始信息。
- Dream 失败不推进 cursor。

### 5.9 SubAgent

SubAgent 模块应支持：

- 主 Agent 通过工具创建子任务。
- 子任务后台异步执行。
- 子任务拥有独立工具 registry 和系统 prompt。
- 子任务结果通过 MessageBus 注入主会话。
- 支持查询运行数量和按 session 取消。

验收标准：

- 主 Agent 可启动 SubAgent。
- SubAgent 完成后主 Agent 能收到结果并继续响应。
- 子任务失败时返回可读错误。
- 取消主任务时能取消相关 SubAgent。

## 6. 非功能需求

性能：

- 默认支持至少 3 个不同 session 并发。
- 同一 session 保证串行。
- 长工具结果不直接塞满上下文。

可靠性：

- Provider transient 错误可重试。
- Channel 发送失败可重试。
- session/memory 写入使用原子写或可恢复策略。
- checkpoint 能恢复中断的工具调用状态。

安全：

- 默认不开放 HTTP 服务。
- 外部聊天用户必须通过 allow_from 或 pairing 授权。
- 文件和 Shell 工具支持 workspace 限制。
- Web 工具默认阻止 private/internal 地址。
- 媒体文件使用安全文件名并限制类型。

可维护性：

- AgentLoop 和 AgentRunner 保持清晰边界。
- Channel 不直接调用模型。
- Provider 不包含产品逻辑。
- Tool 不依赖具体聊天平台。
- 扩展接口通过抽象类和 entry point 暴露。

## 7. 交付物

- `prd.md`：产品需求文档。
- `design.md`：精简版系统设计文档。
- 精简版实现代码。
- 配置模板。
- 最小测试集：
  - AgentRunner 工具循环。
  - AgentLoop session 保存。
  - OpenAI-compatible Provider。
  - ToolRegistry/ToolLoader/MCP。
  - FeiShu/WeiXin 消息解析和权限。
  - SubAgent 生命周期。
  - MemoryStore/Consolidator。

## 8. 成功标准

精简版满足以下条件即认为 P0 完成：

- 能通过 CLI 初始化、对话、保存上下文。
- 能通过 Gateway 接入 FeiShu 和 WeiXin。
- 能调用 OpenAI-compatible 模型完成普通对话和工具调用。
- 能配置 MCP 并调用 MCP 工具。
- 能保存短期 session，并把超长会话压缩进长期记忆。
- 能派生 SubAgent 并把结果注入主会话。
- 能通过 BaseChannel 和 ProviderSpec 扩展新渠道和新 OpenAI-compatible Provider。
