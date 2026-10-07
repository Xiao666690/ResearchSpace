"""Graph and Studio storage."""

from alembic import op

from core.backend.db.database import Base
from core.backend.db import models  # noqa: F401

revision = '003_graph_studio'
down_revision = '002_timeline_compare_evidence'
branch_labels = None
depends_on = None


def upgrade():
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=True)


def downgrade():
    raise RuntimeError('Restore a database backup to downgrade ResearchSpace data.')
