import sys
import types
import typing
from typing import Any, get_type_hints, get_origin, get_args, Collection, Literal, TypeVar

__all__ = ['dict_to_object']

T = TypeVar('T')

_sentinel = object()


def dict_to_object(source_dict: dict[str, Any], target_type: type[T]) -> T:
    """
    Convert a dictionary to an object of the specified type.

    This function will create an instance of the specified type and populate its attributes with the values from the
    dictionary. The dictionary keys must match the attribute names of the target type.

    The following types are supported:

    - Primitive types (str, int, float, bool, NoneType)
    - Custom classes (fields have to be defined like in dataclasses)
    - Dataclasses
    - Collection types (list, set, tuple, dict)
    - Nested collections and custom classes
    - Literal types
    - Type aliases, including TypeAliasType (Python 3.12+)
    - Union types
    - Optional types

    :param source_dict: The dictionary to convert to an object.
    :param target_type: The type of the object to create.
    :return:
    """
    target_instance = object.__new__(target_type)

    for attr, expected_type in get_type_hints(target_type).items():
        raw_field_value = source_dict.get(attr, getattr(target_instance, attr, _sentinel))
        if raw_field_value is _sentinel:
            raise ValueError(f"Attribute {attr!r} is missing in the source dictionary "
                             "and the class definition doesn't have a default value for it.")
        converted_value = transform_element(raw_field_value, expected_type)
        setattr(target_instance, attr, converted_value)

    return target_instance


def handle_collection(source: Collection[Any], collection_type: type):
    origin = get_origin(collection_type)
    type_args = get_args(collection_type)

    if issubclass(origin, list):
        return [transform_element(item, type_args[0]) for item in source]

    elif issubclass(origin, tuple):
        if len(type_args) == 2 and type_args[1] is Ellipsis:
            return tuple(transform_element(item, type_args[0]) for item in source)
        else:
            return tuple(
                transform_element(source_value, element_type)
                for element_type, source_value in zip(type_args, source, strict=True)
            )

    elif issubclass(origin, set):
        return {transform_element(item, type_args[0]) for item in source}

    elif issubclass(origin, dict):
        key_type, value_type = type_args
        assert isinstance(source, dict)
        return {
            transform_element(k, key_type): transform_element(v, value_type)
            for k, v in source.items()
        }

    raise TypeError(f"Unsupported collection type: {collection_type}.")


def handle_literal(value: Any, literal_type: type):
    if value not in get_args(literal_type):
        raise ValueError(f"Value {value} is not a valid literal for type {literal_type}.")
    return value


def handle_union(value: Any, union_type: type):
    for candidate_type in get_args(union_type):
        try:
            return transform_element(value, candidate_type)
        except (AssertionError, TypeError, ValueError):
            continue
    raise TypeError(f"`{value}` does not match any of: {get_args(union_type)}.")


def transform_element(raw_value: Any, target_type: type[T]) -> T:
    if sys.version_info >= (3, 12) and isinstance(target_type, typing.TypeAliasType):  # novermin
        target_type = target_type.__value__

    if target_type is None:
        target_type = types.NoneType

    target_type_origin = get_origin(target_type) or target_type

    if target_type_origin is Literal:
        return handle_literal(raw_value, target_type)
    elif target_type_origin in (typing.Union, types.UnionType):
        return handle_union(raw_value, target_type)
    elif is_collection_type(target_type_origin):
        return handle_collection(raw_value, target_type)
    elif is_primitive_type(target_type_origin):
        assert isinstance(raw_value, target_type)
        return raw_value
    else:
        assert isinstance(raw_value, dict)
        return dict_to_object(raw_value, target_type)


def is_collection_type(origin: type):
    return issubclass(origin, list | set | tuple | dict)


def is_primitive_type(type_: type):
    return issubclass(type_, str | int | float | bool | types.NoneType)
