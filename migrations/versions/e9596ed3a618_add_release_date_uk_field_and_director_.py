"""add release_date_uk field and director_id to movie model

Revision ID: e9596ed3a618
Revises: affd804a37d8
Create Date: 2020-08-05 17:34:58.197456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9596ed3a618'
down_revision = 'affd804a37d8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movie', sa.Column('director_id', sa.Integer(), nullable=True))
    op.add_column('movie', sa.Column('release_date_uk', sa.Date(), nullable=True))
    op.create_foreign_key(None, 'movie', 'people', ['director_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'movie', type_='foreignkey')
    op.drop_column('movie', 'release_date_uk')
    op.drop_column('movie', 'director_id')
    # ### end Alembic commands ###
