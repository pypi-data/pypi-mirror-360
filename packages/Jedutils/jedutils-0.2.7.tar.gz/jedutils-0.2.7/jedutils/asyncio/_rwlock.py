import asyncio
from contextlib import asynccontextmanager


class RWLock:
    """Asynchronous Read-Write Lock (RWLock) implementation"""

    def __init__(self):
        """Initialize the RWLock"""

        self.__readers = 0
        self.__writers = 0
        self.__write_lock = asyncio.Lock()
        self.__read_lock = asyncio.Lock()

    async def acquire_read(self):
        async with self.__read_lock:
            self.__readers += 1
            if self.__readers == 1:
                await self.__write_lock.acquire()

    async def release_read(self):
        async with self.__read_lock:
            self.__readers -= 1
            if self.__readers == 0:
                self.__write_lock.release()

    async def acquire_write(self):
        await self.__write_lock.acquire()

    def release_write(self):
        self.__write_lock.release()

    @property
    def readers(self):
        """Return the current count of active readers"""

        return self.__readers

    @property
    def writers(self):
        """Return the current count of active writers"""

        return self.__writers

    @asynccontextmanager
    async def read(self):
        """A context manager for acquiring a read lock"""

        try:
            await self.acquire_read()
            yield
        finally:
            await self.release_read()

    @asynccontextmanager
    async def write(self):
        """A context manager for acquiring a write lock"""

        try:
            await self.acquire_write()
            yield
        finally:
            self.release_write()
