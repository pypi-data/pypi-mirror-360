from __future__ import annotations

import struct
from typing import Generic, Literal, TypeVar, get_args, get_origin, get_type_hints

from typing_extensions import Any

T = TypeVar("T", int, float)


class BitFieldMixin:
    """Mixin class to provide type hints for dynamically added methods."""

    _bitfield_data: int
    _bitfield_total_bits: int
    _bitfield_descriptors: dict

    def to_bytes(self, byteorder: Literal["big", "little"] = "big") -> bytes:
        """Convert bitfield to bytes."""
        raise NotImplementedError  # pragma: no cover

    def from_bytes(self, data: bytes, byteorder: Literal["big", "little"] = "big"):
        """Load bitfield from bytes."""
        raise NotImplementedError  # pragma: no cover

    def to_int(self) -> int:
        """Get raw bitfield data as integer."""
        raise NotImplementedError  # pragma: no cover

    def from_int(self, value: int):
        """Set bitfield data from integer."""
        raise NotImplementedError  # pragma: no cover

    def get_bit_length(self) -> int:
        """Get the total bit length of the bitfield."""
        raise NotImplementedError  # pragma: no cover

    def get_byte_length(self) -> int:
        """Get the total byte length of the bitfield (rounded up)."""
        raise NotImplementedError  # pragma: no cover


class BitFieldType(Generic[T]):
    """Base class for bitfield types with bit length specification."""

    bit_length: int

    def __init__(self, bit_length: int) -> None:
        self.bit_length = bit_length

    def __class_getitem__(cls, bit_length: int) -> BitFieldType[int]:
        return cls(bit_length)  # type: ignore

    def pack(self, value) -> int:
        """Pack a value into the bitfield format. Subclasses should override this."""
        raise NotImplementedError("Subclasses must implement pack method")

    def unpack(self, value: int):
        """Unpack a value from the bitfield format. Subclasses should override this."""
        raise NotImplementedError("Subclasses must implement unpack method")


class Int(BitFieldType[int]):
    """Signed integer bitfield type."""

    min_value: int
    max_value: int

    def __init__(self, bit_length: int) -> None:
        super().__init__(bit_length)
        self.min_value = -(1 << (bit_length - 1))
        self.max_value = (1 << (bit_length - 1)) - 1

    def __class_getitem__(cls, bit_length: int) -> Int:
        return cls(bit_length)

    def pack(self, value: int) -> int:
        if not isinstance(value, int):
            raise TypeError(f"Expected int, got {type(value)}")
        if not (self.min_value <= value <= self.max_value):
            raise ValueError(
                f"Value {value} out of range for {self.bit_length}-bit signed integer"
            )
        return value & ((1 << self.bit_length) - 1)

    def unpack(self, value: int) -> int:
        # Sign extend if necessary
        if value & (1 << (self.bit_length - 1)):
            return value | ~((1 << self.bit_length) - 1)
        return value


class Uint(BitFieldType[int]):
    """Unsigned integer bitfield type."""

    max_value: int

    def __init__(self, bit_length: int) -> None:
        super().__init__(bit_length)
        self.max_value = (1 << bit_length) - 1

    def __class_getitem__(cls, bit_length: int) -> Uint:
        return cls(bit_length)

    def pack(self, value: int) -> int:
        if not isinstance(value, int):
            raise TypeError(f"Expected int, got {type(value)}")
        if not (0 <= value <= self.max_value):
            raise ValueError(
                f"Value {value} out of range for {self.bit_length}-bit unsigned integer"
            )
        return value

    def unpack(self, value: int) -> int:
        return value


class Float(BitFieldType[float]):
    """Float bitfield type (limited support for 32-bit only)."""

    def __init__(self, bit_length: int) -> None:
        super().__init__(bit_length)
        if bit_length != 32:
            raise ValueError("Float bitfields only support 32-bit length")

    def __class_getitem__(cls, bit_length: int) -> Float:  # type: ignore
        return cls(bit_length)

    def pack(self, value: float) -> int:
        if not isinstance(value, (int, float)):
            raise TypeError(f"Expected float, got {type(value)}")
        return struct.unpack(">I", struct.pack(">f", float(value)))[0]

    def unpack(self, value: int) -> float:
        return struct.unpack(">f", struct.pack(">I", value))[0]


class BitFieldDescriptor:
    """Descriptor for bitfield attributes."""

    def __init__(self, field_type: BitFieldType, bit_offset: int, name: str):
        self.field_type = field_type
        self.bit_offset = bit_offset
        self.name = name
        self.mask = ((1 << field_type.bit_length) - 1) << bit_offset

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:
            return self
        raw_value = (obj._bitfield_data & self.mask) >> self.bit_offset
        return self.field_type.unpack(raw_value)

    def __set__(self, obj: Any, value: int) -> None:
        packed_value = self.field_type.pack(value)
        # Clear the bits for this field
        obj._bitfield_data &= ~self.mask
        # Set the new bits
        obj._bitfield_data |= packed_value << self.bit_offset

    def __set_name__(self, owner, name):
        """Call when the descriptor is assigned to a class attribute."""
        self.name = name


class BitFieldStructDescriptor:
    """Descriptor for nested bitfield structure attributes."""

    def __init__(self, struct_class, bit_offset: int, name: str):
        self.struct_class = struct_class
        self.bit_offset = bit_offset
        self.name = name

        # Get the bit length from the nested structure
        if hasattr(struct_class, "_bitfield_total_bits"):
            self.bit_length = struct_class._bitfield_total_bits
        else:
            raise ValueError(
                f"Class {struct_class.__name__} is not a bitfield structure"
            )

        self.mask = ((1 << self.bit_length) - 1) << bit_offset

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:
            return self

        # Extract the bits for this nested structure
        raw_value = (obj._bitfield_data & self.mask) >> self.bit_offset

        # Create an instance of the nested structure and set its data
        nested_obj = self.struct_class()
        nested_obj.from_int(raw_value)

        return nested_obj

    def __set__(self, obj: Any, value: Any) -> None:
        if not isinstance(value, self.struct_class):
            raise TypeError(f"Expected {self.struct_class.__name__}, got {type(value)}")

        # Get the raw data from the nested structure
        packed_value = value.to_int()

        # Clear the bits for this field
        obj._bitfield_data &= ~self.mask
        # Set the new bits
        obj._bitfield_data |= packed_value << self.bit_offset


def bitfield(cls: type) -> type:
    """Convert a class with bitfield type annotations into a bitfield structure.

    Usage:
        @bitfield
        class MyStruct:
            field1: Int[8]
            field2: Uint[16]
            field3: Float[32]
    """
    # Get type hints
    hints = get_type_hints(cls)

    # First pass: calculate total bits for each field
    field_info = []
    total_bits = 0

    for name, annotation in hints.items():
        field_bits = 0
        field_type = None

        # Check if it's a bitfield type (must be an instance of BitFieldType)
        if isinstance(annotation, BitFieldType):
            field_type = annotation
            field_bits = field_type.bit_length
        elif get_origin(annotation) is not None:
            # Handle Int[8], Uint[16], etc.
            origin = get_origin(annotation)
            args = get_args(annotation)
            if origin and hasattr(origin, "__name__") and args:
                if origin.__name__ in ("Int", "Uint", "Float"):
                    field_type = origin[args[0]]
                    field_bits = field_type.bit_length
                else:
                    continue
            else:
                continue
        elif hasattr(annotation, "_bitfield_total_bits"):
            # Handle nested bitfield structures
            field_type = annotation
            field_bits = annotation._bitfield_total_bits
        else:
            continue

        field_info.append((name, field_type, field_bits))
        total_bits += field_bits

    # Second pass: create descriptors with big-endian bit layout
    # Fields are arranged from high bits to low bits (big-endian layout)
    descriptors = {}
    current_bit_offset = total_bits

    for name, field_type, field_bits in field_info:
        current_bit_offset -= field_bits

        if hasattr(field_type, "_bitfield_total_bits"):
            # Nested bitfield structure
            descriptors[name] = BitFieldStructDescriptor(
                field_type, current_bit_offset, name
            )
        else:
            # Regular bitfield type
            descriptors[name] = BitFieldDescriptor(field_type, current_bit_offset, name)

    # Add descriptors to class
    for name, descriptor in descriptors.items():
        setattr(cls, name, descriptor)

    # Store metadata
    cls._bitfield_total_bits = total_bits
    cls._bitfield_descriptors = descriptors

    # Modify __init__ to initialize bitfield data
    original_init = cls.__init__ if hasattr(cls, "__init__") else lambda self: None

    def __init__(self, *args, **kwargs):
        self._bitfield_data = 0
        original_init(self, *args, **kwargs)

    cls.__init__ = __init__

    # Add utility methods
    def to_bytes(self, byteorder: Literal["big", "little"] = "big") -> bytes:
        """Convert bitfield to bytes."""
        byte_length = (self._bitfield_total_bits + 7) // 8
        return self._bitfield_data.to_bytes(byte_length, byteorder)

    def from_bytes(self, data: bytes, byteorder: Literal["big", "little"] = "big"):
        """Load bitfield from bytes."""
        self._bitfield_data = int.from_bytes(data, byteorder)
        return self

    def to_int(self) -> int:
        """Get raw bitfield data as integer."""
        return self._bitfield_data

    def from_int(self, value: int):
        """Set bitfield data from integer."""
        max_value = (1 << self._bitfield_total_bits) - 1
        if value < 0 or value > max_value:
            raise ValueError(
                f"Value {value} out of range for {self._bitfield_total_bits}-bit bitfield"
            )
        self._bitfield_data = value
        return self

    def get_bit_length(self) -> int:
        """Get the total bit length of the bitfield."""
        return self._bitfield_total_bits

    def get_byte_length(self) -> int:
        """Get the total byte length of the bitfield (rounded up)."""
        return (self._bitfield_total_bits + 7) // 8

    def __repr__(self):
        field_values = []
        for name in self._bitfield_descriptors:
            value = getattr(self, name)
            field_values.append(f"{name}={value}")
        return f"{cls.__name__}({', '.join(field_values)})"

    cls.to_bytes = to_bytes
    cls.from_bytes = from_bytes
    cls.to_int = to_int
    cls.from_int = from_int
    cls.get_bit_length = get_bit_length
    cls.get_byte_length = get_byte_length
    cls.__repr__ = __repr__

    # Update annotations to reflect actual runtime types
    new_annotations = {}
    for name, field_type, _ in field_info:
        if hasattr(field_type, "_bitfield_total_bits"):
            # Nested structure - keep original type
            new_annotations[name] = field_type
        elif isinstance(field_type, (Int, Uint)):
            # Integer fields accept int
            new_annotations[name] = int
        elif isinstance(field_type, Float):
            # Float fields accept float
            new_annotations[name] = float
        else:
            # Keep original annotation for unknown types
            new_annotations[name] = hints[name]

    # Preserve method annotations
    new_annotations.update({
        "to_bytes": 'Callable[[Literal["big", "little"]], bytes]',
        "from_bytes": 'Callable[[bytes, Literal["big", "little"]], object]',
        "to_int": "Callable[[], int]",
        "from_int": "Callable[[int], object]",
        "get_bit_length": "Callable[[], int]",
        "get_byte_length": "Callable[[], int]",
    })

    cls.__annotations__ = new_annotations

    return cls
