from enum import Enum
import inspect
import logging
from typing import Annotated, Any, Generic, Literal, Optional, Sequence, TypeVar, Union
from fastapi import APIRouter, Depends, params
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from .basic_api import BasicApi
from ..base_schemes import ListDTO, ResponseStatus

from ..basic_operations.model_with_schemes import ManagerModelSchemes


_log = logging.getLogger(__name__)

M = TypeVar('M')
A = TypeVar('A', bound=BaseModel, default=Any)
E = TypeVar('E', bound=BaseModel, default=Any)
O = TypeVar('O', bound=BaseModel, default=Any)


class ManagerApiModelWithSchemes(
    ManagerModelSchemes[M, A, E, O],
    BasicApi,
    Generic[M, A, E, O]
):
    """Менеджер для работы со схемами, моделями и автогенерацией API

    Args:
        ManagerModelSchemes (_type_): Менеджер для работы со схемами, моделями
        BasicApi (_type_): Базовое создание API
    """

    def __init__(
        self,

        model: type[M],

        add_scheme: type[A],

        edit_scheme: type[E],

        out_scheme: type[O],

        session_factory: async_sessionmaker[AsyncSession],

        search_fields: Optional[list[str]] = None,

        return_get_all: Literal["pagination", "list"] = "pagination",

        prefix: Optional[str] = None,

        tags: Optional[list[Union[str, Enum]]] = None,

        dependencies: Optional[Sequence[params.Depends]] = None,

    ) -> None:
        """Менеджер для работы со схемами, моделями и автогенерацией API

        Args:
            model (type[M]): Модель
            add_scheme (type[A]): Схема добавления
            edit_scheme (type[E]): Схема редактирования
            out_scheme (type[O]): Схема вывода
            session_factory (async_sessionmaker[AsyncSession]): Фабрика сессии
            search_fields (Optional[list[str]], optional): Поля поиска. По умолчанию None.
            return_get_all (Literal["pagination", "list"], optional): Возвращать пагинацию или список. По умолчанию "pagination".
            prefix (Optional[str], optional): Свой префикс. По умолчанию None.
            tags (Optional[list[Union[str, Enum]]], optional): Свой список тегов. По умолчанию None.
            dependencies (Optional[Sequence[params.Depends]], optional): Зависимости. По умолчанию None.

        """

        super().__init__(
            model,
            add_scheme,
            edit_scheme,
            out_scheme
        )

        prefix = prefix if prefix else f"/{self.model.__name__.lower()}"
        tags = tags if tags else [self.model.__name__]

        router = APIRouter(
            prefix=prefix,
            tags=tags,
            dependencies=dependencies,
        )

        BasicApi.__init__(
            self=self,
            router=router,
            session_factory=session_factory,
            search_fields=search_fields,
            return_get_all=return_get_all,
            prefix=prefix,
            tags=tags,
            dependencies=dependencies
        )

        self.__fill_router()

    def __fill_router(self) -> None:
        self.__create_get_all()
        self.__create_add()
        self.__create_get_by()
        self.__create_edit()
        self.__create_delete()

    def __create_get_by(self):
        output = self.out_scheme

        path = ""
        for pk in self.pks:
            path += "/{" + pk + "}"

        self.router.add_api_route(
            path=path,
            endpoint=self.__create_func_get_by(),
            methods=["GET"],
            response_model=output
        )

    def __create_func_get_by(self):
        pks = self.pks
        type_cols = self.type_cols

        params = [
            inspect.Parameter(
                name=pk,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=type_cols[pk]
            )
            for pk in pks
        ]

        params.insert(0, inspect.Parameter(
            name="session",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[AsyncSession, Depends(self.get_db_session)],
        ))

        signature = inspect.Signature(params)

        async def get_by(*args: Any, **kwargs: Any) -> O:
            bound_args = signature.bind(*args, **kwargs)
            bound_args.apply_defaults()

            pk_values = {pk: bound_args.arguments[pk] for pk in pks}

            session = bound_args.arguments["session"]
            return await self.get_by(
                session=session,
                is_model=False,
                is_get_none=False,
                **pk_values
            )

        get_by.__signature__ = signature  # type: ignore
        return get_by

    def __create_add(self):
        self.router.add_api_route(
            path="",
            endpoint=self.__create_func_add(),
            methods=["POST"],
            response_model=self.out_scheme
        )

    def __create_func_add(self):
        add_schema = self.add_scheme

        params = [
            inspect.Parameter(
                name="session",
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[AsyncSession,
                                     Depends(self.get_db_session)],
            ),
            inspect.Parameter(
                name="data",
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=add_schema,
            ),
        ]

        signature = inspect.Signature(params)

        async def add(*args: Any, **kwargs: Any) -> O:
            bound_args = signature.bind(*args, **kwargs)
            bound_args.apply_defaults()

            session = bound_args.arguments["session"]
            data = bound_args.arguments["data"]
            return await self.add(
                session=session,
                data=data,
                is_model=False
            )

        add.__signature__ = signature  # type: ignore
        return add

    def __create_get_all(self):
        if self.return_get_all == "pagination":
            self.router.add_api_route(
                path="/all",
                endpoint=self.__create_func_get_all(),
                methods=["GET"],
                response_model=ListDTO[self.out_scheme]
            )
        else:
            self.router.add_api_route(
                path="/all",
                endpoint=self.__create_func_get_all(),
                methods=["GET"],
                response_model=list[self.out_scheme]
            )

    def __create_func_get_all(self):

        async def get_all(
            session: Annotated[AsyncSession, Depends(self.get_db_session)],
            search: Union[str, None] = None,
            sort_by: Union[str, None] = None,
            desc: int = 0,
            page: int = 1,
            limit: int = -1,
        ):
            if self.return_get_all == "pagination":
                return await self.get_all(
                    session=session,
                    search=search,
                    search_fields=self.search_fields,
                    loads=self.loads,
                    sort_by=sort_by,
                    desc=desc,
                    page=page,
                    limit=limit,
                    is_model=False,
                    is_pagination=True
                )

            return await self.get_all(
                session=session,
                search=search,
                search_fields=self.search_fields,
                loads=self.loads,
                sort_by=sort_by,
                desc=desc,
                page=page,
                limit=limit,
                is_model=False,
                is_pagination=False
            )

        return get_all

    def __create_edit(self):
        output = self.out_scheme

        path = ""
        for pk in self.pks:
            path += "/{" + pk + "}"

        self.router.add_api_route(
            path=path,
            endpoint=self.__create_func_edit(),
            methods=["PATCH"],
            response_model=output
        )

    def __create_func_edit(self):
        pks = self.pks
        type_cols = self.type_cols

        params = [
            inspect.Parameter(
                name=pk,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=type_cols[pk]
            )
            for pk in pks
        ]

        params.insert(0, inspect.Parameter(
            name="session",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[AsyncSession, Depends(self.get_db_session)],
        ))

        params.insert(0, inspect.Parameter(
            name="edit_item",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=self.edit_scheme,
        ))

        signature = inspect.Signature(params)

        async def edit(*args: Any, **kwargs: Any) -> O:
            bound_args = signature.bind(*args, **kwargs)
            bound_args.apply_defaults()

            pk_values: dict[str, Any] = {
                pk: bound_args.arguments[pk] for pk in pks}

            session = bound_args.arguments["session"]
            edit_item = bound_args.arguments["edit_item"]
            return await self.edit(
                session=session,
                edit_item=edit_item.model_dump(),
                loads=None,
                is_return=True,
                return_query=None,
                is_get_none=False,
                is_model=False,
                **pk_values
            )

        edit.__signature__ = signature  # type: ignore
        return edit

    def __create_delete(self):
        path = ""
        for pk in self.pks:
            path += "/{" + pk + "}"

        self.router.add_api_route(
            path=path,
            endpoint=self.__create_func_delete(),
            methods=["DELETE"],
            response_model=ResponseStatus
        )

    def __create_func_delete(self):
        pks = self.pks
        type_cols = self.type_cols

        params = [
            inspect.Parameter(
                name=pk,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=type_cols[pk]
            )
            for pk in pks
        ]

        params.insert(0, inspect.Parameter(
            name="session",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[AsyncSession, Depends(self.get_db_session)],
        ))

        signature = inspect.Signature(params)

        async def delete(*args: Any, **kwargs: Any) -> ResponseStatus:
            bound_args = signature.bind(*args, **kwargs)
            bound_args.apply_defaults()

            pk_values = {pk: bound_args.arguments[pk] for pk in pks}

            session = bound_args.arguments["session"]
            return await self.delete(
                session=session,
                **pk_values
            )

        delete.__signature__ = signature  # type: ignore
        return delete
