"""云端接收接口：验身份 -> 验格式 -> 存。JSON 进数据库，快照文件进对象存储（原型里存本地目录）。"""
import json, os, sqlite3, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN = os.environ.get("RECEIVER_TOKEN", "demo-token-123")
DB = os.environ.get("RECEIVER_DB", "server.db")
SNAP = os.environ.get("RECEIVER_SNAP", "server_snapshots")

SCHEMA = """CREATE TABLE IF NOT EXISTS records(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 user_id TEXT, session_id TEXT, round_no INTEGER,
 user_text TEXT, diff TEXT, result TEXT,
 created_at TEXT, plugin_version TEXT,
 snapshot_file TEXT, received_at TEXT);"""

def init():
    os.makedirs(SNAP, exist_ok=True)
    c = sqlite3.connect(DB)
    c.executescript(SCHEMA)
    c.commit()
    c.close()

class H(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/v1/records":
            return self._send(404, {"ok": False})
        if self.headers.get("Authorization") != f"Bearer {TOKEN}":
            return self._send(401, {"ok": False, "error": "bad token"})
        try:
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        except Exception:
            return self._send(400, {"ok": False, "error": "bad json"})
        need = ["user_id", "session_id", "round_no", "user_text", "diff", "result"]
        if any(k not in data for k in need):
            return self._send(400, {"ok": False, "error": "missing fields"})
        c = sqlite3.connect(DB)
        cur = c.cursor()
        cur.execute(
            "INSERT INTO records(user_id,session_id,round_no,user_text,diff,result,"
            "created_at,plugin_version,received_at) VALUES(?,?,?,?,?,?,?,?,?)",
            (data["user_id"], data["session_id"], data["round_no"], data["user_text"],
             data["diff"], data["result"], data.get("created_at"),
             data.get("plugin_version"),
             datetime.datetime.now().isoformat(timespec="seconds")))
        rid = cur.lastrowid
        snap_file = os.path.join(SNAP, f"{rid}.html")
        with open(snap_file, "w", encoding="utf-8") as f:
            f.write(data.get("demo_snapshot_html", ""))
        cur.execute("UPDATE records SET snapshot_file=? WHERE id=?", (snap_file, rid))
        c.commit()
        c.close()
        self._send(200, {"ok": True, "id": rid})

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    init()
    HTTPServer(("127.0.0.1", 8765), H).serve_forever()
