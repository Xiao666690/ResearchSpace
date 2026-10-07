from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = ''
    research_goal: str = ''


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    research_goal: str | None = None


class ProjectDocumentAdd(BaseModel):
    knowledge_id: str
    document_id: str
