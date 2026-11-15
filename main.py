import asyncio

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

import repositories
from database import engine

app = FastAPI(root_path="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/posts/")
def get_posts():
    with Session(engine) as session:
        return repositories.get_posts(session)


class UserData(BaseModel):
    username: str


@app.post("/users/", status_code=201)
def create_user(data: UserData):
    with Session(engine) as session:
        user = repositories.create_user(session, data.username)
        return {"id": user.id, "username": user.username}


class PostData(BaseModel):
    title: str
    text: str
    author_id: int


@app.post("/posts/", status_code=201)
def create_post(data: PostData):
    with Session(engine) as session:
        author = repositories.get_users(session, data.author_id)

        if author is None:
            raise HTTPException(
                status_code=404,
                detail="Автор не найден",
            )
        post = repositories.create_post(
            session, data.title, data.text, author.id
        )

        return {
            "id": post.id,
            "title": post.title,
            "text": post.text,
            "author_id": post.author_id,
        }


@app.put("/posts/{post_id}/")
def update_post(post_id: int, data: PostData):
    with Session(engine) as session:
        post = repositories.get_post(session, post_id)
        if post is None:
            raise HTTPException(
                status_code=404,
                detail="Пост не найден",
            )

        author = repositories.get_users(session, data.author_id)
        if author is None:
            raise HTTPException(
                status_code=404,
                detail="Автор не найден"
            )

        post = repositories.update_post(
            session, post, data.title, data.text, author.id
        )
        return {
            "id": post.id,
            "title": post.title,
            "text": post.text,
            "author_id": post.author_id,
        }


@app.delete("/posts/{post_id}/")
def delete_post(post_id: int):
    with Session(engine) as session:
        post = repositories.get_post(session, post_id)
        if post is None:
            raise HTTPException(
                status_code=404,
                detail="Пост не найден",
            )
        repositories.delete_post(session, post)
        return {"message": "Пост удалён"}


async def run() -> None:
    config = uvicorn.Config(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
    server = uvicorn.Server(config=config)
    tasks = (
        asyncio.create_task(server.serve()),
    )

    await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED,
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
