"""Added permissions

Revision ID: 2ee61df618fd
Revises: 45d9f82cee53
Create Date: 2024-01-20 14:34:00.442018

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ee61df618fd'
down_revision: Union[str, None] = '45d9f82cee53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('permissions',
                    sa.Column('name', sa.String(length=255), nullable=False),
                    sa.Column('id', sa.UUID(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('modified_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name')
                    )
    op.create_table('role_permissions',
                    sa.Column('role_id', sa.UUID(), nullable=False),
                    sa.Column('permission_id', sa.UUID(), nullable=False),
                    sa.Column('id', sa.UUID(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('modified_at', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('role_permissions')
    op.drop_table('permissions')
    # ### end Alembic commands ###
