from .result import Result


def res(status: bool = False, err: str = None, msg: any = None):
    """
    响应
    :param status: 状态
    :param err: 错误信息
    :param msg: 消息
    :return: dict
    """
    return {
        "status": status,  # 状态
        "err": err if err else "",  # 错误信息
        "msg": msg if not msg else {},  # 消息
    }


def from_result(result: Result):
    """
    从结果中获取响应
    :param result: 结果
    :return: dict
    """
    if result.is_ok():
        return res(True, result.err, None)
    else:
        return res(False, None, result.value)
