# pp-zcode

融合两套上游体系的 zcode 插件，两侧技能都随插件打包：**Matt Pocock 的 Skills** 负责需求工程（做什么、做到什么程度），**PStack（poteto-mode）** 负责工程执行（怎么做、如何证明做对了）。没有强制中央路由（可选的 `pp-zcode:ask` 只负责指路）：需求侧技能自由组合，工作多小、流程就多短；`implement-spec` 把 spec（及其工单）交接给 `poteto-mode` 执行引擎，`pipeline-accept` 凭证据逐条验收。

```
pp-zcode:grilling → pp-zcode:to-spec → (pp-zcode:to-tickets) │ pp-zcode:implement-spec │ pp-zcode:poteto-mode → pp-zcode:pipeline-accept
     Pocock              Pocock              Pocock          │         桥接交接        │     pstack 移植           逐条验收
```

## 命名与防冲突

zcode 会把插件技能同时注册为 `pp-zcode:<name>` 和裸名 `<name>`。裸名只是别名：发现顺序里用户级技能优先，所以本机若已安装同名的 `to-spec`、`grilling`、`implement-spec` 等技能，裸名会被用户级副本遮蔽，插件里的版本反而调不到。

因此本插件的规则是：**一律用限定名调用，一律用限定名互相引用**。

- 调用：`/pp-zcode:to-spec`、`/pp-zcode:poteto-mode`、`/pp-zcode:pipeline-accept`……
- 技能文件内部的交叉引用同样写 `pp-zcode:<name>`，包括交给子代理的简报和 playbook 里的路由。
- 裸名只作为别名存在，不写入任何流程、文档或简报。

## 职责边界

| 环节 | 主导方 | 交付物 | 门禁 |
| --- | --- | --- | --- |
| 需求探索 | 本插件 `pp-zcode:grilling` / `pp-zcode:grill-with-docs` | 需求决策记录 | 关键问题已决策 |
| 规格设计 | 本插件 `pp-zcode:to-spec` | tracker 上的 spec（验收标准 + 测试缝） | 标准可测、缝已确认 |
| 任务拆解 | 本插件 `pp-zcode:to-tickets` | 带阻塞边的工单 | 粒度与依赖经用户确认 |
| 实施规划 + 编码 | 本插件 `pp-zcode:implement-spec` → `pp-zcode:poteto-mode` + 7 个 playbook | 代码变更 + 工单证据 | 计划与 spec 一致、spec 只读 |
| 质量审查 + 验证 | 本插件（宿主 glm-reviewer / glm-tester） | 审查与验证证据 | 真实命令输出才算 verified |
| 最终验收 | 本插件 `pp-zcode:pipeline-accept` | 逐项验收报告 | 每条标准 pass / fail / unverified |

三条铁律：

1. **Pocock 定标准和拆任务，poteto-mode 只定执行顺序与技术方案。** 执行阶段发现需求级问题，带着点名的问题退回 spec 阶段，绝不悄悄改 spec 或工单。
2. **审查只做一次。** 规格完整性在 spec 阶段由用户把关；代码正确性在执行阶段由独立审查把关。不加重复的全量 review。
3. **完成必须有证据。** 工单 `verified` 只认本会话内真实运行过的命令输出；环境跑不了的记 `unverified: <需要什么>`，绝不默认通过。

## 插件内容

```
plugins/pp-zcode/
├── .zcode-plugin/plugin.json
└── skills/
    ├── ask/                          入口：按处境路由到合适的技能或流程
    ├── grilling/                     Pocock 需求侧：逐轮追问，设计树推进
    ├── grill-me/                     入口：直接调用 grilling
    ├── grill-with-docs/              入口：grilling + domain-modeling
    ├── domain-modeling/              GLOSSARY.md / ADR 的建立与维护
    ├── to-spec/                      把已谈妥的决策综合成 spec，发布到 tracker
    ├── to-tickets/                   拆成带阻塞边的纵切工单
    ├── setup-matt-pocock-skills/     首次使用前配置 tracker、triage 标签、领域文档
    ├── triage/                       问题与外PR 的分诊状态机，产出 agent brief
    ├── tdd/                          red-green-refactor 参考 + bug 修复回归循环
    ├── codebase-design/              深模块设计的共享词汇
    ├── implement-spec/               ★ 桥接：从 tracker 取 spec/工单，构建交接简报，交给引擎
    │   └── references/               交接简报模板、目标项目 AGENTS.md 片段
    ├── poteto-mode/                  执行引擎（pstack poteto-mode 的 zcode 移植版）
    │   └── playbooks/                investigation / bug-fix / feature /
    │                                 refactoring / prototype / shipping / opening-a-pr
    ├── pipeline-accept/              ★ 最终验收门：spec 验收标准 × 证据矩阵
    ├── pipeline-status/              只读进度查询：阶段判定 + 工单表 + 下一步归属
    ├── how / why / architect / swarm / arena    执行侧路由技能
    ├── unslop / no-comments / technical-writing / benchmark-checklist
    └── principle-*/（24 个）          pstack 原则微技能
```

插件图标在仓库根的 `assets/icon.png`（512×512，SVG 源文件同目录）。ZCode 的市场卡片按 HTTPS URL 加载图标，`marketplace.json` 的 `icon` 指向本仓库该文件的 raw 地址；仓库为私有时 raw 地址不可匿名读取，卡片会退回默认图标。

移植方式沿用 pstack 官方的适配层做法：上游技能**原样保留**，所有 Cursor 专有名称（Task、模型 slug、cloud agent、Bugbot 等）集中在 `poteto-mode` 的 Harness adapter 一张表里映射到 zcode 的对应物（`Agent`、宿主的 glm-coder / glm-reviewer / glm-tester 等专项 agent、`gh`、browser-use 技能）。未随插件携带的上游技能（`interrogate`、`figure-it-out`、`show-me-your-work`、babysit 等）在 Substitutions 表里给了明确的替代行为，不靠猜。

Pocock 技能按上游原文打包，只做了一处机械改动：技能之间的调用与指引改成 `pp-zcode:<name>` 限定名。唯一的内容融合在 `tdd`：保留 Pocock 的测试方法论，并并入 pstack 的 bug 修复循环、跳过规则与证据报告。

## 依赖

- **宿主专项 agent**（glm-coder / glm-coder-flash / glm-explorer / glm-reviewer / glm-tester）：存在则优先使用，缺失时回落到 general-purpose 并内联委派简报。
- **`gh` CLI**：GitHub tracker 上的 spec、工单、验收证据都通过它读写。
- 目标项目先跑一次 `/pp-zcode:setup-matt-pocock-skills` 配置 issue tracker。

Matt Pocock 的需求侧技能已随插件打包，**不需要**再单独安装用户级副本；即使本机装了同名技能，限定名调用也不会受遮蔽影响。

## 安装

市场目录在仓库根的 `marketplace.json`，添加方式二选一（**粘贴仓库或目录地址，不要粘贴 GitHub 网页里某个文件的链接**）：

- 远程：**Plugin Marketplace → Add → Add Plugin Marketplace**，粘贴 `https://github.com/hi-fangj/pp-zcode`（私有仓库需本机 git 凭证，如 gh 登录）
- 本地：粘贴本仓库的根目录路径

然后 **Personal → pp-zcode-market → pp-zcode → Install**，在目标项目跑一次 `/pp-zcode:setup-matt-pocock-skills` 配置 issue tracker。

## 使用

```
/pp-zcode:ask 给购物车加一个"稍后再买"列表  # 不确定用哪个技能：按处境指路
/pp-zcode:grill-me 给购物车加一个"稍后再买"列表  # 追问清需求（要沉淀 ADR/词汇表用 /pp-zcode:grill-with-docs）
/pp-zcode:to-spec                              # 把已谈妥的决策综合成 spec，发布到 tracker
/pp-zcode:to-tickets                           # 大活才需要：把 spec 拆成带阻塞边的纵切工单
/pp-zcode:implement-spec                       # 取 spec（和工单）→ 交接简报 → poteto-mode 执行
/pp-zcode:poteto-mode 修复登录超时              # 小活直接进引擎，按任务形状选 playbook
/pp-zcode:pipeline-accept                      # spec 背书的活执行完后逐条验收
/pp-zcode:pipeline-status 购物车                # 只读查询：进度在哪、下一步归谁
```

### 场景 → 技能路由

需求侧技能自由组合，执行和验收用本插件。没有必经的固定链条——工作多小，流程就多短：小活 grill 完直接 `/pp-zcode:poteto-mode`；一个完整 feature 出完 spec 直接实现；多部分/跨切面的活才拆票。

| 你遇到的情况 | 用什么 | 会发生什么 |
| --- | --- | --- |
| 不确定该用哪个技能、该从哪一步开始 | `/pp-zcode:ask <你的情况>` | 按处境路由到最合适的技能或流程并说明理由；要动手时直接接手 |
| 有新需求或想法，还没谈清 | `/pp-zcode:grill-me`（要沉淀 ADR/词汇表用 `/pp-zcode:grill-with-docs`） | 逐轮追问，直到关键问题全部决策 |
| 决策已敲定，要固化成规格 | `/pp-zcode:to-spec` | 只综合、不再追问，发布 spec 到 tracker 并打 `ready-for-agent` |
| spec 太大，要拆成可独立验证的工单 | `/pp-zcode:to-tickets` | 纵切工单 + 阻塞边，粒度经你确认 |
| spec（和工单）就绪，开始实现 | `/pp-zcode:implement-spec` | 从 tracker 取件 → 构建交接简报 → `poteto-mode` 按工单或按 spec 整体执行，证据纪律全程生效 |
| 小活直接改代码，不值得出 spec | `/pp-zcode:poteto-mode` | 执行引擎按任务形状自动选 playbook（见下表） |
| 工单全部 verified，要最终验收 | `/pp-zcode:pipeline-accept` | 逐条验收标准对证据，输出 pass / fail / unverified 报告 |
| 只想看进度，不动任何东西 | `/pp-zcode:pipeline-status <feature>` | 只读报告：阶段判定、工单表、下一个能动的工单、下一步归谁 |
| 新 issue 或外部 PR 要归类、补信息、写 agent brief | `/pp-zcode:triage` | 按五类 triage 角色推进状态机，必要时先 grill，再产出可执行的 brief |

### poteto-mode 内部：任务形状 → playbook

| 任务形状 | playbook |
| --- | --- |
| 只读问题："X 怎么工作""该做 X 还是 Y" | investigation |
| 报来的缺陷 | bug-fix（先复现，再根因） |
| 新功能或行为变更 | feature |
| 重命名、提取、去重等行为不变的结构调整 | refactoring |
| 设计或实证分歧，用一次性草图定夺 | prototype |
| 一摞已绿的 PR 要落地 | shipping（先独立复核，只落连续验证段） |
| 收尾开 PR | opening-a-pr（每个 playbook 的最后一步） |

没有匹配 playbook 的大活或跨切面改造不在这里即兴发挥：先 `/pp-zcode:to-tickets` 拆成工单，再经 `/pp-zcode:implement-spec` 进来。

### 执行侧技能（可单独使用）

| 情况 | 技能 |
| --- | --- |
| "X 是怎么工作的"、改代码前先看懂、该放哪一层 | `/pp-zcode:how` |
| "X 为什么这么设计"、决策依据、回溯与复盘 | `/pp-zcode:why` |
| 动手前先定类型、签名、模块结构 | `/pp-zcode:architect` |
| 并行覆盖、竞速、矩阵式探索 | `/pp-zcode:swarm` |
| 多个方案同题比稿，选底座再嫁接 losers 的强项 | `/pp-zcode:arena` |
| 写文档、RFC、README、PR 描述、commit message | `/pp-zcode:technical-writing` |
| 去掉文字里的 AI 腔 | `/pp-zcode:unslop` |
| 审查代码里的注释是否该留 | `/pp-zcode:no-comments` |
| 跑基准、报性能数字之前先过一遍 | `/pp-zcode:benchmark-checklist` |

### 失败与异常怎么走

| 情况 | 路由 |
| --- | --- |
| 审查或验证失败 | 重开对应工单，回到 poteto-mode 修 |
| 执行中发现 spec 本身有错（标准不可满足、漏了 case） | 停止执行，点名问题退回 spec 阶段，只对增量重新出票 |
| 交付后用户报缺陷 | spec 没错 → 重开工单回执行；需求错了 → 改 spec，增量重新出票 |
| 环境跑不了的验证 | 记 `unverified: <需要什么人工步骤或设备>`，绝不算完成 |

`principle-*`（24 个）不是调用入口：poteto-mode 在执行中按需点名加载这些原则微技能（最小改动、根因修复、先证明再宣称完成……），随执行自动生效。

工单状态机：`ready-for-agent → in-progress → in-review → verified`，另有 `blocked` 与 `unverified: <原因>`。

## 实施路线

- **v0.6（当前）**：新增 `pp-zcode:ask` 技能路由器：按处境把工作导向插件内合适的技能与流程，不引入强制链条。
- **v0.5**：Pocock 需求侧技能（含 triage）随插件打包，所有技能统一以 `pp-zcode:<name>` 限定名调用与互相引用，避免用户级同名技能遮蔽。
- **v0.4**：去掉中央路由。需求链自由组合，`implement-spec` 桥接 + `poteto-mode` 直入口；串行闭环维持。
- 之后：并行 fan-out（明确文件所有权与合并顺序）、补 `interrogate` / `figure-it-out` 等上游技能、失败重试与任务恢复。

## 上游与许可

- PStack / poteto-mode：[cursor/plugins](https://github.com/cursor/plugins/tree/main/pstack)，Lauren Tan，MIT。移植与原样文件清单见 [NOTICE](plugins/pp-zcode/NOTICE.md)。
- Matt Pocock's skills：[mattpocock/skills](https://github.com/mattpocock/skills)，MIT。打包清单与改动见 [NOTICE](plugins/pp-zcode/NOTICE.md)。
