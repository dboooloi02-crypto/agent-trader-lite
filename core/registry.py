"""
Plugin registry — 数据源 / 分析器 / 输出器的注册与发现机制。
允许第三方模块通过一行注册接入管线。
"""

_plugins: dict[str, dict] = {
    "datasource": {},
    "analyzer": {},
    "outputter": {},
}


def register(kind: str, name: str, instance):
    """注册一个插件。

    Args:
        kind: 'datasource' | 'analyzer' | 'outputter'
        name: 唯一名称（如 'tencent', 'sentiment'）
        instance: 实现了对应接口的对象或函数
    """
    store = _plugins.get(kind)
    if store is None:
        raise ValueError(f"未知插件类型: {kind}，可选: datasource, analyzer, outputter")
    store[name] = instance


def get(kind: str, name: str):
    """获取已注册的插件实例"""
    store = _plugins.get(kind, {})
    inst = store.get(name)
    if inst is None:
        raise KeyError(f"插件 '{name}' 未注册（类型: {kind}）")
    return inst


def list_plugins(kind: str | None = None) -> dict:
    """列出全部 / 某类插件"""
    if kind:
        return {kind: dict(_plugins.get(kind, {}))}
    return {k: dict(v) for k, v in _plugins.items()}


class Datasource:
    """数据源基类 —— 所有 datasource 应继承此类"""

    def fetch(self, config: dict) -> dict:
        """执行数据抓取，返回结构化 dict"""
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.__class__.__name__


class Analyzer:
    """分析器基类"""

    def analyze(self, data: dict, config: dict) -> dict:
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.__class__.__name__


class Outputter:
    """输出器基类"""

    def output(self, data: dict, config: dict) -> str:
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.__class__.__name__
