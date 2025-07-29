# SPDX-License-Identifier: Apache-2.0
from typing import List, Optional, Union


def nullable_ints(val: str) -> Optional[Union[int, List[int]]]:
    """Parses a string containing comma-separated integers or a single integer.

    Args:
        val: String value to be parsed.

    Returns:
        An integer if the string represents a single value, a list of integers 
        if it contains multiple values, or None if the input is empty.
    """
    if not val:
        return None

    items = [item.strip() for item in val.split(",")]

    try:
        parsed_values = [int(item) for item in items]
    except ValueError as exc:
        raise ValueError("device_id should be integers.") from exc

    return parsed_values[0] if len(parsed_values) == 1 else parsed_values