# Agent Trader Lite

**一个会自己盯盘的 AI Agent。**  
自动采集 A股行情、热门板块、基金净值，生成可读报告。  
配置驱动、插件扩展、全部免费数据源。

> 不用打开多个炒股软件，一行命令出报告。  
> 适合自己盯盘、数据分析、自动化投研。

---

## Demo

![demo](https://raw.githubusercontent.com/dboooloi02-crypto/agent-trader-lite/main/docs/demo.gif)
*↑ 终端运行 python agent.py，自动抓取数据并输出报告*

---

## 它能帮你做什么

| 你以前 | 现在 |
|--------|------|
| 打开同花顺/天天基金/东财三个软件看行情 | 一行命令全部拉完 |
| 手动记基金净值 | 自动出净值 + 盘中估算 |
| 刷财经新闻找热点板块 | 自动拉 Top10 热门题材 |
| 自己算涨跌幅 | 报告直接给你算好 |

**已有数据源（全部免费，无需 API Key）：**

| 数据源 | 类型 | 提供商 |
|--------|------|--------|
| 腾讯行情 | A股/ETF 实时行情 | qt.gtimg.cn |
| 东方财富热门板块 | 市场热点题材 | emcfgdata.eastmoney.com |
| 天天基金净值 | 基金实时净值+估算 | fundgz.1234567.com.cn |

---

## 快速开始（3步）

```bash
git clone https://github.com/dboooloi02-crypto/agent-trader-lite
cd agent-trader-lite
pip install -r requirements.txt
python agent.py
```

**输出效果：**

```
════════════════════════════════════════════════════
  Agent Trader Lite · 数据报告
════════════════════════════════════════════════════

── 实时行情 ──
  📈 标普500ETF南方 (513650): 1.906  (+2.69%)
  📈 创业板ETF易方达 (159915): 4.034  (+2.23%)

── 热门板块 Top 10 ──
   1. 科特估         10.0 ██████████
   2. 国产芯片        9.4 █████████
   3. 国家大基金持股  9.2 █████████
   ...

── 基金净值 ──
  易方达全球成长精选 (012920)
    净值: 4.0475 (2026-05-21)
    估算: 4.0584  📈 +0.27%
```

---

## 架构

```
数据源层                   分析层              输出层
┌──────────────┐        ┌──────────┐      ┌──────────────┐
│ 腾讯行情      │        │          │      │ JSON 文件    │
│ 东财热点板块  │ ───→   │ 插件化   │ ──→  │ 可读报告     │
│ 天天基金净值  │        │ 可扩展   │      │ 推送到任意端 │
└──────────────┘        └──────────┘      └──────────────┘
```

所有数据源通过插件注册机制接入，新增一个数据源只需写一个类 + 一行注册。

---

## 定时运行

配合 cron 每天自动跑：

```bash
# 每天 15:00 盘后
0 15 * * 1-5 cd /path/to/agent-trader-lite && python agent.py

# 每天 09:30 开盘
30 9 * * 1-5 cd /path/to/agent-trader-lite && python agent.py
```

配合微信/飞书/Telegram 推送：

```bash
python agent.py 2>&1 | curl -X POST -d @- https://your-webhook/...
```

---

## 配置

编辑 `config.yaml`，改你想盯的股票代码即可：

```yaml
datasources:
  chain:
    - tencent
    - eastmoney_hot
    - fund_nav
  sources:
    tencent:
      codes:
        - "sh513650"      # 代码前加 sh/sz
        - "sz159915"
    eastmoney_hot:
      limit: 10
    fund_nav:
      codes:
        - "012920"
```

---

## 扩展

想接入自己的数据源？写一个类注册即可：

```python
from core.registry import Datasource, register

class MySource(Datasource):
    def fetch(self, config):
        return {"my_data": [...]}

register("datasource", "my_source", MySource())
```

然后在 config.yaml 的 chain 里加上 `my_source`。

---

## 技术栈

- Python 3.10+
- 数据采集：requests / curl_cffi（TLS 指纹模拟绕过反爬）
- 配置：PyYAML
- 可接任何大模型做 AI 分析

---

## 许可

MIT

## 联系

GitHub Issues → 提问 / 需求  
业务咨询 / 定制开发 → Issues 私信
