"""delete column release_date_uk 2

Revision ID: 15253f648026
Revises: 652d337b5616
Create Date: 2020-08-06 17:39:25.847116

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '15253f648026'
down_revision = '652d337b5616'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_column('movie', 'release_date_uk')
    # ### end Alembic commands ###
    with op.batch_alter_table('movie') as batch_op:
        batch_op.drop_column('release_date_uk')


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movie', sa.Column('release_date_uk', sa.DATE(), nullable=True))
    # ### end Alembic commands ###
