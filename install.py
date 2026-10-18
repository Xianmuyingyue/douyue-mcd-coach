#!/usr/bin/env python3
"""
douyue-mcd-coach · 安装脚本 (install.py)
----------------------------------------
把本 Skill 安装到目标平台的技能目录。

用法：
    python install.py --target workbuddy     # 安装到 ~/.workbuddy/skills/douyue-mcd-coach
    python install.py --target .              # 仅校验本目录结构（不复制）
    python install.py --help

仅依赖 Python 标准库。
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys

# 仓库内应包含的必备文件 / 目录
REQUIRED = [
    "README.md",
    "CONTEST_DECLARATION.md",
    "MCP_INTEGRATION.md",
    "mcp-config.example.json",
    "SKILL.md",
    "workbuddy.md",
    "references",
    "scripts",
    "docs",
]


def repo_root() -> str:
    """返回本脚本所在目录（即 Skill 根目录）。"""
    return os.path.dirname(os.path.abspath(__file__))


def check_structure(root: str) -> list[str]:
    """返回缺失的必备条目列表。"""
    missing = []
    for item in REQUIRED:
        if not os.path.exists(os.path.join(root, item)):
            missing.append(item)
    return missing


def target_dir(target: str) -> str:
    home = os.path.expanduser("~")
    if target == "workbuddy":
        return os.path.join(home, ".workbuddy", "skills", "douyue-mcd-coach")
    raise ValueError(f"未知 target：{target}（支持：workbuddy）")


def install(target: str) -> int:
    root = repo_root()
    missing = check_structure(root)
    if missing:
        print(f"❌ 缺少必备文件/目录：{', '.join(missing)}", file=sys.stderr)
        print("   请在本 Skill 根目录运行 install.py。", file=sys.stderr)
        return 1

    dst = target_dir(target)
    if os.path.exists(dst):
        backup = dst + ".bak"
        print(f"⚠️ 目标已存在，先备份到：{backup}")
        if os.path.exists(backup):
            shutil.rmtree(backup)
        shutil.move(dst, backup)

    shutil.copytree(root, dst)
    print(f"✅ 已安装到：{dst}")
    print("   在 WorkBuddy 左侧【专家·技能】中即可看到「窦月·麦门健康执行器」。")
    print("   记得在 MCP 配置里填入你的 MCD_MCP_TOKEN（见 mcp-config.example.json）。")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="安装 douyue-mcd-coach Skill")
    ap.add_argument("--target", default="workbuddy",
                    help="安装目标：workbuddy（默认）/ .（仅校验）")
    args = ap.parse_args()

    root = repo_root()
    missing = check_structure(root)
    if missing:
        print(f"⚠️ 结构校验：缺少 {', '.join(missing)}")
    else:
        print("✅ 结构校验通过：必备文件/目录齐全。")

    if args.target == ".":
        print("（仅校验模式，未复制文件。）")
        return 0 if not missing else 1

    return install(args.target)


if __name__ == "__main__":
    sys.exit(main())
