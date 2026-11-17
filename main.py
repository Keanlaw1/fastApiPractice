import asyncio

import uvicorn
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

import repositories
import use_cases
from database import engine
from schemas import PostData, UserData

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


@app.post("/users/", status_code=201)
def create_user(data: UserData):
    with Session(engine) as session:
        try:
            user = use_cases.register_user(session, data.username)
        except use_cases.UsernameTakenError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

        return {"id": user.id, "username": user.username}


@app.post("/posts/", status_code=201)
def create_post(data: PostData):
    with Session(engine) as session:
        try:
            post = use_cases.create_post(
                session, data.title, data.text, data.author_id
            )
        except use_cases.NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {
            "id": post.id,
            "title": post.title,
            "text": post.text,
            "author_id": post.author_id,
        }


@app.put("/posts/{post_id}/")
def update_post(post_id: int, data: PostData):
    with Session(engine) as session:
        try:
            post = use_cases.update_post(
                session, post_id, data.title, data.text, data.author_id
            )
        except use_cases.NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {
            "id": post.id,
            "title": post.title,
            "text": post.text,
            "author_id": post.author_id,
        }


@app.delete("/posts/{post_id}/")
def delete_post(post_id: int):
    with Session(engine) as session:
        try:
            use_cases.delete_post(session, post_id)
        except use_cases.NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
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
