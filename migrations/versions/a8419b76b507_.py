"""empty message

Revision ID: a8419b76b507
Revises: 3998053e46a0
Create Date: 2020-06-08 19:53:00.375820

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a8419b76b507'
down_revision = '3998053e46a0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('genres', sa.ARRAY(sa.String()), nullable=False))
    op.add_column('venue', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('venue', sa.Column('website', sa.String(length=120), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'website')
    op.drop_column('venue', 'seeking_description')
    op.drop_column('venue', 'genres')
    # ### end Alembic commands ###
