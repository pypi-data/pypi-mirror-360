import re
import pathlib
from datetime import datetime
from ..tools import Result
from typing import Any, Callable, List, Type, Union, Pattern, TypeVar

Num = TypeVar("E", bound=Union[int, float])


class Validator:
    """验证器类（返回Result.ok(True) 表示验证通过）"""

    @staticmethod
    def is_subclass(parent_class: Type) -> Callable[[Any], Result]:
        """验证是否为指定父类的子类"""

        def wrapper(value: Any) -> Result:
            if not issubclass(value, parent_class):
                return Result.err(ValueError(f"{value}不是{parent_class}的子类"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def not_null() -> Callable[[Any], Result]:
        """验证值不为None"""

        def wrapper(value: Any) -> Result:
            if value is None:
                return Result.err(ValueError("值为空"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def not_empty() -> Callable[[Any], Result]:
        """验证值不为空"""

        def wrapper(value: Any) -> Result:
            if value:
                return Result.err(ValueError("值为空"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def in_list(valid_list: List[Any]) -> Callable[[Any], Result]:
        """验证值在指定列表中"""

        def wrapper(value: Any) -> Result:
            if value not in valid_list:
                return Result.err(ValueError(f"值不在允许的列表{valid_list}中"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def max_length(length: int) -> Callable[[str], Result]:
        """验证可迭代对象的长度不超过最大值"""

        def wrapper(value: str) -> Result:
            if len(value) > length:
                return Result.err(ValueError(f"长度超过最大值{length}"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def min_length(length: int) -> Callable[[str], Result]:
        """验证可迭代对象的长度不小于最小值"""

        def wrapper(value: str) -> Result:
            if len(value) < length:
                return Result.err(ValueError(f"长度小于最小值{length}"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def max(max_val: Num) -> Callable[[Num], Result]:
        """验证值不大于最大值（适用于数值/可比较对象）"""

        def wrapper(value: Num) -> Result:
            if value > max_val:
                return Result.err(ValueError(f"值超过最大值{max_val}"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def min(min_val: Num) -> Callable[[Num], Result]:
        """验证值不小于最小值（适用于数值/可比较对象）"""

        def wrapper(value: Num) -> Result:
            if value < min_val:
                return Result.err(ValueError(f"值小于最小值{min_val}"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def eq(
        expected: Union[int, float, str],
    ) -> Callable[[Union[int, float, str]], Result]:
        """验证值等于预期值"""

        def wrapper(value: Union[int, float, str]) -> Result:
            if value != expected:
                return Result.err(ValueError(f"值不等于{expected}"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def neq(
        unexpected: Union[int, float, str],
    ) -> Callable[[Union[int, float, str]], Result]:
        """验证值不等于指定值"""

        def wrapper(value: Union[int, float, str]) -> Result:
            if value == unexpected:
                return Result.err(ValueError(f"值等于{unexpected}"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def gt(min_val: Num) -> Callable[[Num], Result]:
        """验证值大于指定值（严格大于）"""

        def wrapper(value: Num) -> Result:
            if value <= min_val:
                return Result.err(ValueError(f"值不大于{min_val}"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def lt(max_val: Num) -> Callable[[Num], Result]:
        """验证值小于指定值（严格小于）"""

        def wrapper(value: Num) -> Result:
            if value >= max_val:
                return Result.err(ValueError(f"值不小于{max_val}"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def ge(min_val: Num) -> Callable[[Num], Result]:
        """验证值大于或等于指定值"""

        def wrapper(value: Num) -> Result:
            if value < min_val:
                return Result.err(ValueError(f"值小于{min_val}"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def le(max_val: Num) -> Callable[[Num], Result]:
        """验证值小于或等于指定值"""

        def wrapper(value: Num) -> Result:
            if value > max_val:
                return Result.err(ValueError(f"值大于{max_val}"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def regex(
        pattern: Union[str, Pattern], flags: int = 0, msg: str = ""
    ) -> Callable[[str], Result]:
        """
        验证字符串是否匹配正则表达式
        参数：
            pattern: 正则表达式字符串或已编译的Pattern对象
            flags: 正则标志（如re.IGNORECASE）
        返回：
            Result.ok(True)  或 Result.err(ValueError)
        """

        def wrapper(value: str) -> Result:
            try:
                if isinstance(pattern, Pattern):
                    compiled = pattern
                else:
                    compiled = re.compile(pattern, flags)

                if not compiled.search(value):
                    return (
                        Result.err(ValueError(f"字符串不匹配正则表达式: {pattern}"))
                        if msg == ""
                        else Result.err(ValueError(msg))
                    )
                return Result.ok(True)
            except re.error as e:
                return Result.err(ValueError(f"无效的正则表达式: {e}"))

        return wrapper

    @staticmethod
    def starts_with(prefix: str) -> Callable[[str], Result]:
        """验证字符串以特定前缀开头"""

        def wrapper(value: str) -> Result:
            if not value.startswith(prefix):
                return Result.err(ValueError(f"字符串不以'{prefix}'开头"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def ends_with(suffix: str) -> Callable[[str], Result]:
        """验证字符串以特定后缀结尾"""

        def wrapper(value: str) -> Result:
            if not value.endswith(suffix):
                return Result.err(ValueError(f"字符串不以'{suffix}'结尾"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def contains(substring: str) -> Callable[[str], Result]:
        """验证字符串包含特定子字符串"""

        def wrapper(value: str) -> Result:
            if substring not in value:
                return Result.err(ValueError(f"字符串不包含'{substring}'"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def not_contains(substring: str) -> Callable[[str], Result]:
        """验证字符串不包含特定子字符串"""

        def wrapper(value: str) -> Result:
            if substring in value:
                return Result.err(ValueError(f"字符串包含'{substring}'"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def path_exists() -> Callable[[pathlib.Path], Result]:
        """验证路径存在"""

        def wrapper(path: pathlib.Path) -> Result:
            if not path.is_file():
                return Result.err(FileNotFoundError(f"文件不存在: {path}"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def path_not_exists() -> Callable[[pathlib.Path], Result]:
        """验证路径不存在"""

        def wrapper(path: pathlib.Path) -> Result:
            if path.is_file():
                return Result.err(FileExistsError(f"文件已存在: {path}"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def path_is_dir() -> Callable[[pathlib.Path], Result]:
        """验证路径是目录"""

        def wrapper(path: pathlib.Path) -> Result:
            if not path.is_dir():
                return Result.err(NotADirectoryError(f"不是目录: {path}"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def path_is_file() -> Callable[[pathlib.Path], Result]:
        """验证路径是文件"""

        def wrapper(path: pathlib.Path) -> Result:
            if not path.is_file():
                return Result.err(IsADirectoryError(f"不是文件: {path}"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def datetime_between(
        min_datetime: datetime, max_datetime: datetime
    ) -> Callable[[datetime], Result]:
        """验证日期时间在指定的两个日期之间"""

        def wrapper(value: datetime) -> Result:
            if not (min_datetime <= value <= max_datetime):
                return Result.err(
                    ValueError(f"日期时间不在{min_datetime}和{max_datetime}之间")
                )
            return Result.ok(True)

        return wrapper

    @staticmethod
    def datetime_before(
        max_datetime: datetime,
    ) -> Callable[[datetime], Result]:
        """验证日期时间早于指定最大日期时间"""

        def wrapper(value: datetime) -> Result:
            if value >= max_datetime:
                return Result.err(ValueError(f"日期时间晚于或等于{max_datetime}"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def datetime_after(
        min_datetime: datetime,
    ) -> Callable[[datetime], Result]:
        """验证日期时间晚于指定最小日期时间"""

        def wrapper(value: datetime) -> Result:
            if value <= min_datetime:
                return Result.err(ValueError(f"日期时间早于或等于{min_datetime}"))
            return Result.ok(True)

        return wrapper

    @staticmethod
    def datetime_equal(
        expected_datetime: datetime,
    ) -> Callable[[datetime], Result]:
        """验证日期时间与指定预期日期时间相等"""

        def wrapper(value: datetime) -> Result:
            if value != expected_datetime:
                return Result.err(ValueError(f"日期时间不等于{expected_datetime}"))
            return Result.ok(True)

        return wrapper
