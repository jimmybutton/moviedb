"""remove movie description and stars

Revision ID: 3dcbe19a2e8d
Revises: 6ffd623b5c7b
Create Date: 2020-04-28 21:25:09.835456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3dcbe19a2e8d'
down_revision = '6ffd623b5c7b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('movie') as batch_op:
        batch_op.drop_column('stars')
        batch_op.drop_column('description')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movie', sa.Column('description', sa.VARCHAR(length=200), nullable=True))
    op.add_column('movie', sa.Column('stars', sa.FLOAT(), nullable=True))
    # ### end Alembic commands ###