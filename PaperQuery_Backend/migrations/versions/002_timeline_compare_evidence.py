"""Timeline, comparison, and evidence board storage."""

from alembic import op

from core.backend.db.database import Base
from core.backend.db import models  # noqa: F401

revision = '002_timeline_compare_evidence'
down_revision = '001_project_kernel'
branch_labels = None
depends_on = None


def upgrade():
    names = ('comparison_sessions', 'comparison_cells', 'research_claims', 'claim_evidence')
    Base.metadata.create_all(bind=op.get_bind(), tables=[Base.metadata.tables[name] for name in names], checkfirst=True)


def downgrade():
    raise RuntimeError('Restore a database backup to downgrade ResearchSpace data.')
