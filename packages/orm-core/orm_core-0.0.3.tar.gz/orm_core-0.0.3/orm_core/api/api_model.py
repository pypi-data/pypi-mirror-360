from enum import Enum
from typing import Any, AsyncGenerator,  Generic, Literal, Optional, Sequence, TypeVar, Union
from fastapi import APIRouter, params
from pydantic import BaseModel, ConfigDict, create_model
from sqlalchemy import Column
from sqlalchemy.util import ReadOnlyProperties
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.sql.base import ReadOnlyColumnCollection
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession


from ..basic_operations.model import ManagerModel

from .api_schemes import ManagerApiModelWithSchemes


M = TypeVar('M')


class ManagerApiModel(
    ManagerModel[M],
    Generic[M],
):
    """Менеджер для работы со схемами, моделями и автогенерацией API, только используя модель

    Args:
        ManagerModel (_type_): Базовый менеджер для работы с моделями
        BasicApi (_type_): Базовое создание API
    """

    def __init__(
        self,

        model: type[M],

        session_factory: async_sessionmaker[AsyncSession],

        search_fields: Optional[list[str]] = None,

        return_get_all: Literal["pagination", "list"] = "pagination",

        prefix: Optional[str] = None,

        tags: Optional[list[Union[str, Enum]]] = None,

        dependencies: Optional[Sequence[params.Depends]] = None,
    ) -> None:
        """Менеджер для работы со схемами, моделями и автогенерацией API, только используя модель

        Args:
            model (type[M]): Модель
            session_factory (async_sessionmaker[AsyncSession]): Фабрика сессий
            search_fields (Optional[list[str]], optional): Поля по которым можно осуществлять поиск. Defaults to None.
            return_get_all (Literal["pagination", "list"], optional): Возвращать ли список или пагинацию. Defaults to "pagination".
            prefix (Optional[str], optional): Префикс для API. Defaults to None.
            tags (Optional[list[Union[str, Enum]]], optional): Теги для API. Defaults to None.
            dependencies (Optional[Sequence[params.Depends]], optional): Зависимости для API. Defaults to None.
        """

        super().__init__(
            model=model
        )

        self.add_scheme = create_model(
            f"Add{self.model.__name__}DTO",
            __base__=BaseModel,
            **self.get_fileds_for_add(self.mapper.columns)
        )

        self.edit_scheme = create_model(
            f"Edit{self.model.__name__}DTO",
            __base__=BaseModel,
            **self.get_fileds_for_edit(self.mapper.columns)
        )

        self.out_scheme = create_model(
            f"Out{self.model.__name__}DTO",
            __base__=BaseModel,
            __config__=ConfigDict(from_attributes=True),
            **self.get_fileds_for_out(self.mapper.columns, self.mapper.relationships)
        )

        self.manager_api = ManagerApiModelWithSchemes(
            model=model,
            add_scheme=self.add_scheme,
            edit_scheme=self.edit_scheme,
            out_scheme=self.out_scheme,
            session_factory=session_factory,
            search_fields=search_fields,
            return_get_all=return_get_all,
            prefix=prefix,
            tags=tags,
            dependencies=dependencies
        )

    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        return self.manager_api.get_db_session()

    @property
    def router(self) -> APIRouter:
        return self.manager_api.router

    @property
    def prefix(self) -> Optional[str]:
        return self.manager_api.prefix

    @property
    def tags(self) -> Optional[list[Union[str, Enum]]]:
        return self.manager_api.tags

    @property
    def dependencies(self) -> Optional[Sequence[params.Depends]]:
        return self.manager_api.dependencies

    @property
    def search_fields(self) -> Optional[list[str]]:
        return self.manager_api.search_fields

    @property
    def return_get_all(self) -> Literal["pagination", "list"]:
        return self.manager_api.return_get_all

    def get_fileds_for_add(self, columns: ReadOnlyColumnCollection[str, Column[Any]]) -> dict[str, Any]:
        fields: dict[str, Any] = {}

        for column in columns:
            name = column.key
            type_: Any = column.type.python_type
            default: Any = ...

            if column.nullable:
                type_ = Optional[type_]
                default = None

            if column.default is not None:
                default = None

            fields[name] = (type_, default)

        return fields

    def get_fileds_for_out(
        self,
        columns: ReadOnlyColumnCollection[str, Column[Any]],
        relationships: ReadOnlyProperties[RelationshipProperty[Any]] | None = None
    ) -> dict[str, Any]:
        fields: dict[str, Any] = {}

        for column in columns:
            name = column.key
            type_: Any = column.type.python_type
            default: Any = ...

            if column.nullable:
                type_ = Optional[type_]
                default = None

            if column.default is not None:
                default = None

            fields[name] = (type_, default)

        if relationships is None:
            return fields

        for relation in relationships:
            name = relation.key

            class_relation = create_model(
                f"Out{name}DTO",
                __base__=BaseModel,
                __config__=ConfigDict(from_attributes=True),
                **self.get_fileds_for_out(
                    columns=relation.mapper.columns
                )
            )

            if relation.uselist and relation.direction.name == "ONETOMANY" or relation.direction.name == "MANYTOMANY":
                class_relation = list[class_relation]  # type: ignore
            else:
                class_relation = Optional[class_relation]  # type: ignore

            fields[name] = (class_relation, None)

        return fields

    def get_fileds_for_edit(self, columns: ReadOnlyColumnCollection[str, Column[Any]]) -> dict[str, Any]:
        fields: dict[str, Any] = {}

        for column in columns:
            if column.key in self.pks:
                continue

            name = column.key
            type_ = Optional[column.type.python_type]  # type: ignore
            default = None

            fields[name] = (type_, default)

        return fields
