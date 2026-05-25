"""
天天基金净值数据源 (免费)
API: fundgz.1234567.com.cn/js/{code}.js

返回基金最新净值 + 盘中估算。
"""

import json
import re
from core.registry import Datasource, register

try:
    import requests
except ImportError:
    requests = None  # type: ignore


def _safe_float(v) -> float:
    try:
        return round(float(v), 4)
    except (ValueError, TypeError):
        return 0.0


class FundNAV(Datasource):
    """基金净值查询"""

    @property
    def name(self):
        return "fund_nav"

    def fetch(self, config: dict) -> dict:
        if requests is None:
            return {"error": "缺少依赖: requests"}

        codes = config.get("codes", [])
        if not codes:
            return {"error": "未指定 codes"}

        results = {}
        for code in codes:
            url = f"https://fundgz.1234567.com.cn/js/{code}.js"
            try:
                resp = requests.get(url, timeout=15)
                match = re.search(r"jsonpgz\((.+)\)", resp.text)
                if not match:
                    results[code] = {"error": "解析失败"}
                    continue
                data = json.loads(match.group(1))
                results[code] = {
                    "name": data.get("name", ""),
                    "code": code,
                    "nav": _safe_float(data.get("dwjz")),
                    "nav_date": data.get("jzrq", ""),
                    "estimate": _safe_float(data.get("gsz")),
                    "estimate_pct": _safe_float(data.get("gszzl")),
                    "estimate_time": data.get("gztime", ""),
                }
            except Exception as e:
                results[code] = {"error": str(e)}

        return {"funds": results, "source": "fund_nav"}


register("datasource", "fund_nav", FundNAV())
