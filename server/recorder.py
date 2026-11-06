"""记录器：每轮对话结束调用一次，把四样东西写进本地账本并加入上传队列。"""
import sqlite3, os, datetime
from sanitizer import sanitize

def log_round(db_path, snap_dir, user_id, session_id, round_no,
              user_text, demo_html, diff, result, plugin_version="0.1.0"):
    os.makedirs(snap_dir, exist_ok=True)
    clean = sanitize(user_text)  # 先脱敏再存
    snap_path = os.path.join(snap_dir, f"{session_id}_r{round_no}.html")
    with open(snap_path, "w", encoding="utf-8") as f:
        f.write(demo_html)
    now = datetime.datetime.now().isoformat(timespec="seconds")
    c = sqlite3.connect(db_path)
    cur = c.cursor()
    cur.execute(
        "INSERT INTO records(user_id,session_id,round_no,user_text,demo_snapshot_path,"
        "diff,result,created_at,plugin_version) VALUES(?,?,?,?,?,?,?,?,?)",
        (user_id, session_id, round_no, clean, snap_path, diff, result, now, plugin_version))
    rid = cur.lastrowid
    cur.execute("INSERT OR IGNORE INTO upload_queue(record_id) VALUES(?)", (rid,))
    c.commit()
    c.close()
    return rid
