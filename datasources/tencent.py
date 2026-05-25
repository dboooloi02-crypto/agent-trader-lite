"""
腾讯财经行情数据源 (免费，无需 API Key)
API: qt.gtimg.cn/q=sh/sz+代码

支持 A 股、ETF 实时行情。
返回格式：字段以 ~ 分隔，GBK 编码。
"""

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


def _safe_int(v) -> int:
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return 0


class TencentQuote(Datasource):
    """腾讯财经行情"""

    @property
    def name(self):
        return "tencent"

    def fetch(self, config: dict) -> dict:
        if requests is None:
            return {"error": "缺少依赖: requests"}

        codes = config.get("codes", [])
        if not codes:
            return {"error": "未指定 codes"}

        results = {}
        for code in codes:
            raw = code[-6:]
            prefix = "sh" if raw.startswith(("6", "5")) else "sz"
            url = f"https://qt.gtimg.cn/q={prefix}{raw}"
            try:
                resp = requests.get(url, timeout=10)
                resp.encoding = "gbk"
                match = re.search(r'"(.+)"', resp.text)
                if not match:
                    results[code] = {"error": "解析失败"}
                    continue
                fields = match.group(1).split("~")
                if len(fields) < 40:
                    results[code] = {"error": "字段不足"}
                    continue
                results[code] = {
                    "name": fields[1],
                    "code": code,
                    "price": _safe_float(fields[3]),
                    "prev_close": _safe_float(fields[4]),
                    "open": _safe_float(fields[5]),
                    "high": _safe_float(fields[33]),
                    "low": _safe_float(fields[34]),
                    "volume": _safe_int(fields[6]) * 100,
                    "amount": _safe_float(fields[37]) * 10000,
                    "change_pct": _safe_float(fields[32]),
                    "change_amount": _safe_float(fields[31]),
                }
            except Exception as e:
                results[code] = {"error": str(e)}

        return {"quotes": results, "source": "tencent"}


# 自动注册
register("datasource", "tencent", TencentQuote())
