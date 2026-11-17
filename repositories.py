from psycopg.errors import UniqueViolation
from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

from models import Category, Comment, Like, Location, Post, User


class DuplicateUsernameError(Exception):
    pass


def create_user(session, username):
    user = User(username=username)
    session.add(user)

    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        if (
            isinstance(exc.orig, UniqueViolation)
            and exc.orig.diag.constraint_name == "users_username_key"
        ):
            raise DuplicateUsernameError from exc
        raise

    session.refresh(user)
    return user


def get_posts(session):
    return session.scalars(select(Post)).all()


def get_post(session, post_id):
    return session.get(Post, post_id)


def get_users(session, user_id):
    return session.get(User, user_id)


def create_post(session, title, text, author_id, image):
    post = Post(
        title=title,
        text=text,
        author_id=author_id,
        image=image,
    )
    session.add(post)
    session.commit()
    return post


def update_post(session, post, title, text, author_id):
    post.title = title
    post.text = text
    post.author_id = author_id
    session.commit()
    session.refresh(post)
    return post


def delete_post(session, post):
    session.delete(post)
    session.commit()


def get_comments(session, post_id):
    query = (
        select(Comment)
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at)
    )
    return session.scalars(query).all()


def create_comment(session, post_id, text, author_id):
    comment = Comment(post_id=post_id, text=text, author_id=author_id)
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


def get_categories(session):
    return session.scalars(select(Category)).all()


def create_category(session, title, description, slug):
    category = Category(title=title, description=description, slug=slug)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def get_locations(session):
    return session.scalars(select(Location)).all()


def create_location(session, name):
    location = Location(name=name)
    session.add(location)
    session.commit()
    session.refresh(location)
    return location


def create_like(session, post_id, user_id):
    query = (
        insert(Like)
        .values(post_id=post_id, user_id=user_id)
        .on_conflict_do_nothing(index_elements=[Like.post_id, Like.user_id])
        .returning(Like.user_id)
    )
    created = session.scalar(query) is not None
    session.commit()
    return created


def count_likes(session, post_id):
    query = select(func.count()).select_from(Like).where(
        Like.post_id == post_id
    )
    return session.scalar(query)


def delete_like(session, post_id, user_id):
    query = (
        delete(Like)
        .where(Like.post_id == post_id, Like.user_id == user_id)
        .returning(Like.user_id)
    )
    deleted = session.scalar(query) is not None
    session.commit()
    return deleted
