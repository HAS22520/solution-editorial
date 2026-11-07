#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""三段代码等价性验证：抽取题解里的 C++/C/Python，编译、同输入运行、逐字节比对输出。

用法：
  python verify_triple.py 题解.md --input in.txt
  python verify_triple.py 题解.md --input in.txt --expect out.txt
  python verify_triple.py 题解.md --input in.txt --keep     # 保留临时目录便于调试

退出码：0 全部一致；1 编译失败/运行失败/输出不一致；2 参数或抽块失败。
缺少某语言的编译器时降级为警告，不算失败。
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LANG_ORDER = ["cpp", "c", "python"]
LANG_ALIAS = {
    "cpp": "cpp", "c++": "cpp", "cxx": "cpp", "cc": "cpp",
    "c": "c",
    "py": "python", "python": "python", "python3": "python",
}
FILENAME = {"cpp": "main.cpp", "c": "main.c", "python": "main.py"}


def normalize(lang):
    return LANG_ALIAS.get(lang.strip().lower(), lang.strip().lower())


def extract_blocks(text):
    """返回 {语言: 代码}，只保留本技能关心的三种。"""
    blocks = {}
    for m in re.finditer(r"```([\w+]*)[ \t]*\n(.*?)```", text, re.S):
        lang = normalize(m.group(1))
        if lang in LANG_ORDER and lang not in blocks:
            blocks[lang] = m.group(2)
    return blocks


def which(names):
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    return None


def run(cmd, cwd, stdin_bytes):
    return subprocess.run(cmd, cwd=cwd, input=stdin_bytes,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main():
    ap = argparse.ArgumentParser(description="验证题解三段代码等价")
    ap.add_argument("path", help="题解 markdown")
    ap.add_argument("--input", required=True, help="测试输入文件")
    ap.add_argument("--expect", help="期望输出文件（可选）")
    ap.add_argument("--keep", action="store_true", help="保留临时目录")
    ap.add_argument("--timeout", type=int, default=30, help="单次运行超时秒数，默认 30")
    args = ap.parse_args()

    md = Path(args.path)
    if not md.is_file():
        print(f"✗ 读不到题解：{md}")
        return 2
    inp = Path(args.input)
    if not inp.is_file():
        print(f"✗ 读不到输入：{inp}")
        return 2

    blocks = extract_blocks(md.read_text(encoding="utf-8-sig", errors="replace"))
    missing = [l for l in LANG_ORDER if l not in blocks]
    if missing:
        print(f"✗ 题解缺少代码块：{', '.join(missing)}")
        return 2

    stdin_bytes = inp.read_bytes()
    expect = Path(args.expect).read_bytes() if args.expect else None
    tmp = Path(tempfile.mkdtemp(prefix="editorial-verify-"))
    results, failures = {}, []

    try:
        for lang in LANG_ORDER:
            src = tmp / FILENAME[lang]
            src.write_text(blocks[lang], encoding="utf-8", newline="\n")

            if lang == "cpp":
                cxx = which(["g++", "clang++"])
                if not cxx:
                    print(f"! 跳过 cpp：找不到 g++/clang++")
                    continue
                exe = tmp / "a_cpp.exe"
                build = run([cxx, "-std=c++11", "-O2", "-pipe", str(src), "-o", str(exe)], tmp, b"")
                exec_cmd = [str(exe)]

            elif lang == "c":
                cc = which(["gcc", "clang"])
                if not cc:
                    print(f"! 跳过 c：找不到 gcc/clang")
                    continue
                exe = tmp / "a_c.exe"
                build = run([cc, "-std=c11", "-O2", "-pipe", str(src), "-o", str(exe)], tmp, b"")
                exec_cmd = [str(exe)]

            else:
                py = which(["python", "python3"])
                if not py:
                    print("! 跳过 python：找不到解释器")
                    continue
                build = None
                exec_cmd = [py, str(src)]

            if build is not None and build.returncode != 0:
                msg = build.stderr.decode("utf-8", "replace").strip()
                print(f"✗ {lang} 编译失败：\n{msg[:1200]}")
                failures.append(f"{lang} 编译失败")
                continue

            proc = run(exec_cmd, tmp, stdin_bytes)
            if proc.returncode != 0:
                msg = proc.stderr.decode("utf-8", "replace").strip()
                print(f"✗ {lang} 运行失败（exit {proc.returncode}）：{msg[:600]}")
                failures.append(f"{lang} 运行失败")
                continue
            results[lang] = proc.stdout

        if len(results) < 2:
            print("✗ 可用于比对的实现少于两份")
            return 1

        base_lang = LANG_ORDER[0] if LANG_ORDER[0] in results else list(results)[0]
        base = results[base_lang]
        for lang, out in results.items():
            if out == base:
                print(f"✓ {lang:<7} 与 {base_lang} 输出一致（{len(out)} 字节）")
            else:
                print(f"✗ {lang:<7} 输出不一致")
                print(f"    {base_lang}: {base[:200]!r}")
                print(f"    {lang}: {out[:200]!r}")
                failures.append(f"{lang} 输出不一致")

        if expect is not None:
            if base.strip() == expect.strip():
                print("✓ 与期望输出一致")
            else:
                print("✗ 与期望输出不一致")
                print(f"    期望: {expect[:200]!r}")
                print(f"    实际: {base[:200]!r}")
                failures.append("与期望输出不一致")

        if failures:
            print(f"\n—— 失败 {len(failures)} 项：{'; '.join(failures)}")
            return 1
        print("\n—— 三段代码等价性验证通过")
        return 0
    finally:
        if args.keep:
            print(f"临时目录保留：{tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
