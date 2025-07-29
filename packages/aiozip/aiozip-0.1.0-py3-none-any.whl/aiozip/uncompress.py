import asyncio
import os
import tarfile
from concurrent.futures import ThreadPoolExecutor

from .exceptions import UnsupportedFormatError, CorruptArchiveError, ArchiveNotFoundError, AiozipError
from .zip_reader import AsyncZipExtractor

_executor = ThreadPoolExecutor(max_workers=os.cpu_count())


async def uncompress(source_path: str, dest_path: str = "."):
    """
    异步解压一个归档文件到指定目录。
    自动检测文件格式 (.zip, .tar, .tar.gz, .tar.bz2) 并调用相应的解压器。

    :param source_path: 归档文件的路径。
    :param dest_path: 解压目标目录的路径。
    :raises ArchiveNotFoundError: 如果源文件不存在。
    :raises UnsupportedFormatError: 如果文件格式不被支持。
    :raises CorruptArchiveError: 如果归档文件损坏。
    """
    if not os.path.exists(source_path):
        raise ArchiveNotFoundError(f"归档文件未找到: {source_path}")

    source_path_lower = source_path.lower()

    if source_path_lower.endswith('.zip'):
        async with AsyncZipExtractor(source_path) as extractor:
            await extractor.extractall(dest_path)
    elif any(source_path_lower.endswith(ext) for ext in ['.tar', '.gz', '.tar.gz', '.bz2', '.tar.bz2']):
        await _untar_threaded(source_path, dest_path)
    else:
        raise UnsupportedFormatError(f"不支持的归档格式: {source_path}")


def _untar_sync(source_path: str, dest_path: str):
    """同步的 tar 解压函数，将在线程池中执行"""
    try:
        with tarfile.open(source_path, 'r:*') as tar_ref:
            tar_ref.extractall(dest_path)
    except tarfile.ReadError as e:
        raise CorruptArchiveError(f"TAR 文件解压失败，文件可能已损坏: {e}") from e
    except Exception as e:
        raise AiozipError(f"An unexpected error occurred during TAR extraction: {e}") from e


async def _untar_threaded(source_path: str, dest_path: str):
    """将同步的 tar 解压操作放入线程池中执行"""
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        _executor,
        _untar_sync,
        source_path,
        dest_path
    )
