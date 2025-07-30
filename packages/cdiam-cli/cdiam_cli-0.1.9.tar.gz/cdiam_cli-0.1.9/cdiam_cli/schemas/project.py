from datetime import datetime
from typing import Optional

from pydantic import validator
from cdiam_cli.schemas import ProjectSettings
from pydantic import BaseModel


class ProjectBase(BaseModel):
    name: str


class Project(ProjectBase):

    id: str
    tombstone: Optional[bool]
    time_created: datetime
    is_public: bool
    delete_date: Optional[datetime]
    settings: Optional[str]
    storage_used: int
    created_by: str

    @validator("settings")
    def validate_settings(cls, v: str):
        if v == "nan":
            v = "{}"
        if v is None:
            v = "{}"
        return ProjectSettings.encode_settings(ProjectSettings.decode_setting(v))

    @validator("tombstone")
    def validate_tombstone(cls, v):
        if not v:
            return False
        return v
