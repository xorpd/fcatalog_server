
from catalog1 import sign

def isdword(x):
    """
    Check if x is a dword.
    An integer between 0 and 2**32 - 1, inclusive.
    """
    if not isinstance(x,int):
        return False

    if x < 0:
        return False

    if x > 2**32:
        return False

    return True


def test_sign_basic():
    """
    Sign some strings.
    """
    res = sign(b'afdasdklfjaskljdfaklsjdf',num_perms=16)
    assert len(res) == 16
    for x in res:
        assert isdword(x)

    res = \
        sign(b'3kl4jfklsdjfklasjf8934j9sjdf9adfkalsdjflkasjdflkasdf',num_perms=20)
    assert len(res) == 20
    for x in res:
        assert isdword(x)

    res = sign(b'4095809348529384523904582390485092384509283',num_perms=32)
    assert len(res) == 32
    for x in res:
        assert isdword(x)


def test_sign_long_data():
    """
    Sign long data
    """
    res = sign((b'asdfklasjdf') * 40,num_perms=20)
    assert len(res) == 20
    for x in res:
        assert isdword(x)


def test_sign_deterministic():
    """
    Make sure that signing the same data results in the same result
    """
    res1 = sign(b'3kl4jfklsdjfklasjf8934j9sjdf9adfkalsdjflkasjdflkasdf',num_perms=20)
    res2 = sign(b'3kl4jfklsdjfklasjf8934j9sjdf9adfkalsdjflkasjdflkasdf',num_perms=20)
    assert res1 == res2

