from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    is_published: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
    )


class Category(BaseModel):
    __tablename__ = "categories"

    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text)
    slug: Mapped[str] = mapped_column(String(50), unique=True)

    def __str__(self):
        return self.title


class Location(BaseModel):
    __tablename__ = "locations"

    name: Mapped[str] = mapped_column(String(256))

    def __str__(self):
        return self.name


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(150), unique=True)
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        default="",
        server_default="",
    )
    email: Mapped[str] = mapped_column(String(254), default="")
    first_name: Mapped[str] = mapped_column(String(150), default="")
    last_name: Mapped[str] = mapped_column(String(150), default="")

    def __str__(self):
        return self.username


class Post(BaseModel):
    __tablename__ = "posts"

    title: Mapped[str] = mapped_column(String(256))
    text: Mapped[str] = mapped_column(Text)

    pub_date: Mapped[datetime | None] = mapped_column(
      default=lambda: datetime.now(timezone.utc),
      nullable=True,
    )

    author_id: Mapped[int] = mapped_column(
      ForeignKey("users.id", ondelete="CASCADE"),
    )
    category_id: Mapped[int | None] = mapped_column(
      ForeignKey("categories.id", ondelete="SET NULL"),
      nullable=True,
    )
    location_id: Mapped[int | None] = mapped_column(
      ForeignKey("locations.id", ondelete="SET NULL"),
      nullable=True,
    )
    category: Mapped[Category | None] = relationship(lazy="joined")
    location: Mapped[Location | None] = relationship(lazy="joined")

    def __str__(self):
        return self.title


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)

    post_id: Mapped[int] = mapped_column(
      ForeignKey("posts.id", ondelete="CASCADE"),
    )
    author_id: Mapped[int] = mapped_column(
      ForeignKey("users.id", ondelete="CASCADE"),
    )

    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
      default=lambda: datetime.now(timezone.utc),
    )

    def __str__(self):
        return self.text[:30]


class Like(Base):
    __tablename__ = "likes"

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )


class PostImage(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(100))
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        unique=True,
    )
