"""recreate column release_date as date

Revision ID: 9392d2b54572
Revises: 7dde762b575a
Create Date: 2020-08-06 17:24:37.374102

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9392d2b54572'
down_revision = '7dde762b575a'
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
