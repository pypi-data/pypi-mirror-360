# aiozip

[![PyPI version](https://badge.fury.io/py/aiozip.svg)](https://badge.fury.io/py/aiozip)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

**aiozip** 是一个使用原生 `asyncio` 构建的 Python 库，用于高性能地异步处理归档文件。

当前阶段专注于提供一个简单、统一的 API 来解压各种常见的归档格式。

## ✨ 主要特性

* **原生异步**: 对 `.zip` 文件实现了从零开始的原生异步解压，无任何阻塞I/O。
* **统一 API**: 一个简单的 `aiozip.uncompress()` 函数即可处理多种格式。
* **多格式支持**: 目前支持 `.zip`, `.tar`, `.tar.gz`, `.tar.bz2`。
* **轻量级**: 仅依赖 `aiofiles`，保持最小的依赖。
* **现代 & 类型提示**: 使用现代 Python 特性 (Python 3.8+) 并提供完整的类型提示。

## 🚀 安装

```bash
pip install aiozip
```

## 💡 快速开始

使用 `aiozip` 非常简单。下面是一个解压 `.zip` 和 `.tar.gz` 文件的例子：

```python
import asyncio
import aiozip

async def main():
    try:
        print("正在解压 zip 文件...")
        # 假设你有一个 my_archive.zip 文件
        await aiozip.uncompress("my_archive.zip", "./unzipped_files")
        print("解压完成!")

    except aiozip.AiozipError as e:
        print(f"发生了一个错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## API

### `await aiozip.uncompress(source_path, dest_path)`

异步解压一个归档文件。

* **`source_path` (str)**: 源归档文件的路径。
* **`dest_path` (str)**: 解压目标目录的路径。

### 异常

* `aiozip.ArchiveNotFoundError`: 源文件未找到。
* `aiozip.UnsupportedFormatError`: 不支持的归档格式。
* `aiozip.CorruptArchiveError`: 归档文件已损坏。

## 未来计划

* [ ] 实现原生异步的文件**压缩**功能。
* [ ] 支持更多归档格式 (如 .7z, .rar)。
* [ ] 支持对加密归档文件的处理。

## 🤝 贡献

欢迎任何形式的贡献！请随时提交 Pull Request 或创建 Issue。

## 📄 许可证

本项目使用 [MIT 许可证](LICENSE)。