import logging
from typing import Any, TypeVar, Generic
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...base_schemes import ResponseStatus

from ..model.delete import BasicModelDeleteOperations


_log = logging.getLogger(__name__)


M = TypeVar('M')
A = TypeVar('A', bound=BaseModel, default=Any)
E = TypeVar('E', bound=BaseModel, default=Any)
O = TypeVar('O', bound=BaseModel, default=Any)


class BasicDeleteSchemeOperations(
        BasicModelDeleteOperations[M],
        Generic[M, A, E, O]
):

    model: type[M]
    input_scheme: type[A]
    edit_scheme: type[E]
    out_scheme: type[O]

    pks: list[str]
    loads: dict[str, str]

    async def delete(
        self,

        session: AsyncSession,

        **pks: Any,

    ) -> ResponseStatus:
        """Удаление объекта

        Args:
            session (AsyncSession): Сессия
            **pks (Any): Первыичные ключ

        Returns:
            ResponseStatus: Статус успешного удаления
        """

        return await super().delete(
            session=session,
            **pks
        )
