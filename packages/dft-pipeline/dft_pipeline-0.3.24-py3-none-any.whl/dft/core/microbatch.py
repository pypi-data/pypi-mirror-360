"""Simple microbatch strategy for DFT pipelines"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from enum import Enum
import logging

from .state import PipelineState


class BatchPeriod(Enum):
    """Supported batch periods"""
    MINUTE_10 = "10min"
    HOUR = "hour"
    DAY = "day" 
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


@dataclass
class BatchWindow:
    """Time window for batch processing"""
    start: datetime
    end: datetime
    period: BatchPeriod
    
    def __str__(self) -> str:
        return f"{self.period.value}[{self.start.isoformat()}-{self.end.isoformat()}]"


@dataclass
class MicrobatchConfig:
    """Microbatch configuration"""
    event_time_column: str
    batch_size: BatchPeriod
    lookback: int = 1
    begin: Optional[datetime] = None
    end: Optional[datetime] = None


class MicrobatchStrategy:
    """Simple microbatch strategy - generates windows and runs pipeline in cycle"""
    
    def __init__(self, config: MicrobatchConfig, pipeline_name: str):
        self.config = config
        self.pipeline_name = pipeline_name
        self.state = PipelineState(pipeline_name)
        self.logger = logging.getLogger(f"dft.microbatch.{pipeline_name}")
    
    def get_batch_windows(self) -> List[BatchWindow]:
        """Get list of batch windows to process"""
        
        # Get last processed timestamp
        last_processed = self._get_last_processed_timestamp()
        now = datetime.now(timezone.utc)
        
        # Determine start time
        if last_processed is None:
            if self.config.begin is None:
                raise ValueError("begin time must be specified for initial microbatch run")
            start_time = self.config.begin
        else:
            # Apply lookback - go back N periods from last processed
            start_time = self._subtract_periods(last_processed, self.config.lookback)
        
        # Determine end time
        end_time = self.config.end if self.config.end else now
        
        # Generate windows
        windows = []
        current_start = start_time
        
        while current_start < end_time:
            current_end = self._add_period(current_start)
            
            # Don't go beyond end_time
            if current_end > end_time:
                current_end = end_time
            
            windows.append(BatchWindow(
                start=current_start,
                end=current_end,
                period=self.config.batch_size
            ))
            
            current_start = current_end
        
        return windows
    
    def get_batch_variables(self, window: BatchWindow) -> Dict[str, Any]:
        """Get variables for batch processing"""
        return {
            'batch_start': window.start.isoformat(),
            'batch_end': window.end.isoformat(),
            'event_time_column': self.config.event_time_column,
            'batch_period': window.period.value,
        }
    
    def mark_window_processed(self, window: BatchWindow) -> None:
        """Mark batch window as successfully processed"""
        self.state.set("last_microbatch_timestamp", window.end.isoformat())
        self.logger.debug(f"Marked window {window} as processed")
    
    def _get_last_processed_timestamp(self) -> Optional[datetime]:
        """Get last processed timestamp from state"""
        timestamp_str = self.state.get("last_microbatch_timestamp")
        if timestamp_str:
            return datetime.fromisoformat(timestamp_str)
        return None
    
    def _add_period(self, dt: datetime) -> datetime:
        """Add one period to datetime"""
        period = self.config.batch_size
        
        if period == BatchPeriod.MINUTE_10:
            return dt + timedelta(minutes=10)
        elif period == BatchPeriod.HOUR:
            return dt + timedelta(hours=1)
        elif period == BatchPeriod.DAY:
            return dt + timedelta(days=1)
        elif period == BatchPeriod.WEEK:
            return dt + timedelta(weeks=1)
        elif period == BatchPeriod.MONTH:
            return dt + timedelta(days=30)
        elif period == BatchPeriod.YEAR:
            return dt + timedelta(days=365)
        
        raise ValueError(f"Unsupported period: {period}")
    
    def _subtract_periods(self, dt: datetime, count: int) -> datetime:
        """Subtract N periods from datetime"""
        if count == 0:
            return dt
            
        period = self.config.batch_size
        
        if period == BatchPeriod.MINUTE_10:
            return dt - timedelta(minutes=10 * count)
        elif period == BatchPeriod.HOUR:
            return dt - timedelta(hours=count)
        elif period == BatchPeriod.DAY:
            return dt - timedelta(days=count)
        elif period == BatchPeriod.WEEK:
            return dt - timedelta(weeks=count)
        elif period == BatchPeriod.MONTH:
            return dt - timedelta(days=30 * count)
        elif period == BatchPeriod.YEAR:
            return dt - timedelta(days=365 * count)
        
        raise ValueError(f"Unsupported period: {period}")