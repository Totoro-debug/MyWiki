# Agent、工具与记忆

自动主题地图：按标题/章节中的术语归组。关联仅表示主题邻近，不表示技术等价。

路由词：Agent、MCP、记忆、Tool、Workflow、Skill、Nanobot

## 来源入口

### [design](../notes/d_00a19d84e16555709c696358.md)

来源：`09-unachive/design.md` · SHA-256 `9b98ffc79a81`

- L417-L461 · nanobot 精简复现版设计文档 > 7. 工具与 MCP 设计 > 7.1 Tool 抽象

  摘录（原文）：

  ```text
  保留：
  ```

- L151-L152 · nanobot 精简复现版设计文档 > 4. Agent 核心设计
- L153-L192 · nanobot 精简复现版设计文档 > 4. Agent 核心设计 > 4.1 AgentLoop

  摘录（原文）：

  ```text
  AgentLoop 是产品层 turn 编排器。
  ```

- L193-L230 · nanobot 精简复现版设计文档 > 4. Agent 核心设计 > 4.2 AgentRunner

  摘录（原文）：

  ```text
  AgentRunner 是模型与工具调用循环，不依赖渠道。
  ```

- 其余 30 个相关章节见来源卡片。

### [Agent](../notes/d_d2c2cbba52e4c44b075985b1.md)

来源：`04-AI/Agent.md` · SHA-256 `e9a35558d95c`

- L7-L11 · Agent 核心模块 > 2. 记忆系统

  摘录（原文）：

  ```text
  - LLM 记忆只局限于上下文窗口，而 Agent 的记忆分为短期和长期记忆，能在交互中保持上下文，并从历史经验中学习。
  ```

- L178-L182 · 四、Agent 设计范式 > (四) Agentic Workflow

  摘录（原文）：

  ```text
  - 纯 Agent 不确定性太高，行为不可控，纯 Workflow 不够灵活，因此最实用的做法就是：整体架构用 Workflow 确保可控性，灵活性要求高的局部用 Agent 保证灵活性。
  ```

- L1-L2 · Agent 核心模块
- L3-L6 · Agent 核心模块 > 1. 工具调用

  摘录（原文）：

  ```text
  - 工具是 Agent 和外部世界交互、执行任务的唯一入口。
  ```

- 其余 40 个相关章节见来源卡片。

### [Nanobot](../notes/d_1948111147ba4d63fa14404f.md)

来源：`05-项目/Nanobot.md` · SHA-256 `0fa880d77493`

- L37-L39 · 二、Core Agent 智能体核心层 > (三) Memory 记忆系统

  摘录（原文）：

  ```text
  - Nanobot 记忆系统采用三层记忆架构：**短期记忆** + **长期记忆** + **历史记录**。
  ```

- L40-L40 · 二、Core Agent 智能体核心层 > (三) Memory 记忆系统 > 1. MemoryStore 记忆存储与管理
- L41-L44 · 二、Core Agent 智能体核心层 > (三) Memory 记忆系统 > 1. MemoryStore 记忆存储与管理 > 1.1 Session JSONL 短期记忆

  摘录（原文）：

  ```text
  - Session 存储一个会话中的 **完整对话历史**、**工具调用记录**、**会话状态上下文**。
  ```

- L45-L49 · 二、Core Agent 智能体核心层 > (三) Memory 记忆系统 > 1. MemoryStore 记忆存储与管理 > 1.2 MEMORY.md 长期记忆

  摘录（原文）：

  ```text
  - Memory 存储 **关键事实、用户偏好、项目状态**等，每次请求都要通过 `read_memory()` 读取并注入 Prompt。
  ```

- 其余 19 个相关章节见来源卡片。

### [detailed-design](../notes/d_92b442e574fb14453e3673eb.md)

来源：`09-unachive/detailed-design.md` · SHA-256 `067bc65c6044`

- L311-L312 · nanobot 详细设计文档 > 9. 上下文、提示词、技能与记忆
- L313-L339 · nanobot 详细设计文档 > 9. 上下文、提示词、技能与记忆 > 9.1 ContextBuilder

  摘录（原文）：

  ```text
  核心文件：`nanobot/agent/context.py`
  ```

- L340-L348 · nanobot 详细设计文档 > 9. 上下文、提示词、技能与记忆 > 9.2 Skills

  摘录（原文）：

  ```text
  技能文件位于：
  ```

- L349-L367 · nanobot 详细设计文档 > 9. 上下文、提示词、技能与记忆 > 9.3 Session

  摘录（原文）：

  ```text
  核心文件：`nanobot/session/manager.py`
  ```

- 其余 49 个相关章节见来源卡片。

### [prd](../notes/d_199411a030d23767f85f18e8.md)

来源：`09-unachive/prd.md` · SHA-256 `061cf34e6fbc`

- L227-L256 · nanobot 精简复现版 PRD > 5. 功能需求 > 5.6 Agent 核心

  摘录（原文）：

  ```text
  AgentLoop 应负责产品层 turn 生命周期：
  ```

- L257-L280 · nanobot 精简复现版 PRD > 5. 功能需求 > 5.7 工具与 MCP

  摘录（原文）：

  ```text
  工具系统应支持：
  ```

- L281-L305 · nanobot 精简复现版 PRD > 5. 功能需求 > 5.8 双层记忆

  摘录（原文）：

  ```text
  短期记忆：
  ```

- L1-L4 · nanobot 精简复现版 PRD

  摘录（原文）：

  ```text
  生成日期：2026-05-28
  ```

- 其余 16 个相关章节见来源卡片。

### [system-overall-design](../notes/d_faf5d2081ba5a11865b45895.md)

来源：`09-unachive/system-overall-design.md` · SHA-256 `293146e77920`

- L94-L128 · nanobot 系统整体设计文档 > 3. 核心模块设计 > 3.3 Agent 编排层

  摘录（原文）：

  ```text
  Agent 编排层负责一次用户请求从恢复、构造上下文、运行、保存到响应的完整生命周期。
  ```

- L129-L161 · nanobot 系统整体设计文档 > 3. 核心模块设计 > 3.4 Agent 执行层

  摘录（原文）：

  ```text
  Agent 执行层负责 LLM 与工具调用循环。它不关心消息来自哪个平台，也不关心最终如何展示。
  ```

- L183-L208 · nanobot 系统整体设计文档 > 3. 核心模块设计 > 3.6 Tool 层

  摘录（原文）：

  ```text
  Tool 层是 Agent 访问外部世界的主要方式。
  ```

- L391-L403 · nanobot 系统整体设计文档 > 5. 关键流程设计 > 5.5 记忆压缩流程
- 其余 33 个相关章节见来源卡片。

### [Super-agent 设计探索（全文转载存档）](../notes/d_8fe0c399fd1ad3ac37c9c8cd.md)

来源：`00-resource/references/dsh-superagent-2026-10-31/Super-agent 设计探索（全文转载存档）.md` · SHA-256 `ec03dd388c88`

- L1-L12 · Super-agent 设计探索：迈向更自主的 Agent 系统

  摘录（原文）：

  ```text
  > 作者：DeepSeek 产品部 / DeepSeek Harness 团队。下载日期：2026-10-31。
  ```

- L13-L54 · Super-agent 设计探索：迈向更自主的 Agent 系统 > 1. Super-agent

  摘录（原文）：

  ```text
  过去一年里，以 Coding Agent 为代表的单任务 Agent 已经证明，模型能够使用工具解决复杂问题，且越来越少需要人类持续监控和逐步干预。与此同时，模型的多 Agent 协同能力也在提升，使跨会话的组织与调度变得可行。随着人类在底层执行中的参与减少，人的角色正逐步上移到更高层的决策与验收。
  ```

- L55-L74 · Super-agent 设计探索：迈向更自主的 Agent 系统 > 2. 双层架构

  摘录（原文）：

  ```text
  要同时实现跨信道的连续交互与多任务的高效并发，系统在底层会话组织上面临连续性与吞吐量之间的根本权衡（Trade-off）。
  ```

- L75-L90 · Super-agent 设计探索：迈向更自主的 Agent 系统 > 2. 双层架构 > 2.1 Router 层

  摘录（原文）：

  ```text
  Router 层是常驻的全局路由层，负责承接所有入口的人类交互。所有跨任务的信息与决策都在 Router 层中汇总，由它充当全局的序点（Sequence Point）、协调点和记忆。为了避免这一全局节点成为系统的性能瓶颈，Router 层在设计上不直接执行具体任务，只负责人类交互与任务分派，甚至可以不配备 Bash 工具。
  ```

- 其余 25 个相关章节见来源卡片。

### [SKILL](../notes/d_010233c1f837a714795b8e6c.md)

来源：`00-resource/references/dsh-superagent-2026-10-31/dsh-superagent-prototype-main/skills/dsh-superagent-feishu/SKILL.md` · SHA-256 `5cd538eef17f`

- L1-L12 · SKILL

  摘录（原文）：

  ```text
  A worker's messages carry each Trigger; read trigger/<id> with orchestrator_read when one is cut or you need its context. Its context references read the source message, its thread …〔截断〕
  ```


### [SKILL](../notes/d_e3e23ac9a99e97db07c0d27c.md)

来源：`00-resource/references/dsh-superagent-2026-10-31/dsh-superagent-prototype-main/skills/dsh-superagent-github/SKILL.md` · SHA-256 `5081401e5381`

- L1-L14 · SKILL

  摘录（原文）：

  ```text
  Workers use orchestrator_read for repository context when needed: github/issues/<number> or github/pulls/<number> for the description; github/issues/<number>/comments/1 for convers …〔截断〕
  ```


### [DeepSeek Super-agent 设计解读](../notes/d_b1545aad8cfdb3030977d192.md)

来源：`04-AI/DeepSeek Super-agent 设计解读.md` · SHA-256 `de5b86c1ecc1`

- L1-L5 · DeepSeek Super-agent 设计解读

  摘录（原文）：

  ```text
  > 阅读日期：2026-10-31。以公开原型提交 `6337fc823ce20251c8de8085948165c81aaa701e` 为源码依据。
  ```

- L6-L13 · DeepSeek Super-agent 设计解读 > 一、它解决什么问题

  摘录（原文）：

  ```text
  单任务 Agent 越来越能自行执行，但同时处理多个任务时，人仍要切换会话、补充上下文、跟进执行、转发结果。Super-agent 把这些管理工作交给系统，使人主要负责确定目标、关键决策与验收。
  ```

- L14-L15 · DeepSeek Super-agent 设计解读 > 二、核心设计
- L16-L23 · DeepSeek Super-agent 设计解读 > 二、核心设计 > 1. Router 管全局，Worker 做具体任务

  摘录（原文）：

  ```text
  Router 是常驻的协调会话，理解新请求、识别任务关系、分派工作、统一沟通。具体编码、测试与问题复现交给上下文隔离的 Worker。每个 Worker 可在内部使用 Subagent，但任务内部的拆解不需要 Router 参与。
  ```

- 其余 9 个相关章节见来源卡片。

### [README](../notes/d_e9fc72155df8d426094a73cf.md)

来源：`00-resource/references/dsh-superagent-2026-10-31/README.md` · SHA-256 `7c8fc46657e2`

- L1-L4 · DeepSeek Super-agent 资料存档

  摘录（原文）：

  ```text
  下载日期：2026-10-31。资料保留原作者署名及源码 MIT 许可证。
  ```

- L5-L13 · DeepSeek Super-agent 资料存档 > 一、设计文章

  摘录（原文）：

  ```text
  - 标题：《Super-agent 设计探索：迈向更自主的 Agent 系统》。
  ```

- L14-L24 · DeepSeek Super-agent 资料存档 > 二、官方源码与文档

  摘录（原文）：

  ```text
  - [官方 GitHub 仓库](https://github.com/deepseek-ai/dsh-superagent-prototype)。
  ```

- L25-L27 · DeepSeek Super-agent 资料存档 > 三、中文解读

  摘录（原文）：

  ```text
  见[DeepSeek Super-agent 设计解读](../../../04-AI/DeepSeek%20Super-agent%20设计解读.md)，包含架构、执行路径、源码入口、实验数据及公开原型与文章设想的区别。
  ```


### [000-philosophy](../notes/d_781cf6489a55a16b5ebe168b.md)

来源：`00-resource/references/dsh-superagent-2026-10-31/dsh-superagent-prototype-main/docs/000-philosophy.md` · SHA-256 `0a1212684355`

- L9-L16 · 000 Philosophy > What follows for the agent

  摘录（原文）：

  ```text
  - **It acts only when asked, or when a written rule allows it.** A request counts only when it addresses the agent directly and comes from a person the team allowed: one on an allo …〔截断〕
  ```


### [006-deployment](../notes/d_0160c7205b26697bd99c2433.md)

来源：`00-resource/references/dsh-superagent-2026-10-31/dsh-superagent-prototype-main/docs/006-deployment.md` · SHA-256 `92c5a1c6aeca`

- L31-L48 · 006 Deployment > Accounts > Agent GitHub account

  摘录（原文）：

  ```text
  1. Create a GitHub user account for the agent and give it write access to the repository. A GitHub App cannot be the agent, because dsh-superagent reads the account's notifications …〔截断〕
  ```

- L244-L247 · 006 Deployment > Upgrade > Agent presets

  摘录（原文）：

  ```text
  The worker and router presets move shell commands to the background after 5 seconds. A Session cannot load without its preset. Keep the `dsh-superagent-worker` and `dsh-superagent- …〔截断〕
  ```


## 相邻主题

- [LLM、RAG 与检索](rag.md)
- [网络、协议与通信](network.md)

## 检索入口

```powershell
python LLMWiki/wiki.py search "Agent"
```
