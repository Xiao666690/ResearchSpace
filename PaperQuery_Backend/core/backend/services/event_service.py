"""Write activity records without taking ownership of the caller's transaction."""

import json

from core.backend.db.models import ActivityEvent


def emit_event(db, *, lid, event_type, project_id=None, target_type=None, target_id=None,
               title=None, description=None, metadata=None):
    event = ActivityEvent(lid=lid, project_id=project_id, event_type=event_type,
                          target_type=target_type, target_id=target_id,
                          title=title, description=description,
                          metadata_json=json.dumps(metadata, ensure_ascii=False) if metadata else None)
    db.add(event)
    return event
