"""本地账本：SQLite，两张表（records 存记录，upload_queue 存待上传队列）。"""
import sqlite3, os

SCHEMA = """
CREATE TABLE IF NOT EXISTS records(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 user_id TEXT, session_id TEXT, round_no INTEGER,
 user_text TEXT, demo_snapshot_path TEXT, diff TEXT, result TEXT,
 created_at TEXT, plugin_version TEXT, uploaded INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS upload_queue(
 record_id INTEGER PRIMARY KEY, attempts INTEGER DEFAULT 0, next_retry TEXT);
"""

def init(path):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    c = sqlite3.connect(path)
    c.executescript(SCHEMA)
    c.commit()
    c.close()
