#!/usr/bin/env python3
"""
Agent Trader Lite — 主入口

用法:
  python agent.py                     # 单次运行，打印报告
  python agent.py --config my.yaml   # 使用自定义配置
  python agent.py --json-only        # 只输出 JSON，不打印报告

定时运行 (配合 cron/systemd):
  0 9 * * 1-5 cd /path/to/agent-trader-lite && python agent.py
"""

import argparse
import logging
import sys
import os

# 确保包目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml

# 导入数据源 / 输出器（触发自动注册）
import datasources.tencent        # noqa: F401
import datasources.eastmoney      # noqa: F401
import datasources.fund           # noqa: F401
import outputs.json_writer        # noqa: F401
import outputs.reporter           # noqa: F401

from core.pipeline import Pipeline


def main():
    parser = argparse.ArgumentParser(description="Agent Trader Lite")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("--json-only", action="store_true", help="仅输出 JSON")
    parser.add_argument("--verbose", action="store_true", help="详细日志")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
    )

    # 加载配置
    config_path = args.config
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 运行管线
    pipeline = Pipeline(config)
    result = pipeline.run()

    # 处理输出
    outputs = result.get("outputs", {})

    if args.json_only:
        # 只写 JSON，不打印报告
        if "json_writer" in outputs:
            print(outputs["json_writer"])
        return

    # 打印报告到终端
    report = outputs.get("reporter", "")
    if report:
        print("\n" + report)

    # 确保 JSON 文件也生成了
    if "json_writer" in outputs:
        print(f"\n  📄 {outputs['json_writer']}")


if __name__ == "__main__":
    main()
