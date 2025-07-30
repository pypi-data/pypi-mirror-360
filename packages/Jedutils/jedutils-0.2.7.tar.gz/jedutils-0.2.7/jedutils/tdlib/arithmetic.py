def as_tdlib_message_id(message_id: int) -> int:
    r"""
    Convert server message ID to TDLib message ID

    \Example:
        .. code-block:: python

        >>> as_tdlib_message_id(12345)
        12944670720

    \Parameters:
        message_id (``int``):
            Server message ID

    \Returns:
        ``int``: TDLib message ID
    """

    return message_id << 20


def as_server_message_id(message_id: int) -> int:
    r"""
    Converts TDLib message ID to server message ID

    \Example:
        .. code-block:: python

            >>> as_server_message_id(12944670720)
            12345

    \Parameters:
        message_id (``int``):
            TDLib message ID

    \Returns:
        ``int``: The server message ID
    """

    result = message_id >> 20
    assert as_tdlib_message_id(result) == message_id
    return result


def as_server_message_id_unchecked(message_id: int) -> int:
    r"""
    Converts TDLib message ID to server message ID

    \Example:
        >>> as_server_message_id_unchecked(12944670720)
        12345
        >>> as_server_message_id_unchecked(12944670721) # Invalid ID
        0

    \Parameters:
        message_id (``int``):
            TDLib message ID

    \Returns:
        ``int``:
            The server message ID or 0 if the conversion is invalid
    """

    result = message_id >> 20
    if as_tdlib_message_id(result) != message_id:
        return 0
    return result


def get_supergroup_chat_id(supergroup_id: int) -> int:
    r"""
    Convert supergroup_id to chat_id

    \Example:
        >>> get_supergroup_chat_id(-123456789)
        -1000123456789

    \Parameters:
        supergroup_id (``int``):
            ID of the supergroup

    \Returns:
        ``int``: The chat ID of the supergroup
    """

    return -1000000000000 - (supergroup_id if supergroup_id > 0 else -supergroup_id)


def get_supergroup_id(chat_id: int) -> int:
    r"""
    Convert chat_id to supergroup_id

    Example:
        >>> get_supergroup_id(-1000123456789)
        123456789

    Parameters:
        chat_id (``int``):
            The chat ID to convert to a supergroup ID

    Returns:
        ``int``: The supergroup ID
    """

    return -1000000000000 - chat_id
