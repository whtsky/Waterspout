def test_object_dict():
    from waterspout.utils import ObjectDict
    obj = ObjectDict()
    import random
    v = random.randint(1, 100)
    obj.a = v
    assert obj.a == v
    del obj.a
    try:
        obj.a
    except AttributeError:
        pass
    else:
        raise


def test_get_root_path():
    import os
    path = os.path.abspath(__file__)
    root = os.path.abspath(os.path.dirname(path))
    from waterspout.utils import get_root_path
    assert root == get_root_path(__name__)


def test_cached_property():
    from waterspout.utils import cached_property

    class Num(object):
        @property
        def m(self):
            import random
            return random.randint(1, 100)

        @cached_property
        def n(self):
            import random
            return random.randint(1, 100)

    num = Num()
    assert num.m != num.m
    assert num.n == num.n