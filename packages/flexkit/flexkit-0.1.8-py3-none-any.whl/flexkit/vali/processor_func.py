import pathlib
from datetime import datetime

from ..tools import Result

from typing import Any, Callable


class Processor:
    """处理器类（返回Result.ok( 转换后的值)）"""

    @staticmethod
    def trim() -> Callable[[Any], Result]:
        """去除首尾空格"""

        def wrapper(value: Any) -> Result:
            if not isinstance(value, str):
                return Result.err(TypeError(" 不是字符串"))
            else:
                return Result.ok(value.strip())

        return wrapper

    @staticmethod
    def replace(old: str, new: str) -> Callable[[Any], Result]:
        """替换"""

        def wrapper(value: Any) -> Result:
            if not isinstance(value, str):
                return Result.err(TypeError(" 不是字符串"))
            else:
                return Result.ok(value.replace(old, new))

        return wrapper

    @staticmethod
    def re_prefix(prefix: str) -> Callable[[Any], Result]:
        """移除前缀"""

        def wrapper(value: Any) -> Result:
            if not isinstance(value, str):
                return Result.err(TypeError(" 不是字符串"))
            elif not value.startswith(prefix):
                return Result.err(ValueError(f" 不以{prefix}开头"))
            else:
                return Result.ok(value[len(prefix) :])

        return wrapper

    @staticmethod
    def re_suffix(suffix: str) -> Callable[[Any], Result]:
        """移除后缀"""

        def wrapper(value: Any) -> Result:
            if not isinstance(value, str):
                return Result.err(TypeError(" 不是字符串"))
            elif not value.endswith(suffix):
                return Result.err(ValueError(f" 不以{suffix}结尾"))
            else:
                return Result.ok(value[: -len(suffix)])

        return wrapper

    @staticmethod
    def split(sep: str) -> Callable[[Any], Result]:
        """分割"""

        def wrapper(value: Any) -> Result:
            if not isinstance(value, str):
                return Result.err(TypeError(" 不是字符串"))
            else:
                return Result.ok(value.split(sep))

        return wrapper

    @staticmethod
    def to_upper() -> Callable[[Any], Result]:
        """将值转换为大写"""

        def wrapper(value: Any) -> Result:
            if not isinstance(value, str):
                return Result.err(TypeError(" 不是字符串"))
            else:
                return Result.ok(value.upper())

        return wrapper

    @staticmethod
    def to_lower() -> Callable[[Any], Result]:
        """将值转换为小写"""

        def wrapper(value: Any) -> Result:
            if not isinstance(value, str):
                return Result.err(TypeError(" 不是字符串"))
            else:
                return Result.ok(value.lower())

        return wrapper

    @staticmethod
    def to_title() -> Callable[[Any], Result]:
        """将值转换为标题大小写"""

        def wrapper(value: Any) -> Result:
            if not isinstance(value, str):
                return Result.err(TypeError(" 不是字符串"))
            else:
                return Result.ok(value.title())

        return wrapper

    @staticmethod
    def to_capitalize() -> Callable[[Any], Result]:
        """将值转换为首字母大写"""

        def wrapper(value: Any) -> Result:
            if not isinstance(value, str):
                return Result.err(TypeError(" 不是字符串"))
            else:
                return Result.ok(value.capitalize())

        return wrapper

    @staticmethod
    def to_string() -> Callable[[Any], Result]:
        """将值转换为字符串"""

        def wrapper(value: Any) -> Result:
            try:
                return Result.ok(str(value))
            except Exception as e:
                return Result.err(ValueError(f" 无法转换为字符串: {e}"))

        return wrapper

    @staticmethod
    def to_int() -> Callable[[Any], Result]:
        """将值转换为整数"""

        def wrapper(value: Any) -> Result:
            try:
                return Result.ok(int(value))
            except ValueError as e:
                return Result.err(ValueError(f" 无法转换为整数: {e}"))

        return wrapper

    @staticmethod
    def to_float() -> Callable[[Any], Result]:
        """将值转换为浮点数"""

        def wrapper(value: Any) -> Result:
            try:
                return Result.ok(float(value))
            except ValueError as e:
                return Result.err(ValueError(f" 无法转换为浮点数: {e}"))

        return wrapper

    @staticmethod
    def to_bool() -> Callable[[Any], Result]:
        """将值转换为布尔值"""

        def wrapper(value: Any) -> Result:
            try:
                return Result.ok(bool(value))
            except ValueError as e:
                return Result.err(ValueError(f" 无法转换为布尔值: {e}"))

        return wrapper

    @staticmethod
    def to_list() -> Callable[[Any], Result]:
        """将值转换为列表"""

        def wrapper(value: Any) -> Result:
            try:
                return Result.ok([value])
            except ValueError as e:
                return Result.err(ValueError(f" 无法转换为列表: {e}"))

        return wrapper

    @staticmethod
    def to_tuple() -> Callable[[Any], Result]:
        """将值转换为元组"""

        def wrapper(value: Any) -> Result:
            try:
                return Result.ok((value,))
            except ValueError as e:
                return Result.err(ValueError(f" 无法转换为元组: {e}"))

        return wrapper

    @staticmethod
    def to_set() -> Callable[[Any], Result]:
        """将值转换为集合"""

        def wrapper(value: Any) -> Result:
            try:
                return Result.ok({value})
            except ValueError as e:
                return Result.err(ValueError(f" 无法转换为集合: {e}"))

        return wrapper

    @staticmethod
    def to_dict() -> Callable[[Any], Result]:
        """将值转换为字典"""

        def wrapper(value: Any) -> Result:
            try:
                return Result.ok({"key": value})
            except ValueError as e:
                return Result.err(ValueError(f" 无法转换为字典: {e}"))

        return wrapper

    @staticmethod
    def to_json() -> Callable[[Any], Result]:
        """将值转换为JSON"""

        def wrapper(value: Any) -> Result:
            try:
                import json

                return Result.ok(json.dumps(value))
            except ValueError as e:
                return Result.err(ValueError(f" 无法转换为JSON: {e}"))

        return wrapper

    @staticmethod
    def path_absolute() -> Callable[[pathlib.Path], Result]:
        """获取绝对路径"""

        def wrapper(value: pathlib.Path) -> Result:
            try:
                return Result.ok(value.absolute())
            except ValueError as e:
                return Result.err(ValueError(f" 无法获取绝对路径: {e}"))

        return wrapper

    @staticmethod
    def to_path() -> Callable[[Any], Result]:
        """将值转换为路径"""

        def wrapper(value: Any) -> Result:
            try:
                return Result.ok(pathlib.Path(value))
            except ValueError as e:
                return Result.err(ValueError(f" 无法转换为路径: {e}"))

        return wrapper

    @staticmethod
    def to_datetime() -> Callable[[Any], Result]:
        """将值转换为日期时间"""

        def wrapper(value: Any) -> Result:
            try:
                if value:
                    return Result.ok(datetime.now())
                return Result.ok(datetime.fromisoformat(value))
            except ValueError as e:
                return Result.err(ValueError(f"无法转换为日期时间: {e}"))

        return wrapper
