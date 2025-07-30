from abc import ABC, abstractmethod
from contextlib import contextmanager
from io import BufferedReader, BytesIO
from pathlib import Path
from typing import Generator, Union


class RequestFile(ABC):
    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def size(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def extension(self) -> str:
        raise NotImplementedError

    @abstractmethod
    @contextmanager
    def open(self) -> Generator[BufferedReader, None, None]:
        raise NotImplementedError


class RequestFileFromPath(RequestFile):
    def __init__(self, path: Union[str, Path]):
        if isinstance(path, Path):
            self.path = path
        else:
            self.path = Path(path)

    @property
    def size(self) -> int:
        return self.path.stat().st_size

    @property
    def extension(self) -> str:
        return self.path.suffix[1:]

    @contextmanager
    def open(self) -> Generator[BufferedReader, None, None]:
        file = None
        try:
            file = open(self.path, "rb")
            yield file
        finally:
            if file is not None:
                file.close()


class RequestFileFromReader(RequestFile):
    def __init__(self, reader: BufferedReader, size: int, extension: str):
        self._size = size
        self._extension = extension
        self._reader = reader

    @contextmanager
    def open(self) -> Generator[BufferedReader, None, None]:
        yield self._reader

    @property
    def size(self) -> int:
        return self._size

    @property
    def extension(self) -> str:
        return self._extension


class RequestFileFromBytes(RequestFile):
    def __init__(self, file_bytes: bytes, extension: str):
        self._extension = extension
        self._bytes = file_bytes

    @contextmanager
    def open(self) -> Generator[BufferedReader, None, None]:
        yield BufferedReader(BytesIO(self._bytes))

    @property
    def size(self) -> int:
        return len(self._bytes)

    @property
    def extension(self) -> str:
        return self._extension
