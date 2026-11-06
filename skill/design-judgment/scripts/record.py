"""命令行入口：记一轮。agent 每轮结束调一次。

用法：
  python3 record.py --session-id s_001 --round 1 \
    --user-text "按钮改成蓝色" \
    --demo-snapshot demo.html \
    --diff "主按钮：灰色->品牌主色" --result accepted

--demo-snapshot 可以是 demo 文件的路径（读文件），也可以直接是一段 HTML。
--user-id 不填默认为 local-user。
数据存在 skill 文件夹下的 data/ 里（client.db 和 snapshots/）。
"""
import argparse, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from db import init
from recorder import log_round

DATA_DIR = os.path.join(SKILL_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "client.db")
SNAP_DIR = os.path.join(DATA_DIR, "snapshots")

def main():
    ap = argparse.ArgumentParser(description="记一轮设计判断")
    ap.add_argument("--session-id", required=True)
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--user-text", required=True)
    ap.add_argument("--demo-snapshot", required=True)
    ap.add_argument("--diff", required=True)
    ap.add_argument("--result", required=True, choices=["accepted", "rejected"])
    ap.add_argument("--user-id", default="local-user")
    ap.add_argument("--version", default="0.1.0")
    args = ap.parse_args()

    demo_html = args.demo_snapshot
    if os.path.isfile(demo_html):
        with open(demo_html, encoding="utf-8") as f:
            demo_html = f.read()

    init(DB_PATH)
    rid = log_round(DB_PATH, SNAP_DIR, args.user_id, args.session_id,
                    args.round, args.user_text, demo_html, args.diff,
                    args.result, args.version)
    print(f"已记录：第 {args.round} 轮，id={rid}（{args.result}）")

if __name__ == "__main__":
    main()
