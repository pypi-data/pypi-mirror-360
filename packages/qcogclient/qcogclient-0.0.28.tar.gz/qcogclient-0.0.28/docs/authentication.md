# Authentication

This guide covers the different ways to authenticate with the Qognitive API.

## Overview

The Qognitive API uses API keys for authentication. You can authenticate using the following methods:

1. **CLI Login** - Store credentials locally for CLI and Python use
2. **Environment Variables** - Use environment variables for configuration
3. **Direct API Key** - Pass API key directly in Python code

## CLI Authentication

### Login Command

Store your API key locally:

```bash
qcog admin login --api-key <your-api-key>
```

**Important**: This operation saves the API key **unencrypted** on your local machine.

### Benefits
- Convenient for interactive use
- Works with both CLI and Python interfaces
- No need to pass API key repeatedly

## Python Authentication

### Method 1: Using Stored Credentials

If you've already logged in via CLI:

```python
from qcogclient import AdminClient

# Uses previously saved API key from CLI login
admin_client = AdminClient()
```

### Method 2: Environment Variables

Use environment variables for configuration:

```bash
export QCOG_API_KEY="your-api-key"
```

```python
import os
from qcogclient import AdminClient

admin_client = AdminClient(api_key=os.getenv("QCOG_API_KEY"))
```

or load from a `.env` file (recommended):

```python
import os
import dotenv
from qcogclient import AdminClient

# Load API key from .env file
dotenv.load_dotenv()

admin_client = AdminClient(api_key=os.getenv("QCOG_API_KEY"))
```

### Method 3: Direct API Key

Pass the API key directly, although we strongly recommend using the environment variables method for scripts or loading from a `.env`file.

```python
from qcogclient import AdminClient

# Pass API key directly (not recommended, use environment variables instead)
admin_client = AdminClient(api_key="your-api-key")
```

## Client Types

Each of the other client types can be authenticated using the same methods:

```python
import os
from qcogclient import AdminClient, ProjectClient, ExperimentClient

# All support the same authentication options
API_KEY = os.getenv("QCOG_API_KEY")
admin_client = AdminClient(api_key=API_KEY)
project_client = ProjectClient(api_key=API_KEY)
experiment_client = ExperimentClient(api_key=API_KEY)
```

## Verify Credentials

Once you've configured your authentication, verify that everything is working correctly.

### CLI Verification

```bash
qcog admin whoami
```

### Python Verification

```python
from qcogclient import AdminClient

client = AdminClient()
result = await client.whoami()

if 'response' in result:
    user_data = result['response']
    print(f"✅ Connected as: {user_data['user_name']}")
    print(f"Project: {user_data.get('project_name', 'No project set')}")
else:
    print(f"❌ Authentication failed: {result['error']}")
```

## Understanding the Response

### What `whoami` Returns

The `whoami` command provides comprehensive information about your access:

| Field | Description |
|-------|-------------|
| **User Details** | `user_id`, `user_name` - Your account information |
| **System Permissions** | What system-level operations you can perform |
| **Current Project** | Project you're currently associated with |
| **Project Permissions** | Your permissions within the project (read, write, delete datasets, etc.) |
| **Available Datasets** | Datasets you have access to |

### Example Response

```json
{
    "response": {
        "user_id": "fa72b94a-f651-4663-a35b-5633b642d254",
        "user_name": "john.doe",
        "project_id": "90a7a84e-895b-4adc-a80f-577344dd1391", 
        "project_name": "my-project",
        "system_permissions": ["system.read"],
        "project_permissions": ["project.admin", "dataset.read", "run.write"],
        "datasets": [
            {
                "id": "dataset-id",
                "name": "my-dataset",
                "description": "Training data"
            }
        ]
    }
}
```

## Handling API Responses

### Response Structure

All Python API calls return a consistent structure:

```python
# Success response
{
    "response": {
        # Actual data here
    }
}

# Error response  
{
    "error": "Error message describing what went wrong"
}
```

### Best Practice Pattern

Use this pattern for robust error handling:

```python
async def safe_api_call():
    try:
        result = await client.whoami()
        
        if 'response' in result:
            # Success - process the data
            data = result['response']
            return data
        else:
            # API returned an error
            print(f"API Error: {result['error']}")
            return None
            
    except Exception as e:
        # Network or other unexpected error
        print(f"Unexpected error: {e}")
        return None
```

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** in production
3. **Rotate keys regularly** if supported
4. **Use project-specific keys** when possible
5. **Store keys securely** in production environments

## Troubleshooting

### Common Authentication Issues

**Invalid API Key**
```
Error: Authentication failed
```
- Double-check your API key
- Ensure no extra spaces or characters
- Verify the key hasn't expired

**Connection Refused**
```
Error: Connection refused
```
- Check your internet connection
- Verify the base URL is correct
- For local development, ensure the server is running

**Permission Denied**
```
Error: Insufficient permissions
```
- Check your user permissions with `whoami`
- Contact your administrator for access
- Ensure you're using the correct project API key

## Next Steps

Once authenticated:

1. **[Explore Admin Operations](admin-operations.md)** - Manage projects and users
2. **[Upload Datasets](dataset-management.md)** - Start working with data
3. **[Run Training Jobs](training-runs.md)** - Execute experiments 