# Agent Trader Lite

**一个轻量级的数据 Agent 管线框架。**  
定时采集实时行情 → 热点板块 → AI 分析 → 结构化输出 + 可读报告。  
配置驱动、插件扩展、开箱即用，全部免费数据源。

> 作者：一个做 AI Agent 的独立开发者  
> 业务咨询 / 定制开发 → GitHub Issues / 私信

---

## 它能做什么

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│  定时数据采集    │ →  │  分析处理    │ →  │  多格式输出      │
│  - 股票/ETF行情  │    │  (可扩展)    │    │  - 结构化 JSON   │
│  - 热门板块      │    │              │    │  - 人类可读报告  │
│  - 基金净值      │    │              │    │  - 推送到任意端  │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

**已有数据源（全部免费，无需 API Key）：**

| 数据源 | 类型 | 数据提供商 |
|--------|------|-----------|
| 腾讯行情 | A股/ETF实时行情 | qt.gtimg.cn |
| 东方财富热门板块 | 市场热点题材 | emcfgdata.eastmoney.com |
| 天天基金净值 | 基金实时净值+估算 | fundgz.1234567.com.cn |

## 快速开始

```bash
# 1. 下载
git clone https://github.com/你的用户名/agent-trader-lite
cd agent-trader-lite

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行
python agent.py
```

输出：

```
════════════════════════════════════════════════════
  Agent Trader Lite · 数据报告
  2026-05-25 14:30:00
════════════════════════════════════════════════════

── 实时行情 ──
  📈 标普500ETF南方 (513650): 2.145  (+0.42%)

── 热门板块 Top 10 ──
   1. 科特估         10.0 ██████████
   2. 国产芯片        9.9 ██████████
   ...

── 基金净值 ──
  易方达全球成长精选 (012920)
    净值: 3.8156 (2026-05-24)
    估算: 3.8201  📈 +0.12%
```

## 定时运行

配合 cron：

```bash
# 每天 15:00 跑（盘后）
0 15 * * 1-5 cd /path/to/agent-trader-lite && python agent.py

# 每天 09:30 跑（开盘）
30 9 * * 1-5 cd /path/to/agent-trader-lite && python agent.py
```

配 Hermes Agent / 微信推送 / 飞书机器人 / Telegram Bot：

```bash
python agent.py 2>&1 | curl -X POST -d @- https://your-webhook/...
```

## 配置

编辑 `config.yaml`：

```yaml
datasources:
  chain:
    - tencent
    - eastmoney_hot
  sources:
    tencent:
      codes:
        - "sh513650"      # A股/ETF代码
        - "sz300059"      # sh=上海, sz=深圳
    eastmoney_hot:
      limit: 10            # 取前 N 个热门板块
    fund_nav:
      codes:
        - "012920"         # 基金代码
outputters:
  - reporter
  - json_writer
```

## 扩展

写一个新的数据源，注册即可：

```python
from core.registry import Datasource, register

class MyDataSource(Datasource):
    @property
    def name(self):
        return "my_source"

    def fetch(self, config: dict) -> dict:
        # 你的抓取逻辑
        return {"my_data": [...]}

register("datasource", "my_source", MyDataSource())
```

然后改 `config.yaml` 的 `chain` 加入 `my_source` 即可。

## 技术栈

- Python 3.10+
- 数据采集：requests / curl_cffi（TLS 指纹模拟）
- 配置：PyYAML
- 无外部依赖的 AI 分析层（可接任何 LLM / 本地模型）

## 许可

MIT

## 联系

GitHub Issues → 提问 / 需求 / Bug 报告  
如果这个项目帮到了你，star ⭐ 就是最好的支持。
