from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from internal.api.schemas import ExperimentCreate, ExperimentRunCreate, ExperimentRunResponse, ExperimentResponse
from internal.usecases.experiment_service import ExperimentService
from internal.adapters.postgres.experiment_repository import PostgresExperimentRepository
from internal.adapters.postgres.database import get_db_session

router = APIRouter()

def get_experiment_service(session: Session = Depends(get_db_session)):
    repo = PostgresExperimentRepository(session)
    service = ExperimentService(repo)
    return service

# POST /experiments
@router.post("/experiments", response_model=ExperimentResponse)
def create_experiment(experiment: ExperimentCreate, service: ExperimentService = Depends(get_experiment_service)):
    return service.create_experiment(experiment)

# POST /runs
@router.post("/runs", response_model=ExperimentRunResponse)
def create_run(run: ExperimentRunCreate, service: ExperimentService = Depends(get_experiment_service)):
    return service.create_run(run)

# GET /runs/{id}
@router.get("/runs/{run_id}", response_model=ExperimentRunResponse)
def get_run(run_id: int, service: ExperimentService = Depends(get_experiment_service)):
    run = service.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
