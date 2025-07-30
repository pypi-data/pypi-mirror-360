# Model Deployment

This guide covers deploying trained models for inference using the Qognitive platform.

## Prerequisites

- Authenticated ExperimentClient
- A completed training run with saved checkpoints
- Understanding of model selection criteria

## Overview

Model deployment selects the best performing checkpoint from a training run and creates a deployment using the saved state parameters. Each experiment saves metrics associated with checkpoints that you can use to select the best model.

## Deployment Process

### Basic Model Deployment

```python
from qcogclient import ExperimentClient
import os
import dotenv

dotenv.load_dotenv()

client = ExperimentClient(
    api_key=os.getenv("QCOG_API_KEY"),
)

result = await client.create_deployment(
    name="my-model-deployment",
    run_name="my-training-run",  # Training run to deploy
    version="1.0.0",
    criterion={
        "metric": "loss",
        "value": "smallest"  # Select checkpoint with smallest loss
    }
)

if 'response' in result:
    print(f"Deployment created: {result['response']['deployment_id']}")
else:
    print(f"Deployment failed: {result['error']}")
```

### Selection Criteria

You can use different criteria to select the best checkpoint:

**Smallest Loss:**
```python
criterion = {
    "metric": "loss",
    "value": "smallest"
}
```

**Largest Accuracy:**
```python
criterion = {
    "metric": "accuracy", 
    "value": "largest"
}
```

### Check Available Metrics

To see what metrics are available from a training run, you can use the `get_experiment_run` method. This will return the recorded metrics from your training run.

```python
from qcogclient import ExperimentClient

client = ExperimentClient()

# Get training run details
result = await client.get_experiment_run("my-training-run")
metrics = result['response'].get('metrics', {})

print("Available metrics:")
for metric_name, value in metrics.items():
    print(f"  {metric_name}: {value}")
```

## Deployment Management

### List Deployments

View deployments for a specific training run:

**CLI:**
```bash 
qcog experiment list-deployments --run-name "my-training-run"
```

**Python:**
```python
from qcogclient import ExperimentClient

client = ExperimentClient()
deployments = await client.list_deployments(run_name="my-training-run")

for deployment in deployments['response']:
    print(f"Deployment: {deployment['name']}")
    print(f"  Version: {deployment['version']}")
    print(f"  Status: {deployment['status']}")
```

### Checkpoints for an Experiment

For a given experiment, you can list the checkpoints that were used to create the deployments.

As an example with the CLI, you can list the checkpoints for an experiment:

```bash
qcog experiment list-checkpoints --run-name "my-training-run"
```
and to get a specific checkpoint:

```bash
qcog experiment get-checkpoint --run-name "my-training-run" --checkpoint-name my-checkpoint
```

## Next Steps

After deploying your model:

- **[Run Inferences](running-inferences.md)** - Make predictions with your deployed model