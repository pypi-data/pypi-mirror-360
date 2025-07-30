from toolforge_weld.utils import peek


def test_peek_data():
    first, iterator = peek(iter(["first", "second", "third"]))
    assert first == "first"
    assert list(iterator) == ["first", "second", "third"]


def test_peek_empty():
    first, iterator = peek(iter([]))
    assert first is None
    assert list(iterator) == []
