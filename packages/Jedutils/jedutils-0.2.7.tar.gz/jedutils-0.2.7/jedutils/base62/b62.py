from typing import Union

BASE62_CHARS = list("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
BASE62_LOOKUP = {char: index for index, char in enumerate(BASE62_CHARS)}


def b62encode(data: Union[bytes, int]) -> str:
    r"""
    Encodes the given data into a base62 string

    \Example:
        .. code-block:: python
            >>> b62encode(b'hello world')
            'AAwf93rvy4aWQVw'
            >>> b62encode(123456789)
            '8M0kX'

    \Parameters:
        data (``bytes`` or ``int``):
            The data to be encoded. It must be either bytes or an integer

    \Returns:
        ``str``: The base62 encoded string
    """

    if isinstance(data, bytes):
        num = int.from_bytes(data, byteorder="big")
    elif isinstance(data, int):
        num = data
    else:
        raise TypeError("data must be bytes or int")

    base62 = []

    while num > 0:
        num, remainder = divmod(num, 62)
        base62.append(BASE62_CHARS[remainder])

    return "".join(reversed(base62))


def b62decode(b62_string: str, as_int: bool = False) -> Union[bytes, int]:
    r"""
    Decodes a Base62 encoded string

    \Example:
        .. code-block:: python
            >>> b62decode("AAwf93rvy4aWQVw")
            b'hello world'
            >>> b62decode("8M0kX", as_int=True)
            123456789

    \Parameters:
        b62_string (``str``):
            The Base62 encoded string to decode

        as_int (``bool``, *optional*):
            Pass ``True`` to return the decoded value as an integer. Default is ``False``

    \Returns:
        ``bytes`` or ``int``: The decoded value as bytes if ``as_int`` is ``False``, otherwise as an integer.
    """

    num = 0
    for char in b62_string:
        num = num * 62 + BASE62_LOOKUP[char]

    if as_int:
        return num
    return num.to_bytes(((num.bit_length() + 7) // 8), byteorder="big")
