# FlexKit 配置管理模块(vic)

## 概述
`vic` 模块为 FlexKit 应用提供了灵活的配置管理功能，包括：
- 配置项的声明式定义
- 类型安全的配置值管理
- 配置的持久化和加载
- 分组配置管理

## 核心组件

### Config 类
配置容器，管理多个配置项(Field)。

#### 主要功能
- `add_field()`: 添加单个配置项
- `add_fields()`: 批量添加配置项
- `get()`/`set()`: 获取/设置配置值
- `reset()`: 重置所有配置为默认值
- `load_from_json()`/`save_to_json()`: 从JSON文件加载/保存配置

### Field 类
配置项定义，包含配置的元信息。

#### 属性
- `path`: 配置分组路径
- `name`: 配置项名称
- `ftype`: 类型转换函数
- `d_value`: 默认值

#### 方法
- `reset()`: 重置为默认值
- `get()`: 获取当前值
- `set()`: 设置新值(会进行类型检查)

### FType 函数
提供类型转换和验证功能。

#### 内置类型转换
- `f_string()`: 字符串类型
- `f_int()`: 整型
- `f_float()`: 浮点型
- `f_bool()`: 布尔型
- `f_list()`: 列表类型
- `f_tuple()`: 元组类型
- `f_json_dict()`: JSON字典文件
- `f_json_list()`: JSON列表文件
- `f_folder()`: 文件夹路径

## 使用示例

### 基本使用
```python
from flexkit.vic import Config, Field, f_int, f_string

# 创建配置容器
config = Config()

# 添加配置项
config.add_field(Field("app", "port", f_int, 8080))
config.add_field(Field("app", "name", f_string, "myapp"))

# 获取/设置配置
print(config.get("app", "port"))  # 8080
config.set("app", "port", 9090)

# 保存/加载配置
config.save_to_json("config.json")
config.load_from_json("config.json")
```

### 分组配置
```python
# 添加不同分组的配置
config.add_field(Field("db", "host", f_string, "localhost"))
config.add_field(Field("db", "port", f_int, 5432))

# 获取分组配置
db_config = {
    "host": config.get("db", "host"),
    "port": config.get("db", "port")
}
```

### 自定义类型
```python
def f_positive_int(value):
    res, err = f_int(value)
    if err:
        return None, err
    if res <= 0:
        return None, ValueError("必须为正整数")
    return res, None

config.add_field(Field("app", "timeout", f_positive_int, 30))
```

## 最佳实践
1. 按功能模块分组配置项
2. 为配置项提供合理的默认值
3. 使用合适的类型转换函数确保类型安全
4. 定期保存重要配置变更
5. 复杂的配置验证逻辑可以封装为自定义FType函数
