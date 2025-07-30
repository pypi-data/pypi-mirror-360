import json
import os
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

try:
    from .config_loader import get_config_value
except ImportError:
    # Fallback for tests or standalone usage
    def get_config_value(path: str, default: any = None) -> any:
        return default

class IssueTracker:
    """Simple persistent tracker for GitHub issues keyed by repo and error type."""

    def __init__(self, file_path: Optional[str] = None):
        if file_path is None:
            # Debug: Check current working directory
            cwd = os.getcwd()
            logger.debug(f"IssueTracker: Current working directory = {cwd}")
            
            # Get workspace base from environment variable first, then config with fallback
            workspace_base = os.environ.get("WORKSPACE_BASE")
            logger.debug(f"IssueTracker: WORKSPACE_BASE env var = {workspace_base}")
            
            if not workspace_base:
                # Try to get from config
                try:
                    workspace_base = get_config_value("system.workspace_base", "/workspace")
                    logger.debug(f"IssueTracker: workspace_base from config = {workspace_base}")
                except Exception as e:
                    logger.debug(f"IssueTracker: Failed to get workspace_base from config: {e}")
                    workspace_base = "/workspace"
            
            # Safeguard: Never use Python installation paths or current working directory if it's a Python path
            if (workspace_base and 
                "/usr/local/lib/python" not in workspace_base and 
                "/site-packages" not in workspace_base and
                not workspace_base.startswith(cwd) if "/usr/local/lib/python" in cwd else True):
                
                try:
                    base_dir = Path(workspace_base)
                    logger.debug(f"IssueTracker: Using workspace base_dir = {base_dir}")
                    
                    # For container environments, always try /workspace first
                    if base_dir == Path("/workspace"):
                        data_dir = base_dir / "data" / "db"
                        data_dir.mkdir(parents=True, exist_ok=True)
                        file_path = str(data_dir / "issue_tracker.json")
                        logger.debug(f"IssueTracker: Using workspace path = {file_path}")
                    # For other paths, check if they exist and are writable
                    elif base_dir.exists() and base_dir.is_dir():
                        # Test if we can write to this directory
                        test_file = base_dir / "test_write_access"
                        try:
                            with open(test_file, "x"):
                                pass
                            test_file.unlink()
                            data_dir = base_dir / "data" / "db"
                            data_dir.mkdir(parents=True, exist_ok=True)
                            file_path = str(data_dir / "issue_tracker.json")
                            logger.debug(
                                f"IssueTracker: Using accessible workspace path = {file_path}"
                            )
                        except (PermissionError, OSError):
                            raise PermissionError(
                                f"Workspace directory {base_dir} not writable"
                            )
                    else:
                        raise PermissionError(f"Workspace directory {base_dir} not accessible")
                        
                except (PermissionError, OSError) as e:
                    logger.debug(f"IssueTracker: Workspace not accessible ({e}), falling back to /tmp")
                    # Fallback to /tmp for container environments
                    data_dir = Path("/tmp") / "diagram_to_iac" / "data" / "db"
                    data_dir.mkdir(parents=True, exist_ok=True)
                    file_path = str(data_dir / "issue_tracker.json")
                    logger.debug(f"IssueTracker: Using tmp path = {file_path}")
            else:
                logger.debug(f"IssueTracker: Invalid workspace_base ({workspace_base}) or unsafe cwd ({cwd}), using /tmp")
                # Always fallback to /tmp if workspace_base is invalid or points to Python paths
                data_dir = Path("/tmp") / "diagram_to_iac" / "data" / "db"
                data_dir.mkdir(parents=True, exist_ok=True)
                file_path = str(data_dir / "issue_tracker.json")
                logger.debug(f"IssueTracker: Using tmp fallback path = {file_path}")
                
        self.file_path = Path(file_path)
        logger.debug(f"IssueTracker: Final file_path = {self.file_path}")
        
        # Final safety check: ensure the path is never in Python installation
        if "/usr/local/lib/python" in str(self.file_path) or "/site-packages" in str(self.file_path):
            logger.warning(f"IssueTracker: Detected Python installation path {self.file_path}, forcing /tmp fallback")
            data_dir = Path("/tmp") / "diagram_to_iac" / "data" / "db"
            data_dir.mkdir(parents=True, exist_ok=True)
            self.file_path = data_dir / "issue_tracker.json"
            logger.debug(f"IssueTracker: Corrected file_path = {self.file_path}")
        
        self._table: Dict[str, Dict[str, int]] = {}
        self._load()

    def _load(self) -> None:
        """Load the issue tracker data from file."""
        if self.file_path.exists():
            try:
                with open(self.file_path, "r") as f:
                    self._table = json.load(f)
                logger.debug(f"IssueTracker: Loaded {len(self._table)} repos from {self.file_path}")
            except Exception as e:
                logger.warning(f"IssueTracker: Failed to load from {self.file_path}: {e}")
                self._table = {}
        else:
            # File doesn't exist, start with empty table
            # Directory was already created in __init__, so no need to create again
            self._table = {}
            logger.debug(f"IssueTracker: Starting with empty table at {self.file_path}")

    def _save(self) -> None:
        """Save the issue tracker data to file."""
        try:
            # Directory was already created in __init__, no need to create again
            with open(self.file_path, "w") as f:
                json.dump(self._table, f, indent=2)
            logger.debug(f"IssueTracker: Saved {len(self._table)} repos to {self.file_path}")
        except Exception as e:
            logger.error(f"IssueTracker: Failed to save to {self.file_path}: {e}")
            pass

    def get_issue(self, repo_url: str, error_type: str) -> Optional[int]:
        return self._table.get(repo_url, {}).get(error_type)

    def record_issue(self, repo_url: str, error_type: str, issue_id: int) -> None:
        repo_map = self._table.setdefault(repo_url, {})
        repo_map[error_type] = issue_id
        self._save()

    def clear(self) -> None:
        self._table = {}
        if self.file_path.exists():
            try:
                self.file_path.unlink()
            except Exception:
                pass
