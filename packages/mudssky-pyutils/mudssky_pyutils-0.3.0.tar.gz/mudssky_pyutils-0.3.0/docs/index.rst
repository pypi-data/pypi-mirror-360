pyutils 文档
=============

欢迎使用 pyutils！这是一个功能丰富的 Python 实用工具库，提供了各种常用的函数和类。

.. toctree::
   :maxdepth: 2
   :caption: 内容目录:

   installation
   quickstart
   modules
   contributing
   changelog
   authors
   history
   readme
   usage

特性
----

* 🚀 **高性能**: 优化的算法和数据结构
* 🔧 **易用性**: 简洁直观的 API 设计
* 📦 **模块化**: 按功能组织的模块结构
* 🧪 **测试完备**: 高覆盖率的测试套件
* 📚 **文档完整**: 详细的文档和示例
* 🔒 **类型安全**: 完整的类型注解支持

主要模块
--------

* **array**: 数组和列表操作工具
* **string**: 字符串处理和格式化工具
* **math**: 数学计算和统计函数
* **object**: 对象操作和反射工具
* **function**: 函数式编程工具
* **async_utils**: 异步编程辅助工具

快速开始
--------

使用 uv 安装（推荐）::

    uv add pyutils

或使用 pip 安装::

    pip install pyutils

基本使用示例::

    from pyutils import array, string, math

    # 数组操作
    chunks = array.chunk([1, 2, 3, 4, 5, 6], 2)
    # [[1, 2], [3, 4], [5, 6]]

    # 字符串处理
    camel = string.camel_case("hello_world")
    # "helloWorld"

    # 数学计算
    clamped = math.clamp(150, 0, 100)
    # 100

索引和表格
==========

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
