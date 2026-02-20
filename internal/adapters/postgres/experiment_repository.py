# repository.py
from internal.domain.ports.experiment_repository import ExperimentRepositoryPort
from internal.domain.models import ExperimentCreate, ExperimentRunCreate, ExperimentRunResponse, ExperimentResponse
from .models import Experiment, ExperimentRun, Parameter, Metric, Artifact
from sqlalchemy.orm import Session
from typing import List, Optional

class PostgresExperimentRepository(ExperimentRepositoryPort):
    def __init__(self, session: Session):
        self.session = session

    def create_experiment(self, experiment: ExperimentCreate) -> ExperimentResponse:
        db_exp = Experiment(name=experiment.name, description=experiment.description)
        self.session.add(db_exp)
        self.session.commit()
        self.session.refresh(db_exp)
        return ExperimentResponse.from_orm(db_exp)

    def get_experiment_by_name(self, name: str) -> Optional[ExperimentResponse]:
        db_exp = self.session.query(Experiment).filter(Experiment.name == name).first()
        return ExperimentResponse.from_orm(db_exp) if db_exp else None

    def get_experiment(self, experiment_id: int) -> Optional[ExperimentResponse]:
        db_exp = self.session.query(Experiment).filter(Experiment.id == experiment_id).first()
        return ExperimentResponse.from_orm(db_exp) if db_exp else None

    def create_run(self, run: ExperimentRunCreate) -> ExperimentRunResponse:
        db_run = ExperimentRun(
            experiment_id=run.experiment_id,
            version=run.version,
            status=run.status
        )
        self.session.add(db_run)
        self.session.flush()  

    
        for p in run.parameters:
            self.create_parameter(db_run.id, p["key"], p["value"])
        for m in run.metrics:
            self.create_metric(db_run.id, m["key"], m["value"])
        for a in run.artifacts:
            self.create_artifact(db_run.id, a["file_path"], a.get("type"))

        self.session.commit()
        self.session.refresh(db_run)
        return self.get_run(db_run.id)

    def get_run(self, run_id: int) -> Optional[ExperimentRunResponse]:
        db_run = self.session.query(ExperimentRun).filter(ExperimentRun.id == run_id).first()
        if not db_run:
            return None

        return ExperimentRunResponse(
            id=db_run.id,
            experiment_id=db_run.experiment_id,
            version=db_run.version,
            status=db_run.status,
            started_at=db_run.started_at,
            parameters=[{"key": p.key, "value": p.value} for p in db_run.parameters],
            metrics=[{"key": m.key, "value": m.value} for m in db_run.metrics],
            artifacts=[{"file_path": a.file_path, "type": a.type} for a in db_run.artifacts]
        )

    def get_run_versions(self, experiment_id: int) -> List[int]:
        versions = (
            self.session.query(ExperimentRun.version)
            .filter(ExperimentRun.experiment_id == experiment_id)
            .all()
        )
        return [v[0] for v in versions]

    def create_parameter(self, run_id: int, key: str, value: str):
        self.session.add(Parameter(run_id=run_id, key=key, value=value))

    def create_metric(self, run_id: int, key: str, value: float):
        self.session.add(Metric(run_id=run_id, key=key, value=value))

    def create_artifact(self, run_id: int, file_path: str, type: Optional[str] = None):
        self.session.add(Artifact(run_id=run_id, file_path=file_path, type=type))

    def get_parameters(self, run_id: int) -> List[dict]:
        params = self.session.query(Parameter).filter(Parameter.run_id == run_id).all()
        return [{"key": p.key, "value": p.value} for p in params]

    def get_metrics(self, run_id: int) -> List[dict]:
        metrics = self.session.query(Metric).filter(Metric.run_id == run_id).all()
        return [{"key": m.key, "value": m.value} for m in metrics]

    def get_artifacts(self, run_id: int) -> List[dict]:
        artifacts = self.session.query(Artifact).filter(Artifact.run_id == run_id).all()
        return [{"file_path": a.file_path, "type": a.type} for a in artifacts]
