import logging
from typing import Any, Literal, Optional, TypeVar, Generic, Union, overload
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload


_log = logging.getLogger(__name__)


M = TypeVar('M')


class BasicModelAddOperations(Generic[M]):

    model: type[M]
    pks: list[str]

    @overload
    async def add(
        self,
        *,
        session: AsyncSession,
        data: Union[M, dict[str, Any]]
    ) -> M:
        ...

    @overload
    async def add(
        self,
        *,
        session: AsyncSession,
        data: Union[M, dict[str, Any]],
        loads: dict[str, str]
    ) -> M:
        ...

    @overload
    async def add(
        self,
        *,
        session: AsyncSession,
        data: Union[M, dict[str, Any]],
        return_query: Select[Any]
    ) -> M:
        ...

    @overload
    async def add(
        self,
        *,
        session: AsyncSession,
        data: Union[M, dict[str, Any]],
        is_return: Literal[False] = False
    ) -> None:
        ...

    @overload
    async def add(
        self,
        *,
        session: AsyncSession,
        data: Union[M, dict[str, Any]],
        is_return: bool = True,
        loads: Optional[dict[str, str]] = None,
        return_query: Optional[Select[Any]] = None
    ) -> Optional[M]:
        ...

    async def add(
        self,

        session: AsyncSession,

        data: Union[M, dict[str, Any]],

        is_return: bool = True,

        loads: Optional[dict[str, str]] = None,

        return_query: Optional[Select[Any]] = None

    ) -> Optional[M]:
        """Создание объекта в базе

        Args:
            session (AsyncSession): Сессия
            data (Union[M, dict]): Объект
            is_return (bool, optional): Возвращать ли объект после создания. По умолчанию возвращается.
            loads (Optional[dict[str, str]], optional): Список полей для дополнительной загрузки. По умолчанию не загружается.
            return_query (Optional[Select], optional): Запрос для возврата объекта. (Какие-то дополнительные условия).

        Raises:
            HTTPException: 500 - ошибка в базе при добавлении

        Returns:
            Optional[M]: Объект


        Example:

            ### Для сложных случаев можно использовать свой return_query, по умолчанию он создается автоматически
            return_user_add_query = select(
                User
                ).options(
                    joinedload(
                        User.role
                    ).selectinload(
                        User.permissions
                    )
                )

            user_add = await db_client.user.add(
                session=session, 
                data=data, 
                is_return=True, 
                loads={
                    "role": "j", # joinedload
                    "permissions": "s" # selectinload
                },
                return_query=return_user_add_query
            )
        """

        _log.debug("Add model %s", self.model.__name__)

        if isinstance(data, dict):
            model: M = self.model(**data)
        else:
            model = data

        session.add(model)
        await session.flush()

        if not is_return:
            return None

        if return_query is None:
            stmt = select(self.model)
        else:
            stmt = return_query

        filter_pks = [
            getattr(self.model, pk) == getattr(model, pk)
            for pk in self.pks
        ]

        stmt = stmt.filter(
            *filter_pks
        )

        if loads:
            for key, val in loads.items():
                if val == "s":
                    stmt = stmt.options(
                        selectinload(getattr(self.model, key))
                    )
                elif val == "j":
                    stmt = stmt.options(
                        joinedload(getattr(self.model, key))
                    )

        r = await session.execute(stmt)
        return_model = r.scalars().first()

        return return_model
