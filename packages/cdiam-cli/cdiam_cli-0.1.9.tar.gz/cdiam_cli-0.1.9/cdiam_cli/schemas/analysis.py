from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class TaskStatus(BaseModel):
    status: str = "UNKNOWN"


class AnalysisResultBase(BaseModel):
    result_id: str
    data_id: str
    analysis: int
    task_id: str
    args: str
    project_id: str
    user_email: Optional[str]


class AnalysisCatalogBase(BaseModel):
    name: str
    description: Optional[str]


class AnalysisCatalog(AnalysisCatalogBase):
    """
    This table stores available analyses type
    that the App supports.
    """

    id: int
    time_created: datetime
    time_modified: datetime
    """A list of all analysis results of this type"""
    results: List["AnalysisResult"]


class AnalysisResultRead(AnalysisResultBase):
    """
    A response model of an anlysis result
    """

    time_created: datetime
    time_modified: datetime
    task: Optional[TaskStatus]
    result_data_status: Optional[str]


class AnalysisResult(AnalysisResultBase):
    """
    This table stores all analyses that had been produced for a data
    The analysis reference points to the description of the analysis.
    The result_id reference points to the detail result of the analysis
    """

    time_created: datetime
    time_modified: datetime
