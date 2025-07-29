from ..err import MException


def v_s_not_null(value: str, name: str = ""):
    """
    验证字符串是否为 null 或空字符串。
    """
    if value is None:
        raise MException("FieldVerifyError", f"字段({name})值为 null")
    return value


def v_s_is_empty(value: str, name: str = ""):
    """
    验证字符串是否为空字符串。
    """
    if value.strip() == "":
        raise MException("FieldVerifyError", f"字段({name})值为空")
    return value


def v_s_trim(value: str, name: str = ""):
    """
    去除字符串两端的空格。
    """
    try:
        return value.strip()
    except Exception as e:
        raise MException("FieldVerifyError", f"字段({name})去除两端空格失败: {e}")


def v_s_lower(value: str, name: str = ""):
    """
    将字符串转换为小写。
    """
    try:
        return value.lower()
    except Exception as e:
        raise MException("FieldVerifyError", f"字段({name})转换小写失败: {e}")


def v_s_upper(value: str, name: str = ""):
    """
    将字符串转换为大写。
    """
    try:
        return value.upper()
    except Exception as e:
        raise MException("FieldVerifyError", f"字段({name})转换大写失败: {e}")


def param_decorator(**params):
    """
    参数化装饰器，用于传递额外的参数给验证函数。
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs, **params)

        return wrapper

    return decorator


def v_s_len(
    value: str,
    lt: int = None,
    gt: int = None,
    le: int = None,
    ge: int = None,
    name: str = "",
):
    """
    验证字符串长度。
    """
    value_len = len(value)
    if lt is not None and value_len >= lt:
        raise MException(
            "FieldVerifyError", f"字段({name})长度应 < {lt}，但实际为 {value_len}"
        )
    if gt is not None and value_len <= gt:
        raise MException(
            "FieldVerifyError", f"字段({name})长度应 > {gt}，但实际为 {value_len}"
        )
    if le is not None and value_len > le:
        raise MException(
            "FieldVerifyError", f"字段({name})长度应 <= {le}，但实际为 {value_len}"
        )
    if ge is not None and value_len < ge:
        raise MException(
            "FieldVerifyError", f"字段({name})长度应 >= {ge}，但实际为 {value_len}"
        )
    return value


def v_s_in(value: str, enum_value: list, name: str = ""):
    """
    验证字符串是否在枚举值列表中。
    """
    if value not in enum_value:
        raise MException(
            "FieldVerifyError",
            f"字段({name})的可选值为 {enum_value}，当前字段值为 {value}",
        )
    return value
