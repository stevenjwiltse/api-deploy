"""Add kc_id field

Revision ID: 4e1a3a35a089
Revises: d9aa9f87cc2b
Create Date: 2025-04-09 15:17:22.114810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e1a3a35a089'
down_revision: Union[str, None] = 'd9aa9f87cc2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update kc_id field based on user_id, overwriting existing values
    op.execute("""
        UPDATE user
        SET kc_id = CASE user_id
            WHEN 1 THEN '41e28799-7aa8-438b-88b8-e6292b35bb01'
            WHEN 2 THEN '41e28799-7aa8-438b-88b8-e6292b35bb11'
            WHEN 3 THEN '41e28799-7aa8-438b-88b8-e6292b35bb21'
            WHEN 4 THEN '41e28799-7aa8-438b-88b8-e6292b35bb31'
            ELSE kc_id
        END;
    """)

def downgrade() -> None:
    # Revert the kc_id values for specific user_ids
    op.execute("""
        UPDATE user
        SET kc_id = NULL
        WHERE user_id IN (1, 2, 3, 4);
    """)