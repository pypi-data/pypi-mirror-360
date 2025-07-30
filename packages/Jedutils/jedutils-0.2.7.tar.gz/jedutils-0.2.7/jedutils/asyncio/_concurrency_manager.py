import asyncio
from contextlib import asynccontextmanager


class ConcurrencyManager:
    """A class for managing and tracking concurrent operations"""

    def __init__(self):
        """Initialize the ConcurrencyManager class with data and a lock"""

        self.data = {}
        self.lock = asyncio.Lock()

    async def acquire(self, ID) -> None:
        """
        Acquire a lock for the specified ID

        Parameters:
            ID (``str``):
                Identifier for the operation
        """

        async with self.lock:
            self.data.setdefault(ID, 0)
            self.data[ID] += 1

    async def release(self, ID) -> bool:
        """
        Release a lock for the specified ID

        Parameters:
            ID (``str``):
                Identifier for the operation

        Returns:
            ``bool``:
                ``True`` if the lock was released, ``False`` if ID was not found
        """

        async with self.lock:
            if ID in self.data:
                self.data[ID] -= 1
                if self.data[ID] == 0:
                    del self.data[ID]
                return True
            else:
                return False

    async def get_count(self, ID) -> int:
        """
        Get the current count of operations for the specified ID

        Parameters:
            ID (``str``):
                Identifier for the operation

        Returns:
            ``int``:
                Current count of operations for the ID
        """

        async with self.lock:
            return self.data.get(ID, 0)

    @asynccontextmanager
    async def context(self, ID):
        """
        Create a context for the specified ID, acquiring and releasing a lock

        Parameters:
            ID (``str``):
                Identifier for the operation
        """

        await self.acquire(ID)
        try:
            yield
        finally:
            await self.release(ID)

    @asynccontextmanager
    async def limit(self, ID, max_count):
        """
        Create a context with a limit on the number of concurrent operations.

        Parameters:
            ID (``str``):
                Identifier for the operation.

            max_count (``int``):
                Maximum allowed concurrent operations for the ``ID``.

        Raises:
            ``ValueError``:
                If the limit for the ``ID`` is exceeded
        """

        await self.acquire(ID)
        try:
            count = await self.get_count(ID)
            if count <= max_count:
                yield
            else:
                raise ValueError(f"Exceeded limit of {max_count} for {ID}")
        finally:
            await self.release(ID)

    async def wait_until(self, ID, target_count, timeout=None):
        """
        Wait until the count for the specified ID reaches the target count

        Parameters:
            ID (``str``):
                Identifier for the operation

            target_count (``int``):
                Target count to wait for

            timeout (``float``):
                Maximum time to wait in seconds. If ``None``, wait indefinitely

        Raises:
            ``TimeoutError``:
                If the ``timeout`` is reached before the target count is achieved
        """

        while await self.get_count(ID) != target_count:
            await asyncio.sleep(0.1)
            if timeout is not None:
                timeout -= 0.1
                if timeout <= 0:
                    raise TimeoutError(
                        f"Timeout waiting for {ID} to reach {target_count}"
                    )
