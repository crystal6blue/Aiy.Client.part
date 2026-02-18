from abc import ABC, abstractmethod
from typing import List, Optional
from internal.domain.models import ExperimentCreate, ExperimentRunCreate, ExperimentRunResponse, ExperimentResponse


class ExperimentRepositoryPort(ABC):

    @abstractmethod
    def create_experiment(self, experiment: ExperimentCreate) -> ExperimentResponse:
        pass

    @abstractmethod
    def create_run(self, run: ExperimentRunCreate) -> ExperimentRunResponse:
        pass

    @abstractmethod
    def get_run(self, run_id: int) -> Optional[ExperimentRunResponse]:
        pass
