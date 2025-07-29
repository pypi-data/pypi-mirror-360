import logging
from typing import Any, Literal, Optional, Sequence, TypeVar, Generic, Union, overload
from pydantic import BaseModel
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from ...base_schemes import ListDTO

from ..model.get_all import BasicModelGetAllOperations


_log = logging.getLogger(__name__)


M = TypeVar('M')
A = TypeVar('A', bound=BaseModel, default=Any)
E = TypeVar('E', bound=BaseModel, default=Any)
O = TypeVar('O', bound=BaseModel, default=Any)


class BasicGetAllSchemeOperations(
        BasicModelGetAllOperations[M],
        Generic[M, A, E, O]
):

    model: type[M]
    input_scheme: type[A]
    edit_scheme: type[E]
    out_scheme: type[O]

    pks: list[str]
    loads: dict[str, str]

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

        is_model: Literal[False] = False,

        **kwargs: Any

    ) -> ListDTO[O]:
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

        is_pagination: Literal[False] = False,

        is_model: Literal[False] = False,

        **kwargs: Any

    ) -> Sequence[M]:
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

        is_model: bool = True,

        **kwargs: Any

    ) -> Union[ListDTO[M], Sequence[M], ListDTO[O], Sequence[O]]:
        """Получение списка обектов по фильтрам, сортировке и пагинацией из базы данных

        Args:
            session (AsyncSession): Сессия
            search (Optional[str], optional): Поиск по полям. По умолчанию None
            search_fields (Optional[list[str]], optional): Поля поиска. По умолчанию None
            loads (Optional[dict[str, str]], optional): Поля для загрузки. По умолчанию None
            sort_by (Optional[str], optional): Поле сортировки. По умолчанию None
            query_select (Optional[Select[Any]], optional): Кастомный селект запрос. По умолчанию None
            desc (int, optional): Порядок сортировки. По умолчанию 0
            page (int, optional): Номер страницы. По умолчанию 1
            limit (int, optional): Количество элементов на странице. По умолчанию -1
            is_pagination (bool, optional): Пагинация. По умолчанию True
            is_model (bool, optional): Возвращение объекта в виде модели или схемы. По умолчанию True
            **kwargs (Any): Дополнительная фильтрация по полям

        Returns:
            Union[ListDTO[M], Sequence[M], ListDTO[O], Sequence[O]]: Список обектов
        """

        if loads is None and not is_model:
            loads = self.loads

        if is_pagination:
            list_data = await super().get_all(
                session=session,
                search=search,
                search_fields=search_fields,
                loads=loads,
                sort_by=sort_by,
                query_select=query_select,
                desc=desc,
                page=page,
                limit=limit,
                is_pagination=True,
                **kwargs
            )

            if is_model:
                return list_data

            schema_content: list[O] = []

            for c in list_data.content:
                schema_content.append(self.out_scheme.model_validate(c))

            schema_list_data = ListDTO(
                page_number=list_data.page_number,
                page_size=list_data.page_size,
                total_pages=list_data.total_pages,
                total_record=list_data.total_record,
                content=schema_content
            )

            return schema_list_data

        seq_data = await super().get_all(
            session=session,
            search=search,
            search_fields=search_fields,
            loads=loads,
            sort_by=sort_by,
            query_select=query_select,
            desc=desc,
            page=page,
            limit=limit,
            is_pagination=False,
            **kwargs
        )

        if is_model:
            return seq_data

        schema_seq: list[O] = []

        for c in seq_data:
            schema_seq.append(self.out_scheme.model_validate(c))

        return schema_seq
