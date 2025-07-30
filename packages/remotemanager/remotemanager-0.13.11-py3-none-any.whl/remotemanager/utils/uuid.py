import hashlib
from typing import Any

from remotemanager.logging_utils.utils import format_iterable


def generate_uuid(string: Any) -> str:
    """
    Generates a UUID string from an input

    Args:
        string:
            input string
    Returns:
        (str) UUID
    """
    if not isinstance(string, str):
        string = format_iterable(string)
    h = hashlib.sha256()
    h.update(bytes(string, "utf-8"))

    return str(h.hexdigest())
