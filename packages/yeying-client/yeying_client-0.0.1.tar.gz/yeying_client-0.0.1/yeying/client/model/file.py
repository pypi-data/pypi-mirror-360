# -*- coding:utf-8 -*-
import io
import os.path
import time
from io import BytesIO, SEEK_SET, SEEK_CUR, SEEK_END
from yeying.client.utils.digital_format_utils import get_digital_format_by_name


class File:
    """模拟 JavaScript File 对象的 Python 实现"""

    def __init__(self, name: str, size: int, stream, last_modified: int = None):
        if isinstance(stream, str) and os.path.exists(stream):
            with open(stream, 'rb') as file:
                self.stream = file.read()
        elif isinstance(stream, bytes):
            self.stream = stream
        else:
            raise TypeError("stream must be file path or bytes")
        self.name = name
        self.size = size
        self._position = 0
        self.type = get_digital_format_by_name(name)
        self.buffered_reader = io.BufferedReader(io.BytesIO(self.stream))
        self.last_modified = last_modified or int(time.time() * 1000)

    def get_last_modified(self) -> int:
        """获取文件最后修改时间戳（毫秒）"""
        return self.last_modified

    def slice(self, start: int = 0, end: int = None, content_type: str = None) -> "FileSlice":
        """创建文件切片，模拟 File.slice()"""
        if end is None:
            end = self.size
        elif end > self.size:
            end = self.size

        if start < 0:
            start = max(0, self.size + start)
        if end < 0:
            end = max(0, self.size + end)

        if start >= end:
            return FileSlice(b"", content_type or self.type, self.last_modified)

        return FileSlice(self._read_range(start, end), content_type or self.type, self.last_modified)

    def _read_range(self, start: int, end: int) -> bytes:
        """读取文件的指定字节范围"""
        self.buffered_reader.seek(start)
        return self.buffered_reader.read(end - start)

    def read(self, size: int = -1) -> bytes:
        """从当前位置读取数据"""
        self.buffered_reader.seek(self._position)
        data = self.buffered_reader.read(size) if size >= 0 else self.buffered_reader.read()
        self._position = self.buffered_reader.tell()
        return data

    def seek(self, offset: int, whence: int = SEEK_SET) -> int:
        """移动文件指针"""
        if whence == SEEK_SET:
            self._position = max(0, min(offset, self.size))
        elif whence == SEEK_CUR:
            self._position = max(0, min(self._position + offset, self.size))
        elif whence == SEEK_END:
            self._position = max(0, min(self.size + offset, self.size))
        else:
            raise ValueError("Invalid whence value")
        return self._position

    def tell(self) -> int:
        """获取当前文件指针位置"""
        return self._position

    def __repr__(self):
        return f"<File {self.name} ({self.size} bytes, {self.type})>"


class FileSlice:
    """表示文件切片的类"""

    def __init__(self, data: bytes, content_type: str, last_modified: int):
        self.data = data
        self.size = len(data)
        self.type = content_type
        self._stream = BytesIO(data)
        self.last_modified = last_modified

    def read(self, size: int = -1) -> bytes:
        """从切片中读取数据"""
        return self._stream.read(size)

    def seek(self, offset: int, whence: int = SEEK_SET) -> int:
        """移动切片指针"""
        return self._stream.seek(offset, whence)

    def tell(self) -> int:
        """获取当前切片指针位置"""
        return self._stream.tell()

    def text(self, encoding: str = "utf-8") -> str:
        """以文本形式读取切片内容"""
        return self.data.decode(encoding)

    def stream(self) -> bytes:
        """以文本形式读取切片内容"""
        return self.data

    def save(self, file_path: str):
        """保存切片到文件"""
        with open(file_path, "wb") as f:
            f.write(self.data)

    def get_last_modified(self) -> int:
        """获取切片最后修改时间戳（毫秒）"""
        return self.last_modified

    def __repr__(self):
        return f"<FileSlice ({self.size} bytes, {self.type})>"
