# Installation & Setup

This guide covers installing the Qognitive API Client and setting up your development environment.

## Prerequisites

- Python 3.8 or higher
- `uv` package manager (recommended) or `pip`
- A valid Qognitive API key

## Installing the Client

### Using UV (Recommended)

```bash
# using the uv add command
uv add qcogclient
# or using the uv pip command
uv pip install qcogclient
```

### Using Pip

```bash
pip install qcogclient
```

## Optional Dependencies

### Hyperparameter Types

For enhanced type support when working with hyperparameters:

```bash
uv add qcog-types
```

This package provides type definitions for hyperparameters used in various experiments, enabling better IDE support and validation.

## Verify Installation

Check that the client is installed correctly:

```bash
qcog --version
```

You should see output similar to:
```
qcog version 0.0.22
```

## Local Development

For developers working against a local Qognitive server, see the **[Local Development Setup](local-development.md)** guide for detailed instructions on:

- Environment configuration
- Client setup for local servers
- API key generation
- Troubleshooting local issues

## Troubleshooting

### Common Issues

**ImportError: No module named 'qcogclient'**
- Ensure you've installed the package: `uv add qcogclient`
- Check your Python environment is activated

**Connection errors**
- Verify your API key is correct
- Check your network connection
- For local development, ensure the local server is running

**Version compatibility**
- Ensure you have version 0.0.22 or higher
- Update if needed: `uv add qcogclient --upgrade`

## Next Steps

Once you have the client installed:

1. **[Set up authentication](authentication.md)** - Configure your API credentials
2. **[Manage datasets](dataset-management.md)** - Upload and manage your datasets
3. TODO: Add more guides here

## Environment Variables Reference

For convenient configuration, you can set these environment variables:

```bash
export QCOG_API_KEY="your_api_key"
```
