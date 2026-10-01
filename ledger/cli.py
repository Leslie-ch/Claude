"""命令行入口：python -m ledger <命令> ..."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from .core import Expense, Ledger

DEFAULT_PATH = Path(os.environ.get("LEDGER_FILE", "~/.ledger.json")).expanduser()


def bar(value: float, maximum: float, width: int = 20) -> str:
    """用字符画一个简单的横向条形图。"""
    filled = round(width * value / maximum) if maximum else 0
    return "█" * filled + "·" * (width - filled)


def cmd_add(ledger: Ledger, args: argparse.Namespace) -> None:
    kwargs = {"amount": args.amount, "category": args.category, "note": args.note}
    if args.date:
        kwargs["day"] = args.date
    ledger.add(Expense(**kwargs))
    print(f"✅ 已记录：{args.category} ¥{args.amount:.2f}")


def cmd_list(ledger: Ledger, args: argparse.Namespace) -> None:
    items = ledger.filter(category=args.category, month=args.month)
    if not items:
        print("（没有记录）")
        return
    for e in sorted(items, key=lambda e: e.day):
        print(f"{e.day}  {e.category:<6} ¥{e.amount:>9.2f}  {e.note}")
    print(f"共 {len(items)} 笔，合计 ¥{sum(e.amount for e in items):.2f}")


def cmd_summary(ledger: Ledger, args: argparse.Namespace) -> None:
    totals = ledger.summary(month=args.month)
    if not totals:
        print("（没有记录）")
        return
    top = max(totals.values())
    for cat, amount in totals.items():
        print(f"{cat:<6} {bar(amount, top)} ¥{amount:.2f}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ledger", description="命令行记账本")
    parser.add_argument("--file", type=Path, default=DEFAULT_PATH, help="账本文件路径")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="记一笔")
    p_add.add_argument("amount", type=float)
    p_add.add_argument("category")
    p_add.add_argument("note", nargs="?", default="")
    p_add.add_argument("--date", help="日期 YYYY-MM-DD，默认今天")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="列出记录")
    p_list.add_argument("--category")
    p_list.add_argument("--month", help="YYYY-MM")
    p_list.set_defaults(func=cmd_list)

    p_sum = sub.add_parser("summary", help="分类统计")
    p_sum.add_argument("--month", help="YYYY-MM")
    p_sum.set_defaults(func=cmd_summary)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        args.func(Ledger(args.file), args)
    except ValueError as exc:
        print(f"❌ {exc}")
        return 1
    return 0
