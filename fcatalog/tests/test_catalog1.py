
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


###########################################
###########################################


def calc_sim(sgn1,sgn2):
    """
    Calculate the similarity between two signatures of the same size.
    """
    total = 0
    assert len(sgn1) == len(sgn2)

    for i in range(len(sgn1)):
        if sgn1[i] == sgn2[i]:
            total += 1

    return total


def test_sign_similars():
    """
    Sign similar strings and expect similar signatures.
    Sign very different strings and expect zero similarity.
    """
    s1 = sign(b'hello world he2llo world',16)
    s2 = sign(b'hello world he1llo world',16)
    assert calc_sim(s1,s2) > 6

    s1 = sign(b'akjdflkasjflkasjlfkasjdflkjaslkdfjaslkjfsaklfdjaslkjdfsf',16)
    s2 = sign(b'4039582903850923850928345982309589023845823458230945',16)
    assert calc_sim(s1,s2) == 0



