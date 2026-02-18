from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Experiment(Base):
    __tablename__ = "experiments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    runs = relationship("ExperimentRun", back_populates="experiment", cascade="all, delete-orphan")


class ExperimentRun(Base):
    __tablename__ = "experiment_runs"
    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    status = Column(String(50), default="running")
    started_at = Column(TIMESTAMP, server_default=func.now())

    experiment = relationship("Experiment", back_populates="runs")
    parameters = relationship("Parameter", cascade="all, delete-orphan")
    metrics = relationship("Metric", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", cascade="all, delete-orphan")


class Parameter(Base):
    __tablename__ = "parameters"
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("experiment_runs.id", ondelete="CASCADE"))
    key = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)


class Metric(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("experiment_runs.id", ondelete="CASCADE"))
    key = Column(String(255), nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now())


class Artifact(Base):
    __tablename__ = "artifacts"
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("experiment_runs.id", ondelete="CASCADE"))
    file_path = Column(Text, nullable=False)
    type = Column(String(50))
