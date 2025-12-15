# 测试文档

## 测试目录结构

```
tests/
├── __init__.py                    # 测试包初始化
├── conftest.py                    # pytest 固件和配置
├── test_config.py                 # 配置系统测试
├── test_database_operations.py   # 数据库操作测试
└── README.md                      # 本文档
```

## 运行测试

### 安装测试依赖

```bash
pip install -r requirements-dev.txt
```

### 运行所有测试

```bash
pytest
```

### 运行特定测试文件

```bash
pytest tests/test_config.py
pytest tests/test_database_operations.py
```

### 运行特定测试

```bash
pytest tests/test_config.py::test_get_settings
```

### 按标记运行测试

```bash
# 只运行单元测试（不需要数据库）
pytest -m unit

# 只运行集成测试（需要数据库）
pytest -m integration
```

### 查看测试覆盖率

```bash
pytest --cov=. --cov-report=html
```

查看覆盖率报告：
```bash
# 打开 htmlcov/index.html 查看详细报告
```

## 测试说明

### 单元测试 (unit)
- 不需要外部依赖（数据库等）
- 测试配置加载、数据模型等
- 执行速度快

### 集成测试 (integration)
- 需要真实的数据库连接
- 测试数据库操作功能
- 使用实际数据库进行测试

### 注意事项

1. **数据库配置**：集成测试使用真实的数据库连接，确保 `.env` 文件已正确配置
2. **测试数据**：测试使用实际数据库中的表（如 `ll_recharge_success`），不会修改数据
3. **只读操作**：所有测试只进行只读操作，不会写入或修改数据
4. **测试隔离**：每个测试函数独立运行，互不影响

## 添加新测试

1. 在 `tests/` 目录下创建 `test_*.py` 文件
2. 使用 pytest 的固件（fixtures）来获取测试依赖
3. 使用适当的标记（`@pytest.mark.unit` 或 `@pytest.mark.integration`）
4. 遵循测试命名约定：`test_<功能名>`

示例：

```python
import pytest

@pytest.mark.integration
def test_my_feature(db_ops, sample_database):
    """测试我的功能"""
    result = db_ops.my_feature(sample_database)
    assert result is not None
```
