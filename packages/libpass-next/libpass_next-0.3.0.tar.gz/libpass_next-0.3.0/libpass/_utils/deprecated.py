from __future__ import annotations

import binascii

_BASE64_STRIP = b"=\n"
_BASE64_PAD1 = b"="
_BASE64_PAD2 = b"=="


def b64s_encode(data: bytes) -> bytes:
    """
    Encode using shortened base64 format which omits padding & whitespace.

    uses default ``+/`` altchars.
    """
    return binascii.b2a_base64(data).rstrip(_BASE64_STRIP)


def b64s_decode(data: bytes | str) -> bytes:
    """
    Decode from shortened base64 format which omits padding & whitespace.

    uses default ``+/`` altchars.
    """
    if isinstance(data, str):
        # needs bytes for replace() call, but want to accept ascii-unicode ala a2b_base64()
        data = data.encode("ascii")
    offset = len(data) % 4
    if offset == 0:
        pass
    elif offset == 2:  # noqa: PLR2004
        data += _BASE64_PAD2
    elif offset == 3:  # noqa: PLR2004
        data += _BASE64_PAD1
    else:
        msg = "invalid base64 input"
        raise ValueError(msg)
    try:
        return binascii.a2b_base64(data)
    except binascii.Error as err:
        raise TypeError(err) from err


def ab64_encode(data: bytes) -> bytes:
    """
    Encode using shortened base64 format which omits padding & whitespace.

    uses custom ``./`` altchars.
    it is primarily used by Passlib's custom pbkdf2 hashes.
    """
    return b64s_encode(data).replace(b"+", b".")


def ab64_decode(data: bytes | str) -> bytes:
    """
    Decode from shortened base64 format which omits padding & whitespace.

    uses custom ``./`` altchars, but supports decoding normal ``+/`` altchars as well.
    it is primarily used by Passlib's custom pbkdf2 hashes.
    """
    if isinstance(data, str):
        # needs bytes for replace() call, but want to accept ascii-unicode ala a2b_base64()
        try:
            data = data.encode("ascii")
        except UnicodeEncodeError as e:
            msg = "string argument should contain only ASCII characters"
            raise ValueError(msg) from e
    return b64s_decode(data.replace(b".", b"+"))
