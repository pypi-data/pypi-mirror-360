import struct
from dataclasses import dataclass

# 定义 ZIP 文件中常见的 "magic numbers" 或签名
END_OF_CENTRAL_DIR_SIGNATURE = b'\x50\x4b\x05\x06'
CENTRAL_DIR_FILE_HEADER_SIGNATURE = b'\x50\x4b\x01\x02'
LOCAL_FILE_HEADER_SIGNATURE = b'\x50\x4b\x03\x04'


@dataclass
class EndOfCentralDirectory:
    """中央目录结束记录 (EOCD)"""
    disk_number: int
    start_disk_number: int
    num_entries_on_disk: int
    num_entries_total: int
    central_directory_size: int
    central_directory_offset: int
    comment_length: int

    @classmethod
    def from_bytes(cls, data: bytes):
        # < 是小端字节序
        # H = unsigned short (2 bytes)
        # I = unsigned int (4 bytes)
        if len(data) < 18:
            raise ValueError("EOCD data is too short")
        parts = struct.unpack('<HHHHIIH', data[:18])
        return cls(*parts)


@dataclass
class CentralDirectoryFileHeader:
    """中央目录中的文件头"""
    version_made_by: int
    version_needed: int
    flags: int
    compression_method: int
    last_mod_time: int
    last_mod_date: int
    crc32: int
    compressed_size: int
    uncompressed_size: int
    file_name_length: int
    extra_field_length: int
    file_comment_length: int
    disk_number_start: int
    internal_file_attributes: int
    external_file_attributes: int
    local_header_offset: int
    file_name: str
    extra_field: bytes
    file_comment: bytes
