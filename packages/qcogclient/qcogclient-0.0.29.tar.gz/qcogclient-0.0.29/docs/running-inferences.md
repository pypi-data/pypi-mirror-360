# Running Inferences

This guide covers how to run inferences using deployed QCML models.

**Note**: The inference API is still in development.

## Prerequisites

To run inferences, you need:

- **A deployment name** - The deployed model endpoint (see [Model Deployment](model-deployment.md) for more information)
- **An experiment run name** - The training run that the deployment is associated with (see [Training Runs](training-runs.md) for more information)
- **A dataset** - Data to run predictions on (see [Dataset Management](dataset-management.md) for more information)

## Find Available Deployments

If you don't remember the deployment name, you can search for it using the CLI:

```bash
qcog experiment list-deployments --run-name <run-name>
```

For example, to find deployments for a specific training run:

```bash
qcog experiment list-deployments --run-name training-run-v1
```

## Running Synchronous Inference

### Basic Setup

```python
from qcogclient import ExperimentClient
from pathlib import Path
import dotenv
import os

dotenv.load_dotenv() # Load environment variables from .env file

api_key = os.getenv("QCOG_API_KEY")

experiment_client = ExperimentClient(api_key=api_key)
```

### Run Inference

This is an example of running synchronous inference. By synchronous, we mean that the inference request will block until the inference is complete.

```python
# Path to your inference dataset
test_inference_dataset = Path("./test-inference.csv")

# Run synchronous inference
# This method runs the inferences on the deployment synchronously 
# and returns the predictions
predictions = await experiment_client.sync_inference(
    dataset=test_inference_dataset,
    deployment_name="sample-inference",
    run_name="training-run-v1",
)

print(predictions)
```

There you go! You've run your first inference.
