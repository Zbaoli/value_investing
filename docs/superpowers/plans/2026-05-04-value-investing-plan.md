# 价值投资分析项目 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建以 Markdown 文件库为核心的价值投资分析项目，包含模板系统、企业目录结构、Python 数据脚本。

**Architecture:** 纯文件系统项目——`companies/` 按企业组织 Markdown 文件，`templates/` 提供标准化模板，`scripts/` 是独立 Python 辅助脚本，`cross-cutting/` 做跨企业视图。无数据库、无前端。

**Tech Stack:** Python 3.11+, akshare, pandas, python-dotenv, loguru, uv 包管理

---

### Task 1: 项目基础文件

**Files:**
- Create: `pyproject.toml`
- Create: `.env`
- Create: `.gitignore`

- [ ] **Step 1: 创建 pyproject.toml**

```toml
[project]
name = "value-investing"
version = "0.1.0"
description = "价值投资分析项目"
requires-python = ">=3.11"
dependencies = [
    "akshare",
    "pandas",
    "python-dotenv",
    "loguru",
]

[tool.ruff]
line-length = 100
```

- [ ] **Step 2: 创建 .env**

```
PROJECT_ROOT=.
COMPANIES_DIR=companies
TEMPLATES_DIR=templates
```

- [ ] **Step 3: 创建 .gitignore**

```
.env
__pycache__/
.venv/
*.pyc
uv.lock
```

- [ ] **Step 4: 安装依赖**

```bash
cd /Users/baoli/Documents/warehouse/value_investing && uv venv && uv sync
```

- [ ] **Step 5: 验证安装**

```bash
cd /Users/baoli/Documents/warehouse/value_investing && uv run python -c "import akshare; import pandas; import dotenv; import loguru; print('ok')"
```

Expected: prints "ok"

---

### Task 2: 模板文件

**Files:**
- Create: `templates/profile.tmpl.md`
- Create: `templates/deep-research.tmpl.md`
- Create: `templates/financials.tmpl.md`
- Create: `templates/tracking.tmpl.md`

- [ ] **Step 1: 创建目录**

```bash
mkdir -p /Users/baoli/Documents/warehouse/value_investing/templates
```

- [ ] **Step 2: 创建 templates/profile.tmpl.md**

```markdown
# {{COMPANY_NAME}}（{{TICKER}}）

## 一句话描述
<!-- 用一句话说明这家公司做什么、为什么存在 -->

## 商业模式
<!-- 怎么赚钱？收入结构？成本结构？轻资产/重资产？ -->

## 护城河
<!-- 品牌、转换成本、网络效应、规模优势、特许经营权？ -->
<!-- 护城河宽度评估：宽 / 中 / 窄 / 无 -->

## 行业地位
<!-- 市场份额、竞争格局、上下游议价权 -->

## 管理层评估
<!-- 能力、诚信、资本配置能力、股东文化 -->
<!-- 关键人物：-->

## 增长驱动
<!-- 量价增长来源、新业务、国际化、并购 -->

## 关键风险
<!-- 护城河削弱、竞争、监管、技术颠覆、宏观 -->
```

- [ ] **Step 3: 创建 templates/deep-research.tmpl.md**

```markdown
# {{COMPANY_NAME}} 深度研报

> 初稿：{{DATE}} | 最后修订：{{DATE}}

## 投资 Thesis
<!-- 3句话内说清：为什么这家公司值得投资 -->

## 一、公司概览
<!-- 从 profile 摘录，简要回顾 -->

## 二、护城河深度分析
<!-- 这是报告核心，定量+定性 -->
<!-- 护城河类型、宽度、趋势（增强/削弱） -->
<!-- ROIC 历史趋势作为护城河的定量证据 -->

## 三、财务分析
<!-- 过去 5-10 年关键指标趋势 -->
<!-- ROE、ROIC、毛利率、净利率、FCF/Sales -->
<!-- 资产负债结构、有息负债率 -->
<!-- 增长质量（收入增速 vs 利润增速） -->

## 四、估值
<!-- 估值方法选择（DCF、PE 历史分位、FCF Yield 等） -->
<!-- 保守假设 + 合理假设的情况 -->
<!-- 安全边际判断 -->

## 五、风险与反驳
<!-- 列出最重要的看空观点，认真思考 -->
<!-- 什么情况下 thesis 会失效？ -->

## 六、结论与行动计划
<!-- 买入区间、仓位上限、观察点 -->
<!-- 什么情况下需要重新评估？ -->
```

- [ ] **Step 4: 创建 templates/financials.tmpl.md**

```markdown
# {{COMPANY_NAME}} 财务数据 - {{PERIOD}}

## 利润表
| 项目 | 本季 | 同比(%) | 年初至今 | 同比(%) |
|------|------|---------|----------|---------|
| 营业收入 | | | | |
| 营业成本 | | | | |
| 毛利 | | | | |
| 销售费用 | | | | |
| 管理费用 | | | | |
| 研发费用 | | | | |
| 营业利润 | | | | |
| 利润总额 | | | | |
| 净利润 | | | | |
| 归母净利润 | | | | |

## 资产负债表
| 项目 | 期末 | 期初 | 变动 |
|------|------|------|------|
| 总资产 | | | |
| 流动资产 | | | |
| 货币资金 | | | |
| 应收账款 | | | |
| 存货 | | | |
| 非流动资产 | | | |
| 固定资产 | | | |
| 无形资产 | | | |
| 总负债 | | | |
| 流动负债 | | | |
| 有息负债 | | | |
| 股东权益 | | | |
| 归母权益 | | | |

## 现金流量表
| 项目 | 本季 | 年初至今 |
|------|------|----------|
| 经营活动现金流 | | |
| 投资活动现金流 | | |
| 筹资活动现金流 | | |
| 资本开支 | | |
| 自由现金流 | | |

## 关键比率
| 指标 | 数值 | 行业均值 | 评价 |
|------|------|----------|------|
| ROE | | | |
| ROIC | | | |
| 毛利率 | | | |
| 净利率 | | | |
| FCF 转化率 | | | |
| 有息负债率 | | | |
| 流动比率 | | | |
```

- [ ] **Step 5: 创建 templates/tracking.tmpl.md**

```markdown
# {{COMPANY_NAME}} 跟踪日志

> 持续跟踪记录，倒序排列（最新在前）

## {{DATE}} - 初始跟踪

<!-- 事件描述、影响分析、观点变化 -->
```

---

### Task 3: 跨企业视图文件

**Files:**
- Create: `cross-cutting/watchlist.md`
- Create: `cross-cutting/allocation.md`
- Create: `cross-cutting/themes.md`

- [ ] **Step 1: 创建目录**

```bash
mkdir -p /Users/baoli/Documents/warehouse/value_investing/cross-cutting
```

- [ ] **Step 2: 创建 cross-cutting/watchlist.md**

```markdown
# 观察列表

> 跟踪企业的估值对比与观察要点

## 核心持仓

| 企业 | 代码 | 关注方向 | 理想买入区间 | 当前状态 |
|------|------|----------|-------------|----------|
| | | | | |

## 观察中

| 企业 | 代码 | 关注方向 | 等待条件 | 备注 |
|------|------|----------|----------|------|
| | | | | |
```

- [ ] **Step 3: 创建 cross-cutting/allocation.md**

```markdown
# 持仓与组合管理

> 仓位记录与组合审视

## 当前持仓

| 企业 | 代码 | 仓位占比 | 成本 | 日期 | 备注 |
|------|------|----------|------|------|------|
| | | | | | |

## 组合审视
- 行业集中度：
- 仓位满意度：
- 调仓计划：
```

- [ ] **Step 4: 创建 cross-cutting/themes.md**

```markdown
# 跨企业主题研究

> 行业趋势、宏观思考、投资理念演进

## 当前主题

### 主题名称
<!-- 背景、涉及企业、观点 -->

## 历史主题归档
<!-- 已完成或放弃的主题分析 -->
```

---

### Task 4: 企业脚手架脚本

**Files:**
- Create: `scripts/new_company.py`
- Modify: `templates/tracking.tmpl.md` (if needed, depends on template)

- [ ] **Step 1: 创建 scripts 目录**

```bash
mkdir -p /Users/baoli/Documents/warehouse/value_investing/scripts
```

- [ ] **Step 2: 创建 scripts/new_company.py**

```python
"""交互式创建新企业目录和模板文件。"""

import os
import sys
from datetime import date

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

PROJECT_ROOT = os.getenv("PROJECT_ROOT", ".")
COMPANIES_DIR = os.getenv("COMPANIES_DIR", "companies")
TEMPLATES_DIR = os.getenv("TEMPLATES_DIR", "templates")


def render_template(content: str, **kwargs) -> str:
    """替换模板中的占位符。"""
    for key, value in kwargs.items():
        content = content.replace("{{%s}}" % key, value)
    return content


def create_company(ticker: str, name: str) -> str:
    """创建企业目录结构并生成模板文件。"""
    dir_name = f"{ticker}-{name}"
    company_dir = os.path.join(PROJECT_ROOT, COMPANIES_DIR, dir_name)
    financials_dir = os.path.join(company_dir, "financials")
    templates_dir = os.path.join(PROJECT_ROOT, TEMPLATES_DIR)

    if os.path.exists(company_dir):
        logger.error(f"企业目录已存在: {company_dir}")
        sys.exit(1)

    os.makedirs(financials_dir)

    today = date.today().isoformat()
    vars_map = {
        "COMPANY_NAME": name,
        "TICKER": ticker,
        "DATE": today,
    }

    # 从模板创建各文件
    file_template_map = {
        "profile.tmpl.md": os.path.join(company_dir, "profile.md"),
        "deep-research.tmpl.md": os.path.join(company_dir, "deep-research.md"),
        "tracking.tmpl.md": os.path.join(company_dir, "tracking.md"),
    }

    for tmpl_name, dest_path in file_template_map.items():
        tmpl_path = os.path.join(templates_dir, tmpl_name)
        if os.path.exists(tmpl_path):
            with open(tmpl_path, "r", encoding="utf-8") as f:
                content = f.read()
            rendered = render_template(content, **vars_map)
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(rendered)
            logger.info(f"创建: {dest_path}")
        else:
            logger.warning(f"模板不存在: {tmpl_name}")

    # 思考链文件不从模板生成，直接创建空文件
    thinking_path = os.path.join(company_dir, "thinking.md")
    with open(thinking_path, "w", encoding="utf-8") as f:
        f.write(f"# {name} 思考链\n\n> 投资逻辑碎片记录\n")
    logger.info(f"创建: {thinking_path}")

    logger.success(f"企业 {name}({ticker}) 创建完成: {company_dir}")
    return company_dir


if __name__ == "__main__":
    ticker = input("请输入股票代码: ").strip()
    name = input("请输入企业名称（拼音简称，如 贵州茅台）: ").strip()
    if not ticker or not name:
        logger.error("代码和名称不能为空")
        sys.exit(1)
    create_company(ticker, name)
```

- [ ] **Step 3: 验证脚本**

```bash
cd /Users/baoli/Documents/warehouse/value_investing && uv run python scripts/new_company.py
```

手动输入测试代码和名称（例如 `600519` / `贵州茅台`），检查目录结构是否正确生成。

---

### Task 5: 财务数据拉取脚本

**Files:**
- Create: `scripts/fetch_financials.py`

- [ ] **Step 1: 创建 scripts/fetch_financials.py**

```python
"""从 akshare 拉取企业财务数据，输出到 Markdown 文件。"""

import os
import sys
from datetime import date

import pandas as pd
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

PROJECT_ROOT = os.getenv("PROJECT_ROOT", ".")
COMPANIES_DIR = os.getenv("COMPANIES_DIR", "companies")


def fetch_a_share_financials(ticker: str, year: int, quarter: int) -> pd.DataFrame | None:
    """
    从 akshare 拉取 A 股财务摘要数据。
    使用同花顺接口，返回利润表+资产负债表+现金流关键指标。
    """
    import akshare as ak

    try:
        df = ak.stock_financial_abstract_ths(symbol=ticker, indicator="按报告期")
        if df is None or df.empty:
            logger.error(f"未获取到 {ticker} 的财务数据")
            return None
        logger.info(f"获取 {ticker} 财务数据: {len(df)} 条记录")
        return df
    except Exception as e:
        logger.error(f"获取 {ticker} 财务数据失败: {e}")
        return None


def format_financials_markdown(
    ticker: str, name: str, year: int, quarter: int, df: pd.DataFrame
) -> str:
    """将财务数据 DataFrame 格式化为 Markdown 内容。"""
    # 过滤目标期间的数据
    period_str = f"{year}-{quarter:02d}-"
    filtered = df[df["报告期"].astype(str).str.startswith(period_str)]

    lines = [
        f"# {name} 财务数据 - {year}-Q{quarter}",
        "",
        f"> 数据来源：akshare 同花顺 | 拉取时间：{date.today().isoformat()}",
        "",
    ]

    if filtered.empty:
        lines.append("**暂无该期间数据**")
        return "\n".join(lines)

    # 输出关键字段表格
    row = filtered.iloc[0]
    key_fields = [
        ("营业收入", "营业收入"),
        ("营业成本", "营业成本"),
        ("营业利润", "营业利润"),
        ("利润总额", "利润总额"),
        ("净利润", "净利润"),
        ("归母净利润", "归属于母公司所有者的净利润"),
        ("总资产", "资产总计"),
        ("流动资产", "流动资产合计"),
        ("总负债", "负债合计"),
        ("流动负债", "流动负债合计"),
        ("股东权益", "股东权益合计"),
        ("经营现金流", "经营活动现金流量净额"),
        ("投资现金流", "投资活动现金流量净额"),
        ("筹资现金流", "筹资活动现金流量净额"),
    ]

    lines.append("## 关键财务数据")
    lines.append("")
    lines.append("| 指标 | 数值（元） |")
    lines.append("|------|-----------|")

    for label, field in key_fields:
        if field in row.index:
            val = row[field]
            if pd.notna(val):
                lines.append(f"| {label} | {val:,.2f} |")

    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="拉取企业财务数据")
    parser.add_argument("ticker", help="股票代码")
    parser.add_argument("name", help="企业名称")
    parser.add_argument("--year", type=int, default=date.today().year - 1,
                        help="年份（默认去年）")
    parser.add_argument("--quarter", type=int, choices=[1, 2, 3, 4],
                        help="季度（1-4），不指定则拉取全年各季度")
    args = parser.parse_args()

    company_dir = os.path.join(PROJECT_ROOT, COMPANIES_DIR, f"{args.ticker}-{args.name}")
    financials_dir = os.path.join(company_dir, "financials")
    os.makedirs(financials_dir, exist_ok=True)

    df = fetch_a_share_financials(args.ticker, args.year, args.quarter or 1)
    if df is None:
        sys.exit(1)

    quarters = [args.quarter] if args.quarter else [1, 2, 3, 4]
    for q in quarters:
        md_content = format_financials_markdown(args.ticker, args.name, args.year, q, df)
        filepath = os.path.join(financials_dir, f"{args.year}-Q{q}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)
        logger.success(f"写入: {filepath}")
```

- [ ] **Step 2: 验证脚本**

```bash
cd /Users/baoli/Documents/warehouse/value_investing && uv run python scripts/fetch_financials.py 600519 贵州茅台 --year 2025 --quarter 4
```

检查是否成功拉取数据并生成 `companies/600519-贵州茅台/financials/2025-Q4.md`。

---

### Task 6: 关键指标计算脚本

**Files:**
- Create: `scripts/gen_metrics.py`

- [ ] **Step 1: 创建 scripts/gen_metrics.py**

```python
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
    pattern = r"\|\s*(.+?)\s*\|\s*([\d,]+\.?\d*)\s*\|"
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
    if revenue and cost and revenue != 0:
        metrics["毛利率"] = round((revenue - cost) / revenue * 100, 2)
    else:
        metrics["毛利率"] = None

    # 净利率
    if net_profit and revenue and revenue != 0:
        metrics["净利率"] = round(net_profit / revenue * 100, 2)
    else:
        metrics["净利率"] = None

    # ROE
    if parent_profit and equity and equity != 0:
        metrics["ROE"] = round(parent_profit / equity * 100, 2)
    else:
        metrics["ROE"] = None

    # 资产负债率
    if total_assets and total_liabilities and total_assets != 0:
        metrics["资产负债率"] = round(total_liabilities / total_assets * 100, 2)
    else:
        metrics["资产负债率"] = None

    return metrics


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="计算关键估值指标")
    parser.add_argument("ticker", help="股票代码")
    parser.add_argument("name", help="企业名称")
    parser.add_argument("--period-start", help="起始期间，如 2020-Q1")
    parser.add_argument("--period-end", help="结束期间，如 2025-Q4")
    args = parser.parse_args()

    financials_dir = os.path.join(
        PROJECT_ROOT, COMPANIES_DIR, f"{args.ticker}-{args.name}", "financials"
    )

    if not os.path.exists(financials_dir):
        logger.error(f"财务数据目录不存在: {financials_dir}")
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
```

- [ ] **Step 2: 验证脚本**

```bash
cd /Users/baoli/Documents/warehouse/value_investing && uv run python scripts/gen_metrics.py 600519 贵州茅台
```

检查是否输出关键指标趋势表。

---

### Task 7: README.md

**Files:**
- Create: `README.md`

- [ ] **Step 1: 创建 README.md**

```markdown
# 价值投资分析项目

以 Markdown 文件库为核心的价值投资分析项目，用巴菲特/芒格式分析框架，覆盖 A 股+港股。

## 目录结构

```
value_investing/
├── companies/           # 按企业组织
│   └── <ticker>-<名称>/
│       ├── profile.md
│       ├── deep-research.md
│       ├── tracking.md
│       ├── thinking.md
│       └── financials/
├── cross-cutting/       # 跨企业视图
├── scripts/             # Python 辅助脚本
└── templates/           # 文件模板
```

## 快速开始

### 安装

```bash
uv venv && uv sync
```

### 创建新企业

```bash
uv run python scripts/new_company.py
```

### 拉取财务数据

```bash
uv run python scripts/fetch_financials.py <代码> <名称> --year 2025 --quarter 4
```

### 计算指标

```bash
uv run python scripts/gen_metrics.py <代码> <名称>
```

## 工作流

1. `new_company.py` → 创建企业目录和模板
2. 填写 `profile.md`（商业模式、护城河、管理层）
3. `fetch_financials.py` → 拉取财务数据
4. `gen_metrics.py` → 计算趋势指标
5. 撰写 `deep-research.md` 深度研报
6. `tracking.md` 持续跟踪 + `thinking.md` 思考记录
```
