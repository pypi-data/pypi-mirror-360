import inspect
from datetime import datetime, date, time
from decimal import Decimal
from uuid import UUID
from typing import Any, Set, Dict

from sthg_common_base.utils.constants import Constants


class EnhancedJSONSerializer:
    """通用对象到字符串转换器"""

    # 需要排除的模块前缀（如框架内部对象）
    EXCLUDED_MODULES = {
        'sqlalchemy.', 'starlette.', 'fastapi.',
        'requests.', 'socket.', '_io.', 'builtins.'
    }

    # 最大递归深度
    MAX_DEPTH = 2

    # 类型特殊处理白名单
    SPECIAL_HANDLERS = {
        datetime: lambda o: o.isoformat(),
        date: lambda o: o.isoformat(),
        time: lambda o: o.isoformat(),
        Decimal: lambda o: f"Decimal({str(o)})",
        UUID: lambda o: str(o),
        complex: lambda o: f"{o.real}+{o.imag}j",
        bytes: lambda o: f"b'{o.hex()}'"
    }

    @classmethod
    def register_excluded_modules(cls, *modules: str) -> None:
        """注册需要排除的模块前缀到集合

        Args:
            modules: 可变数量的字符串参数，例如 'pymysql.', 'django.'
        """
        for module in modules:
            if isinstance(module, str):
                cls.EXCLUDED_MODULES.add(module)

    @classmethod
    def json_serializer(cls, obj: Any) -> str:
        """主转换入口"""
        return cls._convert(obj, depth=0, memo=set())

    @classmethod
    def _convert(cls, obj: Any, depth: int, memo: Set[int]) -> str:
        """递归转换核心方法"""
        try:
            # 基本类型快速返回
            if obj is None:
                return "null"
            if isinstance(obj, (int, float, bool)):
                return str(obj)
            if isinstance(obj, str):
                return f'"{obj}"'  # 保留字符串边界

            # 检测循环引用
            obj_id = id(obj)
            if obj_id in memo:
                return "<Circular Reference>"
            memo.add(obj_id)

            # 深度限制
            if depth >= cls.MAX_DEPTH:
                memo.remove(obj_id)
                return "<Max Depth Reached>"

            # 特殊类型处理
            for typ, handler in cls.SPECIAL_HANDLERS.items():
                if isinstance(obj, typ):
                    return handler(obj)

            # 排除危险类型
            if cls._is_excluded(obj):
                return f"<{type(obj).__name__} excluded>"

            # 容器类型处理
            if isinstance(obj, (list, tuple, set)):
                return cls._convert_iterable(obj, depth, memo)
            if isinstance(obj, dict):
                return cls._convert_dict(obj, depth, memo)
            # 自定义对象处理
            return cls._convert_custom(obj, depth, memo)
        except Exception as ex:
            return f"<Conversion Error: {Constants.Str_Place}>"

    @classmethod
    def _convert_iterable(cls, iterable, depth: int, memo: Set[int]) -> str:
        """处理可迭代对象"""
        items = [
            cls._convert(item, depth + 1, memo)
            for item in iterable
        ]
        if isinstance(iterable, tuple):
            return f"({', '.join(items)})"
        if isinstance(iterable, set):
            return f"{{{', '.join(items)}}}"
        return f"[{', '.join(items)}]"

    @classmethod
    def _convert_dict(cls, dct: Dict, depth: int, memo: Set[int]) -> str:
        """处理字典"""
        pairs = []
        for k, v in dct.items():
            key_str = cls._convert(k, depth + 1, memo)
            val_str = cls._convert(v, depth + 1, memo)
            pairs.append(f"{key_str}: {val_str}")
        return f"{{{', '.join(pairs)}}}"

    @classmethod
    def _convert_custom(cls, obj: Any, depth: int, memo: Set[int]) -> str:
        """处理自定义对象"""
        try:
            # 尝试获取字典表示
            if hasattr(obj, '__dict__'):
                content = cls._convert(vars(obj), depth + 1, memo)
                return f"{type(obj).__name__}({content})"

            # 处理其他可调用对象
            if callable(obj):
                return f"<callable {type(obj).__name__}>"

            # 默认字符串表示
            return f'"{str(obj)}"'
        except Exception as e:
            return f"<Conversion Error: {Constants.Str_Place}>"
        finally:
            memo.discard(id(obj))

    @classmethod
    def _is_excluded(cls, obj: Any) -> bool:
        """检查是否需要排除"""
        try:
            module = inspect.getmodule(obj).__name__
            return any(module.startswith(p) for p in cls.EXCLUDED_MODULES)
        except (AttributeError, TypeError):
            return False



if __name__ == '__main__':
    EnhancedJSONSerializer.register_excluded_modules("pymysql.", "django.")
