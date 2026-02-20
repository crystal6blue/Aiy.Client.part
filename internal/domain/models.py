from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

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


class ExperimentRunCreate(BaseModel):
    experiment_id: int
    version: int
    status: Optional[str] = "running"
    parameters: List[dict] = Field(default_factory=list)
    metrics: List[dict] = Field(default_factory=list)
    artifacts: List[dict] = Field(default_factory=list)

class ExperimentRunResponse(BaseModel):
    id: int
    experiment_id: int
    version: int
    status: str
    started_at: datetime
    parameters: List[dict] = Field(default_factory=list)
    metrics: List[dict] = Field(default_factory=list)
    artifacts: List[dict] = Field(default_factory=list)

    class Config:
        from_attributes = True
