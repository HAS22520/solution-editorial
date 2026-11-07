#!/usr/bin/env python3
"""check_docx.py — 交付前检查一份题解 docx 是否达标

检查项：
  1. 公式是否残留 LaTeX 原文（\\text、\\begin、\\frac、\\ge ...）或裸露的 $...$
  2. 是否出现 <rootKey> 这类序列化垃圾（意味着 docx 与转换器用了不同构建）
  3. 是否有公式（m:oMath）——有 $ 公式的题解必须 > 0
  4. 是否漏出"零注释/无注释"这类自我标榜字样
  5. 可选：给了 --pdf 时检查页数与每页是否有文字

用法：
    python check_docx.py 题解手册.docx [--pdf 题解手册.pdf] [--min-math 6]

退出码：0 通过；1 有问题；2 无法读取文件
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

LATEX_RESIDUE = [
    (r"\\text\{", "`\\text{}` 未转换"),
    (r"\\begin\{", "`\\begin{}` 未转换（cases/matrix 环境需改写）"),
    (r"\\end\{", "`\\end{}` 未转换"),
    (r"\\frac", "`\\frac` 未转换"),
    (r"\\mathbf|\\mathrm|\\mathit", "字体命令未转换"),
    (r"\\left|\\right", "`\\left/\\right` 未转换"),
    (r"\\(ge|le|ll|gg|neq|approx|equiv)\b", "关系符 LaTeX 未转换"),
    (r"\\(implies|Rightarrow|leftarrow|rightarrow|to)\b", "箭头 LaTeX 未转换"),
    (r"\\cdot|\\times|\\div", "运算符 LaTeX 未转换"),
    (r"\\(sum|prod|min|max|log|sqrt)\b", "函数名 LaTeX 未转换"),
    (r"\\quad|\\hspace|\\;|\\,", "间距命令未转换（改用 `\\ \\ `）"),
    (r"\$\$?", "裸露的 $ / $$ 定界符"),
]

BOAST = ["零注释", "无注释", "零注释代码", "三段式规范"]

ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
math_ns = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"


def read_xml(docx: Path) -> str:
    with zipfile.ZipFile(docx) as z:
        return z.read("word/document.xml").decode("utf-8", errors="replace")


def text_of(xml: str) -> str:
    """取所有可见文字（w:t 与 m:t），用于查中文错字类问题。"""
    return "".join(re.findall(r"<[wm]:t[^>]*>(.*?)</[wm]:t>", xml, flags=re.S))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("--pdf", default=None)
    ap.add_argument("--min-math", type=int, default=0,
                    help="至少应有多少个公式（默认 0：不强制）")
    args = ap.parse_args()

    docx = Path(args.docx)
    if not docx.is_file():
        print(f"✗ 找不到 {docx}")
        return 2

    try:
        xml = read_xml(docx)
    except Exception as e:  # noqa: BLE001
        print(f"✗ 无法作为 docx 读取：{e}")
        return 2

    errors: list[str] = []
    warnings: list[str] = []

    # 1. LaTeX 残留
    for pattern, label in LATEX_RESIDUE:
        hits = re.findall(pattern, xml)
        if hits:
            errors.append(f"公式残留：{label}（{len(hits)} 处）")

    # 2. 序列化垃圾
    if "rootKey" in xml:
        errors.append("存在 <rootKey> 垃圾节点：docx 与 mathml-to-docx 用了不同构建")

    # 3. 公式数量
    n_math = len(re.findall(r"<m:oMath[ >]", xml))
    if args.min_math and n_math < args.min_math:
        errors.append(f"公式只有 {n_math} 个，少于要求的 {args.min_math} 个")

    # 4. 自我标榜字样
    visible = text_of(xml)
    for word in BOAST:
        if word in visible:
            errors.append(f"正文出现“{word}”字样（写作约束不该写进题解）")

    # 5. PDF（可选）
    pdf_info = None
    if args.pdf:
        pdf = Path(args.pdf)
        if not pdf.is_file():
            errors.append(f"找不到 pdf：{pdf}")
        else:
            try:
                import pymupdf  # type: ignore

                d = pymupdf.open(pdf)
                empty = [i + 1 for i, p in enumerate(d) if not p.get_text().strip()]
                pdf_info = (d.page_count, empty)
                if empty:
                    warnings.append(f"pdf 第 {empty} 页没有文字，确认是否整页是代码块")
            except ImportError:
                warnings.append("未安装 pymupdf，跳过 pdf 检查")

    # 报告
    print(f"文档：{docx}")
    print(f"公式：{n_math} 个（m:oMath）")
    print(f"可见文字：{len(visible)} 字")
    if pdf_info:
        print(f"PDF：{pdf_info[0]} 页")

    for e in errors:
        print(f"✗ {e}")
    for w in warnings:
        print(f"! {w}")

    if errors:
        print(f"\n结果：{len(errors)} 个错误，需修复")
        return 1

    print("\n结果：通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
