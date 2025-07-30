# Admin Operations

This guide covers administrative operations using the AdminClient. These operations are used to discover available system resources and check your permissions.

## Prerequisites

- API key with appropriate permissions
- AdminClient configured and authenticated

If you haven't already, you can configure the admin client by following the [authentication guide](authentication.md).

## Overview

Using the `AdminClient`, you can:

- List available experiments
- List available environments  
- Check your permissions

## List Available Environments

View all available compute environments:

**CLI:**

```bash
qcog admin environment list
```

**Python:**

```python
from qcogclient import AdminClient

client = AdminClient()
environments = await client.list_environments()

for env in environments['response']:
    print(f"Environment: {env['name']} - {env['description']}")
```

## List Available Experiments

View all available experiments:

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

## Check Permissions

Check your current permissions and user information:

**CLI:**

```bash
qcog admin whoami
```

This will show you:

- Your user information
- Current permissions
- Associated projects

## Next Steps

After discovering available resources, you can proceed to:

1. **[Manage Datasets](dataset-management.md)** - Upload and manage your training data
2. **[Run Training](training-runs.md)** - Start training experiments
3. **[Deploy Models](model-deployment.md)** - Deploy trained models
