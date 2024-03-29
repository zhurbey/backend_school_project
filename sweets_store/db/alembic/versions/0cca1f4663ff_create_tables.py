"""create tables

Revision ID: 0cca1f4663ff
Revises: 
Create Date: 2021-03-27 12:41:01.458181

"""
from alembic import op
import sqlalchemy as sa

from sweets_store.db.tables.couriers import CouriersTypesEnum


# revision identifiers, used by Alembic.
revision = '0cca1f4663ff'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('couriers',
    sa.Column('courier_id', sa.Integer(), nullable=False),
    sa.Column('courier_type', sa.Enum('foot', 'bike', 'car', name='courierstypes'), nullable=False),
    sa.Column('regions', sa.ARRAY(sa.Integer()), nullable=False),
    sa.Column('working_hours', sa.ARRAY(sa.String()), nullable=False),
    sa.PrimaryKeyConstraint('courier_id')
    )
    op.create_table('bundles',
    sa.Column('bundle_id', sa.Integer(), nullable=False),
    sa.Column('courier_id', sa.Integer(), nullable=False),
    sa.Column('courier_type', sa.Enum('foot', 'bike', 'car', name='courierstypes'), nullable=False),
    sa.Column('assign_time', sa.DateTime(), nullable=False),
    sa.Column('is_finished', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['courier_id'], ['couriers.courier_id'], ),
    sa.PrimaryKeyConstraint('bundle_id')
    )
    op.create_table('orders',
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('weight', sa.Float(), nullable=False),
    sa.Column('region', sa.Integer(), nullable=False),
    sa.Column('delivery_hours', sa.ARRAY(sa.String()), nullable=False),
    sa.Column('bundle_id', sa.Integer(), nullable=True),
    sa.Column('complete_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['bundle_id'], ['bundles.bundle_id'], ),
    sa.PrimaryKeyConstraint('order_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('orders')
    op.drop_table('bundles')
    op.drop_table('couriers')
    # ### end Alembic commands ###

    CouriersTypesEnum.drop(op.get_bind(), checkfirst=False)
