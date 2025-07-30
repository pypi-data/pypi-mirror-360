# ModelHub SDK

ModelHub SDK is a powerful tool for orchestrating and managing machine learning workflows, experiments, datasets, and deployments on Kubernetes. It integrates seamlessly with MLflow and supports custom pipelines, dataset management, model logging, and serving through Kserve.

**🚀 New in Latest Version:** The SDK now uses **autonomize-core** as its foundation, providing enhanced authentication, improved HTTP client management, comprehensive exception handling, and better SSL certificate support.

![Python Version](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![MLflow Version](https://img.shields.io/badge/MLflow-2.21.2-blue?style=for-the-badge&logo=mlflow)
![PyPI Version](https://img.shields.io/pypi/v/autonomize-model-sdk?style=for-the-badge&logo=pypi)
![Code Formatter](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)
![Code Linter](https://img.shields.io/badge/linting-pylint-green.svg?style=for-the-badge)
![Code Checker](https://img.shields.io/badge/mypy-checked-blue?style=for-the-badge)
![Code Coverage](https://img.shields.io/badge/coverage-96%25-a4a523?style=for-the-badge&logo=codecov)

## Table of Contents

- [ModelHub SDK](#modelhub-sdk)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Environment Setup](#environment-setup)
  - [CLI Tool](#cli-tool)
  - [Quickstart](#quickstart)
  - [Experiments and Runs](#experiments-and-runs)
    - [Logging Parameters and Metrics](#logging-parameters-and-metrics)
    - [Artifact Management](#artifact-management)
  - [Pipeline Management](#pipeline-management)
    - [Basic Pipeline](#basic-pipeline)
    - [Running a Pipeline](#running-a-pipeline)
    - [Advanced Configuration](#advanced-configuration)
  - [Dataset Management](#dataset-management)
    - [Loading Datasets](#loading-datasets)
    - [Using Blob Storage for Dataset](#using-blob-storage-for-dataset)
  - [Model Deployment through KServe](#model-deployment-through-kserve)
    - [Create a model wrapper:](#create-a-model-wrapper)
    - [Serve models with ModelHub:](#serve-models-with-modelhub)
    - [Deploy with KServe:](#deploy-with-kserve)
  - [Examples](#examples)
    - [Training Pipeline with Multiple Stages](#training-pipeline-with-multiple-stages)
    - [Dataset Version Management](#dataset-version-management)
- [InferenceClient](#inferenceclient)
  - [Installation](#installation-1)
  - [Authentication](#authentication)
  - [Text Inference](#text-inference)
  - [File Inference](#file-inference)
    - [Local File Path](#local-file-path)
    - [File Object](#file-object)
    - [URL](#url)
    - [Signed URL from Cloud Storage](#signed-url-from-cloud-storage)
  - [Response Format](#response-format)
  - [Error Handling](#error-handling)
  - [Additional Features](#additional-features)
  - [Async Support](#async-support)
- [Prompt Management](#prompt-management)
  - [Features](#features)
  - [Installation](#installation-2)
  - [Basic Usage](#basic-usage)
  - [Loading and Using Prompts with AutoRAG](#loading-and-using-prompts-with-autorag)
  - [Managing Prompt Versions](#managing-prompt-versions)
  - [Evaluating Prompts with AutoRAG](#evaluating-prompts-with-autorag)
- [ML Monitoring](#model-monitoring-and-evaluation)
  - [LLL](#llm-monitoring)
  - [Traditional Model Monitoring](#traditional-ml-monitoring)
- [Migration Guide](#migration-guide)

## Installation

To install the ModelHub SDK, simply run:

```bash
pip install autonomize-model-sdk
```

### Optional Dependencies

The SDK uses a modular dependency structure, allowing you to install only what you need:

```bash
# Install with core functionality (base, mlflow, pipeline, datasets)
pip install "autonomize-model-sdk[core]"

# Install with monitoring capabilities
pip install "autonomize-model-sdk[monitoring]"

# Install with serving capabilities
pip install "autonomize-model-sdk[serving]"

# Install with Azure integration
pip install "autonomize-model-sdk[azure]"

# Install the full package with all dependencies
pip install "autonomize-model-sdk[full]"

# Install for specific use cases
pip install "autonomize-model-sdk[data-science]"
pip install "autonomize-model-sdk[deployment]"
```

## What's New: autonomize-core Integration

The ModelHub SDK has been enhanced with **autonomize-core**, providing a more robust and feature-rich foundation:

### 🔧 **Core Improvements**
- **Enhanced HTTP Client**: Built on `httpx` for better async support and connection management
- **Comprehensive Exception Handling**: Detailed error types for better debugging and error handling
- **Improved Authentication**: More secure and flexible credential management
- **Better Logging**: Centralized logging system with configurable levels
- **SSL Certificate Support**: Custom certificate handling for enterprise environments

### 🚀 **Key Features**
- **Backward Compatibility**: All existing code continues to work without changes
- **New Environment Variables**: Cleaner, more consistent naming (with backward compatibility)
- **SSL Verification Control**: Support for custom certificates and SSL configuration
- **Better Error Messages**: More descriptive error messages for troubleshooting
- **Performance Improvements**: Optimized HTTP client and connection pooling

### 📦 **Dependencies**
The integration brings the autonomize-core package as a dependency, which includes:
- Modern HTTP client (`httpx`)
- Comprehensive exception handling
- Advanced credential management
- SSL certificate support
- Structured logging

## Environment Setup

### New Preferred Environment Variables (autonomize-core)

We recommend using the new environment variable names for better consistency and clarity:

```bash
export MODELHUB_URI=https://your-modelhub.com
export MODELHUB_AUTH_CLIENT_ID=your_client_id
export MODELHUB_AUTH_CLIENT_SECRET=your_secret
export GENESIS_CLIENT_ID=your_genesis_client
export GENESIS_COPILOT_ID=your_copilot
export MLFLOW_EXPERIMENT_ID=your_experiment_id
```

### Legacy Environment Variables (Backward Compatibility)

The following environment variables are still supported for backward compatibility:

```bash
export MODELHUB_BASE_URL=https://your-modelhub.com
export MODELHUB_CLIENT_ID=your_client_id
export MODELHUB_CLIENT_SECRET=your_secret
export CLIENT_ID=your_client
export COPILOT_ID=your_copilot
export MLFLOW_EXPERIMENT_ID=your_experiment_id
```

### SSL Certificate Configuration

The SDK now supports custom SSL certificate verification through the `verify_ssl` parameter. This is useful when working with self-signed certificates or custom certificate authorities:

```python
from modelhub.core import ModelhubCredential

# Disable SSL verification (not recommended for production)
credential = ModelhubCredential(
    modelhub_url="https://your-modelhub.com",
    client_id="your_client_id",
    client_secret="your_client_secret",
    verify_ssl=False
)

# Use custom certificate bundle
credential = ModelhubCredential(
    modelhub_url="https://your-modelhub.com",
    client_id="your_client_id",
    client_secret="your_client_secret",
    verify_ssl="/path/to/your/certificate.pem"
)
```

### Environment File Configuration

Alternatively, create a `.env` file in your project directory and add the environment variables:

```bash
# .env file
MODELHUB_URI=https://your-modelhub.com
MODELHUB_AUTH_CLIENT_ID=your_client_id
MODELHUB_AUTH_CLIENT_SECRET=your_secret
GENESIS_CLIENT_ID=your_genesis_client
GENESIS_COPILOT_ID=your_copilot
MLFLOW_EXPERIMENT_ID=your_experiment_id
```

## CLI Tool

The ModelHub SDK includes a command-line interface for managing ML pipelines:

```bash
# Start a pipeline in local mode (with local scripts)
pipeline start -f pipeline.yaml --mode local --pyproject pyproject.toml

# Start a pipeline in CI/CD mode (using container)
pipeline start -f pipeline.yaml --mode cicd
```

CLI Options:

- `-f, --file`: Path to pipeline YAML file (default: pipeline.yaml)
- `--mode`: Execution mode ('local' or 'cicd')
  - local: Runs with local scripts and installs dependencies using Poetry
  - cicd: Uses container image with pre-installed dependencies
- `--pyproject`: Path to pyproject.toml file (required for local mode)

## Quickstart

The ModelHub SDK allows you to easily log experiments, manage pipelines, and use datasets.

Here's a quick example of how to initialize the client and log a run:

### Basic Usage

```python
from modelhub.core import ModelhubCredential
from modelhub.clients import MLflowClient

# Initialize the credential
credential = ModelhubCredential(
    modelhub_url="https://your-modelhub.com",
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Initialize the MLflow client with the credential
client = MLflowClient(
    credential=credential,
    client_id="your_client_id",
    copilot_id="your_copilot_id"
)

experiment_id = "your_experiment_id"
client.set_experiment(experiment_id=experiment_id)

# Start an MLflow run
with client.start_run(run_name="my_experiment_run"):
    client.mlflow.log_param("param1", "value1")
    client.mlflow.log_metric("accuracy", 0.85)
    client.mlflow.log_artifact("model.pkl")
```

### Advanced Usage with SSL Configuration

```python
from modelhub.core import ModelhubCredential
from modelhub.clients import MLflowClient

# Initialize with custom SSL configuration
credential = ModelhubCredential(
    modelhub_url="https://your-modelhub.com",
    client_id="your_client_id",
    client_secret="your_client_secret",
    verify_ssl="/path/to/custom/certificate.pem"  # or False to disable
)

# The rest remains the same
client = MLflowClient(
    credential=credential,
    client_id="your_client_id",
    copilot_id="your_copilot_id"
)
```

### Using Environment Variables

```python
from modelhub.core import ModelhubCredential
from modelhub.clients import MLflowClient

# Credentials will be loaded from environment variables automatically
# MODELHUB_URI, MODELHUB_AUTH_CLIENT_ID, MODELHUB_AUTH_CLIENT_SECRET
credential = ModelhubCredential()

# Client IDs will be loaded from GENESIS_CLIENT_ID, GENESIS_COPILOT_ID
client = MLflowClient(credential=credential)
```

## Experiments and Runs

ModelHub SDK provides an easy way to interact with MLflow for managing experiments and runs.

### Logging Parameters and Metrics

To log parameters, metrics, and artifacts:

```python
with client.start_run(run_name="my_run"):
    # Log parameters
    client.mlflow.log_param("learning_rate", 0.01)

    # Log metrics
    client.mlflow.log_metric("accuracy", 0.92)
    client.mlflow.log_metric("precision", 0.88)

    # Log artifacts
    client.mlflow.log_artifact("/path/to/model.pkl")
```

### Artifact Management

You can log or download artifacts with ease:

```python
# Log artifact
client.mlflow.log_artifact("/path/to/file.csv")

# Download artifact
client.mlflow.artifacts.download_artifacts(run_id="run_id_here", artifact_path="artifact.csv", dst_path="/tmp")
```

## Pipeline Management

ModelHub SDK enables users to define, manage, and run multi-stage pipelines that automate your machine learning workflow. You can define pipelines in YAML and submit them using the SDK.

### Basic Pipeline

Here's a simple pipeline example:

```yaml
name: "Simple Pipeline"
description: "Basic ML pipeline"
experiment_id: "123"
image_tag: "my-image:1.0.0"
stages:
  - name: train
    type: custom
    script: scripts/train.py
```

### Running a Pipeline

Using CLI:

```bash
# Local development
pipeline start -f pipeline.yaml --mode local --pyproject pyproject.toml

# CI/CD environment
pipeline start -f pipeline.yaml --mode cicd
```

Using SDK:

```python
from modelhub.core import ModelhubCredential
from modelhub.clients import PipelineManager

# Initialize the credential
credential = ModelhubCredential(
    modelhub_url="https://your-modelhub.com",
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Initialize the pipeline manager with the credential
pipeline_manager = PipelineManager(
    credential=credential,
    client_id="your_client_id",
    copilot_id="your_copilot_id"
)

# Start the pipeline
pipeline = pipeline_manager.start_pipeline("pipeline.yaml")
```

### Advanced Configuration

For detailed information about pipeline configuration including:

- Resource management (CPU, Memory, GPU)
- Node scheduling with selectors and tolerations
- Blob storage integration
- Stage dependencies
- Advanced examples and best practices

See our [Pipeline Configuration Guide](./PIPELINE.md).

## Dataset Management

ModelHub SDK allows you to load and manage datasets easily, with support for loading data from external storage or datasets managed through the frontend.

### Loading Datasets

To load datasets using the SDK:

```python
from modelhub.core import ModelhubCredential
from modelhub.clients import DatasetClient

# Initialize the credential
credential = ModelhubCredential(
    modelhub_url="https://your-modelhub.com",
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Initialize the dataset client with the credential
dataset_client = DatasetClient(
    credential=credential,
    client_id="your_client_id",
    copilot_id="your_copilot_id"
)

# Load a dataset by name
dataset = dataset_client.load_dataset("my_dataset")

# Load a dataset from a specific directory
dataset = dataset_client.load_dataset("my_dataset", directory="data_folder/")

# Load a specific version and split
dataset = dataset_client.load_dataset("my_dataset", version=2, split="train")
```

### Using Blob Storage for Dataset

```python
# Load dataset from blob storage
dataset = dataset_client.load_dataset(
    "my_dataset",
    blob_storage_config={
        "container": "data",
        "blob_url": "https://storage.blob.core.windows.net",
        "mount_path": "/data"
    }
)
```

## Model Deployment through KServe

Deploy models via KServe after logging them with MLflow:

### Create a model wrapper:

Use the MLflow PythonModel interface to define your model's prediction logic.

```python
import mlflow.pyfunc
import joblib

class ModelWrapper(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        self.model = joblib.load("/path/to/model.pkl")

    def predict(self, context, model_input):
        return self.model.predict(model_input)

# Log the model
client.mlflow.pyfunc.log_model(
    artifact_path="model",
    python_model=ModelWrapper()
)
```

### Serve models with ModelHub:

ModelHub SDK provides classes for serving models through KServe:

```python
from modelhub.serving import ModelhubModelService, ModelServer

# Create model service
model_service = ModelhubModelService(
    name="my-classifier",
    run_uri="runs:/abc123def456/model",
    model_type="pyfunc"
)

# Load the model
model_service.load()

# Start the server
ModelServer().start([model_service])
```

ModelHub supports multiple model types including text, tabular data, and image processing. For comprehensive documentation on model serving capabilities, see our [Model Serving Guide](./SERVING.md).

### Deploy with KServe:

After logging the model, deploy it using KServe:

```yaml
apiVersion: "serving.kserve.io/v1beta1"
kind: "InferenceService"
metadata:
  name: "model-service"
  namespace: "modelhub"
  labels:
    azure.workload.identity/use: "true"
spec:
  predictor:
    containers:
      - image: your-registry.io/model-serve:latest
        name: model-service
        resources:
          requests:
            cpu: "1"
            memory: "2Gi"
          limits:
            cpu: "2"
            memory: "4Gi"
        command:
          [
            "sh",
            "-c",
            "python app/main.py --model_name my-classifier --run runs:/abc123def456/model",
          ]
        env:
          - name: MODELHUB_BASE_URL
            value: "https://api-modelhub.example.com"
    serviceAccountName: "service-account-name"
```

## Examples

### Training Pipeline with Multiple Stages

```python
from modelhub.core import ModelhubCredential
from modelhub.clients import MLflowClient, PipelineManager

# Initialize credential
credential = ModelhubCredential(
    modelhub_url="https://api-modelhub.example.com",
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Setup clients
mlflow_client = MLflowClient(credential=credential)
pipeline_manager = PipelineManager(credential=credential)

# Define and run pipeline
pipeline = pipeline_manager.start_pipeline("pipeline.yaml")

# Track experiment in MLflow
with mlflow_client.start_run(run_name="Training Run"):
    # Log training parameters
    mlflow_client.log_param("model_type", "transformer")
    mlflow_client.log_param("epochs", 10)

    # Log metrics
    mlflow_client.log_metric("train_loss", 0.123)
    mlflow_client.log_metric("val_accuracy", 0.945)

    # Log model artifacts
    mlflow_client.log_artifact("model.pkl")
```

### Dataset Version Management

```python
from modelhub.core import ModelhubCredential
from modelhub.clients import DatasetClient

# Initialize credential
credential = ModelhubCredential(
    modelhub_url="https://api-modelhub.example.com",
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Initialize client
dataset_client = DatasetClient(credential=credential)

# List available datasets
datasets = dataset_client.list_datasets()

# Get specific version
dataset_v2 = dataset_client.get_dataset_versions("dataset_id")

# Load dataset with version control
dataset = dataset_client.load_dataset(
    "my_dataset",
    version=2,
    split="train"
)
```

# InferenceClient

The `InferenceClient` provides a simple interface to perform inference using deployed models. It supports both text-based and file-based inference with comprehensive error handling and support for various input types.

## Installation

The inference client is part of the ModelHub SDK optional dependencies. To install:

```bash
pip install "autonomize-model-sdk[serving]"
```

Or with Poetry:

```bash
poetry add autonomize-model-sdk --extras serving
```

## Authentication

The client supports multiple authentication methods:

```python
from modelhub.core import ModelhubCredential
from modelhub.clients import InferenceClient

# Create credential
credential = ModelhubCredential(
    modelhub_url="https://your-modelhub-instance",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Using credential (recommended approach)
client = InferenceClient(
    credential=credential,
    client_id="client_id",
    copilot_id="copilot_id"
)

# Using environment variables (MODELHUB_BASE_URL, MODELHUB_CLIENT_ID, MODELHUB_CLIENT_SECRET)
# Note: This approach is deprecated and will be removed in a future version
client = InferenceClient()

# Using direct parameters (deprecated)
client = InferenceClient(
    base_url="https://your-modelhub-instance",
    sa_client_id="your-client-id",
    sa_client_secret="your-client-secret",
    genesis_client_id="client id",
    genesis_copilot_id="copilot id"
)

# Using a token (deprecated)
client = InferenceClient(
    base_url="https://your-modelhub-instance",
    token="your-token"
)
```

## Text Inference

For models that accept text input:

```python
# Simple text inference
response = client.run_text_inference(
    model_name="text-model",
    text="This is the input text"
)

# With additional parameters
response = client.run_text_inference(
    model_name="llm-model",
    text="Translate this to French: Hello, world!",
    parameters={
        "temperature": 0.7,
        "max_tokens": 100
    }
)

# Access the result
result = response["result"]
print(f"Processing time: {response.get('processing_time')} seconds")
```

## File Inference

The client supports multiple file input methods:

### Local File Path

```python
# Using a local file path
response = client.run_file_inference(
    model_name="image-recognition",
    file_path="/path/to/image.jpg"
)
```

### File Object

```python
# Using a file-like object
with open("document.pdf", "rb") as f:
    response = client.run_file_inference(
        model_name="document-processor",
        file_path=f,
        file_name="document.pdf",
        content_type="application/pdf"
    )
```

### URL

```python
# Using a URL
response = client.run_file_inference(
    model_name="image-recognition",
    file_path="https://example.com/images/sample.jpg"
)
```

### Signed URL from Cloud Storage

```python
# Using a signed URL from S3 or Azure Blob Storage
response = client.run_file_inference(
    model_name="document-processor",
    file_path="https://your-bucket.s3.amazonaws.com/path/to/document.pdf?signature=...",
    file_name="confidential-document.pdf",  # Optional: Override filename
    content_type="application/pdf"          # Optional: Override content type
)
```

## Response Format

The response format is consistent across inference types:

```python
{
    "result": {
        # Model-specific output
        # For example, text models might return:
        "text": "Generated text",

        # Image models might return:
        "objects": [
            {"class": "car", "confidence": 0.95, "bbox": [10, 20, 100, 200]},
            {"class": "person", "confidence": 0.87, "bbox": [150, 30, 220, 280]}
        ]
    },
    "processing_time": 0.234,  # Time in seconds
    "model_version": "1.0.0",  # Optional version info
    "metadata": {              # Optional additional information
        "runtime": "cpu",
        "batch_size": 1
    }
}
```

## Error Handling

The client provides comprehensive error handling with specific exception types:

```python
from modelhub.clients import InferenceClient
from modelhub.core.exceptions import (
    ModelHubException,
    ModelHubResourceNotFoundException,
    ModelHubBadRequestException,
    ModelhubUnauthorizedException
)

client = InferenceClient(credential=credential)

try:
    response = client.run_text_inference("model-name", "input text")
    print(response)
except ModelHubResourceNotFoundException as e:
    print(f"Model not found: {e}")
    # Handle 404 error
except ModelhubUnauthorizedException as e:
    print(f"Authentication failed: {e}")
    # Handle 401/403 error
except ModelHubBadRequestException as e:
    print(f"Invalid request: {e}")
    # Handle 400 error
except ModelHubException as e:
    print(f"Inference failed: {e}")
    # Handle other errors
```

## Additional Features

- **SSL verification control**: You can disable SSL verification for development environments
- **Automatic content type detection**: The client automatically detects the content type of files based on their extension
- **Customizable timeout**: You can set a custom timeout for inference requests
- **Comprehensive logging**: All operations are logged for easier debugging

## Async Support

The InferenceClient also provides async versions of all methods for use in async applications:

```python
import asyncio
from modelhub.clients import InferenceClient

async def run_inference():
    client = InferenceClient(credential=credential)

    # Text inference
    response = await client.arun_text_inference(
        model_name="text-model",
        text="This is async inference"
    )

    # File inference
    file_response = await client.arun_file_inference(
        model_name="image-model",
        file_path="/path/to/image.jpg"
    )

    return response, file_response

# Run with asyncio
responses = asyncio.run(run_inference())
```

# Prompt Management

The ModelHub SDK provides prompt management capabilities through the MLflowClient, leveraging MLflow's built-in Prompt Registry. This allows you to version, track, and reuse prompts across your organization.

## Features

- **Versioning** - Track the evolution of your prompts with version control
- **Reusability** - Store and manage prompts in a centralized registry
- **Aliases** - Create aliases for prompt versions to simplify deployment pipelines
- **Evaluation** - Evaluate prompts with MLflow's LLM evaluation capabilities
- **Integration** - Seamlessly integrate prompts with models and experiments

## Installation

Prompt management is included in the MLflow integration:

```bash
pip install "autonomize-model-sdk[mlflow]"
```

## Basic Usage

```python
from modelhub.core import ModelhubCredential
from modelhub.clients import MLflowClient

# Initialize credential
credential = ModelhubCredential(
    modelhub_url="https://api-modelhub.example.com",
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Initialize MLflow client
client = MLflowClient(credential=credential)

# Register a new prompt
template = """Summarize content you are provided with in {{ num_sentences }} sentences.
Sentences: {{ sentences }}"""

prompt = client.mlflow.register_prompt(
    name="summarization-prompt",
    template=template,
    commit_message="Initial commit",
    version_metadata={"author": "author@example.com"},
    tags={"task": "summarization", "language": "en"}
)

print(f"Created prompt '{prompt.name}' (version {prompt.version})")
```

## Loading and Using Prompts with AutoRAG

```python
# Load a specific prompt version
prompt = client.mlflow.load_prompt("prompts:/summarization-prompt/1")

# Load a prompt using an alias
prompt = client.mlflow.load_prompt("prompts:/summarization-prompt@production")

# Format the prompt with variables
formatted_prompt = prompt.format(
    num_sentences=2,
    sentences="This is the text to summarize."
)

# Use with AutoRAG for LLM calls
from autorag.language_models import OpenAILanguageModel

# Initialize AutoRAG OpenAI client
openai_llm = OpenAILanguageModel(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# Generate response
response = openai_llm.generate(
    message=[{"role": "user", "content": formatted_prompt}],
    model="gpt-4o-mini",
    temperature=0.1
)

print(response.content)
```

## Managing Prompt Versions

```python
# Update a prompt with a new version
new_template = """You are an expert summarizer. Condense the following content into exactly {{ num_sentences }}
clear and informative sentences that capture the key points.

Sentences: {{ sentences }}

Your summary should:
- Contain exactly {{ num_sentences }} sentences
- Include only the most important information
- Be written in a neutral, objective tone
"""

updated_prompt = client.mlflow.register_prompt(
    name="summarization-prompt",
    template=new_template,
    commit_message="Improved prompt with more specific instructions",
    version_metadata={"author": "author@example.com"}
)

# Create an alias for a specific version
client.mlflow.set_prompt_alias(
    "summarization-prompt",
    alias="production",
    version=2
)
```

## Evaluating Prompts with AutoRAG

```python
import pandas as pd
from autorag.language_models import OpenAILanguageModel

# Prepare evaluation data
eval_data = pd.DataFrame({
    "inputs": [
        "Artificial intelligence has transformed how businesses operate...",
        "Climate change continues to affect ecosystems worldwide..."
    ],
    "targets": [
        "AI has revolutionized business operations...",
        "Climate change is causing accelerating environmental damage..."
    ]
})

# Initialize AutoRAG OpenAI client
openai_llm = OpenAILanguageModel(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# Define prediction function using AutoRAG
def predict(data):
    predictions = []
    prompt = client.mlflow.load_prompt("prompts:/summarization-prompt/1")

    for _, row in data.iterrows():
        formatted_prompt = prompt.format(sentences=row["inputs"], num_sentences=1)
        response = openai_llm.generate(
            message=[{"role": "user", "content": formatted_prompt}],
            model="gpt-4o-mini",
            temperature=0.1
        )
        predictions.append(response.content)

    return predictions

# Run evaluation
with client.start_run(run_name="prompt-evaluation"):
    client.mlflow.log_param("model", "gpt-4o-mini")
    client.mlflow.log_param("temperature", 0.1)

    results = client.mlflow.evaluate(
        model=predict,
        data=eval_data,
        targets="targets",
        extra_metrics=[
            client.mlflow.metrics.latency(),
            client.mlflow.metrics.genai.answer_similarity(model="openai:/gpt-4")
        ]
    )
```

For more detailed information about prompt management, including advanced usage patterns, best practices, and in-depth examples, see our [Prompt Management Guide](./PROMPT.md).

# Model Monitoring and Evaluation

ModelHub SDK provides comprehensive tools for monitoring and evaluating both traditional ML models and Large Language Models (LLMs). These tools help track model performance, detect data drift, and assess LLM-specific metrics.

To install with monitoring capabilities:

```bash
pip install "autonomize-model-sdk[monitoring]"
```

## LLM Monitoring

The `LLMMonitor` utility allows you to evaluate and monitor LLM outputs using specialized metrics and visualizations.

### Basic LLM Evaluation

```python
from modelhub.core import ModelhubCredential
from modelhub.clients.mlflow_client import MLflowClient
from modelhub.monitors.llm_monitor import LLMMonitor

# Initialize credential
credential = ModelhubCredential(
    modelhub_url="https://your-modelhub-instance",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Initialize clients
mlflow_client = MLflowClient(credential=credential)
llm_monitor = LLMMonitor(mlflow_client=mlflow_client)

# Create a dataframe with LLM responses
data = pd.DataFrame({
    "prompt": ["Explain AI", "What is MLOps?"],
    "response": ["AI is a field of computer science...", "MLOps combines ML and DevOps..."],
    "category": ["education", "technical"]
})

# Create column mapping
column_mapping = llm_monitor.create_column_mapping(
    prompt_col="prompt",
    response_col="response",
    categorical_cols=["category"]
)

# Run evaluations
length_report = llm_monitor.evaluate_text_length(
    data=data,
    response_col="response",
    column_mapping=column_mapping,
    save_html=True
)

# Generate visualizations
dashboard_path = llm_monitor.generate_dashboard(
    data=data,
    response_col="response",
    category_col="category"
)

# Log metrics to MLflow
llm_monitor.log_metrics_to_mlflow(length_report)
```

### Evaluating Content Patterns

```python
patterns_report = llm_monitor.evaluate_content_patterns(
    data=data,
    response_col="response",
    words_to_check=["AI", "model", "learning"],
    patterns_to_check=["neural network", "deep learning"],
    prefix_to_check="I'll explain"
)
```

### Semantic Properties Analysis

```python
semantic_report = llm_monitor.evaluate_semantic_properties(
    data=data,
    response_col="response",
    prompt_col="prompt",
    check_sentiment=True,
    check_toxicity=True,
    check_prompt_relevance=True
)
```

### Comprehensive Evaluation

```python
results = llm_monitor.run_comprehensive_evaluation(
    data=data,
    response_col="response",
    prompt_col="prompt",
    categorical_cols=["category"],
    words_to_check=["AI", "model", "learning"],
    run_sentiment=True,
    run_toxicity=True,
    save_html=True
)
```

### LLM-as-Judge Evaluation

Evaluate responses using OpenAI's models as a judge (requires OpenAI API key):

```python
judge_report = llm_monitor.evaluate_llm_as_judge(
    data=data,
    response_col="response",
    check_pii=True,
    check_decline=True,
    custom_evals=[{
        "name": "Educational Value",
        "criteria": "Evaluate whether the response has educational value.",
        "target": "educational",
        "non_target": "not_educational"
    }]
)
```

### Comparing LLM Models

Compare responses from different LLM models:

```python
comparison_report = llm_monitor.generate_comparison_report(
    reference_data=model_a_data,
    current_data=model_b_data,
    response_col="response",
    category_col="category"
)

comparison_viz = llm_monitor.create_comparison_visualization(
    reference_data=model_a_data,
    current_data=model_b_data,
    response_col="response",
    metrics=["length", "word_count", "sentiment_score"]
)
```

## Traditional ML Monitoring

The SDK also includes `MLMonitor` for traditional ML models, providing capabilities for:

- Data drift detection
- Data quality assessment
- Model performance monitoring
- Target drift analysis
- Regression and classification metrics

```python
from modelhub.core import ModelhubCredential
from modelhub.clients.mlflow_client import MLflowClient
from modelhub.monitors.ml_monitor import MLMonitor

# Initialize credential
credential = ModelhubCredential(
    modelhub_url="https://your-modelhub-instance",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Initialize clients
mlflow_client = MLflowClient(credential=credential)
ml_monitor = MLMonitor(mlflow_client=mlflow_client)

results = ml_monitor.run_and_log_reports(
    reference_data=reference_data,
    current_data=current_data,
    report_types=["data_drift", "data_quality", "target_drift", "regression"],
    column_mapping=column_mapping,
    target_column="target",
    prediction_column="prediction",
    log_to_mlflow=True
)
```

## Migration Guide

### autonomize-core Integration (Latest Version)

The latest version of ModelHub SDK is built on **autonomize-core**, providing enhanced functionality and better performance. Here's what you need to know:

#### Environment Variables Migration

**New Preferred Variables:**
```bash
export MODELHUB_URI=https://your-modelhub.com
export MODELHUB_AUTH_CLIENT_ID=your_client_id
export MODELHUB_AUTH_CLIENT_SECRET=your_secret
export GENESIS_CLIENT_ID=your_genesis_client
export GENESIS_COPILOT_ID=your_copilot
```

**Legacy Variables (Still Supported):**
```bash
export MODELHUB_BASE_URL=https://your-modelhub.com
export MODELHUB_CLIENT_ID=your_client_id
export MODELHUB_CLIENT_SECRET=your_secret
export CLIENT_ID=your_client
export COPILOT_ID=your_copilot
```

#### SSL Certificate Support

New SSL configuration options are now available:

```python
from modelhub.core import ModelhubCredential

# Custom certificate path
credential = ModelhubCredential(
    modelhub_url="https://your-modelhub.com",
    client_id="your_client_id",
    client_secret="your_client_secret",
    verify_ssl="/path/to/certificate.pem"
)

# Disable SSL verification (development only)
credential = ModelhubCredential(
    modelhub_url="https://your-modelhub.com",
    client_id="your_client_id",
    client_secret="your_client_secret",
    verify_ssl=False
)
```

#### What's Changed
- **HTTP Client**: Now uses `httpx` instead of `requests` for better performance
- **Exception Handling**: More detailed exception types from autonomize-core
- **Authentication**: Enhanced credential management system
- **Logging**: Improved logging with autonomize-core's logging system

#### What Stays the Same
- **API Compatibility**: All existing client methods work without changes
- **Import Statements**: No changes needed to your import statements
- **Environment Variables**: Legacy environment variables continue to work

### Client Architecture Changes

Starting with version 1.2.0, the ModelHub SDK uses a new architecture based on HTTPX and a centralized credential system. If you're upgrading from an earlier version, you'll need to update your code as follows:

#### Old Way (Deprecated)

```python
from modelhub.clients import BaseClient, DatasetClient, MLflowClient

# Direct initialization with credentials
client = BaseClient(
    base_url="https://api-modelhub.example.com",
    sa_client_id="your_client_id",
    sa_client_secret="your_client_secret"
)

dataset_client = DatasetClient(
    base_url="https://api-modelhub.example.com",
    sa_client_id="your_client_id",
    sa_client_secret="your_client_secret"
)
```

#### New Way (Recommended)

```python
from modelhub.core import ModelhubCredential
from modelhub.clients import BaseClient, DatasetClient, MLflowClient

# Create a credential object
credential = ModelhubCredential(
    modelhub_url="https://api-modelhub.example.com",
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Initialize clients with the credential
base_client = BaseClient(
    credential=credential,
    client_id="your_client_id",  # For RBAC
    copilot_id="your_copilot_id"  # For RBAC
)

dataset_client = DatasetClient(
    credential=credential,
    client_id="your_client_id",
    copilot_id="your_copilot_id"
)

mlflow_client = MLflowClient(
    credential=credential,
    client_id="your_client_id",
    copilot_id="your_copilot_id"
)
```

### Prompt Management Changes

The PromptClient has been replaced with MLflow's built-in prompt registry capabilities:

#### Old Way (Deprecated)

```python
from modelhub.clients.prompt_client import PromptClient

prompt_client = PromptClient(
    base_url="https://api-modelhub.example.com",
    sa_client_id="your_client_id",
    sa_client_secret="your_client_secret"
)

prompt_client.create_prompt(
    name="summarization-prompt",
    template="Summarize this text: {{context}}",
    prompt_type="USER"
)
```

#### New Way (Recommended)

```python
from modelhub.core import ModelhubCredential
from modelhub.clients import MLflowClient

credential = ModelhubCredential(
    modelhub_url="https://api-modelhub.example.com",
    client_id="your_client_id",
    client_secret="your_client_secret"
)

client = MLflowClient(credential=credential)

client.mlflow.register_prompt(
    name="summarization-prompt",
    template="Summarize this text: {{ context }}",
    commit_message="Initial version"
)

# Load and use a prompt
prompt = client.mlflow.load_prompt("prompts:/summarization-prompt/1")
formatted_prompt = prompt.format(context="Your text to summarize")
```

### New Async Support

All clients now support asynchronous operations:

```python
# Synchronous
result = client.get("endpoint")

# Asynchronous
result = await client.aget("endpoint")
```

For detailed information about the new prompt management capabilities, see the [Prompt Management Guide](./PROMPT.md).
