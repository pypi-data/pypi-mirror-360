# # # # # # # # # # # # # # # # # # # #
# Pape (a Python package)
# Copyright 2025 Carter Pape
#
# See file LICENSE for licensing terms.
# # # # # # # # # # # # # # # # # # # #

"""A package of functions for personalized Python add-ons, by Carter Pape."""

from __future__ import annotations

import datetime
import math
import typing

import tzlocal

if typing.TYPE_CHECKING:
    import numbers

_typical_prefix_map = {
    0: "th",
    1: "st",
    2: "nd",
    3: "rd",
    4: "th",
    5: "th",
    6: "th",
    7: "th",
    8: "th",
    9: "th",
}

_ap_number_replacements_map = {
    0: "zero",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
}


def ordinal(number: int) -> str:
    """
    Convert an integer to its ordinal string representation (e.g., 1st, 2nd, 3rd, 4th).

    Args:
        number: The integer to convert.

    Returns:
        The ordinal string representation of the number.

    """
    if _is_teenthish(abs(number)):
        return f"{number}th"
    return f"{number}{_typical_prefix_map[abs(number) % 10]}"


def ap_style_date_string(
    date: datetime.date,
    *,
    relative_to: datetime.date | None | typing.Literal[False] = None,
    use_period: bool = True,
) -> str:
    """
    Format a date into an AP (Associated Press) style string.

    Args:
        date: The datetime.date object to format.

        relative_to: An optional datetime.date object to compare against, or False.
            If the year of `date` matches `relative_to`, the year is omitted from the
            output, per AP style. If `relative_to` is False, treat the date as absolute
            by always including the year in the output.
            Defaults to the current local date if None.

        use_period: If True, uses a period after abbreviated months (e.g., "Jan.").
            Defaults to True, per AP style.

    Returns:
        A string representing the date in AP style.

    """
    period_maybe = "." if use_period else ""
    spelled_out_months = {3, 4, 5, 6, 7}
    september = 9

    date_string_format = (
        "%B %-e"
        if date.month in spelled_out_months
        else f"%b{period_maybe} %-e"
        if date.month != september
        else f"%Sept{period_maybe} %-e"
    )

    if relative_to is None:
        relative_to = datetime.datetime.now(tz=tzlocal.get_localzone())

    if relative_to and (relative_to.year == date.year):
        pass
    else:
        date_string_format += ", %Y"

    return date.strftime(date_string_format)


def _is_teenthish(number: int) -> bool:
    """
    Check if the ordinal form of a number ends in "th" because of the tens digit.

    In English, the last digit typically determines the ordinal form of a number.
    However, if the tens digit is 1, that can change things. For example: 11th vs 21st.
    This function checks whether the tens digit is one.

    Args:
        number: The integer to check.

    Returns:
        True if the tens digit is 1, False otherwise.

    """
    return (math.floor(number / 10) % 10) == 1


def pluralize(
    *,
    singular_form: str,
    count: numbers.Real,
    plural_form: str | None = None,
    use_ap_style: bool = True,
    include_count: bool = True,
) -> str:
    """
    Return the correct singular or plural form of a word based on a count.

    Args:
        singular_form: The singular form of the word.

        count: The number to determine plurality.

        plural_form: Optional. The explicit plural form of the word. If None,
                     appends 's' to the singular form.

        use_ap_style: If True, uses AP style for numbers 0-9 (e.g., "one", "two").
                      Defaults to True.

        include_count: If True, includes the count in the return (e.g., "5 apples").
                       Defaults to True.

    Returns:
        A string with the correct singular/plural form, optionally including the count.

    """
    if plural_form is None:
        plural_form = f"{singular_form}s"

    correct_form = singular_form if count == 1 else plural_form

    if use_ap_style and isinstance(count, int) and count in _ap_number_replacements_map:
        count_string = _ap_number_replacements_map[count]
    else:
        count_string = f"{count:,}"

    return f"{count_string} {correct_form}" if include_count else f"{correct_form}"


def full_class_name(*, of_object: object) -> str:
    """
    Return the full, qualified name of an object's class, including its module.

    Args:
        of_object: The object whose class name is to be retrieved.

    Returns:
        A string representing the full qualified class name (e.g., "module.ClassName").

    """
    # from: https://stackoverflow.com/a/2020083/599097

    _object = of_object
    module = _object.__class__.__module__
    if (module is None) or (
        module == str.__class__.__module__  # i.e. module == "__builtin__"
    ):
        return _object.__class__.__name__
    return f"{module}.{_object.__class__.__name__}"


def full_name(*, of_type: type) -> str:
    """
    Return the full, qualified name of a type, including its module.

    Args:
        of_type: The type whose full name is to be retrieved.

    Returns:
        A string representing the full qualified type name (e.g., "module.TypeName").

    """
    _type = of_type
    module = _type.__module__
    if (module is None) or (
        module == str.__module__  # i.e. module == "__builtin__"
    ):
        return _type.__name__
    return f"{module}.{_type.__name__}"
