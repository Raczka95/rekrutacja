"""Initial migration

Revision ID: 9252f9165f2c
Revises: 879a2953888e
Create Date: 2025-03-13 22:20:30.050962

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9252f9165f2c'
down_revision = '879a2953888e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('uczestnictwo',
    sa.Column('szkolenie_id', sa.Integer(), nullable=False),
    sa.Column('kandydat_id', sa.Integer(), nullable=False),
    sa.Column('decyzja', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['kandydat_id'], ['kandydaci.id'], ),
    sa.ForeignKeyConstraint(['szkolenie_id'], ['szkolenie.id'], ),
    sa.PrimaryKeyConstraint('szkolenie_id', 'kandydat_id')
    )
    with op.batch_alter_table('szkolenie', schema=None) as batch_op:
        batch_op.drop_column('decyzja')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('szkolenie', schema=None) as batch_op:
        batch_op.add_column(sa.Column('decyzja', sa.VARCHAR(length=50), nullable=True))

    op.drop_table('uczestnictwo')
    # ### end Alembic commands ###
