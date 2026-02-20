from fastapi import HTTPException
import logging
from typing import List

from internal.domain.ports.experiment_repository import ExperimentRepositoryPort
from internal.domain.models import (
    ExperimentCreate,
    ExperimentRunCreate,
    ExperimentResponse,
    ExperimentRunResponse
)

logger = logging.getLogger(__name__)


class ExperimentService:
    def __init__(self, repo: ExperimentRepositoryPort):
        self.repo = repo

    def create_experiment(self, experiment: ExperimentCreate) -> ExperimentResponse:
        try:
            existing = self.repo.get_experiment_by_name(experiment.name)
            if existing:
                logger.error(
                    f"Experiment creation failed: name '{experiment.name}' already exists"
                )
                raise HTTPException(
                    status_code=400,
                    detail=f"Experiment with name '{experiment.name}' already exists"
                )

            logger.info(f"Creating experiment '{experiment.name}'")
            return self.repo.create_experiment(experiment)

        except HTTPException:
            raise
        except Exception:
            logger.exception("Unexpected error while creating experiment")
            raise HTTPException(status_code=500, detail="Internal server error")

    def create_run(
        self,
        run: ExperimentRunCreate,
        parameters: List[dict] = None,
        metrics: List[dict] = None,
        artifacts: List[dict] = None
    ) -> ExperimentRunResponse:
        try:
            experiment = self.repo.get_experiment(run.experiment_id)
            if not experiment:
                logger.error(
                    f"Run creation failed: experiment {run.experiment_id} not found"
                )
                raise HTTPException(
                    status_code=400,
                    detail=f"Experiment with id {run.experiment_id} not found"
                )

            if run.version <= 0:
                logger.error(
                    f"Run creation failed: negative version {run.version}"
                )
                raise HTTPException(
                    status_code=400,
                    detail=f"Run version cannot be negative: {run.version}"
                )

            existing_versions = self.repo.get_run_versions(run.experiment_id)
            if run.version in existing_versions:
                logger.error(
                    f"Run creation failed: version {run.version} already exists "
                    f"for experiment {run.experiment_id}"
                )
                raise HTTPException(
                    status_code=400,
                    detail=f"Run with version {run.version} already exists for this experiment"
                )

            logger.info(
                f"Creating run version {run.version} "
                f"for experiment {run.experiment_id}"
            )

            created_run = self.repo.create_run(run)

            if parameters:
                for param in parameters:
                    if not param.get("key") or not param.get("value"):
                        logger.error(f"Invalid parameter: {param}")
                        raise HTTPException(
                            status_code=400,
                            detail=f"Parameter key and value must not be empty: {param}"
                        )
                    self.repo.create_parameter(
                        run_id=created_run.id,
                        key=param["key"],
                        value=param["value"]
                    )

            if metrics:
                for metric in metrics:
                    if not metric.get("key") or metric.get("value") is None:
                        logger.error(f"Invalid metric: {metric}")
                        raise HTTPException(
                            status_code=400,
                            detail=f"Metric key and value must not be empty: {metric}"
                        )
                    self.repo.create_metric(
                        run_id=created_run.id,
                        key=metric["key"],
                        value=metric["value"]
                    )

            if artifacts:
                for artifact in artifacts:
                    if not artifact.get("file_path"):
                        logger.error(f"Invalid artifact: {artifact}")
                        raise HTTPException(
                            status_code=400,
                            detail=f"Artifact file_path must not be empty: {artifact}"
                        )
                    self.repo.create_artifact(
                        run_id=created_run.id,
                        file_path=artifact["file_path"],
                        type=artifact.get("type")
                    )

            logger.info(f"Run {created_run.id} successfully created")
            return created_run

        except HTTPException:
            raise
        except Exception:
            logger.exception("Unexpected error while creating run")
            raise HTTPException(status_code=500, detail="Internal server error")

    def get_run(self, run_id: int) -> ExperimentRunResponse:
        try:
            run = self.repo.get_run(run_id)
            if not run:
                logger.warning(f"Run {run_id} not found")
                raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

            run.parameters = self.repo.get_parameters(run_id)
            run.metrics = self.repo.get_metrics(run_id)
            run.artifacts = self.repo.get_artifacts(run_id)

            logger.info(f"Run {run_id} retrieved successfully")
            return run

        except HTTPException:
            raise
        except Exception:
            logger.exception(f"Unexpected error while retrieving run {run_id}")
            raise HTTPException(status_code=500, detail="Internal server error")