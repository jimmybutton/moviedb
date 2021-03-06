"""director relationship

Revision ID: 3b1663812883
Revises: 52521046886e
Create Date: 2020-08-06 17:57:32.461263

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b1663812883'
down_revision = '52521046886e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.add_column('movie', sa.Column('director_id', sa.Integer(), nullable=True))
    # op.create_foreign_key(None, 'movie', 'people', ['director_id'], ['id'])
    # ### end Alembic commands ###
    # with op.batch_alter_table('post') as batch_op:
    #     batch_op.create_foreign_key(None, 'post', 'event', ['event_id'], ['id'])
    #     batch_op.drop_column('post', 'event')
    with op.batch_alter_table('movie') as batch_op:
        batch_op.create_foreign_key(None, 'movie', 'people', ['director_id'], ['id'])
        batch_op.drop_column('movie', 'people')


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'movie', type_='foreignkey')
    op.drop_column('movie', 'director_id')
    # ### end Alembic commands ###
