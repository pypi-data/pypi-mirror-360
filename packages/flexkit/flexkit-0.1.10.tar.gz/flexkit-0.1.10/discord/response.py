from typing import Any, Dict, Optional, Union, Callable

from ..src.flexkit.tools.result import Result, T, E


class Response:
    """
    标准化响应类，用于封装操作结果

    Attributes:
        status (bool): 操作状态（True=成功，False=失败）
        err (str): 错误描述信息
        msg (dict | str): 附加的响应数据字典
    """

    __slots__ = ("status", "err", "msg")  # 优化内存使用

    def __init__(
        self,
        status: bool = False,
        err: str = "",
        msg: Optional[Union[Dict[str, Any], str]] = None,
    ):
        """
        初始化响应对象

        Args:
            status: 初始状态，默认为False
            err: 初始错误信息，默认为空字符串
            msg: 初始消息字典，默认为空字典
        """
        self.status = status
        self.err = err
        self.msg = msg if msg is not None else {}

    def set_success(self, data: Dict[str, Any]) -> None:
        """设置成功状态及关联数据"""
        self.status = True
        self.msg = data
        self.err = ""

    def set_error(self, error_msg: str) -> None:
        """设置失败状态及错误信息"""
        self.status = False
        self.err = error_msg
        self.msg = {}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典结构（适用于API响应）"""
        return {"status": self.status, "error": self.err, "data": self.msg}

    def is_ok(self) -> bool:
        """更语义化的状态检查"""
        return self.status

    def get_data(self, key: str, default: Any = None) -> Any:
        """安全获取嵌套数据"""
        if isinstance(self.msg, dict):
            return self.msg.get(key, default)
        return default

    @classmethod
    def success(cls, msg: Optional[Dict[str, Any]] = None) -> "Response":
        """创建成功的响应对象"""
        return cls(True, "", msg)

    @classmethod
    def error(cls, err: str) -> "Response":
        """创建失败的响应对象"""
        return cls(False, err, "")

    @classmethod
    def from_result(cls, result: Result[T, E]) -> "Response":
        """最简转换（直接映射状态和消息）"""
        if result.is_ok():
            return Response.success(
                msg={"value": result.value} if result.value is not None else {}
            )
        return Response.error(
            err=str(result.error) if result.error is not None else "Unknown error"
        )

    @classmethod
    def from_result_call(
        cls,
        result: Result[T, E],
        success_formatter: Callable[[T], Dict] = lambda x: {"data": x},
        error_formatter: Callable[[E], str] = str,
    ) -> "Response":
        """支持自定义格式的转换器"""
        return (
            Response.success(msg=success_formatter(result.unwrap()))
            if result.is_ok()
            else Response.error(err=error_formatter(result.error))
        )


def test_response():
    """测试Response类"""
    # 成功用例
    success_resp = Response()
    success_resp.set_success({"user_id": 123, "name": "Alice"})
    print(success_resp.to_dict())

    # 失败用例
    fail_resp = Response()
    fail_resp.set_error("Invalid  input")
    print(fail_resp.to_dict())
