import pytest
from fcatalog.proto.serializer import s_string,d_string,\
        s_blob,d_blob,s_uint32,d_uint32,\
        DeserializeError



def test_serializer_helpers():
    """
    Generally check the validity of the serializer helpers:
    """
    my_str = 'Hello world!'
    my_blob = b'This is a blob'
    my_uint32 = 345235


    data = s_string(my_str) + s_blob(my_blob) + s_uint32(my_uint32)

    nextl,my_str_2 = d_string(data)
    data = data[nextl:]
    nextl,my_blob_2 = d_blob(data)
    data = data[nextl:]
    nextl,my_uint32_2 = d_uint32(data)
    data = data[nextl:]
    assert len(data) == 0


def test_serializer_helpers_errors():
    """
    Check some errors that might occur from serializer helpers.
    """

    short_datas = [b'',b'f',b'4g',b'132']
    # The following should raise an exception:
    for data in short_datas:
        with pytest.raises(DeserializeError):
            d_string(data)

        with pytest.raises(DeserializeError):
            d_blob(data)

        with pytest.raises(DeserializeError):
            d_uint32(data)

    # The length prefix here is too long. We expect an exception:
    bad_prefix = b'123444'
    with pytest.raises(DeserializeError):
        d_string(bad_prefix)
    with pytest.raises(DeserializeError):
        d_string(bad_prefix)

    # UTF-8 decoding error:
    # See https://docs.python.org/3/howto/unicode.html
    bad_utf8 = b'\x04\x00\x00\x00\x80abc'
    with pytest.raises(DeserializeError) as excinfo:
        d_string(bad_utf8)
    assert 'utf-8' in str(excinfo.value)
