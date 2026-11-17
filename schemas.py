from pydantic import BaseModel, Field, field_validator


class UserData(BaseModel):
    username: str
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, username: str) -> str:
        username = username.strip()
        if not 1 <= len(username) <= 150:
            raise ValueError("Имя должно содержать от 1 до 150 символов")
        return username


class PostData(BaseModel):
    title: str
    text: str
    category_id: int | None = Field(default=None, gt=0)
    location_id: int | None = Field(default=None, gt=0)

    @field_validator("title")
    @classmethod
    def validate_title(cls, title: str) -> str:
        title = title.strip()
        if not 1 <= len(title) <= 256:
            raise ValueError("Заголовок должен содержать от 1 до 256 символов")
        return title

    @field_validator("text")
    @classmethod
    def validate_text(cls, text: str) -> str:
        if not text.strip():
            raise ValueError("Текст поста не должен быть пустым")
        return text


class CommentData(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, text: str) -> str:
        if not text.strip():
            raise ValueError("Комментарий не должен быть пустым")
        return text


class LocationData(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, name: str) -> str:
        name = name.strip()
        if not 1 <= len(name) <= 256:
            raise ValueError("Название должно содержать от 1 до 256 символов")
        return name


class CategoryData(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    description: str = Field(min_length=1)
    slug: str = Field(
        min_length=1,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )

    @field_validator("title", "description", "slug", mode="before")
    @classmethod
    def strip_spaces(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
