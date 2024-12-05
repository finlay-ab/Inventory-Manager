"""Addeded loan status and conditions to items

Revision ID: 2dbcce892d68
Revises: 3e2792fdf330
Create Date: 2024-12-05 09:51:05.818487

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2dbcce892d68'
down_revision = '3e2792fdf330'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('loan_status', sa.Enum('available', 'on_loan', 'unavailable', name='loan_status_enum'), nullable=False))
        batch_op.add_column(sa.Column('condition', sa.Enum('functional', 'minor_repair', 'under_repair', 'out_of_service', 'missing_parts', 'inspection_needed', name='condition_enum'), nullable=False))
        batch_op.drop_column('quantity')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('quantity', sa.INTEGER(), nullable=True))
        batch_op.drop_column('condition')
        batch_op.drop_column('loan_status')

    # ### end Alembic commands ###
