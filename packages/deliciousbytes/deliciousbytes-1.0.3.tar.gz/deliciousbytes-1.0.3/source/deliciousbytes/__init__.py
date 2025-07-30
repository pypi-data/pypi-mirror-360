from __future__ import annotations

import ctypes
import logging
import enumerific
import struct
import typing
import sys
import math
import builtins

from classicist import classproperty

from deliciousbytes.utilities import hexbytes

logger = logging.getLogger(__name__)


class Encoding(enumerific.Enumeration, aliased=True):
    """Define the various string encoding formats."""

    Undefined = None
    ASCII = "ascii"
    Bytes = "bytes"
    Unicode = "utf-8"
    UTF8 = "utf-8"
    UTF16 = "utf-16"
    UTF32 = "utf-32"


class ByteOrder(enumerific.Enumeration, aliased=True):
    """Define the two styles of byte ordering - big-endian and little-endian."""

    # Most significant byte ordering
    MSB = "big"

    # Least significant byte ordering
    LSB = "little"

    # Vendor aliases
    Motorolla = MSB
    Intel = LSB

    # Endian aliases
    BigEndian = MSB
    LittleEndian = LSB

    # Endian aliases (shorter)
    Big = MSB
    Little = LSB

    @classproperty
    def Native(cls) -> ByteOrder:
        if sys.byteorder == "big":
            return ByteOrder.MSB
        elif sys.byteorder == "little":
            return ByteOrder.LSB


class Type(object):
    """The Type class is the superclass for all deliciousbytes types and defines shared
    properties and behaviour for each type class."""

    _length: int = None
    _signed: bool = None
    _format: str = None
    _order: ByteOrder = None

    @classproperty
    def length(cls) -> int | None:
        """Return the number of bytes that are used to hold the value."""
        return cls._length

    @classproperty
    def signed(cls) -> bool | None:
        """Return whether the type is signed or not."""
        return cls._signed

    @classproperty
    def format(cls) -> str | None:
        """Return the format character used for the type in the struct module if set."""
        return cls._format

    @property
    def order(self) -> ByteOrder:
        """Return the current byte order associated with the type."""

        return self._order

    @order.setter
    def order(self, order: ByteOrder):
        """Support changing the byte order used to encode the type."""

        if not isinstance(order, ByteOrder):
            raise TypeError(
                "The 'order' argument must have a ByteOrder enumeration value!"
            )

        self._order = order


class Int(int, Type):
    """Signed unbounded integer type."""

    _length: int = 0  # Unbounded length integer limited only by available system memory
    _signed: bool = True
    _format: str = None
    _order: ByteOrder = ByteOrder.MSB

    # In Python 3, the int type is unbounded and can store arbitrarily large numbers and
    # as there is no integer infinity, we must use the float infinity sentinels instead:
    _minimum: int = float("-inf")
    _maximum: int = float("inf")

    def __new__(cls, value, base: int = 10, **kwargs):
        logger.debug(
            "%s.__new__(cls: %s, value: %s, base: %s, kwargs: %s)",
            cls.__name__,
            cls,
            value,
            base,
            kwargs,
        )

        if not isinstance(value, (int, float, str, bytes, bytearray)):
            raise ValueError(
                "The 'value' argument must have an integer, float, string, bytes or bytearray value!"
            )

        if not isinstance(base, int):
            raise ValueError("The 'base' argument must have an integer value!")

        if isinstance(value, (int, float)):
            return super().__new__(cls, value)
        elif isinstance(value, (str, bytes, bytearray)):
            return super().__new__(cls, value, base=base)

    def __bytes__(self) -> bytes:
        return self.encode()

    def __len__(self) -> int:
        return len(bytes(self))

    def __int__(self) -> int:
        return int.__int__(self)

    def __float__(self) -> float:
        return float.__float__(self)

    def __bool__(self) -> bool:
        return self > 0

    def __getitem__(self, key: int) -> bytes:
        """Support obtaining individual bytes from the encoded version of the value."""

        encoded: bytes = bytes(self)

        if not (isinstance(key, int) and key >= 0):
            raise TypeError("The 'key' argument must have a positive integer value!")

        if key >= len(encoded):
            raise KeyError(
                "The 'key' argument must have a positive integer value that is in range of the element indicies that are available!"
            )

        return encoded[key]

    def __setitem__(self, key: int, value: int):
        raise NotImplementedError

    def __delitem__(self, key: int, value: int):
        raise NotImplementedError

    def __add__(self, other: int) -> Int:
        """Addition"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) + int(other))

    def __mul__(self, other: int) -> Int:
        """Multiply"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) * int(other))

    def __truediv__(self, other: int) -> Int:
        """True division"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) / int(other))

    def __floordiv__(self, other: int) -> Int:
        """Floor division"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) // int(other))

    def __sub__(self, other: int) -> Int:
        """Subtraction"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) - int(other))

    def __mod__(self, other: int) -> Int:
        """Modulo"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) % int(other))

    def __pow__(self, other: int) -> Int:
        """Power"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) ** int(other))

    def __rshift__(self, other: int) -> Int:
        """Right bit shift"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) >> int(other))

    def __lshift__(self, other: int) -> Int:
        """Left bit shift"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) << int(other))

    def __and__(self, other: int) -> Int:
        """Binary AND"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) & int(other))

    def __or__(self, other: int) -> Int:
        """Binary OR"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) | int(other))

    def __xor__(self, other: int) -> Int:
        """Binary XOR"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) ^ int(other))

    def __iadd__(self, other: int) -> Int:
        """Asignment addition"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) + int(other))

    def __imul__(self, other: int) -> Int:
        """Asignment multiply"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) * int(other))

    def __idiv__(self, other: int) -> Int:
        """Asignment true division"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) / int(other))

    def __ifloordiv__(self, other: int) -> Int:
        """Asignment floor division"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) // int(other))

    def __isub__(self, other: int) -> Int:
        """Asignment subtract"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) - int(other))

    def __imod__(self, other: int) -> Int:
        """Asignment modulo"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) % int(other))

    def __ipow__(self, other: int) -> Int:
        """Asignment power"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) ** int(other))

    def __irshift__(self, other: int) -> Int:
        """Asignment right bit shift"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) >> int(other))

    def __ilshift__(self, other: int) -> Int:
        """Asignment left bit shift"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) << int(other))

    def __iand__(self, other: int) -> Int:
        """Asignment AND"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) & int(other))

    def __ior__(self, other: int) -> Int:
        """Asignment OR"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) | int(other))

    def __ixor__(self, other: int) -> Int:
        """Asignment XOR"""
        if not isinstance(other, int):
            raise TypeError("The 'other' argument must have an integer value!")
        return self.__class__(int(self) ^ int(other))

    def __neg__(self) -> Int:
        """Unary negation"""
        return self.__class__(-int(self))

    def __pos__(self) -> Int:
        """Unary positive"""
        return self.__class__(+int(self))

    def __invert__(self) -> Int:
        """Unary invert"""
        return self.__class__(~int(self))

    @classproperty
    def MIN(cls) -> int:
        """Return the minimum value that can be held by the type."""
        return cls._minimum

    @classproperty
    def MAX(cls) -> int:
        """Return the maximum value that can be held by the type."""
        return cls._maximum

    def encode(self, order: ByteOrder = None) -> bytes:
        if not isinstance(self, Int):
            raise TypeError(
                "Ensure the 'encode' method is being called on a class instance!"
            )

        if order is None:
            order = self.order
        elif not isinstance(order, ByteOrder):
            raise TypeError(
                "The 'order' argument must have a ByteOrder enumeration value!"
            )

        if self.length > 0:
            return self.to_bytes(
                length=self.length,
                byteorder=order.value,
                signed=self.signed,
            )
        else:
            return self.to_bytes(
                length=math.ceil(self.bit_length() / 8),
                byteorder=order.value,
                signed=self.signed,
            )

    @classmethod
    def decode(cls, value: bytes | bytearray, order: ByteOrder = ByteOrder.MSB) -> Int:
        if not isinstance(value, (bytes, bytearray)):
            raise TypeError(
                "The 'value' argument must have a bytes or bytearray value!"
            )

        if not isinstance(order, ByteOrder):
            raise TypeError(
                "The 'order' argument must have a ByteOrder enumeration value!"
            )

        decoded = cls(
            int.from_bytes(bytes(value), byteorder=order.value, signed=cls._signed)
        )

        logger.debug(
            "%s.decode(value: %r, order: %r) => %r",
            cls.__name__,
            hexbytes(value),
            order,
            decoded,
        )

        return decoded


class Int8(Int):
    """An signed 1-byte, 8-bit integer type."""

    _length: int = 1
    _signed: bool = True
    _minimum: int = -128
    _maximum: int = +127

    def __new__(cls, value: int, *args, **kwargs):
        if not isinstance(value, int):
            raise ValueError("The 'value' argument must have an integer value!")

        int8 = ctypes.c_int8(value)

        return super().__new__(cls, int8.value, *args, **kwargs)


class Int16(Int):
    """An signed 2-byte, 16-bit integer type."""

    _length: int = 2
    _signed: bool = True
    _minimum: int = -32768
    _maximum: int = +32767

    def __new__(cls, value: int, *args, **kwargs):
        if not isinstance(value, int):
            raise ValueError("The 'value' argument must have an integer value!")

        int16 = ctypes.c_int16(value)

        return super().__new__(cls, int16.value, *args, **kwargs)


class Int32(Int):
    """An signed 4-byte, 32-bit integer type."""

    _length: int = 4
    _signed: bool = True
    _minimum: int = -2_147_483_648
    _maximum: int = +2_147_483_647

    def __new__(cls, value: int, *args, **kwargs):
        if not isinstance(value, int):
            raise ValueError("The 'value' argument must have an integer value!")

        int32 = ctypes.c_int32(value)

        return super().__new__(cls, int32.value, *args, **kwargs)


class Int64(Int):
    """An signed 8-byte, 64-bit integer type."""

    _length: int = 8
    _signed: bool = True
    _minimum: int = -9_223_372_036_854_775_808
    _maximum: int = +9_223_372_036_854_775_807

    def __new__(cls, value: int, *args, **kwargs):
        if not isinstance(value, int):
            raise ValueError("The 'value' argument must have an integer value!")

        int64 = ctypes.c_int64(value)

        return super().__new__(cls, int64.value, *args, **kwargs)


class UInt(Int):
    """An unsigned unbounded integer type."""

    _length: int = None
    _signed: bool = False
    _minimum: int = 0
    _maximum: int = float("inf")


class UInt8(UInt):
    """An unsigned 1-byte, 8-bit wide integer type."""

    _length: int = 1
    _minimum: int = 0
    _maximum: int = 255

    def __new__(cls, value: int, *args, **kwargs):
        if not isinstance(value, int):
            raise ValueError("The 'value' argument must have an integer value!")

        uint8 = ctypes.c_uint8(value)

        return super().__new__(cls, uint8.value, *args, **kwargs)


class UInt16(UInt):
    """An unsigned 2-byte, 16-bit wide integer type."""

    _length: int = 2
    _minimum: int = 0
    _maximum: int = 65535

    def __new__(cls, value: int, *args, **kwargs):
        if not isinstance(value, int):
            raise ValueError("The 'value' argument must have an integer value!")

        uint16 = ctypes.c_uint16(value)

        return super().__new__(cls, uint16.value, *args, **kwargs)


class UInt32(UInt):
    """An unsigned 4-byte, 32-bit wide integer type."""

    _length: int = 4
    _minimum: int = 0
    _maximum: int = 4294967295

    def __new__(cls, value: int, *args, **kwargs):
        if not isinstance(value, int):
            raise ValueError("The 'value' argument must have an integer value!")

        uint32 = ctypes.c_uint32(value)

        return super().__new__(cls, uint32.value, *args, **kwargs)


class UInt64(UInt):
    """An unsigned 8-byte, 64-bit wide integer type."""

    _length: int = 8
    _minimum: int = 0
    _maximum: int = 1.844674407370955e19

    def __new__(cls, value: int, *args, **kwargs):
        if not isinstance(value, int):
            raise ValueError("The 'value' argument must have an integer value!")

        uint64 = ctypes.c_uint64(value)

        return super().__new__(cls, uint64.value, *args, **kwargs)


class Char(UInt8):
    """A char is an unsigned 1-byte, 8-bits wide integer type."""

    _format: str = "c"
    _signed: bool = False

    def __new__(cls, value: int | str | bytes, *args, **kwargs):
        if not isinstance(value, (int, str, bytes)):
            raise ValueError(
                "The 'value' argument must have an integer, string or bytes value!"
            )

        if isinstance(value, (str, bytes)):
            if isinstance(value, bytes):
                value = value.decode()

            if len(value) > 1:
                raise ValueError(
                    "The 'value' argument, if provided as a string or as bytes, cannot be longer than one character!"
                )

            value = ord(value[0])

        return super().__new__(cls, value, *args, **kwargs)

    def __str__(self) -> str:
        return chr(self)


class SignedChar(Int8):
    """A signed char is an signed 1-byte, 8-bits wide integer type."""

    _format: str = "b"
    _signed: bool = True

    def __new__(cls, value: int | str | bytes, *args, **kwargs):
        if not isinstance(value, (int, str, bytes)):
            raise ValueError(
                "The 'value' argument must have an integer, string or bytes value!"
            )

        if isinstance(value, (str, bytes)):
            if isinstance(value, bytes):
                value = value.decode()

            if len(value) > 1:
                raise ValueError(
                    "The 'value' argument, if provided as a string or as bytes, cannot be longer than one character!"
                )

            value = ord(value[0])

        return super().__new__(cls, value, *args, **kwargs)

    def __str__(self) -> str:
        return chr(self)


class UnsignedChar(Char):
    pass


class Short(Int16):
    """A short integer is an signed 2-byte, 16-bits wide integer type."""

    _format: str = "h"


class SignedShort(Int16):
    """A short integer is an signed 2-byte, 16-bits wide integer type."""

    _format: str = "h"


class UnsignedShort(UInt16):
    """An unsigned short integer is an unsigned 2-byte, 16-bits wide integer type."""

    _format: str = "H"


class Long(Int32):
    """A long integer is an signed 4-byte, 32-bits wide integer type."""

    _format: str = "l"


class SignedLong(Int32):
    """A long integer is an signed 4-byte, 32-bits wide integer type."""

    _format: str = "l"


class UnsignedLong(UInt32):
    """An unsigned long integer is an unsigned 4-byte, 32-bits wide integer type."""

    _format: str = "L"


class LongLong(Int64):
    """A long long integer is an signed 8-byte, 64-bits wide integer type."""

    _format: str = "q"


# An alias for LongLong
class SignedLongLong(Int64):
    """A long long integer is an signed 8-byte, 64-bits wide integer type."""

    _format: str = "q"


class UnsignedLongLong(UInt64):
    """An unsinged long long integer is an unsigned 8-byte, 64-bits wide integer type."""

    _format: str = "Q"


class Size(UInt):
    """An unsigned integer type of the maximum byte width supported by the system."""

    # Determine the maximum system size for an integer
    for size, x in enumerate(range(0, 8), start=1):
        if sys.maxsize == (pow(2, pow(2, x) - 1) - 1):
            break
        else:
            size = 0

    # sys.maxsize accounts for signing, so returns a 1 byte less to account for this
    _length: int = (size + 1) if size > 0 else 0
    _signed: bool = False


class SignedSize(Size):
    """An signed integer type of the maximum byte width supported by the system."""

    _signed: bool = True


class UnsignedSize(Size):
    """An unsigned integer type of the maximum byte width supported by the system."""

    _signed: bool = False


class Float(float, Type):
    """Signed double-precision float type, 64-bits, 8-bytes of width."""

    _length: int = 8  # 8-byte, 64-bit signed float
    _format: str = "d"  # double-precision float
    _signed: bool = True
    _order: ByteOrder = ByteOrder.MSB
    _minimum: float = float("-inf")
    _maximum: float = float("inf")

    def __new__(cls, value: float, **kwargs):
        logger.debug(
            "%s.__new__(cls: %s, value: %s, kwargs: %s)",
            cls.__name__,
            cls,
            value,
            kwargs,
        )

        if not isinstance(value, (int, float)):
            raise ValueError(
                "The 'value' argument must have an integer or float value!"
            )

        return super().__new__(cls, value)

    def __bytes__(self) -> bytes:
        return self.encode()

    def __float__(self) -> float:
        return self

    def __int__(self) -> int:
        return int(self)

    def __bool__(self) -> bool:
        return self > 0.0

    def __len__(self) -> int:
        return len(bytes(self))

    def __getitem__(self, key: int) -> bytes:
        """Support obtaining individual bytes from the encoded version of the value."""

        encoded: bytes = bytes(self)

        if not (isinstance(key, int) and key >= 0):
            raise TypeError("The 'key' argument must have a positive integer value!")

        if key >= len(encoded):
            raise KeyError(
                "The 'key' argument must have a positive integer value that is in range of the element indicies that are available!"
            )

        return encoded[key]

    def __setitem__(self, key: int, value: int):
        raise NotImplementedError

    def __delitem__(self, key: int, value: int):
        raise NotImplementedError

    def __add__(self, other: float | int) -> Float:
        """Addition"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) + float(other))

    def __mul__(self, other: float | int) -> Float:
        """Multiply"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) * float(other))

    def __truediv__(self, other: float) -> Float:
        """True division"""
        if not isinstance(other, (int, float)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) / float(other))

    def __floordiv__(self, other: float | int) -> Float:
        """Floor division"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) // float(other))

    def __sub__(self, other: float | int) -> Float:
        """Subtraction"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) - float(other))

    def __mod__(self, other: float | int) -> Float:
        """Modulo"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) % float(other))

    def __pow__(self, other: float | int) -> Float:
        """Power"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) ** float(other))

    def __rshift__(self, other: float | int) -> Float:
        """Right bit shift"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) >> float(other))

    def __lshift__(self, other: float | int) -> Float:
        """Left bit shift"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) << float(other))

    def __and__(self, other: float | int) -> Float:
        """Binary AND"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) & float(other))

    def __or__(self, other: float | int) -> Float:
        """Binary OR"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) | float(other))

    def __xor__(self, other: float | int) -> Float:
        """Binary XOR"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) ^ float(other))

    def __iadd__(self, other: float | int) -> Float:
        """Asignment addition"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) + float(other))

    def __imul__(self, other: float | int) -> Float:
        """Asignment multiply"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) * float(other))

    def __idiv__(self, other: float | int) -> Float:
        """Asignment true division"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) / float(other))

    def __ifloordiv__(self, other: float | int) -> Float:
        """Asignment floor division"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) // float(other))

    def __isub__(self, other: float | int) -> Float:
        """Asignment subtract"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) - float(other))

    def __imod__(self, other: float | int) -> Float:
        """Asignment modulo"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) % float(other))

    def __ipow__(self, other: float | int) -> Float:
        """Asignment power"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) ** float(other))

    def __irshift__(self, other: float | int) -> Float:
        """Asignment right bit shift"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) >> float(other))

    def __ilshift__(self, other: float | int) -> Float:
        """Asignment left bit shift"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) << float(other))

    def __iand__(self, other: float | int) -> Float:
        """Asignment AND"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) & float(other))

    def __ior__(self, other: float | int) -> Float:
        """Asignment OR"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) | float(other))

    def __ixor__(self, other: float | int) -> Float:
        """Asignment XOR"""
        if not isinstance(other, (float, int)):
            raise TypeError("The 'other' argument must have a float or integer value!")
        return self.__class__(float(self) ^ float(other))

    def __neg__(self) -> Float:
        """Unary negation"""
        return self.__class__(-float(self))

    def __pos__(self) -> Float:
        """Unary positive"""
        return self.__class__(+float(self))

    def __invert__(self) -> Float:
        """Unary invert"""
        return self.__class__(~float(self))

    @classproperty
    def MIN(cls) -> float:
        """Return the minimum value that can be held by the type."""
        return cls._minimum

    @classproperty
    def MAX(cls) -> float:
        """Return the maximum value that can be held by the type."""
        return cls._maximum

    def encode(self, order: ByteOrder = ByteOrder.MSB) -> bytes:
        if not isinstance(self, Float):
            raise TypeError(
                "Ensure the 'encode' method is being called on a class instance!"
            )

        if not isinstance(order, ByteOrder):
            raise TypeError(
                "The 'order' argument must reference a ByteOrder enumeration option!"
            )

        if order is ByteOrder.MSB:
            format = f">{self._format}"
        elif order is ByteOrder.LSB:
            format = f"<{self._format}"

        return struct.pack(format, self)

    @classmethod
    def decode(
        cls, value: bytes | bytearray, order: ByteOrder = ByteOrder.MSB
    ) -> Float:
        if not isinstance(value, (bytes, bytearray)):
            raise TypeError(
                "The 'value' argument must have a bytes or bytearray value!"
            )
        elif not len(value) == cls._length:
            raise TypeError(
                f"The 'value' argument must have a length of {cls._length} bytes!"
            )

        if not isinstance(order, ByteOrder):
            raise TypeError(
                "The 'order' argument must reference a ByteOrder enumeration option!"
            )

        if order is ByteOrder.MSB:
            format = f">{cls._format}"
        elif order is ByteOrder.LSB:
            format = f"<{cls._format}"

        return cls(value=struct.unpack(format, bytes(value))[0])


class Float16(Float):
    _length: int = 2  # 2-byte, 16-bit signed float
    _format: str = "e"  # single-precision 2-byte, 16-bit float


class Float32(Float):
    _length: int = 4  # 4-byte, 32-bit signed float
    _format: str = "f"  # single-precision 4-byte, 32-bit float


class Float64(Float):
    _length: int = 8  # 8-byte, 64-bit signed float
    _format: str = "d"  # double-precision float


class Double(Float):
    _length: int = 8  # 8-byte, 64-bit signed float
    _format: str = "d"  # double-precision float


class Pointer(Size):
    pass


class Bytes(bytes, Type):
    _length: int = None

    def __new__(cls, value: bytes | bytearray | Int, length: int = None):
        if isinstance(value, Int):
            value = value.encode(order=ByteOrder.MSB)

        if not isinstance(value, (bytes, bytearray)):
            raise TypeError(
                "The 'value' argument must have a 'bytes' value or reference a 'bytesarray' instance!"
            )

        self = super().__new__(cls, value)

        if length is None:
            pass
        elif isinstance(length, int) and length >= 1:
            self._length: int = length
        else:
            raise TypeError(
                "The 'length' argument, if specified, must have a positive integer value!"
            )

        return self

    def encode(
        self, order: ByteOrder = ByteOrder.MSB, length: int = None, raises: bool = True
    ) -> bytes:
        if not isinstance(self, Bytes):
            raise TypeError(
                "Ensure the 'encode' method is being called on a class instance!"
            )

        if not isinstance(order, ByteOrder):
            raise TypeError(
                "The 'order' argument must have a ByteOrder enumeration value!"
            )

        if length is None:
            length = self._length
        elif not (isinstance(length, int) and length >= 1):
            raise TypeError(
                "The 'length' argument, if specified, must have a positive integer value!"
            )

        if not isinstance(raises, bool):
            raise TypeError("The 'raises' argument must have a boolean value!")

        encoded: bytesarray = bytearray()

        if order is ByteOrder.MSB:
            for index, byte in enumerate(self):
                # logger.debug("%s.encode(order: MSB) index => %s, byte => %s (%x)", self.__class__.__name__, index, byte, byte)
                encoded.append(byte)

            while len(encoded) < length:
                encoded.insert(0, 0)
        elif order is ByteOrder.LSB:
            for index, byte in enumerate(reversed(self)):
                # logger.debug("%s.encode(order: LSB) index => %s, byte => %s (%x)", self.__class__.__name__, index, byte, byte)
                encoded.append(byte)

            while len(encoded) < length:
                encoded.append(0)

        if raises is True and self.length and len(encoded) > self.length:
            raise ValueError(
                "The encoded bytes value is longer than that allowed by the Bytes subclass; the value encodes to %d bytes whereas the class allows %d bytes; ensure the value is in range, use a larger Bytes subclass or use the base Bytes class which by default imposes no length restrictions!"
                % (len(encoded), self.length)
            )

        return bytes(encoded)

    @classmethod
    def decode(cls, value: bytes | bytearray, order: ByteOrder = None) -> Bytes:
        if not isinstance(value, (bytes, bytearray)):
            raise TypeError(
                "The 'value' argument must have a bytes or bytearray value!"
            )

        if order is ByteOrder.LSB:
            value = bytes(reversed(value))

        return cls(value=bytes(value))


class Bytes8(Bytes):
    _length: int = 1  # 1 byte = 8 bits (1 * 8 = 8)


class Bytes16(Bytes):
    _length: int = 2  # 2 bytes = 16 bits (2 * 8 = 16)


class Bytes32(Bytes):
    _length: int = 4  # 4 bytes = 32 bits (4 * 8 = 32)


class Bytes64(Bytes):
    _length: int = 8  # 8 bytes = 64 bits (8 * 8 = 64)


class Bytes128(Bytes):
    _length: int = 16  # 16 bytes = 128 bits (16 * 8 = 128)


class Bytes256(Bytes):
    _length: int = 32  # 32 bytes = 256 bits (32 * 8 = 256)


class String(str, Type):
    """An unbounded string type which defaults to Unicode (UTF-8) encoding."""

    _encoding: Encoding = Encoding.UTF8  # Default encoding for Python 3 strings is UTF8

    def __new__(cls, value: str, *args, **kwargs):
        return super().__new__(cls, value, *args, **kwargs)

    @classproperty
    def encoding(cls) -> Encoding:
        return cls._encoding

    def encode(
        self,
        order: ByteOrder = ByteOrder.MSB,
        encoding: Encoding = None,
    ):
        if not isinstance(self, String):
            raise TypeError(
                "Ensure the 'encode' method is being called on a class instance!"
            )

        if encoding is None:
            encoding = self.encoding
        elif not isinstance(encoding, Encoding):
            raise TypeError(
                "The 'encoding' argument, if specified, must reference an Encoding enumeration option!"
            )

        if order is ByteOrder.MSB:
            return bytes(bytearray(str.encode(self, encoding.value)))
        elif order is ByteOrder.LSB:
            return bytes(reversed(bytearray(str.encode(self, encoding.value))))
        else:
            raise TypeError(
                "The 'order' argument must reference a ByteOrder enumeration option!"
            )

    @classmethod
    def decode(
        cls,
        value: bytes,
        order: ByteOrder = ByteOrder.MSB,
        encoding: Encoding = None,
    ) -> String:
        if not isinstance(value, bytes):
            raise TypeError("The 'value' argument must have a 'bytes' value!")

        if not isinstance(order, ByteOrder):
            raise TypeError(
                "The 'order' argument must reference a ByteOrder enumeration option!"
            )

        if encoding is None:
            encoding = cls.encoding
        elif not isinstance(encoding, Encoding):
            raise TypeError(
                "The 'encoding' argument, if specified, must reference an Encoding enumeration option!"
            )

        if order is ByteOrder.LSB:
            value = bytes(reversed(bytearray(value)))

        return cls(value.decode(encoding.value))


class Unicode(String):
    """An unbounded string type which defaults to Unicode (UTF-8) encoding."""

    _encoding: Encoding = Encoding.UTF8


class UTF8(Unicode):
    """An unbounded string type which defaults to Unicode (UTF-8) encoding."""

    _encoding: Encoding = Encoding.UTF8


class UTF16(Unicode):
    """An unbounded string type which defaults to Unicode (UTF-16) encoding."""

    _encoding: Encoding = Encoding.UTF16


class UTF32(Unicode):
    """An unbounded string type which defaults to Unicode (UTF-32) encoding."""

    _encoding: Encoding = Encoding.UTF32


class ASCII(String):
    """An unbounded string type which defaults to ASCII encoding."""

    _encoding: Encoding = Encoding.ASCII


class BytesView(object):
    _type: str = None

    _types: dict[str, dict] = {
        "x": {"size": 0, "signed": None, "type": None},
        "c": {"size": 1, "signed": None, "type": Char},
        "b": {"size": 1, "signed": True, "type": SignedChar},
        "B": {"size": 1, "signed": False, "type": UnsignedChar},
        "?": {"size": 1, "signed": None, "type": bool},
        "h": {"size": 2, "signed": True, "type": Short},
        "H": {"size": 2, "signed": False, "type": UnsignedShort},
        "i": {"size": 4, "signed": True, "type": Int32},
        "I": {"size": 4, "signed": False, "type": UInt32},
        "l": {"size": 4, "signed": True, "type": Long},
        "L": {"size": 4, "signed": False, "type": UnsignedLong},
        "q": {"size": 8, "signed": True, "type": LongLong},
        "Q": {"size": 8, "signed": False, "type": UnsignedLongLong},
        "n": {"size": 0, "signed": True, "type": SignedSize},
        "N": {"size": 0, "signed": False, "type": Size},
        "e": {"size": 2, "signed": True, "type": Float16},
        "f": {"size": 4, "signed": True, "type": Float32},
        "d": {"size": 8, "signed": True, "type": Double},
        "s": {"size": 0, "signed": None, "type": String},
        "p": {"size": 0, "signed": None, "type": Bytes},
        "P": {"size": 0, "signed": None, "type": Pointer},
    }

    _orders: list[str] = [
        "@",  # native (native size, native alignment)
        "=",  # native (standard size, no specific alignment)
        "<",  # little-endian (standard size, no specific alignment)
        ">",  # big-endian (standard size, no specific alignment)
        "!",  # network (big-endian, standard size, no specific alignment)
    ]

    def __init__(
        self,
        data: bytes | bytearray,
        split: int = 1,
        partial: bool = False,
        order: ByteOrder = ByteOrder.MSB,
    ):
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("The 'data' argument must have a bytes or bytearray value!")

        self._data = bytearray(data)

        self._size = len(self._data)

        if not isinstance(split, int):
            raise TypeError("The 'split' argument must have a positive integer value!")
        elif 1 <= split <= self._size:
            self._splits = split
        else:
            raise ValueError(
                "The 'split' argument must have a positive integer value between 1 and the length of the provided data, currently, %d!"
                % (self._size)
            )

        self.partial = partial

        self.order = order

    def __len__(self) -> int:
        parts: float = self._size / self._splits

        if self.partial is True:
            return math.ceil(parts)
        else:
            return math.floor(parts)

    def __iter__(self) -> BytesView:
        self._index = 0
        return self

    def __next__(self) -> bytearray | object:
        if self._index + self._splits > self._size:
            raise StopIteration

        value: bytes = self.data[self._index : self._index + self._splits]

        self._index += self._splits

        if isinstance(typed := self.typed, type):
            value = typed.decode(
                value=value,
                order=self.byteorder,
            )

        return value

    def __getitem__(self, index: int | slice) -> bytearray | object:
        logger.debug("%s.__getitem__(index: %r)", self.__class__.__name__, index)

        maxindex: int = math.floor(self._size / self._splits) - 1
        reverse: bool = False

        if isinstance(index, slice):
            start: int = index.start or 0
            stop: int = index.stop or self._size
            step: int = (0 - index.step) if (index.step or 1) < 0 else (index.step or 1)
            reverse: bool = (index.step or 1) < 0
        elif isinstance(index, int):
            if index >= 0:
                start: int = self._splits * index
                stop: int = start + self._splits
                step: int = 1
            else:
                raise ValueError(
                    "The 'index' argument must have a positive integer >= 0!"
                )

            if index > maxindex:
                if self.partial is True:
                    if (self._splits + (self._size - end)) < 0:
                        raise IndexError(
                            f"The index, {index}, is out of range; based on the length of the current data, {self._size}, and split length, {self._splits}, index must be between 0 – {maxindex}!"
                        )
                    else:
                        stop = self._size
                elif self.partial is False:
                    raise IndexError(
                        f"The index, {index}, is out of range; based on the length of the current data, {self._size}, and split length, {self._splits}, index must be between 0 – {maxindex}!"
                    )
        else:
            raise TypeError("The 'index' argument must have an integer or slice value!")

        # logger.debug(start, stop, step, "r" if reverse else "f")

        value = self.data[start:stop:step]

        if reverse is True:
            value = bytearray(reversed(value))

        if isinstance(typed := self.typed, type):
            value = typed.decode(
                value=value,
                order=self.byteorder,
            )

        return value

    @property
    def data(self) -> bytearray:
        return self._data

    @property
    def splits(self) -> int:
        return self._splits

    @splits.setter
    def splits(self, splits: int):
        if not isinstance(splits, int):
            raise TypeError("The 'splits' argument must have a positive integer value!")
        elif not 1 <= splits < self._size:
            raise ValueError(
                "The 'splits' argument must have a positive integer value between 1 and the length of the provided data, currently, %d!"
                % (self._size)
            )
        self._splits = splits

    @property
    def partial(self) -> bool:
        return self._partial

    @partial.setter
    def partial(self, partial: bool):
        if not isinstance(partial, bool):
            raise TypeError("The 'partial' argument must have a boolean value!")
        self._partial = partial

    @property
    def order(self) -> str:
        return self._order

    @order.setter
    def order(self, order: str | ByteOrder):
        if order is None:
            self._order = "@"
        elif isinstance(order, ByteOrder):
            if order is ByteOrder.MSB:
                self._order = ">"
            elif order is ByteOrder.LSB:
                self._order = "<"
        elif not isinstance(order, str):
            raise TypeError("The 'order' argument must have a string value!")
        elif order in self.orders:
            self._order = order
        else:
            raise ValueError(
                "The 'order' argument, if specified, must have one of the following values: %s!"
                % (", ".join(self.orders))
            )

    @property
    def orders(self) -> list[str]:
        return list(self._orders)

    @property
    def byteorder(self) -> ByteOrder:
        if self.order == "@" or self.order == "=":
            if sys.byteorder == "big":
                return ByteOrder.MSB
            elif sys.byteorder == "little":
                return ByteOrder.LSB
        elif self.order == ">":
            return ByteOrder.MSB
        elif self.order == "<":
            return ByteOrder.LSB
        elif self.order == "!":
            return ByteOrder.MSB

    @property
    def type(self) -> str | None:
        return self._type

    @type.setter
    def type(self, type: str):
        if type is None:
            self._type = None
        elif not isinstance(type, str):
            raise TypeError("The 'type' argument must have a string value!")
        elif type in self.types:
            self._type = type
        else:
            raise ValueError(
                "The 'type' argument, if specified, must have one of the following values: '%s', not '%s'!"
                % (
                    "', '".join(self.types.keys()),
                    type,
                )
            )

    @property
    def types(self) -> dict[str, dict]:
        return dict(self._types)

    @property
    def typed(self) -> type | None:
        if self.type:
            if isinstance(typed := self.types[self.type]["type"], type):
                logger.debug(
                    "%s.typed() => type => %r => class => %r",
                    self.__class__.__name__,
                    self.type,
                    typed,
                )

                return typed

    def split(self, split: int = None) -> BytesView:
        """The `split()` method supports changing the split length; it expects a value
        between `1` and the length in bytes of provided `data`, and returns a reference
        to `self` so calls can be chained with further calls including iteration."""

        if not isinstance(split, int):
            raise TypeError("The 'split' argument must have an integer value!")

        self.splits = split

        return self

    def cast(self, type: str | Type | None, order: ByteOrder = None) -> BytesView:
        """The `cast()` method supports casting the values held in the assigned `data`
        to one of the supported types offered by the `deliciousbytes` library, all of
        which are subclasses of native Python data types, so maybe used interchangeably.
        Using `cast()` implies a specific `split` length as each data type requires a
        certain number of raw bytes to be decoded into the native form. The `cast()`
        method returns a reference to `self` so calls can be chained with further calls
        including iteration."""

        if type is None:
            self.type = None
        elif isinstance(type, builtins.type) and issubclass(type, Type):
            if isinstance(format := type.format, str):
                self.type = format
            else:
                raise TypeError(
                    f"The 'type' argument referenced a Type subclass, '{type.__name__}', that cannot be cast!"
                )
        elif not isinstance(type, str):
            raise TypeError(
                "The 'type' argument must have a string value or reference a Type subclass!"
            )
        else:
            if not 1 <= len(type) <= 2:
                raise ValueError(
                    "The 'type' argument must have a length between 1 - 2 characters!"
                )
            elif len(type) == 2:
                self.order = type[0]
                self.type = type = type[1]
            elif isinstance(order, ByteOrder):
                if order is ByteOrder.MSB:
                    self.order = ">"
                elif order is ByteOrder.LSB:
                    self.order = "<"

            if type in self.types:
                self.type = type
                self.splits = struct.calcsize(f"{self.order}{self.type}")

                logger.debug(
                    "%s.cast() cast setup for type '%s%s' and length %d",
                    self.__class__.__name__,
                    self.order,
                    self.type,
                    self.splits,
                )
            else:
                raise ValueError(
                    "The 'type' argument, if specified, must have one of the following values: %s!"
                    % (", ".join(self.types.keys()))
                )

        return self

    def tell(self) -> int:
        """The 'tell' method provides support for reporting current the index position."""

        return self._index

    def seek(self, index: int) -> BytesView:
        """The 'seek' method provides support for moving the index to the specified position."""

        if not isinstance(index, int):
            raise TypeError("The 'index' argument must have an integer value!")
        elif 0 <= index < len(self):
            if self._splits > 1:
                self._index = self._splits * index
            else:
                self._index = index
        else:
            raise TypeError(
                f"The 'index' argument must have an integer value between 0 - {len(self) - 1}!"
            )

        return self

    def next(self, type: str | Type = None, order: ByteOrder = None) -> object | None:
        """The `next()` method supports obtaining the next group of bytes in the view,
        or optionally casting the value to one of the supported types offered by the
        `deliciousbytes` library, all of which are subclasses of native Python data
        types, so maybe used interchangeably.

        Using `next()` implies a specific `split` length as each data type requires a
        certain number of raw bytes to be decoded into its native form, so when calling
        `next()` and specifying an optional `type`, the split length will be changed
        accordingly for the current instance and will be used until it is updated again.

        The `next()` method may be called as many times as needed to obtain each group
        of bytes in the view, each time either with no defined type or with a different
        type each time, if the data being decoded requires it."""

        if type is None:
            pass
        elif not isinstance(type, (str, Type)):
            raise TypeError(
                "The 'type' argument, if specified, must have a string value or reference a Type subclass!"
            )

        try:
            return next(self.cast(type=type, order=order))
        except StopIteration:
            return None

    def decode(
        self, format: str, order: ByteOrder = None, index: int = 0
    ) -> tuple[Type]:
        """The decode method supports decoding the data held by a BytesView into a tuple
        of deliciousbytes.Type instances, which all subclass native Python types and may
        be used interchangably with native types.

        To decode raw bytes data held by a BytesView instance, specify a format string
        of one character per type to be decoded from the underlaying data; each type is
        specified by a character as per those defined in the `struct` module.

        The format string does not need to be long enough to decode all of the data held
        in the BytesView, but if the format string specifies more data types than held
        in the data, an error will be raised."""

        if not isinstance(self, BytesView):
            raise TypeError(
                "Ensure the 'decode' method is being called on a class instance!"
            )

        if not isinstance(format, str):
            raise TypeError("The 'format' argument must have a string value!")
        elif not len(format := format.strip()) > 0:
            raise TypeError("The 'format' argument must have a non-empty string value!")

        if len(format) >= 2 and format[0] in self.orders:
            order = format[0]
            format = format[1:]

        if order is None:
            byteorder: str = "@"
        elif isinstance(order, str) and order in self.orders:
            byteorder: str = order
        elif isinstance(order, ByteOrder):
            if order is ByteOrder.MSB:
                byteorder: str = ">"
            elif order is ByteOrder.LSB:
                byteorder: str = "<"
        else:
            raise TypeError(
                "The 'order' argument, if specified, must reference a ByteOrder enumeration option!"
            )

        if not isinstance(index, int):
            raise TypeError("The 'index' argument must have an integer value!")
        elif not 0 <= index < (datasize := len(self.data)):
            raise TypeError(
                f"The 'index' argument must have a positive integer value between 0 - {datasize}!"
            )

        if (calcsize := struct.calcsize(f"{byteorder}{format}")) > datasize:
            raise ValueError(
                f"The 'format' string specifies data types for more raw data than is available; the format string is calculated to require {calcsize} bytes, while the view currently holds {datasize} bytes!"
            )

        self.seek(index)

        types: list[str] = []

        number: str = ""

        # Support struct-style format strings which allow spaces and repeated types
        for char in format:
            if char.isspace():
                number = ""  # reset number; spaces cannot be between numbers and types
                continue  # spaces are ignored
            elif char in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                number += char
            elif char in self.types:
                if len(number) > 0:
                    if (count := int(number)) > 0:
                        for i in range(0, count):
                            types.append(char)
                    number = ""  # reset number now that we have encountered a type
                else:
                    types.append(char)
            elif char in self.orders:
                raise ValueError(
                    "The 'format' argument string contains a byte order specifier, '%s', in a location where it cannot be used; a byte order specifier can appear no more than once, and if included, it must be at the beginning of the format string!"
                    % (char)
                )
            else:
                raise ValueError(
                    "The 'format' argument string contains a type specifier, '%s', that is not recognized; type specifiers must be one of the following values: '%s'!"
                    % (char, "', '".join(self.types))
                )

        values: list[Type] = []

        # Iterate through the types, attempting to decode and cast each data type value
        for type in types:
            if isinstance(value := next(self.cast(type=type, order=order)), Type):
                values.append(value)
            else:
                values.append(None)

        return tuple(values)

    @classmethod
    def encode(
        cls,
        values: list[Type] | tuple[Type],
        order: ByteOrder = ByteOrder.MSB,
    ) -> BytesView:
        """The encode class method provides support for encoding one or more Type class
        instances to their underlying bytes values and concatenating those bytes to form
        the input data for a BytesView class instance that can then be used to further
        work with and manipulate the data as needed."""

        if not isinstance(values, (list, tuple)):
            raise TypeError(
                "The 'values' argument must reference a list or tuple of Type instances!"
            )

        if not isinstance(order, ByteOrder):
            raise TypeError(
                "The 'order' argument, if specified, must reference a ByteOrder enumeration option!"
            )

        data: bytearray = bytearray()

        for value in values:
            if not isinstance(value, Type):
                raise TypeError(
                    "All of the values provided to '%s.encode()' must be instances of Type!"
                    % (cls.__name__,)
                )

            data += value.encode(order=order)

        return BytesView(data, order=order)
