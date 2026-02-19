from typing import List

from internal.domain.ports.experiment_repository import ExperimentRepositoryPort
from internal.domain.models import (
    ExperimentCreate,
    ExperimentRunCreate,
    ExperimentResponse,
    ExperimentRunResponse,
)
from internal.logging.logger import get_logger


logger = get_logger("service")


class ExperimentService:
    def __init__(self, repo: ExperimentRepositoryPort):
        self.repo = repo

    def create_experiment(self, experiment: ExperimentCreate) -> ExperimentResponse:
        logger.info("service_create_experiment_started", name=experiment.name)
        existing = self.repo.get_experiment_by_name(experiment.name)
        if existing:
            logger.error(
                "service_create_experiment_conflict",
                error_type="ExperimentAlreadyExists",
                name=experiment.name,
            )
            raise ValueError(f"Experiment with name '{experiment.name}' already exists")

        result = self.repo.create_experiment(experiment)
        logger.info("service_create_experiment_succeeded", experiment_id=result.id)
        return result

    def create_run(
        self,
        run: ExperimentRunCreate,
        parameters: List[dict] | None = None,
        metrics: List[dict] | None = None,
        artifacts: List[dict] | None = None,
    ) -> ExperimentRunResponse:
        logger.info(
            "service_create_run_started",
            experiment_id=run.experiment_id,
            version=run.version,
        )

        experiment = self.repo.get_experiment(run.experiment_id)
        if not experiment:
            logger.error(
                "service_create_run_experiment_missing",
                error_type="ExperimentNotFound",
                experiment_id=run.experiment_id,
            )
            raise ValueError(f"Experiment with id {run.experiment_id} not found")

        existing_versions = self.repo.get_run_versions(run.experiment_id)
        if run.version in existing_versions:
            logger.error(
                "service_create_run_version_conflict",
                error_type="RunVersionConflict",
                experiment_id=run.experiment_id,
                version=run.version,
            )
            raise ValueError(
                f"Run with version {run.version} already exists for this experiment"
            )

        created_run = self.repo.create_run(run)

        if parameters:
            for param in parameters:
                self.repo.create_parameter(
                    run_id=created_run.id, key=param["key"], value=param["value"]
                )

        if metrics:
            for metric in metrics:
                self.repo.create_metric(
                    run_id=created_run.id, key=metric["key"], value=metric["value"]
                )

        if artifacts:
            for artifact in artifacts:
                self.repo.create_artifact(
                    run_id=created_run.id,
                    file_path=artifact["file_path"],
                    type=artifact.get("type"),
                )

        logger.info("service_create_run_succeeded", run_id=created_run.id)
        return created_run

    def get_run(self, run_id: int) -> ExperimentRunResponse | None:
        logger.info("service_get_run_called", run_id=run_id)
        run = self.repo.get_run(run_id)
        if not run:
            logger.error(
                "service_get_run_not_found",
                error_type="RunNotFound",
                run_id=run_id,
            )
            return None

        run.parameters = self.repo.get_parameters(run_id)
        run.metrics = self.repo.get_metrics(run_id)
        run.artifacts = self.repo.get_artifacts(run_id)

        logger.info("service_get_run_succeeded", run_id=run_id)
        return run
