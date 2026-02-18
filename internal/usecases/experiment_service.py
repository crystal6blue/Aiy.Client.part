from internal.domain.ports.experiment_repository import ExperimentRepositoryPort
from internal.domain.models import (
    ExperimentCreate,
    ExperimentRunCreate,
    ExperimentResponse,
    ExperimentRunResponse
)
from typing import List

class ExperimentService:
    def __init__(self, repo: ExperimentRepositoryPort):
        self.repo = repo

    def create_experiment(self, experiment: ExperimentCreate) -> ExperimentResponse:
        existing = self.repo.get_experiment_by_name(experiment.name)
        if existing:
            raise ValueError(f"Experiment with name '{experiment.name}' already exists")
        return self.repo.create_experiment(experiment)

    def create_run(
        self,
        run: ExperimentRunCreate,
        parameters: List[dict] = None,
        metrics: List[dict] = None,
        artifacts: List[dict] = None
    ) -> ExperimentRunResponse:
        experiment = self.repo.get_experiment(run.experiment_id)
        if not experiment:
            raise ValueError(f"Experiment with id {run.experiment_id} not found")

        existing_versions = self.repo.get_run_versions(run.experiment_id)
        if run.version in existing_versions:
            raise ValueError(f"Run with version {run.version} already exists for this experiment")

        created_run = self.repo.create_run(run)

        if parameters:
            for param in parameters:
                self.repo.create_parameter(run_id=created_run.id, key=param["key"], value=param["value"])

        if metrics:
            for metric in metrics:
                self.repo.create_metric(run_id=created_run.id, key=metric["key"], value=metric["value"])

        if artifacts:
            for artifact in artifacts:
                self.repo.create_artifact(run_id=created_run.id, file_path=artifact["file_path"], type=artifact.get("type"))

        return created_run

    def get_run(self, run_id: int) -> ExperimentRunResponse:
        run = self.repo.get_run(run_id)
        if not run:
            return None

        run.parameters = self.repo.get_parameters(run_id)
        run.metrics = self.repo.get_metrics(run_id)
        run.artifacts = self.repo.get_artifacts(run_id)

        return run
