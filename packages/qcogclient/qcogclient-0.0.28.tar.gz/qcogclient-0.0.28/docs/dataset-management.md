# Dataset Management

This guide covers how to manage datasets in your Qcog project, including loading local datasets, uploading them to the platform, and creating references to remote datasets.

## Overview

Qcog supports two main approaches for dataset management:

1. **Direct Upload**: Load and upload datasets directly from your local environment
2. **Remote References**: Create references to datasets stored in external locations (e.g., S3 buckets)

## Loading Local Datasets

### Using CSV Files

You can load CSV files using the `load_csv` adapter, which also extracts metadata about your dataset:

```python
from qcogclient import ProjectClient
from qcogclient.qcog.adapters import load_csv

# Load a CSV file and extract metadata
loaded_dataset = load_csv("/path/to/your/dataset.csv")

# The adapter extracts useful information:
number_of_cols = loaded_dataset['number_of_columns']  # Used for model input operators
number_of_rows = loaded_dataset['number_of_rows']
```

## Direct Dataset Upload

### Uploading to the Platform

Once you've loaded a dataset, you can upload it directly to the Qcog platform:

```python
client = ProjectClient()

await client.upload_dataset(
    file=loaded_dataset['file'],
    name="my-dataset",
    description="Description of your dataset",
    override=True,  # Set to True to overwrite existing datasets with the same name
    chunk_size=1024 * 1024 * 128  # 128MB chunks
)
```

### Upload Considerations

- **Large Datasets**: This operation can take considerable time for large datasets
- **Chunk Size**: Increase the `chunk_size` parameter for more efficient uploads of large files
- **Override**: Use `override=True` to replace existing datasets with the same name

## Remote Dataset References

### Creating References to External Storage

For large datasets or those already stored in cloud storage, you can create references instead of uploading directly.

```python
from qcogclient import ProjectClient

client = ProjectClient()

await client.create_dataset(
    name="my-remote-dataset",
    dataset_location="s3://your-bucket/path/to/dataset.csv",
    dataset_format="csv",
    credentials={
        "AWS_ACCESS_KEY_ID": "your-access-key-id",
        "AWS_SECRET_ACCESS_KEY": "your-secret-access-key",
        "AWS_REGION": "your-aws-region",
    }
)
```

**NOTE**: Currently, only CSV uploads and external S3 buckets are supported.

## Managing Datasets

### Listing Available Datasets

To view all datasets in your project:

```bash
qcog project dataset list
```

This command will show both uploaded datasets and remote dataset references.

Once you have a dataset, you can use it in your experiments. See the [Training Runs](training-runs.md) guide for more information on how to train models.
