快速开始
========

本指南将帮助您快速上手 pyutils 库的主要功能。

基本导入
--------

pyutils 采用模块化设计，您可以按需导入所需的功能：

.. code-block:: python

    # 导入特定模块
    from pyutils import array, string, math
    
    # 或者导入整个库
    import pyutils
    
    # 导入特定函数
    from pyutils.string import camel_case, snake_case
    from pyutils.array import chunk, unique

数组操作
--------

pyutils 提供了丰富的数组和列表操作工具：

.. code-block:: python

    from pyutils import array
    
    # 将数组分块
    data = [1, 2, 3, 4, 5, 6, 7, 8]
    chunks = array.chunk(data, 3)
    print(chunks)  # [[1, 2, 3], [4, 5, 6], [7, 8]]
    
    # 去重
    numbers = [1, 2, 2, 3, 3, 3, 4]
    unique_numbers = array.unique(numbers)
    print(unique_numbers)  # [1, 2, 3, 4]
    
    # 随机打乱
    shuffled = array.shuffle([1, 2, 3, 4, 5])
    print(shuffled)  # [3, 1, 5, 2, 4] (随机结果)
    
    # 数组差集
    diff = array.diff([1, 2, 3, 4], [2, 3])
    print(diff)  # [1, 4]

字符串处理
----------

强大的字符串处理和格式化工具：

.. code-block:: python

    from pyutils import string
    
    # 命名风格转换
    snake_str = "hello_world_example"
    camel_str = string.camel_case(snake_str)
    print(camel_str)  # "helloWorldExample"
    
    # 反向转换
    back_to_snake = string.snake_case(camel_str)
    print(back_to_snake)  # "hello_world_example"
    
    # URL 友好的 slug
    title = "Hello World! 这是一个测试 123"
    slug = string.slugify(title)
    print(slug)  # "hello-world-123"
    
    # 模糊匹配
    similarity = string.fuzzy_match("hello", "helo")
    print(similarity)  # 0.8 (相似度)
    
    # 生成 UUID
    uuid = string.generate_uuid()
    print(uuid)  # "550e8400-e29b-41d4-a716-446655440000"

数学计算
--------

实用的数学函数和统计工具：

.. code-block:: python

    from pyutils import math
    
    # 数值限制
    value = math.clamp(150, 0, 100)  # 限制在 0-100 之间
    print(value)  # 100
    
    # 线性插值
    result = math.lerp(0, 100, 0.5)  # 0 到 100 的中点
    print(result)  # 50.0
    
    # 数值归一化
    normalized = math.normalize(75, 0, 100)  # 将 75 归一化到 0-1
    print(normalized)  # 0.75
    
    # 角度转换
    radians = math.deg_to_rad(180)
    print(radians)  # 3.141592653589793
    
    degrees = math.rad_to_deg(3.14159)
    print(degrees)  # 179.99954498897746

对象操作
--------

对象检查和操作工具：

.. code-block:: python

    from pyutils import object as obj_utils
    
    # 深拷贝
    original = {"a": [1, 2, 3], "b": {"c": 4}}
    copied = obj_utils.deep_copy(original)
    
    # 对象合并
    obj1 = {"a": 1, "b": 2}
    obj2 = {"b": 3, "c": 4}
    merged = obj_utils.merge(obj1, obj2)
    print(merged)  # {"a": 1, "b": 3, "c": 4}
    
    # 获取嵌套属性
    data = {"user": {"profile": {"name": "Alice"}}}
    name = obj_utils.get_nested(data, "user.profile.name")
    print(name)  # "Alice"
    
    # 检查对象类型
    is_dict = obj_utils.is_dict({"key": "value"})
    print(is_dict)  # True

函数式编程
----------

函数式编程工具和装饰器：

.. code-block:: python

    from pyutils import function
    
    # 函数组合
    def add_one(x):
        return x + 1
    
    def multiply_two(x):
        return x * 2
    
    composed = function.compose(multiply_two, add_one)
    result = composed(5)  # (5 + 1) * 2
    print(result)  # 12
    
    # 偏函数应用
    def greet(greeting, name):
        return f"{greeting}, {name}!"
    
    say_hello = function.partial(greet, "Hello")
    message = say_hello("Alice")
    print(message)  # "Hello, Alice!"
    
    # 缓存装饰器
    @function.memoize
    def fibonacci(n):
        if n < 2:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    
    print(fibonacci(10))  # 55 (缓存加速)

异步编程
--------

异步编程辅助工具：

.. code-block:: python

    import asyncio
    from pyutils import async_utils
    
    # 异步任务批量执行
    async def fetch_data(url):
        # 模拟异步请求
        await asyncio.sleep(0.1)
        return f"Data from {url}"
    
    async def main():
        urls = ["url1", "url2", "url3"]
        tasks = [fetch_data(url) for url in urls]
        
        # 并发执行所有任务
        results = await async_utils.gather_with_concurrency(tasks, limit=2)
        print(results)
        
        # 超时控制
        try:
            result = await async_utils.timeout(fetch_data("slow_url"), 0.05)
        except asyncio.TimeoutError:
            print("请求超时")
    
    # 运行异步代码
    asyncio.run(main())

实际应用示例
------------

数据处理管道
~~~~~~~~~~~~

.. code-block:: python

    from pyutils import array, string, math
    
    # 处理用户数据
    users = [
        {"name": "john_doe", "age": 25, "score": 85},
        {"name": "jane_smith", "age": 30, "score": 92},
        {"name": "bob_wilson", "age": 35, "score": 78},
    ]
    
    # 数据转换和处理
    processed_users = []
    for user in users:
        processed_user = {
            "displayName": string.camel_case(user["name"]),
            "age": user["age"],
            "normalizedScore": math.normalize(user["score"], 0, 100),
            "grade": "A" if user["score"] >= 90 else "B" if user["score"] >= 80 else "C"
        }
        processed_users.append(processed_user)
    
    # 按分数分组
    score_groups = array.chunk(sorted(processed_users, key=lambda x: x["normalizedScore"]), 2)
    print(score_groups)

配置管理
~~~~~~~~

.. code-block:: python

    from pyutils import object as obj_utils, string
    
    # 默认配置
    default_config = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "myapp"
        },
        "cache": {
            "enabled": True,
            "ttl": 3600
        }
    }
    
    # 用户配置
    user_config = {
        "database": {
            "host": "prod-server",
            "password": "secret"
        },
        "debug": True
    }
    
    # 合并配置
    final_config = obj_utils.deep_merge(default_config, user_config)
    
    # 获取配置值
    db_host = obj_utils.get_nested(final_config, "database.host")
    print(db_host)  # "prod-server"

下一步
------

现在您已经了解了 pyutils 的基本用法，可以：

1. 查看 :doc:`modules` 了解完整的 API 参考
2. 阅读 :doc:`contributing` 了解如何贡献代码
3. 查看 GitHub 仓库中的更多示例
4. 运行性能基准测试：``uv run python benchmark.py``

如果您有任何问题或建议，欢迎在 GitHub 上创建 issue 或提交 pull request！