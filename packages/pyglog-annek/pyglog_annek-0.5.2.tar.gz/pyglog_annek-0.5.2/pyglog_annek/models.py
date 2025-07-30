from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict, Optional


class Assignment(BaseModel):
    assigned_from_tags: List[str]
    collector_id: str
    configuration_id: str


class NodeDetails(BaseModel):
    collector_configuration_directory: str
    ip: str
    log_file_list: Optional[List[str]] = None
    metrics: Dict
    operating_system: str
    status: Dict
    tags: List[str]


class Sidecar(BaseModel):
    active: bool
    assignments: list[Assignment]
    collectors: None
    last_seen: datetime
    node_details: NodeDetails
    node_id: str
    node_name: str
    sidecar_version: str