import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.backend.db.models import ActivityEvent
from core.backend.router.dependencies import get_db
from core.backend.services.project_service import get_project_or_404
from core.backend.utils.utils import get_current_user

router = APIRouter(prefix='/projects/{project_id}/timeline', tags=['timeline'])


@router.get('')
def timeline(project_id: str, limit: int = 100, user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    rows = db.query(ActivityEvent).filter_by(project_id=project_id, lid=project.lid).order_by(
        ActivityEvent.created_at.desc(), ActivityEvent.id.desc()).limit(min(max(limit, 1), 200)).all()
    return {'status_code': 200, 'data': [{
        'id': row.id, 'event_type': row.event_type, 'target_type': row.target_type,
        'target_id': row.target_id, 'title': row.title, 'description': row.description,
        'metadata': json.loads(row.metadata_json) if row.metadata_json else {},
        'created_at': row.created_at.isoformat() if row.created_at else None,
    } for row in rows]}
