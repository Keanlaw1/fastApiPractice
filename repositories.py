from sqlalchemy import select

from models import Category, Comment, Location, Post, User


def create_user(session, username):
    user = User(username=username)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_posts(session):
    return session.scalars(select(Post)).all()


def get_post(session, post_id):
    return session.get(Post, post_id)


def get_users(session, user_id):
    return session.get(User, user_id)


def create_post(session, title, text, author_id):
    post = Post(title=title, text=text, author_id=author_id)
    session.add(post)
    session.commit()
    session.refresh(post)
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
