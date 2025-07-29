from enum import Enum
import logging
from typing import Any, AsyncGenerator, Literal, Optional, Sequence, Union
from fastapi import APIRouter, HTTPException, params
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession


_log = logging.getLogger(__name__)


class BasicApi:
    def __init__(
        self,

        router: APIRouter,

        session_factory: async_sessionmaker[AsyncSession],

        search_fields: Optional[list[str]] = None,

        return_get_all: Literal["pagination", "list"] = "pagination",

        prefix: Optional[str] = None,

        tags: Optional[list[Union[str, Enum]]] = None,

        dependencies: Optional[Sequence[params.Depends]] = None,

    ) -> None:

        self.router = router
        self.__session_factory = session_factory
        self.search_fields = search_fields
        self.return_get_all: Literal["pagination", "list"] = return_get_all
        self.prefix = prefix
        self.tags = tags
        self.dependencies = dependencies

    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.__session_factory() as session:
            try:
                yield session
                await session.commit()
            except exc.IntegrityError as e:
                await session.rollback()
                _log.debug(e)
                if "UniqueViolationError" in str(e):
                    _log.debug(e.orig)
                    raise HTTPException(
                        status_code=400,
                        detail=f"Объект с таким первичным ключом уже существует"
                    )
                else:
                    raise HTTPException(
                        status_code=500,
                        detail="Ошибка IntegrityError"
                    )
            except exc.SQLAlchemyError as error:
                await session.rollback()
                _log.error(error)
                raise HTTPException(
                    status_code=500, detail="Ошибка SQLAlchemyError")

            finally:
                await session.close()

    def model_to_dict(self, model: Any) -> dict[str, Any]:
        data = {column.name: getattr(model, column.name)
                for column in model.__table__.columns}

        # Добавляем связанные объекты (если есть)
        for rel in model.__mapper__.relationships:
            related_obj = getattr(model, rel.key)
            if related_obj is not None:
                if rel.uselist:  # Если это список (например, posts)
                    data[rel.key] = [self.model_to_dict(item)
                                     for item in related_obj]
                else:  # Если одиночный объект
                    data[rel.key] = self.model_to_dict(related_obj)
        return data
