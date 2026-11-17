from pydantic import BaseModel, Field, field_validator


class UserData(BaseModel):
    username: str

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
    author_id: int = Field(gt=0)

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
