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


def create_post(session, title, text, author_id, photo_file):
    author = _require_author(session, author_id)
    filename = photos.save_photo(photo_file)

    try:
        return repositories.create_post(
            session, title, text, author.id, filename
        )
    except SQLAlchemyError:
        session.rollback()
        (photos.UPLOAD_DIR / filename).unlink(missing_ok=True)
        raise


def update_post(session, post_id, title, text, author_id):
    post = _require_post(session, post_id)
    author = _require_author(session, author_id)
    return repositories.update_post(session, post, title, text, author.id)


def delete_post(session, post_id):
    post = _require_post(session, post_id)
    repositories.delete_post(session, post)


def get_comments(session, post_id):
    post = _require_post(session, post_id)
    return repositories.get_comments(session, post.id)


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
