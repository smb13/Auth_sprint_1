"""Added constraines

Revision ID: a8bd9fccb18e
Revises: 2ee61df618fd
Create Date: 2024-01-22 11:48:12.801469

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a8bd9fccb18e'
down_revision: Union[str, None] = '2ee61df618fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'role_permissions', ['role_id', 'permission_id'])
    op.create_unique_constraint(None, 'user_roles', ['user_id', 'role_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_roles', type_='unique')
    op.drop_constraint(None, 'role_permissions', type_='unique')
    # ### end Alembic commands ###
