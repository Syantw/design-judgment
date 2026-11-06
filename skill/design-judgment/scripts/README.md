# scripts/ 里有什么

这个文件夹里的东西都是纯 Python 标准库，不用另外装东西。agent 按 SKILL.md 说的调下面两个命令就行，其余文件是被它们调用的。

## 直接调的两个入口

| 文件 | 干什么 | 什么时候调 |
|---|---|---|
| `record.py` | 记一轮：用户原话 + 这一轮的 demo + 改了什么 + 接受/打回，写进本地账本 | 每轮对话结束调一次 |
| `upload.py` | 把攒着的记录传到云端接收接口 | 会话结束调一次 |

用法：

```bash
python3 record.py --session-id s_001 --round 1 --user-text "按钮改成蓝色" \
  --demo-snapshot demo.html --diff "主按钮：灰色->品牌主色" --result accepted

python3 upload.py
```

`--demo-snapshot` 可以是 demo 文件的路径（读文件），也可以直接是一段 HTML。
`--result` 只能填 `accepted`（接受）或 `rejected`（打回）。

## 被调用的四个文件

| 文件 | 干什么 |
|---|---|
| `db.py` | 本地账本（SQLite）：records 存记录，upload_queue 存待上传的队列 |
| `recorder.py` | 写记录：先脱敏再存，demo 快照存成文件，记录进上传队列 |
| `sanitizer.py` | 脱敏：敏感词名单 + 正则，命中替换成 `***`，在本地、发出之前做 |
| `uploader.py` | 上传：扫队列发给接收接口，成功标记已上传，失败等一会儿再试 |

## 数据存在哪

都在 skill 文件夹下的 `data/` 里：`client.db`（账本）、`snapshots/`（每轮 demo 快照）、`consent.json`（同意上传的开关，不存在就是没同意）。

## 上传开关

`upload.py` 默认不传。同意的办法（二选一）：环境变量 `JUDGMENT_UPLOAD=1`，或在 `data/consent.json` 里写 `{"upload_enabled": true}`。接收地址默认是本地测试地址，用 `--endpoint` / `--token` 改，或用环境变量 `JUDGMENT_ENDPOINT` / `JUDGMENT_TOKEN`。
