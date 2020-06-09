"""empty message

Revision ID: 3998053e46a0
Revises: 16f3806031c1
Create Date: 2020-06-08 19:30:56.401099

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3998053e46a0'
down_revision = '16f3806031c1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('city', sa.String(length=120), nullable=False))
    op.add_column('artist', sa.Column('facebook_link', sa.String(length=120), nullable=False))
    op.add_column('artist', sa.Column('genres', sa.ARRAY(sa.String()), nullable=False))
    op.add_column('artist', sa.Column('image_link', sa.String(length=500), nullable=False))
    op.add_column('artist', sa.Column('name', sa.String(), nullable=False))
    op.add_column('artist', sa.Column('phone', sa.String(length=120), nullable=False))
    op.add_column('artist', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('artist', sa.Column('seeking_venues', sa.Boolean(), nullable=False))
    op.add_column('artist', sa.Column('state', sa.String(length=120), nullable=False))
    op.add_column('artist', sa.Column('website', sa.String(length=120), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artist', 'website')
    op.drop_column('artist', 'state')
    op.drop_column('artist', 'seeking_venues')
    op.drop_column('artist', 'seeking_description')
    op.drop_column('artist', 'phone')
    op.drop_column('artist', 'name')
    op.drop_column('artist', 'image_link')
    op.drop_column('artist', 'genres')
    op.drop_column('artist', 'facebook_link')
    op.drop_column('artist', 'city')
    # ### end Alembic commands ###
