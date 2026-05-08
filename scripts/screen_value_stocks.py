"""批量价值投资筛选脚本。

按量化价值投资框架（ROE/PE 剪刀差 + OCF 验证 + 分红质量 + 安全性），
从全 A 股中筛选并排序。

用法:
    uv run scripts/screen_value_stocks.py                     # 默认参数
    uv run scripts/screen_value_stocks.py --pe-max 15         # PE ≤ 15x
    uv run scripts/screen_value_stocks.py --market-cap 100    # 市值 ≥ 100亿
    uv run scripts/screen_value_stocks.py --top 30            # 输出 Top 30
    uv run scripts/screen_value_stocks.py --output top50.csv  # 导出 CSV
"""

import argparse
import concurrent.futures
import os
import sys
from dataclasses import dataclass, field
from datetime import date

import pandas as pd
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# ── 复用 fetch_financials.py 中的 A 股字段映射和转换函数 ──
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_financials import (
    A_KEY_FIELDS,
    _fetch_to_long,
    _long_to_period_dict,
)

# ── 财务指标中文名 → 内部 key ──
_FIELD_MAP = {cn: en for cn, en in A_KEY_FIELDS}


@dataclass
class StockScore:
    """单只股票的评分卡。"""
    code: str
    name: str
    price: float
    market_cap: float          # 亿
    pe: float                  # 静态 PE
    roe: float = 0.0           # 最近 FY 的 ROE（%）
    roe_3y: list[float] = field(default_factory=list)  # 近 3 年 ROE
    gross_margin: float = 0.0  # 毛利率（%）
    net_margin: float = 0.0    # 净利率（%）
    debt_ratio: float = 0.0    # 资产负债率（%）
    ocf_ni_ratio: float = 0.0  # OCF/净利润
    revenue_yoy: float = 0.0   # 营收同比（%）
    profit_yoy: float = 0.0    # 利润同比（%）

    # 评分
    score_roe: float = 0.0
    score_value: float = 0.0
    score_safety: float = 0.0
    score_dividend: float = 0.0
    total_score: float = 0.0

    def __repr__(self) -> str:
        return (
            f"{self.code} {self.name:8s} "
            f"总分{self.total_score:4.0f} "
            f"ROE{self.roe:5.1f}% PE{self.pe:5.1f}x "
            f"ROE/PE{self.roe/self.pe if self.pe else 0:.2f} "
        )


def _get_latest_fy(data: dict[str, dict[str, float]]) -> str | None:
    """获取最近一个 Q4（财年）的报告期。"""
    q4_periods = sorted([p for p in data if p.endswith("-4")], reverse=True)
    return q4_periods[0] if q4_periods else None


def _calc_roe(net_profit: float, equity: float) -> float:
    """计算 ROE（%）。"""
    return (net_profit / equity) * 100 if equity else 0.0


def _calc_ratio(numerator: float, denominator: float) -> float:
    """安全除法，返回小数。"""
    return numerator / denominator if denominator else 0.0


def fetch_and_score(code: str, name: str, price: float, pe: float,
                    market_cap: float) -> StockScore | None:
    """拉取单只股票的财务数据并评分。"""
    import akshare as ak

    score = StockScore(code=code, name=name, price=price, pe=pe,
                       market_cap=market_cap)

    # ── 拉取三张表 ──
    try:
        benefit_df = _fetch_to_long(code, ak.stock_financial_benefit_new_ths)
        debt_df = _fetch_to_long(code, ak.stock_financial_debt_new_ths)
        cash_df = _fetch_to_long(code, ak.stock_financial_cash_new_ths)
    except Exception:
        return None

    combined: dict[str, dict[str, float]] = {}
    for df in [benefit_df, debt_df, cash_df]:
        if df is None:
            continue
        for period, metrics in _long_to_period_dict(df).items():
            combined.setdefault(period, {}).update(metrics)

    if not combined:
        return None

    # ── 找最近两个可用 Q4（跳过数据明显不完整的年份）──
    all_q4 = sorted([p for p in combined if p.endswith("-4")], reverse=True)
    if not all_q4:
        return None

    # 最新 Q4 营收不到前一年的 50% → 数据不全，用前一年
    usable_q4 = [all_q4[0]]
    for i in range(1, len(all_q4)):
        curr = all_q4[i]
        prev = usable_q4[-1]
        rev_curr = combined[curr].get("operating_income_total", 0) or combined[curr].get("operating_income", 0)
        rev_prev = combined[prev].get("operating_income_total", 0) or combined[prev].get("operating_income", 0)
        # 最新选中的 Q4 营收如果不到候选 Q4 的 50%，说明最新是残缺数据
        if rev_curr > 0 and rev_prev > 0 and rev_prev < rev_curr * 0.5:
            usable_q4[-1] = curr  # 用 curr 替换残缺的 prev
        else:
            usable_q4.append(curr)

    latest_q4 = usable_q4[0]
    prev_q4 = usable_q4[1] if len(usable_q4) > 1 else None

    d = combined[latest_q4]
    p = combined[prev_q4] if prev_q4 else {}

    # ── 提取关键指标（API 返回英文 metric_name）──
    revenue = d.get("operating_income_total") or d.get("operating_income", 0)
    cost = d.get("operating_costs_total") or d.get("operating_costs", 0)
    net_profit = d.get("net_profit", 0)
    parent_profit = d.get("parent_holder_net_profit", net_profit)
    total_assets = d.get("assets_total", 0)
    total_debt = d.get("total_debt", 0)
    equity = d.get("holder_equity_total") or d.get("parent_holder_equity_total", 0)
    ocf = d.get("act_cash_flow_net", 0)

    prev_revenue = p.get("operating_income_total") or p.get("operating_income", 0)
    prev_profit = p.get("net_profit", 0)

    # ── 计算指标 ──
    if equity > 0:
        score.roe = _calc_roe(parent_profit, equity)
    if revenue > 0:
        score.gross_margin = ((revenue - cost) / revenue) * 100 if cost else 0
        score.net_margin = (net_profit / revenue) * 100 if net_profit else 0
    if total_assets > 0:
        score.debt_ratio = (total_debt / total_assets) * 100
    if net_profit > 0 and ocf != 0:
        score.ocf_ni_ratio = ocf / net_profit
    if prev_revenue > 0:
        score.revenue_yoy = ((revenue - prev_revenue) / prev_revenue) * 100
    if prev_profit and prev_profit > 0:
        score.profit_yoy = ((net_profit - prev_profit) / prev_profit) * 100

    # ── 计算近 3 年 ROE（用于稳定性评分） ──
    roe_3y = []
    for q4 in usable_q4[:3]:
        fy_data = combined[q4]
        fy_profit = fy_data.get("parent_holder_net_profit", fy_data.get("net_profit", 0))
        fy_equity = fy_data.get("holder_equity_total") or fy_data.get("parent_holder_equity_total", 0)
        if fy_equity > 0:
            roe_3y.append(_calc_roe(fy_profit, fy_equity))
    score.roe_3y = roe_3y

    # ═══════════════════════════════
    # 评分
    # ═══════════════════════════════

    # ── ROE 质量（40 分）──
    # ROE 水平（25 分）
    roe_val = score.roe
    if roe_val > 20:
        score.score_roe += 25
    elif roe_val > 15:
        score.score_roe += 18
    elif roe_val > 10:
        score.score_roe += 10
    # < 10% 得 0 分

    # ROE 稳定性（10 分）：近 3 年标准差
    if len(roe_3y) >= 3:
        import statistics
        std_roe = statistics.stdev(roe_3y)
        if std_roe < 3:
            score.score_roe += 10
        elif std_roe < 5:
            score.score_roe += 5
    elif len(roe_3y) == 2:
        diff = abs(roe_3y[0] - roe_3y[1])
        if diff < 3:
            score.score_roe += 7
        elif diff < 5:
            score.score_roe += 3

    # ROE 趋势（5 分）
    if len(roe_3y) >= 2:
        if roe_3y[0] > roe_3y[-1] * 1.02:
            score.score_roe += 5   # 升
        elif roe_3y[0] > roe_3y[-1] * 0.98:
            score.score_roe += 3   # 稳
        # 否则降，得 0 分

    # ── 估值折价（30 分）──
    roe_pe = score.roe / pe if pe > 0 else 0
    if roe_pe > 2.0:
        score.score_value += 20
    elif roe_pe > 1.5:
        score.score_value += 15
    elif roe_pe > 1.0:
        score.score_value += 10
    elif roe_pe > 0.5:
        score.score_value += 3

    # PE 绝对值（10 分）
    if pe < 10:
        score.score_value += 10
    elif pe < 15:
        score.score_value += 7
    elif pe < 20:
        score.score_value += 3

    # ── 安全性（20 分）──
    # 资产负债率（10 分）
    dr = score.debt_ratio
    if dr < 30:
        score.score_safety += 10
    elif dr < 50:
        score.score_safety += 7
    elif dr < 70:
        score.score_safety += 3

    # OCF/净利润（10 分）
    ocf_ni = score.ocf_ni_ratio
    if ocf_ni > 1.0:
        score.score_safety += 10
    elif ocf_ni > 0.7:
        score.score_safety += 5
    elif ocf_ni > 0.3:
        score.score_safety += 2
    # < 0.3 或负值得 0 分

    # ── 分红质量（10 分）──
    # 用 (ROE * (1-分红率)) 反推近似股息率
    # 更准确的方式：按 ROE 和 PE 估算股息率 = 分红率/PE
    # 假设成熟企业分红率 30-60%，取 40% 中值估算
    # 实际估算：盈利收益率(E/P) × 0.4 = (1/PE) × 0.4
    est_div_yield = (1 / pe) * 0.4 * 100 if pe > 0 else 0
    # 实际上用 ROE/PE × 0.4 更对：ROE% × 0.4 / PE = 股息率
    est_div_yield = (score.roe * 0.4) / pe if pe > 0 else 0

    if est_div_yield > 4:
        score.score_dividend += 5
    elif est_div_yield > 2:
        score.score_dividend += 3
    elif est_div_yield > 1:
        score.score_dividend += 1

    score.total_score = (score.score_roe + score.score_value +
                         score.score_safety + score.score_dividend)
    return score


def screen_stocks(pe_max: float = 25, pb_min: float = 0.5,
                  market_cap_min: float = 50.0, top_n: int = 50,
                  workers: int = 6) -> list[StockScore]:
    """主筛选函数。

    Args:
        pe_max: 市盈率上限
        pb_min: 市净率下限
        market_cap_min: 市值下限（亿）
        top_n: 输出前 N 名
        workers: 并发线程数
    """
    import akshare as ak

    logger.info("【第一层】获取全 A 股行情数据...")
    df_all = ak.stock_zh_a_spot_em()

    # 过滤
    df = df_all.copy()
    df = df[(df["市盈率-动态"] > 0) & (df["市盈率-动态"] <= pe_max)]
    df = df[df["市净率"] > pb_min]
    df = df[df["总市值"] > market_cap_min * 1e8]

    # 剔除 ST
    df = df[~df["名称"].str.contains("ST|退市", na=False)]
    # 剔除金融/保险/证券/航空（天然高杠杆，不适配统一评分）
    exclude_keywords = "银行|保险|证券|信托|租赁|航空|机场|太保|人寿|海航|春秋|吉祥"
    df = df[~df["名称"].str.contains(exclude_keywords, na=False)]
    # 剔除新股（上市时间<1年，代码段688/689可暂不过滤）

    total = len(df)
    logger.info(f"【第一层】筛选后剩余 {total} 只股票（全市场 {len(df_all)} 只）")

    # ── 按市值排序后分批处理（优先大市值） ──
    df = df.sort_values("总市值", ascending=False)

    logger.info(f"【第二层】并发拉取财务数据（{workers} 线程），预计 8-15 分钟...")
    results: list[StockScore] = []
    processed = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {}
        for _, row in df.iterrows():
            code = row["代码"]
            name = row["名称"]
            price = row["最新价"]
            pe = row["市盈率-动态"]
            mcap = row["总市值"] / 1e8

            fut = executor.submit(fetch_and_score, code, name, price, pe, mcap)
            futures[fut] = (code, name)

        for fut in concurrent.futures.as_completed(futures):
            code, name = futures[fut]
            processed += 1
            try:
                result = fut.result()
                if result and result.total_score > 0:
                    results.append(result)
            except Exception:
                pass

            if processed % 100 == 0:
                logger.info(f"  进度: {processed}/{total}")

    # ── 排名 ──
    results.sort(key=lambda s: s.total_score, reverse=True)
    logger.info(f"【第三层】评分完成，有效结果 {len(results)} 只")

    return results[:top_n]


def print_table(scores: list[StockScore]) -> None:
    """打印排名表。"""
    header = (
        f"{'排名':<4} {'代码':<8} {'名称':<10} {'总分':>4} "
        f"{'ROE%':>6} {'PE':>5} {'ROE/PE':>7} "
        f"{'负债%':>6} {'OCF/利':>6} {'毛利率%':>7} {'净利率%':>7}"
    )
    print("\n" + "=" * len(header))
    print(header)
    print("-" * len(header))

    for i, s in enumerate(scores, 1):
        roe_pe = s.roe / s.pe if s.pe else 0
        print(
            f"{i:<4} {s.code:<8} {s.name:<10} {s.total_score:4.0f} "
            f"{s.roe:6.1f} {s.pe:5.1f} {roe_pe:7.2f} "
            f"{s.debt_ratio:6.1f} {s.ocf_ni_ratio:6.2f} "
            f"{s.gross_margin:7.1f} {s.net_margin:7.1f}"
        )
    print("=" * len(header))
    print(f"共 {len(scores)} 只 | 数据日期: {date.today()}")


def export_csv(scores: list[StockScore], path: str) -> None:
    """导出 CSV。"""
    rows = []
    for i, s in enumerate(scores, 1):
        rows.append({
            "排名": i,
            "代码": s.code,
            "名称": s.name,
            "总分": round(s.total_score, 1),
            "ROE(%)": round(s.roe, 1),
            "PE": round(s.pe, 1),
            "ROE/PE": round(s.roe / s.pe, 2) if s.pe else 0,
            "资产负债率(%)": round(s.debt_ratio, 1),
            "OCF/净利润": round(s.ocf_ni_ratio, 2),
            "毛利率(%)": round(s.gross_margin, 1),
            "净利率(%)": round(s.net_margin, 1),
            "ROE得分": round(s.score_roe, 1),
            "估值得分": round(s.score_value, 1),
            "安全得分": round(s.score_safety, 1),
            "分红得分": round(s.score_dividend, 1),
            "市值(亿)": round(s.market_cap, 0),
            "股价": s.price,
        })
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8-sig")
    logger.success(f"导出: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="全 A 股价值投资批量筛选",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  uv run scripts/screen_value_stocks.py
  uv run scripts/screen_value_stocks.py --pe-max 15
  uv run scripts/screen_value_stocks.py --market-cap 100 --top 20
  uv run scripts/screen_value_stocks.py --output top50.csv
        """,
    )
    parser.add_argument("--pe-max", type=float, default=25,
                        help="市盈率上限（默认 25）")
    parser.add_argument("--pb-min", type=float, default=0.5,
                        help="市净率下限（默认 0.5）")
    parser.add_argument("--market-cap", type=float, default=50,
                        help="市值下限/亿元（默认 50）")
    parser.add_argument("--top", type=int, default=50,
                        help="输出前 N 名（默认 50）")
    parser.add_argument("--workers", type=int, default=6,
                        help="并发线程数（默认 6）")
    parser.add_argument("--output", type=str, default=None,
                        help="导出 CSV 路径（可选）")
    args = parser.parse_args()

    scores = screen_stocks(
        pe_max=args.pe_max,
        pb_min=args.pb_min,
        market_cap_min=args.market_cap,
        top_n=args.top,
        workers=args.workers,
    )

    print_table(scores)

    if args.output:
        export_csv(scores, args.output)


if __name__ == "__main__":
    main()
