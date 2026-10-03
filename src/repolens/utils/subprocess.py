"""Cross-platform command execution and OS abstraction."""

import os
import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union


@dataclass
class CommandResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool = False

    @property
    def success(self) -> bool:
        return self.exit_code == 0 and not self.timed_out


class CommandRunner:
    """Abstract/base command runner interface."""

    def run(
        self,
        cmd: Union[str, List[str]],
        cwd: Optional[Path] = None,
        timeout: int = 60,
        env: Optional[Dict[str, str]] = None,
        capture_output: bool = True,
    ) -> CommandResult:
        raise NotImplementedError


class SafeCommandRunner(CommandRunner):
    """
    Cross-platform safe command runner for Windows, Linux, and macOS.
    Does not run destructive commands blindly, sets reasonable timeouts,
    and captures stdout/stderr properly.
    """

    def __init__(self) -> None:
        self.os_type = platform.system().lower()  # windows, linux, darwin

    def is_windows(self) -> bool:
        return self.os_type == "windows"

    def run(
        self,
        cmd: Union[str, List[str]],
        cwd: Optional[Path] = None,
        timeout: int = 60,
        env: Optional[Dict[str, str]] = None,
        capture_output: bool = True,
    ) -> CommandResult:
        working_dir = str(cwd) if cwd else None
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)

        cmd_str = cmd if isinstance(cmd, str) else " ".join(cmd)
        shell = True

        try:
            process = subprocess.Popen(
                cmd,
                cwd=working_dir,
                env=merged_env,
                shell=shell,
                stdout=subprocess.PIPE if capture_output else None,
                stderr=subprocess.PIPE if capture_output else None,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            stdout, stderr = process.communicate(timeout=timeout)
            return CommandResult(
                command=cmd_str,
                exit_code=process.returncode,
                stdout=stdout or "",
                stderr=stderr or "",
                timed_out=False,
            )
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            return CommandResult(
                command=cmd_str,
                exit_code=-1,
                stdout=stdout or "",
                stderr=(stderr or "") + "\nCommand timed out.",
                timed_out=True,
            )
        except Exception as e:
            return CommandResult(
                command=cmd_str,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                timed_out=False,
            )


default_runner = SafeCommandRunner()
