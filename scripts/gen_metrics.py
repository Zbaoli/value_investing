"""从财务数据文件计算关键估值指标。"""

import os
import re
import sys

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

PROJECT_ROOT = os.getenv("PROJECT_ROOT", ".")
COMPANIES_DIR = os.getenv("COMPANIES_DIR", "companies")


def parse_financials_file(filepath: str) -> dict[str, float]:
    """从 Markdown 财务数据文件中解析数值。"""
    data: dict[str, float] = {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        logger.warning(f"文件不存在: {filepath}")
        return data

    # 匹配表格行格式: | 指标名 | 数值 |
    # 使用 [ \t] 而非 \s 防止跨行匹配（\s 会匹配 \n）
    pattern = r"\|[ \t]*([^|]+?)[ \t]*\|[ \t]*(-?[\d,]+\.?\d*)[ \t]*\|"
    for match in re.finditer(pattern, content):
        key = match.group(1).strip()
        try:
            value = float(match.group(2).replace(",", ""))
            data[key] = value
        except ValueError:
            continue

    return data


def calc_metrics(financials_data: dict[str, float]) -> dict[str, float | None]:
    """计算关键指标。"""
    metrics: dict[str, float | None] = {}

    # 基本财务数值
    revenue = financials_data.get("营业收入")
    cost = financials_data.get("营业成本")
    net_profit = financials_data.get("净利润")
    parent_profit = financials_data.get("归母净利润")
    total_assets = financials_data.get("总资产")
    total_liabilities = financials_data.get("总负债")
    equity = financials_data.get("股东权益")

    # 毛利率
    if revenue is not None and cost is not None and revenue != 0:
        metrics["毛利率"] = round((revenue - cost) / revenue * 100, 2)
    else:
        metrics["毛利率"] = None

    # 净利率
    if net_profit is not None and revenue is not None and revenue != 0:
        metrics["净利率"] = round(net_profit / revenue * 100, 2)
    else:
        metrics["净利率"] = None

    # ROE
    if parent_profit is not None and equity is not None and equity != 0:
        metrics["ROE"] = round(parent_profit / equity * 100, 2)
    else:
        metrics["ROE"] = None

    # 资产负债率
    if total_assets is not None and total_liabilities is not None and total_assets != 0:
        metrics["资产负债率"] = round(total_liabilities / total_assets * 100, 2)
    else:
        metrics["资产负债率"] = None

    return metrics


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="计算关键估值指标")
    parser.add_argument("ticker", help="股票代码")
    parser.add_argument("name", help="企业名称")
    args = parser.parse_args()

    # 输入校验
    if not re.fullmatch(r"[A-Za-z0-9]{1,10}", args.ticker):
        logger.error(f"无效的股票代码: {args.ticker}")
        sys.exit(1)
    if "/" in args.name or "\\" in args.name or ".." in args.name:
        logger.error(f"无效的企业名称: {args.name}")
        sys.exit(1)

    financials_dir = os.path.join(
        PROJECT_ROOT, COMPANIES_DIR, f"{args.ticker}-{args.name}", "financials"
    )

    if not os.path.exists(financials_dir):
        logger.error(f"财务数据目录不存在: {financials_dir}")
        logger.error("请先运行 fetch_financials.py 获取财务数据")
        sys.exit(1)

    # 收集所有期间数据
    files = sorted(os.listdir(financials_dir))
    all_periods: dict[str, dict[str, float]] = {}

    for filename in files:
        if not filename.endswith(".md"):
            continue
        period = filename.replace(".md", "")
        filepath = os.path.join(financials_dir, filename)
        data = parse_financials_file(filepath)
        if data:
            all_periods[period] = data

    if not all_periods:
        logger.error("未找到任何财务数据")
        sys.exit(1)

    # 计算各期间指标
    print("\n## 关键指标趋势")
    print()
    header = ["期间", "毛利率(%)", "净利率(%)", "ROE(%)", "资产负债率(%)"]
    print("| " + " | ".join(header) + " |")
    print("| " + " | ".join(["------"] * len(header)) + " |")

    for period, data in all_periods.items():
        m = calc_metrics(data)
        row = [
            period,
            f"{m['毛利率']:.1f}" if m["毛利率"] is not None else "-",
            f"{m['净利率']:.1f}" if m["净利率"] is not None else "-",
            f"{m['ROE']:.1f}" if m["ROE"] is not None else "-",
            f"{m['资产负债率']:.1f}" if m["资产负债率"] is not None else "-",
        ]
        print("| " + " | ".join(row) + " |")
