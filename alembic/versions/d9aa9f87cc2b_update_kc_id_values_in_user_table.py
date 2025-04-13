"""Update kc_id values in user table

Revision ID: d9aa9f87cc2b
Revises: 73983ed6aa8a
Create Date: 2025-04-09 14:57:52.012267

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9aa9f87cc2b'
down_revision: Union[str, None] = '73983ed6aa8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update kc_id field based on user_id
    op.execute("""
        UPDATE user
        SET kc_id = CASE user_id
            WHEN 1 THEN '41e28799-7aa8-438b-88b8-e6292b35bb01'
            WHEN 2 THEN '41e28799-7aa8-438b-88b8-e6292b35bb11'
            WHEN 3 THEN '41e28799-7aa8-438b-88b8-e6292b35bb21'
            WHEN 4 THEN '41e28799-7aa8-438b-88b8-e6292b35bb31'
            ELSE kc_id
        END
        WHERE kc_id IS NULL; -- Only update rows where kc_id is empty
    """)

def downgrade() -> None:
    # Revert the kc_id values to NULL for specific user_id
    op.execute("""
        UPDATE user
        SET kc_id = NULL
        WHERE user_id IN (1, 2, 3, 4);
    """)