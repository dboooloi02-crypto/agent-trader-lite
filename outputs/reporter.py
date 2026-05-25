"""
可读报告生成器 — 把结构化数据转成人类可读文本。
"""

from datetime import datetime

from core.registry import Outputter, register


def _now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Reporter(Outputter):
    """生成可读报告"""

    @property
    def name(self):
        return "reporter"

    def output(self, raw: dict, config: dict) -> str:
        lines = []
        lines.append("=" * 50)
        lines.append(f"  Agent Trader Lite · 数据报告")
        lines.append(f"  {_now_str()}")
        lines.append("=" * 50)
        lines.append("")

        # === 行情 ===
        quotes = raw.get("tencent", {}).get("quotes", {})
        if quotes:
            lines.append("── 实时行情 ──")
            for code, q in quotes.items():
                if "error" in q:
                    lines.append(f"  {code}: {q['error']}")
                    continue
                name = q.get("name", code)
                price = q.get("price", 0)
                chg = q.get("change_pct", 0)
                flag = "📈" if chg > 0 else ("📉" if chg < 0 else "➖")
                lines.append(f"  {flag} {name} ({code}): {price}  ({chg:+.2f}%)")
            lines.append("")

        # === 热点板块 ===
        hot = raw.get("eastmoney_hot", {})
        sectors = hot.get("sectors", [])
        if sectors:
            lines.append("── 热门板块 Top 10 ──")
            for i, s in enumerate(sectors, 1):
                bar = "█" * int(s.get("hot", 0))
                lines.append(f"  {i:2d}. {s.get('name', ''):<12s} {s.get('hot', 0):>5.1f} {bar}")
            lines.append("")

        # === 基金净值 ===
        funds = raw.get("fund_nav", {}).get("funds", {})
        if funds:
            lines.append("── 基金净值 ──")
            for code, f in funds.items():
                if "error" in f:
                    lines.append(f"  {code}: {f['error']}")
                    continue
                name = f.get("name", code)
                nav = f.get("nav", 0)
                date = f.get("nav_date", "")
                est = f.get("estimate", 0)
                est_pct = f.get("estimate_pct", 0)
                lines.append(f"  {name} ({code})")
                lines.append(f"    净值: {nav} ({date})")
                if est:
                    flag = "📈" if est_pct > 0 else ("📉" if est_pct < 0 else "➖")
                    lines.append(f"    估算: {est}  {flag} {est_pct:+.2f}%")
            lines.append("")

        # === 错误摘要 ===
        errors = []
        for src_name, src_data in raw.items():
            if isinstance(src_data, dict) and "error" in src_data:
                errors.append(f"  {src_name}: {src_data['error']}")
        if errors:
            lines.append("── 异常 ──")
            lines.extend(errors)
            lines.append("")

        lines.append("=" * 50)
        return "\n".join(lines)


register("outputter", "reporter", Reporter())
