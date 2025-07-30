# Training Runs

This guide covers running QCML models on your datasets.

## Prerequisites

- Access to datasets in your project (see [Dataset Management](dataset-management.md))
- Understanding of available experiments and environments (see [Admin Operations](admin-operations.md))
- Authenticated ExperimentClient (see [Installation](installation.md))

## Overview

To run a training experiment, you need:

1. **An uploaded dataset** - Your training data
2. **An experiment** - A QCML model configuration
3. **Hyperparameters** - Hyperparameters for the QCML models, which have type definitions in the `qcog-types` package
4. **Compute environment** - Hardware specifications

## Discover Available Resources

### List Available Experiments

Find what ML experiments are available using both the CLI and Python client:

**CLI:**
```bash
qcog admin experiment list
```

**Python:**
```python
from qcogclient import AdminClient

client = AdminClient()
experiments = await client.list_experiments()

for exp in experiments['response']:
    print(f"Experiment: {exp['name']}")
    print(f"Description: {exp['description']}")
```

For the purposes of this guide, we'll use the `pytorch-models` experiment. This contains a variety of PyTorch implementations of QCML models,
as well as the ability to configure training runs using familiar PyTorch settings.

### List Available Datasets

Find your uploaded datasets using both the CLI and Python client:

**CLI:**
```bash
qcog project dataset list
```

**Python:**
```python
from qcogclient import ProjectClient

client = ProjectClient()
datasets = await client.list_datasets()

for ds in datasets['response']:
    print(f"Dataset: {ds['name']}")
```

### List Available Environments

Check available compute environments. These environments are used to run your training runs, and can include different hardware configurations and Python package versions.

**CLI:**
```bash
qcog admin environment list
```

Example output:

```rich
✅ Success

📋 Items
└── Item 1
    ├── id: 562ca654-b214-4252-aae7-2bf2d82b8fc5
    ├── name: python3.12
    ├── description: Basic Python environment with no GPU support
    ├── image_id: 6cc759a7-7a35-47a7-953a-02454d9653dd
    ├── created_ts: 2025-05-15T20:05:49.259037Z
    ├── updated_ts: 2025-05-15T20:05:49.259037Z
    └── metadata: None
```

## Configure Hyperparameters

QCML models have type definitions in the `qcog-types` package. These are used to validate and configure your training runs. We supply the type definitions and guidelines for the `pytorch-models` experiment in the `qcog-types` package which you can install with the following command.

For more on the pytorch-models experiment, see the [pytorch-models](pytorch-models.md) guide.

```bash
uv add qcog-types
```

or

```bash
pip install qcog-types
```

### Example: PyTorch Model Configuration

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

# Dataset configuration
total_columns = 78  # Total columns in your dataset
number_of_columns = total_columns - 1  # Exclude target column

# Configure hyperparameters
hyperparameters = GeneralHSModelHyperparameters(
    hsm_model="general",
    epochs=100,
    batch_size=2000,
    seed=24,
    target="target_column_name",  # Your target column, can be a str or list of strs
    device="cuda",  # or "cpu"
    input_operator_count=number_of_columns,
    output_operator_count=1,
    hilbert_space_dims=4,
    complex=True,
    split=0.2,  # Validation split
    
    # Optimizer configuration
    optimizer_config=OptimizerConfig(
        type="Adam",
        default_params={"lr": 0.001},
        group_params=[
            PerGroupOptimizerParams(
                param_name_contains=["input_diag"],
                params={"lr": 1e-4, "weight_decay": 0}
            )
        ]
    ),
    
    # Loss function
    loss_fn_config=LossFunctionConfig(
        type="MSELoss",
        params={}
    ),
    
    # Learning rate scheduler
    scheduler_config=SchedulerConfig(
        type="StepLR",
        params={"step_size": 3, "gamma": 0.5}
    ),
    
    # Early stopping
    early_stopping_config=EarlyStoppingConfig(
        monitor="val_loss",
        patience=3,
        mode="min",
        min_delta=0.0001,
        verbose=True,
        restore_best_weights=True
    ),
    
    # Gradient clipping
    gradient_clipping_config=GradientClippingConfig(
        max_norm=1.0,
        norm_type=2
    )
)
```

## Run Training Experiment

### Basic Training Run

```python
from qcogclient import ExperimentClient

client = ExperimentClient()

result = await client.run_experiment(
    name="my-training-run",
    description="Training run for a dataset with CUDA",
    experiment_name="pytorch-models",  # From available experiments
    dataset_name="my-dataset",      # From your datasets
    environment_name="py3.12-cuda",    # From available environments
    parameters={
        "hyperparameters": hyperparameters,
        "cpu_count": 4,
        "memory": 1024 * 6,    # 6GB RAM
        "timeout": 3600 * 24,  # 24 hours max
        "gpu_type": "T4"       # GPU specification
    }
)

if 'response' in result:
    print(f"Training started: {result['response']['run_id']}")
else:
    print(f"Failed to start training: {result['error']}")
```

### Resource Configuration

Configure compute resources based on your training requirements:

- **`cpu_count`**: Number of CPU cores
- **`memory`**: Memory in MB 
- **`timeout`**: Maximum runtime in seconds
- **`gpu_type`**: GPU specification (T4, V100, A100)
- **`disk_size`**: Disk space in MB (optional)


### GPU Types

Available GPU options:

- **T4** - Good for most workflows
- **L4** - Good for most workflows
- **A10G** - Faster training, higher memory
- **A100-40GB** - Fastest training, higher memory
- **A100-80GB** - Fastest training, highest memory

## Monitor Training Progress

### Check Training Status

It's important to note that the result has its own response field, with status, metrics, and errors.

**Python:**
```python
from qcogclient import ExperimentClient

client = ExperimentClient()

# Get experiment run details
data = await client.get_experiment_run("training-run-v1")
response = data.get("response")

response.pop("params")

status = response.get("status")
metrics = response.get("metrics")

print(f"Status: {status}")
print(f"Metrics: {metrics}")
```

### Training Status Values

- **`unknown`** - Request not yet processed
- **`pending`** - Waiting to be processed
- **`running`** - Currently training
- **`completed`** - Training finished successfully
- **`failed`** - Training failed with errors

In the case of a failed run, the metrics will contain the error message.

### Understanding Metrics

Completed training runs provide metrics like:

```python
{
    'test_loss': 0.142,
    'best_val_loss': 0.145,
    'avg_epoch_time': 0.54,
    'final_val_loss': 0.145,
    'epochs_completed': 28,
    'final_train_loss': 0.140,
    'val_dataset_size': 5200,
    'train_dataset_size': 20798,
    'total_training_time': 15.2
}
```

## Complete Training Workflow

### End-to-End Example

```python
import os
import asyncio
from qcogclient import ExperimentClient
from qcog_types.pytorch_models.hyperparameters import GeneralHSModelHyperparameters
import dotenv

async def run_complete_training():
    # 1. Setup
    dotenv.load_dotenv()
    client = ExperimentClient()
    
    # 2. Configure hyperparameters
    hyperparameters = GeneralHSModelHyperparameters(
        hsm_model="general",
        epochs=50,
        batch_size=1000,
        target="target_column",
        device="cuda",
        input_operator_count=77,
        output_operator_count=1,
        # ... other parameters
    )
    
    # 3. Start training
    await client.run_experiment(
        name="training-run-v1",
        description="Training run",
        experiment_name="pytorch-models",
        dataset_name="training-dataset",
        environment_name="py3.12-cuda",
        parameters={
            "hyperparameters": hyperparameters,
            "cpu_count": 8,
            "memory": 1024 * 16,  # 16GB
            "timeout": 3600 * 8,  # 8 hours
            "gpu_type": "V100"
        }
    )
    
    run_name = "training-run-v1"
    print(f"Training started: {run_name}")
    
    # 4. Monitor progress
    while True:
        status_result = await client.get_experiment_run(run_name)
        status = status_result['response'].get('status', 'unknown')
        
        print(f"Status: {status}")
        
        if status in ['completed', 'failed']:
            break
            
        # Wait before checking again
        await asyncio.sleep(60)  # Check every minute
    
    # 5. Get final results
    final_result = await client.get_experiment_run(run_name)
    metrics = final_result['response'].get('metrics', {})
    error = final_result['response'].get('error', None)
    
    if error:
        print(f"Training failed: {error}")
    else:
        print(f"Training completed!")
        print(f"Final validation loss: {metrics.get('final_val_loss')}")
        print(f"Training time: {metrics.get('total_training_time')} seconds")
    
    return run_name
```


## Error Handling

### Common Training Errors

```python
async def safe_training_run(name, hyperparameters):
    try:
        await client.run_experiment(
            name=name,
            description="Safe training run",
            experiment_name="pytorch-models",
            dataset_name="my-dataset",
            environment_name="py3.12-cuda",
            parameters={
                "hyperparameters": hyperparameters,
                "cpu_count": 4,
                "memory": 1024 * 8,
                "timeout": 3600 * 4
            }
        )
        # result has its own response field, with status, metrics, and errors
        result = await client.get_experiment_run(name)
        
        if 'error' in result['response']:
            print(f"Training failed: {result['response']['error']}")
            return None
            
        return result['response']
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

### Troubleshooting

#### Out of Memory Errors

- Reduce batch size or increase GPU memory

#### Timeout Issues

- Increase timeout value
- Reduce epochs or dataset size

#### GPU Unavailable

- Check GPU type availability
- Fall back to CPU training

## Best Practices

### Resource Management

- Start with smaller resources and scale up
- Monitor resource usage during training

### Hyperparameter Management

- Keep hyperparameters in version control
- Document parameter choices

## Next Steps

After successful training:

1. **[Deploy Models](model-deployment.md)** - Deploy your trained model
2. **[Run Inferences](running-inferences.md)** - Make predictions
3. **[Manage Long-Running Jobs](long-running-jobs.md)** - Handle extended training
