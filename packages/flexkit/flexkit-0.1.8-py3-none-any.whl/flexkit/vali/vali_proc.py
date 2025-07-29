from ..err import MException
from ..tools import Result

from typing import Any, Callable, Optional


def vali_group_dict(data: dict, **valis: "ValiProc") -> Callable[[Any], Result]:
    """
    校验一个字典中的多个字段。

    Args:
        data (dict): 待校验的字典。
        **valis (ValiProc): 字段名到校验处理器的映射。

    Returns:
        Callable[[Any], Result]: 一个返回校验结果的函数。

    该函数会遍历传入的 `valis` 参数中的每个键值对，其中键为字段名，值为对应的校验处理器。
    对于每个字段，会调用相应的校验处理器进行校验，并获取校验结果。
    如果校验失败（即结果是一个错误），则返回一个返回该错误结果的函数。
    如果所有字段都校验通过，则更新 `data` 字典中对应字段的值为校验后的值，并返回一个返回成功结果的函数。

    """
    for key, vali in valis.items():
        res = vali.val(data.get(key))
        if res.is_err():
            return lambda x: res
        data[key] = res.value
    return Result.ok(data)


def vali_group_list(data: list, *valis: "ValiProc") -> Result:
    """
    验证数据列表中的每个元素是否符合给定的验证条件。

    Args:
        data (list): 待验证的数据列表。
        *valis (ValiProc): 可变数量的验证器，数量必须与data列表的长度相同。

    Returns:
        Result: 验证结果。如果所有元素都通过验证，则返回包含验证后数据的Result.ok；
                如果有元素未通过验证，则返回包含错误信息的Result.err。

    """
    for index, value in enumerate(data):
        res = valis[index].val(value)
        if res.is_err():
            return res
        data[index] = res.value
    return Result.ok(data)


def vali_pro(params: dict = None):
    """
    用于定义校验器或处理器函数的装饰器。

    Args:
        params (dict, optional): 用于校验或处理器函数的参数字典。默认为 None。注：此处定义的参数在定义的函数中也需要定义参数，否则无法使用

    Returns:
        Callable[[Any], Result]: 返回一个新的函数，该函数在调用时会使用给定的参数字典校验传入的参数。


    Example:

        >>> @vali_pro(params={"msg": "值必须是非负数"})
        ... def my_func(a: int, msg: str) -> Result:
        ...     if a < 0:
        ...         return Result.err(f"{msg} 不能为负数")
        ...     return Result.ok(f"{a} {msg}")

    """

    def decorator(func: Callable[[Any], Result]) -> Callable[[Any], Result]:
        def wrapper(value, *args, **kwargs) -> Result:
            if params:
                return func(value, *args, **params, **kwargs)
            else:
                return func(value)

        return wrapper

    return decorator


def validator(
    msg: str, *validators: Callable[[Any], Result]
) -> Callable[[Any], Result]:
    """组合多个验证器函数，返回一个组合验证器包装函数。

    当输入值通过所有验证器时返回成功结果，任一验证失败则立即返回错误。
    错误信息可被自定义消息包裹，保留原始错误信息。

    Args:
        msg: 验证失败时的自定义错误消息前缀。若为空字符串则直接返回验证器的原始错误
        validators: 验证器函数列表，每个函数接受任意输入并返回Result对象

    Returns:
        包装函数：接受输入值，返回聚合验证结果的Result对象
        错误时：返回包含自定义消息和原始错误的MException（若msg非空）
        成功时：返回最后一个验证器的成功结果
    """

    def wrapper(value: Any) -> Result:
        for validate in iter(validators):
            result = validate(value)
            if result.is_err():
                return Result.err(MException(msg, str(result.error))) if msg else result
        return result

    return wrapper


def processor(
    msg: str, *processors: Callable[[Any], Result]
) -> Callable[[Any], Result]:
    """组合多个处理器函数，返回一个顺序处理包装函数。

    按顺序将前一个处理器的输出作为下一个处理器的输入，形成处理链。
    任一处理器失败则中断流程，成功时返回最终处理结果。

    Args:
        msg: 处理失败时的自定义错误消息前缀。若为空字符串则直接返回处理器的原始错误
        processors: 处理器函数列表，每个函数接受任意输入并返回Result对象

    Returns:
        包装函数：接受初始值，返回最终处理结果的Result对象
        错误时：返回包含自定义消息和原始错误的MException（若msg非空）
        成功时：返回最后一个处理器的成功结果（包含处理后的值）
    """

    def wrapper(value: Any) -> Result:
        current_value = value
        for processor in iter(processors):
            result = processor(current_value)
            if result.is_err():
                return Result.err(MException(msg, str(result.error))) if msg else result
            current_value = result.value
        return Result.ok(current_value)

    return wrapper


class ValiProc:
    """
    ValiProc类，用于组合处理器和验证器。

    Attributes:
        processors (Optional[Callable[[Any], Result]]): 处理函数。
        validators (Optional[Callable[[Any], Result]]): 验证函数。

    Methods:
        val(value: Any) -> Result: 执行验证器链，返回聚合验证结果的Result对象。
    """

    def __init__(
        self,
        processors: Optional[Callable[[Any], Result]] = None,
        validators: Optional[Callable[[Any], Result]] = None,
    ):
        """
        初始化函数。

        Args:
            processors (Optional[Callable[[Any], Result]], optional): 处理函数。默认为 None。
            validators (Optional[Callable[[Any], Result]], optional): 验证函数。默认为 None。

        Attributes:
            processors (Optional[Callable[[Any], Result]]): 处理函数。
            validators (Optional[Callable[[Any], Result]]): 验证函数。
        """
        self.processors = processors
        self.validators = validators

    def val(self, value: Any) -> Result:
        """
        执行验证器链，返回聚合验证结果的Result对象。

        Args:
            value (Any): 需要验证的值。

        Returns:
            Result: 聚合验证结果的Result对象。

        """
        new_value = value
        if self.processors:
            result = self.processors(value)
            if result.is_err():
                return result
            new_value = result.value
        if self.validators:
            result = self.validators(new_value)
            if result.is_err():
                return result
        return Result.ok(new_value)
