Purpose
A specialized system for tracking Machine Learning experiments. It logs training parameters, performance metrics, and artifact paths into a central database.

Tech Stack

FastAPI: API layer

SQLAlchemy / PostgreSQL: Persistence

Loguru: Structured JSON logging

Docker: Containerization

Execution Chain
ML Script → AyimApi Client → FastAPI Router → Service Layer → Repository → PostgreSQL

Deployment

Docker Compose: Runs API and DB simultaneously.

Auto-Migrations: SQL scripts run automatically on startup.

Healthchecks: API waits for DB readiness.

Data Relationships

Experiment (1) : (N) Runs — One project can have many training attempts.

Run (1) : (N) Params/Metrics/Artifacts — Each attempt stores its own specific data.

Usage Example (JSON)

Create Experiment (POST /experiments):

JSON
{
  "name": "Image_Classifier_v1",
  "description": "ResNet50 training"
}
Create Run (POST /runs):

JSON
{
  "experiment_id": 1,
  "version": 1,
  "status": "completed",
  "parameters": [{"key": "lr", "value": "0.001"}],
  "metrics": [{"key": "accuracy", "value": 0.95}],
  "artifacts": [{"file_path": "/models/best.pth", "type": "weights"}]
}