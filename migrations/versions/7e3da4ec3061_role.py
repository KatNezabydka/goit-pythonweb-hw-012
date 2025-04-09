from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '7e3da4ec3061'
down_revision: Union[str, None] = '87fc0e1fa609'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('role', sa.String(length=255), nullable=False, server_default='user'))
    # ### end Alembic commands ###

    op.execute("""
              UPDATE users
              SET role = 'user'
              WHERE role IS NULL
          """)

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'role')