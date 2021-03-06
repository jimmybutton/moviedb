"""movie release_country field

Revision ID: 761c4d4fc797
Revises: e9596ed3a618
Create Date: 2020-08-06 09:42:43.066984

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '761c4d4fc797'
down_revision = 'e9596ed3a618'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movie', sa.Column('release_country', sa.String(length=5), nullable=True))
    op.create_foreign_key(None, 'movie', 'people', ['director_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'movie', type_='foreignkey')
    op.drop_column('movie', 'release_country')
    # ### end Alembic commands ###
