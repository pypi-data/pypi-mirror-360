from sqlalchemy.orm import DeclarativeBase  # noqa


class Base(DeclarativeBase):
    # Базовый класс для всех моделей теблиц

    repr_cols_num = 10
    repr_cols = tuple()  # type: ignore

    def __repr__(self):
        """Relationships не используются в repr(), т.к. могут вести к неожиданным подгрузкам"""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:  # type: ignore
                cols.append(f"{col}={getattr(self, col)}")  # type: ignore

        return f"<{self.__class__.__name__} {', '.join(cols)}>"  # type: ignore

    def model_to_dict(self):
        return vars(self)
