"""empty message

Revision ID: b2955ad9e338
Revises: 9efd67749c8b
Create Date: 2020-04-29 21:40:32.780743

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2955ad9e338'
down_revision = '9efd67749c8b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movie', sa.Column('runtime', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('movie', 'runtime')
    # ### end Alembic commands ###
