import logging
from typing import Any, Generic, TypeVar
from sqlalchemy import ForeignKey, Column
from sqlalchemy.orm import class_mapper

from .add import BasicModelAddOperations
from .get_all import BasicModelGetAllOperations
from .get_by import BasicModelGetByOperations
from .edit import BasicModelEditOperations
from .delete import BasicModelDeleteOperations


_log = logging.getLogger(__name__)


M = TypeVar('M')


# class BasicModelGetByOperations наследуется из BasicModelEditOperations
class ManagerModel(
    BasicModelAddOperations[M],
    BasicModelGetAllOperations[M],
    BasicModelGetByOperations[M],
    BasicModelEditOperations[M],
    BasicModelDeleteOperations[M],
    Generic[M]
):
    """
    Менеджер для работы с моделями

    Args:
        BasicModelAddOperations (_type_): Работа с добавлением
        BasicModelGetAllOperations (_type_): Работа с получением всех объектов
        BasicModelEditOperations (_type_): Работа с редактированием и получением по id и полям
        BasicModelDeleteOperations (_type_): Работа с удалением
        BasicModelGetByOperations (_type_): Работа с получением по полям
        Generic (_type_): _type_
    """

    def __init__(self, model: type[M]) -> None:
        """Менеджер для работы с моделями

        Args:
            model (type[M]): Модель
        """
        self.model = model

        primary_key = self.model.__table__.primary_key  # type: ignore
        self.pks: list[str] = [
            col.name  # type: ignore
            for col in primary_key.columns  # type: ignore
            if not any(isinstance(constraint, ForeignKey)
                       for constraint in col.foreign_keys)  # type: ignore
        ]

        mapper = class_mapper(self.model)
        self.mapper = mapper
        self.attrs_rel: dict[str, str] = {}

        self.type_cols: dict[str, Any] = {}
        self.info_cols: list[Column[Any]] = []
        for attr in mapper.columns:
            self.type_cols[attr.key] = attr.type.python_type
            self.info_cols.append(attr)

        for attr in mapper.relationships:  # type: ignore
            self.attrs_rel[attr.key] = attr.direction.name

        self.loads: dict[str, str] = {}
        for key, val in self.attrs_rel.items():
            if val == "MANYTOMANY" or val == "ONETOMANY":
                self.loads[key] = "s"
            elif val == "MANYTOONE" or val == "ONETOONE":
                self.loads[key] = "j"
