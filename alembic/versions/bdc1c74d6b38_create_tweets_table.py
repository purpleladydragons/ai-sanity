"""create tweets table

Revision ID: bdc1c74d6b38
Revises: 
Create Date: 2023-04-19 14:17:41.111867

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'bdc1c74d6b38'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'tweets',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('tweet_id', sa.String, nullable=False),
        sa.Column('username', sa.String, nullable=False),
        sa.Column('display_name', sa.String, nullable=False),
        sa.Column('content', sa.String, nullable=False),
        sa.Column('num_likes', sa.Integer, nullable=False),
        sa.Column('tweet_time', sa.TIMESTAMP, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('now')),
    )


def downgrade():
    op.drop_table('tweets')
