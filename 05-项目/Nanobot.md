# 一、GateWay 网关层

## (一) ChannelManager

- 外部平台管理

## (二) MessageBus 消息总线

- 使用**生产者-消费者**模式，分为 Inbound Queue 和 Outbound Queue。
- 消息队列使用 asyncio.Queue 实现，非阻塞的消息传递模式，支持高并发。

# 二、Core Agent 智能体核心层

- Agent 核心模块，主要包括消息消费、ReAct 架构、提示词构建、记忆管理、子 Agent 管理。

## (一) AgentLoop 智能体循环
- `AgentLoop.run()` 负责整个智能体的循环，是最顶层的 Agentic Workflow，其中任务执行部分交给 ReAct 处理。
1. 从 `MessageBus.Inbound_Queue` 中获取消息。
2. 创建**会话锁**，保证同一会话中的消息串行执行。
3. 创建**并发令牌**，控制并发处理的会话数量 (默认并发数为 3)。
4. 创建 AgentRunner，初始化 agent 工作区、供应商配置、工具列表等。
5. `AgentRunner.run()` 通过 ReAct 循环执行任务。
6. 调用 `_save_turn()` 将对话持久化到 **Session Jsonl** 中。
7. 将结果发送到 `MessageBus.Outbound_Queue` 中。

## (二) AgentRunner 智能体执行
- `AgentRunner.run()` 实现了基础的 **ReAct** 循环 (默认**最多循环 40 次**)，实现了典型的“思考-执行-观察”的循环。
1. ReAct 循环**前置 Hook**，如：日志记录、状态检查等。
2. 调用大模型进行思考。
3. 存在 **tool_calls**：
	1. 工具调用**前置 Hook**，如：权限检查、安全检查等。
	2. 工具调用。
	3. 处理工具返回的结果。
	4. ReAct 循环**后置 Hook**，如：结果记录、数据统计等。
4. 没有 tool_calls，任务完成，退出循环。

## (三) Memory 记忆系统
- Nanobot 记忆系统采用三层记忆架构：**短期记忆** + **长期记忆** + **历史记录**。
- **记忆存储**：三层记忆全部存储在文件中，无外部依赖、开箱即用、用户可编辑。
### 1. MemoryStore 记忆存储与管理
#### 1.1 Session JSONL 短期记忆
- Session 存储一个会话中的 **完整对话历史**、**工具调用记录**、**会话状态上下文**。
- Session 采用 JSONL 格式，非常适合追加方式写入，利于对话过程中的动态、流式写入。

#### 1.2 MEMORY.md 长期记忆
- Memory 存储 **关键事实、用户偏好、项目状态**等，每次请求都要通过 `read_memory()` 读取并注入 Prompt。
- Memory 采用 Markdown 文件存储，同时利好 LLM、Agent、用户，用户可以自行编辑。
- 由模型自行决定是否调用 `save_memory()` 以**覆盖**的方式对长期记忆的进行更新。

#### 1.3 HISTORY.md 历史事件
- History 按时间顺序组织**事件摘要**，每次只在文件末尾追加事件摘要，由 LLM 调用工具按需查找。
- 当 HISTORY.md 增长到一定大小后，会触发 **MemoryConsolidator** 对较旧的历史记录进行压缩，保留最近的历史记录。

### 2. MemoryConsolidator 记忆压缩器
- 每次构建完当前 prompt 后，就要判断该 prompt 是否会超出上下文窗口，如果超出就触发记忆压缩。
- 然后将更新后的 Memory 写入文件，并追加事件摘要到 History 末尾。最后丢弃被压缩的对话历史。


## (四) ContextBuilder 提示词构造器


## (五) SubAgent Manager 子代理管理

# 三、Provider 模型供应商层

- 对供应商以及 LLM 进行封装，屏蔽差异。

# 四、Skill 技能层
## (一) Skill 发现与注册
- Nanobot 在两个位置搜索 skill，一是程序内置 skill 路径，二是工作目录下的 skills 子目录。Nanobot 首先加载并注册内置 skill，然后加载并注册工作目录中的用户自定义 skill。
- Skill 注册时用 skill 的名字作为唯一 ID，因此用户自定义 skill 会覆盖同名的内置 skill。

# 五、Tool 工具层

## (一) Built-in Tools 内置工具
- 内置工具主要包含：
	1. 文件读写与修改。
	2. 命令行执行工具。
	3. Web 网页搜索相关工具。
	4. 启动子代理工具。

## (二) MCP Tools 外部 MCP 工具
### 1. MCPToolWrapper
- MCP 工具包装类，用来将 MCP Server 中工具包装为内置工具的格式，实现**无缝集成**和**接口统一**。

### 2. MCP Server 配置
- 在配置文件中配置 MCP Server，agent 启动时会尝试连接 MCP Server 并获取工具列表，然后将 MCP tools 注册到注册中心。

## (三) ToolRegistry 工具注册中心
- ToolRegistry 负责工具的统一注册与调用，包括：内置、MCP 和自定义。