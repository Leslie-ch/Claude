# ledger — 命令行记账本

一个零依赖的小型 Python 记账工具（标准库：dataclasses / argparse / json / pathlib）。

```bash
python -m ledger add 35 餐饮 牛肉面            # 记一笔（默认今天）
python -m ledger add 128 交通 高铁 --date 2026-09-28
python -m ledger list --month 2026-10          # 列出，可按 --category / --month 筛选
python -m ledger summary                       # 分类合计 + 字符条形图
```

数据默认存到 `~/.ledger.json`，可用 `--file` 或环境变量 `LEDGER_FILE` 指定。

运行测试：`pip install pytest && python -m pytest`
