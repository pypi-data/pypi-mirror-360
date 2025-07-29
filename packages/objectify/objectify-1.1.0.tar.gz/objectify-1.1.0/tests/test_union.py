from objectify import dict_to_object


class InnerA:
    labels: list[str]
    height: int


class InnerB:
    labels: list[int]
    height: int


class InnerC:
    names: list[str]
    height: int


class ClassA:
    name: str
    value: int
    nested: InnerA


class ClassB:
    name: str
    value: int
    nested: InnerB


class ClassC:
    name: str
    value: int
    nested: InnerC


class ClassD:
    name: str
    value: int
    nested: float


class ClassE:
    name: str
    value: int
    nested: ClassA | ClassB | ClassC


class Main:
    id: int
    child: ClassA | ClassB | ClassC | ClassD | ClassE


def test_child_should_be_class_a():
    dictionary = {
        'id': 890,
        'child': {
            'name': 'addags',
            'value': 312,
            'nested': {
                'labels': ['asd', 'gds', 'hbc'],
                'height': 773
            }
        }
    }
    obj = dict_to_object(dictionary, Main)
    assert isinstance(obj.child, ClassA)


def test_child_should_be_class_a_due_to_order_in_union():
    dictionary = {
        'id': 38,
        'child': {
            'name': 'addags',
            'value': 889,
            'nested': {
                'labels': [],  # Matches both TreeA and TreeB, but TreeA is first in the union type
                'height': 42
            }
        }
    }
    obj = dict_to_object(dictionary, Main)
    assert isinstance(obj.child, ClassA)


def test_child_should_be_class_b():
    dictionary = {
        'id': 12,
        'child': {
            'name': 'addags',
            'value': 457,
            'nested': {
                'labels': [1, 5, 7],
                'height': 9976
            }
        }
    }
    obj = dict_to_object(dictionary, Main)
    assert isinstance(obj.child, ClassB)


def test_child_should_be_class_c():
    dictionary = {
        'id': 421,
        'child': {
            'name': 'addags',
            'value': 8967,
            'nested': {
                'names': ['asd', 'gds', 'hbc'],
                'height': 366
            }
        }
    }
    obj = dict_to_object(dictionary, Main)
    assert isinstance(obj.child, ClassC)


def test_child_should_be_class_d():
    dictionary = {
        'id': 345,
        'child': {
            'name': 'addags',
            'value': 859,
            'nested': 4.6
        }
    }
    obj = dict_to_object(dictionary, Main)
    assert isinstance(obj.child, ClassD)


def test_child_should_be_class_e_with_class_a():
    dictionary = {
        'id': 61,
        'child': {
            'name': 'ghjghkg',
            'value': 14,
            'nested': {
                'name': 'rtegfdh',
                'value': 79,
                'nested': {
                    'labels': ['asd', 'gds', 'hbc'],
                    'height': 990
                }
            }
        }
    }
    obj = dict_to_object(dictionary, Main)
    assert isinstance(obj.child, ClassE)
    assert isinstance(obj.child.nested, ClassA)


def test_child_should_be_class_e_with_class_b():
    dictionary = {
        'id': 56,
        'child': {
            'name': 'child_name',
            'value': 97,
            'nested': {
                'name': 'nested_name',
                'value': 87,
                'nested': {
                    'labels': [9, 5, 0],
                    'height': 578
                }
            }
        }
    }
    obj = dict_to_object(dictionary, Main)
    assert isinstance(obj.child, ClassE)
    assert isinstance(obj.child.nested, ClassB)


def test_child_should_be_class_e_with_class_c():
    dictionary = {
        'id': 96,
        'child': {
            'name': 'child_name',
            'value': 775,
            'nested': {
                'name': 'nested_name',
                'value': 457,
                'nested': {
                    'names': ['name1', 'name2', 'name3'],
                    'height': 33
                }
            }
        }
    }
    obj = dict_to_object(dictionary, Main)
    assert isinstance(obj.child, ClassE)
    assert isinstance(obj.child.nested, ClassC)
