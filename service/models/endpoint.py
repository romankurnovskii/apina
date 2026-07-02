from pydantic import BaseModel
from typing import List, Dict, Optional, Any


class Parameter(BaseModel):
    name: str
    type: str
    required: bool
    description: Optional[str] = None


class EndpointSchema(BaseModel):
    id: str
    path: str
    method: str
    full_url: str
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: Dict[str, List[Parameter]]
    responses: Dict[str, Any]
    tags: Optional[List[str]] = None
