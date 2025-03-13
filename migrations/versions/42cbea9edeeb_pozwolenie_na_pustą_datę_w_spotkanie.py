"""Pozwolenie na pustą datę w Spotkanie

Revision ID: 42cbea9edeeb
Revises: ee72becf7211
Create Date: 2025-02-07 00:55:24.076782

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42cbea9edeeb'
down_revision = 'ee72becf7211'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('spotkanie', schema=None) as batch_op:
        batch_op.alter_column('data',
               existing_type=sa.DATETIME(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('spotkanie', schema=None) as batch_op:
        batch_op.alter_column('data',
               existing_type=sa.DATETIME(),
               nullable=False)

    # ### end Alembic commands ###
