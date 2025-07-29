import logging
from typing import Any, TypeVar, Generic
from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from ...base_schemes import ResponseStatus


_log = logging.getLogger(__name__)


M = TypeVar('M')


class BasicModelDeleteOperations(Generic[M]):

    model: type[M]
    pks: list[str]

    async def delete(
        self,

        session: AsyncSession,

        **pks: Any,

    ) -> ResponseStatus:
        """Удаление объекта из БД

        Args:
            session (AsyncSession): Сессия
            **pks (Any): Первыичные ключ для поиска объекта

        Raises:
            HTTPException: 404 - Объект не найден

        Returns:
            ResponseStatus: Статус, что объект удален успешно
        """

        _log.info("Delete model %s", self.model.__name__)

        stmt = delete(
            self.model
        ).filter_by(**pks)

        r = await session.execute(stmt)
        delete_count = r.rowcount

        if delete_count == 0:
            raise HTTPException(
                status_code=404, detail=f"{self.model.__name__} not found")

        await session.flush()

        return ResponseStatus()
