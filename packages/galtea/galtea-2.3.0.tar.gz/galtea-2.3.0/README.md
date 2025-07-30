# Galtea SDK

<p align="center">
  <img src="https://galtea.ai/img/galtea_mod.png" alt="Galtea" width="500" height="auto"/>
</p>

<p align="center">
  <strong>Comprehensive AI/LLM Testing & Evaluation Framework</strong>
</p>

<p align="center">
	<a href="https://pypi.org/project/galtea/">
		<img src="https://img.shields.io/pypi/v/galtea.svg" alt="PyPI version">
	</a>
	<a href="https://pypi.org/project/galtea/">
		<img src="https://img.shields.io/pypi/pyversions/galtea.svg" alt="Python versions">
	</a>
	<a href="https://www.apache.org/licenses/LICENSE-2.0">
		<img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License">
	</a>
</p>

## Overview

Galtea SDK empowers AI engineers, ML engineers and data scientists to rigorously test and evaluate their AI products. With a focus on reliability and transparency, Galtea offers:

1. **Automated Test Dataset Generation** - Create comprehensive test datasets tailored to your AI product
2. **Sophisticated Product Evaluation** - Evaluate your AI products across multiple dimensions

## Installation

```bash
pip install galtea
```

## Development

### Building the Project

This project uses Poetry for dependency management and packaging. To build the project:

```bash
poetry build
```

This will create distribution packages (wheel and source distribution) in the `dist/` directory.

### Development Setup

```bash
# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

## Quick Start

```python
from galtea import Galtea
import os

# Initialize with your API key
galtea = Galtea(api_key=os.getenv("GALTEA_API_KEY"))

# Create a test, which is a collection of test cases
test = galtea.tests.create(
    name="factual-accuracy-test",
    type="QUALITY",
    product_id="your-product-id",
    ground_truth_file_path="path/to/ground-truth.pdf"
)

# Get test cases to iterate over
test_cases = galtea.test_cases.list(test.id)

# Create a version, which is a specific iteration of your product
version = galtea.versions.create(
    name="gpt-4-self-hosted-v1",
    product_id="your-product-id",
    description="Self-hosted GPT-4 equivalent model",
    endpoint="http://your-model-endpoint.com/v1/chat"
)

for test_case in test_cases:
    # Simulate a call to your product to get its output for a given test case
    # In a real scenario, you would call your actual product endpoint
    model_answer = f"The answer to '{test_case.input}' is..."    # Run an evaluation task
    # An Evaluation is implicitly created to group these tasks
    galtea.evaluation_tasks.create_single_turn(
        metrics=["factual-accuracy", "coherence", "relevance"],
        version_id=version.id,
        test_case_id=test_case.id,
        actual_output=model_answer
    )
```

## Core Features

### 1. Test Creation

- **Quality Tests**: Assess response quality, coherence, and factual accuracy
- **Adversarial Tests**: Stress-test your models against edge cases and potential vulnerabilities
- **Ground Truth Integration**: Upload ground truth documents to validate factual responses
- **Custom Test Types**: Define tests tailored to your specific use cases and requirements

```python
# Create a custom test with your own dataset
test = galtea.tests.create(
    name="medical-knowledge-test",
    type="QUALITY",
    product_id="your-product-id",
    ground_truth_file_path="medical_reference.pdf"
)
```

### 2. Comprehensive Product Evaluation

Evaluate your AI products with sophisticated metrics:

- **Multi-dimensional Analysis**: Analyze outputs across various dimensions including accuracy, relevance, and coherence
- **Customizable Metrics**: Define your own evaluation criteria and rubrics
- **Batch Processing**: Run evaluations on large datasets efficiently
- **Detailed Reports**: Get comprehensive insights into your model's performance

```python
# Define custom evaluation metrics
custom_metric = galtea.metrics.create(
    name="medical-accuracy",
    criteria="Assess if the response is medically accurate based on the provided context.",
    evaluation_params=["actual output", "context"]
)

# Run batch evaluation
import pandas as pd

# Load your test data
test_data = pd.read_json("medical_queries.json")

# 1. Create a session for this batch evaluation
session = galtea.sessions.create(version_id=version.id, is_production=True)

# 2. Log each interaction as an inference result
for _, row in test_data.iterrows():
    # Get response from your product
    model_response = your_product_function(row["query"], row["medical_context"])
    
    # Log each turn to the session
    galtea.inference_results.create(
        session_id=session.id,
        input=row["query"],
        output=model_response,
        retrieval_context=row["medical_context"]
    )

# 3. Evaluate the entire session at once
galtea.evaluation_tasks.create(
    metrics=[custom_metric.name, "coherence", "toxicity"],
    session_id=session.id
)
```

## Managing Your AI Products

Galtea provides a complete ecosystem for evaluating and monitoring your AI products:

### Products

Represents a functionality or service that is evaluated by Galtea.

```python
# List your products
products = galtea.products.list()

# Select a product to work with
product = products[0]
```

### Versions

Represents a specific iteration of a product. This allows for tracking improvements and regressions over time.

```python
# Create a new version of your product
version = galtea.versions.create(
    name="gpt-4-fine-tuned-v2",
    product_id=product.id,
    description="Fine-tuned GPT-4 for medical domain",
    model_id="gpt-4",
    system_prompt="You are a helpful medical assistant..."
)

# List versions of your product
versions = galtea.versions.list(product_id=product.id)
```

### Tests

A collection of test cases designed to evaluate specific aspects of your product versions.

```python
# Create a test
test = galtea.tests.create(
    name="medical-qa-test",
    type="QUALITY",
    product_id=product.id,
    ground_truth_file_path="medical_data.pdf"
)

# Download a test file
test_file = galtea.tests.download(test, output_dir="tests")
```

### Test Cases

A single challenge for evaluating product performance. Each test case typically includes an input and may include an expected output and context.

### Sessions

A group of inference results that represent a complete conversation between a user and an AI system.

### Inference Results

A single turn in a conversation, including the user's input and the AI's output. These are the raw interactions that can be evaluated.

### Evaluations

A group of inference results from a session that can be evaluated. It acts as a container for all the evaluation tasks that measure how effectively the product version performs.

```python
# Evaluations are created implicitly when you log evaluation tasks.
# For example, when you run this, an evaluation is created behind the scenes:
galtea.evaluation_tasks.create_single_turn(
    metrics=["factual-accuracy"],
    version_id=version.id,
    test_case_id=test_cases[0].id,
    actual_output="Some output from your product."
)

# List evaluations for a product
evaluations = galtea.evaluations.list(product_id=product.id)
```

## Advanced Usage

### Custom Metrics

Define custom evaluation criteria specific to your needs:

```python
# Create a custom metric
custom_metric_1 = galtea.metrics.create(
    name="patient-safety-score-v1",
    criteria="Evaluate responses for patient safety considerations",
    evaluation_params=["actual output"]
)
```

### Batch Processing

Efficiently evaluate your model on large datasets:

```python
import pandas as pd
import os

# Load your test queries from a JSON file
queries_file = os.path.join(os.path.dirname(__file__), 'test_data.json')
df = pd.read_json(queries_file)

# Create a session for this batch evaluation
session = galtea.sessions.create(version_id=version.id, is_production=True)

# Process each query
for idx, row in df.iterrows():
    # Get your model's response to the query
    model_response = your_product_function(row['query'])

    # Log each turn to the session
    galtea.inference_results.create(
        session_id=session.id,
        input=row['query'],
        output=model_response
    )

# Evaluate the entire session
galtea.evaluation_tasks.create(
    metrics=["relevance", custom_metric_1.name],
    session_id=session.id
)
```

## API Reference

### Main Classes

- **`Galtea`**: Main client for interacting with the Galtea platform

### Product Management

- **`galtea.products.list(offset=None, limit=None)`**: List available products
- **`galtea.products.get(product_id)`**: Get a specific product by ID

### Test Management

- **`galtea.tests.create(name, type, product_id, ground_truth_file_path=None, test_file_path=None)`**: Create a new test
- **`galtea.tests.get(test_id)`**: Retrieve a test by ID
- **`galtea.tests.list(product_id, offset=None, limit=None)`**: List tests for a product
- **`galtea.tests.download(test, output_dir)`**: Download test files in the selected directory.

### Test Cases Management

- **`galtea.test_cases.create(test_id, input, expected_output, context=None)`**: Create a new test case
- **`galtea.test_cases.get(test_case_id)`**: Get a test case by ID
- **`galtea.test_cases.list(test_id, offset=None, limit=None)`**: List test cases for a test
- **`galtea.test_cases.delete(test_case_id)`**: Delete a test case by ID

### Version Management

- **`galtea.versions.create(product_id, name, description=None, ...)`**: Create a new product version
- **`galtea.versions.get(version_id)`**: Get a version by ID
- **`galtea.versions.list(product_id, offset=None, limit=None)`**: List versions for a product

### Metric Management

- **`galtea.metrics.create(name, criteria=None, evaluation_steps=None, evaluation_params=None)`**: Create a custom metric
- **`galtea.metrics.get(metric_type_id)`**: Get a metric by ID
- **`galtea.metrics.list(offset=None, limit=None)`**: List available metrics

### Session Management

- **`galtea.sessions.create(version_id, ...)`**: Create a new session to log a conversation.
- **`galtea.sessions.get(session_id)`**: Get a session by ID.
- **`galtea.sessions.list(version_id, ...)`**: List sessions for a version.
- **`galtea.sessions.delete(session_id)`**: Delete a session by ID.

### Inference Result Management

- **`galtea.inference_results.create(session_id, input, output, ...)`**: Log a single turn in a conversation.
- **`galtea.inference_results.get(inference_result_id)`**: Get an inference result by ID.
- **`galtea.inference_results.list(session_id, ...)`**: List inference results for a session.
- **`galtea.inference_results.delete(inference_result_id)`**: Delete an inference result by ID.

### Evaluation Management

- An `Evaluation` is created implicitly when you create evaluation tasks.
- **`galtea.evaluations.get(evaluation_id)`**: Get an evaluation by ID
- **`galtea.evaluations.list(product_id, offset=None, limit=None)`**: List evaluations for a product

### Evaluation Tasks Management

- **`galtea.evaluation_tasks.list(evaluation_id, offset=None, limit=None)`**: List tasks performed for an evaluation
- **`galtea.evaluation_tasks.get(evaluation_task_id)`**: Get a specific task by ID
- **`galtea.evaluation_tasks.create(metrics, session_id)`**: Create evaluation tasks for all inference results within a given session.
- **`galtea.evaluation_tasks.create_single_turn(metrics, version_id, ...)`**: Create an evaluation task for a single-turn interaction, such as one based on a specific test case or a production query.

## Getting Help

- **Documentation**: [https://docs.galtea.ai/](https://docs.galtea.ai/)
- **Support**: [support@galtea.ai](mailto:support@galtea.ai)

## Authors

This software has been developed by the members of the product team of Galtea Solutions S.L.

## License

Apache License 2.0
