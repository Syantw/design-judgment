"""管理员看板（最小版）：按"改了什么"分组计数 -> 候选规则；导出偏好样本供以后微调。"""
import sqlite3, json

def report(db_path="server.db"):
    c = sqlite3.connect(db_path)
    c.row_factory = sqlite3.Row
    rows = c.execute(
        "SELECT diff, result, COUNT(*) n FROM records "
        "GROUP BY diff, result ORDER BY n DESC").fetchall()
    print("候选规则（按出现次数）：")
    for r in rows:
        print(f"  {r['diff']} | {r['result']} | {r['n']}次")
    total = c.execute("SELECT COUNT(*) n FROM records").fetchone()["n"]
    print(f"共收到 {total} 条记录")
    recs = c.execute("SELECT user_text, diff, result FROM records").fetchall()
    with open("tuning.jsonl", "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps({"prompt": r["user_text"], "change": r["diff"],
                                "label": r["result"]}, ensure_ascii=False) + "\n")
    print("已导出 tuning.jsonl（偏好样本，供以后微调）")
    c.close()

if __name__ == "__main__":
    report()
