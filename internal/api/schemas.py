from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class ExperimentBase(BaseModel):
    name: str
    description: Optional[str] = None

class ExperimentCreate(ExperimentBase):
    pass

class ExperimentResponse(ExperimentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  

class ExperimentRunBase(BaseModel):
    version: int
    status: Optional[str] = "running"

class ExperimentRunCreate(ExperimentRunBase):
    experiment_id: int
    parameters: List[dict] = []
    metrics: List[dict] = []
    artifacts: List[dict] = []

class ExperimentRunResponse(ExperimentRunBase):
    id: int
    experiment_id: int
    started_at: datetime
    parameters: List[dict] = []
    metrics: List[dict] = []
    artifacts: List[dict] = []

    class Config:
        from_attributes = True
