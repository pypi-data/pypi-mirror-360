__all__ = ("random_string", "random_string_urandom", "random_hex_string")

import binascii
import os
import string
import random


chars = list(string.digits + string.ascii_letters)
chars_len = len(chars)


def random_string(length: int):
    r"""Generate a random string

    Parameters:
        length (``int``):
            The length of the string
    """

    return "".join(random.choices(chars, k=length))


def random_string_urandom(length: int):
    r"""Generate a random string using os.urandom

    Parameters:
        length (``int``):
            The length of the string (in bytes)
    """

    return "".join(chars[b % chars_len] for b in os.urandom(length))


def random_hex_string(length):
    r"""Generate a random hex string

    Parameters:
        length (``int``):
            The length of the string (in bytes)
    """

    return binascii.hexlify(os.urandom(length)).decode()
