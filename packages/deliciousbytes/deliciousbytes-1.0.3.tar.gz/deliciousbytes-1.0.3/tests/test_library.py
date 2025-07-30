import pytest
import math
import sys

from deliciousbytes import (
    Encoding,
    ByteOrder,
    Type,
    Int,
    Int8,
    Int16,
    Int32,
    Int64,
    UInt,
    UInt8,
    UInt16,
    UInt32,
    UInt64,
    Char,
    SignedChar,
    UnsignedChar,
    Short,
    SignedShort,
    UnsignedShort,
    Long,
    UnsignedLong,
    SignedLong,
    LongLong,
    UnsignedLongLong,
    SignedLongLong,
    Size,
    SignedSize,
    UnsignedSize,
    Float,
    Float16,
    Float32,
    Float64,
    Double,
    Bytes,
    Bytes8,
    Bytes16,
    Bytes32,
    Bytes64,
    Bytes128,
    Bytes256,
    String,
    Unicode,
    UTF8,
    UTF16,
    UTF32,
    ASCII,
)

from deliciousbytes.utilities import print_hexbytes


def test_byte_order_enumeration():
    """Test the ByteOrder enumeration class."""

    assert ByteOrder.MSB is ByteOrder.BigEndian
    assert ByteOrder.MSB is ByteOrder.Motorolla
    assert ByteOrder.MSB is ByteOrder.Big

    assert ByteOrder.LSB is ByteOrder.LittleEndian
    assert ByteOrder.LSB is ByteOrder.Intel
    assert ByteOrder.LSB is ByteOrder.Little

    if sys.byteorder == "big":
        assert ByteOrder.Native is ByteOrder.MSB
    elif sys.byteorder == "little":
        assert ByteOrder.Native is ByteOrder.LSB


def test_encoding_enumeration():
    """Test the Encoding enumeration class."""

    assert Encoding.ASCII == "ascii"
    assert Encoding.Bytes == "bytes"
    assert Encoding.Unicode == "utf-8"
    assert Encoding.UTF8 == "utf-8"
    assert Encoding.UTF16 == "utf-16"
    assert Encoding.UTF32 == "utf-32"


def test_int():
    """Test the Int data type which subclases int, Python's arbitrarily long int type."""

    value: Int = Int(4000050)

    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 0  # byte length, 0 means unbounded, only limited by memory
    assert value.signed is True

    assert value == 4000050

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x3d\x09\x32"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x32\x09\x3d"


def test_int8():
    """Test the Int8 data type which is a fixed 1-byte, 8-bit signed integer type."""

    value: Int8 = Int8(127)

    assert isinstance(value, Int8)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 1  # byte length
    assert value.signed is True

    assert value == 127

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x7f"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x7f"


def test_int8_overflow():
    """Test the Int8 data type which is a fixed 1-byte, 8-bit signed integer type."""

    value: Int8 = Int8(129)

    assert isinstance(value, Int8)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 1  # byte length
    assert value.signed is True

    assert value == -127  # int8 129 overflows to -127

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x81"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x81"


def test_int16():
    """Test the Int16 data type which is a fixed 2-byte, 16-bit signed integer type."""

    value: Int16 = Int16(127)

    assert isinstance(value, Int16)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 2  # byte length
    assert value.signed is True

    assert value == 127

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x00\x7f"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x7f\x00"


def test_int32():
    """Test the Int32 data type which is a fixed 4-byte, 32-bit signed integer type."""

    value: Int32 = Int32(127)

    assert isinstance(value, Int32)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 4  # byte length
    assert value.signed is True

    assert value == 127

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x00\x00\x00\x7f"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x7f\x00\x00\x00"


def test_int64():
    """Test the Int64 data type which is a fixed 8-byte, 64-bit signed integer type."""

    value: Int64 = Int64(127)

    assert isinstance(value, Int64)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 8  # byte length
    assert value.signed is True

    assert value == 127

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x00\x00\x00\x00\x00\x00\x00\x7f"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x7f\x00\x00\x00\x00\x00\x00\x00"


def test_uint8():
    """Test the UInt8 data type which is a fixed 1-byte, 8-bit unsigned integer type."""

    value: UInt8 = UInt8(127)

    assert isinstance(value, UInt8)
    assert isinstance(value, UInt)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 1  # byte length
    assert value.signed is False

    assert value == 127

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x7f"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x7f"


def test_uint8_overflow():
    """Test the UInt8 data type which is a fixed 1-byte, 8-bit unsigned integer type."""

    value: UInt8 = UInt8(256)

    assert isinstance(value, UInt8)
    assert isinstance(value, UInt)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 1  # byte length
    assert value.signed is False

    assert value == 0  # uint8 256 overflows to 0

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x00"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x00"


def test_uint16():
    """Test the UInt16 data type which is a fixed 2-byte, 16-bit unsigned integer type."""

    value: UInt16 = UInt16(127)

    assert isinstance(value, UInt16)
    assert isinstance(value, UInt)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 2  # byte length
    assert value.signed is False

    assert value == 127

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x00\x7f"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x7f\x00"


def test_uint32():
    """Test the UInt32 data type which is a fixed 4-byte, 32-bit unsigned integer type."""

    value: UInt32 = UInt32(4000050)

    assert isinstance(value, UInt32)
    assert isinstance(value, UInt)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 4  # byte length
    assert value.signed is False

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x00\x3d\x09\x32"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x32\x09\x3d\x00"


def test_uint64():
    """Test the UInt64 data type which is a fixed 8-byte, 64-bit unsigned integer type."""

    value: UInt64 = UInt64(4000050)

    assert isinstance(value, UInt64)
    assert isinstance(value, UInt)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 8  # byte length
    assert value.signed is False

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x00\x00\x00\x00\x00\x3d\x09\x32"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x32\x09\x3d\x00\x00\x00\x00\x00"


def test_char():
    """Test the Char data type which is a fixed 1-byte, 8-bit unsigned integer type."""

    value: Char = Char("a")

    assert isinstance(value, Char)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 1  # byte length
    assert value.signed is False

    assert value == 97

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"a"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"a"


def test_signed_char():
    """Test the SignedChar data type which is a fixed 1-byte, 8-bit signed integer type."""

    value: SignedChar = SignedChar("a")

    assert isinstance(value, SignedChar)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 1  # byte length
    assert value.signed is True

    assert value == 97

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"a"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"a"


def test_unsigned_char():
    """Test the UnsignedChar data type which is a fixed 1-byte, 8-bit unsigned integer type."""

    value: UnsignedChar = UnsignedChar("a")

    assert isinstance(value, UnsignedChar)
    assert isinstance(value, Char)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 1  # byte length
    assert value.signed is False

    assert value == 97

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"a"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"a"


def test_short():
    """Test the Short data type which is a fixed 2-byte, 16-bit signed integer type."""

    value: Short = Short(127)

    assert isinstance(value, Short)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 2  # byte length
    assert value.signed is True

    assert value == 127

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x00\x7f"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x7f\x00"


def test_unsigned_short():
    """Test the UnsignedShort data type which is a fixed 2-byte, 16-bit unsigned integer type."""

    value: UnsignedShort = UnsignedShort(127)

    assert isinstance(value, UnsignedShort)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 2  # byte length
    assert value.signed is False

    assert value == 127

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x00\x7f"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x7f\x00"


def test_signed_short():
    """Test the SignedShort data type which is a fixed 2-byte, 16-bit signed integer type."""

    value: SignedShort = SignedShort(127)

    assert isinstance(value, SignedShort)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 2  # byte length
    assert value.signed is True

    assert value == 127

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x00\x7f"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x7f\x00"


def test_long():
    """Test the Long data type which is a fixed 4-byte, 32-bit signed integer type."""

    value: Long = Long(127)

    assert isinstance(value, Long)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 4  # byte length
    assert value.signed is True

    assert value == 127

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x00\x00\x00\x7f"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x7f\x00\x00\x00"


def test_unsigned_long():
    """Test the UnsignedLong data type which is a fixed 4-byte, 32-bit unsigned integer type."""

    value: UnsignedLong = UnsignedLong(127)

    assert isinstance(value, UnsignedLong)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 4  # byte length
    assert value.signed is False

    assert value == 127

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x00\x00\x00\x7f"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x7f\x00\x00\x00"

    # 5848 in big   endian is \x16\xd8
    # 5848 in litte endian is \xd8\x16

    data: Bytes = Bytes.decode(b"\xd8\x16", order=ByteOrder.LSB)
    assert isinstance(data, Bytes)
    assert data == b"\x16\xd8"  # Bytes.decode() flips the bytes to MSB order

    decoded: UInt32 = UInt32.decode(data)
    assert isinstance(decoded, UInt32)
    assert isinstance(decoded, int)
    assert decoded == 5848

    decoded: UInt64 = UInt64.decode(data)
    assert isinstance(decoded, UInt64)
    assert isinstance(decoded, int)
    assert decoded == 5848

    decoded: UnsignedLong = UnsignedLong.decode(data)
    assert isinstance(decoded, UnsignedLong)
    assert isinstance(decoded, int)
    assert decoded == 5848


def test_signed_long():
    """Test the SignedLong data type which is a fixed 4-byte, 32-bit signed integer type."""

    value: SignedLong = SignedLong(127)

    assert isinstance(value, SignedLong)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 4  # byte length
    assert value.signed is True

    assert value == 127

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x00\x00\x00\x7f"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x7f\x00\x00\x00"


def test_long_long():
    """Test the LongLong data type which is a fixed 8-byte, 64-bit signed integer type."""

    value: LongLong = LongLong(127)

    assert isinstance(value, LongLong)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 8  # byte length
    assert value.signed is True

    assert value == 127

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x00\x00\x00\x00\x00\x00\x00\x7f"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x7f\x00\x00\x00\x00\x00\x00\x00"


def test_unsigned_long_long():
    """Test the UnsignedLongLong data type which is a fixed 8-byte, 64-bit unsigned integer type."""

    value: UnsignedLongLong = UnsignedLongLong(127)

    assert isinstance(value, UnsignedLongLong)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 8  # byte length
    assert value.signed is False

    assert value == 127

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x00\x00\x00\x00\x00\x00\x00\x7f"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x7f\x00\x00\x00\x00\x00\x00\x00"


def test_signed_long_long():
    """Test the SignedLongLong data type which is a fixed 8-byte, 64-bit signed integer type."""

    value: SignedLongLong = SignedLongLong(127)

    assert isinstance(value, SignedLongLong)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length == 8  # byte length
    assert value.signed is True

    assert value == 127

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x00\x00\x00\x00\x00\x00\x00\x7f"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x7f\x00\x00\x00\x00\x00\x00\x00"


def test_size():
    """Test the Size data type which is a variable length unsigned integer type."""

    value: Size = Size(127)

    assert isinstance(value, Size)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length >= 1  # byte length
    assert value.signed is False

    assert value == 127

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded.endswith(b"\x00\x00\x00\x7f")

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded.startswith(b"\x7f\x00\x00\x00")


def test_signed_size():
    """Test the SignedSize data type which is a variable length signed integer type."""

    value: SignedSize = SignedSize(127)

    assert isinstance(value, SignedSize)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length >= 1  # byte length
    assert value.signed is True

    assert value == 127

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded.endswith(b"\x00\x00\x00\x7f")

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded.startswith(b"\x7f\x00\x00\x00")


def test_unsigned_size():
    """Test the UnsignedSize data type which is a variable length unsigned integer type."""

    value: UnsignedSize = UnsignedSize(127)

    assert isinstance(value, UnsignedSize)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    assert value.length >= 1  # byte length
    assert value.signed is False

    assert value == 127

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded.endswith(b"\x00\x00\x00\x7f")

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded.startswith(b"\x7f\x00\x00\x00")


def test_float():
    """Test the Float data type which is a 8-byte, 64-bit floating point type."""

    value: Float = Float(127.987)

    assert isinstance(value, Float)
    assert isinstance(value, float)

    assert value.length == 8  # byte length
    assert value.signed is True

    # Compare using math.isclose() due to float precision variance between systems
    assert math.isclose(value, 127.987)

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x40\x5f\xff\x2b\x02\x0c\x49\xba"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\xba\x49\x0c\x02\x2b\xff\x5f\x40"


def test_float16():
    """Test the Float16 data type which is a 2-byte, 16-bit floating point type."""

    value: Float16 = Float16(127.987)

    assert isinstance(value, Float16)
    assert isinstance(value, Float)
    assert isinstance(value, float)

    assert value.length == 2  # byte length
    assert value.signed is True

    # Note: 16 bit float looses some precision, will rounds to 128.0
    assert math.isclose(value, 127.987)

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x58\x00"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x00\x58"

    decoded: Float16 = Float16.decode(encoded, order=ByteOrder.LittleEndian)
    assert isinstance(decoded, Float16)
    assert isinstance(decoded, Float)
    assert isinstance(decoded, float)

    # Note: 16 bit float looses some precision, so 127.987 rounds to 128.0
    assert math.isclose(decoded, 128.0)


def test_float32():
    """Test the Float32 data type which is a 4-byte, 32-bit floating point type."""

    value: Float32 = Float32(127.987)

    assert isinstance(value, Float32)
    assert isinstance(value, Float)
    assert isinstance(value, float)

    assert value.length == 4  # byte length
    assert value.signed is True

    # Note: 32 bit float looses some precision, so 127.987 rounds to 127.98699951171875
    assert math.isclose(value, 127.987)

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x42\xff\xf9\x58"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x58\xf9\xff\x42"

    decoded: Float32 = Float32.decode(encoded, order=ByteOrder.LittleEndian)
    assert isinstance(decoded, Float32)
    assert isinstance(decoded, Float)
    assert isinstance(decoded, float)

    # Note: 32 bit float looses some precision, so 127.987 rounds to 127.98699951171875
    assert math.isclose(decoded, 127.98699951171875)


def test_float64():
    """Test the Float64 data type which is a 8-byte, 64-bit floating point type."""

    value: Float64 = Float64(127.987)

    assert isinstance(value, Float64)
    assert isinstance(value, Float)
    assert isinstance(value, float)

    assert value.length == 8  # byte length
    assert value.signed is True

    assert math.isclose(value, 127.987)

    encoded: bytes = value.encode(order=ByteOrder.BigEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x40\x5f\xff\x2b\x02\x0c\x49\xba"

    encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
    assert isinstance(encoded, bytes)
    assert encoded == b"\xba\x49\x0c\x02\x2b\xff\x5f\x40"

    decoded: Float64 = Float64.decode(encoded, order=ByteOrder.LittleEndian)
    assert isinstance(decoded, Float64)
    assert isinstance(decoded, Float)
    assert isinstance(decoded, float)

    assert math.isclose(decoded, 127.987)


def test_bytes64():
    """Test the Bytes64 data type which is a fixed 8-byte, 64-bit bytes type."""

    value: UInt32 = UInt32(4000050)

    assert isinstance(value, UInt32)
    assert isinstance(value, UInt)
    assert isinstance(value, Int)
    assert isinstance(value, int)

    value: Bytes64 = Bytes64(bytearray([byte for byte in bytes(value)]))

    assert isinstance(value, Bytes64)
    assert isinstance(value, Bytes)
    assert isinstance(value, bytes)

    encoded: bytes = value.encode(order=ByteOrder.MSB)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x00\x00\x00\x00\x00\x3d\x09\x32"

    encoded: bytes = value.encode(order=ByteOrder.LSB)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x32\x09\x3d\x00\x00\x00\x00\x00"


def test_string():
    """Test the String data type which is unbounded and defaults to UTF-8 encoding."""

    uncoded: String = String("hello")

    assert isinstance(uncoded, String)
    assert isinstance(uncoded, str)

    # As String is a subclass of 'str' we can compare values directly
    assert uncoded == "hello"
    assert uncoded.encoding is Encoding.UTF8

    encoded: bytes = uncoded.encode(order=ByteOrder.MSB)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x68\x65\x6c\x6c\x6f"

    encoded: bytes = uncoded.encode(order=ByteOrder.LSB)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x6f\x6c\x6c\x65\x68"

    decoded = String.decode(b"\x68\x65\x6c\x6c\x6f", order=ByteOrder.MSB)
    assert isinstance(decoded, String)
    assert isinstance(decoded, str)

    # As String is a subclass of 'str' we can compare values directly
    assert decoded == "hello"
    assert decoded.encode(order=ByteOrder.MSB) == b"\x68\x65\x6c\x6c\x6f"


def test_unicode():
    """Test the Unicode data type which is unbounded and defaults to UTF-8 encoding."""

    uncoded: Unicode = Unicode("hello")

    assert isinstance(uncoded, Unicode)
    assert isinstance(uncoded, String)
    assert isinstance(uncoded, str)

    # As Unicode is ultimately a subclass of 'str' we can compare values directly
    assert uncoded == "hello"
    assert uncoded.encoding is Encoding.UTF8

    encoded: bytes = uncoded.encode(order=ByteOrder.MSB)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x68\x65\x6c\x6c\x6f"

    encoded: bytes = uncoded.encode(order=ByteOrder.LSB)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x6f\x6c\x6c\x65\x68"

    decoded = Unicode.decode(b"\x68\x65\x6c\x6c\x6f", order=ByteOrder.MSB)
    assert isinstance(decoded, Unicode)
    assert isinstance(decoded, String)
    assert isinstance(decoded, str)

    # As Unicode is ultimately a subclass of 'str' we can compare values directly
    assert decoded == "hello"
    assert decoded.encode(order=ByteOrder.MSB) == b"hello"


def test_utf8():
    """Test the UTF8 data type which is unbounded and uses UTF-8 encoding."""

    uncoded: UTF8 = UTF8("hello")

    assert isinstance(uncoded, UTF8)
    assert isinstance(uncoded, Unicode)
    assert isinstance(uncoded, String)
    assert isinstance(uncoded, str)

    # As UTF8 is ultimately a subclass of 'str' we can compare values directly
    assert uncoded == "hello"
    assert uncoded.encoding is Encoding.UTF8

    encoded: bytes = uncoded.encode(order=ByteOrder.MSB)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x68\x65\x6c\x6c\x6f"

    encoded: bytes = uncoded.encode(order=ByteOrder.LSB)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x6f\x6c\x6c\x65\x68"

    decoded = UTF8.decode(b"\x68\x65\x6c\x6c\x6f", order=ByteOrder.MSB)
    assert isinstance(decoded, UTF8)
    assert isinstance(decoded, Unicode)
    assert isinstance(decoded, String)
    assert isinstance(decoded, str)

    # As UTF8 is ultimately a subclass of 'str' we can compare values directly
    assert decoded == "hello"
    assert decoded.encode(order=ByteOrder.MSB) == b"\x68\x65\x6c\x6c\x6f"


def test_utf16():
    """Test the UTF16 data type which is unbounded and uses UTF-16 encoding."""

    uncoded: UTF16 = UTF16("hello")

    assert isinstance(uncoded, UTF16)
    assert isinstance(uncoded, Unicode)
    assert isinstance(uncoded, String)
    assert isinstance(uncoded, str)

    # As UTF16 is ultimately a subclass of 'str' we can compare values directly
    assert uncoded == "hello"
    assert uncoded.encoding is Encoding.UTF16

    encoded: bytes = uncoded.encode(order=ByteOrder.MSB)
    assert isinstance(encoded, bytes)
    assert encoded == b"\xff\xfe\x68\x00\x65\x00\x6c\x00\x6c\x00\x6f\x00"

    encoded: bytes = uncoded.encode(order=ByteOrder.LSB)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x00\x6f\x00\x6c\x00\x6c\x00\x65\x00\x68\xfe\xff"

    decoded = UTF16.decode(encoded, order=ByteOrder.LSB)
    assert isinstance(decoded, UTF16)
    assert isinstance(decoded, Unicode)
    assert isinstance(decoded, String)
    assert isinstance(decoded, str)

    # As UTF16 is ultimately a subclass of 'str' we can compare values directly
    assert decoded == "hello"
    assert (
        decoded.encode(order=ByteOrder.MSB)
        == b"\xff\xfe\x68\x00\x65\x00\x6c\x00\x6c\x00\x6f\x00"
    )


def test_utf32():
    """Test the UTF32 data type which is unbounded and uses UTF-32 encoding."""

    uncoded: UTF32 = UTF32("hello")

    assert isinstance(uncoded, UTF32)
    assert isinstance(uncoded, Unicode)
    assert isinstance(uncoded, String)
    assert isinstance(uncoded, str)

    # As UTF32 is ultimately a subclass of 'str' we can compare values directly
    assert uncoded == "hello"
    assert uncoded.encoding is Encoding.UTF32

    encoded: bytes = uncoded.encode(order=ByteOrder.MSB)
    assert isinstance(encoded, bytes)
    assert (
        encoded
        == b"\xff\xfe\x00\x00\x68\x00\x00\x00\x65\x00\x00\x00\x6c\x00\x00\x00\x6c\x00\x00\x00\x6f\x00\x00\x00"
    )

    encoded: bytes = uncoded.encode(order=ByteOrder.LSB)
    assert isinstance(encoded, bytes)
    assert (
        encoded
        == b"\x00\x00\x00\x6f\x00\x00\x00\x6c\x00\x00\x00\x6c\x00\x00\x00\x65\x00\x00\x00\x68\x00\x00\xfe\xff"
    )

    decoded = UTF32.decode(encoded, order=ByteOrder.LSB)
    assert isinstance(decoded, UTF32)
    assert isinstance(decoded, Unicode)
    assert isinstance(decoded, String)
    assert isinstance(decoded, str)

    # As UTF32 is ultimately a subclass of 'str' we can compare values directly
    assert decoded == "hello"
    assert (
        decoded.encode(order=ByteOrder.MSB)
        == b"\xff\xfe\x00\x00\x68\x00\x00\x00\x65\x00\x00\x00\x6c\x00\x00\x00\x6c\x00\x00\x00\x6f\x00\x00\x00"
    )


def test_ascii():
    """Test the ASCII data type which is unbounded and uses ASCII encoding."""

    uncoded: ASCII = ASCII("hello")

    assert isinstance(uncoded, ASCII)
    assert isinstance(uncoded, String)
    assert isinstance(uncoded, str)

    # As ASCII is ultimately a subclass of 'str' we can compare values directly
    assert uncoded == "hello"
    assert uncoded.encoding is Encoding.ASCII

    encoded: bytes = uncoded.encode(order=ByteOrder.MSB)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x68\x65\x6c\x6c\x6f"

    encoded: bytes = uncoded.encode(order=ByteOrder.LSB)
    assert isinstance(encoded, bytes)
    assert encoded == b"\x6f\x6c\x6c\x65\x68"

    decoded = ASCII.decode(encoded, order=ByteOrder.LSB)
    assert isinstance(decoded, ASCII)
    assert isinstance(decoded, String)
    assert isinstance(decoded, str)

    # As ASCII is ultimately a subclass of 'str' we can compare values directly
    assert decoded == "hello"
    assert decoded.encode(order=ByteOrder.MSB) == b"\x68\x65\x6c\x6c\x6f"
