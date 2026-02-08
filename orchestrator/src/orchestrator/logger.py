from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .core import ExecutionResult


class SessionLogger:
    def __init__(self, log_dir: Path) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._session_dir = log_dir / timestamp
        self._session_dir.mkdir(parents=True, exist_ok=True)

    @property
    def session_dir(self) -> Path:
        return self._session_dir

    def log_operation(self, result: ExecutionResult) -> Path:
        data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project": result.project_name,
            "operation": result.operation,
            "success": result.success,
            "return_code": result.return_code,
            "duration_seconds": result.duration_seconds,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
        path = self._session_dir / f"{result.project_name}_{result.operation}.json"
        path.write_text(json.dumps(data, indent=2) + "\n")
        return path

    def log_session_summary(
        self,
        results: list[ExecutionResult],
        total_duration: float,
    ) -> Path:
        data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_duration_seconds": round(total_duration, 1),
            "operations": [
                {
                    "project": r.project_name,
                    "operation": r.operation,
                    "success": r.success,
                    "duration_seconds": r.duration_seconds,
                }
                for r in results
            ],
            "all_succeeded": all(r.success for r in results),
        }
        path = self._session_dir / "session_summary.json"
        path.write_text(json.dumps(data, indent=2) + "\n")
        return path
