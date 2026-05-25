"""
JSON 文件输出器
"""

import json
from pathlib import Path
from core.registry import Outputter, register


class JSONWriter(Outputter):
    """将数据写入 JSON 文件"""

    @property
    def name(self):
        return "json_writer"

    def output(self, data: dict, config: dict) -> str:
        path = Path(config.get("path", "output.json"))
        indent = config.get("indent", 2)
        ensure_ascii = config.get("ensure_ascii", False)

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)

        return f"✓ 已写入 {path.resolve()} ({path.stat().st_size} 字节)"


register("outputter", "json_writer", JSONWriter())
