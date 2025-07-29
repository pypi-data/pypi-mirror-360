"""Logging configuration for DFT"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich import box


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: Optional[str] = None
) -> None:
    """Setup dual logging - rich console + file"""
    
    # Create log directory if specified
    if log_dir:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        if not log_file:
            log_file = f"{log_dir}/dft_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Create console with rich handler
    console = Console()
    
    # Setup handlers
    handlers = [
        RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            rich_tracebacks=True,
            markup=True,
            show_level=False  # Don't show log level in console
        )
    ]
    
    # Add file handler if specified (with full format)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(message)s",  # Rich handler will format nicely
        handlers=handlers
    )
    
    # Set DFT logger level
    logging.getLogger("dft").setLevel(getattr(logging, level.upper()))


class PipelineLogger:
    """Enhanced pipeline logger with rich console output"""
    
    def __init__(self, pipeline_name: str):
        self.pipeline_name = pipeline_name
        # Keep logger for file logging only
        self.logger = logging.getLogger(f"dft.pipeline.{pipeline_name}")
        # Disable console output for this logger to avoid duplication
        self.logger.propagate = False
        
        # Add file handler if not already present
        if not self.logger.handlers:
            from pathlib import Path
            log_dir = Path(".dft/logs")
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"{pipeline_name}.log"
            
            file_handler = logging.FileHandler(log_file)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            self.logger.setLevel(logging.INFO)
        
        # Create completely isolated console for clean pipeline output
        import sys
        self.console = Console(file=sys.stdout, stderr=False, force_terminal=True, legacy_windows=False)
        self.executions = []
        
        # Track steps for progress
        self.total_steps = 0
        self.completed_steps = 0
        self.current_step = None
    
    def set_total_steps(self, count: int) -> None:
        """Set total number of steps for progress tracking"""
        self.total_steps = count
        self.completed_steps = 0
    
    def log_pipeline_start(self, batch_info: Optional[str] = None) -> str:
        """Log pipeline start with clean formatting"""
        execution_id = f"{self.pipeline_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Clean logging output like dbt
        if batch_info:
            self.console.print(f"Running {self.total_steps} steps for {batch_info}")
        else:
            self.console.print(f"Running {self.total_steps} steps")
        self.console.print("")  # Empty line for separation
        
        return execution_id
    
    def log_pipeline_complete(self, execution_id: str, success: bool) -> None:
        """Log pipeline completion with summary"""
        if success:
            self.console.print(f"\n[bold green]Completed successfully[/bold green]")
        else:
            self.console.print(f"\n[bold red]Completed with {self.total_steps - self.completed_steps} error(s)[/bold red]")
        
        # No additional logging to avoid Rich handler conflicts
    
    def log_step_start(self, step_id: str) -> None:
        """Log step start with progress"""
        self.current_step = step_id
        
        # Progress indicator like dbt
        step_num = self.completed_steps + 1
        self.console.print(f"{step_num:2d} of {self.total_steps:2d} START {step_id}..................................... [RUN]", end="", style="")
        
        # Standard logging for file only
        # self.logger.info(f"Step '{step_id}' started")
    
    def log_step_complete(self, step_id: str, success: bool, row_count: int = 0, size_mb: float = 0.0) -> None:
        """Log step completion with metrics and rich formatting"""
        self.completed_steps += 1
        
        if success:
            # Metrics display
            metrics_parts = []
            if row_count > 0:
                metrics_parts.append(f"{row_count:,} rows")
            if size_mb > 0:
                metrics_parts.append(f"{size_mb:.2f}MB")
            
            metrics_text = f" {', '.join(metrics_parts)}" if metrics_parts else ""
            
            # Complete the line started in log_step_start - like dbt format
            self.console.print(f" [bold green]OK[/bold green]{metrics_text}")
        else:
            self.console.print(f" [bold red]ERROR[/bold red]")
        
        # Standard logging for file only
        # status = "SUCCESS" if success else "FAILED"
        # self.logger.info(f"Step '{step_id}' completed with status: {status}, rows: {row_count}, size: {size_mb:.2f}MB")
    
    def log_step_error(self, step_id: str, error: str) -> None:
        """Log step error with rich formatting"""
        self.completed_steps += 1
        
        # Complete the line started in log_step_start with error
        self.console.print(f" [bold red]ERROR[/bold red]")
        self.console.print(f"  {error}")
        
        # Log to file
        if self.logger:
            self.logger.error(f"Step '{step_id}' failed: {error}")
    
    def log_metrics(self, step_id: str, metrics: dict) -> None:
        """Log step metrics"""
        if self.logger:
            self.logger.info(f"Step '{step_id}' metrics: {metrics}")