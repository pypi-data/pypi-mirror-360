import logging
from typing import Any, Literal, Optional, TypeVar, Generic, Union, overload
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from ..model.get_by import BasicModelGetByOperations


_log = logging.getLogger(__name__)


M = TypeVar('M')
A = TypeVar('A', bound=BaseModel, default=Any)
E = TypeVar('E', bound=BaseModel, default=Any)
O = TypeVar('O', bound=BaseModel, default=Any)


class BasicGetBySchemeOperations(
        BasicModelGetByOperations[M],
        Generic[M, A, E, O]
):

    model: type[M]
    input_scheme: type[A]
    edit_scheme: type[E]
    out_scheme: type[O]

    pks: list[str]
    loads: dict[str, str]

    @overload
    async def get_by(
        self,
        *,
        session: AsyncSession,
        loads: Optional[dict[str, str]] = None,
        is_model: Literal[True],
        is_get_none: Literal[True],
        **kwargs: Any
    ) -> Optional[M]: ...

    @overload
    async def get_by(
        self,
        *,
        session: AsyncSession,
        loads: Optional[dict[str, str]] = None,
        is_model: Literal[True],
        is_get_none: Literal[False] = False,
        **kwargs: Any
    ) -> M: ...

    @overload
    async def get_by(
        self,
        *,
        session: AsyncSession,
        loads: Optional[dict[str, str]] = None,
        is_get_none: Literal[True],
        **kwargs: Any
    ) -> Optional[O]: ...

    @overload
    async def get_by(
        self,
        *,
        session: AsyncSession,
        loads: Optional[dict[str, str]] = None,
        is_get_none: Literal[False] = False,
        **kwargs: Any
    ) -> O: ...

    @overload
    async def get_by(
        self,
        *,
        session: AsyncSession,
        loads: Optional[dict[str, str]] = None,
        is_model: bool = False,
        is_get_none: bool = False,
        **kwargs: Any
    ) -> Union[M, O, None]: ...

    async def get_by(
        self,
        *,
        session: AsyncSession,
        loads: Optional[dict[str, str]] = None,
        is_model: bool = False,
        is_get_none: bool = False,
        **kwargs: Any
    ) -> Union[O, M, None]:
        ...
        """
        Получение объекта по полям

        Args:
            session (AsyncSession): Сессия
            loads (Optional[dict[str, str]], optional): Список полей для дополнительной загрузки. Defaults to None.
            is_model (bool, optional): Возвращать ли объект модели. Defaults to True.
            is_get_none (bool, optional): Возвращать ли None, если объект не найден. Defaults to False.
            **kwargs (Any): Поля

        Raises:
            HTTPException: 404 Нет обязательных полей

        Returns:
            Optional[O, M]: Объект
        """
        if not all(pk in kwargs.keys() for pk in self.pks):
            raise HTTPException(
                status_code=404,
                detail=f"Нет обязательных полей {self.pks}"
            )

        if loads is None and not is_model:
            loads = self.loads

        if is_get_none:
            model = await super().get_by(
                session=session,
                loads=loads,
                is_get_none=True,
                **kwargs
            )
        else:
            model = await super().get_by(
                session=session,
                loads=loads,
                **kwargs
            )

        if is_model:
            return model

        return self.out_scheme.model_validate(model)

    @overload
    async def get_by_query(
        self,
        session: AsyncSession,
        query: Select[Any],
    ) -> M: ...

    @overload
    async def get_by_query(
        self,
        session: AsyncSession,
        query: Select[Any],
        is_get_none: Literal[True],
    ) -> Optional[M]: ...

    @overload
    async def get_by_query(
        self,
        session: AsyncSession,
        query: Select[Any],
        *,
        is_model: Literal[False]
    ) -> O: ...

    @overload
    async def get_by_query(
        self,
        session: AsyncSession,
        query: Select[Any],
        is_get_none: Literal[True],
        is_model: Literal[False]
    ) -> Optional[O]: ...

    async def get_by_query(
        self,

        session: AsyncSession,

        query: Select[Any],

        is_get_none: bool = False,

        is_model: bool = True,

    ) -> Union[M, O, None]:
        """Получение объекта по запросу

        Args:
            session (AsyncSession): Сессия
            query (Select[Any]): Запрос
            is_get_none (bool, optional): Возвращать ли None, если объект не найден. По умолчанию False
            is_model (bool, optional): Возвращать ли объект модели. По умолчанию True

        Returns:
            Union[M, O, None]: Объект
        """

        if is_get_none:
            model = await super().get_by_query(
                session=session,
                query=query,
                is_get_none=True
            )

            if model is None:
                return None

        else:
            model = await super().get_by_query(
                session=session,
                query=query,
            )

        if is_model:
            return model
        return self.out_scheme.model_validate(model)
