# DeliciousBytes

The `deliciousbytes` library provides a range of data types that can be encoded into and
decoded from their binary forms which is useful when working with data that is stored in
certain file formats or transmitted over networks with certain encodings.

The data types provided by the library all subclass their corresponding native Python
types so can be used interchangeably with those types while offering standardised support
for decoding from and encoding into binary forms according to the specified byte order.

The library provides a range of signed and unsigned integer types of fixed lengths,
`char`, unsigned `char`, equivalents for signed and unsigned `short`, signed and unsigned
`long`, signed and unsigned `long long`, as well as `float`, `double`, and `bytes` and
various string types of different default character encodings.

The integer types automatically overflow if the specified value is out of range, for
example if the unsigned 8-bit integer type, `UInt8`, which can hold `255` as its largest
value, is instantiated with a value of `256` it will automatically overflow to `0`, and
if a signed 8-bit integer type, `Int8`, which can hold a minimum value of `-127` and a
maximum value of `128` is instantiated with a value of `129` it will overflow to `-127`.

While many of the built-in types offer conversion operations to and from their binary
forms, the library provides a consistent interface across the data types to achieve this
as well as the encoding and decoding of bytes and string values with defined endianness.

### Requirements

The DeliciousBytes library has been tested with Python 3.10, 3.11, 3.12 and 3.13. The
library has not been tested with and is likely incompatible with Python 3.9 and earlier.

### Installation

The DeliciousBytes library is available from PyPI, so may be added to a project's dependencies
via its `requirements.txt` file or similar by referencing the DeliciousBytes library's name,
`deliciousbytes`, or the library may be installed directly into your local runtime environment
using `pip` via the `pip install` command by entering the following into your shell:

	$ pip install deliciousbytes

### Example Usage

To use the DeliciousBytes library, import the library and the data type or data types
one needs for a given project and use them just like their regular counterparts. When
required, each of the types' `encode()` and `decode()` methods provide support for
encoding and decoding the values to and from their binary representations:

```python
from deliciousbytes import (
    Int, Int8, ByteOrder,
)

value: Int8 = Int8(127)

assert isinstance(value, Int8)
assert isinstance(value, Int)
assert isinstance(value, int)

assert value == 127

encoded: bytes = value.encode(order=ByteOrder.BigEndian)
assert isinstance(encoded, bytes)
assert encoded == b"\x7f"

encoded: bytes = value.encode(order=ByteOrder.LittleEndian)
assert isinstance(encoded, bytes)
assert encoded == b"\x7f"
```

<a id='classes-and-methods'></a>
### Classes & Methods

The DeliciousBytes library provides the following data type classes, all of which are
ultimately a subclass of one of the native Python data type classes so all instances of
the classes below can be used interchangeably with their native Python data types; each
data type class is also a subclasses of the `deliciousbytes.Type` superclass, from which
they inherit shared behaviour and class hierarchy membership:

| Class              | Description                            | Subclass Of | Format   |
|--------------------|----------------------------------------|-------------|:--------:|
| `Int`              | Signed unbounded integer               | `int`       |          |
| `Int8`             | Signed 8-bit integer                   | `Int`       |          |
| `Int16`            | Signed 16-bit integer                  | `Int`       |          |
| `Int32`            | Signed 32-bit integer                  | `Int`       |          |
| `Int64`            | Signed 64-bit integer                  | `Int`       |          |
| `UInt`             | Unsigned unbounded integer             | `Int`       |          |
| `UInt8`            | Unsigned 8-bit integer                 | `UInt`      |          |
| `UInt16`           | Unsigned 16-bit integer                | `UInt`      |          |
| `UInt32`           | Unsigned 32-bit integer                | `UInt`      |          |
| `UInt64`           | Unsigned 64-bit integer                | `UInt`      |          |
| `Char`             | An 8-bit integer, defaults to unsigned | `UInt8`     | `c`      |
| `SignedChar`       | Signed 8-bit integer                   | `Int8`      | `b`      |
| `UnsignedChar`     | Unsigned 8-bit integer                 | `UInt8`     | `B`      |
| `Short`            | Signed short (16-bit) integer          | `Int16`     | `h`      |
| `SignedShort`      | An alias for `Short`                   | `Short`     | `h`      |
| `UnsignedShort`    | Unsigned short (16-bit) integer        | `UInt16`    | `H`      |
| `Long`             | Signed long (32-bit) integer           | `Int32`     | `l`      |
| `SignedLong`       | An alias for `Long`                    | `Long`      | `l`      |
| `UnsignedLong`     | Unsigned long (32-bit) integer         | `UInt32`    | `L`      |
| `LongLong`         | Signed long long (64-bit) integer      | `Int64`     | `q`      |
| `SignedLongLong`   | An alias for `LongLong`                | `LongLong`  | `q`      |
| `UnsignedLongLong` | Unsigned long long (64-bit) integer    | `UInt64`    | `Q`      |
| `Size`             | A unsigned integer type of system size | `UInt`      | `n`      |
| `SignedSize`       | A signed integer type of system size   | `Int`       | `N`      |
| `UnsignedSize`     | An alias for `Size`                    | `Size`      | `n`      |
| `Float`            | A float type, defaulting to 64-bit     | `float`     | `d`      |
| `Float16`          | 16-bit float type                      | `Float`     | `e`      |
| `Float32`          | 32-bit float type                      | `Float`     | `f`      |
| `Float64`          | 64-bit float type                      | `Float`     | `d`      |
| `Double`           | An alias for `Float64`                 | `Float64`   | `d`      |
| `Pointer`          | A signed integer type of system size   | `Size`      | `P`      |
| `Bytes`            | Unbounded bytes type                   | `bytes`     | `p`      |
| `Bytes8`           | 8-bit bytes type                       | `Bytes`     |          |
| `Bytes16`          | 16-bit bytes type                      | `Bytes`     |          |
| `Bytes32`          | 32-bit bytes type                      | `Bytes`     |          |
| `Bytes64`          | 64-bit bytes type                      | `Bytes`     |          |
| `Bytes128`         | 128-bit bytes type                     | `Bytes`     |          |
| `Bytes256`         | 256-bit bytes type                     | `Bytes`     |          |
| `String`           | Unbounded string type                  | `str`       | `s`      |
| `Unicode`          | Unbounded UTF-8 string type            | `String`    |          |
| `UTF8`             | Unbounded UTF-8 string type            | `Unicode`   |          |
| `UTF16`            | Unbounded UTF-16 string type           | `Unicode`   |          |
| `UTF32`            | Unbounded UTF-32 string type           | `Unicode`   |          |
| `ASCII`            | Unbounded ASCII string type            | `String`    |          |

The unbounded types have no length/size restrictions on the values that they can hold
beyond those imposed by the Python interpreter being used. The bounded types do impose a
limit on the length/size of the values that they can hold, for example the `UInt8` type
can hold a minimum value of `0` and a maximum value of `255` being an 8-bit unsigned int
value; larger values will overflow, be trimmed, or result in an exception being raised
depending on the data type being used.

While on some platforms, the `short`, `long`, and `long long` types and their `unsigned`
equivalents guarantee a minimum of `16`, `32` or `64` bits respectively they are aliases
for the equivalent fixed length types in this library. See the [**Data Type Sizes**](#data-type-sizes)
section for more information on the types, and where applicable, their minimum and maximum values.

As each of the type classes ultimately subclass from one of the native Python data types
the class instances can be used interchangeably with their native Python counterparts.

Each of the data type classes provide the following methods:

 * `encode(order: ByteOrder = ByteOrder.MSB)` (`bytes`) – The `encode()` method provides
support for encoding the value held by the type into its binary representation according
to the byte order defined during the call to the method. The byte order defaults to most
significant bit first, and is represented by the `ByteOrder` enumeration class which
provides enumeration options to specify the endianness that is needed for the use case.
 
 * `decode(value: bytes, order: ByteOrder = ByteOrder.MSB)` (`object`) – The `decode()`
methods on each of the data type classes are class rather than instance methods, so must
be called on the class type rather than on an instance of the class. The method takes a
binary encoded value provided via a `bytes` data type value, and decodes the value into
its native data type value. The byte order defaults to most-significant bit first, and
is represented by the `ByteOrder` enumeration class which provides enumeration options
to specify the endianness that is needed for the use case.

The `deliciousbytes` class also provides a `ByteView` class which provides a method for
iterating over bytes, either as individual bytes or in groups of bytes of the specified
split size, where these bytes may be accessed as raw `bytes` values or cast into one of
the supported types. The class also supports indexed item and slice access semantics.

The `ByteView` class offers the following methods:

 * `__init__(data: bytes | bytearray)` – The `__init__()` method expects a `bytes` or `bytearray` object as input via the `data` argument, and will also accept any of the following optional keyword arguments:
   * `split` (`int`) – The `split` argument defines how many bytes are put into each group for iterating over; by default it is set to `1` so each individual byte can be accessed independently; if the supplied `data` holds bytes that represent data that spans multiple bytes, say each two bytes represent a value, the `split` can be set to two, and groups of two bytes will be returned during iteration. The `split` length can also be changed at any time after initialisation, which can be especially useful when `data` holds bytes for mixed data types where it may be necessary to obtain two bytes, then four bytes, then two bytes, etc.

   * `partial` (`bool`) – The `partial` argument defines if the view should allow iteration to continue after all whole groups have been iterated over; that is if the length of `data` is not evenly divisible by `split`, there could be a partial group of bytes left over at the end; say `data` is 10 bytes long, and `split` is set to `3`, there would be `3` groups of `3` bytes each, with `1` byte remaining; by default `partial` is set to `False` so this last group would not be returned during iteration; setting `partial` to `True` ensures that it is.

   * `order` (`ByteOrder`) – The `order` argument defines the byte order of the data for decoding purposes; by default it is set to big-endian (`ByteOrder.MSB`), but can be set to little-endian via `ByteOrder.LSB` or one of the equivalent `ByteOrder` enumeration options, or one of the byte order characters supported by the `struct` module, `@`, `=`, `>`, `<` and `!`, can be used instead. See the [**Byte Order**](#byte-order) section for more information.

 * `__len__()` (`int`) – The `__len__()` method returns the current number of items that the `BytesView` class can iterate over; the returned length is dependent upon the length of the assigned `data` value and the current `split` length, so the reported length can change if the `split` length is changed; it is also dependent upon if `partial` iteration is enabled or not, and if the length of `data` is evenly divisible by the `split` length or not.

 * `__iter__()` (`BytesView`) – The `__iter__()` method supports iterating over a `BytesView` class instance using standard constructs such as a `for ... in ...` loop; an iterator can also be obtained by passing the class instance to the `iter()` standard library method.

 * `__next__()` (`bytes` | `object`) – The `__next__()` method supports iterating over a `BytesView` class instance using standard constructs such as a `for ... in ...` loop, and returns the next available group of bytes in the view.

 * `__getitem__(index: int)` (`bytes` | `object`) – The `__getitem__()` method supports item access to the groups of bytes in the view as defined by the group's index. If the specified index is out-of-bounds a `KeyError` exception will be raised.

 * `split(length: int)` (`BytesView`) – The `split()` method supports changing the split length after class initialisation; it expects a positive integer value between `1` and the length in bytes of provided `data`, and returns a reference to `self` so calls to `split()` can be chained with further calls including iteration.

 * `cast(type: Type | str, order: ByteOrder = None)` (`bytes` | `object`) – The `cast()` method supports casting the values held in the assigned `data` to one of the supported types offered by the `deliciousbytes` library, all of which are subclasses of native Python data types, so maybe used interchangeably. Using `cast()` implies a specific `split` length as each data type requires a certain number of raw bytes to be decoded into the native form. The `cast()` method returns a reference to `self` so calls to `cast()` can be chained with further calls including iteration.

 * `next(type: Type | str = None, order: ByteOrder = None)` (`bytes` | `object`) – The `next()` method supports obtaining the next group of bytes in the view, or optionally casting the value to one of the supported types offered by the `deliciousbytes` library, all of which are subclasses of native Python data types, so maybe used interchangeably. Using `next()` implies a specific `split` length as each data type requires a certain number of raw bytes to be decoded into the native form, so when calling `next()` and specifying an optional `type`, the split length will be changed accordingly. The `next()` method may be called as many times as needed to obtain each group of bytes in the view, each time either with no defined `type` or with a different `type` if the data being decoded requires it.

 * `tell()` (`int`) – The `tell()` method returns the current index position which is updated after each iteration; the `index` starts at `0` and is advanced during each iteration step, so at any given time it reports the index of the next item to be retrieved from the view.

 * `seek(index: int)` (`BytesView`) – The `seek()` method provides support for moving the index to the specified position. The `seek()` method returns a reference to `self` so calls to `seek()` can be chained with further calls including iteration.

 * `decode(format: str, order: ByteOrder = None, index: int = 0)` (`tuple[Type]`) – The `decode()` method provides support for decoding and casting a group of items to one or more of the `deliciousbytes.Type` subclasses by specifying a format string; the count of items returned depends upon the number of characters in the format string, less the optional byte order mark `>` or `<` at the beginning of the format string; note that the `.decode()` method always returns a tuple even if only a single value is decoded. Format strings do not need to provide instructions for decoding every value in the data, but if the format string requests more values than held in the provided raw data an exception will be raised.

 * `encode(values: list[Type], order: ByteOrder = None)` (`BytesView`) – The `encode()` class method provides support for encoding one or more `deliciousbytes.Type` subclass instances to their underlying `bytes` values and concatenating those `bytes` to form the input data for a `BytesView` class instance that can then be used to further work with and manipulate the data as needed.

The `ByteView` class offers the following properties:

 * `data` (`bytes` | `bytearray`) – The `data` property returns the data held by the `BytesView` class.

 * `splits` (`int`) – The `splits` property returns the current split length value; it can also be used to update the split length value in addition to calling the `split()` method; if setting `splits` it must be assigned to a positive `int` value between `1` and the length in bytes of the `data` assigned to the class.

 * `partial` (`bool`) – The `partial` property returns the current partial iteration status, where `True` indicates that iteration will include any partial groups of bytes at the end of the list, as detailed above, and `False` indicates that iteration will stop after iterating over all whole groups of bytes. The `partial` property can also be used to update the `partial` property; if setting `partial` it must be assigned to a `bool` value.

 * `order` (`ByteOrder`) – The `order` property returns the current byte order configured for the view; it can also be used to update the byte order; if setting `order` it must be assigned to a `ByteOrder` enumeration option.

```python
from deliciousbytes import (
    Int, Int8, ByteOrder, BytesView,
)

data: bytes = b"\x00\x01\x00\x02\x00\x03\x00\x04"

view = BytesView(data, split=2)

assert isinstance(view, BytesView)

# The length reflects the current length of the data as divided by the split size
# This is the number of items that can iterated over in the view where the maximum index
# that can be used during iteration or item level access is the reported length - 1.
assert len(view) == 4

# The items can be iterated over using normal iterator semantics such as for/enumerate
for index, val in enumerate(view):
    if index == 0:
        assert val == b"\x00\x01"
    elif index == 1:
        assert val == b"\x00\x02"
    elif index == 2:
        assert val == b"\x00\x03"
    elif index == 3:
        assert val == b"\x00\x04"

# Individual groups of bytes (based on the split size) can be accessed using item access
assert view[0] == b"\x00\x01"
assert view[1] == b"\x00\x02"
assert view[2] == b"\x00\x03"
assert view[3] == b"\x00\x04"

# Note: When slicing access is used, the current split size is ignored

# Test obtaining bytes from 1 until 4 (i.e. bytes 1, 2, 3)
assert view[1:4] == b"\x01\x00\x02"

# Test obtaining bytes from 0 until 4 (i.e. bytes 0, 1, 2, 3)
assert view[0:4:+1] == b"\x00\x01\x00\x02"

# Test obtaining bytes from 0 until 8, stepping 2 bytes each time
assert view[0:8:+2] == b"\x00\x00\x00\x00"

# Test obtaining bytes from 1 until 8, stepping 2 bytes each time
assert view[1:8:+2] == b"\x01\x02\x03\x04"

# Test obtaining bytes from 0 until 8, stepping -2 bytes each time, i.e. reversed
assert view[1:8:-2] == b"\x04\x03\x02\x01"

# Test obtaining bytes from 0 until 4, stepping -1 bytes each time, i.e. reversed
assert view[0:4:-1] == b"\x02\x00\x01\x00"

# The split length can be changed at any point
for index, val in enumerate(view.split(4)):
    if index == 0:
        assert val == b"\x00\x01\x00\x02"
    elif index == 1:
        assert val == b"\x00\x03\x00\x04"

# The last split length will be remembered (!)
assert view[0] == b"\x00\x01\x00\x02"
assert view[1] == b"\x00\x03\x00\x04"

# Item values can be cast from raw bytes to the defined type; note that casting implies
# an associated split size as each type cast requires the relevant number of bytes for
# decoding into the defined type:
for index, val in enumerate(view.cast(">h")):
    if index == 0:
        assert val == 1
    elif index == 1:
        assert val == 2
    elif index == 2:
        assert val == 3
    elif index == 3:
        assert val == 4

# Items can be cast as a group via .decode() by specifying a format string; the count of
# items returned depends upon the number of characters in the format string, less the
# optional byte order mark `>` or `<` at the beginning of the format string; note that
# the .decode() method always returns a tuple even if only a single value is decoded:
assert view.decode(">h") == (1, )
assert view.decode(">hh") == (1, 2)
assert view.decode(">hhh") == (1, 2, 3)
assert view.decode(">hhhh") == (1, 2, 3, 4)
```

<a id='byte-order'></a>
### Byte Order

The byte order for each of the data type classes defaults to most-significant bit first,
MSB, but may be changed to least-significant bit first, LSB, if needed. The `ByteOrder`
enumeration class value offers enumeration options to specify the endianness that is
needed for the use case, and for convenience provides the enumerations in a few flavours
depending on how one prefers to refer to endianness:

| Enumeration Option             | Byte Order | Endianness |
|--------------------------------|------------|------------|
| `ByteOrder.MSB`                | MSB        | Big        |
| `ByteOrder.LSB`                | LSB        | Little     |
| `ByteOrder.Motorolla`          | MSB        | Big        |
| `ByteOrder.Intel`              | LSB        | Little     |
| `ByteOrder.BigEndian`          | MSB        | Big        |
| `ByteOrder.LittleEndian`       | LSB        | Little     |
| `ByteOrder.Big`                | MSB        | Big        |
| `ByteOrder.Little`             | LSB        | Little     |
| `ByteOrder.Native`             | Native     | Native     |

* The `ByteOrder.Native` option will report the system's native byte, returning either
`ByteOrder.MSB` for big endian systems or `ByteOrder.LSB` for little endian systems.

The `struct` module byte order mark equivalents are handled as follows:

| Struct Byte Order Mark | Byte Order | Alignment | Notes                              |
|------------------------|------------|-----------|------------------------------------|
| `@`                    | System     | Native    | Alignment is not handled           |
| `=`                    | System     | N/A       |                                    |
| `>`                    | MSB        | N/A       |                                    |
| `<`                    | LSB        | N/A       |                                    |
| `!`                    | MSB        | N/A       | Most network protocols use MSB     |

If either system dependent byte order mark, `@` or `=` is specified, the byte order will
be determined based on the endianness reported by Python's `sys.byteorder` property, so
systems reporting `big` endianness will map to `ByteOrder.MSB` and systems reporting
`little` endianness will map to `ByteOrder.LSB`.

<a id='data-type-sizes'></a>
### Data Type Sizes

| Class              | Bytes | Minimum Value              | Maximum Value              |
|--------------------|:-----:|----------------------------|----------------------------|
| `Int`              | `1+`  | (depends on system)        | (depends on system)        |
| `Int8`             | `1`   | -127                       | +128                       |
| `Int16`            | `2`   | -32,768                    | +32,767                    |
| `Int32`            | `4`   | -2,147,483,648             | +2,147,483,647             |
| `Int64`            | `8`   | -9,223,372,036,854,775,808 | +9,223,372,036,854,775,807 |
| `UInt`             | `1+`  | +0                         | (depends on system)        |
| `UInt8`            | `1`   | +0                         | +255                       |
| `UInt16`           | `2`   | +0                         | +65,535                    |
| `UInt32`           | `4`   | +0                         | +429,496,729               |
| `UInt64`           | `8`   | +0                         | +1.844,674,407,370,955e19  |
| `Char`             | `1`   | +0                         | +255                       |
| `SignedChar`       | `1`   | -127                       | +128                       |
| `UnsignedChar`     | `1`   | +0                         | +255                       |
| `Short`            | `2`   | -32,768                    | +32,767                    |
| `SignedShort`      | `2`   | -32,768                    | +32,767                    |
| `UnsignedShort`    | `2`   | +0                         | +65,535                    |
| `Long`             | `4`   | -2,147,483,648             | +2,147,483,647             |
| `SignedLong`       | `4`   | -2,147,483,648             | +2,147,483,647             |
| `UnsignedLong`     | `4`   | +0                         | +429,496,729               |
| `LongLong`         | `8`   | -9,223,372,036,854,775,808 | +9,223,372,036,854,775,807 |
| `SignedLongLong`   | `8`   | -9,223,372,036,854,775,808 | +9,223,372,036,854,775,807 |
| `UnsignedLongLong` | `8`   | +0                         | +1.844,674,407,370,955e19  |
| `Size`             | `1+`  | +0                         | (depends on system)        |
| `SignedSize`       | `1+`  | (depends on system)        | (depends on system)        |
| `UnsignedSize`     | `1+`  | +0                         | (depends on system)        |
| `Float`            | `8`   | ≈ -1.7976931348623157e+308 | ≈ 1.7976931348623157e+308  |
| `Float16`          | `2`   | -65,504                    | +65,504                    |
| `Float32`          | `4`   | ≈ -1.17549435e-38          | ≈ 3.4028235e38             |
| `Float64`          | `8`   | ≈ -1.7976931348623157e+308 | ≈ 1.7976931348623157e+308  |
| `Double`           | `8`   | ≈ -1.7976931348623157e+308 | ≈ 1.7976931348623157e+308  |
| `Bytes`            | `1+`  | (storage for 1 byte)       | (depends on system)        |
| `Bytes8`           | `1`   | (storage for 1 byte)       | (storage for 1 byte)       |
| `Bytes16`          | `2`   | (storage for 2 bytes)      | (storage for 2 bytes)      |
| `Bytes32`          | `4`   | (storage for 4 bytes)      | (storage for 4 bytes)      |
| `Bytes64`          | `8`   | (storage for 8 bytes)      | (storage for 8 bytes)      |
| `Bytes128`         | `16`  | (storage for 16 bytes)     | (storage for 16 bytes)     |
| `Bytes256`         | `32`  | (storage for 32 bytes)     | (storage for 32 bytes)     |
| `String`           | `1+`  | (storage for 1 character)  | (depends on system)        |
| `Unicode`          | `1+`  | (storage for 1 character)  | (depends on system)        |
| `UTF8`             | `1+`  | (storage for 1 character)  | (depends on system)        |
| `UTF16`            | `1+`  | (storage for 1 character)  | (depends on system)        |
| `UTF32`            | `1+`  | (storage for 1 character)  | (depends on system)        |
| `ASCII`            | `1+`  | (storage for 1 character)  | (depends on system)        |

<a id='unit-tests'></a>
### Unit Tests

The DeliciousBytes library includes a suite of comprehensive unit tests which ensure that
the library functionality operates as expected. The unit tests were developed with and are
run via `pytest`.

To ensure that the unit tests are run within a predictable runtime environment where all of the necessary dependencies are available, a [Docker](https://www.docker.com) image is created within which the tests are run. To run the unit tests, ensure Docker and Docker Compose is [installed](https://docs.docker.com/engine/install/), and perform the following commands, which will build the Docker image via `docker compose build` and then run the tests via `docker compose run` – the output of running the tests will be displayed:

```shell
$ docker compose build
$ docker compose run tests
```

To run the unit tests with optional command line arguments being passed to `pytest`, append the relevant arguments to the `docker compose run tests` command, as follows, for example passing `-vv` to enable verbose output:

```shell
$ docker compose run tests -vv
```

See the documentation for [PyTest](https://docs.pytest.org/en/latest/) regarding available optional command line arguments.

### Copyright & License Information

Copyright © 2025 Daniel Sissman; licensed under the MIT License.