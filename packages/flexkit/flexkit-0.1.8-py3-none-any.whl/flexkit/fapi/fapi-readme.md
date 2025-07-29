# FlexKit FastAPI 封装模块(fapi)

## 概述
`fapi` 模块为 FlexKit 应用提供了对 FastAPI 的封装，简化了 API 开发流程，包括：
- 应用快速初始化
- 路由自动注册
- 请求方法枚举
- 默认配置预设

## 核心组件

### App 类
FastAPI 应用封装类。

#### 主要功能
- 初始化 FastAPI 应用
- 添加中间件
- 批量注册路由
- 启动服务

#### 示例：
```python
from flexkit.fapi import App, ChildPath, Router, HttpMethod

# 创建路由
routes = [
    ChildPath("api", "/api", ["API示例"], [
        Router(hello_world, "/hello", HttpMethod("GET"))
    ])
]

# 初始化应用
app = App(
    app_o={"title": "My API"},
    middleware={"middleware_class": CORSMiddleware},
    routers=routes
)

# 启动服务
app.run(port=8000)
```

### ChildPath 类
路由分组管理。

#### 特性：
- 支持多级路由嵌套
- 自动生成 API 文档标签
- 支持根路径特殊处理

#### 示例：
```python
api_v1 = ChildPath("api-v1", "/v1", ["API V1"], [
    Router(get_users, "/users", HttpMethod.GET),
    Router(create_user, "/users", HttpMethod.POST)
])
```

### Router 类
路由定义封装。

#### 参数：
- `func`: 路由处理函数
- `path`: 路由路径
- `method`: HttpMethod 枚举值
- 其他 FastAPI 路由参数

### HttpMethod 枚举
标准 HTTP 方法封装。

#### 支持方法：
- GET
- POST
- PUT
- DELETE

#### 示例：
```python
method = HttpMethod("POST")  # 或 HttpMethod().POST()
```

### 默认配置
#### app_default_options()
返回默认的 FastAPI 初始化参数。

#### default_cors()
返回默认的 CORS 中间件配置。

## 使用建议
1. 使用 ChildPath 组织路由结构
2. 通过 Router 封装路由定义
3. 使用 HttpMethod 确保方法类型安全
4. 合理使用默认配置快速初始化
5. 生产环境应自定义安全配置

## 最佳实践
```python
from flexkit.fapi import App, ChildPath, Router, HttpMethod
from flexkit.fapi.default_options import app_default_options, default_cors

# 定义路由处理函数
async def get_items():
    return {"message": "Get items"}

# 创建路由分组
routes = [
    ChildPath("items", "/items", ["商品管理"], [
        Router(get_items, "/", HttpMethod.GET)
    ])
]

# 初始化应用
app = App(
    app_o=app_default_options(),
    middleware=default_cors(),
    routers=routes
)

# 启动服务
app.run(host="0.0.0.0", port=8000)
```
