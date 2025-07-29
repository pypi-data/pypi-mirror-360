安装指南
========

本页面介绍如何安装和配置 pyutils。

系统要求
--------

* Python 3.8 或更高版本
* 支持的操作系统：Windows、macOS、Linux

推荐安装方式 (uv)
------------------

我们强烈推荐使用 `uv <https://docs.astral.sh/uv/>`_ 作为包管理器，它提供了更快的安装速度和更好的依赖管理。

安装 uv
~~~~~~~~

**Windows (PowerShell)**::

    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

**macOS/Linux**::

    curl -LsSf https://astral.sh/uv/install.sh | sh

**使用 pip**::

    pip install uv

安装 pyutils
~~~~~~~~~~~~~

使用 uv 安装 pyutils::

    uv add pyutils

或者在新项目中::

    uv init my-project
    cd my-project
    uv add pyutils

传统安装方式 (pip)
------------------

如果您更喜欢使用传统的 pip，也可以这样安装：

从 PyPI 安装
~~~~~~~~~~~~

::

    pip install pyutils

从源码安装
~~~~~~~~~~

::

    git clone https://github.com/your-username/pyutils.git
    cd pyutils
    pip install -e .

开发环境安装
------------

如果您想为 pyutils 贡献代码，需要安装开发依赖：

使用 uv (推荐)
~~~~~~~~~~~~~~

::

    git clone https://github.com/your-username/pyutils.git
    cd pyutils
    uv sync --all-extras --dev

使用 pip
~~~~~~~~

::

    git clone https://github.com/your-username/pyutils.git
    cd pyutils
    pip install -e ".[dev]"

验证安装
--------

安装完成后，您可以验证 pyutils 是否正确安装：

::

    python -c "import pyutils; print(pyutils.__version__)"

或者运行一个简单的测试：

::

    python -c "from pyutils import string; print(string.camel_case('hello_world'))"

应该输出：``helloWorld``

可选依赖
--------

pyutils 支持一些可选的功能，需要额外的依赖：

* **async**: 异步功能支持
* **cache**: 高级缓存功能
* **network**: 网络工具
* **validation**: 数据验证工具

安装所有可选依赖：

使用 uv::

    uv add "pyutils[all]"

使用 pip::

    pip install "pyutils[all]"

或者只安装特定功能：

::

    uv add "pyutils[async,cache]"
    # 或
    pip install "pyutils[async,cache]"

故障排除
--------

常见问题
~~~~~~~~

**问题**: 导入错误 ``ModuleNotFoundError: No module named 'pyutils'``

**解决方案**: 

1. 确认 pyutils 已正确安装：``pip list | grep pyutils``
2. 检查 Python 环境是否正确
3. 如果使用虚拟环境，确保已激活

**问题**: 版本冲突

**解决方案**: 

1. 使用 uv 管理依赖可以避免大多数版本冲突
2. 创建新的虚拟环境：``uv venv && uv sync``
3. 更新到最新版本：``uv add pyutils@latest``

**问题**: 性能问题

**解决方案**: 

1. 确保使用最新版本的 pyutils
2. 检查是否安装了可选的性能优化依赖
3. 参考性能基准测试：``uv run python benchmark.py``

获取帮助
--------

如果您遇到安装问题，可以：

1. 查看 `GitHub Issues <https://github.com/your-username/pyutils/issues>`_
2. 创建新的 issue 报告问题
3. 查看 :doc:`contributing` 了解如何贡献代码