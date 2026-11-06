"""脱敏：在本地、发出之前做。敏感词名单 + 正则，命中替换成 ***。"""
import re

# 示例名单：实际随插件下发，管理员可在云端更新
KEYWORDS = ["XX银行", "某某公司"]
PATTERNS = [re.compile(r"1[3-9]\d{9}"), re.compile(r"[\w.]+@[\w.]+")]

def sanitize(text):
    for kw in KEYWORDS:
        text = text.replace(kw, "***")
    for p in PATTERNS:
        text = p.sub("***", text)
    return text
