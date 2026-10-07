"""Project collaboration storage."""

from alembic import op

from core.backend.db.database import Base
from core.backend.db import models  # noqa: F401

revision = '004_collaboration'
down_revision = '003_graph_studio'
branch_labels = None
depends_on = None


def upgrade():
    names = ('project_members', 'research_comments', 'task_assignments')
    Base.metadata.create_all(bind=op.get_bind(), tables=[Base.metadata.tables[name] for name in names], checkfirst=True)


def downgrade():
    raise RuntimeError('Restore a database backup to downgrade ResearchSpace data.')
