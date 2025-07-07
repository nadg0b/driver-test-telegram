from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column()
    tg_id: Mapped[int] = mapped_column()
    