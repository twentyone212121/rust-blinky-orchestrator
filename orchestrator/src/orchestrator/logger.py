from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .core import ExecutionResult


class SessionLogger:
    def __init__(self, log_dir: Path) -> None:
        self._log_file = log_dir / "orchestrator.jsonl"
        self._log_file.parent.mkdir(parents=True, exist_ok=True)
        self._session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    @property
    def log_file(self) -> Path:
        return self._log_file

    def log_operation(self, result: ExecutionResult) -> None:
        data = {
            "type": "operation",
            "session_id": self._session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project": result.project_name,
            "operation": result.operation,
            "board": result.board,
            "command": result.command,
            "success": result.success,
            "return_code": result.return_code,
            "duration_seconds": result.duration_seconds,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
        with self._log_file.open("a") as f:
            f.write(json.dumps(data) + "\n")

    def log_session_summary(
        self,
        results: list[ExecutionResult],
        total_duration: float,
    ) -> None:
        data = {
            "type": "summary",
            "session_id": self._session_id,
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
        with self._log_file.open("a") as f:
            f.write(json.dumps(data) + "\n")
