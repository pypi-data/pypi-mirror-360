from dataclasses import dataclass

import pytest

from objectify import dict_to_object


class Test:
    a: int
    b: str
    c: float
    d: bool
    e: None


def test_primitive_types_are_handled_correctly():
    obj = dict_to_object({'a': 1, 'b': 'xyz', 'c': 3.0, 'd': True, 'e': None}, Test)

    assert obj.a == 1
    assert obj.b == 'xyz'
    assert obj.c == 3.0
    assert obj.d is True
    assert obj.e is None


def test_conversion_to_dataclass_type():
    obj = dict_to_object({'a': 1, 'b': 'xyz', 'c': 3.0, 'd': True, 'e': None}, dataclass(Test))

    assert obj.a == 1
    assert obj.b == 'xyz'
    assert obj.c == 3.0
    assert obj.d is True
    assert obj.e is None


def test_conversion_to_dataclass_type_without_init():
    obj = dict_to_object({'a': 1, 'b': 'xyz', 'c': 3.0, 'd': True, 'e': None}, dataclass(init=False)(Test))

    assert obj.a == 1
    assert obj.b == 'xyz'
    assert obj.c == 3.0
    assert obj.d is True
    assert obj.e is None


def test_missing_fields_with_default_values():
    class TestWithDefaults:
        a: int
        b: str
        c: float = 3.0
        d: bool = True
        e: None = None

    obj = dict_to_object({'a': 1, 'b': 'xyz', 'd': False}, TestWithDefaults)

    assert obj.a == 1
    assert obj.b == 'xyz'
    assert obj.c == 3.0
    assert obj.d is False
    assert obj.e is None


def test_missing_required_fields_raises_exception():
    """Fails because 'a' and 'b' are missing."""
    with pytest.raises(Exception):
        dict_to_object({'c': 3.0, 'd': True, 'e': None}, Test)


def test_extra_fields_are_ignored():
    """Ignores extra field and doesn't raise an error."""
    obj = dict_to_object({'a': 1, 'b': 'xyz', 'c': 3.0, 'd': True, 'e': None, 'extra': 'unexpected'}, Test)
    assert obj.a == 1
    assert isinstance(obj, Test)
    assert not hasattr(obj, 'extra')


def test_wrong_types_raises_exception():
    """Fails because types do not match."""
    with pytest.raises(Exception):
        dict_to_object({'a': "not an int", 'b': 123, 'c': "not a float", 'd': "not a bool", 'e': "not None"}, Test)
