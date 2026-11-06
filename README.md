# 设计判断沉淀回流

做一个能给别人用的系统：别人的 agent 挂上我们的 skill，就能查设计规范和业务知识库、生成界面 demo；每轮的产物、用户原话、自评好坏自动记下来传回云端；云端整理后把提炼出的规则写回知识库，下次所有人挂上就拿到新的。

总纲和进度见 [project.md](project.md)，里面有目标、子目标 check 表和待确认事项。

## 目录

- `skill/design-judgment/` — skill 本体。SKILL.md、记录/上传脚本、示例设计规范与业务知识库、安装说明、验证记录。
- `server/` — 本地接收端 + 管理员看板（最小闭环原型）。云端正式方案用阿里内部知识库 kbase 的 MCP 服务，这里是本地 stand-in。
- `docs/` — 几步走计划、实现指南。
- `project.md` — 总纲。

## 快速开始

1. 装 skill：把 `skill/design-judgment/` 复制到 `~/.qoder/skills/`（Qoder）或 `~/.claude/skills/`（Claude Code），新开会话即生效。传到 GitHub 后也可以 `npx skills add https://github.com/Syantw/design-judgment --skill design-judgment -a qoder` 一条命令装。
2. 起本地接收端（验证用）：`cd server && RECEIVER_TOKEN=test-token-123 python3 receiver.py`，跑在 127.0.0.1:8765。
3. 在 Qoder 里让 agent 按规范生成一个 demo，每轮结束它会记一条，会话结束上传。
4. 看板：`python3 admin.py`（在 server/ 里跑，看原型说明）。

## 状态

- 第一步（本地 skill）已搭完，本地端到端跑通：3 轮记→脱敏→上传→接收→看板，断网重传也测过。
- 云端（kbase MCP + 云端 agent 整理）等 kbase 工具清单、认证、单条大小、云端 agent 跑在哪，确认后动第三步。
- 详细进度见 [project.md](project.md)。
