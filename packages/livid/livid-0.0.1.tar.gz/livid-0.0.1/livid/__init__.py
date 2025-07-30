"""yid is an implementation of YouTube IDs."""

import math
import random

# Base64 alphabet (RFC 4648), but URL-safe, using "-_" instead of "+/".
B64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
# Indexes 0..63.
B64_INDEX = {c: i for i, c in enumerate(B64_ALPHABET)}


def encode_yid(value: int, length: int = 11) -> str:
    """Encode the unsigned int `value` into a URL-safe string.

    `length` can be 1 to 11. Each character represents 6 bits.
    Therefore, length=5 can encode a 30-bit integer.

    For length=11, ensure the highest 2 bits are zero, representing a 64-bit int.
    This means the value is lower than 2^64.
    """
    if not (0 < length < 12):
        raise ValueError(f"length must be 1 to 11; given: {length}")
    max_bits = 6 * length
    if value < 0 or value >= (1 << max_bits):
        raise ValueError(
            f"Value out of range for {length}-char string (max {max_bits} bits)"
        )
    # For 11 chars, ensure 64-bit spec: even though max_bits=66, require value <2^64
    if length == 11 and value >= (1 << 64):
        raise ValueError(f"For length=11, value must be < 2^64. Given: {value}")
    chars = []
    for _ in range(length):
        chars.append(B64_ALPHABET[value & 0x3F])
        value >>= 6
    return "".join(reversed(chars))


def decode_yid(s: str) -> int:
    """Decode a URL-safe yid string; return the integer.

    Accept length 1–11. For length==11, ensure the last char is within spec:
    its index must have zero in its 2 most significant bits (i.e. <16).
    """
    length = len(s)
    if length < 1 or length > 11:
        raise ValueError(f"Invalid ID length: {length}")
    value = 0
    for char in s:
        if char not in B64_INDEX:
            raise ValueError(f"Invalid character: {char!r}")
        value = (value << 6) | B64_INDEX[char]
    if length == 11:
        # Mask out high 2 bits of 66-bit aggregate: ensure they were zero
        if value >= (1 << 64):
            raise ValueError(f"Invalid 11-char ID, encodes more than 64 bits: {s}")
    return value


def random_yid_int(length: int = 11) -> int:
    """Generate a random integer suitable for encoding into a yid.

    Ensure that the value fit within the appropriate string length.
    """
    if not (1 <= length <= 11):
        raise ValueError(f"Length must be between 1 and 11; given: {length}")
    bits = 64 if length == 11 else 6 * length
    return random.getrandbits(bits) & ((1 << bits) - 1)


def random_yid_str(length: int = 11) -> str:
    """Generate a random yid string of the given length."""
    return encode_yid(random_yid_int(length), length)
