"""
MongoDB 连接简化模块
专注于简化连接管理和集合/数据库创建
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing import Optional


class MongoDBConnector:
    """
    MongoDB 连接简化类

    示例用法:
    >>> connector = MongoDBConnector(uri="mongodb://localhost:27017/")
    >>> db = connector.get_database("test_db")
    >>> collection = connector.get_collection("test_collection", db_name="test_db")
    """

    def __init__(self, uri: str = "mongodb://localhost:27017/"):
        """
        初始化 MongoDB 连接器

        参数:
            uri: MongoDB 连接字符串
        """
        self.uri = uri
        self.client = None
        self._connect()

    def _connect(self) -> bool:
        """
        内部方法：连接到 MongoDB 服务器

        返回:
            bool: 连接是否成功
        """
        try:
            self.client = MongoClient(self.uri)
            # 测试连接
            self.client.admin.command("ping")
            return True
        except ConnectionFailure as e:
            print(f"无法连接到 MongoDB: {e}")
            return False

    def get_database(self, db_name: str):
        """
        获取数据库实例，如果不存在则创建

        参数:
            db_name: 数据库名称

        返回:
            Database: MongoDB 数据库实例

        抛出:
            ValueError: 如果连接未建立或数据库名称为空
        """
        if not self.client:
            raise ValueError("MongoDB 连接未建立")
        if not db_name:
            raise ValueError("数据库名称不能为空")

        return self.client[db_name]

    def get_collection(self, collection_name: str, db_name: Optional[str] = None):
        """
        获取集合实例，如果不存在则创建

        参数:
            collection_name: 集合名称
            db_name: 数据库名称，如果为 None 则必须通过 get_database 先获取数据库

        返回:
            Collection: MongoDB 集合实例

        抛出:
            ValueError: 如果数据库未指定或集合名称为空
        """
        if not collection_name:
            raise ValueError("集合名称不能为空")

        if db_name:
            db = self.get_database(db_name)
        else:
            raise ValueError("必须指定数据库名称")

        return db[collection_name]

    def close(self):
        """
        关闭 MongoDB 连接
        """
        if self.client:
            self.client.close()

    def __enter__(self):
        """支持 with 语句"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持 with 语句"""
        self.close()


def ping(self, verbose: bool = False) -> bool:
    """
    测试数据库连接状态

    参数:
        verbose: 是否打印连接状态信息

    返回:
        bool: 连接是否成功
    """
    try:
        if not self.client:
            if verbose:
                print("MongoDB 客户端未初始化")
            return False

        # 发送ping命令测试连接
        self.client.admin.command("ping")
        if verbose:
            print("成功连接到 MongoDB 服务器")
        return True
    except Exception as e:
        if verbose:
            print(f"无法连接到 MongoDB: {e}")
        return False


if __name__ == "__main__":
    # 使用 with 语句自动管理连接
    with MongoDBConnector() as connector:
        # 获取数据库
        db = connector.get_database("example_db")
        print(f"数据库 '{db.name}' 已获取")

        # 获取集合
        collection = connector.get_collection("example_collection", "example_db")
        print(f"集合 '{collection.name}' 已获取")
