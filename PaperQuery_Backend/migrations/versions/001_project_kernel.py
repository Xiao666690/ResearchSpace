"""Adopt existing SQLite databases and create the project kernel.

The first revision accepts both an empty database and the pre-Alembic schema.
Column checks make the former main.py PRAGMA upgrades safe to replay.
"""

from alembic import op
from sqlalchemy import Column, String, inspect

from core.backend.db.database import Base
from core.backend.db import models  # noqa: F401

revision = '001_project_kernel'
down_revision = None
branch_labels = None
depends_on = None


def _column(table, name, column):
    bind = op.get_bind()
    if table in inspect(bind).get_table_names() and name not in {c['name'] for c in inspect(bind).get_columns(table)}:
        op.add_column(table, column)


def upgrade():
    bind = op.get_bind()
    # The baseline schema was previously created by SQLAlchemy at import time.
    # Create absent tables only, then inspect legacy tables before adding columns.
    names = ('users', 'teams', 'team_members', 'team_requests', 'knowledges',
             'documents', 'tmpdocuments', 'notes', 'posts', 'commits',
             'research_tasks', 'research_steps', 'skill_runs', 'artifacts',
             'activity_events', 'research_projects', 'project_documents')
    Base.metadata.create_all(bind=bind, tables=[Base.metadata.tables[name] for name in names], checkfirst=True)
    _column('users', 'role', Column('role', String(16), nullable=False, server_default='user'))
    _column('posts', 'category', Column('category', String(20), nullable=False, server_default='技术'))
    _column('research_tasks', 'parent_task_id', Column('parent_task_id', String(64)))
    for table in ('research_tasks', 'artifacts', 'activity_events'):
        _column(table, 'project_id', Column('project_id', String(64)))
    for name, typ in [('target_type', String(32)), ('target_id', String(255)),
                      ('title', String(255)), ('description', String()), ('metadata_json', String())]:
        _column('activity_events', name, Column(name, typ))
    inspector = inspect(bind)
    for table, name in [('research_tasks', 'project_id'), ('artifacts', 'project_id'),
                        ('activity_events', 'project_id')]:
        indexes = {index['name'] for index in inspector.get_indexes(table)}
        index_name = f'ix_{table}_{name}'
        if index_name not in indexes:
            op.create_index(index_name, table, [name])


def downgrade():
    raise RuntimeError('Project kernel migration is intentionally irreversible; restore a database backup.')
