def hexbytes(data: bytes | bytearray, prefix: bool = False, limit: int = 0) -> str:
    """Format a bytes or bytearray value into a human readable string for debugging."""

    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("The 'data' argument must have a bytes or bytesarray value!")

    if not isinstance(prefix, bool):
        raise TypeError("The 'prefix' argument must have a boolean value!")

    if not (isinstance(limit, int) and limit >= 0):
        raise TypeError("The 'limit' argument must have a positive integer value!")

    hex_string = ("" if prefix else " ").join(
        [
            (r"\x" if prefix else "") + f"{byte:02x}"
            for (index, byte) in enumerate(data)
            if limit == 0 or index < limit
        ]
    )

    if limit > 0 and len(data) > limit:
        hex_string += " ..."

    return ('b"' if prefix else "[> ") + hex_string + ('"' if prefix else " <]")


def print_hexbytes(data: bytes | bytearray, **kwargs) -> None:
    """Print a bytes or bytearray value as a human readable string for debugging."""

    print(hexbytes(data=data, **kwargs))
