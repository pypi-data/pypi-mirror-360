import asyncio
import os
import struct
import zlib

import aiofiles

from .exceptions import CorruptArchiveError, ArchiveNotFoundError
from .structs import (
    EndOfCentralDirectory, CentralDirectoryFileHeader,
    END_OF_CENTRAL_DIR_SIGNATURE, CENTRAL_DIR_FILE_HEADER_SIGNATURE, LOCAL_FILE_HEADER_SIGNATURE
)


class AsyncZipExtractor:
    def __init__(self, file_path: str):
        if not os.path.exists(file_path):
            raise ArchiveNotFoundError(f"Archive not found at path: {file_path}")
        self.file_path = file_path
        self._file = None
        self.eocd: EndOfCentralDirectory = None
        self.file_headers: list[CentralDirectoryFileHeader] = []

    async def __aenter__(self):
        self._file = await aiofiles.open(self.file_path, 'rb')
        await self._parse()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._file:
            await self._file.close()
            self._file = None

    async def _find_eocd(self) -> int:
        """异步从文件末尾查找 EOCD 记录的位置"""
        chunk_size = 1024
        # aiofiles doesn't support seek from end in text mode, but it's fine in binary
        await self._file.seek(0, 2)
        file_size = await self._file.tell()

        offset = max(0, file_size - chunk_size)

        while True:
            await self._file.seek(offset)
            chunk = await self._file.read(chunk_size)
            if not chunk:
                break

            pos = chunk.rfind(END_OF_CENTRAL_DIR_SIGNATURE)
            if pos != -1:
                return offset + pos

            if offset == 0:
                break

            offset = max(0, offset - (chunk_size - 4))

        raise CorruptArchiveError("Could not find End of Central Directory record")

    async def _parse(self):
        """解析 ZIP 文件的元数据"""
        eocd_offset = await self._find_eocd()
        await self._file.seek(eocd_offset + 4)
        eocd_data = await self._file.read(22 - 4)
        self.eocd = EndOfCentralDirectory.from_bytes(eocd_data)

        await self._file.seek(self.eocd.central_directory_offset)
        cd_data = await self._file.read(self.eocd.central_directory_size)

        offset = 0
        for _ in range(self.eocd.num_entries_total):
            if offset >= len(cd_data) or not cd_data[offset:].startswith(CENTRAL_DIR_FILE_HEADER_SIGNATURE):
                raise CorruptArchiveError("中央目录数据已损坏或格式错误")

            # 文件头的固定部分长度为 42 字节
            # 签名(4字节) + 字段(42字节) = 总共 46 字节
            header_data = cd_data[offset + 4:offset + 46]

            # 修正后的格式化字符串 (6个H, 3个I, 5个H, 2个I = 42字节)
            header_parts = struct.unpack('<HHHHHHIIIHHHHHII', header_data)

            file_name_length = header_parts[9]
            extra_field_length = header_parts[10]
            file_comment_length = header_parts[11]

            start = offset + 46
            file_name_bytes = cd_data[start: start + file_name_length]
            try:
                # 首先尝试 UTF-8, 如果失败则回退到 cp437 (旧ZIP文件常见编码)
                file_name = file_name_bytes.decode('utf-8')
            except UnicodeDecodeError:
                file_name = file_name_bytes.decode('cp437')

            start += file_name_length
            extra_field = cd_data[start: start + extra_field_length]
            start += extra_field_length
            file_comment = cd_data[start: start + file_comment_length]

            self.file_headers.append(CentralDirectoryFileHeader(
                *header_parts, file_name, extra_field, file_comment
            ))

            offset += 46 + file_name_length + extra_field_length + file_comment_length

    async def list_files(self) -> list[str]:
        return [header.file_name for header in self.file_headers]

    async def extractall(self, dest_path: str):
        if not os.path.exists(dest_path):
            os.makedirs(dest_path, exist_ok=True)

        tasks = [self.extract(header, dest_path) for header in self.file_headers]
        await asyncio.gather(*tasks)

    async def extract(self, file_header: CentralDirectoryFileHeader, dest_path: str):
        """Asynchronously extracts a single file."""
        # Skip directories
        if file_header.file_name.endswith('/'):
            dir_path = os.path.join(dest_path, file_header.file_name)
            os.makedirs(dir_path, exist_ok=True)
            return

        await self._file.seek(file_header.local_header_offset)
        local_header_chunk = await self._file.read(30)
        if not local_header_chunk.startswith(LOCAL_FILE_HEADER_SIGNATURE):
            raise CorruptArchiveError("Local file header signature mismatch")

        local_fn_len, local_ef_len = struct.unpack('<HH', local_header_chunk[26:30])
        data_offset = file_header.local_header_offset + 30 + local_fn_len + local_ef_len

        await self._file.seek(data_offset)
        compressed_data = await self._file.read(file_header.compressed_size)

        if file_header.compression_method == 8:  # DEFLATE
            uncompressed_data = zlib.decompress(compressed_data, wbits=-15)
        elif file_header.compression_method == 0:  # Store
            uncompressed_data = compressed_data
        else:
            raise NotImplementedError(f"Unsupported compression method: {file_header.compression_method}")

        if len(uncompressed_data) != file_header.uncompressed_size:
            raise CorruptArchiveError("Uncompressed size does not match header")

        output_path = os.path.join(dest_path, file_header.file_name)
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        async with aiofiles.open(output_path, 'wb') as f:
            await f.write(uncompressed_data)
