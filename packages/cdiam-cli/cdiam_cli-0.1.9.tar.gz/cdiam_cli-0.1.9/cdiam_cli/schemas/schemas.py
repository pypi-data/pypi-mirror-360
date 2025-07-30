from typing import Literal
from pydantic import BaseModel
from typing import Union, List, Dict, Any
import json


class ProjectSettings(BaseModel):

    cpdb: List[str] = []
    enrichment: List[str] = []

    @staticmethod
    def encode_settings(settings: Union[Dict[str, Any], "ProjectSettings"]) -> str:
        return ProjectSettings.parse_obj(settings).json()

    @staticmethod
    def decode_setting(settings: str) -> "ProjectSettings":
        if settings is None:
            settings = "{}"
        return ProjectSettings.parse_obj(json.loads(settings))


class ParamsRequestGetTaskStatus(BaseModel):
    """
    Represents the parameters for a request to get the status of an analysis task.

    :param api: The API endpoint being called, which should be "get_task_status".
    :param task_id: The unique identifier of the analysis task.
    """

    api: Literal["get_task_status"]
    task_id: str
