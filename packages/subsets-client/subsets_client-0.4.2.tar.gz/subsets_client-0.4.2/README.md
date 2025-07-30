# Subsets Python Client

Simple Python client for the Subsets data platform.

## Installation

```bash
pip install subsets-client
```

## Quick Start

```python
from subsets_client import SubsetsClient
import pandas as pd

# Initialize client
client = SubsetsClient(api_key="your_api_key")

# Create a dataset
dataset = client.create_dataset({
    "id": "sales_data",
    "title": "Global Sales Data",
    "description": "Quarterly sales by region",
    "license": "MIT",
    "columns": [
        {"id": "region", "type": "string", "description": "Sales region"},
        {"id": "quarter", "type": "string", "description": "Quarter (e.g., 2023-Q1)"},
        {"id": "revenue", "type": "double", "description": "Revenue in millions"}
    ]
})

# Add data
import pyarrow as pa

table = pa.table({
    "region": ["North America", "Europe", "Asia"],
    "quarter": ["2023-Q1", "2023-Q1", "2023-Q1"],
    "revenue": [125.4, 98.2, 156.8]
})
client.add_data("sales_data", table)

# Query data
results = client.query("SELECT * FROM subsets.sales_data WHERE revenue > 100")
print(results)
```

## API Reference

### Creating Datasets

```python
dataset = client.create_dataset({
    "id": "dataset_id",
    "title": "Dataset Title",
    "description": "Description",
    "license": "MIT",
    "columns": [...]
})
```

### Adding Data

```python
# Using PyArrow Table
import pyarrow as pa

table = pa.table({
    "col1": [1, 2, 3],
    "col2": ["a", "b", "c"]
})
client.add_data("dataset_id", table)
```

### Querying Data

```python
# Returns a pandas DataFrame
df = client.query("SELECT * FROM subsets.dataset_id")
```

### Managing Datasets

```python
# List datasets
datasets = client.list_datasets(search="sales", limit=10)

# Get dataset info
info = client.get_dataset("dataset_id")

# Delete data (keeps structure)
client.delete_data("dataset_id")

# Delete entire dataset
client.delete_dataset("dataset_id")
```

## Error Handling

```python
from subsets_client import SubsetsError, AuthenticationError

try:
    client.add_data("dataset_id", data)
except AuthenticationError:
    print("Invalid API key")
except SubsetsError as e:
    print(f"Error: {e}")
```

## License

MIT