"""character table

Revision ID: 14b840151c2f
Revises: 5f1654c61a38
Create Date: 2020-06-16 18:07:44.967078

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14b840151c2f'
down_revision = '5f1654c61a38'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('character',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_timestamp', sa.DateTime(), nullable=True),
    sa.Column('created_id', sa.Integer(), nullable=True),
    sa.Column('modified_timestamp', sa.DateTime(), nullable=True),
    sa.Column('modified_id', sa.Integer(), nullable=True),
    sa.Column('movie_id', sa.Integer(), nullable=True),
    sa.Column('actor_id', sa.Integer(), nullable=True),
    sa.Column('character_name', sa.String(length=128), nullable=True),
    sa.Column('character_url', sa.String(length=128), nullable=True),
    sa.Column('movie_title', sa.String(length=128), nullable=True),
    sa.Column('movie_year', sa.Integer(), nullable=True),
    sa.Column('actor_name', sa.String(length=128), nullable=True),
    sa.ForeignKeyConstraint(['actor_id'], ['people.id'], ),
    sa.ForeignKeyConstraint(['created_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['modified_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['movie_id'], ['movie.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_character_created_timestamp'), 'character', ['created_timestamp'], unique=False)
    op.create_index(op.f('ix_character_modified_timestamp'), 'character', ['modified_timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_character_modified_timestamp'), table_name='character')
    op.drop_index(op.f('ix_character_created_timestamp'), table_name='character')
    op.drop_table('character')
    # ### end Alembic commands ###
