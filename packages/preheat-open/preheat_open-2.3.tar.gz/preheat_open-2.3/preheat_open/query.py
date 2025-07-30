"""
query.py

This module defines classes and functions for querying objects based on specified criteria.

Classes:
    Query

Functions:
    query_stuff
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from inspect import signature
from typing import ClassVar, Generator, Iterable, Type, TypeVar

T = TypeVar("T")


def build_instance_from_dict(
    cls: Type[T], data: dict, remove_keys: bool = True
) -> tuple[T, dict]:
    """
    Builds an instance of a dataclass from a dictionary and returns the instance and the remaining keys.

    :param cls: The class to build an instance of.
    :type cls: Type[T]
    :param data: The dictionary to build the instance from.
    :type data: dict
    :param remove_keys: Whether to remove the keys used to build the instance from the dictionary.
    :type remove_keys: bool, optional
    :return: A tuple containing the instance and the remaining keys.
    :rtype: tuple[T, dict]
    """

    cls_fields = list(signature(cls.__init__).parameters)

    obj = cls(**{k: v for k, v in data.items() if k in cls_fields})

    if remove_keys:
        for k in cls_fields:
            data.pop(k, None)

    return obj, data


@dataclass
class Query:
    """
    Represents a query for filtering objects based on specified attributes.

    :cvar _class: The class type that the query is filtering.
    :vartype _class: ClassVar

    Methods:
        __post_init__: Initializes the query attributes.
        __eq__: Checks if an object matches the query.
        convert_attr: Converts an attribute to the appropriate type.
        empty: Checks if the query has no attributes set.
        from_kwargs: Creates a Query object from keyword arguments.
    """

    _class: ClassVar
    exclude: Query = None

    def __post_init__(self):
        """
        Initializes the query attributes by converting them to lists and applying type conversion.
        """
        for attribute, value in self.__dict__.items():
            if attribute == "exclude":
                if value is not None and isinstance(value, dict):
                    setattr(self, attribute, self.from_kwargs(**value))
            else:
                value = value if isinstance(value, list) else [value]
                setattr(
                    self, attribute, [self.convert_attr(v, attribute) for v in value]
                )

    @classmethod
    def is_type(cls, obj: object) -> bool:
        """
        Checks if the object is of the type specified by the query class.

        :param obj: The object to check.
        :type obj: object
        :return: True if the object is of the specified type, False otherwise.
        :rtype: bool
        """
        return cls.__name__[:-5] == obj.__class__.__name__

    def __eq__(self, other: object) -> bool:
        """
        Checks if an object matches the query.

        :param value: The object to check against the query.
        :type value: object
        :return: True if the object matches the query, False otherwise.
        :rtype: bool
        """

        def match(attr, query_list):
            if attr is None and not query_list:
                return True
            else:
                return attr in query_list

        if isinstance(other, self._class):
            matches = [
                match(getattr(other, attr_name), query_list)
                for attr_name, query_list in self.__dict__.items()
                if query_list and attr_name != "exclude"
            ]
            if self.exclude is not None and self.exclude == other:
                return False
            return all(matches)
        return False

    def isin(self, iterable: Iterable) -> bool:
        """
        Checks if the query matches any element in the iterable.

        :param iterable: The iterable to check against the query.
        :type iterable: Iterable
        :return: True if the query matches any element in the iterable, False otherwise.
        :rtype: bool
        """
        return any(self == item for item in iterable)

    @classmethod
    def convert_attr(cls, value, name):
        """
        Converts an attribute to the appropriate type based on the class definition.

        :param value: The value to convert.
        :type value: Any
        :param name: The name of the attribute.
        :type name: str
        :return: The converted value.
        :rtype: Any
        """
        if not isinstance(value, list):
            try:
                class_type = getattr(cls, f"_type_{name}")
                class_type = cls if class_type == "self" else class_type
                if not isinstance(value, class_type):
                    value = (
                        class_type(**value)
                        if isinstance(value, dict)
                        else class_type(value)
                    )
            except AttributeError:
                pass
        return value

    @classmethod
    def from_kwargs(
        cls,
        query: Query | None = None,
        **kwargs,
    ) -> Query:
        """
        Creates a Query object from keyword arguments.

        :param query: An existing Query object to use as a base.
        :type query: Query, optional
        :param kwargs: Additional keyword arguments to set as query attributes.
        :return: A new Query object.
        :rtype: Query
        :raises TypeError: If unknown keys are provided in kwargs.
        """
        if query is None:
            allowed_keys = [f.name for f in fields(cls)]
            if wrong_keys := [
                key for key, _ in kwargs.items() if key not in allowed_keys
            ]:
                raise TypeError(
                    f"Unknown keys received when instantiating {cls}. Expected keys are {allowed_keys} but received {wrong_keys}."
                )
            build_pars = {
                key: cls.convert_attr(val, key)
                for key, val in kwargs.items()
                if key in allowed_keys
            }

            return cls(**build_pars)
        return query


def query_stuff(
    obj: object,
    query: Query | list[Query | dict] | None,
    sub_obj_attrs: list[str],
    sub_obj_attrs_for_removal: list[str] | None = None,
    query_type: type = Query,
    include_obj: bool = False,
    **kwargs,
) -> Generator[object, None, None]:
    """
    Queries objects and their sub-objects based on specified criteria.

    :param obj: The object to query.
    :type obj: object
    :param query: The query or list of queries to apply.
    :type query: Query | list[Query | dict]
    :param sub_obj_attrs: The attributes of the object that contain sub-objects to query.
    :type sub_obj_attrs: list[str]
    :param sub_obj_attrs_for_removal: The attributes to remove from sub-objects during querying.
    :type sub_obj_attrs_for_removal: list[str], optional
    :param query_type: The type of query to use.
    :type query_type: type, optional
    :param include_obj: Whether to include the object itself in the results if it matches the query.
    :type include_obj: bool, optional
    :param kwargs: Additional keyword arguments for the query.
    :return: A generator yielding objects that match the query.
    :rtype: Generator[object, None, None]
    """
    sub_obj_attrs_for_removal = (
        sub_obj_attrs_for_removal if sub_obj_attrs_for_removal is not None else []
    )

    if isinstance(query, list):
        queries = [
            q if isinstance(q, Query) else query_type.from_kwargs(**q) for q in query
        ]
    else:
        queries = [
            query
            if isinstance(query, Query)
            else query_type.from_kwargs(query=query, **kwargs)
        ]
    # Yield the object if it is a match to the query
    if query_type.is_type(obj) and include_obj and obj in queries:
        yield obj
    # Iterate through the sub-objects and query them
    for sub_obj_attr in sub_obj_attrs:
        try:
            sub_objs = getattr(obj, sub_obj_attr)
        except AttributeError:
            continue
        else:
            sub_objs = sub_objs if isinstance(sub_objs, Iterable) else [sub_objs]
            sub_obj_attrs_i = [
                i for i in sub_obj_attrs if i not in sub_obj_attrs_for_removal
            ]
            if sub_obj_attr == "related_units" and "children" in sub_obj_attrs_i:
                sub_obj_attrs_i.remove("children")
            for sub_obj in sub_objs:
                yield from query_stuff(
                    obj=sub_obj,
                    sub_obj_attrs=sub_obj_attrs_i,
                    query=queries,
                    query_type=query_type,
                    include_obj=True,
                )


T = TypeVar("T")


class NoElementError(Exception):
    """
    Raised when there is no unique element in the generator.
    """

    pass


class NoUniqueElementError(Exception):
    """
    Raised when there is no unique element in the generator.
    """

    pass


def unique(generator: Generator[T, None, None]) -> T:
    """
    Returns the unique element from the generator.
    Raises an error if the generator yields more than one unique element.

    :param generator: A generator that yields elements.
    :return: The unique element.
    :raises ValueError: If the generator yields more than one unique element or no elements.
    """
    try:
        # Get the first element from the generator
        unique_element = next(generator)
    except StopIteration as e:
        # Raise an error if the generator yields no elements
        raise NoElementError("Generator yields no elements") from e

    try:
        # Try to get the second element from the generator
        next(generator)
        # If we get here, it means there is more than one element
        raise NoUniqueElementError("Generator yields more than one unique element")
    except StopIteration:
        # If StopIteration is raised, it means there was only one element
        pass

    return unique_element
