import pytest

from ledger import Expense, Ledger
from ledger.cli import main


@pytest.fixture
def ledger_file(tmp_path):
    return tmp_path / "ledger.json"


def test_rejects_non_positive_amount():
    with pytest.raises(ValueError):
        Expense(amount=0, category="餐饮")


def test_blank_category_becomes_other():
    assert Expense(amount=1, category="  ").category == "其他"


def test_persists_and_reloads(ledger_file):
    Ledger(ledger_file).add(Expense(12.5, "餐饮", "午饭", "2026-10-01"))
    reloaded = Ledger(ledger_file)
    assert reloaded.expenses == [Expense(12.5, "餐饮", "午饭", "2026-10-01")]


def test_filter_and_summary(ledger_file):
    ledger = Ledger(ledger_file)
    ledger.add(Expense(30, "餐饮", day="2026-09-30"))
    ledger.add(Expense(20, "餐饮", day="2026-10-01"))
    ledger.add(Expense(100, "交通", day="2026-10-02"))

    assert len(ledger.filter(month="2026-10")) == 2
    assert len(ledger.filter(category="餐饮")) == 2
    assert ledger.summary() == {"交通": 100, "餐饮": 50}
    assert list(ledger.summary(month="2026-10")) == ["交通", "餐饮"]


def test_cli_end_to_end(ledger_file, capsys):
    f = ["--file", str(ledger_file)]
    assert main([*f, "add", "25", "餐饮", "咖啡", "--date", "2026-10-01"]) == 0
    assert main([*f, "add", "-3", "餐饮"]) == 1
    assert main([*f, "summary"]) == 0
    out = capsys.readouterr().out
    assert "已记录" in out and "金额必须大于 0" in out and "¥25.00" in out
