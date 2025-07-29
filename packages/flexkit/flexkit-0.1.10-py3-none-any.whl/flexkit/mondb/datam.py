"""数据模型基类 - Pydantic 高级封装
提供增强的 Pydantic 基类，支持 MongoDB 兼容性和通用数据操作
可独立使用，无需数据库依赖
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from bson import ObjectId
import json
import uuid


class DataModel(BaseModel):
    """增强的数据模型基类

    特性:
    - 自动时间戳管理
    - MongoDB 兼容性
    - 灵活的序列化选项
    - 数据验证和类型安全
    - 可独立使用，无数据库依赖
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={datetime: lambda v: v.isoformat()},
        populate_by_name=True,
        validate_assignment=True,
        extra="ignore",
    )

    id: Optional[str] = Field(
        default=str(ObjectId()), alias="_id", description="唯一标识符"
    )

    def to_mongo(self) -> Dict[str, Any]:
        """转换为 MongoDB 兼容格式"""
        data = self.model_dump(by_alias=True, exclude_unset=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data

    def to_dict(
        self, exclude_none: bool = True, by_alias: bool = False
    ) -> Dict[str, Any]:
        """转换为字典格式

        参数:
            exclude_none: 是否排除 None 值
            by_alias: 是否使用字段别名
        """
        return self.model_dump(
            exclude_none=exclude_none, by_alias=by_alias, mode="json"
        )

    def to_json(self, indent: int = None, ensure_ascii: bool = False) -> str:
        """转换为 JSON 字符串

        参数:
            indent: JSON 缩进空格数
            ensure_ascii: 是否确保 ASCII 编码
        """
        data = self.to_dict()
        return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii, default=str)

    @classmethod
    def from_mongo(cls, data: Dict[str, Any]):
        """从 MongoDB 数据创建实例"""
        if not data:
            return None
        return cls(**data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典创建实例"""
        if not data:
            return None
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str):
        """从 JSON 字符串创建实例"""
        if not json_str:
            return None
        data = json.loads(json_str)
        return cls.from_dict(data)

    def update_fields(self, **kwargs) -> "DataModel":
        """更新字段值并返回新实例

        参数:
            **kwargs: 要更新的字段和值
        """
        data = self.to_dict()
        data.update(kwargs)
        data["updated_at"] = datetime.utcnow()
        return self.__class__.from_dict(data)

    def copy_with(self, **kwargs) -> "DataModel":
        """复制实例并修改指定字段

        参数:
            **kwargs: 要修改的字段和值
        """
        return self.update_fields(**kwargs)

    def mark_updated(self) -> None:
        """标记为已更新（更新 updated_at 时间戳）"""
        self.updated_at = datetime.utcnow()

    def get_field_names(self) -> List[str]:
        """获取所有字段名称"""
        return list(self.model_fields.keys())

    def get_changed_fields(self, other: "DataModel") -> Dict[str, Any]:
        """获取与另一个实例不同的字段

        参数:
            other: 要比较的另一个实例

        返回:
            Dict[str, Any]: 不同字段的字典 {字段名: 当前值}
        """
        if not isinstance(other, self.__class__):
            raise ValueError("只能与相同类型的实例进行比较")

        current_data = self.to_dict()
        other_data = other.to_dict()

        changed = {}
        for key, value in current_data.items():
            if key not in other_data or other_data[key] != value:
                changed[key] = value

        return changed

    def validate_data(self) -> bool:
        """验证数据完整性

        返回:
            bool: 数据是否有效
        """
        try:
            self.model_validate(self.model_dump())
            return True
        except Exception:
            return False

    def __str__(self) -> str:
        """字符串表示"""
        class_name = self.__class__.__name__
        id_str = f"id={self.id}" if self.id else "id=None"
        return f"{class_name}({id_str})"

    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.to_json(indent=2)

    def __eq__(self, other) -> bool:
        """相等性比较"""
        if not isinstance(other, self.__class__):
            return False
        return self.to_dict() == other.to_dict()

    def __hash__(self) -> int:
        """哈希值计算"""
        if self.id:
            return hash(str(self.id))
        return hash(self.to_json())


# 便捷函数
def create_model_class(class_name: str, fields: Dict[str, Any]) -> type:
    """动态创建数据模型类

    参数:
        class_name: 类名
        fields: 字段定义字典

    返回:
        type: 新创建的数据模型类
    """
    return type(class_name, (DataModel,), {"__annotations__": fields})


if __name__ == "__main__":
    # 使用示例

    # 定义用户模型
    class User(DataModel):
        name: str = Field(..., description="用户姓名")
        email: str = Field(..., description="用户邮箱")
        age: Optional[int] = Field(None, ge=0, le=150, description="用户年龄")
        tags: List[str] = Field(default_factory=list, description="用户标签")
        is_active: bool = Field(default=True, description="是否激活")

    # 创建用户实例
    user = User(
        name="张三", email="zhangsan@example.com", age=25, tags=["开发者", "Python"]
    )

    print("=== 基本操作 ===")
    print(f"用户: {user}")
    print(f"JSON: {user.to_json()}")
    print(f"字典: {user.to_dict()}")

    print("\n=== 数据转换 ===")
    # 转换为 MongoDB 格式
    mongo_data = user.to_mongo()
    print(f"MongoDB 格式: {mongo_data}")

    # 从字典重建
    user2 = User.from_dict(mongo_data)
    print(f"重建用户: {user2}")

    print("\n=== 字段操作 ===")
    # 更新字段
    updated_user = user.update_fields(age=26, tags=["开发者", "Python", "MongoDB"])
    print(f"更新后: {updated_user.to_dict()}")

    # 获取变更字段
    changes = updated_user.get_changed_fields(user)
    print(f"变更字段: {changes}")

    print("\n=== 验证 ===")
    print(f"数据有效性: {user.validate_data()}")
    print(f"字段名称: {user.get_field_names()}")
