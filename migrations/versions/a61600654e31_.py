"""empty message

Revision ID: a61600654e31
Revises: 01ae6765b98d
Create Date: 2020-08-06 17:36:05.366104

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a61600654e31'
down_revision = '01ae6765b98d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_column('movie', 'release_date')
    # ### end Alembic commands ###
    with op.batch_alter_table('movie') as batch_op:
        batch_op.drop_column('release_date')


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movie', sa.Column('release_date', sa.VARCHAR(length=128), nullable=True))
    # ### end Alembic commands ###
