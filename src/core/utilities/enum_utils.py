"""
Copyright (c) Cutleast
"""

from enum import Enum


def get_member_by_name[E: type[Enum], T](
    enum_name: str, enum: E, default: T = None
) -> E | T:
    """
    Returns the enum member with the given name.

    Args:
        enum_name (str): Name of the enum member.
        enum (E): Enum.
        default (T, optional): Default value to return if the enum member is not found. Defaults to None.

    Returns:
        E | T: Enum member or default value.
    """

    try:
        return enum[enum_name]
    except KeyError:
        return default
