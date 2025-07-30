from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
import threading
from typing import Any, Dict


class LogBus:
    """Simple JSONL logging service."""

    def __init__(self, log_dir: str | Path | None = None) -> None:
        if log_dir:
            self.log_dir = Path(log_dir)
        else:
            # Use workspace-aware path logic (similar to IssueTracker)
            workspace_base = os.environ.get("WORKSPACE_BASE", "/workspace")
            
            # CRITICAL: Check if workspace_base contains Python paths (ROOT CAUSE)
            if ("/usr/local/lib/python" in workspace_base or 
                "/site-packages" in workspace_base or
                workspace_base.endswith("python3.11") or
                "site-packages" in workspace_base):
                # Force to safe path if Python installation path detected
                workspace_base = "/tmp/diagram_to_iac"
            
            # Additional safety: Check current working directory
            cwd = os.getcwd()
            if ("/usr/local/lib/python" in cwd or "/site-packages" in cwd):
                # If running from Python installation, force workspace to /tmp
                workspace_base = "/tmp/diagram_to_iac"
            
            # Try to use workspace, fallback to /tmp if not accessible
            try:
                base_dir = Path(workspace_base)
                
                # Check if we can actually write to the workspace
                if base_dir == Path("/workspace"):
                    # Test if workspace is writable
                    test_path = base_dir / "logs"
                    try:
                        test_path.mkdir(parents=True, exist_ok=True)
                        # Test write access
                        test_file = test_path / "test_write.tmp"
                        test_file.write_text("test")
                        test_file.unlink()
                        self.log_dir = test_path
                    except (PermissionError, OSError):
                        # Workspace not writable, use /tmp
                        self.log_dir = Path("/tmp/diagram_to_iac/logs")
                elif base_dir.exists() and base_dir.is_dir():
                    self.log_dir = base_dir / "logs"
                else:
                    self.log_dir = Path("/tmp/diagram_to_iac/logs")
            except (PermissionError, OSError):
                self.log_dir = Path("/tmp/diagram_to_iac/logs")
        
        # Final safety check
        if "/usr/local/lib/python" in str(self.log_dir) or "/site-packages" in str(self.log_dir):
            self.log_dir = Path("/tmp/diagram_to_iac/logs")
        
        # Ensure log directory exists and is writable
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError):
            # Final fallback to /tmp
            self.log_dir = Path("/tmp/diagram_to_iac/logs")
            self.log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.log_path = self.log_dir / f"run-{timestamp}.jsonl"
        self._lock = threading.Lock()

    def log(self, event: Dict[str, Any]) -> None:
        """Append an event as a JSON line with timestamp."""
        payload = event.copy()
        payload.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        line = json.dumps(payload)
        with self._lock:
            try:
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
            except Exception as exc:  # noqa: BLE001
                # Logging should never raise; print error and continue
                print(f"LogBus write failed: {exc}")


_global_bus: LogBus | None = None


def _get_bus() -> LogBus:
    global _global_bus
    if _global_bus is None:
        _global_bus = LogBus()
    return _global_bus


def log_event(event_type: str, **kwargs: Any) -> None:
    """Write a structured log event using the global bus."""
    event = {"type": event_type, **kwargs}
    _get_bus().log(event)


def get_log_path() -> Path:
    """Return the path of the current log file."""
    return _get_bus().log_path


def reset_log_bus() -> None:
    """Create a fresh global log bus with a new log file."""
    global _global_bus
    # Nothing to close since LogBus opens files on demand
    _global_bus = LogBus()
