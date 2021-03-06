"""create column release_date as date 2

Revision ID: 652d337b5616
Revises: a61600654e31
Create Date: 2020-08-06 17:37:55.067508

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '652d337b5616'
down_revision = 'a61600654e31'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movie', sa.Column('release_date', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('movie', 'release_date')
    # ### end Alembic commands ###
