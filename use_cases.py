from sqlalchemy.exc import SQLAlchemyError

import photos
import repositories


class UsernameTakenError(Exception):
    pass


def register_user(session, username):
    try:
        return repositories.create_user(session, username)
    except repositories.DuplicateUsernameError as exc:
        raise UsernameTakenError(
            f"Имя пользователя '{username}' уже занято"
        ) from exc


class NotFoundError(Exception):
    pass


def _require_post(session, post_id):
    post = repositories.get_post(session, post_id)
    if post is None:
        raise NotFoundError("Пост не найден")
    return post


def _require_author(session, author_id):
    author = repositories.get_users(session, author_id)
    if author is None:
        raise NotFoundError("Автор не найден")
    return author


def create_post(
    session, title, text, author_id, photo_file,
    category_id=None, location_id=None,
):
    author = _require_author(session, author_id)

    if category_id is not None:
        get_category(session, category_id)
    if location_id is not None:
        get_location(session, location_id)

    filename = None
    if photo_file is not None:
        filename = photos.save_photo(photo_file)

    try:
        return repositories.create_post(
            session, title, text, author.id, filename,
            category_id=category_id,
            location_id=location_id,
        )
    except SQLAlchemyError:
        session.rollback()
        if filename is not None:
            (photos.UPLOAD_DIR / filename).unlink(missing_ok=True)
        raise


def update_post(
    session, post_id, title, text, author_id,
    category_id=None, location_id=None,
):
    post = _require_post(session, post_id)
    author = _require_author(session, author_id)

    if category_id is not None:
        get_category(session, category_id)
    if location_id is not None:
        get_location(session, location_id)

    return repositories.update_post(
        session, post, title, text, author.id,
        category_id=category_id,
        location_id=location_id,
    )


def delete_post(session, post_id):
    post = _require_post(session, post_id)
    repositories.delete_post(session, post)


def get_comments(session, post_id, limit=10, page=1):
    post = _require_post(session, post_id)
    return repositories.get_comments(session, post.id, limit, page)


def create_comment(session, post_id, text, author_id):
    post = _require_post(session, post_id)
    author = _require_author(session, author_id)
    return repositories.create_comment(
        session, post_id=post.id, text=text, author_id=author.id
    )


class LikeAlreadyExistsError(Exception):
    pass


def like_post(session, post_id, user_id):
    post = _require_post(session, post_id)
    user = _require_author(session, user_id)
    if not repositories.create_like(session, post.id, user.id):
        raise LikeAlreadyExistsError("Пользователь уже лайкнул этот пост")


def count_likes(session, post_id):
    post = _require_post(session, post_id)
    return repositories.count_likes(session, post.id)


def unlike_post(session, post_id, user_id):
    post = _require_post(session, post_id)
    if not repositories.delete_like(session, post.id, user_id):
        raise NotFoundError("Лайк не найден")


def get_post(session, post_id):
    return _require_post(session, post_id)


def get_location(session, location_id):
    location = repositories.get_location(session, location_id)
    if location is None:
        raise NotFoundError("Локация не найдена")
    return location


class CategorySlugTakenError(Exception):
    pass


def create_category(session, title, description, slug):
    try:
        return repositories.create_category(
            session, title, description, slug
        )
    except repositories.DuplicateCategorySlugError as exc:
        raise CategorySlugTakenError(
            f"Категория со slug '{slug}' уже существует"
        ) from exc


def get_category(session, category_id):
    category = repositories.get_category(session, category_id)
    if category is None:
        raise NotFoundError("Категория не найдена")
    return category


def get_image_path(session, image_id):
    image = repositories.get_image(session, image_id)
    if image is None:
        raise NotFoundError("Изображение не найдено")

    path = photos.UPLOAD_DIR / image.filename
    if not path.is_file():
        raise NotFoundError("Файл изображения не найден")

    return path
