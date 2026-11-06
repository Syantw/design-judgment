"""命令行入口：把攒着的记录传到云端。会话结束调一次。

默认不传：需要先同意。同意的办法（二选一）：
  1. 环境变量 JUDGMENT_UPLOAD=1
  2. 在 skill 文件夹的 data/consent.json 里写 {"upload_enabled": true}

接收地址默认是本地测试地址，可用 --endpoint / --token 改，
或用环境变量 JUDGMENT_ENDPOINT / JUDGMENT_TOKEN。
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from db import init
from uploader import flush

DATA_DIR = os.path.join(SKILL_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "client.db")

DEFAULT_ENDPOINT = "http://127.0.0.1:8765/v1/records"
DEFAULT_TOKEN = "demo-token-123"

def consent_given():
    if os.environ.get("JUDGMENT_UPLOAD") == "1":
        return True
    consent_file = os.path.join(DATA_DIR, "consent.json")
    try:
        with open(consent_file, encoding="utf-8") as f:
            return bool(json.load(f).get("upload_enabled"))
    except (OSError, ValueError):
        return False

def main():
    ap = argparse.ArgumentParser(description="上传已记录的设计判断")
    ap.add_argument("--endpoint", default=os.environ.get("JUDGMENT_ENDPOINT", DEFAULT_ENDPOINT))
    ap.add_argument("--token", default=os.environ.get("JUDGMENT_TOKEN", DEFAULT_TOKEN))
    args = ap.parse_args()

    if not consent_given():
        print("未同意上传，不传。同意办法：JUDGMENT_UPLOAD=1，或在 data/consent.json 写 {\"upload_enabled\": true}。")
        return
    init(DB_PATH)
    sent, failed = flush(DB_PATH, args.endpoint, args.token)
    print(f"上传：成功 {sent} 条，失败 {failed} 条")

if __name__ == "__main__":
    main()
