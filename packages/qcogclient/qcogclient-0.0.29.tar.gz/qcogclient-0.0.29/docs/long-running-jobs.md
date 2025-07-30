# Long-Running Jobs

This guide covers managing jobs that exceed the standard 24-hour timeout limit using the Qognitive platform.

## Prerequisites

- Authenticated ExperimentClient  
- Understanding of training parameters and resource requirements

## Overview

Long-running jobs are designed for training runs that need more than 24 hours to complete. The **key mechanism** for extending runtime is the `retries` parameter, which allows jobs to automatically restart and continue training beyond the 24-hour limit.

### How Retries Work

The platform handles extended training through automatic retries:

- Each job attempt has a maximum 24-hour timeout
- The `retries` parameter specifies how many additional attempts after the first
- Total possible runtime = `timeout × (1 + retries)`

**Examples:**

- `timeout: 24 hours, retries: 0` = 24 hours maximum
- `timeout: 24 hours, retries: 2` = 72 hours maximum (3 days)
- `timeout: 24 hours, retries: 3` = 96 hours maximum (4 days)

## Configuration

### Basic Setup

```python
import dotenv
import os
from qcogclient import ExperimentClient

dotenv.load_dotenv()

api_key = os.getenv("QCOG_API_KEY")

client = ExperimentClient(api_key=api_key)
```

### Hyperparameters Configuration

```python
from qcog_types.pytorch_models.hyperparameters import (
    GeneralHSModelHyperparameters,
    OptimizerConfig,
    PerGroupOptimizerParams,
    LossFunctionConfig,
    SchedulerConfig,
    EarlyStoppingConfig,
    GradientClippingConfig
)

total_columns = 78
number_of_columns = total_columns - 1

hyperparameters = GeneralHSModelHyperparameters(
    hsm_model="general",
    epochs=100,
    batch_size=2000,
    seed=24,
    target="scaled_demedian_forward_return_22d",
    device="cpu",
    input_operator_count=number_of_columns,
    output_operator_count=1,
    hilbert_space_dims=4,
    complex=True,
    split=0.2,
    optimizer_config=OptimizerConfig(
        type="Adam",
        default_params={
            "lr": 0.001,
        },
        group_params=[
            PerGroupOptimizerParams(
                param_name_contains=["input_diag"],
                params={"lr": 1e-4, "weight_decay": 0}
            )
        ]
    ),
    loss_fn_config=LossFunctionConfig(
        type="MSELoss",
        params={}
    ),
    scheduler_config=SchedulerConfig(
        type="StepLR",
        params={
            "step_size": 3,
            "gamma": 0.5,
        }
    ),
    early_stopping_config=EarlyStoppingConfig(
        monitor="val_loss",
        patience=3,
        mode="min",
        min_delta=0.0001,
        verbose=True,
        restore_best_weights=True
    ),
    gradient_clipping_config=GradientClippingConfig(
        max_norm=1.0,
        norm_type=2
    ),
)
```

### Submit Long-Running Job

```python
await client.run_experiment(
    "long-running-job",
    "This is a long running job",
    experiment_name="pytorch-models",
    dataset_name="training-dat  ",
    instance="cpu",
    parameters={
        "hyperparameters": hyperparameters,
        "cpu_count": 4,
        "memory": 16384,
        "timeout": 3600 * 24,  # 24 hours
        "retries": 3,  # This will run for 3 days
    },
    local_webhook_url=None  # Set ngrok URL for local development
)
```

### Key Parameters

- **`timeout`**: Maximum time per attempt (24 hours = `3600 * 24`)
- **`retries`**: Number of additional attempts after the first (3 = 4 total attempts)
- **Total runtime**: 4 days maximum (4 attempts × 24 hours each)

## Monitoring

### Check Job Status

```python
response = await client.get_experiment_run("long-running-job")

response = response.get("response")
status = response.get("status")
metrics = response.get("metrics")
error = response.get("errors")

print(status)
print(metrics)
print(error)
```

### Job Status Values

- **`pending`** - Waiting to start
- **`running`** - Currently executing  
- **`completed`** - Finished successfully
- **`failed`** - Failed after all retries

## Next Steps

After successful long-running training:

1. **[Deploy Models](model-deployment.md)** - Deploy your trained models
2. **[Run Inferences](running-inferences.md)** - Make predictions with deployed models 