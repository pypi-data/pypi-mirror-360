import logging
from typing import Any, Literal, Optional, TypeVar, Generic, Union, overload
from pydantic import BaseModel
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from ..model.edit import BasicModelEditOperations


_log = logging.getLogger(__name__)


M = TypeVar('M')
A = TypeVar('A', bound=BaseModel, default=Any)
E = TypeVar('E', bound=BaseModel, default=Any)
O = TypeVar('O', bound=BaseModel, default=Any)


class BasicEditSchemeOperations(
        BasicModelEditOperations[M],
        Generic[M, A, E, O]
):

    model: type[M]
    input_scheme: type[A]
    edit_scheme: type[E]
    out_scheme: type[O]

    pks: list[str]
    loads: dict[str, str]

    @overload
    async def edit(
        self,

        session: AsyncSession,

        edit_item: dict[str, Any],

        loads: Optional[dict[str, str]] = None,

        is_return: Literal[False] = False,

        return_query: Optional[Select[Any]] = None,

        is_get_none: bool = True,

        is_model: bool = True,

        **pks: Any

    ) -> None: ...

    @overload
    async def edit(
        self,

        session: AsyncSession,

        edit_item: dict[str, Any],

        loads: Optional[dict[str, str]] = None,

        is_return: Literal[True] = True,

        return_query: Optional[Select[Any]] = None,

        is_get_none: Literal[False] = False,

        is_model: Literal[True] = True,

        **pks: Any

    ) -> M: ...

    @overload
    async def edit(
        self,

        session: AsyncSession,

        edit_item: dict[str, Any],

        loads: Optional[dict[str, str]] = None,

        is_return: Literal[True] = True,

        return_query: Optional[Select[Any]] = None,

        is_get_none: Literal[True] = True,

        is_model: Literal[True] = True,

        **pks: Any

    ) -> Optional[M]: ...

    @overload
    async def edit(
        self,

        session: AsyncSession,

        edit_item: dict[str, Any],

        loads: Optional[dict[str, str]] = None,

        is_return: Literal[True] = True,

        return_query: Optional[Select[Any]] = None,

        is_get_none: Literal[False] = False,

        is_model: Literal[False] = False,

        **pks: Any

    ) -> O: ...

    @overload
    async def edit(
        self,

        session: AsyncSession,

        edit_item: dict[str, Any],

        loads: Optional[dict[str, str]] = None,

        is_return: Literal[True] = True,

        return_query: Optional[Select[Any]] = None,

        is_get_none: Literal[True] = True,

        is_model: Literal[False] = False,

        **pks: Any

    ) -> Optional[O]: ...

    @overload
    async def edit(
        self,

        session: AsyncSession,

        edit_item: dict[str, Any],

        loads: Optional[dict[str, str]],

        is_return: bool,

        return_query: Optional[Select[Any]],

        is_get_none: bool,

        is_model: Literal[True] = True,

        **pks: Any

    ) -> Optional[M]: ...

    @overload
    async def edit(
        self,

        session: AsyncSession,

        edit_item: dict[str, Any],

        loads: Optional[dict[str, str]],

        is_return: bool,

        return_query: Optional[Select[Any]],

        is_get_none: bool,

        is_model: Literal[False] = False,

        **pks: Any

    ) -> Optional[O]: ...

    @overload
    async def edit(
        self,

        session: AsyncSession,

        edit_item: dict[str, Any],

        loads: Optional[dict[str, str]],

        is_return: bool,

        return_query: Optional[Select[Any]],

        is_get_none: bool,

        is_model: bool,

        **pks: Any

    ) -> Union[M, O, None]: ...

    async def edit(
        self,

        session: AsyncSession,

        edit_item: dict[str, Any],

        loads: Optional[dict[str, str]] = None,

        is_return: bool = True,

        return_query: Optional[Select[Any]] = None,

        is_get_none: bool = True,

        is_model: bool = True,

        **pks: Any

    ) -> Union[M, O, None]:
        """Изменение объекта

        Args:
            session (AsyncSession): Сессия
            edit_item (dict[str, Any]): Поля для изменения
            loads (Optional[dict[str, str]], optional): Список полей для загрузки связанных объектов. По умолчанию None.
            is_return (bool, optional): Возвращать ли обновленный объект. По умолчанию True.
            return_query (Optional[Select[Any]], optional): Запрос для возврата. По умолчанию None.
            is_get_none (bool, optional): Возвращает None, если не найден. По умолчанию True.
            is_model (bool, optional): _Возвращает ли объекта в виде модели или схемы. По умолчанию True.


        Returns:
            Union[M, O, None]: Объект
        """

        if loads is None and not is_model:
            loads = self.loads

        return_model = await super().edit(
            session=session,
            edit_item=edit_item,
            loads=loads,
            is_return=is_return,
            return_query=return_query,
            is_get_none=is_get_none,
            **pks
        )

        if is_model:
            return return_model

        if return_model is None:
            return None

        return self.out_scheme.model_validate(return_model)
