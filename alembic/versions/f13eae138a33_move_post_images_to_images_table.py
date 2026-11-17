"""Move post images to images table

Revision ID: f13eae138a33
Revises: f93edd78503f
Create Date: 2026-11-18 01:00:42.939175

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f13eae138a33'
down_revision: Union[str, Sequence[str], None] = 'f93edd78503f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO images (filename, post_id)
        SELECT image, id
        FROM posts
        WHERE image IS NOT NULL AND image <> ''
        ON CONFLICT (post_id) DO NOTHING
    """)
    op.drop_column("posts", "image")


def downgrade() -> None:
    op.add_column(
        "posts",
        sa.Column("image", sa.String(length=100), nullable=True),
    )
    op.execute("""
        UPDATE posts
        SET image = images.filename
        FROM images
        WHERE images.post_id = posts.id
    """)
