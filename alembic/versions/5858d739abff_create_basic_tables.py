"""create basic tables

Revision ID: 5858d739abff
Revises: 
Create Date: 2021-01-09 23:06:58.695212

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5858d739abff'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'recipes',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.Unicode(75), nullable=False),
        sa.Column('description', sa.Unicode(200)), # not currently used
        sa.Column('comments', sa.Unicode(200)),
        sa.Column('url', sa.Unicode(200)),
        sa.Column('tags', sa.Unicode(200)),
    )

def downgrade():
    pass
