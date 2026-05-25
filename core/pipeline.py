"""
Pipeline — 数据管线编排器。

核心流程:
  1. 按 config 加载 datasource → 抓取数据
  2. 按 config 加载 analyzer → 分析数据
  3. 按 config 加载 outputter → 格式化输出
  4. 返回完整结果 dict + 可读报告文本

设计目标:
  - 配置驱动：改 config.yaml 即可增减数据源/分析器/输出器
  - 插件化：写一个新模块 → register 即可接入
  - 链式降级：数据源按优先级顺序尝试，失败自动切到下一个
"""

import logging
from datetime import datetime

from .registry import get, list_plugins

logger = logging.getLogger("pipeline")


def _load_instances(kind: str, names: list[str] | str) -> list:
    """按名称列表加载插件实例"""
    if isinstance(names, str):
        names = [names]
    instances = []
    for name in names:
        try:
            inst = get(kind, name)
            instances.append((name, inst))
        except KeyError:
            logger.warning("  ⚠ %s '%s' 未注册，跳过", kind, name)
    return instances


def run_step(
    step_name: str,
    instances: list[tuple[str, object]],
    method: str,
    data: dict,
    config: dict,
) -> dict:
    """运行一个管线的步骤（fetch / analyze / output）"""
    results = {}
    for name, inst in instances:
        try:
            fn = getattr(inst, method)
            result = fn(data, config) if method in ("analyze", "output") else fn(config)
            results[name] = result
            logger.info("  ✓ %s.%s 完成", name, method)
        except Exception as e:
            results[name] = {"error": str(e)}
            logger.warning("  ⚠ %s.%s 失败: %s", name, method, e)
    return results


class Pipeline:
    """一条完整的数据管线"""

    def __init__(self, config: dict):
        self.config = config
        self.log: list[str] = []

    def run(self) -> dict:
        """执行管线，返回 {result, report, meta}"""
        self.log = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info("═" * 40)
        logger.info("Pipeline 启动: %s", timestamp)
        logger.info("═" * 40)

        # 1. 加载配置
        ds_cfg = self.config.get("datasources", {})
        an_cfg = self.config.get("analyzers", [])
        out_cfg = self.config.get("outputters", [])
        chain_order = ds_cfg.get("chain", list(ds_cfg.get("sources", {}).keys()))

        # 2. 数据采集（支持链式降级）
        raw = {}
        for name in chain_order:
            sources = ds_cfg.get("sources", {})
            if name not in sources:
                continue
            params = sources[name]
            try:
                inst = get("datasource", name)
                result = inst.fetch(params)
                raw[name] = result
                logger.info("  ✓ %s 数据抓取成功", name)
            except Exception as e:
                logger.warning("  ⚠ %s 抓取失败: %s", name, e)
                raw[name] = {"error": str(e)}

        # 3. 分析
        analyzed = {}
        if an_cfg:
            an_instances = _load_instances("analyzer", an_cfg)
            analyzed = run_step("分析", an_instances, "analyze", raw, self.config)

        # 4. 输出
        outputs = {}
        if out_cfg:
            out_instances = _load_instances("outputter", out_cfg)
            outputs = run_step("输出", out_instances, "output", raw, self.config)

        return {
            "timestamp": timestamp,
            "raw": raw,
            "analyzed": analyzed,
            "outputs": outputs,
            "meta": {
                "datasource_count": len(chain_order),
                "analyzer_count": len(an_cfg),
                "outputter_count": len(out_cfg),
            },
        }
