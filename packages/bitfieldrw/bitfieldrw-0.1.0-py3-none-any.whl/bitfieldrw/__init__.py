"""BitFieldRW - A Python library for reading and writing bit fields.

This library provides a powerful and type-safe way to define and manipulate
bit fields using Python type annotations.

Example:
    from bitfieldrw import bitfield, BitFieldMixin, Uint, Int, Float

    @bitfield
    class NetworkPacket(BitFieldMixin):
        version: Uint[4]
        header_len: Uint[4]
        total_length: Uint[16]

"""

__version__ = "0.1.0"
__author__ = "BitFieldRW Contributors"
__email__ = "contact@example.com"

from .core import (
    BitFieldDescriptor,
    BitFieldMixin,
    BitFieldStructDescriptor,
    BitFieldType,
    Float,
    Int,
    Uint,
    bitfield,
)

__all__ = [
    "BitFieldDescriptor",
    "BitFieldMixin",
    "BitFieldStructDescriptor",
    "BitFieldType",
    "Float",
    "Int",
    "Uint",
    "__version__",
    "bitfield",
]
