from .MError import MException


def ex_exception(e_type: str = "ValueError", e_msg: str = "None"):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except MException as e:
                raise e
            except Exception:
                raise MException(e_type, e_msg)

        return wrapper

    return decorator


def async_ex_exception(e_type: str = "AsyncError", e_msg: str = "None"):
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except MException as e:
                raise e
            except Exception:
                raise MException(e_type, e_msg)

        return async_wrapper

    return decorator
