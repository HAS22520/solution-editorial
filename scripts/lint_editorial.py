#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""题解格式检查器。

检查项：
  结构    必须有 `## 题意`、`## 思路`、`## 代码`，且顺序正确
  题意    长度有上限，且不含"题目描述/输入格式/样例"等转录词
  代码    三块顺序必须是 cpp → c → python，且都存在
  注释    三块代码内不得出现 // 、/* 、#
  思路    必须给出 O(...) 复杂度；建议包含正确性论证

用法：
  python lint_editorial.py 题解.md
  python lint_editorial.py 题解.md --strict     # 警告也算失败
  python lint_editorial.py 题解.md --max-intent 240

退出码：0 通过；1 有错误（或 --strict 下有警告）；2 文件读不到。
"""

import argparse
import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = ["题意", "思路", "代码"]
LANG_ORDER = ["cpp", "c", "python"]
LANG_ALIAS = {
    "cpp": "cpp", "c++": "cpp", "cxx": "cpp", "cc": "cpp",
    "c": "c",
    "py": "python", "python": "python", "python3": "python",
}
TRANSCRIBE_WORDS = ["题目描述", "输入格式", "输出格式", "样例输入", "样例输出", "示例", "数据范围"]
CORRECTNESS_WORDS = ["正确性", "为什么", "不变量", "归纳", "反证", "交换论证", "不会漏", "不会错", "等价"]
COMPLEXITY_RE = re.compile(r"O\s*\(\s*[^)]{1,30}\)")

RED, GREEN, YELLOW, DIM, RESET = "\033[31m", "\033[32m", "\033[33m", "\033[2m", "\033[0m"


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, line, msg):
        self.errors.append((line, msg))

    def warn(self, line, msg):
        self.warnings.append((line, msg))

    def render(self, path):
        for line, msg in self.errors:
            print(f"{RED}✗{RESET} {path}:{line}  {msg}")
        for line, msg in self.warnings:
            print(f"{YELLOW}!{RESET} {path}:{line}  {msg}")
        if not self.errors and not self.warnings:
            print(f"{GREEN}✓{RESET} {path}  格式检查全部通过")
            return
        print(f"{DIM}—— 错误 {len(self.errors)} 个，警告 {len(self.warnings)} 个{RESET}")


def scan(text):
    """把文档切成 section 列表和代码块列表，跳过代码块内部的伪标题。"""
    lines = text.splitlines()
    sections, blocks = [], []
    cur_section = {"name": None, "line": 0, "body": []}
    in_fence = False
    cur_block = None

    for no, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_fence:
                in_fence = True
                cur_block = {"lang": stripped[3:].strip(), "line": no, "body": []}
            else:
                in_fence = False
                cur_block["lang"] = normalize_lang(cur_block["lang"])
                blocks.append(cur_block)
                cur_block = None
            continue
        if in_fence:
            cur_block["body"].append(line)
            continue
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            sections.append(cur_section)
            cur_section = {"name": m.group(1).strip(), "line": no, "body": []}
            continue
        cur_section["body"].append(line)

    sections.append(cur_section)
    if in_fence:
        blocks.append(cur_block)
        blocks[-1]["unclosed"] = True
    return [s for s in sections if s["name"]], blocks


def normalize_lang(lang):
    return LANG_ALIAS.get(lang.strip().lower(), lang.strip().lower())


def section_text(section, blocks):
    """去掉代码块后的正文（section body 里可能夹着围栏）。"""
    kept, in_fence = [], False
    for line in section["body"]:
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            kept.append(line)
    return "\n".join(kept)


def check_sections(sections, report):
    names = [s["name"] for s in sections]
    missing = [w for w in REQUIRED_SECTIONS if w not in names]
    for want in missing:
        report.error(0, f"缺少小节 `## {want}`")
    order = [n for n in names if n in REQUIRED_SECTIONS]
    if order == sorted(order, key=REQUIRED_SECTIONS.index) and not missing:
        print(f"{GREEN}✓{RESET} 结构：{' → '.join(order)}")
    elif order and not missing:
        report.error(0, f"小节顺序错误：{' → '.join(order)}，应为 题意 → 思路 → 代码")


def check_intent(sections, blocks, report, max_intent):
    sec = next((s for s in sections if s["name"] == "题意"), None)
    if not sec:
        return
    body = section_text(sec, blocks)
    compact = re.sub(r"\s+", "", body)
    if not compact:
        report.error(sec["line"], "题意段为空")
        return
    if len(compact) > max_intent:
        report.error(sec["line"],
                     f"题意过长（{len(compact)} 字 > {max_intent}），只保留对象、约束、目标")
    for word in TRANSCRIBE_WORDS:
        if word in body:
            report.error(sec["line"], f"题意段出现转录词「{word}」，改为数学化概括")
    lines = [l for l in body.splitlines() if l.strip()]
    if len(lines) > 3:
        report.warn(sec["line"], f"题意写了 {len(lines)} 行，建议压到 3 行以内")


def check_idea(sections, blocks, report):
    sec = next((s for s in sections if s["name"] == "思路"), None)
    if not sec:
        return
    body = section_text(sec, blocks)
    if not COMPLEXITY_RE.search(body):
        report.error(sec["line"], "思路段没有 O(...) 形式的时间/空间复杂度")
    if not any(w in body for w in CORRECTNESS_WORDS):
        report.warn(sec["line"], "思路段缺少正确性论证（不变量/归纳/反证/交换论证）")
    if len(re.sub(r"\s+", "", body)) < 50:
        report.warn(sec["line"], "思路段过短，可能只给了结论没给理由")


def check_blocks(blocks, report):
    if not blocks:
        report.error(0, "没有任何代码块")
        return

    for b in blocks:
        if b.get("unclosed"):
            report.error(b["line"], "代码块没有闭合的 ```")
        if not any(l.strip() for l in b["body"]):
            report.error(b["line"], f"`{b['lang']}` 代码块为空")

    langs = [b["lang"] for b in blocks]
    if langs == LANG_ORDER:
        print(f"{GREEN}✓{RESET} 代码顺序：{' → '.join(langs)}")
    else:
        for want in LANG_ORDER:
            if want not in langs:
                report.error(0, f"缺少 `{want}` 代码块")
        unknown = [l for l in langs if l not in LANG_ORDER]
        if unknown:
            report.error(0, f"出现未知语言块：{', '.join(unknown)}")
        if all(w in langs for w in LANG_ORDER) and [l for l in langs if l in LANG_ORDER] != LANG_ORDER:
            report.error(0, f"代码块顺序为 {' → '.join(langs)}，必须为 cpp → c → python")

    for b in blocks:
        lang, line = b["lang"], b["line"]
        body_lines = b["body"]
        for offset, src in enumerate(body_lines, 1):
            hit = None
            if lang in ("cpp", "c"):
                if "//" in src or "/*" in src or "*/" in src:
                    hit = "// 或 /* */"
            elif lang == "python":
                if "#" in src and not src.lstrip().startswith("#!"):
                    hit = "#"
            if hit:
                report.error(line + offset, f"{lang} 代码里有注释（{hit}），本技能要求零注释：{src.strip()[:40]}")
        if len([l for l in body_lines if l.strip()]) < 5:
            report.warn(line, f"`{lang}` 代码块行数过少，确认是完整文件而不是片段")


def main():
    ap = argparse.ArgumentParser(description="题解格式检查器")
    ap.add_argument("path", help="题解 markdown 路径")
    ap.add_argument("--strict", action="store_true", help="把警告也当作失败")
    ap.add_argument("--max-intent", type=int, default=300, help="题意段最大字数（去空白），默认 300")
    args = ap.parse_args()

    p = Path(args.path)
    if not p.is_file():
        print(f"{RED}✗{RESET} 读不到文件：{p}")
        return 2
    text = p.read_text(encoding="utf-8-sig", errors="replace")

    report = Report()
    sections, blocks = scan(text)
    check_sections(sections, report)
    check_intent(sections, blocks, report, args.max_intent)
    check_idea(sections, blocks, report)
    check_blocks(blocks, report)

    if not re.search(r"^#\s+\S", text, re.M):
        report.warn(1, "缺少一级标题 `# 题目名`")

    report.render(p)

    if report.errors or (args.strict and report.warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
