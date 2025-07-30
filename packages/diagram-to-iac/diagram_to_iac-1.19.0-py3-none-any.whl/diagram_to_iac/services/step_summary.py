from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


def _parse_timestamp(ts: str) -> datetime:
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        # Fallback for timestamps that may not be ISO formatted
        return datetime.strptime(ts.split(".")[0], "%Y-%m-%dT%H:%M:%S")


def generate_step_summary(log_path: str | Path, output_path: str | Path, *, stdout: bool = False) -> str:
    """Generate a Markdown step summary from JSONL logs."""
    log_path = Path(log_path)
    output_path = Path(output_path)

    modules: set[str] = set()
    adds = changes = destroys = 0
    critical = high = medium = low = 0
    start: datetime | None = None
    end: datetime | None = None

    if not log_path.exists():
        raise FileNotFoundError(log_path)

    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            ts = data.get("timestamp")
            if ts:
                ts_dt = _parse_timestamp(ts)
                if start is None or ts_dt < start:
                    start = ts_dt
                if end is None or ts_dt > end:
                    end = ts_dt
            result = data.get("result", "")
            if result:
                modules.update(re.findall(r"module\.([\w-]+)", result))
                m = re.search(r"Plan:\s*(\d+)\s*to\s*add,\s*(\d+)\s*to\s*change,\s*(\d+)\s*to\s*destroy", result)
                if m:
                    adds = int(m.group(1))
                    changes = int(m.group(2))
                    destroys = int(m.group(3))
                m = re.search(r"(\d+)\s*critical", result, re.IGNORECASE)
                if m:
                    critical = int(m.group(1))
                m = re.search(r"(\d+)\s*high", result, re.IGNORECASE)
                if m:
                    high = int(m.group(1))
                m = re.search(r"(\d+)\s*medium", result, re.IGNORECASE)
                if m:
                    medium = int(m.group(1))
                m = re.search(r"(\d+)\s*low", result, re.IGNORECASE)
                if m:
                    low = int(m.group(1))

    runtime = (end - start).total_seconds() if start and end else 0
    modules_str = ", ".join(sorted(modules)) if modules else "root"

    md = (
        "| Module | Adds | Changes | Destroys | Critical | High | Medium | Low | Run Time (s) |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        f"| {modules_str} | {adds} | {changes} | {destroys} | {critical} | {high} | {medium} | {low} | {int(runtime)} |\n"
    )

    output_path.write_text(md, encoding="utf-8")
    if stdout:
        print(md)
    return md
