class Field:
    def __init__(self, path, name, ftype, d_value):
        """
        初始化 Field 类的实例。
        :param path: 此 item 所属配置信息的类别的名称。
        :param name: 此配置信息的键值。
        :param ftype: 类型转换函数，接受一个值并返回 (转换结果, 错误信息)。
        :param d_value: 默认值。
        """
        self.path = path
        self.name = name
        self.ftype = ftype
        self.value = None
        result, error = self.ftype(d_value)
        if error is not None:
            raise ValueError(f"Failed to convert default value: {error}")
        self.d_value = result

    def reset(self):
        """
        将字段的值重置为默认值。
        """
        self.value = self.d_value

    def set(self, value):
        """
        设置字段的值，并进行类型转换和验证。
        :param value: 要设置的值。
        :return: 若出现错误返回错误信息，否则返回 None。
        """
        res, err = self.ftype(value)
        if err is not None:
            raise err
        self.value = res

    def get(self):
        """
        获取字段的当前值，如果未设置则返回默认值。
        :return: 字段的当前值。
        """
        return self.value if self.value is not None else self.d_value

    def __str__(self):
        """
        返回字段的字符串表示形式。
        :return: 包含字段路径、名称、类型和值的字符串。
        """
        return f"Field(path={self.path},  name={self.name},  ftype={self.ftype.__name__},  value={self.get()})"

    def serialize(self):
        """
        将字段的信息序列化为字典，方便保存。
        :return: 包含字段信息的字典。
        """
        return {
            "path": self.path,
            "name": self.name,
            "ftype": self.ftype.__name__,
            "default_value": self.d_value,
            "current_value": self.get(),
        }
