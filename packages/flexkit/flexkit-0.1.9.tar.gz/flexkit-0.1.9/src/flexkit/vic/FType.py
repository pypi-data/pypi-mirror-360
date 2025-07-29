import pathlib
from decimal import Decimal


def f_string(value):
    if isinstance(value, (str, int, float, Decimal, bool)):
        return str(value), None
    if isinstance(value, (list, tuple)):
        return None, ValueError(f"{type(value)}类型无法转换为string")
    return None, ValueError(f"未知类型{type(value)}")


def f_int(value):
    if isinstance(value, (int, bool)):
        return int(value), None
    if isinstance(value, (str, float, Decimal)):
        try:
            return int(value), None
        except (ValueError, TypeError):
            return None, ValueError(f"无法将{type(value)}类型转换为int")
    if isinstance(value, (list, tuple)):
        return None, ValueError(f"{type(value)}类型无法转换为int")
    return None, ValueError(f"未知类型{type(value)}")


def f_float(value):
    if isinstance(value, (float, int, bool)):
        return float(value), None
    if isinstance(value, (str, Decimal)):
        try:
            return float(value), None
        except (ValueError, TypeError):
            return None, ValueError(f"无法将{type(value)}类型转换为float")
    if isinstance(value, (list, tuple)):
        return None, ValueError(f"{type(value)}类型无法转换为float")
    return None, ValueError(f"未知类型{type(value)}")


def f_bool(value):
    if isinstance(value, bool):
        return value, None
    if isinstance(value, (int, float)):
        return bool(value), None
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1"}:
            return True, None
        elif normalized in {"false", "0"}:
            return False, None
        return None, ValueError(f"无法将字符串{value}转换为bool")
    if isinstance(value, (list, tuple)):
        return None, ValueError(f"{type(value)}类型无法转换为bool")
    return None, ValueError(f"未知类型{type(value)}")


def f_list(value):
    if isinstance(value, list):
        return value.copy(), None
    if isinstance(value, (tuple, set, str)):
        return list(value), None
    if isinstance(value, (dict, int, float, bool)):
        return None, ValueError(f"{type(value)}类型无法转换为list")
    return None, ValueError(f"未知类型{type(value)}")


def f_tuple(value):
    if isinstance(value, tuple):
        return value, None
    if isinstance(value, (list, set, str)):
        return tuple(value), None
    if isinstance(value, (dict, int, float, bool)):
        return None, ValueError(f"{type(value)}类型无法转换为tuple")
    return None, ValueError(f"未知类型{type(value)}")


def f_json_dict(value):
    value_obj = pathlib.Path(value)
    if value_obj.suffix != "json":
        return None, ValueError(f"{value} must be a json file")
    if not value_obj.exists():
        value_obj.write_text("{}")
    return str(value_obj), None


def f_json_list(value):
    value_obj = pathlib.Path(value)
    if value_obj.suffix != "json":
        return None, ValueError(f"{value} must be a json file")
    if not value_obj.exists():
        value_obj.write_text("[]")
    return str(value_obj), None


def f_folder(value):
    value_obj = pathlib.Path(value)
    if value_obj.suffix != "":
        return None, ValueError(f"{value} must be a json folder")
    if not value_obj.exists():
        value_obj.mkdir(parents=True, exist_ok=True)
    return str(value_obj), None


def d_value(v_type):
    if v_type == str:
        return "", None
    if v_type == int:
        return 0, None
    if v_type == float:
        return 0.0, None
    if v_type == Decimal:
        return Decimal(0), None
    if v_type == bool:
        return False, None
    if v_type == list:
        return [], None
    if v_type == tuple:
        return (), None
    if v_type == dict:
        return {}, None
    return None, ValueError(f"不支持类型{v_type}")
