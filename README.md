# pp-zcode

融合两套上游体系的 zcode 插件：**Matt Pocock 的 Skills** 负责需求工程（做什么、做到什么程度），**PStack（poteto-mode）** 负责工程执行（怎么做、如何证明做对了）。`pipeline` 编排技能把两者接成一条单向推进、每阶段有交付物和验收门槛的流水线。

```
grilling → spec → tickets │ pipeline-execute 执行 │ pipeline-accept 验收
   Matt        Matt  Matt  │     pstack 移植      │      衔接双方
```

## 职责边界

| 环节 | 主导方 | 交付物 | 门禁 |
| --- | --- | --- | --- |
| 需求探索 | Matt `grilling` / `grill-with-docs` | 需求决策记录 | 关键问题已决策 |
| 规格设计 | Matt `to-spec` | tracker 上的 spec（验收标准 + 测试缝） | 标准可测、缝已确认 |
| 任务拆解 | Matt `to-tickets` | 带阻塞边的工单 | 粒度与依赖经用户确认 |
| 实施规划 + 编码 | 本插件 `pipeline-execute` + 7 个 playbook | 代码变更 + 工单证据 | 计划与 spec 一致、spec 只读 |
| 质量审查 + 验证 | 本插件（宿主 glm-reviewer / glm-tester） | 审查与验证证据 | 真实命令输出才算 verified |
| 最终验收 | 本插件 `pipeline-accept` | 逐项验收报告 | 每条标准 pass / fail / unverified |

三条铁律：

1. **Pocock 定标准和拆任务，pipeline-execute 只定执行顺序与技术方案。** 执行阶段发现需求级问题，带着点名的问题退回 spec 阶段，绝不悄悄改 spec 或工单。
2. **审查只做一次。** 规格完整性在 spec 阶段由用户把关；代码正确性在执行阶段由独立审查把关。不加重复的全量 review。
3. **完成必须有证据。** 工单 `verified` 只认本会话内真实运行过的命令输出；环境跑不了的记 `unverified: <需要什么>`，绝不默认通过。

## 插件内容

```
plugins/pp-zcode/
├── .zcode-plugin/plugin.json
└── skills/
    ├── pipeline/              ★ 融合编排：阶段路由 + 门禁 + 流水线契约
    │   └── references/        交接简报模板、目标项目 AGENTS.md 片段
    ├── pipeline-accept/       ★ 最终验收门：spec 验收标准 × 证据矩阵
    ├── pipeline-status/       只读进度查询：阶段判定 + 工单表 + 下一步归属
    ├── pipeline-execute/      执行引擎（pstack poteto-mode 的 zcode 移植版）
    │   └── playbooks/         investigation / bug-fix / feature /
    │                          refactoring / prototype / shipping / opening-a-pr
    ├── how / why / architect / swarm / arena    执行侧路由技能
    ├── unslop / no-comments / technical-writing / benchmark-checklist
    └── principle-*/（24 个）   pstack 原则微技能
```

移植方式沿用 pstack 官方的适配层做法：上游技能**原样保留**，所有 Cursor 专有名称（Task、模型 slug、cloud agent、Bugbot 等）集中在 `pipeline-execute`（poteto-mode 移植版）的 Harness adapter 一张表里映射到 zcode 的对应物（`Agent`、宿主的 glm-coder / glm-reviewer / glm-tester 等专项 agent、`gh`、browser-use 技能）。未随插件携带的上游技能（`interrogate`、`figure-it-out`、`show-me-your-work`、babysit 等）在 Substitutions 表里给了明确的替代行为，不靠猜。

## 依赖

- **Matt Pocock 的需求侧技能**（`grilling`、`to-spec`、`to-tickets`，建议加 `grill-with-docs`、`domain-modeling`、`tdd`、`setup-matt-pocock-skills`）以用户级技能安装（[mattpocock/skills](https://github.com/mattpocock/skills)）。本插件不重复打包它们——`pipeline` 在 Phase 0 会检测，缺了会点名提示安装。
- **宿主专项 agent**（glm-coder / glm-coder-flash / glm-explorer / glm-reviewer / glm-tester）：存在则优先使用，缺失时回落到 general-purpose 并内联委派简报。
- 目标项目先跑一次 `/setup-matt-pocock-skills` 配置 issue tracker。

## 安装

市场目录在仓库根的 `marketplace.json`，添加方式二选一（**粘贴仓库或目录地址，不要粘贴 GitHub 网页里某个文件的链接**）：

- 远程：**Plugin Marketplace → Add → Add Plugin Marketplace**，粘贴 `https://github.com/hi-fangj/pp-zcode`（私有仓库需本机 git 凭证，如 gh 登录）
- 本地：粘贴本仓库的根目录路径

然后 **Personal → pp-zcode-market → pp-zcode → Install**，在目标项目跑一次 `/setup-matt-pocock-skills`，从 `/pipeline` 进入流水线。

## 使用

```
/pipeline 给购物车加一个"稍后再买"列表  # 无 spec → 路由到 grilling
/pipeline                              # 无参数 → 按产物自动判断阶段续跑
/pipeline-accept                       # 执行完成后逐项验收
/pipeline-status 购物车                 # 只读查询：进度在哪、下一步归谁
```

### 场景 → 技能路由

正常需求从 `/pipeline` 进流水线；只想改代码不走全流程，可直接用执行侧技能。

| 你遇到的情况 | 用什么 | 会发生什么 |
| --- | --- | --- |
| 有新需求或想法，还没有 spec | `/pipeline <需求>` | grilling 追问 → to-spec 出规格 → to-tickets 拆工单 → pipeline-execute 执行 → pipeline-accept 验收 |
| 接着上次的活继续，或不确定走到哪步 | `/pipeline`（无参数） | 按 tracker 上的产物判断阶段，交给当前阶段的唯一 owner 续跑 |
| 只想看进度，不动任何东西 | `/pipeline-status <feature>` | 只读报告：阶段判定、工单表、下一个能动的工单、下一步归谁；无参数则一行一个列出所有 open feature |
| 工单全部 verified，要最终验收 | `/pipeline-accept` | 逐条验收标准对证据，输出 pass / fail / unverified 报告 |
| 小活直接改代码，不走完整流水线 | `/pipeline-execute` | 执行引擎按任务形状自动选 playbook（见下表） |

### pipeline-execute 内部：任务形状 → playbook

| 任务形状 | playbook |
| --- | --- |
| 只读问题："X 怎么工作""该做 X 还是 Y" | investigation |
| 报来的缺陷 | bug-fix（先复现，再根因） |
| 新功能或行为变更 | feature |
| 重命名、提取、去重等行为不变的结构调整 | refactoring |
| 设计或实证分歧，用一次性草图定夺 | prototype |
| 一摞已绿的 PR 要落地 | shipping（先独立复核，只落连续验证段） |
| 收尾开 PR | opening-a-pr（每个 playbook 的最后一步） |

没有匹配 playbook 的大活或跨切面改造不在这里即兴发挥：退回 `/pipeline`，在 ticket 阶段拆分。

### 执行侧技能（可单独使用）

| 情况 | 技能 |
| --- | --- |
| "X 是怎么工作的"、改代码前先看懂、该放哪一层 | how |
| "X 为什么这么设计"、决策依据、回溯与复盘 | why |
| 动手前先定类型、签名、模块结构 | architect |
| 并行覆盖、竞速、矩阵式探索 | swarm |
| 多个方案同题比稿，选底座再嫁接 losers 的强项 | arena |
| 写文档、RFC、README、PR 描述、commit message | technical-writing |
| 去掉文字里的 AI 腔 | unslop |
| 审查代码里的注释是否该留 | no-comments |
| 跑基准、报性能数字之前先过一遍 | benchmark-checklist |

### 失败与异常怎么走

| 情况 | 路由 |
| --- | --- |
| 审查或验证失败 | 重开对应工单，回到 pipeline-execute 修 |
| 执行中发现 spec 本身有错（标准不可满足、漏了 case） | 停止执行，点名问题退回 spec 阶段，只对增量重新出票 |
| 交付后用户报缺陷 | spec 没错 → 重开工单回执行；需求错了 → 改 spec，增量重新出票 |
| 环境跑不了的验证 | 记 `unverified: <需要什么人工步骤或设备>`，绝不算完成 |

`principle-*`（24 个）不是调用入口：pipeline-execute 在执行中按需点名加载这些原则微技能（最小改动、根因修复、先证明再宣称完成……），随流水线自动生效。

工单状态机：`ready-for-agent → in-progress → in-review → verified`，另有 `blocked` 与 `unverified: <原因>`。

## 实施路线

- **v0.1（当前）**：串行闭环。单工单流水，一条走通再放开。
- 之后：并行 fan-out（明确文件所有权与合并顺序）、补 `interrogate` / `figure-it-out` 等上游技能、失败重试与任务恢复。

## 上游与许可

- PStack / poteto-mode：[cursor/plugins](https://github.com/cursor/plugins/tree/main/pstack)，Lauren Tan，MIT。移植与原样文件清单见 [NOTICE](plugins/pp-zcode/NOTICE.md)。
- Matt Pocock's skills：[mattpocock/skills](https://github.com/mattpocock/skills)（本插件只引用，不打包）。
