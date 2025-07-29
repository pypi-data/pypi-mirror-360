import logging
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import class_mapper

from .add import BasicAddSchemeOperations
from .get_by import BasicGetBySchemeOperations
from .get_all import BasicGetAllSchemeOperations
from .edit import BasicEditSchemeOperations
from .delete import BasicDeleteSchemeOperations


_log = logging.getLogger(__name__)


M = TypeVar('M')
A = TypeVar('A', bound=BaseModel, default=Any)
E = TypeVar('E', bound=BaseModel, default=Any)
O = TypeVar('O', bound=BaseModel, default=Any)


class ManagerModelSchemes(
    BasicAddSchemeOperations[M, A, E, O],
    BasicGetBySchemeOperations[M, A, E, O],
    BasicGetAllSchemeOperations[M, A, E, O],
    BasicEditSchemeOperations[M, A, E, O],
    BasicDeleteSchemeOperations[M, A, E, O],
    Generic[M, A, E, O],
):
    """Менеджер для работы со схемами и моделями

    Args:
        BasicAddSchemeOperations (_type_): Создание объекта
        BasicGetBySchemeOperations (_type_): Получение объекта
        BasicGetAllSchemeOperations (_type_): Получение всех объектов
        BasicEditSchemeOperations (_type_): Редактирование объекта
        BasicDeleteSchemeOperations (_type_): Удаление объекта
    """

    def __init__(
        self,
        model: type[M],
        add_scheme: type[A],
        edit_scheme: type[E],
        out_scheme: type[O]
    ) -> None:
        """Менеджер для работы со схемами и моделями 

        Args:
            model (type[M]): Модель
            add_scheme (type[A]): Схема добавления
            edit_scheme (type[E]): Схема редактирования
            out_scheme (type[O]): Схема вывода
        """

        self.model = model
        self.add_scheme = add_scheme
        self.edit_scheme = edit_scheme
        self.out_scheme = out_scheme

        primary_key = self.model.__table__.primary_key  # type: ignore
        self.pks: list[str] = [
            col.name  # type: ignore
            for col in primary_key.columns  # type: ignore
            if not any(isinstance(constraint, ForeignKey)
                       for constraint in col.foreign_keys)  # type: ignore
        ]

        mapper = class_mapper(self.model)
        self.attrs_rel: dict[str, str] = {}

        self.type_cols: dict[str, Any] = {}
        for attr in mapper.columns:
            self.type_cols[attr.key] = attr.type.python_type

        for attr in mapper.relationships:  # type: ignore
            self.attrs_rel[attr.key] = attr.direction.name

        schema = self.out_scheme.model_json_schema()
        self.attrs_out_scheme: Optional[list[str]] = schema.get(
            "properties", {}).keys()
        if self.attrs_out_scheme is None:
            self.attrs_out_scheme = []

        self.loads: dict[str, str] = {}
        for key, val in self.attrs_rel.items():
            if key in self.attrs_out_scheme:
                if val == "MANYTOMANY" or val == "ONETOMANY":
                    self.loads[key] = "s"
                elif val == "MANYTOONE" or val == "ONETOONE":
                    self.loads[key] = "j"
