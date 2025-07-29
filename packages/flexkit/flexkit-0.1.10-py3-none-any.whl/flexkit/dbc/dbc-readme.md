# FlexKit 数据库连接模块(dbc)

## 概述
`dbc` 模块为 FlexKit 应用提供了完整的数据库操作支持，包括：
- 安全的SQL语句构建
- 数据库连接管理
- 错误处理机制
- 结果回调处理

## 核心组件

### Query 类
安全的SQL语句构建器，防止SQL注入。

#### 主要功能
- `select()`: 构建SELECT语句
- `insert()`: 构建INSERT语句
- `update()`: 构建UPDATE语句
- `delete()`: 构建DELETE语句
- 支持复杂WHERE条件(AND/OR/NOT)
- 支持LIMIT/OFFSET分页

示例：
```python
from flexkit.dbc import Query

# 创建查询构建器
query = Query("users", "public")

# 构建复杂查询
sql, params = query.select(
    columns=["id", "name"],
    where={
        "and": {
            "age>=": 18,
            "or": {
                "name LIKE": "张%",
                "name LIKE": "李%"
            }
        }
    },
    orderby="id DESC",
    limit=10
)
```

### PDBConn 类
PostgreSQL数据库连接管理器。

#### 主要功能
- 连接管理(连接/关闭/心跳检测)
- 事务管理(提交/回滚)
- 增删改查操作
- 存储过程调用
- 内置错误处理装饰器

示例：
```python
from flexkit.dbc import PDBConn

# 创建数据库连接
conn = PDBConn(
    user="postgres",
    password="password",
    host="localhost",
    port=5432,
    database="test"
)

# 执行查询
results = conn.select("users", "id, name", "age >= 18")

# 执行更新
conn.update("users", {"name": "张三"}, "id = 1")
conn.commit()
```

### DBCallBack 类
查询结果回调处理器。

#### 内置回调
- `json_cb`: 将结果转换为JSON格式

### DBException 类
数据库操作异常类。

#### 特性
- 类型化错误信息
- 错误信息序列化
- 清晰的错误描述

## 使用建议
1. 使用Query类构建SQL语句，避免SQL注入
2. 重要操作务必使用事务
3. 合理使用回调处理查询结果
4. 捕获并处理DBException异常
5. 长时间空闲的连接应定期发送心跳查询

## 最佳实践
```python
from flexkit.dbc import PDBConn, Query, DBException

try:
    # 初始化
    conn = PDBConn(...)
    query = Query("products", "public")
    
    # 构建安全查询
    sql, params = query.select(...)
    
    # 执行查询
    results = conn.execute(sql, params)
    
    # 处理结果
    for row in results:
        print(row)
        
    conn.commit()
        
except DBException as e:
    print(f"数据库错误: {e}")
    conn.rollback()
finally:
    conn.close()
```
