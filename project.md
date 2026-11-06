# 设计智能体：设计判断沉淀回流

## 目标（一句话）

做一个能给别人用的系统：别人的 agent 挂上我们的 skill，就能查设计规范和业务知识库、生成界面 demo；每轮的产物、用户原话、自评好坏自动记下来传回云端；云端整理后把提炼出的规则写回知识库，下次所有人挂上就拿到新的。

## 定下来的事（不要推翻，除非用户改主意）

- 本地 agent 用 Qoder，不用 Claude Code。
- 用户侧只做一次操作：复制一个 skill 文件夹，不用分清 MCP 还是 skill。
- 先做 skill，不做插件（开发成本高、上平台要审核）；MCP 服务也不搭，本地脚本够用，后面要给程序调用再加。
- 云端用阿里内部知识库 kbase 的 MCP 服务，不自己搭后台数据库。
- 回传存两层：原始区每轮原样存，知识区只存提炼后的规则（带支持次数、接受率、来源）。
- 质量由云端 agent 定期整理把关：去重、合并、过滤一次性意见、算接受率，够格才进知识区；冲突的标给管理员看。
- 上传默认不同意，须用户单独同意；传之前本地脱敏；数据存境内。
- 说话规矩：给用户看的文档用简体中文，先讲怎么做、少用技术词；对外技术分析用正式书面语、每段一个要点、禁用长难句与口语。

## 目标与子目标

### 目标 1：本地 skill 可用 ✅

| 子目标 | 状态 | 证据 / 位置 |
| --- | --- | --- |
| SKILL.md：先读规范再生成、生成后自评、每轮记一条、会话结束上传 | ✅ | design-judgment/SKILL.md |
| 记录/上传脚本（自包含，复用原型逻辑） | ✅ | design-judgment/scripts/ |
| 示例设计规范 YAML + 示例业务知识库 | ✅ | design-judgment/knowledge/ |
| INSTALL.md：一步安装说明 | ✅ | design-judgment/INSTALL.md |
| 本地端到端跑通（3 轮记→脱敏→上传→接收→看板） | ✅ | design-judgment/verification.md |

### 目标 2：记录与上传自动跑起来 🔄

| 子目标 | 状态 | 证据 / 位置 |
| --- | --- | --- |
| 每轮记一条（产物+原话+改动+接受/打回） | ✅ | verification.md 第 3 节 |
| 本地脱敏（敏感词变 ***） | ✅ | verification.md 第 3 节 |
| 同意开关默认关，没同意不传 | ✅ | verification.md 第 4、5 节 |
| 断网重传（失败留队列、指数退避、恢复后补发） | ✅ | verification.md 第 7 节 |
| 在真 Qoder 里装上并跑一轮 | ⬜ | 需在用户装 Qoder 的电脑上动手 |
| agent 在真实会话里每轮都记得记 | ⬜ | 跑一阵看效果；不行再加插件/钩子兜底 |

### 目标 3：云端接住并整理（kbase） ⏸️ 等 kbase 信息

| 子目标 | 状态 | 备注 |
| --- | --- | --- |
| 确认 kbase MCP 工具清单（有没有写工具、叫什么、参数） | ⬜ | 等用户发文档/链接 |
| 确认认证方式（个人 token 还是团队 token） | ⬜ | 同上 |
| 确认单条大小限制、能不能挂快照 | ⬜ | 同上 |
| 确认云端 agent 跑在哪（kbase 自带还是定时跑） | ⬜ | 同上 |
| 上传脚本改调 kbase MCP（脚本当客户端） | ⬜ | 前四项确认后做 |
| 原始区 + 知识区两层落好 | ⬜ | 同上 |

### 目标 4：云端反哺知识库 ⬜

| 子目标 | 状态 | 备注 |
| --- | --- | --- |
| 云端 agent 定期整理（去重、合并、过滤、算接受率） | ⬜ | 依赖目标 3 |
| 规则晋升线（出现几次、接受率多高才进知识区） | ⬜ | 参考 ClawHub 7 天 3 次、Agentic Cortex 三件套 |
| 冲突规则标给管理员审 | ⬜ | 同上 |
| skill 改从 kbase 现读知识 | ⬜ | 云端一改，所有人下次挂上就拿到新的 |

### 目标 5：给别人用 ⬜

| 子目标 | 状态 | 备注 |
| --- | --- | --- |
| 传到 GitHub，npx skills add 一条命令能装 | ⬜ | skill 还没传 GitHub，INSTALL.md 里那条现在走不通 |
| 同意、脱敏、隐私说明写进文档 | ⬜ |  |
| 换真实设计规范 + 业务知识库 | ⬜ | 等用户发真实文件，替换 knowledge/ 两个文件 |

## 文件地图

- `~/workspace/design-agent-skill/design-judgment/` — skill 本体（SKILL.md、scripts/、knowledge/、INSTALL.md、verification.md）
- `~/workspace/judgment-pipeline-proto/` — 最小闭环原型（只复用，不改）
- `~/workspace/research_notes/judgment-loop-evidence-20261104-0929/` — 调研证据（report.md）、实现指南（build-guide-source.md）、几步走计划（plan-steps-2026-11-06.md）
- 对外技术分析页（artifact）：设计判断沉淀回流链路（she-ji-pan-duan-chen-dian-hui-liu-lian-lu），黑底白字、单绿强调色、正式书面语
- 本文件：`~/workspace/design-agent-skill/project.md`（总纲，任何 agent 接手先读这份）

## 接手先读（任何 agent）

1. 先读这份 project.md，再读 plan-steps-2026-11-06.md。
2. 动手前先看 verification.md，知道哪些已经跑通过，别重复验证。
3. 原型 judgment-pipeline-proto/ 只复用、不改。
4. 改完要真跑一遍，把命令和结果写进 verification.md；失败如实写，别报假通过。
5. 用户侧只做一次安装操作；文档简体中文、少用技术词。

## 待确认（等用户）

- kbase MCP 工具清单、认证、单条大小、云端 agent 跑在哪。
- 真实设计规范 + 业务知识库文件（发过来就替换 knowledge/）。
- 在真 Qoder 里装 skill（用户自己电脑上动手）。
