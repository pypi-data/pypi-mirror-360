from dataclasses import dataclass

from objectify import dict_to_object
from . import skip_versions


def test_nested_dataclass_is_converted_correctly():
    @dataclass
    class Test:
        a: int

    @dataclass
    class Nested:
        b: Test

    obj = dict_to_object({'b': {'a': 1}}, Nested)

    assert obj.b.a == 1


def test_nested_dataclass_with_list_is_converted_correctly():
    @dataclass
    class Test:
        a: int

    @dataclass
    class Nested:
        b: list[Test]

    obj = dict_to_object({'b': [{'a': 1}, {'a': 2}, {'a': 3}]}, Nested)

    assert obj.b[0].a == 1
    assert obj.b[1].a == 2
    assert obj.b[2].a == 3


def test_nested_local_dataclass_is_converted_correctly():
    @dataclass
    class Nested:
        a: int
        b: 'Test'

        @dataclass
        class Test:
            c: str

    obj = dict_to_object({'a': 1, 'b': {'c': 'xyz'}}, Nested)

    assert obj.a == 1
    assert obj.b.c == 'xyz'


@skip_versions(lower_than=(3, 11))
def test_nested_local_dataclass_with_list_is_converted_correctly():
    """Before Python 3.11, 'Test' in list['Test'] does not resolve correctly into a class."""

    @dataclass
    class Nested:
        a: int
        b: list['Test']

        @dataclass
        class Test:
            c: str

    obj = dict_to_object({'a': 1, 'b': [{'c': 'xyz'}, {'c': 'abc'}, {'c': '123'}]}, Nested)

    assert obj.a == 1
    assert obj.b[0].c == 'xyz'
    assert obj.b[1].c == 'abc'
    assert obj.b[2].c == '123'
