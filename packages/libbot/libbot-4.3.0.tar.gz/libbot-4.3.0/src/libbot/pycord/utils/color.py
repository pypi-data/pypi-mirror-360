from discord import Colour


def _int_from_hex(hex_string: str) -> int:
    try:
        return int(hex_string, base=16)
    except Exception as exc:
        raise ValueError("Input string must be a valid HEX code.") from exc


def _hex_from_int(color_int: int) -> str:
    if not 0 <= color_int <= 0xFFFFFF:
        raise ValueError("Color's value must be in the range 0 to 0xFFFFFF.")

    return f"#{color_int:06x}"


def color_from_hex(hex_string: str) -> Colour:
    """Convert valid hexadecimal string to discord.Colour.

    :param hex_string: Hexadecimal string to convert into Colour object
    :type hex_string: str
    :return: Colour object
    """
    return Colour(_int_from_hex(hex_string))


def hex_from_color(color: Colour) -> str:
    """Convert discord.Colour to hexadecimal string.

    :param color: Colour object to convert into the string
    :type color: Colour
    :return: Hexadecimal string in #XXXXXX format
    """
    return _hex_from_int(color.value)
