import pytest

from deliciousbytes import (
    ByteOrder,
    BytesView,
    Short,
    Long,
    Type,
)


@pytest.fixture(scope="module", name="data")
def test_data_fixture() -> bytes:
    """Assemble some test raw bytes data to work with throughout the unit tests."""

    return b"\x00\x01\x00\x02\x00\x03\x00\x04"


@pytest.fixture(scope="module", name="view")
def test_bytes_view_fixture(data: bytes) -> BytesView:
    """Create a BytesView class instance to work with throughout the unit tests."""

    # Ensure that the data is bytes or bytearray
    assert isinstance(data, (bytes, bytearray))

    # Ensure that the data has the expected length
    assert len(data) == 8

    # Here we create a BytesView class instance with the assigned data and an initial
    # split length of 2, so when iterating the data will be split into groups of 2 bytes
    return BytesView(data, split=2)


def test_bytesview_initialization(data: bytes, view: BytesView):
    """Test the BytesView class initialization was successful."""

    assert isinstance(view, BytesView)

    assert view.data == data
    assert view.splits == 2


def test_bytesview_length(view: BytesView):
    """Test that the BytesView reports its current length correctly."""

    # The length reflects the current length of the data as divided by the split size
    # This is the number of items that can iterated over in the view where the maximum
    # usable index for iteration or item level access is the reported length minus 1.
    assert len(view) == 4


def test_bytesview_iteration_via_for_in_loop(view: BytesView):
    """Test that the BytesView can be iterated over correctly using a for...in loop."""

    # Iterate over the values using normal iterator semantics such as for/enumerate
    for index, val in enumerate(view):
        if index == 0:
            assert val == b"\x00\x01"
        elif index == 1:
            assert val == b"\x00\x02"
        elif index == 2:
            assert val == b"\x00\x03"
        elif index == 3:
            assert val == b"\x00\x04"


def test_bytesview_item_access(view: BytesView):
    """Test that the BytesView byte groups can be accessed via item access semantics."""

    # Access individual groups of bytes (based on the split size) using item access
    assert view[0] == b"\x00\x01"
    assert view[1] == b"\x00\x02"
    assert view[2] == b"\x00\x03"
    assert view[3] == b"\x00\x04"


def test_bytesview_item_access_slicing(view: BytesView):
    """Test that the BytesView byte groups can be accessed via slicing semantics."""

    # Note: When slicing access is used, the current split length is ignored

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


def test_bytesview_changing_split_size_after_initialization(view: BytesView):
    """Test that the BytesView split size can be changed after initialization."""

    # Change the split size at any point; the last split size will be remembered (!)
    for index, val in enumerate(view.split(4)):
        if index == 0:
            assert val == b"\x00\x01\x00\x02"
        elif index == 1:
            assert val == b"\x00\x03\x00\x04"

    # Note how the group size changed based on the split size set most recently
    assert view[0] == b"\x00\x01\x00\x02"
    assert view[1] == b"\x00\x03\x00\x04"


def test_bytesview_casting(view: BytesView):
    """Test that the BytesView can cast groups to the defined data type."""

    # Cast the values from raw bytes to the defined type; note that casting implies an
    # associated split size as each type cast requires the relevant number of bytes for
    # decoding to the defined type; byte order can be specified using struct shorthand
    for index, val in enumerate(view.cast(">h")):
        if index == 0:
            assert val == 1
        elif index == 1:
            assert val == 2
        elif index == 2:
            assert val == 3
        elif index == 3:
            assert val == 4


def test_bytesview_tell(view: BytesView):
    """Test that the BytesView tell method reports the expected index position."""

    # The current index position can be determined by using the 'tell' method; as the
    # above iterator just completed iterating through 8 bytes of data, index should be 8
    assert view.tell() == 8


def test_bytesview_seek_individual_bytes(view: BytesView):
    """Test that the BytesView seek method changes the index position as expected."""

    # Adjust the split size to 1 to test setting the seek position to individual bytes
    view.split(1)

    # The current index position can be adjusted using the 'seek' method; if an split
    # length is set, then the index will be set to the defined multiple of split; the
    # 'seek' method also returns a reference to 'self' so calls can be chained; notice
    # that the index positions reported by 'tell' are multiples of the split size:
    assert view.seek(0).tell() == 0
    assert view.seek(1).tell() == 1
    assert view.seek(2).tell() == 2
    assert view.seek(3).tell() == 3
    assert view.seek(4).tell() == 4
    assert view.seek(5).tell() == 5
    assert view.seek(6).tell() == 6
    assert view.seek(7).tell() == 7


def test_bytesview_seek_groups_of_bytes(view: BytesView):
    """Test that the BytesView seek method changes the index position as expected."""

    # Adjust the split size to 2 to test setting the seek position to groups of bytes
    view.split(2)

    # The current index position can be adjusted using the 'seek' method; if an split
    # length is set, then the index will be set to the defined multiple of split; the
    # 'seek' method also returns an reference to 'self' to calls can be chained; notice
    # that the index positions reported by 'tell' are multiples of the split size:
    assert view.seek(0).tell() == 0
    assert view.seek(1).tell() == 2
    assert view.seek(2).tell() == 4
    assert view.seek(3).tell() == 6


def test_bytesview_next_iteration(view: BytesView):
    """Test that the BytesView next method returns the expected view item."""

    # Create a new iterator which resets the iteration position to zero (0)
    view = iter(view)

    # Ensure that the iterator index was reset to 0
    assert view.tell() == 0

    # The 'next' method may also be used to obtain the next item from the view, either
    # as raw bytes, or decoded into the specified type; call .next() for each item in
    # the view, specifying how each item should be decoded.

    # Test obtaining the next (in this case the first) item as raw bytes
    assert view.next() == b"\x00\x01"

    # Test obtaining the next (in this case the second) item as a short integer (>h)
    assert view.next(">h") == 2

    # Test obtaining the next (in this case the third) item as a short integer (>h)
    assert view.next(">h") == 3

    # Test obtaining the next (in this case the fourth) item as a short integer (>h)
    assert view.next(">h") == 4

    # If .next() is called more times than there are items in the view, it returns None;
    # if the iterator or its index is reset, .next() will be able to yield values again:
    assert view.next(">h") is None


def test_bytesview_decode(view: BytesView):
    """Test that the BytesView decode method returns the expected decoded items."""

    decoded: tuple[Type] = view.decode(">hhhh")

    assert isinstance(decoded, tuple)

    assert len(decoded) == 4

    assert decoded == (1, 2, 3, 4)

    assert isinstance(decoded[0], Short)
    assert isinstance(decoded[0], int)
    assert decoded[0] == 1

    assert isinstance(decoded[1], Short)
    assert isinstance(decoded[1], int)
    assert decoded[1] == 2

    assert isinstance(decoded[2], Short)
    assert isinstance(decoded[2], int)
    assert decoded[2] == 3

    assert isinstance(decoded[3], Short)
    assert isinstance(decoded[3], int)
    assert decoded[3] == 4


def test_bytesview_decode_numeric_format_string(view: BytesView):
    """Test that the BytesView decode method returns the expected decoded items."""

    decoded: tuple[Type] = view.decode(">2h h 1h")

    assert isinstance(decoded, tuple)

    assert len(decoded) == 4

    assert decoded == (1, 2, 3, 4)


def test_bytesview_encode(view: BytesView):
    """Test that the BytesView decode method returns the expected decoded items."""

    # Assemble some values for testing, each a subclass of Type
    values: list[Type] = [
        Short(7),  # 2-byte, 16-bits
        Short(8),  # 2-byte, 16-bits
        Long(9),  # 4-byte, 32-bits
    ]

    # Encode the values into a BytesView class instance
    encoded: BytesView = BytesView.encode(values, order=ByteOrder.LSB)

    # Ensure that the BytesView class instance was created correctly
    assert isinstance(encoded, BytesView)

    # Ensure that the encoded length of the data is as expected
    assert len(encoded) == 8

    # Ensure that the raw data looks as we would expect it to
    assert encoded[0:2] == b"\x07\x00"  # 7 (as short, 2-bytes, LSB)
    assert encoded[2:4] == b"\x08\x00"  # 8 (as short, 2-bytes, LSB)
    assert encoded[4:8] == b"\x09\x00\x00\x00"  # 9 (as long, 4-bytes, LSB)

    # Now ensure that the values can be decoded correctly as well
    decoded: tuple[Type] = encoded.decode("h h l", order=ByteOrder.LSB)

    # Ensure that the decoded values were returned as a tuple
    assert isinstance(decoded, tuple)

    # Ensure that the tuple contains the expected number of entries
    assert len(decoded) == 3

    # Ensure that each value held in the tuple is a deliciousbytes.Type subclass
    for value in decoded:
        assert isinstance(value, Type)

    # Ensure that the decoded values are as expected
    assert decoded == (7, 8, 9)

    # Ensure that the first value has the expected data type and value
    assert isinstance(decoded[0], Short)
    assert isinstance(decoded[0], int)
    assert decoded[0] == 7

    # Ensure that the second value has the expected data type and value
    assert isinstance(decoded[1], Short)
    assert isinstance(decoded[1], int)
    assert decoded[1] == 8

    # Ensure that the third value has the expected data type and value
    assert isinstance(decoded[2], Long)
    assert isinstance(decoded[2], int)
    assert decoded[2] == 9
