# -*- coding: utf-8 -*-
"""情绪标签解析的隔离自测：绕开包导入，只取出模块里的纯函数与常量。"""
import ast

src = open("main.py", encoding="utf-8").read()
parts = []
for node in ast.parse(src).body:
    if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", None) == "EMOTION_TAGS":
        parts.append(ast.get_source_segment(src, node))
    if isinstance(node, ast.FunctionDef) and node.name == "parse_emotion":
        parts.append(ast.get_source_segment(src, node))

ns = {}
exec("import re\n" + "\n".join(parts), ns)
parse_emotion = ns["parse_emotion"]

cases = [
    # 单标签兜底（老的整句写法）
    ("场景=日常闲聊；调门=松弛；情绪=happy", [("", "(happy)")]),
    ("场景=x；情绪=WHISPER", [("", "(whisper)")]),
    ("场景=x；情绪=", []),
    ("场景=x；情绪=unknown", []),
    ("场景=x；情绪：sad", []),
    ("场景=x", []),
    ("场景=x；情绪 = Excited", [("", "(excited)")]),
    # 逐小句：情绪变化的行才写
    (
        "场景=玩笑；调门=松\n"
        "句=哼，又来这套|情绪=angry\n"
        "句=不过也行吧|情绪=happy\n"
        "句=随你|情绪=happy",
        [("哼，又来这套", "(angry)"), ("不过也行吧", "(happy)"), ("随你", "(happy)")],
    ),
    # 半角竖线、非法标签丢弃、中文等号
    (
        "场景=x\n句=前半|情绪=happy\n句=后半|情绪=zzz",
        [("前半", "(happy)")],
    ),
    # 整段没有 句= 行 → 退回整句
    ("场景=x\n句烂掉了\n情绪=sad", [("", "(sad)")]),
]

ok = True
for raw, want in cases:
    got = parse_emotion(raw)
    if got != want:
        ok = False
    print("OK " if got == want else "FAIL", repr(raw), "->", got, "want", want)

if not ok:
    raise SystemExit("HAS FAILURE")
print("ALL PASS")
