"""username set not null

Revision ID: b2b325eefc4d
Revises: 1c47bd449d83
Create Date: 2023-04-26 09:11:20.015623

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b2b325eefc4d'
down_revision = '1c47bd449d83'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'username',
                    existing_type=sa.VARCHAR(length=50),
                    nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'username',
                    existing_type=sa.VARCHAR(length=50),
                    nullable=True)
    # ### end Alembic commands ###
