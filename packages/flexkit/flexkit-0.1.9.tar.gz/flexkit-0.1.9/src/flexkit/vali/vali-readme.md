# FlexKit 数据验证与处理模块

## 概述
`vali` 模块为 FlexKit 应用提供了强大的数据验证和处理功能，包括：
- 数据转换处理器(Processor)
- 数据验证器(Validator) 
- 验证处理组合工具(ValiProc)

## Processor 类
提供数据转换功能，所有方法返回`Result`对象。

### 常用方法
- `trim()`: 去除字符串首尾空格
- `replace()`: 字符串替换
- `to_upper()`/`to_lower()`: 大小写转换
- `to_int()`/`to_float()`: 数值类型转换
- `to_datetime()`: 日期时间转换
- `to_json()`: JSON序列化

示例：
```python
from flexkit.vali import Processor

# 字符串处理
Processor.trim()(" hello ")  # Result.ok("hello")
Processor.to_upper()("text")  # Result.ok("TEXT")

# 类型转换
Processor.to_int()("123")  # Result.ok(123)
```

## Validator 类
提供数据验证功能，所有方法返回`Result`对象。

### 常用方法
- `not_null()`: 非空验证
- `max()`/`min()`: 数值范围验证
- `regex()`: 正则表达式验证
- `starts_with()`/`ends_with()`: 字符串前后缀验证
- `path_exists()`: 文件路径验证
- `datetime_between()`: 日期时间范围验证

示例：
```python
from flexkit.vali import Validator

# 基础验证
Validator.not_null()(None)  # Result.err("值为空")
Validator.max(100)(50)  # Result.ok(True)

# 字符串验证
Validator.regex(r'^\d+$')("123")  # Result.ok(True)
Validator.starts_with("http")("http://example.com")  # Result.ok(True)
```

## ValiProc 工具类
组合处理器和验证器，提供链式处理能力。

### 核心功能
- `vali_group_dict()`: 字典多字段验证
- `vali_group_list()`: 列表元素验证
- `vali_pro()`: 验证器装饰器
- `validator()`: 组合多个验证器
- `processor()`: 组合多个处理器

示例：
```python
from flexkit.vali import ValiProc, Processor, Validator

# 组合验证
vali = ValiProc(
    processors=Processor.trim(),
    validators=Validator.not_null()
)
vali.val(" hello ")  # Result.ok("hello")

# 字典多字段验证
data = {"name": " John ", "age": "30"}
vali_group_dict(data, 
    name=ValiProc(Processor.trim()), 
    age=ValiProc(Processor.to_int(), Validator.min(18))
)  # Result.ok({"name": "John", "age": 30})
```

## 使用建议
1. 处理器和验证器都返回`Result`对象，便于错误处理
2. 复杂验证逻辑可拆分为多个简单验证器组合
3. 使用`ValiProc`组合处理流程，提高代码可读性
4. 验证失败时返回详细的错误信息
