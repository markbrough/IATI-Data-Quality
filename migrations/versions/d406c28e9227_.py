"""Add user tracking fields (last login etc).

Revision ID: d406c28e9227
Revises: 124571109cab
Create Date: 2019-04-19 23:22:18.009544

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd406c28e9227'
down_revision = '124571109cab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tracker_user', sa.Column('current_login_at', sa.DateTime(), nullable=True))
    op.add_column('tracker_user', sa.Column('current_login_ip', sa.String(length=100), nullable=True))
    op.add_column('tracker_user', sa.Column('last_login_at', sa.DateTime(), nullable=True))
    op.add_column('tracker_user', sa.Column('last_login_ip', sa.String(length=100), nullable=True))
    op.add_column('tracker_user', sa.Column('login_count', sa.Integer(), nullable=True))
    op.drop_column('tracker_user', 'confirmed_at')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tracker_user', sa.Column('confirmed_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('tracker_user', 'login_count')
    op.drop_column('tracker_user', 'last_login_ip')
    op.drop_column('tracker_user', 'last_login_at')
    op.drop_column('tracker_user', 'current_login_ip')
    op.drop_column('tracker_user', 'current_login_at')
    # ### end Alembic commands ###