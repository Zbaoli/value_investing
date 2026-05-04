# 价值投资分析项目 — 设计方案

## 项目定位

以 Markdown 文件库为核心的价值投资分析项目。用巴菲特/芒格式分析框架，覆盖 A 股+港股，深度研报打底 + 持续跟踪 + 思考链贯穿。Python 脚本辅助数据获取和指标计算。

## 目录结构

```
value_investing/
├── companies/
│   └── <ticker>-<short-name>/     # 例: 600519-贵州茅台, 0700-腾讯控股
│       ├── profile.md              # 企业档案（商业模式、护城河、管理层评估）
│       ├── financials/             # 财务数据，每季度一个文件
│       │   └── YYYY-Qn.md          # 例: 2026-Q1.md
│       ├── deep-research.md        # 深度研报（持续修订）
│       ├── tracking.md             # 跟踪日志（倒序，最新在前）
│       └── thinking.md             # 思考碎片（日期标记，类似日志流）
├── cross-cutting/
│   ├── watchlist.md                # 观察列表，核心企业估值对比
│   ├── allocation.md               # 持仓记录与组合管理
│   └── themes.md                   # 跨企业主题研究
├── scripts/
│   ├── fetch_financials.py         # akshare 拉取三张表数据
│   ├── gen_metrics.py              # 计算 ROE/FCF/毛利率/净利率等
│   └── new_company.py              # 交互式创建新企业目录和模板文件
├── templates/
│   ├── profile.tmpl.md
│   ├── deep-research.tmpl.md
│   ├── financials.tmpl.md
│   └── tracking.tmpl.md
├── pyproject.toml
├── .env
├── .gitignore
└── README.md
```

## 文件约定

- 企业目录命名：`<ticker>-<拼音简称>`，如 `600519-贵州茅台`、`0700-腾讯控股`
- 财务数据文件：`YYYY-Qn.md`，按会计季度
- 日期标记统一用 ISO 格式 `YYYY-MM-DD`
- tracking.md：倒序追加，`## YYYY-MM-DD - <事件标题>`
- thinking.md：`### YYYY-MM-DD` 下碎片记录，可附标签如 `#估值` `#护城河` `#风险`
- 文件间引用用 Obsidian `[[wikilink]]` 语法，兼容 Obsidian 打开

## 核心模板

### 企业档案 (profile.tmpl.md)

- 一句话描述、商业模式、护城河、行业地位
- 管理层评估、增长驱动、关键风险

### 深度研报 (deep-research.tmpl.md)

- 投资 Thesis（3 句话）
- 护城河深度分析（定量+定性，ROIC 趋势佐证）
- 财务分析（5-10 年关键指标趋势）
- 估值（保守/合理假设，安全边际判断）
- 风险与反驳（看空观点认真思考）
- 结论与行动计划（买入区间、仓位上限）

### 财务数据 (financials.tmpl.md)

- 利润表、资产负债表、现金流量表
- 关键比率：ROE、ROIC、毛利率、净利率、FCF Yield、有息负债率

## Python 脚本

### 技术栈

- 数据源：`akshare`（免费，A 股+港股覆盖好）
- 数据处理：`pandas`
- 配置：`python-dotenv` + `.env`
- 日志：`loguru`
- 包管理：`uv`，镜像 `https://pypi.tuna.tsinghua.edu.cn/simple`

### 脚本清单

- **new_company.py** — 交互式脚手架，输入 ticker+企业名，创建目录和模板文件
- **fetch_financials.py** — 拉取三张表数据，输出到 `companies/<ticker>/financials/`
- **gen_metrics.py** — 从 financials 读取数据计算关键指标，生成趋势表

### 明确不做

- 不自动生成分析结论（判断留给用户）
- 不做实时行情推送
- 不做数据库存储
- 无定时任务/自动化 pipeline

## 工作流

```
发现标的 → new_company.py 脚手架 → 填写 profile.md
                                      ↓
fetch_financials.py 拉5年数据 ──→ 填写 financials/
                                      ↓
gen_metrics.py 计算趋势 ─────────→ 撰写 deep-research.md
                                      ↓
                               tracking.md 持续跟踪
                               thinking.md 随时记录
                                      ↓
                          cross-cutting/ 定期回顾对比
```

## 环境与依赖

**.gitignore**：`.env`、`__pycache__/`、`.venv/`、`uv.lock`（可选）

**`pyproject.toml`** 依赖：
- `akshare`
- `pandas`
- `python-dotenv`
- `loguru`
