class AiozipError(Exception):
    """所有 aiozip 相关异常的基类"""
    pass


class UnsupportedFormatError(AiozipError):
    """当文件格式不被支持时抛出"""
    pass


class CorruptArchiveError(AiozipError):
    """当归档文件损坏或格式不正确时抛出"""
    pass


class ArchiveNotFoundError(AiozipError, FileNotFoundError):
    """当归档文件不存在时抛出"""
    pass
