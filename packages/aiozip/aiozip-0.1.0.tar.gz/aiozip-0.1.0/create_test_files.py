# create_test_files.py

import io
import pathlib
import tarfile
import time
import zipfile

SAMPLES_DIR = pathlib.Path(__file__).parent / "tests" / "sample_files"
ZIP_FILE = SAMPLES_DIR / "test.zip"
TAR_FILE = SAMPLES_DIR / "test.tar.gz"


def main():
    """Creates standard, reliable test archive files."""
    print("--- Creating test files ---")

    # 1. 确保目录存在
    print(f"Ensuring directory exists: {SAMPLES_DIR}")
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    # 2. 创建 ZIP 文件
    print(f"Creating ZIP file: {ZIP_FILE}")
    zip_content = b"hello zip"
    with zipfile.ZipFile(ZIP_FILE, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("hello.txt", zip_content)
    print("ZIP file created successfully.")

    # 3. 创建 TAR.GZ 文件
    print(f"Creating TAR.GZ file: {TAR_FILE}")
    tar_content = b"hello tar"
    # 使用 BytesIO 作为中间对象
    tar_stream = io.BytesIO()
    with tarfile.open(fileobj=tar_stream, mode="w:gz") as tar:
        # 创建一个文件信息对象
        tarinfo = tarfile.TarInfo(name="world.txt")
        tarinfo.size = len(tar_content)
        tarinfo.mtime = int(time.time())  # 设置修改时间
        # 将文件信息和内容添加到 tar 包中
        tar.addfile(tarinfo, io.BytesIO(tar_content))

    # 将内存中的 tar.gz 数据写入到磁盘文件
    with open(TAR_FILE, "wb") as f:
        f.write(tar_stream.getvalue())
    print("TAR.GZ file created successfully.")

    # 4. 创建一个空的纯文本文件用于测试
    (SAMPLES_DIR / "plain.txt").touch()

    print("\n--- All test files created successfully! ---")


if __name__ == "__main__":
    main()
