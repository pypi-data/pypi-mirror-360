arabic_indic_digits = str.maketrans(
    "0123456789", "\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669"
)
english_digits = str.maketrans(
    "\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669", "0123456789"
)


def to_arabic_nums(string: str):
    """
    Convert a string with english numerals to Arabic numerals

    Example:
        .. code-block:: python
            >>> to_arabic_nums("1234")
            '١٢٣٤'

    Parameters:
        string (``str`` || ``int``):
            The string or integer containing English numerals to convert to Arabic numerals

    Returns:
        ``str``: The string with digits converted to Arabic numerals
    """

    return str(string).translate(arabic_indic_digits)


def to_english_nums(string: str):
    """
    Convert a string with Arabic numerals to English numerals

    Example:
        .. code-block:: python
            >>> to_english_nums("١٢٣٤")
            '1234'

    Parameters:
        string (``str`` || ``int``):
            The string or integer containing Arabic numerals to convert to English numerals

    Returns:
        ``str``: The string with Arabic numerals converted to English numerals
    """

    return str(string).translate(english_digits)
