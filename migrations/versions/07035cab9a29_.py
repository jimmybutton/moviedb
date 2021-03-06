"""empty message

Revision ID: 07035cab9a29
Revises: ace3c4c93c8b
Create Date: 2020-08-06 09:51:22.903967

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07035cab9a29'
down_revision = 'ace3c4c93c8b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_column('movie', 'director_id')
    # ### end Alembic commands ###
    with op.batch_alter_table('movie') as batch_op:
        batch_op.drop_column('director_id')


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movie', sa.Column('director_id', sa.INTEGER(), nullable=True))
    # ### end Alembic commands ###
