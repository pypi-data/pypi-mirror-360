import textwrap


def split_text(text: str, chunk_size: int = 4096):
    """
    Splits a text into chunks of the specified size

    Example:
        .. code-block:: python

            # Split a long text into chunks of 4096 characters
            >>> long_text = "..."  # The long text to split
            >>> for chunk in split_text(long_text, 4096):
            ...     # Send each chunk as a separate message
            ...     send_message(chunk)

    Parameters:
        text (``str``):
            The text to split

        chunk_size (``int``, *optional*):
            The maximum size of each chunk. Defaults to ``4096``

    Returns:
        ``list``:
            A list of text chunks
    """

    if len(text) <= chunk_size:
        return [text]
    else:
        chunks = []
        wrapper = textwrap.TextWrapper(width=chunk_size, break_long_words=False)
        lines = wrapper.wrap(text)
        for line in lines:
            chunks.extend(textwrap.wrap(line, width=chunk_size))
        return chunks
