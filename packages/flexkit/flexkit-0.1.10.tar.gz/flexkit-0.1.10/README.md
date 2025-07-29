# flexkit库

依赖库

```
fastapi
favicon
matplotlib
numpy
opencv-python
pandas>=2.2.3
psycopg2>=2.9.10
pymongo>=4.13.2
pypinyin>=0.54.0
uvicorn>=0.34.2
```

当前版本：0.1.7

- alg算法模块
- dbc数据库模块
- err错误处理模块
- fapi http服务器模块
- mondb mongodb模块
- tools
    - downloadfile文件下载
    - get_favicon_url图标链接获取模块
    - pinyin汉字拼音模块
    - res响应模块
    - response返回返回模块
    - result结果信息模块
- vali数据验证模块
- vdm基于pydantic的数据验证模块
- vic配置信息模块

# 更新日志

## 2025-07-06

- 修改了MongoDB中ObjectID在文档转换时不兼容的问题

## 2025-07-04

- 完善了mondb模块，添加MongoDB类和DataModel类用于MongoDB和pydantic的结合使用
- 添加了ResModel代替Response类
- 修复了DataModel的id属性的ObjectId转换问题

## 2025-06-18

- 删除重复的Result和Response模块，改为从flexkit.tools导入
- 移动res模块到flexkit.tools中
- 添加了mondb模块，用于简化操作MongoDB数据库
- 修复了vdm中引入未知函数的问题
- 修复了tools部分模块引用旧result的模块的问题

## 2025-05-24

- 为vali模块validator_func添加not_empty()方法
- 修改vali模块processor_func的to_datetime()方法，当传入空值，则返回当前时间

## 2025-05-24

- 添加了pinyin、response、result模块
- 添加了vali数据验证模块
