变更日志
========

本文档记录了 pyutils 项目的所有重要变更。

格式基于 `Keep a Changelog <https://keepachangelog.com/zh-CN/1.0.0/>`_，
并且本项目遵循 `语义化版本 <https://semver.org/lang/zh-CN/>`_。

[未发布] - TBD
--------------

新增
~~~~
* 完整的 uv 包管理器支持
* 现代化的开发工具链（Ruff、MyPy、pre-commit）
* GitHub Actions CI/CD 流水线
* 性能基准测试框架
* 完整的 Sphinx 文档系统
* Makefile 简化开发命令
* 代码质量增强建议文档

改进
~~~~
* 更新 README.rst 包含详细的 uv 使用指南
* 优化 pyproject.toml 配置
* 增强测试覆盖率配置
* 改进类型注解支持

修复
~~~~
* 修复异步测试支持问题
* 清理重复的依赖配置

[1.0.0] - 2024-01-XX
--------------------

新增
~~~~
* **array 模块**: 数组和列表操作工具
  
  * ``chunk()``: 将数组分割成指定大小的块
  * ``unique()``: 数组去重
  * ``shuffle()``: 随机打乱数组
  * ``diff()``: 计算数组差集
  * ``flatten()``: 扁平化嵌套数组
  * ``compact()``: 移除数组中的假值

* **string 模块**: 字符串处理和格式化工具
  
  * ``camel_case()``: 转换为驼峰命名
  * ``snake_case()``: 转换为下划线命名
  * ``kebab_case()``: 转换为短横线命名
  * ``slugify()``: 生成 URL 友好的字符串
  * ``fuzzy_match()``: 模糊字符串匹配
  * ``generate_uuid()``: 生成 UUID
  * ``truncate()``: 截断字符串
  * ``pad_start()`` / ``pad_end()``: 字符串填充

* **math 模块**: 数学计算和统计函数
  
  * ``clamp()``: 数值限制
  * ``lerp()``: 线性插值
  * ``normalize()``: 数值归一化
  * ``deg_to_rad()`` / ``rad_to_deg()``: 角度转换
  * ``is_prime()``: 质数检查
  * ``gcd()`` / ``lcm()``: 最大公约数和最小公倍数
  * ``factorial()``: 阶乘计算

* **object 模块**: 对象操作和反射工具
  
  * ``deep_copy()``: 深拷贝对象
  * ``merge()``: 对象合并
  * ``get_nested()``: 获取嵌套属性
  * ``set_nested()``: 设置嵌套属性
  * ``is_dict()`` / ``is_list()`` / ``is_string()``: 类型检查
  * ``pick()`` / ``omit()``: 对象属性选择和排除

* **function 模块**: 函数式编程工具
  
  * ``compose()``: 函数组合
  * ``partial()``: 偏函数应用
  * ``memoize()``: 函数缓存装饰器
  * ``debounce()``: 防抖装饰器
  * ``throttle()``: 节流装饰器
  * ``retry()``: 重试装饰器

* **async_utils 模块**: 异步编程辅助工具
  
  * ``gather_with_concurrency()``: 限制并发数的任务执行
  * ``timeout()``: 异步超时控制
  * ``retry_async()``: 异步重试
  * ``run_in_executor()``: 在线程池中运行同步函数

* **bytes 模块**: 字节操作工具
  
  * ``to_hex()``: 转换为十六进制字符串
  * ``from_hex()``: 从十六进制字符串转换
  * ``encode_base64()`` / ``decode_base64()``: Base64 编解码
  * ``compress()`` / ``decompress()``: 数据压缩

* **cache_utils 模块**: 缓存工具
  
  * ``LRUCache``: LRU 缓存实现
  * ``TTLCache``: 带过期时间的缓存
  * ``cache_result()``: 结果缓存装饰器

* **data_utils 模块**: 数据处理工具
  
  * ``flatten_dict()``: 扁平化字典
  * ``unflatten_dict()``: 反扁平化字典
  * ``group_by()``: 数据分组
  * ``sort_by()``: 多字段排序
  * ``filter_by()``: 条件过滤

* **file_utils 模块**: 文件操作工具
  
  * ``ensure_dir()``: 确保目录存在
  * ``copy_file()`` / ``move_file()``: 文件复制和移动
  * ``get_file_size()``: 获取文件大小
  * ``get_file_hash()``: 计算文件哈希
  * ``read_json()`` / ``write_json()``: JSON 文件操作

* **network_utils 模块**: 网络工具
  
  * ``is_valid_ip()``: IP 地址验证
  * ``is_valid_url()``: URL 验证
  * ``get_domain()``: 提取域名
  * ``download_file()``: 文件下载

* **system_utils 模块**: 系统工具
  
  * ``get_platform()``: 获取平台信息
  * ``get_memory_usage()``: 获取内存使用情况
  * ``run_command()``: 执行系统命令
  * ``get_env_var()``: 获取环境变量

* **time_utils 模块**: 时间工具
  
  * ``format_duration()``: 格式化时间间隔
  * ``parse_duration()``: 解析时间间隔
  * ``get_timestamp()``: 获取时间戳
  * ``sleep_until()``: 睡眠到指定时间

* **validation_utils 模块**: 数据验证工具
  
  * ``is_email()``: 邮箱验证
  * ``is_phone()``: 电话号码验证
  * ``is_credit_card()``: 信用卡号验证
  * ``validate_schema()``: JSON Schema 验证

技术改进
~~~~~~~~
* 完整的类型注解支持
* 高覆盖率的测试套件（90%+）
* 性能优化和基准测试
* 详细的文档和示例
* 模块化设计，支持按需导入

[0.1.0] - 2023-XX-XX
--------------------

新增
~~~~
* 项目初始化
* 基础项目结构
* 初始的工具函数集合

版本说明
--------

版本号格式
~~~~~~~~~~

我们使用语义化版本号 ``MAJOR.MINOR.PATCH``：

* **MAJOR**: 不兼容的 API 变更
* **MINOR**: 向后兼容的功能新增
* **PATCH**: 向后兼容的问题修复

变更类型
~~~~~~~~

* **新增**: 新功能
* **改进**: 对现有功能的改进
* **修复**: 问题修复
* **移除**: 移除的功能
* **弃用**: 即将移除的功能
* **安全**: 安全相关的修复

迁移指南
--------

从 0.x 到 1.0
~~~~~~~~~~~~~~

1.0 版本是一个重大更新，包含了许多破坏性变更：

* **模块重组**: 函数按功能重新组织到不同模块
* **API 变更**: 一些函数的参数和返回值有变化
* **类型注解**: 添加了完整的类型注解
* **性能优化**: 重写了部分算法以提高性能

详细的迁移指南请参考 `迁移文档 <migration.html>`_。

贡献者
------

感谢所有为 pyutils 项目做出贡献的开发者！

* 项目维护者和核心贡献者
* 社区贡献者
* 问题报告者
* 文档改进者

完整的贡献者列表请查看 `AUTHORS.rst <../AUTHORS.rst>`_。