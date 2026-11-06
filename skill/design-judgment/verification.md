# 验证记录（2026-11-06，本地跑通）

下面每一步都是真实跑过的命令和结果，不是推测。

## 1. 安装到测试位置

模拟用户安装：把 skill 文件夹复制到测试用的 skills 目录（对应 Qoder 的 `~/.qoder/skills/`）。

```bash
cp -r ~/workspace/design-agent-skill/design-judgment /tmp/skill-test/.qoder/skills/design-judgment
```

结果：复制成功，SKILL.md、scripts/、knowledge/、INSTALL.md 都在。

## 2. 启动本地接收端

用原型的 receiver.py（没改原型文件），接收地址指向测试库：

```bash
cd ~/workspace/judgment-pipeline-proto
RECEIVER_TOKEN=test-token-123 RECEIVER_DB=/tmp/skill-test/server.db \
  RECEIVER_SNAP=/tmp/skill-test/server_snapshots python3 receiver.py
```

结果：服务在 127.0.0.1:8765 跑起来（GET 探针返回 501，说明服务在，只是不接受 GET）。

## 3. 模拟三轮

先读了 knowledge/spec.yaml 和 knowledge/knowledge.md（就是 agent 每轮生成前要读的两个文件），然后记了三轮：

```bash
SK=/tmp/skill-test/.qoder/skills/design-judgment
# 第 1 轮：demo 用文件路径，接受
python3 $SK/scripts/record.py --session-id s_test_001 --round 1 \
  --user-text "主按钮改成蓝色" --demo-snapshot /tmp/skill-test/demos/r1.html \
  --diff "主按钮：灰色->品牌主色" --result accepted
# 第 2 轮：demo 直接传 HTML，原话里带敏感词，打回
python3 $SK/scripts/record.py --session-id s_test_001 --round 2 \
  --user-text "把主按钮改成描边样式，顺便联系XX银行确认一下" \
  --demo-snapshot "<div>…订单详情…</div>" \
  --diff "主按钮：实底->描边" --result rejected
# 第 3 轮：接受
python3 $SK/scripts/record.py --session-id s_test_001 --round 3 \
  --user-text "描边可以，但线再细一点" \
  --demo-snapshot "<div>…订单详情…</div>" \
  --diff "主按钮描边：粗->细" --result accepted
```

结果：

```
已记录：第 1 轮，id=1（accepted）
已记录：第 2 轮，id=2（rejected）
已记录：第 3 轮，id=3（accepted）
```

本地账本查到 3 条记录，上传队列 3 条，`data/snapshots/` 里 3 个快照文件。

脱敏生效：第 2 轮原话存进本地时已经是「把主按钮改成描边样式，顺便联系***确认一下」——「XX银行」被换成了 ***。

## 4. 没同意时上传（应拒绝）

```bash
python3 $SK/scripts/upload.py
```

结果：

```
未同意上传，不传。同意办法：JUDGMENT_UPLOAD=1，或在 data/consent.json 写 {"upload_enabled": true}。
```

上传开关默认关，验证通过。

## 5. 同意后上传

```bash
JUDGMENT_UPLOAD=1 JUDGMENT_ENDPOINT=http://127.0.0.1:8765/v1/records \
  JUDGMENT_TOKEN=test-token-123 python3 $SK/scripts/upload.py
```

结果：`上传：成功 3 条，失败 0 条`。本地记录全部标记已上传，队列清空（0 条）。

云端库（server.db）收到 3 条：第 2 轮原话仍是脱敏后的版本，快照文件 1.html / 2.html / 3.html 都在，内容完整。

## 6. 管理员看板

```bash
cd /tmp/skill-test
python3 -c "import sys; sys.path.insert(0, '/home/hatch/workspace/judgment-pipeline-proto')
from admin import report; report('/tmp/skill-test/server.db')"
```

结果：

```
候选规则（按出现次数）：
  主按钮描边：粗->细 | accepted | 1次
  主按钮：实底->描边 | rejected | 1次
  主按钮：灰色->品牌主色 | accepted | 1次
共收到 3 条记录
已导出 tuning.jsonl（偏好样本，供以后微调）
```

tuning.jsonl 有 3 行，每行是 {prompt, change, label}。

## 结论

- 读规范 → 生成 → 每轮记一条 → 同意后上传 → 云端接收 → 看板分组，全通。
- 脱敏在本地、发出之前做，云端看到的是脱敏后的版本。
- 没发现失败项。接收端验证后已停掉。

## 还没做的事

- 没在真正的 Qoder 里装过（只在测试目录模拟了复制安装），`/design-judgment` 触发还没真机验证。
- 接收端还是本地测试地址，没上云；token 还是测试用的 `test-token-123` / `demo-token-123`。
- 知识库还是示例内容（示例品牌规范 + 三条业务规则），没换成真实的设计规范和业务知识库。
- 没测断网重传（uploader 的重试逻辑是直接从原型复用的，原型里跑通过，这里没单独再测）。→ 2026-11-06 已补测，见第 7 节。

## 7. 断网重传（2026-11-06 补测）

在 skill 的副本（/tmp/skill-retry-test/design-judgment）上跑，不动 skill 本体：

```bash
# 记一轮
python3 $SK/scripts/record.py --session-id s_retry_001 --round 1 \
  --user-text "重试测试：按钮改大" --demo-snapshot "<div>demo</div>" \
  --diff "按钮：小->大" --result accepted
# 接收端没起时上传
JUDGMENT_UPLOAD=1 JUDGMENT_ENDPOINT=http://127.0.0.1:8765/v1/records \
  JUDGMENT_TOKEN=test-token-123 python3 $SK/scripts/upload.py
```

结果：`上传：成功 0 条，失败 1 条`，队列里还剩 1 条，attempts=1（失败留队列，指数退避）。

```bash
# 起接收端，再传一次
JUDGMENT_UPLOAD=1 JUDGMENT_ENDPOINT=http://127.0.0.1:8765/v1/records \
  JUDGMENT_TOKEN=test-token-123 python3 $SK/scripts/upload.py
```

结果：`上传：成功 1 条，失败 0 条`，队列清空（0 条），本地记录标记已上传，server.db 收到 1 条，原话一致。

结论：断网重传跑通。接收端验证后已停掉。
