# FlexKit 数据验证模块(vdm)

## 概述
`vdm` 模块为 FlexKit 应用提供了数据模型验证功能，包括：
- 数据模型定义
- 字段验证规则
- 多模型管理
- 内置验证函数

## 核心组件

### Model 类
数据模型基类，用于定义数据结构。

#### 主要功能
- `add_field()`: 添加单个字段
- `add_fields()`: 批量添加字段
- `get()`/`set()`: 获取/设置字段值
- 字段存在性检查

示例：
```python
from flexkit.vdm import Model, Field

# 创建用户模型
user_model = Model("User")
user_model.add_fields([
    Field("username", "", [v_s_not_null, v_s_trim]),
    Field("age", 0)
])
```

### Field 类
模型字段定义。

#### 特性：
- `name`: 字段名称
- `default`: 默认值
- `v_funcs`: 验证函数列表
- 值获取和设置方法

### Models 类
多模型管理器。

#### 主要功能：
- `add_model()`: 添加单个模型
- `add_models()`: 批量添加模型
- `get()`: 获取指定模型

### VType 验证函数
内置字段验证函数。

#### 常用验证函数：
- `v_s_not_null`: 非空验证
- `v_s_trim`: 去除两端空格
- `v_s_len`: 长度验证
- `v_s_in`: 枚举值验证
- `v_s_lower`/`v_s_upper`: 大小写转换

## 使用示例

### 基本使用
```python
from flexkit.vdm import Model, Field, v_s_not_null, v_s_len

# 创建产品模型
product_model = Model("Product")
product_model.add_fields([
    Field("name", "", [v_s_not_null]),
    Field("price", 0.0),
    Field("category", "", [
        v_s_not_null,
        lambda v, n: v_s_len(v, gt=2, le=20, name=n)
    ])
])

# 设置字段值
product_model.set("name", "Laptop")
product_model.set("price", 999.99)

# 获取字段值
print(product_model.get("name"))  # "Laptop"
```

### 多模型管理
```python
from flexkit.vdm import Models

# 创建模型管理器
manager = Models()
manager.add_models([user_model, product_model])

# 获取模型实例
user = manager.get("User")
product = manager.get("Product")
```

## 最佳实践
1. 为关键字段添加适当的验证函数
2. 使用lambda包装验证函数实现参数传递
3. 通过Models类集中管理业务模型
4. 自定义验证函数应抛出MException异常
5. 重要字段应设置合理的默认值
