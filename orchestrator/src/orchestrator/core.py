from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExecutionResult:
    project_name: str
    operation: str
    success: bool
    return_code: int
    duration_seconds: float
    stdout: str
    stderr: str


class WestExecutor:
    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose

    def check_west(self) -> None:
        try:
            subprocess.run(
                ["west", "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
        except FileNotFoundError:
            raise SystemExit("Error: west not found. Activate the Zephyr venv first.")

    def build(
        self,
        project_dir: Path,
        board: str,
        pristine: bool = False,
    ) -> ExecutionResult:
        cmd = ["west", "build", "-b", board]
        if pristine:
            cmd.extend(["-p", "always"])
        return self._run(cmd, project_dir, project_dir.name, "build")

    def flash(self, project_dir: Path) -> ExecutionResult:
        cmd = ["west", "flash"]
        return self._run(cmd, project_dir, project_dir.name, "flash")

    def _run(
        self,
        cmd: list[str],
        cwd: Path,
        project_name: str,
        operation: str,
    ) -> ExecutionResult:
        start = time.perf_counter()

        if self.verbose:
            proc = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            stdout_lines: list[str] = []
            assert proc.stdout is not None
            for line in proc.stdout:
                sys.stdout.write(line)
                stdout_lines.append(line)
            proc.wait()
            stdout = "".join(stdout_lines)
            assert proc.stderr is not None
            stderr = proc.stderr.read()
            if stderr:
                sys.stderr.write(stderr)
            return_code = proc.returncode
        else:
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
            stdout = result.stdout
            stderr = result.stderr
            return_code = result.returncode

        duration = time.perf_counter() - start

        return ExecutionResult(
            project_name=project_name,
            operation=operation,
            success=return_code == 0,
            return_code=return_code,
            duration_seconds=round(duration, 1),
            stdout=stdout,
            stderr=stderr,
        )
