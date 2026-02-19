from sqlalchemy.orm import Session

from internal.domain.ports.experiment_repository import ExperimentRepositoryPort
from internal.domain.models import (
    ExperimentCreate,
    ExperimentRunCreate,
    ExperimentRunResponse,
    ExperimentResponse,
)
from internal.logging.logger import get_logger
from .models import Experiment, ExperimentRun, Parameter, Metric, Artifact

logger = get_logger("db")


class PostgresExperimentRepository(ExperimentRepositoryPort):
    def __init__(self, session: Session):
        self.session = session

    def create_experiment(self, experiment: ExperimentCreate) -> ExperimentResponse:
        logger.info("repo_create_experiment_started", name=experiment.name)
        try:
            db_exp = Experiment(name=experiment.name, description=experiment.description)
            self.session.add(db_exp)
            self.session.commit()
            self.session.refresh(db_exp)
            response = ExperimentResponse.from_orm(db_exp)
            logger.info("repo_create_experiment_succeeded", experiment_id=response.id)
            return response
        except Exception as exc:
            logger.error(
                "repo_create_experiment_failed",
                error_type=type(exc).__name__,
                name=experiment.name,
                detail=str(exc),
            )
            self.session.rollback()
            raise

    def create_run(self, run: ExperimentRunCreate) -> ExperimentRunResponse:
        logger.info(
            "repo_create_run_started",
            experiment_id=run.experiment_id,
            version=run.version,
        )
        try:
            db_run = ExperimentRun(
                experiment_id=run.experiment_id,
                version=run.version,
                status=run.status,
            )
            self.session.add(db_run)
            self.session.flush()

            for p in run.parameters:
                self.session.add(
                    Parameter(run_id=db_run.id, key=p["key"], value=p["value"])
                )
            for m in run.metrics:
                self.session.add(
                    Metric(run_id=db_run.id, key=m["key"], value=m["value"])
                )
            for a in run.artifacts:
                self.session.add(
                    Artifact(
                        run_id=db_run.id,
                        file_path=a["file_path"],
                        type=a.get("type"),
                    )
                )

            self.session.commit()
            self.session.refresh(db_run)
            response = self.get_run(db_run.id)
            logger.info("repo_create_run_succeeded", run_id=db_run.id)
            return response
        except Exception as exc:
            logger.error(
                "repo_create_run_failed",
                error_type=type(exc).__name__,
                experiment_id=run.experiment_id,
                version=run.version,
                detail=str(exc),
            )
            self.session.rollback()
            raise

    def get_run(self, run_id: int) -> ExperimentRunResponse | None:
        logger.info("repo_get_run_called", run_id=run_id)
        try:
            db_run = (
                self.session.query(ExperimentRun)
                .filter(ExperimentRun.id == run_id)
                .first()
            )
            if not db_run:
                logger.info("repo_get_run_not_found", run_id=run_id)
                return None

            parameters = [{"key": p.key, "value": p.value} for p in db_run.parameters]
            metrics = [{"key": m.key, "value": m.value} for m in db_run.metrics]
            artifacts = [
                {"file_path": a.file_path, "type": a.type} for a in db_run.artifacts
            ]

            response = ExperimentRunResponse(
                id=db_run.id,
                experiment_id=db_run.experiment_id,
                version=db_run.version,
                status=db_run.status,
                started_at=db_run.started_at,
                parameters=parameters,
                metrics=metrics,
                artifacts=artifacts,
            )
            logger.info("repo_get_run_succeeded", run_id=run_id)
            return response
        except Exception as exc:
            logger.error(
                "repo_get_run_failed",
                error_type=type(exc).__name__,
                run_id=run_id,
                detail=str(exc),
            )
            raise
