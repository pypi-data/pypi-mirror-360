import logging
from typing import Any, Literal, Optional, Sequence, TypeVar, Generic, Union, overload
from fastapi import HTTPException
from sqlalchemy import Select, asc,  desc as func_desc, func, or_, select, cast
from sqlalchemy.types import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from ...base_schemes import ListDTO


_log = logging.getLogger(__name__)


M = TypeVar('M')


class BasicModelGetAllOperations(Generic[M]):

    model: type[M]

    @overload
    async def get_all(
        self,

        session: AsyncSession,

        search: Optional[str] = None,

        search_fields: Optional[list[str]] = None,

        loads: Optional[dict[str, str]] = None,

        sort_by: Optional[str] = None,

        query_select: Optional[Select[Any]] = None,

        desc: int = 0,

        page: int = 1,

        limit: int = -1,

        is_pagination: Literal[False] = False,

        **kwargs: Any

    ) -> Sequence[M]:
        ...

    @overload
    async def get_all(
        self,

        session: AsyncSession,

        search: Optional[str] = None,

        search_fields: Optional[list[str]] = None,

        loads: Optional[dict[str, str]] = None,

        sort_by: Optional[str] = None,

        query_select: Optional[Select[Any]] = None,

        desc: int = 0,

        page: int = 1,

        limit: int = -1,

        is_pagination: Literal[True] = True,

        **kwargs: Any

    ) -> ListDTO[M]:
        ...

    async def get_all(
        self,

        session: AsyncSession,

        search: Optional[str] = None,

        search_fields: Optional[list[str]] = None,

        loads: Optional[dict[str, str]] = None,

        sort_by: Optional[str] = None,

        query_select: Optional[Select[Any]] = None,

        desc: int = 0,

        page: int = 1,

        limit: int = -1,

        is_pagination: bool = True,

        **kwargs: Any

    ) -> Union[ListDTO[M], Sequence[M]]:
        """Получение списка моделей по фильтрам, сортировке и пагинацией из базы данных

        Args:
            session (AsyncSession): Сессия базы данных
            search (Optional[str], optional): Поиск по полям. Defaults to None.
            search_fields (Optional[list[str]], optional): Поля для поиска. Defaults to None.
            loads (Optional[dict[str, str]], optional): Поля для загрузки. Defaults to None.
            sort_by (Optional[str], optional): Поле для сортировки. Defaults to None.
            query_select (Optional[Select[Any]], optional): Запрос для выборки. Defaults to None.
            desc (int, optional): Порядок сортировки. Defaults to 0.
            page (int, optional): Номер страницы. Defaults to 1.
            limit (int, optional): Количество элементов на странице. Defaults to -1.
            is_pagination (bool, optional): Пагинация. Defaults to True.
            **kwargs (Any): Параметры фильтрации

        Raises:
            HTTPException: 400 - Некорректные параметры

        Returns:
            ListDTO[M]: Полученный список моделей с пагинацией
            Sequence[M]: Полученный список моделей без пагинации
        """

        _log.debug("Get all model %s", self.model.__name__)

        desc_int = desc

        if query_select is None:
            query_select = select(
                self.model
            )

        if search and search_fields:
            search_conditions = []
            for field in search_fields:
                if hasattr(self.model, field):
                    column = getattr(self.model, field)
                    search_conditions.append(  # type: ignore
                        # type: ignore
                        cast(column, String).ilike(f"%{search}%"))
                else:
                    raise HTTPException(
                        status_code=400, detail=f"Поле {field} для поиска не найдено"
                    )

            if search_conditions:
                query_select = query_select.filter(
                    or_(*search_conditions))  # type: ignore

        if loads:
            for key, val in loads.items():
                if val == "s":
                    if hasattr(self.model, key):
                        query_select = query_select.options(
                            selectinload(getattr(self.model, key))
                        )
                    else:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Поле {key} для загрузки не найдено"
                        )
                elif val == "j":
                    if hasattr(self.model, key):
                        query_select = query_select.options(
                            joinedload(getattr(self.model, key))
                        )
                    else:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Поле {key} для загрузки не найдено"
                        )

        if kwargs:
            query_select = query_select.filter_by(**kwargs)

        if page < 1:
            raise HTTPException(
                status_code=400, detail="Номер страницы должен быть больше 0"
            )

        q_total_record = query_select

        if sort_by:
            if hasattr(self.model, sort_by):
                query_select = query_select.order_by(
                    func_desc(getattr(self.model, sort_by)) if desc_int else asc(
                        getattr(self.model, sort_by))
                )
            else:
                raise HTTPException(
                    status_code=400, detail=f"Поле {sort_by} для сортировки не найдено"
                )

        query_select = query_select.offset((page - 1) * limit)
        if limit != -1:
            query_select = query_select.limit(limit)

        result = await session.execute(query_select)
        content = result.scalars().all()

        if is_pagination:
            q_total_record = q_total_record.with_only_columns(
                func.count(self.model.id))  # type: ignore
            r_total_record = await session.execute(q_total_record)
            total_record = r_total_record.scalar_one_or_none()

            if total_record is None:
                total_record = 0

            if limit == -1:
                pages = 1
            else:
                pages = total_record // limit if total_record % limit == 0 else total_record // limit + 1

            return ListDTO[M](
                page_number=page,
                page_size=limit if limit != -1 else total_record,
                total_pages=pages,
                total_record=total_record,
                content=[item for item in content]
            )
        else:
            return content
