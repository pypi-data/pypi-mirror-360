import asyncio

try:
    import aiohttp
except ImportError:
    aiohttp = None

import os


async def download_file(
    url: str,
    filename: str,
    chunk_size: int = 8192,
    ignore_status: bool = False,
    progress_callback: callable = None,
    thread_pool=None,
    **kwargs,
) -> None:
    r"""
    Asynchronously download a file from the given URL and saves it to the specified filename using chunked downloading

    Example:
        Download a large file asynchronously:

        .. code-block:: python

            async def my_callback(downloaded, expected_size):
                print(f"Downloaded: {downloaded}/{expected_size}")

            await download_file('https://example.com/large_file.zip', 'my_large_file.zip', progress_callback=my_callback)

    Parameters:
        url (``str``):
            The URL of the file to download

        filename (``str``, *optional*):
            The filename to save the downloaded file as

        chunk_size (``int``, *optional*):
            The size of each chunk to download in bytes. Default is 8192 bytes (8 KB)

        ignore_status (``bool``, *optional*):
            Whether to ignore errors in the response from the server. Default is ``False``

        progress_callback (``callable``, *optional*):
            A callable function to be called with the download progress, in bytes

        thread_pool:
            A thread pool to use for blocking operations. Default is ``None``

        \*\*kwargs:
            Any additional keyword arguments to pass to the `aiohttp.get` call
    Returns:
        ``None``

    Raises:
        :py:class:`aiohttp.ClientResponseError`
    """

    if not aiohttp:
        raise RuntimeError("aiohttp is not installed. Try pip install aiohttp")

    async with aiohttp.ClientSession() as session:
        async with session.get(url, **kwargs) as response:
            if not ignore_status:
                response.raise_for_status()

            expected_size = int(response.headers.get("content-length", 0))
            downloaded_size = 0
            loop = asyncio.get_event_loop()

            if progress_callback:
                progress_callback(downloaded_size, expected_size)

            if not filename:
                filename = os.path.basename(url)
            if not filename:
                raise ValueError("Can't find filename")

            f = None
            try:
                f = await loop.run_in_executor(thread_pool, open, filename, "wb")

                async for chunk in response.content.iter_chunked(chunk_size):
                    await loop.run_in_executor(thread_pool, f.write, chunk)

                    downloaded_size += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded_size, expected_size)

            finally:
                if f:
                    await loop.run_in_executor(thread_pool, f.close)

    return None
