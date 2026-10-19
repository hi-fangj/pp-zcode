# pp-zcode

融合两套上游体系的 zcode 插件，两侧技能都随插件打包：**Matt Pocock 的 Skills** 负责需求工程（做什么、做到什么程度），**PStack（poteto-mode）** 负责工程执行（怎么做、如何证明做对了）。没有强制中央路由（可选的 `pp-zcode:ask` 只负责指路）：需求侧技能自由组合，工作多小、流程就多短；`implement-spec` 把 spec（及其工单）交接给 `poteto-mode` 执行引擎，执行侧的独立评审走 Pocock 的双轴 `code-review`，`pipeline-accept` 凭证据逐条验收并补扫范围蔓延。

```
pp-zcode:grilling → pp-zcode:to-spec → (pp-zcode:to-tickets) │ pp-zcode:implement-spec │ pp-zcode:poteto-mode → pp-zcode:pipeline-accept
     Pocock              Pocock              Pocock          │         桥接交接        │ pstack 移植，独立评审走 code-review   逐条验收 + code→spec 补扫
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
| 质量审查 + 验证 | 本插件 `pp-zcode:code-review`（评审员 glm-reviewer）+ glm-tester 验证 | 审查与验证证据 | 真实命令输出才算 verified |
| 最终验收 | 本插件 `pp-zcode:pipeline-accept` | 逐项验收报告 | 每条标准 pass / fail / unverified，外加 code → spec 补扫 |

三条铁律：

1. **Pocock 定标准和拆任务，poteto-mode 只定执行顺序与技术方案。** 执行阶段发现需求级问题，带着点名的问题退回 spec 阶段，绝不悄悄改 spec 或工单。
2. **审查只做一次。** 规格完整性在 spec 阶段由用户把关；代码正确性在执行阶段由独立审查（`pp-zcode:code-review`）把关，验收阶段只补一次 code → spec 方向的范围检查。不加重复的全量 review。
3. **完成必须有证据。** 工单 `verified` 只认本会话内真实运行过的命令输出；环境跑不了的记 `unverified: <需要什么>`，绝不默认通过。

## 插件内容

```
plugins/pp-zcode/
├── .zcode-plugin/plugin.json
├── agents/
│   └── comment-sicko.md              只读注释审查子代理（no-comments 调用）
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
    ├── code-review/                  Pocock 双轴 diff 评审：repo 规范 + smell 基线；spec 保真（含范围蔓延）
    ├── implement-spec/               ★ 桥接：从 tracker 取 spec/工单，构建交接简报，交给引擎
    │   └── references/               交接简报模板、目标项目 AGENTS.md 片段
    ├── poteto-mode/                  执行引擎（pstack poteto-mode 的 zcode 移植版）
    │   ├── playbooks/                investigation / bug-fix / feature / refactoring /
    │   │                             prototype / session-pickup / pause-safely /
    │   │                             shipping / opening-a-pr
    │   └── scripts/                  session-store.py（只读会话检索）
    ├── pipeline-accept/              ★ 最终验收门：spec 验收标准 × 证据矩阵
    ├── pipeline-status/              只读进度查询：阶段判定 + 工单表 + 下一步归属
    ├── how / why / teach / blast-radius / architect / swarm / arena   执行侧路由技能
    ├── interrogate/                  ★ 对抗评审：按配置的模型面板逐一向变更开火，合成一个裁决
    │   └── references/               评审提示词、评分表、代码质量视角、主审判断框架
    ├── reflect/                      会话复盘：三个视角并行审查，学习点路由到技能编辑
    │   └── references/               判断 / 工具 / 发散评审提示词 + 合成器
    ├── recall/                       跨会话重建近期上下文，输出现状简报
    ├── show-me-your-work/            长任务决策日志（TSV + log.sh + 模板）
    ├── correct/                      把重复出现的 agent 错误固化成架构 / 类型 / lint / 测试
    ├── typescript-best-practices/    TS 类型纪律与 patterns.md
    ├── create-verification-skill/    生成项目级 verify-<app> 技能与 feature map
    ├── maintain-verification-skill/  定期校正 verify 技能与 feature map
    ├── create-formal-verification-skill/   生成项目级形式化验证技能
    ├── maintain-formal-verification-skill/ 代码变更后让形式化验证回到同步状态
    ├── setup-models/                 ★ 模型角色配置：写 ~/.zcode/pp-zcode/models.md，生成预设 agent
    ├── unity-development/            Unity 执行参考：按层选编译 / EditMode / PlayMode / 手动证据
    │   └── references/               证据矩阵、test-first 准入条件、命令层级
    ├── unity-development-setup/      Unity 项目一次性适配：探测工程结构，写验证矩阵与 agent 声明
    │   └── references/               docs/agents/unity-development.md 模板
    ├── unslop / no-comments / technical-writing / benchmark-checklist
    └── principle-*/（24 个）          pstack 原则微技能
```

插件还随包携带 `agents/comment-sicko.md`（`no-comments` 的只读注释审查子代理）。`plugin.json` 的 `agents` 字段指向该目录；agent 不可用时 `no-comments` 回落到 `general-purpose` 并内联同一份 brief。

插件图标在仓库根的 `assets/icon.png`（512×512，SVG 源文件同目录）。ZCode 的市场卡片按 HTTPS URL 加载图标，`marketplace.json` 的 `icon` 指向本仓库该文件的 raw 地址；仓库为私有时 raw 地址不可匿名读取，卡片会退回默认图标。

移植方式沿用 pstack 官方的适配层做法：上游技能**原样保留**，所有 Cursor 专有名称（Task、模型 slug、cloud agent、Bugbot 等）集中在 `poteto-mode` 的 Harness adapter 一张表里映射到 zcode 的对应物（`Agent`、宿主的 glm-coder / glm-reviewer / glm-tester 等专项 agent、`gh`、browser-use 技能）。未随插件携带的上游技能（`figure-it-out`、babysit、orchestrate 等）在 Substitutions 表里给了明确的替代行为，不靠猜。常规评审由 Pocock 的 `code-review` 承担（评审员是 glm-reviewer），`interrogate` 是争议时的多模型对抗升级。

Pocock 技能按上游原文打包，机械改动只有一处：技能之间的调用与指引改成 `pp-zcode:<name>` 限定名。两个例外：`code-review` 的子代理机制映射到宿主 `Agent` 工具、issue 查询指向 tracker 工作流，并接线进执行与验收两侧；`tdd` 做了内容融合——保留 Pocock 的测试方法论，并入 pstack 的 bug 修复循环、跳过规则与证据报告。

## 模型角色

执行侧技能不写死模型。它们读 `~/.zcode/pp-zcode/models.md` 一张角色表，逐行决定每个席位用什么模型、什么推理等级；文件不存在时每个角色都是 `inherit-parent`，即跟随会话模型。

- **写配置**：`/pp-zcode:setup-models`。它检测本机可用模型、询问预算档位（unlimited / large / medium / small）、可选生成"两家族面板"，然后写入角色表。
- **生效方式**：标量角色（feature / bug-fix / how explorer / why synthesizer 等）钉了真实模型时，setup 会生成 `~/.zcode/agents/pp-zcode-<role>.md` 预设 agent；面板角色（`arena runners`、`architect runners`、`interrogate reviewers`）直接把模型列表写进 dynamic workflow，一个条目一个子代理。
- **刷新已保存 workflow**：`setup-models` 会检测 `~/.zcode/workflows/pp-zcode-*.dwf.ts` 里钉住的模型是否与角色表一致，过期就重新生成。
- **对抗评审**：`/pp-zcode:interrogate` 按 `interrogate reviewers` 行逐一 spawn reviewer。信号来自模型多样性，而不是给每个 reviewer 分配不同人设；主会话按 Act on / Consider / Noted / Dismissed 四档合成裁决。

## Unity 项目

Unity 工程没有通用的命令行测试套件，照搬 `/pp-zcode:tdd` 的 red-green 前置会卡住。插件用一对技能解决：

- **`/pp-zcode:unity-development-setup`**（每个 Unity 工程跑一次）：探测 Unity 版本、asmdef 程序集、生成代码边界、测试 runner、Editor 自动化与高风险链路；写 `docs/agents/unity-development.md`（每个 layer 的最小编译检查 + 行为证据矩阵），并把 `### Unity development` 声明加入 `AGENTS.md` 或 `CLAUDE.md`。
- **`pp-zcode:unity-development`**（模型可自动加载）：`poteto-mode` 在识别到 Unity 仓库时先加载它。它把 test-first 当作可选反馈环：有确定性 seam 和 runner 才走 red-green，否则用"最小改动 → 编译受影响程序集 → 跑最近的 Unity 行为"的纵切；完成证据必须是实际跑过的编译、EditMode/PlayMode 或明确标注的 `unverified` 手动场景。

仓库已有的 `docs/agents/unity-development.md` 优先于技能的通用矩阵，重跑 setup 只更新文档和声明，不覆盖工程自己的规则。

## 依赖

- **宿主专项 agent**（glm-coder / glm-coder-flash / glm-explorer / glm-reviewer / glm-tester）：存在则优先使用，缺失时回落到 general-purpose 并内联委派简报。
- **`gh` CLI**：GitHub tracker 上的 spec、工单、验收证据都通过它读写。
- 目标项目先跑一次 `/pp-zcode:setup-matt-pocock-skills` 配置 issue tracker。
- Unity 项目再跑一次 `/pp-zcode:unity-development-setup` 生成验证矩阵。

Matt Pocock 的技能（需求侧 + `code-review`）已随插件打包，**不需要**再单独安装用户级副本；即使本机装了同名技能，限定名调用也不会受遮蔽影响。

## 安装

市场目录在仓库根的 `marketplace.json`，添加方式二选一（**粘贴仓库或目录地址，不要粘贴 GitHub 网页里某个文件的链接**）：

- 远程：**Plugin Marketplace → Add → Add Plugin Marketplace**，粘贴 `https://github.com/hi-fangj/pp-zcode`（私有仓库需本机 git 凭证，如 gh 登录）
- 本地：粘贴本仓库的根目录路径

然后 **Personal → pp-zcode-market → pp-zcode → Install**，在目标项目跑一次 `/pp-zcode:setup-matt-pocock-skills` 配置 issue tracker。想调整执行侧各席位的模型，再跑一次 `/pp-zcode:setup-models`（可选）。

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
/pp-zcode:code-review main                     # 常规评审：自 main 以来的 diff，规范轴 + spec 轴并行
/pp-zcode:interrogate                          # 对抗评审：按配置的模型面板逐一向当前变更开火
/pp-zcode:setup-models                         # 配置各席位模型与推理档位（可选，默认全跟随会话模型）
/pp-zcode:unity-development-setup              # Unity 工程首次适配：写验证矩阵与 agent 声明
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
| 一段改动写完了，要评审（branch、PR、自某点以来的 diff） | `/pp-zcode:code-review <固定点>` | 双轴并行：repo 规范 + Fowler smell 基线；spec 轴对照工单/spec 查缺失、做错与范围蔓延 |
| 工单全部 verified，要最终验收 | `/pp-zcode:pipeline-accept` | 逐条验收标准对证据，输出 pass / fail / unverified 报告，附 code → spec 补扫 |
| 只想看进度，不动任何东西 | `/pp-zcode:pipeline-status <feature>` | 只读报告：阶段判定、工单表、下一个能动的工单、下一步归谁 |
| 新 issue 或外部 PR 要归类、补信息、写 agent brief | `/pp-zcode:triage` | 按五类 triage 角色推进状态机，必要时先 grill，再产出可执行的 brief |
| 想换某个席位的模型、或让评审跨模型家族 | `/pp-zcode:setup-models` | 检测可用模型 → 选预算档位 → 写角色表并按需生成预设 agent |
| 第一次在 Unity 工程里干活 | `/pp-zcode:unity-development-setup` | 探测程序集、生成代码边界、测试 runner 与高风险链路，写验证矩阵并声明执行技能 |
| Unity 里实现、修 bug、重构或写测试 | `pp-zcode:unity-development` | 按 layer 选最小编译检查与行为证据；没有确定性 seam 时不强行 red-green |

### poteto-mode 内部：任务形状 → playbook

| 任务形状 | playbook |
| --- | --- |
| 只读问题："X 怎么工作""该做 X 还是 Y" | investigation |
| 报来的缺陷 | bug-fix（先复现，再根因） |
| 新功能或行为变更 | feature |
| 重命名、提取、去重等行为不变的结构调整 | refactoring |
| 设计或实证分歧，用一次性草图定夺 | prototype |
| 接手一个上次没做完的会话 | session-pickup（先读旧轨迹，不重做） |
| 要停下、交给下一个会话继续 | pause-safely（`wip:` commit + 恢复笔记） |
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
| 常规评审一段 diff：规范 + smell 基线 + spec 保真 | `/pp-zcode:code-review` |
| 对抗评审：多模型独立挑刺，合成一个裁决 | `/pp-zcode:interrogate` |
| 配置执行侧各席位的模型与推理档位 | `/pp-zcode:setup-models` |
| 把一段东西真正讲明白（how + why 合成） | `/pp-zcode:teach` |
| 小改动怕炸到别处，先查影响面 | `/pp-zcode:blast-radius` |
| 长任务 / 无人值守工作留可审计决策日志 | `/pp-zcode:show-me-your-work` |
| 同一类 agent 错误反复出现，想从结构上堵掉 | `/pp-zcode:correct` |
| 写或改 `.ts` / `.tsx`，先对齐类型纪律 | `/pp-zcode:typescript-best-practices` |
| 会话复盘，把经验落回技能 | `/pp-zcode:reflect` |
| 跨会话恢复上下文，先知道上次停在哪 | `/pp-zcode:recall` |
| 项目没有可脚本化驱动真实应用的手段 | `/pp-zcode:create-verification-skill` |
| 保持 verify 技能与 feature map 不腐烂 | `/pp-zcode:maintain-verification-skill` |
| 并发 / 状态机 / 解析器需要测试之外的证明 | `/pp-zcode:create-formal-verification-skill` |
| 代码变了，形式化验证要重新对齐 | `/pp-zcode:maintain-formal-verification-skill` |
| 写文档、RFC、README、PR 描述、commit message | `/pp-zcode:technical-writing` |
| 去掉文字里的 AI 腔 | `/pp-zcode:unslop` |
| 审查代码里的注释是否该留 | `/pp-zcode:no-comments` |
| 跑基准、报性能数字之前先过一遍 | `/pp-zcode:benchmark-checklist` |

### 失败与异常怎么走

| 情况 | 路由 |
| --- | --- |
| 评审（`pp-zcode:code-review` / interrogate）或验证失败 | 重开对应工单，回到 poteto-mode 修 |
| 验收补扫发现范围蔓延 | 回 poteto-mode 删除或说明保留理由；确属需求的先回 spec 阶段，增量重新出票 |
| 执行中发现 spec 本身有错（标准不可满足、漏了 case） | 停止执行，点名问题退回 spec 阶段，只对增量重新出票 |
| 交付后用户报缺陷 | spec 没错 → 重开工单回执行；需求错了 → 改 spec，增量重新出票 |
| 环境跑不了的验证 | 记 `unverified: <需要什么人工步骤或设备>`，绝不算完成 |

`principle-*`（24 个）不是调用入口：poteto-mode 在执行中按需点名加载这些原则微技能（最小改动、根因修复、先证明再宣称完成……），随执行自动生效。

工单状态机：`ready-for-agent → in-progress → in-review → verified`，另有 `blocked` 与 `unverified: <原因>`。

## 实施路线

- **v0.9（当前）**：收编 Pocock 上游 `code-review` 为 `pp-zcode:code-review`（双轴：repo 规范 + Fowler smell 基线、spec 保真）。`poteto-mode` 的独立评审改走该协议，`pipeline-accept` 验收门新增 code → spec 补扫抓范围蔓延，`ask` 增加路由。
- **v0.8**：对齐 pstack-zcode v0.15.28。修正 `why`、`bug-fix`、`shipping`、`opening-a-pr` 里会在 zcode 下失效的 Cursor 机制；`no-comments` 改走插件自带 `comment-sicko` agent（缺失时回落 `general-purpose`）。新增上游技能 `show-me-your-work`、`blast-radius`、`correct`、`teach`、`typescript-best-practices`、`reflect`、`recall`、`create-verification-skill`、`maintain-verification-skill`、`create-formal-verification-skill`、`maintain-formal-verification-skill`，以及 `session-pickup` / `pause-safely` 两个 playbook；`setup-models` 增加 reflect 角色行。
- **v0.7**：移植 pstack-zcode 的模型角色机制：新增 `pp-zcode:setup-models`（角色表 + 预算档位 + 预设 agent + workflow 刷新）与 `pp-zcode:interrogate`（多模型对抗评审）；执行侧技能改为读取 `~/.zcode/pp-zcode/models.md`，不再引用 Cursor 规则或写死模型 slug。
- **v0.6**：新增 `pp-zcode:ask` 技能路由器：按处境把工作导向插件内合适的技能与流程，不引入强制链条。
- **v0.5**：Pocock 需求侧技能（含 triage）随插件打包，所有技能统一以 `pp-zcode:<name>` 限定名调用与互相引用，避免用户级同名技能遮蔽。
- **v0.4**：去掉中央路由。需求链自由组合，`implement-spec` 桥接 + `poteto-mode` 直入口；串行闭环维持。
- 之后：并行 fan-out（明确文件所有权与合并顺序）、补 `figure-it-out` 等上游技能、失败重试与任务恢复。

## 上游与许可

- PStack / poteto-mode：[cursor/plugins](https://github.com/cursor/plugins/tree/main/pstack)，Lauren Tan，MIT。移植与原样文件清单见 [NOTICE](plugins/pp-zcode/NOTICE.md)。
- Matt Pocock's skills：[mattpocock/skills](https://github.com/mattpocock/skills)，MIT。打包清单与改动见 [NOTICE](plugins/pp-zcode/NOTICE.md)。
