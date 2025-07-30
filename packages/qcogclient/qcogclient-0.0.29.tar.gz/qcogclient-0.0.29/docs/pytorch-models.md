# PyTorch Models Guide

This guide covers the available PyTorch models in Qcog, focusing on Hilbert Space Models (HSM) and their configuration options. HSMs are the primary models in the QCML framework.

## Overview

The `pytorch-models` experiment contains a variety of PyTorch implementations of QCML models. We currently support the following models:

### Available Model Types

1. **General HSM**: Uses arbitrary Hermitian operators in a Hilbert space
2. **Pauli HSM**: Expresses the model as a sum of Pauli Strings.
3. **General Full Energy HSM**: Extended version of the General HSM with full energy calculations, meaning that the model minimizes the energy of the system rather than prediction error.

## Model Configuration Structure

All models share a common base configuration structure with model-specific extensions. The configuration is organized into several key components, which are described in more detail below:

- **Model Architecture**: Core model parameters (operators, dimensions)
- **Training Setup**: Epochs, batch size, data splitting
- **Optimization**: Optimizer configuration with support for parameter groups
- **Loss Function**: Configurable loss functions with parameters
- **Learning Rate Scheduling**: Optional scheduler configuration
- **Regularization**: Early stopping and gradient clipping
- **Data Loading**: Worker processes and memory management

## Base Configuration (ModelHyperparameters)

### Core Training Parameters

```python
from qcogclient.qcog.models import ModelHyperparameters, OptimizerConfig, LossFunctionConfig

config = ModelHyperparameters(
    hsm_model="general",  # Choose: "general", "pauli", "general_fullenergy"
    weighted_layer=False,  # Add learnable weights to HSM inputs
    epochs=100,
    batch_size=32,
    split=0.2,  # 20% for test set
    seed=42,  # For reproducibility
    
    # Target and feature configuration
    targets="target_column",  # or ["target1", "target2"] for multi-target
    input_features=None,  # If None, uses all columns except targets
    
    # Device configuration
    device="auto",  # "auto", "cpu", "cuda"
    
    # Data loading
    num_workers=0,  # Number of data loader worker processes
    pin_memory=False,  # CUDA memory pinning
    
    # Required: optimizer and loss function (see sections below)
    optimizer_config=optimizer_config,
    loss_fn_config=loss_config,
)
```

### Key Parameters Explained

- **`weighted_layer`**: When enabled, adds learnable weights to the inputs before the HSM layer, potentially improving model expressiveness
- **`split`**: Fraction of dataset reserved for testing; remaining data is split between training and validation
- **`device="auto"`**: Automatically selects the best available device (CUDA > CPU). Currently MPS is not supported as the compute environment is not available for Mac, and certain PyTorch operations are not supported on MPS.
- **`targets`**: Can be a single string or list of strings for multi-target regression
- **`input_features`**: If specified, only these columns will be used as inputs; targets and inputs cannot overlap

## Optimizer Configuration

### Basic Optimizer Setup

```python
from qcogclient.qcog.models import OptimizerConfig

# Simple optimizer configuration
optimizer_config = OptimizerConfig(
    type="Adam",  # PyTorch optimizer class name
    default_params={
        "lr": 0.001,
        "betas": (0.9, 0.999),
        "weight_decay": 1e-4
    }
)
```

### Advanced: Parameter Groups

Use parameter groups to apply different optimizer settings to different parts of the model.

For general HSM, the parameters are the diagonal elements and upper triangular elements of the input operators. For Pauli HSM, the parameters are the Pauli weights of the input and output operators.

You can supply `param_name_contains` to filter the parameters to apply the optimizer settings to, such as `input_diags`, `input_trius`, `output_diags`, and `output_trius` for GeneralHSM and `input_pauli_coeffs` and `output_pauli_coeffs` for PauliHSM.

```python
from qcogclient.qcog.models import PerGroupOptimizerParams

optimizer_config = OptimizerConfig(
    type="Adam",
    default_params={"lr": 0.001, "weight_decay": 1e-4},
    group_params=[
        # Lower learning rate for upper triangular parameters
        PerGroupOptimizerParams(
            param_name_contains=["input_trius"],
            params={"lr": 1e-4, "weight_decay": 0}
        ),
        # Higher learning rate for operator parameters
        PerGroupOptimizerParams(
            param_name_contains=["input_diags"],
            params={"lr": 0.01}
        )
    ]
)
```

### Supported Optimizers

Any PyTorch optimizer can be used by specifying its class name. We recommend using `"AdamW"` for most cases. As an example, here are some of the optimizers. In principle any PyTorch optimizer can be used, but we recommend using the ones listed here:

- `"Adam"`
- `"AdamW"` (Adam with decoupled weight decay)
- `"SGD"` (Stochastic Gradient Descent)
- `"RMSprop"`

## Loss Function Configuration

We currently support any predefined PyTorch loss functions as defined in the [PyTorch documentation](https://docs.pytorch.org/docs/stable/nn.html#loss-functions).

```python
from qcogclient.qcog.models import LossFunctionConfig

# Regression tasks
loss_config = LossFunctionConfig(
    type="MSELoss",
    params={"reduction": "mean"}
)

# Classification tasks
loss_config = LossFunctionConfig(
    type="CrossEntropyLoss",
    params={"weight": [1.0, 2.0], "label_smoothing": 0.1}
)

```

## Advanced: Learning Rate Scheduling

### Step-based Scheduling

```python
from qcogclient.qcog.models import SchedulerConfig

scheduler_config = SchedulerConfig(
    type="StepLR",
    params={"step_size": 30, "gamma": 0.1},
    interval="epoch"  # "epoch" or "step"
)
```

### Cosine Annealing

```python
scheduler_config = SchedulerConfig(
    type="CosineAnnealingLR",
    params={"T_max": 100, "eta_min": 1e-6},
    interval="epoch"
)
```

### Adaptive Scheduling

```python
scheduler_config = SchedulerConfig(
    type="ReduceLROnPlateau",
    params={
        "monitor": "val_loss",
        "patience": 5,
        "factor": 0.5,
        "min_lr": 1e-6
    },
    interval="epoch"
)
```

## Advanced: Regularization Techniques

### Early Stopping

Prevent overfitting by monitoring validation metrics.

```python
from qcogclient.qcog.models import EarlyStoppingConfig

early_stopping_config = EarlyStoppingConfig(
    monitor="val_loss",  # Metric to monitor
    min_delta=0.0001,   # Minimum improvement threshold
    patience=10,        # Epochs to wait before stopping
    mode="min",         # "min" for loss, "max" for accuracy
    verbose=True,
    restore_best_weights=True  # Restore best model weights
)
```

### Gradient Clipping

Prevent gradient explosion.

```python
from qcogclient.qcog.models import GradientClippingConfig

gradient_clipping_config = GradientClippingConfig(
    max_norm=1.0,      # Maximum gradient norm
    norm_type=2.0      # L2 norm (2.0) or infinity norm (float('inf'))
)
```

## General HSM

The General HSM uses arbitrary Hermitian operators in a Hilbert space, providing maximum flexibility.

### Configuration

```python
from qcog_types.pytorch_models.hyperparameters import GeneralHSModelHyperparameters

config = GeneralHSModelHyperparameters(
    # Model type
    hsm_model="general",  # or "general_fullenergy"
    
    # Architecture parameters
    input_operator_count=10,    # Number of input features, must match the number of input features in your dataset
    output_operator_count=1,    # Number of output targets, must match the number of target variables
    hilbert_space_dims=16,      # Dimension of Hilbert space, larger dimensions allow more complex representations but increase computational cost. Each operator is a dxd matrix.
    
    # Quantum parameters
    beta=None,          # Mixing parameter (None = use lowest eigenvalue)
    complex=True,       # Use complex-valued operators (recommended)
    eigh_eps=1e-8,     # Numerical stability for eigenvalue decomposition
    
    # Standard training parameters
    epochs=100,
    batch_size=32,
    targets=["my_target"],
    
    # Required configurations
    optimizer_config=optimizer_config,
    loss_fn_config=loss_config,
)
```

- **`input_operator_count`**: Must match the number of input features in your dataset
- **`output_operator_count`**: Must match the number of target variables
- **`hilbert_space_dims`**: Larger dimensions allow more complex representations but increase computational cost
- **`beta`**: Controls how ground states are computed; None uses the standard lowest eigenvalue approach
- **`complex=True`**: Complex operators generally provide better expressiveness than real-valued ones
- **`eigh_eps`**: Small value added to matrix diagonal for numerical stability during eigenvalue decomposition

### Model Variants

- **`"general"`**: Standard General HSM
- **`"general_fullenergy"`**: Extended version with full energy calculations (more computationally intensive but potentially more accurate)

## Pauli Hilbert Space Model

The Pauli HSM represents the model as a sum of Pauli Strings. The model learns the coefficients for this weighted sum. Here is an example configuration:

```python
from qcog_types.pytorch_models.hyperparameters import PauliHSModelHyperparameters

config = PauliHSModelHyperparameters(
    # Model type
    hsm_model="pauli",
    
    # Architecture parameters
    input_operator_count=10,     # Number of input features
    output_operator_count=1,     # Number of output targets
    qubits_count=5,             # Number of qubits (Hilbert space = 2^qubits_count)
    
    # Pauli operator constraints
    input_operator_pauli_weight=2,   # Max non-identity Paulis in input operators
    output_operator_pauli_weight=3,  # Max non-identity Paulis in output operators
    
    # Numerical parameters
    eigh_eps=1e-8,
    
    # Standard training parameters
    epochs=100,
    batch_size=32,
    targets=["my_target"],
    
    # Required configurations
    optimizer_config=optimizer_config,
    loss_fn_config=loss_config,
)
```

### Parameters Explained

- **`qubits_count`**: Determines the Hilbert space dimension (2^qubits_count). More qubits = more expressive model but higher computational cost
- **`input_operator_pauli_weight`**: Limits the complexity of input operators by restricting the number of non-identity Pauli matrices. Must be less than or equal to the number of qubits.
- **`output_operator_pauli_weight`**: Similar constraint for output operators. Must be less than or equal to the number of qubits.

## Complete Configuration Example

Here's a complete example combining all components. This example assumes an existing dataset.

```python
from qcog_types.pytorch_models.hyperparameters import GeneralHSModelHyperparameters
from qcogclient.qcog.models import (
    GeneralHSModelHyperparameters,
    OptimizerConfig,
    LossFunctionConfig,
    EarlyStoppingConfig,
    GradientClippingConfig
)

import os
from qcog_types.pytorch_models.hyperparameters import GeneralHSModelHyperparameters, OptimizerConfig, PerGroupOptimizerParams, LossFunctionConfig, SchedulerConfig, EarlyStoppingConfig, GradientClippingConfig
import dotenv

dotenv.load_dotenv()

api_key = os.getenv("API_KEY", None)

total_columns = 78
number_of_columns = total_columns - 1
number_of_targets = 1

# Define all configurations
optimizer_config = OptimizerConfig(
    type="Adam",
    default_params={"lr": 0.001, "weight_decay": 1e-4}
)

loss_config = LossFunctionConfig(
    type="MSELoss",
    params={"reduction": "mean"}
)

scheduler_config = SchedulerConfig(
    type="CosineAnnealingLR",
    params={"T_max": 100},
    interval="epoch"
)

early_stopping_config = EarlyStoppingConfig(
    monitor="val_loss",
    patience=15,
    restore_best_weights=True
)

gradient_clipping_config = GradientClippingConfig(
    max_norm=1.0,
    norm_type=2.0
)

# Complete model configuration
config = GeneralHSModelHyperparameters(
    hsm_model="general",
    weighted_layer=True,
    
    # Architecture
    input_operator_count=number_of_columns,
    output_operator_count=number_of_targets,
    hilbert_space_dims=32,
    complex=True,
    
    # Training
    epochs=200,
    batch_size=64,
    split=0.2,
    seed=42,
    
    # Data specification
    targets=["target_value"],
    input_features=None,  # Use all features except targets
    
    # Device and data loading
    device="auto",
    num_workers=4,
    pin_memory=True,
    
    # Training configuration
    optimizer_config=optimizer_config,
    loss_fn_config=loss_config,
    scheduler_config=scheduler_config,
    early_stopping_config=early_stopping_config,
    gradient_clipping_config=gradient_clipping_config,
)

from qcogclient import ExperimentClient

client = ExperimentClient(
    api_key=api_key,
)

await client.run_experiment(
    "my-dataset-training",
    "Training run for a dataset with CUDA",
    experiment_name="pytorch-models",
    dataset_name="my-dataset",
    environment_name="py3.12-cuda",
    parameters={
        "hyperparameters": config,
        "cpu_count": 4,
        "memory": 1024 * 6, # 6GB
        "timeout": 3600 * 24, # 24 hours is the maximum
        "gpu_type": "T4"
    },
)


```

## Best Practices

### Model Selection

1. **Start with General HSM** for most tasks - it's the most flexible
2. **Try `weighted_layer=True`** for improved performance on complex datasets

### Hyperparameter Tuning

1. **Hilbert Space Dimensions**: Start with 4-16 for General HSM, increase if needed
2. **Batch Size**: Batch sizes depend on the hilbert space dimension and GPU instances.

### Computational Considerations

1. **Memory Usage**: Scales as O(d²) where d is the Hilbert space dimension
2. **GPU Usage**: QCML models benefit significantly from GPU acceleration

### Monitoring Training

- Watch validation loss for overfitting
- Use early stopping to prevent overtraining
- Monitor gradient norms - clip if they become too large
- For Pauli models, start with low Pauli weights and increase if needed

## Troubleshooting

### Common Issues

1. **Memory Errors**: Reduce `hilbert_space_dims` or `batch_size`
2. **Slow Training**: Use GPU (`device="cuda"`), increase `num_workers`
3. **Poor Convergence**: Try different learning rates, add gradient clipping
4. **Overfitting**: Enable early stopping, add weight decay, reduce model complexity

### Validation Errors

- **Operator count mismatch**: Ensure `input_operator_count` matches your feature count
- **Target mismatch**: Verify `output_operator_count` equals the number of targets
- **Device errors**: Check CUDA availability if using `device="cuda"`

For more advanced usage and integration with experiments, see the [Training Runs](training-runs.md) guide.
