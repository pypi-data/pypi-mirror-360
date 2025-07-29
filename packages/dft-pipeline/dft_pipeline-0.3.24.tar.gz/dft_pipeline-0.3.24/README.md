# DFT - Data Flow Tools

[![PyPI version](https://badge.fury.io/py/dft-pipeline.svg)](https://badge.fury.io/py/dft-pipeline)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Flexible ETL pipeline framework designed for data analysts and engineers. Build, orchestrate, and monitor data pipelines with YAML configurations.

## ✨ Key Features

- **🔧 Component-Based**: Modular sources, processors, and endpoints  
- **🔌 Plugin System**: Add custom components directly to your project
- **📋 YAML Configuration**: Simple, readable pipeline definitions
- **🔗 Dependency Management**: Automatic pipeline ordering and validation
- **📊 Interactive Documentation**: Web-based pipeline exploration
- **💾 Database Support**: PostgreSQL, MySQL, ClickHouse with upsert capabilities
- **🔄 Incremental Processing**: Smart data loading with state management
- **⏱️ Microbatch Processing**: Time-based data windows with lookback support
- **⚙️ Data Validation**: Built-in quality checks and constraints
- **🎯 Analyst-Friendly**: Rich CLI tools and component discovery

## 📚 Documentation

- **[Custom Components Guide](docs/CUSTOM_COMPONENTS.md)** - Develop custom sources, processors, and endpoints
- **[Database Integration Guide](docs/DATABASE_INTEGRATION.md)** - Database connections, upsert operations, and incremental processing  
- **[Pipeline Dependencies Guide](docs/PIPELINE_DEPENDENCIES.md)** - Inter-pipeline dependencies and execution order
- **[Microbatch Processing Guide](docs/MICROBATCH_PROCESSING.md)** - Time-based data windows, lookback strategies, and ETL optimization
- **[A/B Testing Guide](docs/AB_TESTING.md)** - Statistical hypothesis testing for experiments with T-test, Z-test, CUPED, and Bootstrap methods

## 🚀 Quick Start

### 1. Installation

#### Option A: Install from PyPI (Recommended)

```bash
# Install directly from PyPI
pip install dft-pipeline
```

#### Option B: Install from Source (For Development)

```bash
# Clone repository
git clone <repository-url>
cd dft

# Install package with dependencies
pip install -e .
```

### 2. Create Project

```bash
# Initialize new project
dft init my_analytics_project
cd my_analytics_project
```

### 3. Explore Examples

```bash
# Initialize a new project with examples
dft init my_analytics_project
cd my_analytics_project

# View interactive documentation
dft docs --serve
# Opens at http://localhost:8080

# Discover available components
dft components list

# Run a simple pipeline (uses sample data)
dft run --select simple_csv_example

# Try the custom components example  
dft run --select custom_example_pipeline
```

## 📦 Built-in Components

DFT includes pre-built components for common data operations:

- **Sources**: CSV, PostgreSQL, MySQL, ClickHouse, Google Play, JSON
- **Processors**: Data validation, anomaly detection  
- **Endpoints**: CSV, PostgreSQL, MySQL, ClickHouse, JSON output

```bash
# Discover available components
dft components list

# Get component details and examples
dft components describe postgresql --format yaml

# Interactive component browser
dft docs --serve
```

## 📋 Pipeline Configuration

### Basic Pipeline

```yaml
pipeline_name: simple_etl
description: Extract, validate, and load user data

connections:
  analytics_db:
    type: postgresql
    host: analytics.company.com
    database: warehouse
    user: analyst
    password: "${POSTGRES_PASSWORD}"

steps:
  - id: load_user_data
    type: source
    source_type: csv
    config:
      file_path: "data/users.csv"

  - id: validate_users
    type: processor
    processor_type: validator
    depends_on: [load_user_data]
    config:
      required_columns: [id, email, created_at]

  - id: save_clean_users
    type: endpoint
    endpoint_type: postgresql
    connection: analytics_db
    depends_on: [validate_users]
    config:
      table: users_clean
      mode: replace
```

### Advanced Features

- **Pipeline Dependencies**: `depends_on: [other_pipeline]`
- **Variables**: `{{ var("date") }}` and `{{ env_var("API_KEY") }}`
- **Named Connections**: Reusable database configurations
- **Tags**: Organize pipelines with `tags: [daily, analytics]`

## 🔄 Pipeline Execution

```bash
# Run all pipelines
dft run

# Run specific pipeline
dft run --select customer_analytics

# Run by tags
dft run --select tag:daily

# Run with dependencies (dbt-style)
dft run --select +customer_analytics  # Include upstream dependencies
dft run --select customer_analytics+  # Include downstream dependencies

# Override variables
dft run --select analytics --vars date=2024-01-15,min_amount=5.00
```

## 📊 Documentation & Monitoring

```bash
# Interactive web documentation
dft docs --serve

# Validate pipeline configurations
dft validate

# Check pipeline dependencies
dft deps

# List available components
dft components list
```

## 🔍 Advanced Features

- **Environment Configuration**: `export DFT_ENV=prod`
- **State Management**: Automatic incremental processing with `{{ state.get() }}`
- **Custom Components**: Plugin system for extending functionality

### Custom Components

Add custom sources, processors, and endpoints in your project's `dft/` directory:

```python
# dft/sources/api_source.py
from dft.core.base import DataSource
from dft.core.data_packet import DataPacket

class ApiSource(DataSource):
    def extract(self, variables=None) -> DataPacket:
        # Your API extraction logic
        return DataPacket(data=data, metadata={})
    
    def test_connection(self) -> bool:
        return True
```

```yaml
# Use in pipelines with snake_case naming
steps:
  - id: fetch_data
    type: source
    source_type: api  # Uses ApiSource class
    config:
      api_url: "https://api.example.com/data"
```

See **[Custom Components Guide](docs/CUSTOM_COMPONENTS.md)** for detailed examples.

## 📁 Project Structure

```
my_project/
├── dft_project.yml          # Project configuration
├── .env                     # Environment variables
├── pipelines/               # Pipeline definitions
│   ├── ingestion.yml
│   ├── analytics.yml
│   └── reporting.yml
├── dft/                     # Custom components (auto-created)
│   ├── sources/            # Custom data sources
│   ├── processors/         # Custom data processors
│   └── endpoints/          # Custom data endpoints
├── data/                    # Input data files
├── output/                  # Generated outputs
└── .dft/                    # DFT metadata and logs
```

## 🚀 Get Started

```bash
# Install DFT
pip install dft-pipeline

# Create new project
dft init my_project && cd my_project

# Explore components and documentation
dft docs --serve

# Run example pipeline
dft run --select custom_example_pipeline
```

## 📄 License

MIT License - see LICENSE file for details.