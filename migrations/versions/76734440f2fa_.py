"""empty message

Revision ID: 76734440f2fa
Revises: 24ca3f519d1f
Create Date: 2023-01-17 12:33:21.113123

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "76734440f2fa"
down_revision = "24ca3f519d1f"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("sub_cat_size", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(
            sa.Column("sub_cat_gender", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(
            sa.Column("sub_cat_homo", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(
            sa.Column("sub_cat_albino", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(
            sa.Column("sub_cat_melanoid", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(
            sa.Column("sub_cat_leucistic", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(
            sa.Column("sub_cat_wild", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(
            sa.Column("sub_cat_heter", sa.String(length=255), nullable=True)
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.drop_column("sub_cat_heter")
        batch_op.drop_column("sub_cat_wild")
        batch_op.drop_column("sub_cat_leucistic")
        batch_op.drop_column("sub_cat_melanoid")
        batch_op.drop_column("sub_cat_albino")
        batch_op.drop_column("sub_cat_homo")
        batch_op.drop_column("sub_cat_gender")
        batch_op.drop_column("sub_cat_size")

    # ### end Alembic commands ###
