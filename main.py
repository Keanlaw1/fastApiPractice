import asyncio
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

from database import engine
from models import Post, User


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
        posts = session.scalars(select(Post)).all()
        return posts

class UserData(BaseModel):
    username: str

@app.post("/users/", status_code=201)
def create_user(data: UserData):
    with Session(engine) as session:
        user = User(username=data.username)

        session.add(user)
        session.commit()
        session.refresh(user)

        return {"id": user.id, "username": user.username}

class PostData(BaseModel):
    title: str
    text: str
    author_id: int

@app.post("/posts/", status_code=201)
def create_post(data: PostData):
    with Session(engine) as session:
        author = session.get(User, data.author_id)

        if author is None:
            raise HTTPException(
                status_code=404,
                detail="Автор не найден",
            )
        post = Post(
            title=data.title,
            text=data.text,
            author_id=data.author_id,
        )
        session.add(post)
        session.commit()
        session.refresh(post)

        return {
            "id": post.id,
            "title": post.title,
            "text": post.text,
            "author_id": post.author_id,
        }

@app.put("/posts/{post_id}/")
def update_post(post_id: int, data: PostData):
    with Session(engine) as session:
        post = session.get(Post, post_id)

        if post is None:
            raise HTTPException(
                status_code=404,
                detail="Пост не найден",
            )

        if session.get(User, data.author_id) is None:
            raise HTTPException(
                status_code=404,
                detail="Автор не найден",
            )

        post.title = data.title
        post.text = data.text
        post.author_id = data.author_id

        session.commit()
        session.refresh(post)

        return {
            "id": post.id,
            "title": post.title,
            "text": post.text,
            "author_id": post.author_id,
        }

@app.delete("/posts/{post_id}/")
def delete_post(post_id: int):
    with Session(engine) as session:
        post = session.get(Post, post_id)

        if post is None:
            raise HTTPException(
                status_code=404,
                detail="Пост не найден",
            )

        session.delete(post)
        session.commit()

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