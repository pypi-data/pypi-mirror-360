import json
from .Field import Field


class Config:
    def __init__(self):
        # 将 _fields 改为嵌套字典，按 path 分组存储 Field 对象
        self._fields = {}

    def add_field(self, field: Field):
        if field.path not in self._fields:
            self._fields[field.path] = {}
        self._fields[field.path][field.name] = field

    def add_fields(self, fields: list):
        for field in fields:
            self.add_field(field)

    def set(self, path, name, value):
        if path in self._fields and name in self._fields[path]:
            field = self._fields[path][name]
            field.set(value)

    def get(self, path, name):
        if path in self._fields and name in self._fields[path]:
            return self._fields[path][name].get()
        return None

    def reset(self):
        """
        将所有字段重置为默认值。
        """
        for path_fields in self._fields.values():
            for field in path_fields.values():
                field.reset()

    def load_from_json(self, file_path):
        """
        从 JSON 文件中加载配置。
        :param file_path: JSON 文件的路径。
        """
        with open(file_path, "r") as f:
            data = json.load(f)
            for path, path_fields in data.items():
                if path in self._fields:
                    for name, value in path_fields.items():
                        if name in self._fields[path]:
                            self._fields[path][name].set(value)

    def save_to_json(self, file_path):
        """
        将配置保存到 JSON 文件中。
        :param file_path: JSON 文件的路径。
        """
        data = {
            path: {name: field.get() for name, field in path_fields.items()}
            for path, path_fields in self._fields.items()
        }
        with open(file_path, "w") as f:
            f.write(json.dumps(data, indent=4))

    def to_json(self):
        return {
            path: {name: field.get() for name, field in path_fields.items()}
            for path, path_fields in self._fields.items()
        }
