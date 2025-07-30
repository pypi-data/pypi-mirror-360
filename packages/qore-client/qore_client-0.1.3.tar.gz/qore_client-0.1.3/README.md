# Qore Client

Qore Client is a Python client library for the Qore API.

## Prerequisites

First, install `uv` package installer:

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows PowerShell
(Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -UseBasicParsing).Content | pwsh -Command -
```

## Installation

For users, simply install using pip:

```bash
pip install qore-client
```

## Usage Example

The code below is an example of creating a simple parquet file, uploading it to Qore Drive, and then downloading it again.

```python
access_key = "access_key"
secret_key = "secret_key"
folder_id = "folder_id"
parquet_file = "data.parquet"

from qore_client.client import QoreClient

client = QoreClient(access_key, secret_key)

data = {
    "name": ["Alice", "Bob", "Charlie", "David"],
    "age": [25, 30, 35, 40],
    "city": ["New York", "Los Angeles", "Chicago", "Houston"],
    "salary": [50000, 60000, 70000, 80000],
}

sample_df = pd.DataFrame(data)
sample_df.to_parquet(parquet_file)

create_file_response = client.create_file(folder_id, parquet_file)
get_file_response = client.get_file(response["id"])

df = pd.read_parquet(response2)

print(df)
#       name  age         city  salary
# 0    Alice   25     New York   50000
# 1      Bob   30  Los Angeles   60000
# 2  Charlie   35      Chicago   70000
# 3    David   40      Houston   80000
```

## Development Environment Setup

1. Clone the repository

```bash
git clone <repository-url>
```

2. Create a virtual environment and install dependencies

```bash
bash dev.sh
```

## Testing Development Versions

```bash
# Install the package from TestPyPI
uv pip install -i https://test.pypi.org/simple/ qore-client=={version}

# Install the package from PyPI
uv pip install qore-client=={version}
```

## CI/CD

This project supports automated testing and deployment through GitLab CI/CD.
