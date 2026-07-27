# nanobot 精简复现版设计文档

生成日期：2026-05-28

## 1. 设计目标

精简版 nanobot 复用当前项目中已经验证的核心分层，但删除非必须入口和能力。系统目标是构建一个本地优先、可通过 CLI/FeiShu/WeiXin 使用、可扩展 Provider/Channel/Tool/MCP 的个人 Agent。

核心设计原则：

- 轻量入口：只保留 CLI 和聊天平台 Gateway。
- OpenAI-compatible 优先：Provider 层只保留兼容 OpenAI 协议的通用实现。
- Agent 内核稳定：保留 AgentLoop、AgentRunner、ToolRegistry、Memory、SubAgent 的边界。
- 渠道解耦：FeiShu、WeiXin 和未来渠道只通过 MessageBus 接入。
- 文件持久化：配置、session、memory、media 均保存在本地 workspace。
- 可扩展：Channel、Tool、ProviderSpec 和 MCP 均保留扩展接口。

## 2. 总体架构

```text
用户入口层
  CLI / FeiShu / WeiXin / 外部 Channel 插件

接入适配层
  CLI Adapter / BaseChannel / ChannelManager

消息总线层
  InboundMessage / OutboundMessage / MessageBus

Agent 编排层
  AgentLoop / CommandRouter / SessionManager / ContextBuilder

Agent 执行层
  AgentRunner / OpenAICompatProvider / ToolRegistry / Hook

能力扩展层
  Built-in Tools / External Tools / MCP / Skills / Memory / SubAgent

持久化与安全层
  Config / Workspace / Sessions / Memory Files / Media / SSRF / Workspace Guard
```

普通调用链：

```text
用户消息
  -> CLI 或 Channel 解析协议、校验权限
  -> 生成 InboundMessage
  -> AgentLoop 获取 session lock
  -> 恢复 checkpoint、读取 session、构造上下文
  -> AgentRunner 调用 OpenAI-compatible Provider
  -> 如模型请求工具，ToolRegistry 执行工具或 MCP 工具
  -> 保存 session，必要时触发 memory consolidation
  -> 生成 OutboundMessage
  -> CLI 或 Channel 渲染发送
```

## 3. 模块划分

### 3.1 CLI 模块

建议保留路径：

- `nanobot/__main__.py`
- `nanobot/cli/commands.py`
- `nanobot/cli/stream.py`
- `nanobot/cli/onboard.py`
- `nanobot/cli/models.py`

保留命令：

- `onboard`
- `agent`
- `gateway`
- `channels status`
- `channels login`
- `plugins list`
- `status`

删除或不实现：

- `serve`
- `provider login/logout`
- WebUI 相关命令或提示。

CLI 运行模式：

- 单轮模式直接调用 `AgentLoop.process_direct()`。
- 交互模式通过 `MessageBus` 复用 Gateway 链路。
- progress、stream delta、reasoning 可在终端渲染；不要求 WebUI 事件兼容。

### 3.2 Gateway 模块

Gateway 是聊天平台长期运行入口。

启动流程：

```text
load_config
  -> resolve env vars
  -> create MessageBus
  -> create SessionManager
  -> build OpenAI-compatible ProviderSnapshot
  -> AgentLoop.from_config
  -> ChannelManager
  -> run AgentLoop.run + ChannelManager.start_all
```

精简点：

- 不启动 WebSocketChannel。
- 不启动 CronService。
- 不启动 HeartbeatService。
- 不注册 Dream 系统 cron job。
- Dream 可作为手动命令或 Agent 内部能力保留，不依赖 Cron。

### 3.3 消息总线

保留：

- `nanobot/bus/events.py`
- `nanobot/bus/queue.py`

核心数据结构：

```python
InboundMessage:
  channel: str
  sender_id: str
  chat_id: str
  content: str
  media: list[str]
  metadata: dict
  session_key_override: str | None

OutboundMessage:
  channel: str
  chat_id: str
  content: str
  media: list[str]
  metadata: dict
  buttons: list | None
```

会话键规则：

- 默认：`{channel}:{chat_id}`。
- 渠道可设置 `session_key_override`，例如 FeiShu topic isolation。
- 可保留 `unified_session` 配置，使多个入口共享 `unified:default`。

## 4. Agent 核心设计

### 4.1 AgentLoop

AgentLoop 是产品层 turn 编排器。

保留状态机：

```text
RESTORE
  -> COMPACT
  -> COMMAND
  -> BUILD
  -> RUN
  -> SAVE
  -> RESPOND
  -> DONE
```

状态职责：

- `RESTORE`：处理媒体/文档提取，恢复 checkpoint 和 pending user turn。
- `COMPACT`：执行 idle 或 token 触发的 session compact 准备。
- `COMMAND`：分发 slash command。
- `BUILD`：读取 session history，构造 system prompt、memory、skills、runtime context。
- `RUN`：调用 AgentRunner。
- `SAVE`：保存用户消息、助手消息、工具结果，清理 checkpoint。
- `RESPOND`：生成 OutboundMessage。

并发策略：

- 每个 session 一个 `asyncio.Lock`。
- 跨 session 通过全局 semaphore 限制并发。
- 同 session 新消息进入 pending queue，在工具执行后注入当前 turn。

精简建议：

- 保留 `/stop`、`/restart`、`/new`、`/status` 等核心命令。
- 移除 WebUI turn coordinator 依赖，或将其包裹成可选空实现。
- 移除 sustained goal 逻辑。
- 保留 checkpoint，避免进程中断污染 session。

### 4.2 AgentRunner

AgentRunner 是模型与工具调用循环，不依赖渠道。

执行流程：

```text
messages + tools
  -> provider.chat/chat_stream
  -> no tool_calls: finalize
  -> has tool_calls:
       prepare_call
       execute tools
       append tool results
       checkpoint
       drain injections
       continue
```

保留能力：

- OpenAI tool_call 格式。
- tool schema 校验。
- 并发安全工具分批执行。
- 工具错误转为模型可读错误。
- 空响应重试。
- length recovery。
- context snip。
- tool result budget。
- orphan tool result 修复。
- SSRF/workspace violation 分类提示。
- Hook 机制。

删除或弱化：

- 非 OpenAI Provider 特殊消息兼容逻辑。
- WebUI 专属 file_edit event 可以保留为 progress hook，但不作为 P0 展示需求。

## 5. Provider 设计

### 5.1 Provider 抽象

保留：

- `LLMProvider`
- `LLMResponse`
- `ToolCallRequest`
- `GenerationSettings`
- `OpenAICompatProvider`

删除：

- `AnthropicProvider`
- `AzureOpenAIProvider`
- `BedrockProvider`
- `OpenAICodexProvider`
- `GitHubCopilotProvider`
- OAuth 登录链路。

### 5.2 ProviderSpec Registry

ProviderSpec 只描述 OpenAI-compatible endpoint。

字段建议：

```python
ProviderSpec:
  name: str
  display_name: str
  keywords: tuple[str, ...]
  default_api_base: str
  env_key: str
  is_gateway: bool
  is_local: bool
  is_direct: bool
  strip_model_prefix: bool
  supports_max_completion_tokens: bool
  thinking_style: str
  gateway_reasoning_style: str
  reasoning_as_content: bool
```

ProviderFactory 简化流程：

```text
resolve model preset
  -> match provider by explicit name / model prefix / keyword / configured key
  -> load ProviderConfig
  -> create OpenAICompatProvider
  -> apply generation settings
```

动态添加 Provider：

- 配置文件支持 `providers.<name>` 动态字段。
- 配置文件支持 `provider_specs.<name>` 或类似结构声明新 ProviderSpec。
- 若未提供 ProviderSpec，可使用 `custom` Provider，显式指定 `api_base` 和 `provider="custom"`。
- 新 Provider 只要兼容 OpenAI 协议，不需要写 Python 子类。

推荐配置示例：

```json
{
  "agents": {
    "defaults": {
      "model": "deepseek-chat",
      "provider": "deepseek"
    }
  },
  "providers": {
    "deepseek": {
      "apiKey": "${DEEPSEEK_API_KEY}",
      "apiBase": "https://api.deepseek.com"
    }
  }
}
```

## 6. Channel 设计

### 6.1 BaseChannel

BaseChannel 是所有聊天平台的扩展接口。

必选方法：

```python
async def start() -> None
async def stop() -> None
async def send(msg: OutboundMessage) -> None
```

可选方法：

```python
async def login(force: bool = False) -> bool
async def send_delta(chat_id: str, delta: str, metadata: dict | None = None) -> None
async def send_reasoning_delta(chat_id: str, delta: str, metadata: dict | None = None) -> None
async def send_reasoning_end(chat_id: str, metadata: dict | None = None) -> None
```

通用能力：

- `allow_from` 授权。
- pairing code。
- 音频转写可选。
- `supports_streaming` 能力探测。
- `_handle_message()` 统一生成 InboundMessage。

### 6.2 ChannelManager

职责：

- 扫描内置渠道和外部插件。
- 只导入启用渠道。
- 注入全局 progress/tool_hints/reasoning 配置。
- 启动所有启用渠道。
- 消费 outbound queue 并发送到目标渠道。
- 发送失败重试。
- stream delta 合并。
- duplicate suppression。

精简内置渠道：

- `feishu`
- `weixin`

外部渠道：

- 通过 entry point `nanobot.channels` 注册。
- 内置渠道与插件同名时，内置优先。

### 6.3 FeiShu Channel

保留设计：

- 使用 `lark-oapi` WebSocket 长连接。
- 支持 `app_id`、`app_secret`、`encrypt_key`、`verification_token`。
- 支持 FeiShu/Lark domain。
- 支持私聊和群聊。
- 支持 `group_policy = mention | open`。
- 支持 `topic_isolation`。
- 支持文本、post、image、audio、file、media、interactive。
- 支持发送 text、post、interactive card、image/file/media。
- 支持 reaction、reply_to_message、streaming card。

关键会话策略：

```text
私聊:
  session_key = feishu:<sender/open_id>

群聊 topic_isolation=true:
  session_key = feishu:<chat_id>:<root_id or message_id>

群聊 topic_isolation=false:
  session_key = feishu:<chat_id>
```

### 6.4 WeiXin Channel

保留设计：

- 使用 ilink HTTP long-poll。
- QR 登录获取 token。
- token 和轮询游标保存到 runtime state 目录。
- 支持文本、图片、语音、文件、视频。
- 支持媒体下载与上传。
- 支持 typing 状态。
- 原生不支持 streaming，`send_delta` 只处理 stream_end 或工具 hint flush。

关键状态：

```text
runtime/weixin/account.json
  token
  get_updates_buf
  context_tokens
  typing_tickets
  base_url
```

## 7. 工具与 MCP 设计

### 7.1 Tool 抽象

保留：

- `Tool`
- `ToolRegistry`
- `ToolLoader`
- `ToolContext`

Tool 必须声明：

```python
name
description
parameters
execute(**kwargs)
```

可选属性：

- `read_only`
- `concurrency_safe`
- `exclusive`
- `config_key`
- `_scopes`
- `enabled(ctx)`
- `create(ctx)`
- `config_cls()`

内置工具建议保留：

- filesystem/read/edit/apply_patch。
- shell/exec_session。
- web_search/web_fetch。
- mcp。
- message。
- spawn/subagent。
- self/runtime_state。

不保留：

- image_generation。
- cron。
- cli_apps，除非后续明确需要。

### 7.2 MCP

MCP 配置：

```python
MCPServerConfig:
  type: "stdio" | "sse" | "streamableHttp" | None
  command: str
  args: list[str]
  env: dict[str, str]
  cwd: str
  url: str
  headers: dict[str, str]
  tool_timeout: int
  enabled_tools: list[str]
```

注册规则：

- 每个 MCP server 建立独立连接。
- MCP tool 统一包装为 `mcp_<server>_<tool>`。
- `enabled_tools=["*"]` 表示全部启用。
- `enabled_tools=[]` 表示不注册工具。

生命周期：

- AgentLoop 启动或首个 turn 前连接 MCP。
- AgentLoop 退出时关闭 MCP AsyncExitStack。
- MCP 工具失败以工具错误返回给模型。

## 8. 记忆设计

精简版保留双层记忆：

### 8.1 第一层：短期 Session

路径：

```text
<workspace>/sessions/<safe_session_key>.jsonl
```

结构：

```text
line 1: metadata
line n: message
```

功能：

- 保存每轮用户/助手/工具消息。
- 支持 `last_consolidated`。
- 支持 metadata 保存 checkpoint。
- 读取时过滤 command 和内部控制消息。
- 支持文件损坏 repair。

### 8.2 第二层：长期 Memory

路径：

```text
<workspace>/memory/MEMORY.md
<workspace>/memory/history.jsonl
<workspace>/memory/.cursor
<workspace>/memory/.dream_cursor
<workspace>/SOUL.md
<workspace>/USER.md
```

职责：

- `MEMORY.md`：长期事实。
- `history.jsonl`：压缩历史条目。
- `SOUL.md`：Agent 行为约束。
- `USER.md`：用户偏好和资料。
- `.cursor`：history 写入游标。
- `.dream_cursor`：Dream 已处理游标。

### 8.3 Consolidator

触发：

- 构造上下文前估算 token。
- session replay 超过预算时选取旧消息。

流程：

```text
estimate session prompt tokens
  -> pick consolidation boundary
  -> LLM summarize old messages
  -> append summary to history.jsonl
  -> advance session.last_consolidated
  -> save session
```

失败策略：

- LLM 总结失败时 raw archive。
- raw archive 后推进 last_consolidated，避免重复归档。

### 8.4 Dream

Dream 用于长期记忆整理，可保留为手动或内部调用能力。

流程：

```text
read unprocessed history since .dream_cursor
  -> Phase 1: analyze memory changes
  -> Phase 2: AgentRunner + file tools edit MEMORY/SOUL/USER/skills
  -> success: advance .dream_cursor
  -> failure: do not advance cursor
```

精简约束：

- 不依赖 Cron 自动调度。
- 可由 CLI 命令、slash command 或手动工具触发。
- Phase 2 只允许访问 workspace memory/skills 相关文件。

## 9. SubAgent 设计

SubAgentManager 保留为后台子任务管理器。

职责：

- 创建子任务 ID。
- 启动后台 asyncio task。
- 为子任务构建独立 ToolRegistry。
- 使用 AgentRunner 执行子任务。
- 保存实时状态。
- 完成后通过 MessageBus 发布系统 InboundMessage。

状态模型：

```python
SubagentStatus:
  task_id
  label
  task_description
  started_at
  phase
  iteration
  tool_events
  usage
  stop_reason
  error
```

回传流程：

```text
SubAgent finished
  -> render subagent_announce prompt
  -> InboundMessage(channel="system", sender_id="subagent")
  -> session_key_override = origin session
  -> AgentLoop 注入 pending queue 或作为新 turn 处理
```

## 10. 上下文构建

ContextBuilder 保留以下输入：

- `templates/agent/identity.md`
- workspace `AGENTS.md`
- workspace `SOUL.md`
- workspace `USER.md`
- `templates/agent/tool_contract.md`
- `memory/MEMORY.md`
- skills summary 或 always-on skills。
- session archived summary。
- recent session history。
- 当前用户消息。
- runtime context。

Runtime Context 只作为运行态元数据：

- 当前时间。
- channel。
- chat_id。
- sender_id。
- session_key。
- workspace。
- 可用 MCP 信息。

安全约束：

- Runtime Context 标记为 metadata，不作为用户指令。
- 外部文档、网页、附件内容应标记为 untrusted。

## 11. 配置设计

根配置：

```python
Config:
  agents
  channels
  providers
  tools
  model_presets
```

删除：

- `api`
- `gateway.heartbeat`
- image generation provider 配置。
- 非 OpenAI-compatible provider 专属配置。

Agent defaults：

```python
workspace
model_preset
model
provider
max_tokens
context_window_tokens
temperature
max_tool_iterations
max_concurrent_subagents
max_tool_result_chars
provider_retry_mode
timezone
bot_name
unified_session
disabled_skills
session_ttl_minutes
max_messages
consolidation_ratio
dream
```

Channels：

```python
channels:
  send_progress
  send_tool_hints
  show_reasoning
  send_max_retries
  transcription_provider
  transcription_language
  feishu
  weixin
  <plugin_channel>
```

Providers：

```python
ProviderConfig:
  api_key
  api_base
  api_type
  extra_headers
  extra_body
```

Tools：

```python
tools:
  web
  exec
  restrict_to_workspace
  mcp_servers
  ssrf_whitelist
```

## 12. 持久化设计

目录结构：

```text
~/.nanobot/config.json

<workspace>/
  AGENTS.md
  SOUL.md
  USER.md
  sessions/
  memory/
    MEMORY.md
    history.jsonl
    .cursor
    .dream_cursor
  media/
  skills/
```

运行态目录：

```text
~/.nanobot/runtime/
  weixin/account.json
```

写入策略：

- session 使用 temp file + replace。
- memory history append 后更新 cursor。
- 关键 overwrite 使用 fsync 或原子替换。
- 损坏文件保留 backup 或 best-effort repair。

## 13. 安全设计

接入安全：

- FeiShu/WeiXin 必须配置 `allow_from` 或 pairing。
- 群聊默认 mention-only。
- pairing code 只在私聊发放。

工具安全：

- `restrict_to_workspace=true` 时，文件和 Shell 只能访问 workspace。
- Web fetch 默认阻止 private/internal 地址。
- SSRF 白名单通过 `tools.ssrf_whitelist` 配置。
- 工具参数通过 JSON Schema 校验。
- 工具结果限制最大字符数，超限截断或落盘。

Provider 安全：

- API key 支持环境变量插值。
- 日志不得输出完整 API key。
- 动态 Provider 只能走 OpenAI-compatible 通用实现，不执行用户代码。

媒体安全：

- 下载文件使用 safe filename。
- media 保存到 workspace 或全局 media 目录。
- 渠道发送前检查文件存在。

## 14. 可靠性设计

模型：

- transient retry。
- retry-after 解析。
- 空响应重试。
- length recovery。

工具：

- 工具异常转为 tool result。
- 重复 workspace violation 给模型明确边界。
- SSRF 作为不可绕过安全边界。

会话：

- 每个 session lock 串行写入。
- checkpoint 记录 awaiting_tools/tools_completed。
- 进程中断后恢复未完成工具状态。

渠道：

- ChannelManager 统一发送重试。
- FeiShu WebSocket 断线重连。
- WeiXin long-poll 失败退避。
- 未知 channel outbound 记录 warning，不影响主循环。

## 15. 测试策略

P0 测试集：

- CLI：
  - `onboard` 生成配置和 workspace。
  - `agent` 单轮调用。
  - 交互模式通过 bus 收发。
- Provider：
  - OpenAICompatProvider tool_call 解析。
  - api_base/api_key/extra_headers/extra_body 透传。
  - 动态 ProviderSpec 匹配。
- Agent：
  - AgentLoop 状态机保存 turn。
  - 同 session 串行。
  - pending injection。
  - checkpoint restore。
  - AgentRunner 工具循环、工具错误、上下文治理。
- Tools/MCP：
  - ToolLoader 内置与插件发现。
  - ToolRegistry 参数校验。
  - MCP tool 注册、过滤、超时。
- Memory：
  - SessionManager JSONL 保存和 repair。
  - Consolidator archive。
  - Dream cursor 成功/失败推进策略。
- SubAgent：
  - spawn、完成回传、失败回传、cancel_by_session。
- Channels：
  - BaseChannel allow_from/pairing。
  - ChannelManager 只加载启用渠道。
  - FeiShu 文本/群聊 mention/topic session。
  - WeiXin 登录状态、消息解析、发送降级。

## 16. 推荐删减实施顺序

1. 冻结精简版范围，移除 WebUI/API/Cron/Heartbeat/图片生成/非目标渠道入口。
2. 简化配置模型，只保留 CLI/Gateway/FeiShu/WeiXin/OpenAI-compatible/Tools/Memory。
3. 简化 ProviderFactory，使所有 Provider 都走 OpenAICompatProvider。
4. 保留 AgentLoop/AgentRunner，清理 WebUI 和 sustained goal 依赖。
5. 保留 Tool/MCP/SubAgent，移除 cron/image/cli_apps 非 P0 工具。
6. 保留 FeiShu、WeiXin、BaseChannel、ChannelManager 和插件发现。
7. 补齐最小测试集。
8. 编写迁移说明和配置模板。
