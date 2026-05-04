"""交互式创建新企业目录和模板文件。"""

import os
import re
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
    # Fix 1: 路径穿越防护 — 校验输入
    if not re.fullmatch(r"^[A-Za-z0-9]{1,10}$", ticker):
        raise ValueError(f"股票代码格式无效（仅允许 1-10 位字母数字）: {ticker}")
    if "/" in name or "\\" in name or ".." in name:
        raise ValueError(f"企业名称包含非法字符（/, \\, ..）: {name}")

    dir_name = f"{ticker}-{name}"
    company_dir = os.path.join(PROJECT_ROOT, COMPANIES_DIR, dir_name)
    financials_dir = os.path.join(company_dir, "financials")
    templates_dir = os.path.join(PROJECT_ROOT, TEMPLATES_DIR)

    # Fix 1: 路径穿越防护 — 确认目标在 COMPANIES_DIR 下
    allowed_root = os.path.realpath(os.path.join(PROJECT_ROOT, COMPANIES_DIR))
    if not os.path.realpath(company_dir).startswith(allowed_root):
        raise ValueError(f"目标目录不在允许的范围内: {company_dir}")

    if os.path.exists(company_dir):
        raise FileExistsError(f"企业目录已存在: {company_dir}")

    os.makedirs(financials_dir)
    logger.info(f"创建财务数据目录（由 fetch_financials.py 填充）: {financials_dir}")

    today = date.today().isoformat()
    vars_map = {
        "COMPANY_NAME": name,
        "TICKER": ticker,
        "DATE": today,
        "PERIOD": "YYYY-Qn",
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

    # 思考链文件不从模板生成，直接创建
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
    try:
        create_company(ticker, name)
    except (FileExistsError, ValueError) as e:
        logger.error(e)
        sys.exit(1)
