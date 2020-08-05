"""score field for People

Revision ID: affd804a37d8
Revises: 2f2f0229ae34
Create Date: 2020-08-05 09:45:17.130432

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'affd804a37d8'
down_revision = '2f2f0229ae34'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('people', sa.Column('score', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('people', 'score')
    # ### end Alembic commands ###
