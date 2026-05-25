"""
东方财富热门题材数据源
API: emcfgdata.eastmoney.com/api/themeInvest/getHotBD

使用 curl_cffi 模拟 Chrome TLS 指纹绕过反爬。
"""

import time
from core.registry import Datasource, register

try:
    from curl_cffi import requests as curl_requests
except ImportError:
    curl_requests = None  # type: ignore


class EastMoneyHotSectors(Datasource):
    """东方财富热门板块/题材"""

    @property
    def name(self):
        return "eastmoney_hot"

    def fetch(self, config: dict) -> dict:
        if curl_requests is None:
            return {"error": "缺少依赖: curl_cffi"}

        limit = config.get("limit", 10)
        try:
            session = curl_requests.Session()
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"
                ),
                "Origin": "https://vipmoney.eastmoney.com",
                "Referer": "https://vipmoney.eastmoney.com/",
                "Content-Type": "application/json",
            }
            payload = {
                "args": {"bdType": 1},
                "client": "android",
                "randomCode": str(int(time.time() * 1000)) + "et375d8f",
                "timestamp": int(time.time() * 1000),
                "clientType": "cfw",
                "clientVersion": "null",
            }
            resp = session.post(
                "https://emcfgdata.eastmoney.com/api/themeInvest/getHotBD",
                json=payload,
                headers=headers,
                timeout=10,
                impersonate="chrome120",
            )
            data = resp.json()
            items = data.get("data", [])
            scores = [i.get("hotRankScore", 0) for i in items]
            max_score = max(scores) if scores else 1
            sectors = [
                {
                    "name": i.get("themeName", ""),
                    "hot": round(i.get("hotRankScore", 0) / max_score * 10, 2),
                }
                for i in items[:limit]
            ]
            return {"sectors": sectors, "source": "eastmoney", "count": len(sectors)}
        except Exception as e:
            return {"error": str(e)}


register("datasource", "eastmoney_hot", EastMoneyHotSectors())
