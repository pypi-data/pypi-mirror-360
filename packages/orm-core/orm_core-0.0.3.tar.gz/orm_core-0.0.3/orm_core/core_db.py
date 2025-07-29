from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa

from .base import Base


class ClientDB:
    """
    Базовый клиент для работы с БД

    Args:
        async_url (str): Асинхронная строка подключения

    Attributes:
        session_factory (async_sessionmaker): Фабрика сессий

    Methods:
        init_db(): Инициализация БД
        drop_tables(): Удаление всех таблиц

    Example:

        from orm_core import ClientDB

        class YourClientDB(ClientDB):
            def __init__(self, async_url: str):
                super().__init__(async_url)

        db_client = YourClientDB(
            "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
        )
    """

    def __init__(self, async_url: str):
        """Базовый клиент для работы с БД

        Args:
            async_url (str): Асинхронная строка подключения
        """
        self.engine = create_async_engine(
            url=async_url
        )

        self.session_factory = async_sessionmaker(self.engine)

    async def init_db(self):
        """
        Инициализация БД
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(
                lambda sync_conn: Base.metadata.create_all(
                    sync_conn, checkfirst=True)
            )

    async def drop_tables(self):
        """
        Удаление всех таблиц
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
