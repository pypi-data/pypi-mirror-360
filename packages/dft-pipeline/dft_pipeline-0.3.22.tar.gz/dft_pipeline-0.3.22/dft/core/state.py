"""State management for incremental processing"""

import json
import fcntl
import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, date
from contextlib import contextmanager
import logging


class StateManager(ABC):
    """Abstract base class for state management"""
    
    @abstractmethod
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get state value by key"""
        pass
    
    @abstractmethod
    def set_state(self, key: str, value: Any) -> None:
        """Set state value by key"""
        pass
    
    @abstractmethod
    def clear_state(self, key: str = None) -> None:
        """Clear state (all or specific key)"""
        pass


class FileStateManager(StateManager):
    """File-based state manager with atomic writes and file locking"""
    
    def __init__(self, state_dir: str = ".dft/state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("dft.state.file")
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get state value from file with shared locking"""
        state_file = self.state_dir / f"{key}.json"
        
        if not state_file.exists():
            return default
        
        try:
            with self._file_lock(state_file, fcntl.LOCK_SH):
                with open(state_file, 'r') as f:
                    data = json.load(f)
                    return data.get('value', default)
        except json.JSONDecodeError as e:
            # Try backup file if main file is corrupted
            backup_file = state_file.with_suffix('.backup')
            if backup_file.exists():
                self.logger.warning(f"Main state file {key} corrupted, trying backup: {e}")
                try:
                    with open(backup_file, 'r') as f:
                        data = json.load(f)
                        return data.get('value', default)
                except Exception:
                    pass
            self.logger.warning(f"Failed to read state {key}: {e}")
            return default
        except Exception as e:
            self.logger.warning(f"Failed to read state {key}: {e}")
            return default
    
    def set_state(self, key: str, value: Any) -> None:
        """Set state value to file with exclusive locking and atomic writes"""
        state_file = self.state_dir / f"{key}.json"
        
        # Convert dates to strings for JSON serialization
        if isinstance(value, (date, datetime)):
            value = value.isoformat()
        
        try:
            with self._file_lock(state_file, fcntl.LOCK_EX):
                # Create backup before writing
                self._create_backup(state_file)
                
                data = {
                    'value': value,
                    'updated_at': datetime.now().isoformat(),
                }
                
                # Atomic write
                self._atomic_write(state_file, data)
                
            self.logger.debug(f"Set state {key} = {value}")
            
        except Exception as e:
            self.logger.error(f"Failed to set state {key}: {e}")
            raise
    
    def clear_state(self, key: str = None) -> None:
        """Clear state file(s)"""
        if key:
            state_file = self.state_dir / f"{key}.json"
            if state_file.exists():
                with self._file_lock(state_file, fcntl.LOCK_EX):
                    state_file.unlink()
                    # Also remove backup if exists
                    backup_file = state_file.with_suffix('.backup')
                    if backup_file.exists():
                        backup_file.unlink()
                self.logger.info(f"Cleared state {key}")
        else:
            # Clear all state files
            for state_file in self.state_dir.glob("*.json"):
                if not state_file.name.endswith('.backup') and not state_file.name.endswith('.lock'):
                    with self._file_lock(state_file, fcntl.LOCK_EX):
                        state_file.unlink()
                        # Also remove backup if exists
                        backup_file = state_file.with_suffix('.backup')
                        if backup_file.exists():
                            backup_file.unlink()
            self.logger.info("Cleared all state")
    
    @contextmanager
    def _file_lock(self, state_file: Path, lock_type: int):
        """Context manager for file locking"""
        lock_file = state_file.with_suffix('.lock')
        lock_file.touch()
        
        with open(lock_file, 'r+') as lock_fd:
            try:
                # Try non-blocking lock first
                fcntl.flock(lock_fd.fileno(), lock_type | fcntl.LOCK_NB)
            except IOError:
                # If non-blocking fails, use blocking lock with timeout info
                self.logger.debug(f"Waiting for lock on {state_file.name}...")
                fcntl.flock(lock_fd.fileno(), lock_type)
                self.logger.debug(f"Acquired lock on {state_file.name}")
            
            try:
                yield
            finally:
                # Lock automatically released when file is closed
                pass
    
    def _create_backup(self, state_file: Path) -> None:
        """Create backup of existing state file"""
        if state_file.exists():
            backup_file = state_file.with_suffix('.backup')
            try:
                shutil.copy2(state_file, backup_file)
                self.logger.debug(f"Created backup: {backup_file.name}")
            except IOError as e:
                # Backup is not critical, just log warning
                self.logger.warning(f"Failed to create backup for {state_file.name}: {e}")
    
    def _atomic_write(self, state_file: Path, data: dict) -> None:
        """Atomically write data to state file"""
        temp_file = state_file.with_suffix('.tmp')
        
        try:
            # Write to temporary file
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                f.flush()
                # Force write to disk
                os.fsync(f.fileno())
            
            # Atomic rename
            temp_file.rename(state_file)
            self.logger.debug(f"Atomically wrote to {state_file.name}")
            
        except Exception as e:
            # Clean up temp file on error
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    pass
            raise e


class PipelineState:
    """Pipeline-specific state management"""
    
    def __init__(self, pipeline_name: str, state_manager: StateManager = None):
        self.pipeline_name = pipeline_name
        self.state_manager = state_manager or FileStateManager()
        self.prefix = f"pipeline_{pipeline_name}"
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get pipeline state"""
        full_key = f"{self.prefix}_{key}"
        return self.state_manager.get_state(full_key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set pipeline state"""
        full_key = f"{self.prefix}_{key}"
        self.state_manager.set_state(full_key, value)
    
    def get_last_processed_date(self, default: str = None) -> Optional[str]:
        """Get last processed date for incremental loading"""
        return self.get("last_processed_date", default)
    
    def set_last_processed_date(self, date_value: str) -> None:
        """Set last processed date"""
        self.set("last_processed_date", date_value)
    
    def get_run_history(self) -> list:
        """Get pipeline run history"""
        return self.get("run_history", [])
    
    def add_run_record(self, status: str, start_time: datetime, end_time: datetime = None, error: str = None) -> None:
        """Add run record to history"""
        history = self.get_run_history()
        
        record = {
            "status": status,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat() if end_time else None,
            "error": error,
        }
        
        history.append(record)
        
        # Keep only last 100 records
        if len(history) > 100:
            history = history[-100:]
        
        self.set("run_history", history)
    
    def clear(self) -> None:
        """Clear all pipeline state"""
        # This is a bit tricky with file-based storage
        # We'd need to list all files with our prefix
        pass


class IncrementalProcessor:
    """Helper class for incremental processing logic"""
    
    def __init__(self, pipeline_state: PipelineState):
        self.state = pipeline_state
        self.logger = logging.getLogger(f"dft.incremental.{pipeline_state.pipeline_name}")
    
    def get_date_range_to_process(
        self, 
        start_date: str = None, 
        end_date: str = None,
        default_lookback_days: int = 30
    ) -> tuple[str, str]:
        """
        Determine date range for incremental processing
        
        Args:
            start_date: Override start date
            end_date: Override end date  
            default_lookback_days: Days to look back if no state exists
            
        Returns:
            Tuple of (start_date, end_date) as strings
        """
        from datetime import datetime, timedelta
        
        # Determine end date
        if end_date:
            process_end_date = end_date
        else:
            # Default to yesterday
            yesterday = (datetime.now() - timedelta(days=1)).date()
            process_end_date = yesterday.isoformat()
        
        # Determine start date
        if start_date:
            process_start_date = start_date
        else:
            # Get from state or use default lookback
            last_processed = self.state.get_last_processed_date()
            if last_processed:
                # Start from day after last processed
                last_date = datetime.fromisoformat(last_processed).date()
                process_start_date = (last_date + timedelta(days=1)).isoformat()
            else:
                # No previous state, use default lookback
                start_date_obj = datetime.now().date() - timedelta(days=default_lookback_days)
                process_start_date = start_date_obj.isoformat()
        
        self.logger.info(f"Processing date range: {process_start_date} to {process_end_date}")
        return process_start_date, process_end_date
    
    def mark_date_processed(self, date_str: str) -> None:
        """Mark a specific date as processed"""
        self.state.set_last_processed_date(date_str)
        self.logger.debug(f"Marked {date_str} as processed")
    
