=======
pyutils
=======


.. image:: https://img.shields.io/pypi/v/pyutils.svg
        :target: https://pypi.python.org/pypi/pyutils

.. image:: https://img.shields.io/travis/mudssky/pyutils.svg
        :target: https://travis-ci.com/mudssky/pyutils

.. image:: https://readthedocs.org/projects/pyutils/badge/?version=latest
        :target: https://pyutils.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status


Python通用工具库 - 提供丰富的实用函数和工具类
==============================================

pyutils是一个功能丰富的Python工具库，提供了大量常用的实用函数，涵盖数组操作、字符串处理、数学计算、对象操作、函数工具、异步编程和字节处理等多个领域。

* 免费开源: MIT许可证
* 文档地址: https://pyutils.readthedocs.io
* 支持Python 3.6+


快速开始
--------

**安装方式**

使用pip安装（传统方式）::

    pip install pyutils

使用uv安装（推荐，更快更现代）::

    # 安装uv
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

    # 使用uv安装pyutils
    uv add pyutils


使用uv进行开发
----------------

`uv` 是一个高性能的Python包管理器，比传统pip快10-100倍，提供统一的项目管理体验。本项目已完全迁移到uv包管理器。

**安装 uv**

.. code-block:: shell

   # Windows (PowerShell)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

**项目环境设置**

.. code-block:: shell

   # 克隆项目
   git clone https://github.com/mudssky/pyutils.git
   cd pyutils

   # 同步项目环境（自动创建虚拟环境并安装所有依赖）
   uv sync --group dev

**常用开发命令**

.. code-block:: shell

   # 运行测试
   uv run pytest tests/

   # 代码质量检查
   uv run ruff check src/
   uv run mypy src/

   # 添加新依赖
   uv add package-name              # 生产依赖
   uv add --group dev package-name  # 开发依赖

   # 运行Python脚本
   uv run python script.py

   # 更新依赖
   uv lock --upgrade

**uv的优势**

* ⚡ **极快速度**: 依赖解析和安装比pip快10-100倍
* 🔒 **版本锁定**: uv.lock文件确保依赖版本一致性
* 🛠️ **统一管理**: 项目、依赖、环境一体化管理
* 🐍 **Python版本管理**: 内置多版本Python支持
* 🔄 **自动化**: 无需手动管理虚拟环境
* 📦 **现代标准**: 完全兼容PEP标准


基本使用::

    from pyutils import array, string, math

    # 数组操作
    result = array.chunk([1, 2, 3, 4, 5], 2)  # [[1, 2], [3, 4], [5]]

    # 字符串处理
    camel = string.camel_case("hello_world")  # "helloWorld"

    # 数学计算
    random_num = math.random_int(1, 100)  # 1-100之间的随机整数


主要功能模块
============

**数组工具 (array)**

* ``chunk`` - 将数组分块
* ``unique`` - 数组去重
* ``shuffle`` - 数组随机排序
* ``diff`` - 数组差集
* ``fork`` - 数组分组
* ``zip_object`` - 创建对象映射
* 更多数组操作函数...

**字符串工具 (string)**

* ``camel_case`` - 转换为驼峰命名
* ``snake_case`` - 转换为下划线命名
* ``pascal_case`` - 转换为帕斯卡命名
* ``slugify`` - 生成URL友好字符串
* ``fuzzy_match`` - 模糊匹配
* ``generate_uuid`` - 生成UUID
* 更多字符串处理函数...

**数学工具 (math)**

* ``clamp`` - 数值限制
* ``lerp`` - 线性插值
* ``normalize`` - 数值归一化
* ``fibonacci`` - 斐波那契数列
* ``is_prime`` - 质数判断
* ``gcd/lcm`` - 最大公约数/最小公倍数
* 更多数学计算函数...

**对象工具 (object)**

* ``pick/omit`` - 对象属性选择/排除
* ``merge`` - 深度合并对象
* ``flatten_dict`` - 扁平化字典
* ``get_nested_value`` - 获取嵌套值
* ``deep_copy`` - 深度复制
* 更多对象操作函数...

**函数工具 (function)**

* ``memoize`` - 函数记忆化
* ``debounce`` - 防抖装饰器
* ``throttle`` - 节流装饰器
* ``with_retry`` - 重试装饰器
* ``once`` - 单次执行装饰器
* 更多函数增强工具...

**异步工具 (async_utils)**

* ``sleep_async`` - 异步延迟
* ``timeout`` - 超时控制
* ``race`` - 竞态执行
* ``gather_with_concurrency`` - 并发控制
* ``map_async`` - 异步映射
* ``batch_process`` - 批量处理
* 更多异步编程工具...

**字节工具 (bytes)**

* ``Bytes`` - 字节处理类
* ``humanize_bytes`` - 人性化字节显示
* ``parse_bytes`` - 字节字符串解析
* 字节单位转换工具


使用示例
--------

**数组操作示例**::

    from pyutils import array

    # 数组分块
    chunks = array.chunk([1, 2, 3, 4, 5, 6], 2)
    # 结果: [[1, 2], [3, 4], [5, 6]]

    # 数组去重并保持顺序
    unique_items = array.unique([1, 2, 2, 3, 1, 4])
    # 结果: [1, 2, 3, 4]

    # 根据条件分组
    evens, odds = array.fork([1, 2, 3, 4, 5], lambda x: x % 2 == 0)
    # evens: [2, 4], odds: [1, 3, 5]

**字符串处理示例**::

    from pyutils import string

    # 命名风格转换
    camel = string.camel_case("hello_world_example")  # "helloWorldExample"
    snake = string.snake_case("HelloWorldExample")   # "hello_world_example"
    pascal = string.pascal_case("hello-world")       # "HelloWorld"

    # URL友好字符串
    slug = string.slugify("Hello World! 你好世界")    # "hello-world"

    # 模糊匹配
    score = string.fuzzy_match("hello", "helo")      # 0.8

**异步编程示例**::

    import asyncio
    from pyutils import async_utils

    async def example():
        # 异步延迟
        await async_utils.sleep_async(1.0)

        # 竞态执行，返回最快完成的结果
        async def fast():
            await asyncio.sleep(0.1)
            return "fast"
        async def slow():
            await asyncio.sleep(1.0)
            return "slow"

        result = await async_utils.race(fast(), slow())  # "fast"

        # 带并发限制的异步映射
        async def process(x):
            await asyncio.sleep(0.1)
            return x * 2

        results = await async_utils.map_async(
            process, [1, 2, 3, 4, 5], concurrency=2
        )  # [2, 4, 6, 8, 10]

**函数增强示例**::

    from pyutils.function import memoize, debounce, with_retry

    # 记忆化缓存
    @memoize
    def expensive_calculation(n):
        return sum(range(n))

    # 防抖处理
    @debounce(delay=1.0)
    def search_handler(query):
        print(f"Searching for: {query}")

    # 自动重试
    @with_retry(max_attempts=3, delay=1.0)
    def unreliable_api_call():
        # 可能失败的API调用
        pass


开发和贡献
----------

**环境准备**

克隆项目并设置开发环境::

    git clone https://github.com/mudssky/pyutils.git
    cd pyutils

    # 使用uv同步开发环境（推荐）
    uv sync --group dev

    # 或使用传统pip方式
    pip install -e .[dev]

**开发工作流**

运行测试::

    # 使用uv（推荐）
    uv run pytest tests/

    # 或传统方式
    pytest

    # 运行基础测试
    uv run python test_basic.py

代码质量检查::

    # 使用uv（推荐）
    uv run ruff check src/
    uv run mypy src/

    # 或传统方式
    ruff check .
    mypy .

**添加新功能**

1. 创建功能分支
2. 编写代码和测试
3. 运行完整测试套件::

    uv run pytest tests/ --cov=src/pyutils --cov-report=html

4. 检查代码质量::

    uv run ruff check src/
    uv run mypy src/

5. 提交代码并创建Pull Request

**依赖管理**

添加新依赖::

    # 生产依赖
    uv add package-name

    # 开发依赖
    uv add --group dev package-name

更新依赖::

    uv lock --upgrade


许可证
------

本项目采用MIT许可证 - 详见 `LICENSE <LICENSE>`_ 文件。


致谢
----

本项目使用 Cookiecutter_ 和 `audreyr/cookiecutter-pypackage`_ 项目模板创建。

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
