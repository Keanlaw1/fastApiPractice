import asyncio

import uvicorn
from fastapi import (Depends, FastAPI, File, Form, HTTPException, Query,
                     Request, UploadFile)
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

import photos
import repositories
import use_cases
from database import engine
from dependencies import get_current_user
from schemas import (CategoryData, CommentData, LocationData, PostData,
                     TokenResponse, UserData)
from security import create_access_token

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


def post_to_dict(post):
    category_name = None
    if post.category is not None:
        category_name = post.category.title

    location_name = None
    if post.location is not None:
        location_name = post.location.name

    return {
        "id": post.id,
        "title": post.title,
        "text": post.text,
        "author_id": post.author_id,
        "category_id": post.category_id,
        "category_name": category_name,
        "location_id": post.location_id,
        "location_name": location_name,
        "is_published": post.is_published,
        "pub_date": post.pub_date,
        "created_at": post.created_at,
    }


@app.get("/posts/")
def get_posts(
    limit: int = Query(default=10, ge=1, le=100),
    page: int = Query(default=1, ge=1),
):
    with Session(engine) as session:
        posts = repositories.get_posts(session, limit, page)
        return {
            "page": page,
            "limit": limit,
            "posts": [post_to_dict(post) for post in posts],
        }


@app.get("/posts/{post_id}/")
def get_post(post_id: int, request: Request):
    with Session(engine) as session:
        try:
            post = use_cases.get_post(session, post_id)
        except use_cases.NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        result = post_to_dict(post)
        result["image_id"] = None
        result["image_url"] = None

        image = repositories.get_post_image(session, post.id)
        if image is not None:
            result["image_id"] = image.id
            result["image_url"] = str(
                request.url_for("get_image", image_id=image.id)
            )

        return result


@app.post("/users/", status_code=201)
def create_user(data: UserData):
    with Session(engine) as session:
        try:
            user = use_cases.register_user(
                session, data.username, data.password
            )
        except use_cases.UsernameTakenError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

        return {"id": user.id, "username": user.username}


@app.post("/posts/", status_code=201)
def create_post(
    request: Request,
    title: str = Form(),
    text: str = Form(),
    image: UploadFile | None = File(default=None),
    category_id: int | None = Form(default=None, examples=[""]),
    location_id: int | None = Form(default=None, examples=[""]),
    current_user=Depends(get_current_user),
):
    try:
        data = PostData(
            title=title,
            text=text,
            category_id=category_id,
            location_id=location_id,
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=exc.errors(include_context=False),
        ) from exc
    photo_file = None
    if image is not None and image.filename:
        photo_file = image.file

    with Session(engine) as session:
        try:
            post = use_cases.create_post(
                session, data.title, data.text, current_user.id, photo_file,
                category_id=data.category_id,
                location_id=data.location_id,
            )
        except use_cases.NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except photos.InvalidPhotoError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        image = repositories.get_post_image(session, post.id)
        image_id = None
        image_url = None

        if image is not None:
            image_id = image.id
            image_url = str(request.url_for("get_image", image_id=image.id))

        result = post_to_dict(post)
        result["image_id"] = image_id
        result["image_url"] = image_url
        return result


@app.put("/posts/{post_id}/")
def update_post(
    post_id: int,
    data: PostData,
    current_user=Depends(get_current_user),
):
    with Session(engine) as session:
        try:
            post = use_cases.update_post(
                session, post_id, data.title, data.text, current_user.id,
                category_id=data.category_id,
                location_id=data.location_id,
            )
        except use_cases.NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except use_cases.PermissionDeniedError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc

        return post_to_dict(post)


@app.delete("/posts/{post_id}/")
def delete_post(
    post_id: int,
    current_user=Depends(get_current_user),
):
    with Session(engine) as session:
        try:
            use_cases.delete_post(session, post_id, current_user.id)
        except use_cases.NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except use_cases.PermissionDeniedError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc

        return {"message": "Пост удалён"}


@app.get("/posts/{post_id}/comments/")
def get_comments(
    post_id: int,
    limit: int = Query(default=10, ge=1, le=100),
    page: int = Query(default=1, ge=1),
):
    with Session(engine) as session:
        try:
            comments = use_cases.get_comments(
                session, post_id, limit, page
            )
        except use_cases.NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        return {
            "page": page,
            "limit": limit,
            "comments": comments,
        }


@app.post("/posts/{post_id}/comments/", status_code=201)
def create_comment(
    post_id: int,
    data: CommentData,
    current_user=Depends(get_current_user),
):
    with Session(engine) as session:
        try:
            comment = use_cases.create_comment(
                session, post_id, data.text, current_user.id
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
def like_post(post_id: int, current_user=Depends(get_current_user)):
    with Session(engine) as session:
        try:
            use_cases.like_post(session, post_id, current_user.id)
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


@app.delete("/posts/{post_id}/likes/")
def unlike_post(post_id: int, current_user=Depends(get_current_user)):
    with Session(engine) as session:
        try:
            use_cases.unlike_post(session, post_id, current_user.id)
        except use_cases.NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        return {"message": "Лайк снят"}


@app.post(
    "/locations/",
    status_code=201,
    dependencies=[Depends(get_current_user)],
)
def create_location(data: LocationData):
    with Session(engine) as session:
        location = repositories.create_location(session, data.name)
        return {"id": location.id, "name": location.name}


@app.get("/locations/")
def get_locations():
    with Session(engine) as session:
        return repositories.get_locations(session)


@app.get("/locations/{location_id}/")
def get_location(location_id: int):
    with Session(engine) as session:
        try:
            return use_cases.get_location(session, location_id)
        except use_cases.NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post(
    "/categories/",
    status_code=201,
    dependencies=[Depends(get_current_user)],
)
def create_category(data: CategoryData):
    with Session(engine) as session:
        try:
            category = use_cases.create_category(
                session, data.title, data.description, data.slug
            )
        except use_cases.CategorySlugTakenError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

        return {
            "id": category.id,
            "title": category.title,
            "description": category.description,
            "slug": category.slug,
        }


@app.get("/categories/")
def get_categories():
    with Session(engine) as session:
        return repositories.get_categories(session)


@app.get("/categories/{category_id}/")
def get_category(category_id: int):
    with Session(engine) as session:
        try:
            return use_cases.get_category(session, category_id)
        except use_cases.NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/images/{image_id}/", response_class=FileResponse)
def get_image(image_id: int):
    with Session(engine) as session:
        try:
            path = use_cases.get_image_path(session, image_id)
        except use_cases.NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        return FileResponse(path)


@app.post("/token/", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends()):
    with Session(engine) as session:
        try:
            user = use_cases.authenticate_user(
                session, form.username, form.password
            )
        except use_cases.InvalidCredentialsError as exc:
            raise HTTPException(
                status_code=401,
                detail=str(exc),
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        return {
            "access_token": create_access_token(user.id),
            "token_type": "bearer",
        }


@app.get("/users/me/")
def get_my_profile(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
    }


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
