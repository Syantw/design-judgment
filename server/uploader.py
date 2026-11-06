"""上传器：扫上传队列，HTTPS POST 发到云端接收接口；成功标记已上传，失败指数退避重试。"""
import sqlite3, json, urllib.request, datetime

def flush(db_path, endpoint, token, batch=20):
    now = datetime.datetime.now().isoformat(timespec="seconds")
    c = sqlite3.connect(db_path)
    c.row_factory = sqlite3.Row
    rows = c.execute(
        """SELECT q.record_id, q.attempts, r.* FROM upload_queue q
           JOIN records r ON r.id = q.record_id
           WHERE r.uploaded = 0 AND (q.next_retry IS NULL OR q.next_retry <= ?)
           ORDER BY q.record_id LIMIT ?""", (now, batch)).fetchall()
    sent, failed = 0, 0
    for row in rows:
        payload = {k: row[k] for k in (
            "user_id", "session_id", "round_no", "user_text",
            "diff", "result", "created_at", "plugin_version")}
        try:
            with open(row["demo_snapshot_path"], encoding="utf-8") as f:
                payload["demo_snapshot_html"] = f.read()
        except OSError:
            payload["demo_snapshot_html"] = ""
        req = urllib.request.Request(
            endpoint, data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {token}"},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                ok = (resp.status == 200)
        except Exception:
            ok = False
        if ok:
            c.execute("UPDATE records SET uploaded=1 WHERE id=?", (row["record_id"],))
            c.execute("DELETE FROM upload_queue WHERE record_id=?", (row["record_id"],))
            sent += 1
        else:
            att = row["attempts"] + 1
            wait = min(2 ** att, 300)
            nxt = (datetime.datetime.now()
                   + datetime.timedelta(seconds=wait)).isoformat(timespec="seconds")
            c.execute("UPDATE upload_queue SET attempts=?, next_retry=? WHERE record_id=?",
                      (att, nxt, row["record_id"]))
            failed += 1
    c.commit()
    c.close()
    return sent, failed
