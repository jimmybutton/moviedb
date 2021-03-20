"""director relationship

Revision ID: 6b145579bb8b
Revises: 3b1663812883
Create Date: 2020-08-07 15:40:30.269846

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b145579bb8b'
down_revision = '3b1663812883'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.create_foreign_key(None, 'movie', 'people', ['director_id'], ['id'])
    # ### end Alembic commands ###
    with op.batch_alter_table('movie') as batch_op:
        batch_op.create_foreign_key(None, 'movie', 'people', ['director_id'], ['id'])
        # batch_op.drop_column('movie', 'people')


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'movie', type_='foreignkey')
    # ### end Alembic commands ###