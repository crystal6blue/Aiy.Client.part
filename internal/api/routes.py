from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from internal.api.schemas import ExperimentCreate, ExperimentRunCreate, ExperimentRunResponse, ExperimentResponse
from internal.usecases.experiment_service import ExperimentService
from internal.adapters.postgres.experiment_repository import PostgresExperimentRepository
from internal.adapters.postgres.database import get_db_session
from internal.logging.logger import get_logger

router = APIRouter()
logger = get_logger("api")

def get_experiment_service(session: Session = Depends(get_db_session)):
    repo = PostgresExperimentRepository(session)
    service = ExperimentService(repo)
    return service

# POST /experiments
@router.post("/experiments", response_model=ExperimentResponse)
def create_experiment(experiment: ExperimentCreate, service: ExperimentService = Depends(get_experiment_service)):
    logger.info("create_experiment called")
    result = service.create_experiment(experiment)
    logger.info("experiment_created", experiment_id=result.id)
    return result

# POST /runs
@router.post("/runs", response_model=ExperimentRunResponse)
def create_run(run: ExperimentRunCreate, service: ExperimentService = Depends(get_experiment_service)):
    logger.info("create_run called")
    result = service.create_run(run)
    logger.info("run_created", run_id=result.id)
    return result

# GET /runs/{id}
@router.get("/runs/{run_id}", response_model=ExperimentRunResponse)
def get_run(run_id: int, service: ExperimentService = Depends(get_experiment_service)):
    logger.info("get_run called", run_id=run_id)
    run = service.get_run(run_id)
    if not run:
        logger.error(
            "run_not_found",
            error_type="RunNotFound",
            run_id=run_id,
        )
        raise HTTPException(status_code=404, detail="Run not found")
    logger.info("run_returned", run_id=run_id)
    return run
