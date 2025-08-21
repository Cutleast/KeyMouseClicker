"""
Copyright (c) Cutleast
"""

from pynput import keyboard


def format_key_string(key: keyboard.Key) -> str:
    """
    Creates a string representation of a key.

    Args:
        key (keyboard.Key): The key to format.

    Returns:
        str: The formatted key.
    """

    formatted_key: str = str(key).strip()
    formatted_key = formatted_key.removeprefix("Key.")

    # If the key to format is the ' key, this makes it show as ' instead of "'"
    # The raw format of "'" is '"\'"'
    if repr(formatted_key) != repr('"\'"'):
        formatted_key = formatted_key.replace("'", "")
    else:
        formatted_key = "'"

    return formatted_key.capitalize()
