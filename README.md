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

1. `new_company.py` — 创建企业目录和模板
2. 填写 `profile.md`（商业模式、护城河、管理层）
3. `fetch_financials.py` — 拉取财务数据
4. `gen_metrics.py` — 计算趋势指标
5. 撰写 `deep-research.md` 深度研报
6. `tracking.md` 持续跟踪 + `thinking.md` 思考记录
