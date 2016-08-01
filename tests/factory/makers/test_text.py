from mongoframes.factory import quotas
from mongoframes.factory.makers import text as text_makers


def test_code():
    """
    `Code` makers should return a random code.
    """

    # Configured with the default character set
    maker = text_makers.Code(quotas.Quota(4))

    # Check the assembled result
    assembled = maker._assemble()
    assert len(assembled) == 4
    assert set(assembled).issubset(set(maker.default_charset))

    # Check the finished result
    finished = maker._finish(assembled)
    assert len(finished) == 4
    assert set(assembled).issubset(set(maker.default_charset))

    # Configured with a custom charset
    custom_charset = 'ABCDEF1234567890'
    maker = text_makers.Code(quotas.Quota(6), custom_charset)

    # Check the assembled result
    assembled = maker._assemble()
    assert len(assembled) == 6
    assert set(assembled).issubset(set(custom_charset))

    # Check the finished result
    finished = maker._finish(assembled)
    assert len(finished) == 6
    assert set(assembled).issubset(set(custom_charset))
