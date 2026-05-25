#!/usr/bin/env python3
"""
示例：每日盘后报告
配合 cron 定时运行：
  0 15 * * 1-5 cd /path/to/agent-trader-lite && python examples/daily_report.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
import datasources.tencent    # noqa: F401
import datasources.eastmoney  # noqa: F401
import datasources.fund       # noqa: F401
import outputs.reporter       # noqa: F401
import outputs.json_writer    # noqa: F401
from core.pipeline import Pipeline

# 日常配置
DEFAULT_CONFIG = {
    "datasources": {
        "chain": ["tencent", "eastmoney_hot"],
        "sources": {
            "tencent": {"codes": ["sh513650", "sz159915"]},
            "eastmoney_hot": {"limit": 5},
        },
    },
    "outputters": ["reporter", "json_writer"],
    "json_writer": {"path": "outputs/daily_report.json"},
}

if __name__ == "__main__":
    pipe = Pipeline(DEFAULT_CONFIG)
    result = pipe.run()

    report = result.get("outputs", {}).get("reporter", "")
    print(report)
