from internal.domain.ports.experiment_repository import ExperimentRepositoryPort
from internal.domain.models import ExperimentCreate, ExperimentRunCreate, ExperimentRunResponse, ExperimentResponse
from .models import Experiment, ExperimentRun, Parameter, Metric, Artifact
from sqlalchemy.orm import Session

class PostgresExperimentRepository(ExperimentRepositoryPort):
    def __init__(self, session: Session):
        self.session = session

    def create_experiment(self, experiment: ExperimentCreate) -> ExperimentResponse:
        db_exp = Experiment(name=experiment.name, description=experiment.description)
        self.session.add(db_exp)
        self.session.commit()
        self.session.refresh(db_exp)
        return ExperimentResponse.from_orm(db_exp)

    def create_run(self, run: ExperimentRunCreate) -> ExperimentRunResponse:
        db_run = ExperimentRun(
            experiment_id=run.experiment_id,
            version=run.version,
            status=run.status
        )
        self.session.add(db_run)
        self.session.flush()

        for p in run.parameters:
            self.session.add(Parameter(run_id=db_run.id, key=p["key"], value=p["value"]))
        for m in run.metrics:
            self.session.add(Metric(run_id=db_run.id, key=m["key"], value=m["value"]))
        for a in run.artifacts:
            self.session.add(Artifact(run_id=db_run.id, file_path=a["file_path"], type=a.get("type")))

        self.session.commit()
        self.session.refresh(db_run)
        return self.get_run(db_run.id)

    def get_run(self, run_id: int) -> ExperimentRunResponse:
        db_run = self.session.query(ExperimentRun).filter(ExperimentRun.id == run_id).first()
        if not db_run:
            return None

        parameters = [{"key": p.key, "value": p.value} for p in db_run.parameters]
        metrics = [{"key": m.key, "value": m.value} for m in db_run.metrics]
        artifacts = [{"file_path": a.file_path, "type": a.type} for a in db_run.artifacts]

        return ExperimentRunResponse(
            id=db_run.id,
            experiment_id=db_run.experiment_id,
            version=db_run.version,
            status=db_run.status,
            started_at=db_run.started_at,
            parameters=parameters,
            metrics=metrics,
            artifacts=artifacts
        )
