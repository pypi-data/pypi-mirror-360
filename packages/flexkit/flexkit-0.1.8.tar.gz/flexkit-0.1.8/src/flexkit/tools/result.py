from typing import Generic, TypeVar, Optional, Dict, Union, Callable

T = TypeVar("T")  # 成功值的泛型类型
U = TypeVar("U")  # 函数返回值的泛型类型
E = TypeVar(
    "E", bound=Union[Exception, str, None]
)  # 错误类型泛类型，约束错误类型范围（Exception, str, None）


class Result(Generic[T, E]):
    """
    Result 是一个泛型类，用于表示一个操作的结果，可以是成功（Ok）或失败（Err）。
    此类模仿rustcair的Result类型。
    主要用于实现对可控错误的处理。对于非控制错误的情况，
    建议使用try-except语句进行异常处理。
    """

    __slots__ = ["value", "error"]

    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        """初始化 Result 对象"""
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        """检查是否成功（无错误）"""
        return self.error is None

    def is_err(self) -> bool:
        """检查是否失败（有错误）"""
        return self.error is not None

    def unwrap(self) -> T | None:
        """返回成功值，若失败则抛出异常（仿 Rust 的 panic）"""
        if self.is_err():
            raise (
                self.error
                if isinstance(self.error, Exception)
                else ValueError(self.error)
            )
        return self.value

    def unwrap_or(self, default: T) -> T | None:
        """返回成功值，若失败则返回默认值"""
        return self.value if self.is_ok() else default

    def expect(self, message: str) -> T | None:
        """类似 unwrap，但支持自定义错误信息"""
        if self.is_err():
            raise RuntimeError(f"{message}: {self.error}")
        return self.value

    def map(self, func: Callable[[T], U]) -> "Result[U, E]":
        """链式转换成功值（类似 Functor）"""
        return Result.ok(func(self.value)) if self.is_ok() else Result.error(self.error)

    def and_then(self, func: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        """Monadic 绑定操作（类似 flatMap）"""
        return func(self.value) if self.is_ok() else Result.err(self.error)

    def match(self, ok_handler: Callable[[T], U], err_handler: Callable[[E], U]) -> U:
        """模式匹配处理"""
        return ok_handler(self.value) if self.is_ok() else err_handler(self.error)

    def __repr__(self) -> str:
        """序列化支持"""
        return f"Result(value={self.value}, err={self.error})"

    def to_dict(self) -> Dict[str, Optional[Union[T, E]]]:
        """转换为 API 友好格式"""
        return {"ok": self.value, "error": self.error}

    @classmethod
    def ok(cls, value: T) -> "Result[T, E]":
        """构造成功结果"""
        return cls(value=value, error=None)

    @classmethod
    def err(cls, error: E) -> "Result[T, E]":
        """构造失败结果"""
        return cls(value=None, error=error)
