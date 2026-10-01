"""记账本的核心逻辑：数据模型与 JSON 持久化。"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path


@dataclass
class Expense:
    amount: float
    category: str
    note: str = ""
    day: str = field(default_factory=lambda: date.today().isoformat())

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValueError("金额必须大于 0")
        self.category = self.category.strip() or "其他"


class Ledger:
    """一个基于 JSON 文件的简单账本。"""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.expenses: list[Expense] = []
        if self.path.exists():
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self.expenses = [Expense(**item) for item in raw]

    def add(self, expense: Expense) -> None:
        self.expenses.append(expense)
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(e) for e in self.expenses]
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def filter(self, category: str | None = None, month: str | None = None) -> list[Expense]:
        """按分类和/或月份（YYYY-MM）筛选。"""
        return [
            e
            for e in self.expenses
            if (category is None or e.category == category)
            and (month is None or e.day.startswith(month))
        ]

    def summary(self, month: str | None = None) -> dict[str, float]:
        """各分类合计，按金额从高到低排序。"""
        totals: dict[str, float] = defaultdict(float)
        for e in self.filter(month=month):
            totals[e.category] += e.amount
        return dict(sorted(totals.items(), key=lambda kv: kv[1], reverse=True))
