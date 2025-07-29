from enum import Enum
import logging
from typing import Any, Literal, Optional, Sequence, TypeVar, Union, overload
from fastapi import params
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from .api.api_model import ManagerApiModel
from .basic_operations.model import ManagerModel
from .basic_operations.model_with_schemes import ManagerModelSchemes
from .api.api_schemes import ManagerApiModelWithSchemes


_log = logging.getLogger(__name__)


M = TypeVar('M', bound=Any)
A = TypeVar('A', bound=BaseModel)
E = TypeVar('E', bound=BaseModel)
O = TypeVar('O', bound=BaseModel)


@overload
def create_orm_manager(
    model: type[M]
) -> ManagerModel[M]:
    """Фабрика для создания менеджера для работы только с моделями

    Args:
        model (type[M]): Модель для работы

    Returns:
        ManagerModel[M]: Менеджер для работы с моделями


    Example:

    from orm_core import ClientDB
    from orm_core import create_factory_orm

    class YourClientDB(ClientDB):
        def __init__(self, async_url: str):
            super().__init__(async_url)

            self.user = create_factory_orm(User)

    db_client = YourClientDB(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    )

    await db_client.user.add(...)
    await db_client.user.edit(...)
    await db_client.user.get_all(...)
    await db_client.user.get_by(...)
    await db_client.user.get_by_query(...)
    await db_client.user.delete(...)
    """
    ...


@overload
def create_orm_manager(
    model: type[M],
    add_scheme: type[A],
    edit_scheme: type[E],
    out_scheme: type[O],
) -> ManagerModelSchemes[M, A, E, O]:
    """Фабрика для создания менеджера для работы с моделями и преобразование в pydantic-схемы

    Args:
        model (type[M]): Модель для работы
        add_scheme (type[A]): Pydantic-схема для добавления
        edit_scheme (type[E]): Pydantic-схема для редактирования
        out_scheme (type[O]): Pydantic-схема для вывода

    Returns:
        ManagerModelSchemes[M, A, E, O]: Менеджер для работы с моделями и преобразование в pydantic-схемы


    Example:

        from orm_core import ClientDB
        from orm_core import create_factory_orm

        class YourClientDB(ClientDB):
            def __init__(self, async_url: str):
                super().__init__(async_url)

                self.user = create_factory_orm(
                    User
                    InputScheme,
                    EditScheme,
                    OutputScheme
                )

        db_client = YourClientDB(
            "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
        )

        # Использование
        await db_client.user.add(...)
        await db_client.user.edit(...)
        await db_client.user.get_all(...)
        await db_client.user.get_by(...)
        await db_client.user.get_by_query(...)
        await db_client.user.delete(...)
    """
    ...


@overload
def create_orm_manager(

    model: type[M],

    add_scheme: type[A],

    edit_scheme: type[E],

    out_scheme: type[O],

    session_factory: async_sessionmaker[AsyncSession],

    api: Literal[True],

    search_fields: Optional[list[str]] = None,

    return_get_all: Literal["pagination", "list"] = "pagination",

    prefix: Optional[str] = None,

    tags: Optional[list[Union[str, Enum]]] = None,

    dependencies: Optional[Sequence[params.Depends]] = None,

) -> ManagerApiModelWithSchemes[M, A, E, O]:
    """Фабрика для создания менеджера для работы с моделями, схемами и автогенерация CRUD API для работы с таблицами  

    Args:
        model (type[M]): Модель для работы
        add_scheme (type[A]): Pydantic-схема для добавления
        edit_scheme (type[E]): Pydantic-схема для редактирования
        out_scheme (type[O]): Pydantic-схема для вывода
        session_factory (async_sessionmaker[AsyncSession]): Фабрика сессий для работы с БД
        api (Literal[True]): Флаг для автогенерации API
        search_fields (Optional[list[str]], optional): Поля по которым будет проводиться поиск при получении списка. По умолчанию None.
        return_get_all (Literal[&quot;pagination&quot;, &quot;list&quot;], optional): При получении списка будет получаться с пагинацией или список. По умолчани. с пагинацией (to "pagination").
        prefix (Optional[str], optional): Кастомный путь для router. По умелчанию создается автоматически по названию модели.
        tags (Optional[list[Union[str, Enum]]], optional): Название router в Swager. По умелчанию название модели.
        dependencies (Optional[Sequence[params.Depends]], optional): Зависимости. По умелчанию их нет.

    Returns:
        ManagerModelWithApi[M, A, E, O]: Менеджер для работы с моделями, схемами и генериацией CRUD API


    Example:

        from orm_core import ClientDB
        from orm_core import create_factory_orm

        class YourClientDB(ClientDB):
            def __init__(self, async_url: str):
                super().__init__(async_url)

                self.user = create_factory_orm(
                    User
                    InputScheme,
                    EditScheme,
                    OutputScheme, 
                    api=True, 
                    session_factory=self.session_factory
                )

        db_client = YourClientDB(
            "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
        )

        # Использование ORM
        await db_client.user.add(...)
        await db_client.user.edit(...)
        await db_client.user.get_all(...)
        await db_client.user.get_by(...)
        await db_client.user.get_by_query(...)
        await db_client.user.delete(...)

        # Создание API
        app = FastAPI()
        app.include_router(db_client.user.router) 
    """
    ...


@overload
def create_orm_manager(
    model: type[M],
    *,
    session_factory: async_sessionmaker[AsyncSession],
    api: Literal[True],
    search_fields: Optional[list[str]] = None,
    return_get_all: Literal["pagination", "list"] = "pagination",
    prefix: Optional[str] = None,
    tags: Optional[list[Union[str, Enum]]] = None,
    dependencies: Optional[Sequence[params.Depends]] = None,
) -> ManagerApiModel[M]:
    """Фабрика для создания менеджера для работы с моделями и автогенерация CRUD API для работы с таблицами

    Args:
        model (type[M]): Модель для работы
        session_factory (async_sessionmaker[AsyncSession]): Фабрика сессий для работы с БД
        api (Literal[True]): Флаг для автогенерации API
        search_fields (Optional[list[str]], optional): Поля по которым будет проводиться поиск при получении списка. По умолчанию None.
        return_get_all (Literal[&quot;pagination&quot;, &quot;list&quot;], optional): При получении списка будет получаться с пагинацией или список. По умолчанию с пагинацией (to "pagination").
        prefix (Optional[str], optional): Кастомный путь для router. По умолчанию создается автоматически по названию модели.
        tags (Optional[list[Union[str, Enum]]], optional): Название router в Swagger. По умолчанию название модели.
        dependencies (Optional[Sequence[params.Depends]], optional): Зависимости. По умелчанию их нет.

    Returns:
        ManagerApiModel[M]: Менеджер для работы с моделями и автогенерацией CRUD API


    Example:

        from orm_core import ClientDB
        from orm_core import create_factory_orm

        class YourClientDB(ClientDB):
            def __init__(self, async_url: str):
                super().__init__(async_url)

                self.user = create_factory_orm(
                    User,
                    api=True, 
                    session_factory=self.session_factory
                )

        db_client = YourClientDB(
            "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
        )

        # Использование ORM
        await db_client.user.add(...)
        await db_client.user.edit(...)
        await db_client.user.get_all(...)
        await db_client.user.get_by(...)
        await db_client.user.get_by_query(...)
        await db_client.user.delete(...)

        # Создание API
        app = FastAPI()
        app.include_router(db_client.user.router) 
    """

    ...


def create_orm_manager(

    model: type[M],

    add_scheme: Optional[type[A]] = None,

    edit_scheme: Optional[type[E]] = None,

    out_scheme: Optional[type[O]] = None,

    session_factory: Optional[async_sessionmaker[AsyncSession]] = None,

    api: bool = False,

    search_fields: Optional[list[str]] = None,

    return_get_all: Optional[Literal["pagination", "list"]] = None,

    prefix: Optional[str] = None,

    tags: Optional[list[Union[str, Enum]]] = None,

    dependencies: Optional[Sequence[params.Depends]] = None,

) -> Union[ManagerModel[M], ManagerModelSchemes[M, A, E, O], ManagerApiModelWithSchemes[M, A, E, O], ManagerApiModel[M]]:

    if api:
        if add_scheme is not None and edit_scheme is not None and out_scheme is not None and session_factory is not None:
            if return_get_all is None:
                return_get_all = "pagination"
            return ManagerApiModelWithSchemes(
                model=model,
                add_scheme=add_scheme,
                edit_scheme=edit_scheme,
                out_scheme=out_scheme,
                session_factory=session_factory,
                search_fields=search_fields,
                return_get_all=return_get_all,
                prefix=prefix,
                tags=tags,
                dependencies=dependencies
            )
        elif model is not None and session_factory is not None:
            if return_get_all is None:
                return_get_all = "pagination"
            return ManagerApiModel(
                model=model,
                session_factory=session_factory,
                search_fields=search_fields,
                return_get_all=return_get_all,
                prefix=prefix,
                tags=tags,
                dependencies=dependencies
            )
        else:
            raise TypeError("Not all arguments are provided")

    elif add_scheme is not None and edit_scheme is not None and out_scheme is not None:
        return ManagerModelSchemes(model, add_scheme, edit_scheme, out_scheme)

    elif add_scheme is None and edit_scheme is None and out_scheme is None:
        return ManagerModel(model)

    else:
        raise TypeError("Either all schemes must be provided or none")
