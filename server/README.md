# server/：本地接收端 + 管理员看板

这里是最小闭环原型的代码：本地跑一个接收接口，收上传的记录、存库、给管理员看分组。云端正式方案用阿里内部知识库 kbase 的 MCP 服务（见 project.md 目标 3），这里只是本地 stand-in，验证回路用。

## 文件

- `receiver.py` — 接收接口：验身份 → 验格式 → 存。JSON 进数据库，快照文件进目录。
- `admin.py` — 管理员看板：按改动 + 接受/打回分组计数，导出 tuning.jsonl（偏好样本，供以后微调）。
- `db.py` / `recorder.py` / `sanitizer.py` / `uploader.py` — 存储、记录、脱敏、上传的共用逻辑（skill/scripts/ 里是同一份的自包含复制）。
- `demo.py` — 一键演示：记 3 轮 → 上传 → 接收 → 看板。

## 跑起来

```bash
cd server
RECEIVER_TOKEN=test-token-123 RECEIVER_DB=server.db RECEIVER_SNAP=server_snapshots python3 receiver.py
```

跑在 127.0.0.1:8765，只接受 POST /v1/records，须带 `Authorization: Bearer <token>`。

上传端（skill/scripts/upload.py）默认就指这个地址，token 默认 `demo-token-123`，可用环境变量 `JUDGMENT_ENDPOINT` / `JUDGMENT_TOKEN` 改。

## 注意

- 跑起来产生的 `server.db`、`server_snapshots/`、`tuning.jsonl` 是本地测试数据，不进仓库（见根目录 .gitignore）。
- 正式上云后这里不再用，改调 kbase MCP。
