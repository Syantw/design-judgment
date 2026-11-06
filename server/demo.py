"""端到端演示：记 3 轮 -> 上传 -> 云端接收 -> 管理员看板。"""
import os, subprocess, sys, time, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
for p in ["client.db", "server.db", "tuning.jsonl"]:
    fp = os.path.join(ROOT, p)
    if os.path.exists(fp):
        os.remove(fp)
for d in ["snapshots", "server_snapshots"]:
    dp = os.path.join(ROOT, d)
    if os.path.isdir(dp):
        shutil.rmtree(dp)

sys.path.insert(0, ROOT)
from db import init
init(os.path.join(ROOT, "client.db"))

env = dict(os.environ, RECEIVER_TOKEN="demo-token-123",
           RECEIVER_DB=os.path.join(ROOT, "server.db"),
           RECEIVER_SNAP=os.path.join(ROOT, "server_snapshots"))
srv = subprocess.Popen([sys.executable, os.path.join(ROOT, "receiver.py")],
                       env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
try:
    from recorder import log_round
    from uploader import flush
    C = os.path.join(ROOT, "client.db")
    S = os.path.join(ROOT, "snapshots")
    r1 = log_round(C, S, "u_001", "s_001", 1, "按钮改成蓝色",
                   "<button style='color:blue'>确定</button>",
                   "button: gray->blue", "accepted")
    print(f"第1轮已记录 id={r1}（接受）")
    r2 = log_round(C, S, "u_001", "s_001", 2, "把主按钮改成描边样式，联系XX银行",
                   "<button style='outline'>确定</button>",
                   "button: solid->outline", "rejected")
    print(f"第2轮已记录 id={r2}（打回；'XX银行'会被脱敏）")
    r3 = log_round(C, S, "u_001", "s_001", 3, "描边可以，但线再细一点",
                   "<button style='outline thin'>确定</button>",
                   "button: outline thick->thin", "accepted")
    print(f"第3轮已记录 id={r3}（接受）")
    sent, failed = flush(C, "http://127.0.0.1:8765/v1/records", "demo-token-123")
    print(f"上传：成功 {sent} 条，失败 {failed} 条")
    print("--- 管理员看板 ---")
    from admin import report
    report(os.path.join(ROOT, "server.db"))
    # 看一眼云端库里第2轮的原话，确认脱敏生效
    import sqlite3
    c = sqlite3.connect(os.path.join(ROOT, "server.db"))
    txt = c.execute("SELECT user_text FROM records WHERE round_no=2").fetchone()[0]
    c.close()
    print(f"云端第2轮原话（脱敏后）：{txt}")
finally:
    srv.terminate()
