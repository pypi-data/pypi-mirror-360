import shutil
from pathlib import Path

import pytest

import aiozip

# 将测试标记为异步测试
pytestmark = pytest.mark.asyncio

# 定义测试文件的路径
SAMPLES_DIR = Path(__file__).parent / "sample_files"
ZIP_FILE = SAMPLES_DIR / "test.zip"
TAR_FILE = SAMPLES_DIR / "test.tar.gz"
TXT_FILE = SAMPLES_DIR / "plain.txt"  # 创建一个空的 plain.txt 用于测试错误情况
OUTPUT_DIR = Path(__file__).parent / "test_output"


@pytest.fixture(autouse=True)
def manage_output_dir():
    """一个 pytest fixture, 在每个测试运行前后自动管理测试输出目录"""
    # 在测试前: 如果目录存在，先清空
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    # 创建一个干净的目录
    OUTPUT_DIR.mkdir()

    # yield 关键字让测试运行
    yield

    # 在测试后: 清理目录
    shutil.rmtree(OUTPUT_DIR)


async def test_uncompress_zip_success():
    """测试原生异步解压 ZIP 文件成功"""
    await aiozip.uncompress(str(ZIP_FILE), str(OUTPUT_DIR))

    # 验证结果
    expected_file = OUTPUT_DIR / "hello.txt"
    assert expected_file.exists()
    assert expected_file.read_text() == "hello zip"


async def test_uncompress_tar_success():
    """测试在线程中解压 TAR.GZ 文件成功"""
    await aiozip.uncompress(str(TAR_FILE), str(OUTPUT_DIR))

    # 验证结果
    expected_file = OUTPUT_DIR / "world.txt"
    assert expected_file.exists()
    assert expected_file.read_text() == "hello tar"


async def test_unsupported_format_error():
    """测试当传入不支持的格式时，是否正确抛出异常"""
    # 确保 plain.txt 存在
    if not TXT_FILE.exists():
        TXT_FILE.touch()

    with pytest.raises(aiozip.UnsupportedFormatError):
        await aiozip.uncompress(str(TXT_FILE), str(OUTPUT_DIR))


async def test_archive_not_found_error():
    """测试当文件不存在时，是否正确抛出异常"""
    with pytest.raises(aiozip.ArchiveNotFoundError):
        await aiozip.uncompress("non_existent_file.zip", str(OUTPUT_DIR))
