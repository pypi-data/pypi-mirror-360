# ORM Manager Factory

[![PyPI Version](https://img.shields.io/pypi/v/orm-manager-factory.svg)](https://pypi.org/project/orm-core/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Универсальная фабрика для создания менеджеров работы с SQLAlchemy ORM, поддерживающая:
- Базовые CRUD-операции
- Автоматическую валидацию через Pydantic схемы
- Генерацию FastAPI роутеров

## 📦 Установка

```bash
pip install orm_core
```

## 🚀 Возможности

### 1. Базовый ORM менеджер
Работа с моделями SQLAlchemy без дополнительных схем.

### 2. Менеджер с Pydantic схемами
Автоматическая валидация входных/выходных данных.

### 3. Менеджер с автогенерацией FastAPI роутеров
Полноценное CRUD API из коробки

## 🔧 Использование

### 1. Базовый ORM менеджер

```python
from orm_manager import ClientDB, create_orm_manager

class YourClientDB(ClientDB):
    def __init__(self, async_url: str):
        super().__init__(async_url)
        self.user = create_orm_manager(User)

db = YourClientDB("postgresql+asyncpg://user:pass@localhost:5432/db")

# Использование
await db.init()

await db.user.add(...)
await db.user.get_by(...)
await db.user.get_by_query(...)
await db.user.get_all(...)
await db.user.delete(...)
```

### 2. С Pydantic схемами

```python
class YourClientDB(ClientDB):
    def __init__(self, async_url: str):
        super().__init__(async_url)
        self.user = create_orm_manager(
            User,
            UserCreateSchema,
            UserUpdateSchema,
            UserOutSchema
        )

# Автоматическая валидация входных/выходных данных в Pydantic схемы
await db.init()

await db.user.add(...)
...
await db.user.delete(...)
```

### 3. С генерацией FastAPI роутеров 

```python
class YourClientDB(ClientDB):
    def __init__(self, async_url: str):
        super().__init__(async_url)

        # Автоматическая генерация Pydantic схем для swagger
        self.group = create_orm_manager(
            Group, 
            session_factory=self.session_factory,
            api=True
        )

        # Можно использовать кастомные схемы
        self.user = create_orm_manager(
            User,
            UserCreateSchema,
            UserUpdateSchema,
            UserOutSchema,
            session_factory=self.session_factory,
            api=True,
            tags=["Users"]
        )
        

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_client.init_db()
    yield

app = FastAPI(
    lifespan=lifespan,
)
app.include_router(db.user.router)
app.include_router(db.group.router)
```

## 📄 Лицензия

MIT License. См. файл [LICENSE](LICENSE).

## 🤝 Вклад
Приветствуются pull requests и issue reports.

## 🧑‍💻 Об авторе

Соловьёв Эрик - [GitHub](https://github.com/ErJokeCode)

