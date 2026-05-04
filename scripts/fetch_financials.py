"""从 akshare 拉取企业财务数据，输出到 Markdown 文件。

使用同花顺 "new" 接口分别获取利润表、资产负债表、现金流量表数据，
输出为结构化 Markdown。
"""

import os
import re
import sys
from datetime import date

import pandas as pd
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

PROJECT_ROOT = os.getenv("PROJECT_ROOT", ".")
COMPANIES_DIR = os.getenv("COMPANIES_DIR", "companies")

# 指标中文名 -> metric_name
KEY_FIELDS: list[tuple[str, str]] = [
    # (显示名称, metric_name)
    ("营业收入", "operating_income_total"),
    ("营业成本", "operating_costs_total"),
    ("营业利润", "operating_profit"),
    ("利润总额", "profit_total"),
    ("净利润", "net_profit"),
    ("归母净利润", "parent_holder_net_profit"),
    ("总资产", "assets_total"),
    ("流动资产", "total_current_assets"),
    ("总负债", "total_debt"),
    ("流动负债", "current_total_debt"),
    ("股东权益", "holder_equity_total"),
    ("经营现金流", "act_cash_flow_net"),
    ("投资现金流", "invest_cash_flow_net"),
    ("筹资现金流", "financing_cash_flow_net"),
]


def _fetch_to_long(symbol: str, api_func) -> pd.DataFrame | None:
    """调用 akshare 接口并返回 long-format DataFrame。

    预期列: report_period, metric_name, value
    """
    try:
        df = api_func(symbol=symbol, indicator="按报告期")
    except Exception as e:
        logger.error(f"API 调用失败: {e}")
        return None

    if df is None or df.empty:
        logger.warning("返回空数据")
        return None

    required = {"report_period", "metric_name", "value"}
    missing = required - set(df.columns)
    if missing:
        logger.warning(f"缺少预期列 {missing}，可用列: {list(df.columns)}")
        return None

    return df


def _long_to_period_dict(long_df: pd.DataFrame) -> dict[str, dict[str, float]]:
    """将 long-format DataFrame 转为 {report_period: {metric_name: value}}。"""
    result: dict[str, dict[str, float]] = {}
    for _, row in long_df.iterrows():
        period = str(row["report_period"])
        metric = str(row["metric_name"])
        val = row["value"]
        if pd.isna(val):
            continue
        try:
            numeric = float(val)
        except (ValueError, TypeError):
            continue
        result.setdefault(period, {})[metric] = numeric
    return result


def fetch_a_share_financials(ticker: str) -> dict[str, dict[str, float]] | None:
    """从 akshare 拉取 A 股财务数据。

    合并利润表、资产负债表、现金流量表为一个嵌套字典：
        {report_period: {metric_name: value}}
    """
    import akshare as ak

    benefit_df = _fetch_to_long(ticker, ak.stock_financial_benefit_new_ths)
    debt_df = _fetch_to_long(ticker, ak.stock_financial_debt_new_ths)
    cash_df = _fetch_to_long(ticker, ak.stock_financial_cash_new_ths)

    combined: dict[str, dict[str, float]] = {}
    for df in [benefit_df, debt_df, cash_df]:
        if df is None:
            continue
        period_dict = _long_to_period_dict(df)
        for period, metrics in period_dict.items():
            combined.setdefault(period, {}).update(metrics)

    if not combined:
        logger.error(f"未获取到 {ticker} 的财务数据")
        return None

    logger.info(f"获取 {ticker} 财务数据: {len(combined)} 个报告期")
    return combined


def format_financials_markdown(
    ticker: str,
    name: str,
    year: int,
    quarter: int,
    data: dict[str, dict[str, float]],
) -> str:
    """将财务数据格式化为 Markdown 内容。"""
    period_key = f"{year}-{quarter}"

    lines = [
        f"# {name} 财务数据 - {year}-Q{quarter}",
        "",
        f"> 数据来源：akshare 同花顺 | 拉取时间：{date.today().isoformat()}",
        "",
    ]

    if period_key not in data:
        lines.append(f"**暂无 {year}-Q{quarter} 期间数据**")
        return "\n".join(lines)

    period_data = data[period_key]

    lines.append("## 关键财务数据")
    lines.append("")
    lines.append("| 指标 | 数值（元） |")
    lines.append("|------|-----------|")

    for label, metric_name in KEY_FIELDS:
        if metric_name in period_data:
            val = period_data[metric_name]
            lines.append(f"| {label} | {val:,.2f} |")

    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="拉取企业财务数据")
    parser.add_argument("ticker", help="股票代码")
    parser.add_argument("name", help="企业名称")
    parser.add_argument(
        "--year",
        type=int,
        default=date.today().year - 1,
        help="年份（默认去年）",
    )
    parser.add_argument(
        "--quarter",
        type=int,
        choices=[1, 2, 3, 4],
        help="季度（1-4），不指定则拉取全年各季度",
    )
    args = parser.parse_args()

    # Fix 1: 路径穿越防护 — 校验输入
    if not re.fullmatch(r"^[A-Za-z0-9]{1,10}$", args.ticker):
        logger.error(f"股票代码格式无效（仅允许 1-10 位字母数字）: {args.ticker}")
        sys.exit(1)
    if "/" in args.name or "\\" in args.name or ".." in args.name:
        logger.error(f"企业名称包含非法字符（/, \\, ..）: {args.name}")
        sys.exit(1)

    company_dir = os.path.join(
        PROJECT_ROOT, COMPANIES_DIR, f"{args.ticker}-{args.name}"
    )

    # Fix 1: 路径穿越防护 — 确认目标在 COMPANIES_DIR 下
    allowed_root = os.path.realpath(os.path.join(PROJECT_ROOT, COMPANIES_DIR))
    if not os.path.realpath(company_dir).startswith(allowed_root):
        logger.error(f"目标目录不在允许的范围内: {company_dir}")
        sys.exit(1)

    financials_dir = os.path.join(company_dir, "financials")

    if not os.path.exists(company_dir):
        logger.error(f"企业目录不存在: {company_dir}，请先运行 new_company.py")
        sys.exit(1)

    os.makedirs(financials_dir, exist_ok=True)

    data = fetch_a_share_financials(args.ticker)
    if data is None:
        logger.error("未能获取财务数据，请检查股票代码是否正确")
        sys.exit(1)

    quarters = [args.quarter] if args.quarter else [1, 2, 3, 4]
    for q in quarters:
        md_content = format_financials_markdown(
            args.ticker, args.name, args.year, q, data
        )
        filepath = os.path.join(financials_dir, f"{args.year}-Q{q}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)
        logger.success(f"写入: {filepath}")
