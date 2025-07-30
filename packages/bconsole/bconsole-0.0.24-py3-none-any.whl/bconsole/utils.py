import re
from difflib import SequenceMatcher
from typing import Any, Iterable, cast

__all__ = [
    "clear_ansi",
    "combine_metaclasses",
    "find_closest_match",
    "first",
    "halve_at",
    "hex_to_rgb",
    "hsl_to_rgb",
    "replace_last",
    "surround_with",
]


_ESC = "\033"


def combine_metaclasses(*metaclasses: type[type]) -> type[type]:
    """
    Combines multiple metaclasses into a type for easier subclassing.

    ### Args:
        metaclasses (type[type]): The metaclasses to combine.

    ### Returns:
        type[type]: The combined metaclass.

    ### Raises:
        ValueError: If no metaclasses are provided.
        TypeError: If a consistent MRO cannot be created.
    """
    if len(metaclasses) == 0:
        raise ValueError("At least one metaclass must be provided.")
    elif len(metaclasses) == 1:
        return metaclasses[0]

    mcs = type(
        "_".join(C.__name__.replace("_", "") for C in metaclasses),
        (*metaclasses,),
        {k: v for C in metaclasses for k, v in dict[str, Any](C.__dict__).items()},  # type: ignore
    )

    mcs.__doc__ = f"A metaclass that combines {format_iter((surround_with(C.__name__, wrapper='`') for C in metaclasses), final_sep=' and ')}."

    return mcs


def first[T, TDefault](
    iterable: Iterable[T], /, default: TDefault = None
) -> T | TDefault:
    """
    Returns the first element of an iterable, or the specified default value if the iterable is empty.

    ### Args:
        iterable (Iterable[T]): The iterable to get the first element of.
        default (TDefault, optional): The default value to return if the iterable is empty. Defaults to None.

    ### Returns:
        T | TDefault: The first element of the iterable, or the default value if the iterable is empty.
    """
    return next(iter(iterable), default)


def surround_with(text: str, /, *, wrapper: str) -> str:
    """
    Surrounds the specified text with the specified wrapper. Uneven wrappers are accepted but a wrapper of length 1 will be automatically duplicated.

    ### Args:
        text (str): The text to surround.
        wrapper (str): The wrapper to use.
        title (bool, optional): Whether to make the first character in the text uppercase. Defaults to True.

    ### Returns:
        str: The surrounded text.

    ### Example:
        >>> surround_with("Hello, World!", wrapper="[]")
        [Hello, World!]
        >>> surround_with("SomeClass", wrapper="`")
        `SomeClass`
    """
    w1, w2 = (wrapper, wrapper) if len(wrapper) == 1 else halve_at(wrapper)
    return f"{w1}{text}{w2}"


def halve_at(text: str, /, *, at: float = 0.5) -> tuple[str, str]:
    """
    Halves the specified text at the specified position.

    ### Args:
        text (str): The text to cut.
        at (float, optional): The position to cut at. Defaults to 0.5.

    ### Returns:
        tuple[str, str]: Each half of the text.
    """
    where = round(len(text) * at)
    return (text[:where], text[where:])


def replace_last(text: str, old: str, new: str, /) -> str:
    """
    Replaces a single occurrence of a substring in a string with another substring, starting from the end of the string.

    ### Args:
        text (str): The text to replace in.
        old (str): The substring to replace.
        new (str): The substring to replace it with.

    ### Returns:
        str: The replaced text.

    ### Example:
        >>> replace_last("apple, banana or cherry", " or ", ", ")
        "apple, banana, cherry"
    """
    return new.join(text.rsplit(old, 1))


def format_iter(
    items: Iterable[str],
    sep: str = ", ",
    final_sep: str = " or ",
    oxford_comma: bool = True,
) -> str:
    """
    Formats items into a string with the specified separator and final separator.

    ### Args:
        items (Iterable[str]): The items to format.
        sep (str, optional): The separator to use. Defaults to ", ".
        final_sep (str, optional): The final separator to use. Defaults to " or ".
        oxford_comma (bool, optional): Whether to use the Oxford comma. Adds a comma before the final separator if there are more than 2 items. Defaults to True.

    ### Returns:
        str: The formatted string.

    ### Example:
        >>> format_iter(("apple", "banana", "cherry"))
        "apple, banana, or cherry"
        >>> format_iter(("apple", "banana", "cherry"), oxford_comma=False)
        "apple, banana or cherry"
        >>> format_iter(("apple", "banana"))
        "apple or banana"
    """
    t_items = tuple(items)

    if len(t_items) > 2 and oxford_comma:
        final_sep = "," + final_sep

    return replace_last(sep.join(t_items), sep, final_sep)


def find_closest_match[TDefault](
    string: str,
    options: Iterable[str],
    /,
    *,
    min_value: float = 0.2,
    default: TDefault = None,
) -> str | TDefault:
    """
    Finds the closest match to the specified string in the specified options, returning the default value if no match is found.

    ### Args:
        string (str): The string to find a match for.
        options (Iterable[str]): The options to find a match in.
        min_value (float, optional): The minimum similarity value to consider a match. Defaults to 0.1.
        default (TDefault, optional): The default value to return if no match is found. Defaults to None.

    ### Returns:
        str | TDefault: The closest match to the string, or the default value if no match is found.
    """
    match, max_value = max(
        {o: SequenceMatcher(None, string, o).ratio() for o in options}.items(),
        key=lambda i: i[1],
    )
    return match if max_value >= min_value else default


def clear_ansi(string: str, /) -> str:
    """
    Removes all ANSI escape codes from the specified string.

    ### Args:
        string (str): The string to clear.
        escape (str, optional): The escape sequence to use. Defaults to `bconsole.core.ESCAPE`.

    ### Returns:
        str: The cleared string.
    """
    return re.sub(rf"{_ESC}\[[0-9;]*m", "", string)


def clamp(value: float, min_: float, max_: float) -> float:
    """
    Clamps a value between a minimum and maximum value.

    ### Args:
        value (float): The value to clamp.
        min_ (float): The minimum value.
        max_ (float): The maximum value.

    ### Returns:
        float: The clamped value.
    """
    return max(min_, min(max_, value))


def hex_to_rgb(hex: str, /) -> tuple[int, int, int]:
    """
    Converts a hexadecimal color code to its RGB components.

    ### Args:
        hex (str): The hexadecimal color code to convert.

    ### Returns:
        tuple[int, int, int]: The RGB components of the color code.
    """
    hex = hex.lstrip("#")

    if len(hex) != 6:
        raise ValueError(
            f"Invalid hexadecimal color code: {hex}. Note that the alpha channel is not supported."
        )

    return cast(tuple[int, int, int], tuple(int(hex[i : i + 2], 16) for i in (0, 2, 4)))


def hsl_to_rgb(h: float, s: float, l: float, /) -> tuple[float, float, float]:  # noqa: E741
    """
    Converts a HSL color to its RGB components.

    ### Args:
        h (float): The hue component.
        s (float): The saturation component.
        l (float): The lightness component.

    ### Returns:
        tuple[float, float, float]: The RGB components of the color.
    """
    nr = abs(h * 6.0 - 3.0) - 1.0
    ng = 2.0 - abs(h * 6.0 - 2.0)
    nb = 2.0 - abs(h * 6.0 - 4.0)

    nr = clamp(nr, 0.0, 1.0)
    nb = clamp(nb, 0.0, 1.0)
    ng = clamp(ng, 0.0, 1.0)

    chroma = (1.0 - abs(2.0 * l - 1.0)) * s

    return (nr - 0.5) * chroma + l, (ng - 0.5) * chroma + l, (nb - 0.5) * chroma + l
