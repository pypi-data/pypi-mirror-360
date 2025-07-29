from typing import Optional

from objectify import dict_to_object


class InnerA:
    labels: list[str]
    height: int


class InnerB:
    labels: list[int]
    height: int


class ClassA:
    name: str
    value: int
    nested: InnerA


class ClassB:
    name: str
    value: int
    nested: InnerB


class MainA:
    id: int
    child: ClassA | None


class MainB:
    id: int
    child: Optional[ClassB]


def test_main_a_child_should_be_class_a():
    dictionary = {
        'id': 890,
        'child': {
            'name': 'addags',
            'value': 312,
            'nested': {
                'labels': ['a', 'b', 'c'],
                'height': 10
            }
        }
    }

    obj = dict_to_object(dictionary, MainA)
    assert isinstance(obj, MainA)
    assert isinstance(obj.child, ClassA)


def test_main_a_child_should_be_none():
    dictionary = {
        'id': 890,
        'child': None
    }

    obj = dict_to_object(dictionary, MainA)
    assert isinstance(obj, MainA)
    assert obj.child is None


def test_main_b_child_should_be_class_b():
    dictionary = {
        'id': 890,
        'child': {
            'name': 'addags',
            'value': 312,
            'nested': {
                'labels': [1, 2, 3],
                'height': 10
            }
        }
    }

    obj = dict_to_object(dictionary, MainB)
    assert isinstance(obj, MainB)
    assert isinstance(obj.child, ClassB)


def test_main_b_child_should_be_none():
    dictionary = {
        'id': 890,
        'child': None
    }

    obj = dict_to_object(dictionary, MainB)
    assert isinstance(obj, MainB)
    assert obj.child is None
