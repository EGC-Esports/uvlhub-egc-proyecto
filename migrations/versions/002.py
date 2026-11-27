"""2FA: secreto TOTP en user y tabla recovery_code (WI200-1)

Revision ID: 002
Revises: 001
Create Date: 2026-11-26 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        # Guarda el secreto cifrado con Fernet (~140 caracteres), no el base32 en claro.
        batch_op.add_column(sa.Column('totp_secret', sa.String(length=255), nullable=True))
        batch_op.add_column(
            sa.Column('two_factor_enabled', sa.Boolean(), nullable=False, server_default=sa.false())
        )

    op.create_table('recovery_code',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('code_hash', sa.String(length=64), nullable=False),
    sa.Column('used_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('recovery_code', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_recovery_code_user_id'), ['user_id'], unique=False)


def downgrade():
    # Sin drop_index previo: MariaDB no deja borrar ix_recovery_code_user_id
    # mientras lo use la clave foránea (error 1553). Al borrar la tabla se va
    # también el índice.
    op.drop_table('recovery_code')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('two_factor_enabled')
        batch_op.drop_column('totp_secret')
