from __future__ import annotations

import logging
from dataclasses import fields, is_dataclass
from functools import lru_cache

import sqlalchemy.inspection
import sqlalchemy.orm
from sqlalchemy import Column
from sqlalchemy.orm import MANYTOONE, DeclarativeBase, declared_attr, ONETOMANY
from sqlalchemy.sql.schema import Table
from typing_extensions import Type, get_args, Dict, Any, TypeVar, Generic

from .utils import recursive_subclasses

logger = logging.getLogger(__name__)

T = TypeVar('T')
_DAO = TypeVar("_DAO", bound="DataAccessObject")


class NoGenericError(TypeError):
    def __init__(self, cls):
        super().__init__(f"Cannot determine original class for {cls.__name__!r}. "
                         "Did you forget to parameterise the DataAccessObject subclass?")


def is_data_column(column: Column):
    return not column.primary_key and len(column.foreign_keys) == 0 and column.name != "polymorphic_type"

class HasGeneric(Generic[T]):

    @classmethod
    @lru_cache(maxsize=None)
    def original_class(cls) -> Type:
        """
        :return: The original class of this DAO.
        """
        # Fall back to the original method for manually created classes
        try:
            # Look for DataAccessObject in the class's MRO (Method Resolution Order)
            for base_cls in cls.__mro__:
                if base_cls is DataAccessObject:
                    # Found DataAccessObject, now find the generic parameter
                    for base in cls.__orig_bases__:
                        if hasattr(base, "__origin__") and base.__origin__ is DataAccessObject:
                            type_args = get_args(base)
                            if type_args:
                                return type_args[0]

            # If we get here, we didn't find a DataAccessObject base with a generic parameter
            # Try the original approach as a fallback
            for base in getattr(cls, "__orig_bases__", []):
                type_args = get_args(base)
                if type_args:
                    return type_args[0]

            raise NoGenericError(cls)
        except (AttributeError, IndexError):
            raise NoGenericError(cls)

class DataAccessObject(HasGeneric[T]):
    """
    This class defines the interfaces the DAO classes should implement.

    ORMatic generates classes from your python code that are derived from the provided classes in your package.
    The generated classes can be instantiated from objects of the given classes and vice versa.
    This class describes the necessary functionality.
    """


    @classmethod
    def to_dao(cls, obj: T, memo: Dict[int, Any] = None) -> _DAO:
        """
        Create an instance of this class from an instance of the original class.
        This method checks the fields in the DAO and tries to copy the value from `obj`.
        If the type of the field in this class is another DAO, the construction recurses into the type.

        If a different specification than the specification of the original class is needed, overload this method.


        :param obj: The instance of the original class.
        :param memo: The memo dictionary to use for memoization.
        :return: An instance of this class created from the original class.
        """

        if memo is None:
            memo = {}
        if id(obj) in memo:
            return memo[id(obj)]

        # TODO if the object passed in has an alternative mapping, construct the alternative mapping first
        # if isinstance(obj, AlternativeMapping):
        #     alternative_mapping_cls = get_alternative_mapping(type(obj))
        #     obj = alternative_mapping_cls.from_dao(obj, memo=memo)
        #
        # Create a new instance of the DAO class
        dao_instance = cls()

        # Fill super class columns, Mapper-columns - self.columns
        mapper: sqlalchemy.orm.Mapper = sqlalchemy.inspection.inspect(cls)

        all_columns = mapper.columns
        columns_of_this_table = cls.__table__.columns
        columns_of_parent = [c for c in all_columns if c.name not in columns_of_this_table]

        base = cls.__bases__[0]

        # handle classes that have a super class that's alternatively mapped
        if issubclass(base, DataAccessObject) and issubclass(base.original_class(), AlternativeMapping):

            # create dao of alternativly mapped superclass
            parent_dao = base.original_class().to_dao(obj)

            # copy values from superclass dao
            for column in columns_of_parent:
                if is_data_column(column):
                    setattr(dao_instance, column.name, getattr(parent_dao, column.name))

            # copy values that only occur in this table def
            for column in columns_of_this_table:
                if is_data_column(column):
                    setattr(dao_instance, column.name, getattr(obj, column.name))

        else:

            # copy all data required for the table
            for column in all_columns:
                if is_data_column(column):
                    setattr(dao_instance, column.name, getattr(obj, column.name))


        for relationship in mapper.relationships:
            # update one to one like relationships
            if (relationship.direction == MANYTOONE or
                    (relationship.direction == ONETOMANY and not relationship.uselist)):
                try:
                    value_in_obj = getattr(obj, relationship.key)
                    if value_in_obj is None:
                        dao_of_value = None
                    else:
                        dao_class = get_dao_class(type(value_in_obj))
                        if dao_class is None:
                            raise ValueError(f"Class {type(value_in_obj)} does not have a DAO.")
                        if issubclass(dao_class.original_class(), AlternativeMapping):
                            dao_of_value = dao_class.original_class().to_dao(value_in_obj, memo=memo)
                            dao_of_value = dao_class.to_dao(dao_of_value, memo=memo)
                        else:
                            dao_of_value = dao_class.to_dao(value_in_obj, memo=memo)

                    setattr(dao_instance, relationship.key, dao_of_value)
                except ValueError as e:
                    logger.warning(f"Skipping relationship {relationship.key} because {e} ")

            # update one to many relationships (list of other objects)
            elif relationship.direction == ONETOMANY:
                result = []
                try:
                    value_in_obj = getattr(obj, relationship.key)
                    for v in value_in_obj:
                        result.append(get_dao_class(type(v)).to_dao(v, memo=memo))
                except AttributeError as e:
                    logger.warning(f"Skipping relationship {relationship.key} because {e} ")
                setattr(dao_instance, relationship.key, result)
        memo[id(obj)] = dao_instance

        return dao_instance

    def from_dao(self, memo: Dict[int, Any] = None) -> T:
        """
        Create the original instance of this class from an instance of this DAO.
        If a different specification than the specification of the original class is needed, overload this method.

        :param memo: The memo dictionary to use for memoization.
        :return: An instance of this class created from the original class.
        """
        if memo is None:
            memo = {}
        if id(self) in memo:
            return memo[id(self)]

        init_of_original_cls = self.original_class().__init__

        # get the args and kwargs of the original init
        raise NotImplementedError


    def __repr__(self):
        cls = self.__class__
        attr_items: list[tuple[str, object]] = []

        # 1) Try to obtain the SQLAlchemy mapper to get the column order.
        try:
            from sqlalchemy.inspection import inspect as _sa_inspect

            mapper = _sa_inspect(cls, raiseerr=False)
            if mapper is not None:
                for column in mapper.columns:
                    key = column.key
                    # Attributes might be deferred / unloaded, getattr handles that.
                    if not key.startswith("_"):
                        attr_items.append((key, getattr(self, key, None)))
        except Exception:  # pragma: no cover – any error → graceful fallback
            mapper = None  # noqa: F841 – keep the name for clarity

        # 2) Fallback to type hints declared on the class.
        if not attr_items and hasattr(cls, "__annotations__"):
            for key in cls.__annotations__:
                if not key.startswith("_") and hasattr(self, key):
                    attr_items.append((key, getattr(self, key)))

                    # 3) Final fallback to whatever is present on the instance.
        if not attr_items:
            for key, value in self.__dict__.items():
                if not key.startswith("_"):
                    attr_items.append((key, value))

                    # Build the string.
        inner = ", ".join(f"{k}={v!r}" for k, v in attr_items)
        return f"{cls.__name__}({inner})"


class AlternativeMapping(HasGeneric[T]):

    @classmethod
    def to_dao(cls, obj: T, memo: Dict[int, Any] = None) -> _DAO:
        """
        Specifies how to build an instance of this class from an instance of the original class.
        """
        if memo is None:
            memo = {}
        if id(obj) in memo:
            return memo[id(obj)]
        else:
            return obj

@lru_cache(maxsize=None)
def get_dao_class_of_mapped(cls: Type):
    for dao in recursive_subclasses(DataAccessObject):
        if dao.original_class() == cls:
            return dao
    return None

@lru_cache(maxsize=None)
def get_alternative_mapping(cls: Type):
    for alt_mapping in recursive_subclasses(AlternativeMapping):
        if alt_mapping.original_class() == cls:
            return alt_mapping
    return None

@lru_cache(maxsize=None)
def get_dao_class(cls: Type):
    alternative_mapping = get_alternative_mapping(cls)
    if alternative_mapping:
        return get_dao_class_of_mapped(alternative_mapping)
    else:
        return get_dao_class_of_mapped(cls)