"""Add adhar_no column to patient table

Revision ID: 365f6e97d0bc
Revises: 
Create Date: 2025-08-27 11:18:07.575634
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '365f6e97d0bc'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add adhaar_no column to patientdetails
    op.add_column('patientdetails', sa.Column('adhaar_no', sa.String(), nullable=True))
    # Create index for the new column
    op.create_index(op.f('ix_patientdetails_adhaar_no'), 'patientdetails', ['adhaar_no'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the index
    op.drop_index(op.f('ix_patientdetails_adhaar_no'), table_name='patientdetails')
    # Drop the column
    op.drop_column('patientdetails', 'adhaar_no')