# FlexKit 错误处理模块

## 概述
`err` 模块为 FlexKit 应用提供了统一的错误处理机制，包括：
- 自定义异常类 `MException`
- 同步和异步错误处理的装饰器

## MException 类
带有额外类型信息的基异常类。

### 属性
- `typ`: 错误类型 (默认: "ValueError")
- `msg`: 错误信息 (默认: "None")

### 方法
- `dump()`: 以字典形式返回错误信息
- `__str__()`: 返回格式化的错误字符串

## 装饰器

### ex_exception
用于同步函数的装饰器，将异常包装为MException。

参数：
- `e_type`: 错误类型 (默认: "ValueError")
- `e_msg`: 错误信息 (默认: "None")

示例：
```python
@ex_exception(e_type="CustomError", e_msg="发生错误")
def risky_operation():
    # 你的代码
```

### async_ex_exception
用于异步函数的装饰器，将异常包装为MException。

参数：
- `e_type`: 错误类型 (默认: "AsyncError")
- `e_msg`: 错误信息 (默认: "None")

示例：
```python
@async_ex_exception(e_type="AsyncError", e_msg="异步操作失败")
async def async_operation():
    # 你的异步代码
```

## 使用说明
1. 两个装饰器都会保留原始抛出的MException
2. 其他所有异常都会被包装为MException
3. 使用`dump()`方法获取错误信息用于API响应
