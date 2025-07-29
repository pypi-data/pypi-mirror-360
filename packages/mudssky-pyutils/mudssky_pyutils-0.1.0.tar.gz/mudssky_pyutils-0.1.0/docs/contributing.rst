贡献指南
========

感谢您对 pyutils 项目的关注！我们欢迎各种形式的贡献，包括但不限于：

* 报告 bug
* 提出新功能建议
* 改进文档
* 提交代码修复
* 添加新功能
* 优化性能

开发环境设置
------------

推荐使用 uv 进行开发环境管理：

1. **克隆仓库**::

    git clone https://github.com/your-username/pyutils.git
    cd pyutils

2. **安装 uv** （如果尚未安装）::

    # Windows
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    # macOS/Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh

3. **设置开发环境**::

    uv sync --all-extras --dev

4. **安装 pre-commit 钩子**::

    uv run pre-commit install
    uv run pre-commit install --hook-type commit-msg

5. **验证环境**::

    uv run pytest tests/
    uv run ruff check src/
    uv run mypy src/

开发工作流
----------

我们使用现代化的开发工具链来确保代码质量：

代码质量检查
~~~~~~~~~~~~

.. code-block:: bash

    # 代码格式化
    uv run ruff format src/ tests/
    
    # 代码检查和自动修复
    uv run ruff check --fix src/ tests/
    
    # 类型检查
    uv run mypy src/
    
    # 安全检查
    uv run bandit -r src/

测试
~~~~

.. code-block:: bash

    # 运行所有测试
    uv run pytest tests/
    
    # 运行测试并生成覆盖率报告
    uv run pytest --cov=src --cov-report=html --cov-report=term
    
    # 运行特定测试
    uv run pytest tests/test_string.py
    
    # 运行性能基准测试
    uv run python benchmark.py

使用 Makefile
~~~~~~~~~~~~~

项目提供了 Makefile 来简化常用命令：

.. code-block:: bash

    # 查看所有可用命令
    make help
    
    # 快速检查（格式化 + 检查 + 类型检查）
    make quick-check
    
    # 运行所有 CI 检查
    make ci
    
    # 设置开发环境
    make dev-setup

提交代码
--------

分支策略
~~~~~~~~

* ``main`` - 主分支，包含稳定的发布版本
* ``develop`` - 开发分支，包含最新的开发代码
* ``feature/*`` - 功能分支
* ``bugfix/*`` - 修复分支
* ``hotfix/*`` - 紧急修复分支

提交流程
~~~~~~~~

1. **创建功能分支**::

    git checkout -b feature/your-feature-name

2. **进行开发**，确保遵循代码规范

3. **运行测试和检查**::

    make quick-check
    uv run pytest tests/

4. **提交代码**::

    git add .
    git commit -m "feat: add your feature description"

5. **推送分支**::

    git push origin feature/your-feature-name

6. **创建 Pull Request**

提交信息规范
~~~~~~~~~~~~

我们使用 `Conventional Commits <https://www.conventionalcommits.org/>`_ 规范：

.. code-block::

    <type>[optional scope]: <description>
    
    [optional body]
    
    [optional footer(s)]

类型说明：

* ``feat``: 新功能
* ``fix``: 修复 bug
* ``docs``: 文档更新
* ``style``: 代码格式化（不影响功能）
* ``refactor``: 重构代码
* ``perf``: 性能优化
* ``test``: 添加或修改测试
* ``chore``: 构建过程或辅助工具的变动

示例：

.. code-block::

    feat(string): add fuzzy matching function
    
    fix(array): handle empty array in chunk function
    
    docs: update installation guide for uv
    
    test(math): add tests for clamp function edge cases

代码规范
--------

代码风格
~~~~~~~~

* 使用 Ruff 进行代码格式化和检查
* 行长度限制为 88 字符
* 使用 Google 风格的 docstring
* 遵循 PEP 8 规范

类型注解
~~~~~~~~

* 所有公共函数必须有完整的类型注解
* 使用 ``typing`` 模块的类型提示
* 复杂类型使用 ``TypeVar`` 和 ``Generic``

示例：

.. code-block:: python

    from typing import List, Optional, TypeVar, Union
    
    T = TypeVar('T')
    
    def chunk(array: List[T], size: int) -> List[List[T]]:
        """将数组分割成指定大小的块。
        
        Args:
            array: 要分割的数组
            size: 每块的大小
            
        Returns:
            分割后的数组列表
            
        Raises:
            ValueError: 当 size 小于等于 0 时
            
        Examples:
            >>> chunk([1, 2, 3, 4, 5], 2)
            [[1, 2], [3, 4], [5]]
        """
        if size <= 0:
            raise ValueError("Size must be positive")
        
        return [array[i:i + size] for i in range(0, len(array), size)]

文档规范
~~~~~~~~

* 使用 Google 风格的 docstring
* 包含参数说明、返回值说明和示例
* 重要函数需要包含异常说明
* 复杂算法需要说明时间复杂度

测试规范
--------

测试结构
~~~~~~~~

* 每个模块对应一个测试文件：``test_<module_name>.py``
* 使用 pytest 框架
* 测试函数命名：``test_<function_name>_<scenario>``
* 使用参数化测试处理多种输入情况

示例：

.. code-block:: python

    import pytest
    from pyutils.array import chunk
    
    class TestChunk:
        """测试 chunk 函数。"""
        
        def test_chunk_normal_case(self):
            """测试正常情况。"""
            result = chunk([1, 2, 3, 4, 5], 2)
            assert result == [[1, 2], [3, 4], [5]]
        
        def test_chunk_empty_array(self):
            """测试空数组。"""
            result = chunk([], 2)
            assert result == []
        
        @pytest.mark.parametrize("array,size,expected", [
            ([1, 2, 3, 4], 2, [[1, 2], [3, 4]]),
            ([1, 2, 3, 4, 5], 3, [[1, 2, 3], [4, 5]]),
            ([1], 1, [[1]]),
        ])
        def test_chunk_parametrized(self, array, size, expected):
            """参数化测试。"""
            assert chunk(array, size) == expected
        
        def test_chunk_invalid_size(self):
            """测试无效的 size 参数。"""
            with pytest.raises(ValueError, match="Size must be positive"):
                chunk([1, 2, 3], 0)

覆盖率要求
~~~~~~~~~~

* 新代码的测试覆盖率应达到 90% 以上
* 关键功能必须有完整的测试覆盖
* 边界条件和异常情况必须测试

性能测试
~~~~~~~~

对于性能敏感的功能，需要添加基准测试：

.. code-block:: python

    def test_chunk_performance(benchmark):
        """测试 chunk 函数性能。"""
        large_array = list(range(10000))
        result = benchmark(chunk, large_array, 100)
        assert len(result) == 100

文档贡献
--------

文档类型
~~~~~~~~

* API 文档：自动从 docstring 生成
* 用户指南：手写的教程和示例
* 开发文档：贡献指南、架构说明等

构建文档
~~~~~~~~

.. code-block:: bash

    # 构建 HTML 文档
    make docs
    
    # 或者直接使用 Sphinx
    cd docs
    uv run sphinx-build -b html . _build/html

发布流程
--------

版本管理
~~~~~~~~

* 使用语义化版本号：``MAJOR.MINOR.PATCH``
* 在 ``pyproject.toml`` 中更新版本号
* 创建 git tag：``git tag v1.2.3``

自动发布
~~~~~~~~

项目配置了 GitHub Actions 自动发布：

1. 推送 tag 到 GitHub
2. GitHub Actions 自动构建和测试
3. 自动发布到 PyPI

手动发布
~~~~~~~~

.. code-block:: bash

    # 构建发布包
    make build
    
    # 发布到 PyPI
    make release

问题报告
--------

报告 Bug
~~~~~~~~~

请在 GitHub Issues 中报告 bug，包含以下信息：

* Python 版本
* pyutils 版本
* 操作系统
* 重现步骤
* 期望行为
* 实际行为
* 错误信息（如有）

功能请求
~~~~~~~~

提出新功能建议时，请说明：

* 功能描述
* 使用场景
* 预期 API 设计
* 是否愿意实现

获取帮助
--------

如果您在贡献过程中遇到问题，可以：

* 查看现有的 Issues 和 Pull Requests
* 在 GitHub Discussions 中提问
* 发送邮件给维护者

感谢您的贡献！🎉