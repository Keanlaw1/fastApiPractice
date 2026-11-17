import asyncio

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

import photos
import repositories
import use_cases
from database import engine
from schemas import CommentData, LikeData, PostData, UserData

app = FastAPI(root_path="/api/v1")

photos.UPLOAD_DIR.mkdir(exist_ok=True)
app.mount(
    "/uploads",
    StaticFiles(directory=photos.UPLOAD_DIR),
    name="uploads",
)

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
def create_post(
    request: Request,
    title: str = Form(),
    text: str = Form(),
    author_id: int = Form(),
    image: UploadFile = File(),
):
    try:
        data = PostData(title=title, text=text, author_id=author_id)
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=exc.errors(include_context=False),
        ) from exc

    with Session(engine) as session:
        try:
            post = use_cases.create_post(
                session, data.title, data.text, data.author_id, image.file
            )
        except use_cases.NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except photos.InvalidPhotoError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        return {
            "id": post.id,
            "title": post.title,
            "text": post.text,
            "author_id": post.author_id,
            "image_url": str(request.url_for("uploads", path=post.image)),
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


@app.get("/posts/{post_id}/comments/")
def get_comments(post_id: int):
    with Session(engine) as session:
        try:
            return use_cases.get_comments(session, post_id)
        except use_cases.NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/posts/{post_id}/comments/", status_code=201)
def create_comment(post_id: int, data: CommentData):
    with Session(engine) as session:
        try:
            comment = use_cases.create_comment(
                session, post_id, data.text, data.author_id
            )
        except use_cases.NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        return {
            "id": comment.id,
            "post_id": comment.post_id,
            "author_id": comment.author_id,
            "text": comment.text,
            "created_at": comment.created_at,
        }


@app.post("/posts/{post_id}/likes/", status_code=201)
def like_post(post_id: int, data: LikeData):
    with Session(engine) as session:
        try:
            use_cases.like_post(session, post_id, data.user_id)
        except use_cases.NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except use_cases.LikeAlreadyExistsError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

        return {"message": "Лайк поставлен"}


@app.get("/posts/{post_id}/likes/")
def count_likes(post_id: int):
    with Session(engine) as session:
        try:
            return {"count": use_cases.count_likes(session, post_id)}
        except use_cases.NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.delete("/posts/{post_id}/likes/{user_id}/")
def unlike_post(post_id: int, user_id: int):
    with Session(engine) as session:
        try:
            use_cases.unlike_post(session, post_id, user_id)
        except use_cases.NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        return {"message": "Лайк снят"}


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
