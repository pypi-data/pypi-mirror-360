# 使用说明

## 快速运行

```bash
# 使用管道输入配置文件路径
cat path.txt | uv run python run.py

# 或者直接传递配置文件
uv run python run.py test.json
```

## 缓存控制

在 `run.py` 文件第14行可以控制缓存设置：

```python
# 硬编码缓存配置
CACHE_ENABLED = False  # 修改此处控制是否启用下载缓存
```

### 配置说明
- `CACHE_ENABLED = True`: 启用下载缓存，重复运行时会使用缓存文件
- `CACHE_ENABLED = False`: 禁用缓存，每次都重新下载资源

## 实现方式

1. `run.py` 将硬编码的 `CACHE_ENABLED` 作为 `--cache-enabled` 命令行参数
2. `main()` 函数解析 `--cache-enabled` 参数
3. `main()` 函数将缓存参数传递给 `AeroSpotReportGenerator`
4. `AeroSpotReportGenerator` 将缓存参数传递给 `ResourceManager`

## 优势

- ✅ **简单直接**: 只需修改一行代码
- ✅ **标准方式**: 通过命令行参数传递，符合标准做法
- ✅ **职责分离**: run.py负责设置参数，main负责解析参数
- ✅ **无需打包**: 修改后直接生效
- ✅ **保持兼容**: 不影响直接调用main()的方式