# Qognitive API Client Guide

Welcome to the Qognitive API Client Guide. This comprehensive guide will walk you through using the Qognitive API Client to access QCML and explore its various features.

As a prerequisite, you will need to have a valid API key to access the QCML API. If you don't have one, please contact us at support@qognitive.com to get one.

## 📚 Documentation Structure

This guide is organized into focused sections, each covering specific aspects of the Qognitive API Client:

### Getting Started

- **[Installation & Setup](docs/installation.md)** - Install the client and required dependencies
- **[Authentication](docs/authentication.md)** - Learn different ways to authenticate with the API

### Operations & Workflows

- **[Admin Operations](docs/admin-operations.md)** - Manage projects, users, and API keys
- **[Dataset Management](docs/dataset-management.md)** - Upload and manage your training datasets
- **[Training Runs](docs/training-runs.md)** - Execute machine learning experiments
- **[Model Deployment](docs/model-deployment.md)** - Deploy trained models for inference
- **[Running Inferences](docs/running-inferences.md)** - Run predictions on deployed models
- **[Long-Running Jobs](docs/long-running-jobs.md)** - Manage jobs that exceed standard timeouts

## 🏗️ Client Architecture

The Qognitive client consists of three main components:

- **Admin Client** - Manages system-wide resources and operations not tied to specific projects
- **Project Client** - Handles project-specific resources like datasets and models  
- **Experiment Client** - Manages experiment execution and results

Each client offers both **CLI** and **Python** interfaces for maximum flexibility.

## 🚀 Quick Start

1. **Install the client**: `uv add qcogclient`
2. **Authenticate**: `qcog admin login --api-key <your-api-key>`
3. **Verify setup**: `qcog admin whoami`
4. **Explore**: Follow the guides above for specific operations


## 🆘 Support

For questions, issues, or feature requests:

- **Email**: [support@qognitive.com](mailto:support@qognitive.com)

*Get started by following the [Installation & Setup](docs/installation.md) guide, then explore the specific operations you need for your project.*