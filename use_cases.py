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


def create_post(session, title, text, author_id):
    author = _require_author(session, author_id)
    return repositories.create_post(session, title, text, author.id)


def update_post(session, post_id, title, text, author_id):
    post = _require_post(session, post_id)
    author = _require_author(session, author_id)
    return repositories.update_post(session, post, title, text, author.id)


def delete_post(session, post_id):
    post = _require_post(session, post_id)
    repositories.delete_post(session, post)
