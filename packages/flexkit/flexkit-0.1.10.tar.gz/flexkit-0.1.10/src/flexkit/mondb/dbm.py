"""MongoDB 连接简化模块 - 极简版本
专注于最简化的使用体验，基于 Pydantic 和 PyMongo 的融合设计
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing import Optional, Dict, List, Union, Type, TypeVar
import os

# 导入数据模型基类
from .datam import DataModel
from pydantic import Field

T = TypeVar("T", bound=DataModel)


class MongoDB:
    """极简 MongoDB 连接器"""

    def __init__(self, uri: str = None, database: str = None):
        """
        初始化 MongoDB 连接

        参数:
            uri: MongoDB 连接字符串，默认从环境变量 MONGODB_URI 获取或使用 localhost
            database: 默认数据库名，默认从环境变量 MONGODB_DB 获取
        """
        self.uri = uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.default_db = database or os.getenv("MONGODB_DB", "default")
        self.client = None
        self._connect()

    def _connect(self):
        """连接到 MongoDB"""
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command("ping")
        except ConnectionFailure as e:
            raise ConnectionError(f"无法连接到 MongoDB: {e}")

    def db(self, name: str = None):
        """获取数据库"""
        return self.client[name or self.default_db]

    def collection(self, name: str, db: str = None):
        """获取集合"""
        if db is None:
            return self.db(self.default_db)[name]
        return self.db(db)[name]

    # 简化的 CRUD 操作
    def save(self, collection: str, doc: DataModel, db: str = None) -> str:
        """保存文档（插入或更新）"""
        coll = self.collection(collection, db)
        if doc.id:
            # 更新现有文档
            coll.replace_one({"_id": doc.id}, doc.to_mongo())
            return str(doc.id)
        else:
            # 插入新文档
            result = coll.insert_one(doc.to_mongo())
            return str(result.inserted_id)

    def save_many(
        self, collection: str, docs: List[DataModel], db: str = None
    ) -> List[str]:
        """批量保存文档"""
        coll = self.collection(collection, db)
        docs_data = [doc.to_mongo() for doc in docs]
        result = coll.insert_many(docs_data)
        return [str(oid) for oid in result.inserted_ids]

    def find_one(
        self, collection: str, model: Type[T], filter_dict: Dict = None, db: str = None
    ) -> Optional[T]:
        """查找单个文档"""
        coll = self.collection(collection, db)
        result = coll.find_one(filter_dict or {})
        return model.from_mongo(result)

    def find(
        self,
        collection: str,
        model: Type[T],
        filter_dict: Dict = None,
        limit: int = None,
        skip: int = None,
        sort: List = None,
        db: str = None,
    ) -> List[T]:
        """查找多个文档"""
        coll = self.collection(collection, db)
        cursor = coll.find(filter_dict or {})

        if sort:
            cursor = cursor.sort(sort)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)

        return [model.from_mongo(doc) for doc in cursor]

    def update(
        self,
        collection: str,
        filter_dict: Dict,
        update_data: Union[DataModel, Dict],
        db: str = None,
    ) -> int:
        """更新文档"""
        coll = self.collection(collection, db)

        if isinstance(update_data, DataModel):
            update_dict = {"$set": update_data.to_mongo()}
        else:
            update_dict = {"$set": update_data}

        result = coll.update_many(filter_dict, update_dict)
        return result.modified_count

    def delete(self, collection: str, filter_dict: Dict, db: str = None) -> int:
        """删除文档"""
        coll = self.collection(collection, db)
        result = coll.delete_many(filter_dict)
        return result.deleted_count

    def count(self, collection: str, filter_dict: Dict = None, db: str = None) -> int:
        """统计文档数量"""
        coll = self.collection(collection, db)
        return coll.count_documents(filter_dict or {})

    def exists(self, collection: str, filter_dict: Dict, db: str = None) -> bool:
        """检查文档是否存在"""
        return self.count(collection, filter_dict, db) > 0

    def close(self):
        """关闭连接"""
        if self.client:
            self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 全局实例（可选使用）
_default_db = None


def get_db() -> MongoDB:
    """获取默认数据库实例"""
    global _default_db
    if _default_db is None:
        _default_db = MongoDB()
    return _default_db


def set_db(uri: str = None, database: str = None):
    """设置默认数据库连接"""
    global _default_db
    _default_db = MongoDB(uri, database)


# 便捷函数
def save(collection: str, doc: DataModel, db: str = None) -> str:
    """保存文档到默认数据库"""
    return get_db().save(collection, doc, db)


def find_one(
    collection: str, model: Type[T], filter_dict: Dict = None, db: str = None
) -> Optional[T]:
    """从默认数据库查找单个文档"""
    return get_db().find_one(collection, model, filter_dict, db)


def find(
    collection: str, model: Type[T], filter_dict: Dict = None, **kwargs
) -> List[T]:
    """从默认数据库查找多个文档"""
    return get_db().find(collection, model, filter_dict, **kwargs)


def update(
    collection: str,
    filter_dict: Dict,
    update_data: Union[DataModel, Dict],
    db: str = None,
) -> int:
    """更新默认数据库中的文档"""
    return get_db().update(collection, filter_dict, update_data, db)


def delete(collection: str, filter_dict: Dict, db: str = None) -> int:
    """从默认数据库删除文档"""
    return get_db().delete(collection, filter_dict, db)


if __name__ == "__main__":
    # 使用示例

    # 定义文档模型
    class User(DataModel):
        name: str
        email: str
        age: Optional[int] = None
        tags: List[str] = Field(default_factory=list)

    # 方式1：使用类实例
    with MongoDB("mongodb://123.249.88.131:27017/", "test") as db:
        # 创建用户
        user = User(name="张三", email="zhangsan@example.com", age=25)
        user_id = db.save("users", user)
        print(f"保存用户: {user_id}")

        # 查找用户
        found_user = db.find_one("users", User, {"name": "张三"})
        if found_user:
            print(f"找到用户: {found_user.name}")

        # 查找所有用户
        all_users = db.find("users", User, limit=10)
        print(f"用户总数: {len(all_users)}")

    # 方式2：使用全局函数（更简单）
    set_db("mongodb://123.249.88.131:27017/", "test")

    user = User(name="李四", email="lisi@example.com", age=30)
    user_id = save("users", user)

    users = find("users", User, {"age": {"$gte": 18}}, limit=5)
    print(f"成年用户数量: {len(users)}")
