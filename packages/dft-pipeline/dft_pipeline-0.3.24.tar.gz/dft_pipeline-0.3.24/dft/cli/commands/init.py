"""Initialize DFT project command"""

import click
from pathlib import Path


def init_project(project_name: str, pipelines_dir: str) -> None:
    """Initialize a new DFT project"""
    
    project_path = Path(project_name)
    
    if project_path.exists():
        click.echo(f"Error: Directory '{project_name}' already exists")
        return
    
    try:
        # Create project structure
        project_path.mkdir()
        (project_path / pipelines_dir).mkdir()
        (project_path / "tests").mkdir()
        (project_path / "output").mkdir()  # Create output directory
        (project_path / ".dft").mkdir()
        (project_path / ".dft" / "logs").mkdir()  # Create logs directory
        
        # Create dft_project.yml
        project_config = f"""# DFT Project Configuration
project_name: {project_name}
version: '1.0'

# Pipeline configuration
pipelines_dir: {pipelines_dir}

# Default variables
vars:
  target: dev

# State management configuration
state:
  # Whether to ignore state files in git (recommended for development)
  # Set to false for production/GitOps workflows where state should be versioned
  ignore_in_git: true

# Database and service connections (use environment variables for secrets)
connections:
  postgres_default:
    type: postgresql
    host: "{{{{ env_var('DB_HOST', 'localhost') }}}}"
    port: "{{{{ env_var('DB_PORT', '5432') }}}}"
    database: "{{{{ env_var('DB_NAME', 'analytics') }}}}"
    user: "{{{{ env_var('DB_USER', 'postgres') }}}}"
    password: "{{{{ env_var('DB_PASSWORD', '') }}}}"

# Logging configuration
logging:
  level: INFO
  dir: .dft/logs
"""
        
        (project_path / "dft_project.yml").write_text(project_config)
        
        # Create example pipeline
        example_pipeline = f"""# Example pipeline configuration
pipeline_name: example_pipeline
tags: [example, daily]

steps:
  - id: extract_data
    type: source
    source_type: csv
    config:
      file_path: "data/sample.csv"
  
  - id: validate_data
    type: processor
    processor_type: validator
    depends_on: [extract_data]
    config:
      required_columns: [id, name]
      row_count_min: 1
  
  - id: save_results
    type: endpoint
    endpoint_type: csv
    depends_on: [validate_data]
    config:
      file_path: "output/processed_{{{{ today() }}}}.csv"
"""
        
        (project_path / pipelines_dir / "example_pipeline.yml").write_text(example_pipeline)
        
        # Create example pipeline with custom components
        custom_pipeline = f"""# Example pipeline using custom components
pipeline_name: custom_example_pipeline
tags: [example, custom]

steps:
  - id: generate_data
    type: source
    source_type: my_custom  # This will use MyCustomSource class
    config: {{}}
  
  - id: process_data
    type: processor
    processor_type: my_custom  # This will use MyCustomProcessor class
    depends_on: [generate_data]
    config: {{}}
  
  - id: save_results
    type: endpoint
    endpoint_type: my_custom  # This will use MyCustomEndpoint class
    depends_on: [process_data]
    config:
      output_path: "output/custom_processed_data.txt"
"""
        
        (project_path / pipelines_dir / "custom_example_pipeline.yml").write_text(custom_pipeline)
        
        # Create .env template
        env_template = """# Environment variables for DFT project
# Copy this file to .env and fill in your values

# Database connections
DB_HOST=localhost
DB_PORT=5432
DB_NAME=analytics
DB_USER=postgres
DB_PASSWORD=your_password_here

# API keys
SLACK_TOKEN=xoxb-your-slack-token
API_KEY=your_api_key_here
"""
        
        (project_path / ".env.example").write_text(env_template)
        
        # Create sample data directory and sample CSV file
        (project_path / "data").mkdir()
        
        # Create sample CSV data
        sample_csv_data = """id,name,value,category,date
1,Alice,100,A,2024-01-01
2,Bob,150,B,2024-01-02
3,Charlie,200,A,2024-01-03
4,David,120,C,2024-01-04
5,Eve,180,B,2024-01-05
6,Frank,90,A,2024-01-06
7,Grace,220,C,2024-01-07
8,Henry,160,B,2024-01-08
9,Ivy,140,A,2024-01-09
10,Jack,190,C,2024-01-10"""
        
        (project_path / "data" / "sample.csv").write_text(sample_csv_data)
        
        # Create custom components directories
        (project_path / "dft").mkdir()
        (project_path / "dft" / "sources").mkdir()
        (project_path / "dft" / "processors").mkdir()
        (project_path / "dft" / "endpoints").mkdir()
        
        # Create __init__.py files for custom components
        (project_path / "dft" / "__init__.py").write_text('"""Custom DFT components"""')
        (project_path / "dft" / "sources" / "__init__.py").write_text('"""Custom data sources"""')
        (project_path / "dft" / "processors" / "__init__.py").write_text('"""Custom data processors"""')
        (project_path / "dft" / "endpoints" / "__init__.py").write_text('"""Custom data endpoints"""')
        
        # Create example custom components
        example_source = '''"""Example custom data source"""

from typing import Any, Dict, Optional
from dft.core.base import DataSource
from dft.core.data_packet import DataPacket


class MyCustomSource(DataSource):
    """Example custom data source that generates sample data"""
    
    def extract(self, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Extract sample data"""
        # Example: generate sample data with pandas fallback
        try:
            import pandas as pd
            data = {
                'id': [1, 2, 3, 4, 5],
                'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
                'value': [10, 20, 30, 40, 50]
            }
            df = pd.DataFrame(data)
            timestamp = pd.Timestamp.now()
        except ImportError:
            # Fallback if pandas not available
            data = [
                {'id': 1, 'name': 'Alice', 'value': 10},
                {'id': 2, 'name': 'Bob', 'value': 20},
                {'id': 3, 'name': 'Charlie', 'value': 30},
                {'id': 4, 'name': 'David', 'value': 40},
                {'id': 5, 'name': 'Eve', 'value': 50}
            ]
            df = data  # Use list of dicts as fallback
            from datetime import datetime
            timestamp = datetime.now()
        
        return DataPacket(
            data=df,
            metadata={
                'source': 'MyCustomSource',
                'row_count': len(df) if hasattr(df, '__len__') else 5,
                'generated_at': timestamp
            }
        )
    
    def test_connection(self) -> bool:
        """Test connection (always returns True for this example)"""
        return True
'''
        
        example_processor = '''"""Example custom data processor"""

from typing import Any, Dict, Optional
from datetime import datetime
from dft.core.base import DataProcessor
from dft.core.data_packet import DataPacket


class MyCustomProcessor(DataProcessor):
    """Example custom processor that doubles values"""
    
    def process(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Process data by doubling the 'value' column"""
        try:
            import pandas as pd
            df = packet.data.copy()
            
            # Example processing: double the value column if it exists
            if 'value' in df.columns:
                df['value'] = df['value'] * 2
                df['processed'] = True
            
            timestamp = pd.Timestamp.now()
        except ImportError:
            # Fallback for non-pandas data
            if isinstance(packet.data, list):
                df = []
                for row in packet.data:
                    new_row = row.copy()
                    if 'value' in new_row:
                        new_row['value'] = new_row['value'] * 2
                        new_row['processed'] = True
                    df.append(new_row)
            else:
                df = packet.data
            timestamp = datetime.now()
        
        return DataPacket(
            data=df,
            metadata={
                **packet.metadata,
                'processor': 'MyCustomProcessor',
                'processed_at': timestamp
            }
        )
'''
        
        example_endpoint = '''"""Example custom data endpoint"""

from typing import Any, Dict, Optional
from datetime import datetime
from dft.core.base import DataEndpoint
from dft.core.data_packet import DataPacket


class MyCustomEndpoint(DataEndpoint):
    """Example custom endpoint that prints data info"""
    
    def load(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> bool:
        """Load data by printing information about it"""
        data = packet.data
        
        try:
            import pandas as pd
            print(f"Custom endpoint received data:")
            print(f"  Shape: {data.shape}")
            print(f"  Columns: {list(data.columns)}")
            print(f"  Sample data:")
            print(data.head().to_string(index=False))
            
            # Save to file
            output_path = self.get_config('output_path', 'output/custom_data.txt')
            with open(output_path, 'w') as f:
                f.write(f"Data processed at {pd.Timestamp.now()}\\n")
                f.write(f"Shape: {data.shape}\\n")
                f.write(f"Columns: {list(data.columns)}\\n")
                f.write("\\nData:\\n")
                f.write(data.to_string(index=False))
            
        except ImportError:
            # Fallback for non-pandas data
            print(f"Custom endpoint received data:")
            if isinstance(data, list):
                print(f"  Rows: {len(data)}")
                if data:
                    print(f"  Columns: {list(data[0].keys()) if isinstance(data[0], dict) else 'N/A'}")
                    print(f"  Sample data: {data[:3]}")
            else:
                print(f"  Data type: {type(data)}")
                print(f"  Data: {data}")
            
            # Save to file
            output_path = self.get_config('output_path', 'output/custom_data.txt')
            with open(output_path, 'w') as f:
                f.write(f"Data processed at {datetime.now()}\\n")
                if isinstance(data, list):
                    f.write(f"Rows: {len(data)}\\n")
                    f.write(f"Sample data: {data[:5]}\\n")
                else:
                    f.write(f"Data: {data}\\n")
        
        return True
'''
        
        (project_path / "dft" / "sources" / "my_custom_source.py").write_text(example_source)
        (project_path / "dft" / "processors" / "my_custom_processor.py").write_text(example_processor)
        (project_path / "dft" / "endpoints" / "my_custom_endpoint.py").write_text(example_endpoint)
        
        # Create gitignore - will be updated based on state config
        gitignore = """.dft/logs/
.dft/docs/
.env
output/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
"""
        
        # Add state to gitignore based on config (default is ignore_in_git: true)
        gitignore += ".dft/state/\n"
        
        (project_path / ".gitignore").write_text(gitignore)
        
        # Update gitignore based on state configuration
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(project_path)
            from .gitignore import update_gitignore_for_state
            from dft.core.config import ProjectConfig
            
            project_config = ProjectConfig("dft_project.yml")
            update_gitignore_for_state(project_config)
        except Exception as e:
            click.echo(f"Warning: Could not update gitignore for state config: {e}")
        finally:
            os.chdir(old_cwd)
        
        click.echo(f"✅ DFT project '{project_name}' initialized successfully!")
        click.echo(f"📁 Created directory structure:")
        click.echo(f"   {project_name}/")
        click.echo(f"   ├── dft_project.yml")
        click.echo(f"   ├── {pipelines_dir}/")
        click.echo(f"   │   ├── example_pipeline.yml")
        click.echo(f"   │   └── custom_example_pipeline.yml  # Uses custom components")
        click.echo(f"   ├── dft/                      # Custom components")
        click.echo(f"   │   ├── sources/              # Custom data sources")
        click.echo(f"   │   ├── processors/           # Custom processors")
        click.echo(f"   │   └── endpoints/            # Custom endpoints")
        click.echo(f"   ├── tests/")
        click.echo(f"   ├── data/")
        click.echo(f"   │   └── sample.csv            # Sample data for testing")
        click.echo(f"   ├── output/")
        click.echo(f"   ├── .dft/")
        click.echo(f"   ├── .env.example")
        click.echo(f"   └── .gitignore")
        click.echo()
        click.echo(f"Next steps:")
        click.echo(f"1. cd {project_name}")
        click.echo(f"2. cp .env.example .env  # and fill in your credentials")
        click.echo(f"3. dft run --select example_pipeline")
        click.echo(f"4. dft run --select custom_example_pipeline  # Test custom components")
        click.echo()
        click.echo(f"💡 You can now add your own custom components to the dft/ directory!")
        click.echo(f"   - Sources: dft/sources/")
        click.echo(f"   - Processors: dft/processors/")
        click.echo(f"   - Endpoints: dft/endpoints/")
        
    except Exception as e:
        click.echo(f"Error creating project: {e}")
        # Cleanup on error
        if project_path.exists():
            import shutil
            shutil.rmtree(project_path)