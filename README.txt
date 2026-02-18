-- nothing

Json for Experiments:
```json
{
  "name": "Spam Classifier",
  "description": "Эксперимент с разными learning rate"
}
```

Json for Run Experiments:

```json
{
  "experiment_id": 1,
  "version": 1,
  "status": "running",
  "parameters": [
    {"key": "learning_rate", "value": "0.01"},
    {"key": "batch_size", "value": "32"}
  ],
  "metrics": [
    {"key": "accuracy", "value": 0.85},
    {"key": "loss", "value": 0.35}
  ],
  "artifacts": [
    {"file_path": "models/spam_classifier_v1.pkl", "type": "model"},
    {"file_path": "plots/loss_curve.png", "type": "plot"}
  ]
}
```