from typing import Any

import pytest

from objectify import dict_to_object


def test_collection_types_are_converted_correctly():
    class Test:
        a: list[int]
        b: set[str]
        c: tuple[float, ...]
        d: dict[str, bool]

    obj = dict_to_object({
        'a': [1, 2, 3],
        'b': {'x', 'y', 'z'},
        'c': (1.0, 2.0, 3.0),
        'd': {'x': True, 'y': False}
    }, Test)

    assert obj.a == [1, 2, 3]
    assert obj.b == {'x', 'y', 'z'}
    assert obj.c == (1.0, 2.0, 3.0)
    assert obj.d == {'x': True, 'y': False}


def test_empty_tuple_type_accepts_empty_tuple():
    class Test:
        a: tuple[()]

    obj = dict_to_object({'a': ()}, Test)

    assert obj.a == ()


def test_empty_tuple_type_raises_for_non_empty_tuple():
    class Test:
        a: tuple[()]

    with pytest.raises(Exception):
        dict_to_object({'a': (1, 2, 3)}, Test)


@pytest.mark.parametrize('value,clazz', [
    ((), int),
    ((1,), int),
    ((1, 2, 3), int),
    ((), str),
    (('a',), str),
    (('a', 'b', 'c'), str),
    ((), float),
    ((1.0,), float),
    ((1.0, 2.0, 3.0), float),
    ((), bool),
    ((True,), bool),
    ((True, False, True), bool),
    ((), None),
    ((None,), None),
    ((None, None, None), None),
])
def test_variable_length_tuple_type_accepts_valid_values(value: tuple[Any, ...], clazz: type[Any]):
    class Test:
        a: tuple[clazz, ...]

    obj = dict_to_object({'a': value}, Test)

    assert obj.a == value


@pytest.mark.parametrize('value,clazz', [
    ((1, 2, 'a'), int),
    ((1, 2, 3), str),
    ((1.0, 2.0, 'a'), float),
    ((1.0, 2.0, 3.0), bool),
    ((True, False, 'a'), bool),
    ((True, False, True), None),
    ((None, None, 'a'), None),
    ((None, None, None), int),
    ((1, 2, 3), str),
    ((1.0, 2.0, 3.0), bool),
    ((True, False, True), None),
    ((None, None, None), int),
])
def test_variable_length_tuple_type_rejects_invalid_values(value: tuple[Any, ...], clazz: type[Any]):
    class Test:
        a: tuple[clazz, ...]

    with pytest.raises(Exception):
        dict_to_object({'a': value}, Test)


@pytest.mark.parametrize('value,clazz', [
    ((1,), tuple[int]),
    ((1, 2, 3), tuple[int, int, int]),
    (('a',), tuple[str]),
    (('a', 'b', 'c'), tuple[str, str, str]),
    ((1.0,), tuple[float]),
    ((1.0, 2.0, 3.0), tuple[float, float, float]),
    ((True,), tuple[bool]),
    ((True, False, True), tuple[bool, bool, bool]),
    ((None,), tuple[None]),
    ((None, None, None), tuple[None, None, None]),
    ((1, 'abc', 3.0, False, None), tuple[int, str, float, bool, None]),
])
def test_fixed_length_tuple_type_accepts_valid_values(value: tuple[Any, ...], clazz: type[Any]):
    class Test:
        a: clazz

    obj = dict_to_object({'a': value}, Test)

    assert obj.a == value


@pytest.mark.parametrize('value,clazz', [
    ((1, 2, 'a'), tuple[int, int, int]),
    ((1, 2, 3), tuple[str, str, str]),
    (('a', 'b', 'c'), tuple[str, str]),
    (('a', 'b', 'c'), tuple[str, str, str, str]),
    ((1.0, 2.0, 'a'), tuple[float, float, float]),
    ((1.0, 2.0, 3.0), tuple[bool, bool, bool]),
    ((1.0, 2.0, 3.0), tuple[float, float, float, float]),
    ((True, False, 'a'), tuple[bool, bool, bool]),
    ((True, False, True), tuple[None, None, None]),
    ((None, None, 'a'), tuple[int, int, int]),
    ((None, None, None), tuple[str, str, str]),
    ((1, 2, 3), tuple[float, float, float]),
    ((1.0, 2.0, 3.0), tuple[bool, bool, bool]),
    ((True, False, True), tuple[None, None, None]),
    ((None, None, None), tuple[int, int, int]),
    ((1, 'abc', 3.0, False, None), tuple[int, str, float, str, None]),
])
def test_fixed_length_tuple_type_rejects_invalid_values(value: tuple[Any, ...], clazz: type[Any]):
    class Test:
        a: clazz

    with pytest.raises(Exception):
        dict_to_object({'a': value}, Test)


def test_nested_list_is_converted_correctly():
    class Test:
        a: list[list[int]]

    obj = dict_to_object({'a': [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}, Test)

    assert obj.a == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]


def test_nested_set_is_converted_correctly():
    class Test:
        a: list[set[str]]

    obj = dict_to_object({'a': [{'a', 'b', 'c'}, {'d', 'e', 'f'}, {'g', 'h', 'i'}]}, Test)

    assert obj.a == [{'a', 'b', 'c'}, {'d', 'e', 'f'}, {'g', 'h', 'i'}]


def test_nested_tuple_is_converted_correctly():
    class Test:
        a: tuple[tuple[int, float], tuple[float, str]]

    obj = dict_to_object({'a': [(1, 2.0), (3.0, '4.0')]}, Test)

    assert obj.a == ((1, 2.0), (3.0, '4.0'))
