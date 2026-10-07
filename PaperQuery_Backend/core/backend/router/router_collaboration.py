"""Project member roles, comments, and research task assignments."""

import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.backend.db.models import (Artifact, ComparisonSession, ProjectDocument, ProjectMember,
                                    ResearchClaim, ResearchComment, ResearchTask, TaskAssignment, User)
from core.backend.router.dependencies import get_db
from core.backend.services.event_service import emit_event
from core.backend.services.project_service import get_project_or_404, require_project_owner
from core.backend.utils.utils import get_current_user, get_workspace_lid

router = APIRouter(prefix='/projects/{project_id}/collaboration', tags=['collaboration'])


class MemberAdd(BaseModel):
    username: str
    role: Literal['OWNER', 'EDITOR', 'VIEWER'] = 'EDITOR'


class CommentAdd(BaseModel):
    target_type: Literal['paper', 'claim', 'comparison', 'task', 'artifact']
    target_id: str
    content: str = Field(min_length=1, max_length=5000)


class AssignmentAdd(BaseModel):
    task_id: str
    username: str


def _workspace_user(db, username, lid):
    target = db.query(User).filter_by(username=username).first()
    if not target or get_workspace_lid(db, target) != lid:
        raise HTTPException(404, '用户不在当前工作空间')
    return target


def _target_exists(db, project_id, kind, target_id):
    model, key = {
        'paper': (ProjectDocument, 'document_id'),
        'claim': (ResearchClaim, 'claim_id'),
        'comparison': (ComparisonSession, 'session_id'),
        'task': (ResearchTask, 'task_id'),
        'artifact': (Artifact, 'artifact_id'),
    }[kind]
    return db.query(model).filter(getattr(model, key) == target_id,
                                  model.project_id == project_id).first() is not None


@router.get('/members')
def members(project_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    rows = db.query(ProjectMember).filter_by(project_id=project_id).order_by(ProjectMember.id).all()
    members = [{'username': row.username, 'role': row.role,
                'joined_at': row.joined_at.isoformat() if row.joined_at else None} for row in rows]
    if not any(item['username'] == project.created_by for item in members):
        members.insert(0, {'username': project.created_by, 'role': 'OWNER', 'joined_at': None})
    return {'status_code': 200, 'data': members}


@router.post('/members')
def add_member(project_id: str, payload: MemberAdd, user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    require_project_owner(project, user, db)
    target = _workspace_user(db, payload.username.strip(), project.lid)
    member = db.query(ProjectMember).filter_by(project_id=project_id, username=target.username).first()
    if member:
        member.role = payload.role
    else:
        db.add(ProjectMember(project_id=project_id, username=target.username, role=payload.role))
    db.commit()
    return members(project_id, user, db)


@router.delete('/members/{username}')
def remove_member(project_id: str, username: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    require_project_owner(project, user, db)
    if username == project.created_by:
        raise HTTPException(403, '不能移除项目创建者')
    member = db.query(ProjectMember).filter_by(project_id=project_id, username=username).first()
    if member is None:
        raise HTTPException(404, '项目成员不存在')
    db.delete(member)
    db.commit()
    return {'status_code': 200, 'msg': '项目成员已移除'}


@router.get('/comments')
def comments(project_id: str, target_type: str | None = None, target_id: str | None = None,
             user=Depends(get_current_user), db: Session = Depends(get_db)):
    get_project_or_404(db, project_id, user)
    query = db.query(ResearchComment).filter_by(project_id=project_id)
    if target_type:
        query = query.filter_by(target_type=target_type)
    if target_id:
        query = query.filter_by(target_id=target_id)
    rows = query.order_by(ResearchComment.id.desc()).limit(200).all()
    return {'status_code': 200, 'data': [{'comment_id': row.comment_id, 'username': row.username,
        'target_type': row.target_type, 'target_id': row.target_id, 'content': row.content,
        'created_at': row.created_at.isoformat() if row.created_at else None} for row in rows]}


@router.post('/comments')
def add_comment(project_id: str, payload: CommentAdd, user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    if not _target_exists(db, project_id, payload.target_type, payload.target_id):
        raise HTTPException(404, '评论对象不属于当前项目')
    row = ResearchComment(comment_id=uuid.uuid4().hex, project_id=project_id,
                          username=user.username, target_type=payload.target_type,
                          target_id=payload.target_id, content=payload.content.strip())
    if not row.content:
        raise HTTPException(422, '评论不能为空')
    db.add(row)
    emit_event(db, lid=project.lid, project_id=project_id, event_type='COMMENT_CREATED',
               target_type=payload.target_type, target_id=payload.target_id,
               title=f'{user.username} 添加评论')
    db.commit()
    return {'status_code': 200, 'data': {'comment_id': row.comment_id}}


@router.get('/assignments')
def assignments(project_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    get_project_or_404(db, project_id, user)
    rows = db.query(TaskAssignment, ResearchTask).join(
        ResearchTask, ResearchTask.task_id == TaskAssignment.task_id).filter(
        ResearchTask.project_id == project_id).all()
    return {'status_code': 200, 'data': [{'task_id': item.task_id, 'goal': task.goal,
        'username': item.username, 'assigned_at': item.assigned_at.isoformat() if item.assigned_at else None}
        for item, task in rows]}


@router.post('/assignments')
def assign_task(project_id: str, payload: AssignmentAdd, user=Depends(get_current_user), db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id, user)
    task = db.query(ResearchTask).filter_by(task_id=payload.task_id, project_id=project_id,
                                            lid=project.lid).first()
    if task is None:
        raise HTTPException(404, '任务不属于当前项目')
    _workspace_user(db, payload.username.strip(), project.lid)
    existing = db.query(TaskAssignment).filter_by(task_id=task.task_id, username=payload.username).first()
    if existing is None:
        db.add(TaskAssignment(task_id=task.task_id, username=payload.username))
        emit_event(db, lid=project.lid, project_id=project_id, event_type='TASK_ASSIGNED',
                   target_type='task', target_id=task.task_id, title=task.goal[:255],
                   metadata={'username': payload.username})
        db.commit()
    return {'status_code': 200, 'msg': '任务已分配'}
