"""
Enhanced Bash/Shell command execution tool with improved process management.
"""

import asyncio
import io
import os
import shlex
import signal
import tempfile
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import pexpect

    PEXPECT_AVAILABLE = True
except ImportError:
    # Fallback for environments where pexpect is not available (e.g., Windows)
    pexpect = None
    PEXPECT_AVAILABLE = False

from ..utils import command_sanitizer, path_validator
from .base import ResourceLock, Tool, ToolDefinition, ToolParameter, ToolResult


class ProcessManager:
    """Manages process lifecycle with proper cleanup and resource management."""

    def __init__(self):
        self.active_processes = set()
        self._cleanup_lock: Optional[asyncio.Lock] = None
        self._init_thread_lock = threading.Lock()

    async def _ensure_lock_initialized(self) -> None:
        """Ensure lock is initialized using thread-safe pattern."""
        # Fast path: check if already initialized
        if self._cleanup_lock is not None:
            return

        # Use thread lock for thread-safe lazy initialization
        with self._init_thread_lock:
            # Double-check pattern: check again after acquiring lock
            if self._cleanup_lock is None:
                self._cleanup_lock = asyncio.Lock()

    async def register_process(self, process):
        """Register a process for tracking."""
        await self._ensure_lock_initialized()
        async with self._cleanup_lock:  # type: ignore[union-attr]
            self.active_processes.add(process)

    async def unregister_process(self, process):
        """Unregister a process from tracking."""
        await self._ensure_lock_initialized()
        async with self._cleanup_lock:  # type: ignore[union-attr]
            self.active_processes.discard(process)

    async def cleanup_all(self):
        """Cleanup all active processes."""
        await self._ensure_lock_initialized()
        async with self._cleanup_lock:  # type: ignore[union-attr]
            for process in list(self.active_processes):
                await self._terminate_process(process)
            self.active_processes.clear()

    async def _terminate_process(self, process):
        """Terminate a single process with escalation."""
        if process.returncode is not None:
            return  # Already terminated

        try:
            # Try graceful termination first
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                # Escalate to SIGKILL
                try:
                    process.kill()
                    await asyncio.wait_for(process.wait(), timeout=2.0)
                except asyncio.TimeoutError:
                    # Process is really stuck, try OS-level kill
                    import platform

                    if platform.system() == "Windows":
                        # Windows-specific process termination
                        if process.pid:
                            try:
                                import subprocess  # nosec B404

                                subprocess.run(  # nosec B603 B607
                                    ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                                    check=False,
                                    capture_output=True,
                                )
                            except (OSError, subprocess.SubprocessError):
                                pass
                    else:
                        # Unix-specific process group kill
                        if hasattr(os, "killpg") and process.pid:
                            try:
                                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                            except (OSError, ProcessLookupError):
                                pass
        except (ProcessLookupError, OSError):
            # Process already dead
            pass


# Global process manager instance
_process_manager = ProcessManager()


class BashTool(Tool):
    """Enhanced Bash/Shell command execution tool with robust process management."""

    def __init__(self):
        super().__init__()
        self.process_manager = _process_manager

    @property
    def definition(self) -> ToolDefinition:
        """Define the bash tool specification.

        Returns:
            ToolDefinition with parameters for executing shell commands including
            command, working directory, environment variables, timeout, and
            interactive mode options.
        """
        return ToolDefinition(
            name="bash",
            description="Execute shell commands with advanced features and safety controls",  # noqa: E501
            category="System Operations",  # noqa: E501
            resource_locks=[ResourceLock.SHELL],
            parameters=[
                ToolParameter(
                    name="command",
                    type="string",
                    description="Shell command to execute",
                    required=True,
                ),
                ToolParameter(
                    name="working_dir",
                    type="string",
                    description="Working directory for command execution",
                    required=False,
                    default=".",
                ),
                ToolParameter(
                    name="timeout",
                    type="number",
                    description="Command timeout in seconds (0 = no timeout)",
                    required=False,
                    default=30,
                ),
                ToolParameter(
                    name="capture_output",
                    type="boolean",
                    description="Capture stdout and stderr",
                    required=False,
                    default=True,
                ),
                ToolParameter(
                    name="shell",
                    type="string",
                    description="Shell to use (bash, sh, zsh, fish)",
                    required=False,
                    default="bash",
                ),
                ToolParameter(
                    name="env_vars",
                    type="object",
                    description="Additional environment variables",
                    required=False,
                    default={},
                ),
                ToolParameter(
                    name="input_data",
                    type="string",
                    description="Input data to pipe to the command",
                    required=False,
                ),
                ToolParameter(
                    name="interactive",
                    type="boolean",
                    description="Run in interactive mode (for commands requiring input)",  # noqa: E501
                    required=False,  # noqa: E501
                    default=False,
                ),
                ToolParameter(
                    name="safe_mode",
                    type="boolean",
                    description="Enable safety checks (prevent dangerous commands)",
                    required=False,
                    default=True,
                ),
                ToolParameter(
                    name="show_command",
                    type="boolean",
                    description="Show the command being executed",
                    required=False,
                    default=True,
                ),
            ],
        )

    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute shell command with enhanced features."""
        # Extract parameters
        command = kwargs.get("command")
        if not command:
            return ToolResult(
                success=False,
                output="",
                error="Command parameter is required",
            )
        working_dir = kwargs.get("working_dir", ".")
        timeout = kwargs.get("timeout", 30)
        capture_output = kwargs.get("capture_output", True)
        shell = kwargs.get("shell", "bash")
        env_vars = kwargs.get("env_vars", {})
        input_data = kwargs.get("input_data")
        interactive = kwargs.get("interactive", False)
        safe_mode = kwargs.get("safe_mode", True)
        show_command = kwargs.get("show_command", True)

        try:
            # Validate working directory using centralized validator
            is_valid, error_msg, work_dir = path_validator.validate_path(
                working_dir, check_exists=True
            )
            if not is_valid:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Working directory validation failed: {error_msg}",
                )

            if work_dir and not work_dir.is_dir():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Working directory is not a directory: {working_dir}",
                )

            # Safety checks using enhanced sanitizer
            if safe_mode:
                sanitize_result = command_sanitizer.sanitize_command(
                    str(command), strict_mode=True
                )
                is_safe: bool = sanitize_result[0]
                sanitized_cmd: str = sanitize_result[1]
                sanitize_error: Optional[str] = sanitize_result[2]
                if not is_safe:
                    return ToolResult(
                        success=False,
                        output="",
                        error=f"Command blocked for safety: {sanitize_error}",
                    )
                # Use the sanitized command
                if sanitized_cmd:
                    command = sanitized_cmd

            # Prepare environment with enhanced sanitization
            env = os.environ.copy()
            if env_vars:
                # Use the enhanced sanitizer for environment variables
                safe_env_vars = command_sanitizer.sanitize_environment(env_vars)
                env.update(safe_env_vars)

            # Prepare shell command
            shell_cmd = self._prepare_shell_command(str(command), shell)

            output_lines = []
            if show_command:
                output_lines.append(f"$ {command}")
                output_lines.append("")

            # Execute command
            if interactive and PEXPECT_AVAILABLE:
                result = await self._execute_interactive(
                    shell_cmd, work_dir or Path("."), env, timeout, input_data
                )
            else:
                # Fall back to standard execution if pexpect unavailable
                if interactive and not PEXPECT_AVAILABLE:
                    if show_command:  # Use show_command instead of undefined verbose
                        output_lines.append(
                            "⚠️  Interactive mode unavailable, using standard execution"
                        )
                result = await self._execute_standard(
                    shell_cmd,
                    work_dir or Path("."),
                    env,
                    timeout,
                    capture_output,
                    input_data,
                )

            # Format output
            if result["success"]:
                if result["stdout"]:
                    output_lines.append(result["stdout"])

                if result["stderr"] and capture_output:
                    output_lines.append("STDERR:")
                    output_lines.append(result["stderr"])

                output = "\n".join(output_lines).rstrip()

                return ToolResult(
                    success=True,
                    output=output,
                    metadata={
                        "command": command,
                        "working_dir": str(work_dir),
                        "return_code": result["return_code"],
                        "execution_time": result.get("execution_time", 0),
                        "shell": shell,
                    },
                )
            else:
                error_msg = result["stderr"] or "Command execution failed"
                stdout = result.get("stdout", "")

                # Combine stdout and error for better context
                if stdout:
                    output_lines.append(stdout)

                return ToolResult(
                    success=False,
                    output="\n".join(output_lines).rstrip() if output_lines else "",
                    error=error_msg,
                    metadata={
                        "command": command,
                        "return_code": result["return_code"],
                        "execution_time": result.get("execution_time", 0),
                    },
                )

        except Exception as e:
            return ToolResult(
                success=False, output="", error=f"Command execution failed: {str(e)}"
            )

    def _prepare_shell_command(self, command: str, shell: str) -> List[str]:
        """Prepare shell command for execution with proper sanitization."""
        import platform
        import shutil

        # Windows-specific handling
        if platform.system() == "Windows":
            # On Windows, use cmd.exe or PowerShell
            if shell in ["powershell", "pwsh"]:
                # Use PowerShell if requested and available
                powershell_path = shutil.which("pwsh") or shutil.which("powershell")
                if powershell_path:
                    return [
                        powershell_path,
                        "-ExecutionPolicy",
                        "Bypass",
                        "-Command",
                        f"& {{{command}}}",
                    ]

            # Default to cmd.exe on Windows
            cmd_path = shutil.which("cmd") or "cmd.exe"
            return [cmd_path, "/c", command]

        # Unix-like systems
        shell_map = {
            "bash": "bash",
            "sh": "sh",
            "zsh": "zsh",
            "fish": "fish",
        }

        # Validate shell parameter
        if shell not in shell_map:
            shell = "bash"  # Default to bash

        shell_name = shell_map[shell]

        # Use shutil.which to find the shell executable
        shell_path = shutil.which(shell_name)

        if not shell_path:
            # Fallback shells in order of preference
            fallback_shells = ["bash", "sh", "zsh", "fish"]
            for fallback in fallback_shells:
                shell_path = shutil.which(fallback)
                if shell_path:
                    break
            else:
                # Last resort: use 'sh' command
                shell_path = "sh"

        # Use exec form to prevent shell injection
        return [shell_path, "-c", command]

    @asynccontextmanager
    async def _managed_process(
        self,
        shell_cmd: List[str],
        work_dir: Path,
        env: Dict[str, str],
        capture_output: bool,
        input_data: Optional[str],
    ):
        """Enhanced context manager for proper process cleanup."""
        process = None
        try:
            # Create process with proper settings
            kwargs: Dict[str, Any] = {
                "cwd": str(work_dir),
                "env": env,
            }

            # Set up process group for better cleanup on Unix
            import platform

            if platform.system() != "Windows" and hasattr(os, "setsid"):
                kwargs["start_new_session"] = True  # More portable than preexec_fn

            if capture_output:
                kwargs["stdout"] = asyncio.subprocess.PIPE
                kwargs["stderr"] = asyncio.subprocess.PIPE
                kwargs["stdin"] = asyncio.subprocess.PIPE if input_data else None

            process = await asyncio.create_subprocess_exec(*shell_cmd, **kwargs)

            # Register process for tracking
            await self.process_manager.register_process(process)

            yield process

        finally:
            if process:
                # Unregister process
                await self.process_manager.unregister_process(process)

                # Ensure proper cleanup
                if process.returncode is None:
                    try:
                        # Try graceful termination
                        process.terminate()
                        try:
                            await asyncio.wait_for(process.wait(), timeout=5.0)
                        except asyncio.TimeoutError:
                            # Force kill
                            process.kill()
                            try:
                                await asyncio.wait_for(process.wait(), timeout=2.0)
                            except asyncio.TimeoutError:
                                # Try OS-level process group kill
                                if hasattr(os, "killpg") and process.pid:
                                    try:
                                        os.killpg(
                                            os.getpgid(process.pid), signal.SIGKILL
                                        )
                                    except (OSError, ProcessLookupError):
                                        pass
                    except (ProcessLookupError, OSError):
                        # Process already terminated
                        pass

                # Ensure stdin is closed (stdout/stderr are read-only)
                if process.stdin and not process.stdin.is_closing():
                    process.stdin.close()

    async def _execute_standard(
        self,
        shell_cmd: List[str],
        work_dir: Path,
        env: Dict[str, str],
        timeout: int,
        capture_output: bool,
        input_data: Optional[str],
    ) -> Dict[str, Any]:
        """Execute command in standard mode with enhanced error handling."""
        start_time = time.time()

        try:
            async with self._managed_process(
                shell_cmd, work_dir, env, capture_output, input_data
            ) as process:
                if capture_output:
                    try:
                        # Prepare input
                        input_bytes = None
                        if input_data:
                            input_bytes = input_data.encode("utf-8", errors="replace")

                        # Execute with timeout
                        if timeout > 0:
                            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                                process.communicate(input=input_bytes), timeout=timeout
                            )
                        else:
                            stdout_bytes, stderr_bytes = await process.communicate(
                                input=input_bytes
                            )

                        # Decode output
                        stdout = (
                            stdout_bytes.decode("utf-8", errors="replace")
                            if stdout_bytes
                            else ""
                        )
                        stderr = (
                            stderr_bytes.decode("utf-8", errors="replace")
                            if stderr_bytes
                            else ""
                        )

                        return_code = process.returncode

                    except asyncio.TimeoutError:
                        # Process timed out
                        return {
                            "success": False,
                            "stdout": "",
                            "stderr": f"Command timed out after {timeout} seconds",
                            "return_code": -15,  # SIGTERM
                            "execution_time": time.time() - start_time,
                        }
                else:
                    # No output capture
                    try:
                        if timeout > 0:
                            return_code = await asyncio.wait_for(
                                process.wait(), timeout=timeout
                            )
                        else:
                            return_code = await process.wait()

                        stdout, stderr = "", ""

                    except asyncio.TimeoutError:
                        return {
                            "success": False,
                            "stdout": "",
                            "stderr": f"Command timed out after {timeout} seconds",
                            "return_code": -15,
                            "execution_time": time.time() - start_time,
                        }

            execution_time = time.time() - start_time

            return {
                "success": return_code == 0,
                "stdout": stdout.rstrip() if stdout else "",
                "stderr": stderr.rstrip() if stderr else "",
                "return_code": return_code,
                "execution_time": execution_time,
            }

        except FileNotFoundError as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command not found: {e}",
                "return_code": 127,
                "execution_time": time.time() - start_time,
            }
        except PermissionError as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Permission denied: {e}",
                "return_code": 126,
                "execution_time": time.time() - start_time,
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "return_code": -1,
                "execution_time": time.time() - start_time,
            }

    def _expect_eof_safe(self, child):
        """Safely expect EOF from pexpect child process."""
        if not PEXPECT_AVAILABLE:
            return
        try:
            child.expect(pexpect.EOF)
        except pexpect.TIMEOUT:
            # Expected for timeout scenarios
            pass
        except pexpect.exceptions.ExceptionPexpect:
            # Handle other pexpect exceptions
            pass
        except Exception:  # nosec
            # Catch any other exceptions
            pass

    async def _execute_interactive(
        self,
        shell_cmd: List[str],
        work_dir: Path,
        env: Dict[str, str],
        timeout: int,
        input_data: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute command in interactive mode using pexpect with improved handling."""
        if not PEXPECT_AVAILABLE:
            # Fallback to standard execution if pexpect is not available
            return await self._execute_standard(
                shell_cmd, work_dir, env, timeout, True, input_data
            )
        output_buffer = io.StringIO()
        child = None
        start_time = time.time()

        try:
            # Convert shell command to string
            cmd_str = " ".join(shlex.quote(arg) for arg in shell_cmd)

            # Create pexpect spawn with conservative settings
            child = pexpect.spawn(
                cmd_str,
                cwd=str(work_dir),
                env=env,
                encoding="utf-8",
                timeout=min(timeout, 30) if timeout > 0 else 30,
                maxread=8192,  # Limit read size
            )

            # Set up output capture
            child.logfile_read = output_buffer

            # Send input data if provided
            if input_data:
                input_lines = input_data.splitlines()
                for i, line in enumerate(input_lines):
                    try:
                        # Send line with timeout
                        await asyncio.wait_for(
                            asyncio.get_event_loop().run_in_executor(
                                None, child.sendline, line
                            ),
                            timeout=5.0,
                        )

                        # Small delay between lines
                        if i < len(input_lines) - 1:
                            await asyncio.sleep(0.1)

                    except asyncio.TimeoutError:
                        break

            # Wait for completion
            try:
                remaining_timeout = (
                    max(1, timeout - (time.time() - start_time)) if timeout > 0 else 30
                )

                await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None, self._expect_eof_safe, child
                    ),
                    timeout=remaining_timeout,
                )
            except asyncio.TimeoutError:
                pass

            # Get output and status
            final_output = output_buffer.getvalue()

            # Close child process
            child.close(force=True)
            return_code = child.exitstatus if child.exitstatus is not None else -1

            return {
                "success": return_code == 0,
                "stdout": final_output,
                "stderr": "",  # pexpect combines stdout/stderr
                "return_code": return_code,
                "execution_time": time.time() - start_time,
            }

        except Exception as e:
            # Handle pexpect.TIMEOUT if available, otherwise general Exception
            is_timeout = PEXPECT_AVAILABLE and isinstance(e, pexpect.TIMEOUT)
            if child:
                if is_timeout:
                    child.terminate(force=True)
                else:
                    try:
                        child.terminate(force=True)
                    except Exception:  # nosec
                        pass

            # Return appropriate error message
            error_msg = (
                f"Interactive command timed out after {timeout} seconds"
                if is_timeout
                else str(e)
            )
            return {
                "success": False,
                "stdout": output_buffer.getvalue(),
                "stderr": error_msg,
                "return_code": -1,
                "execution_time": time.time() - start_time,
            }
        finally:
            # Ensure cleanup
            if child and child.isalive():
                try:
                    child.terminate(force=True)
                except Exception:  # nosec
                    pass
            output_buffer.close()


class ScriptTool(Tool):
    """Tool for creating and executing shell scripts."""

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="script",
            description="Create and execute shell scripts with multiple commands",
            category="System Operations",
            resource_locks=[ResourceLock.SHELL, ResourceLock.FILESYSTEM_WRITE],
            parameters=[
                ToolParameter(
                    name="script_content",
                    type="string",
                    description="Script content (multiple commands separated by newlines)",  # noqa: E501
                    required=True,  # noqa: E501
                ),
                ToolParameter(
                    name="script_type",
                    type="string",
                    description="Script type: 'bash', 'sh', 'python', 'node'",
                    required=False,
                    default="bash",
                ),
                ToolParameter(
                    name="working_dir",
                    type="string",
                    description="Working directory for script execution",
                    required=False,
                    default=".",
                ),
                ToolParameter(
                    name="timeout",
                    type="number",
                    description="Script timeout in seconds",
                    required=False,
                    default=60,
                ),
                ToolParameter(
                    name="save_script",
                    type="boolean",
                    description="Save script to temporary file for inspection",
                    required=False,
                    default=False,
                ),
                ToolParameter(
                    name="env_vars",
                    type="object",
                    description="Environment variables for script",
                    required=False,
                    default={},
                ),
            ],
        )

    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute a shell script with proper validation."""
        try:
            # Extract parameters (support both 'script_content' and 'script' for compatibility) # noqa: E501
            script_content = kwargs.get("script_content") or kwargs.get(
                "script"
            )  # noqa: E501
            script_type = kwargs.get("script_type", "bash")
            working_dir = kwargs.get("working_dir", ".")
            timeout = kwargs.get("timeout", 60)
            save_script = kwargs.get("save_script", False)
            env_vars = kwargs.get("env_vars", {})

            if not script_content:
                return ToolResult(
                    success=False, output="", error="No script content provided"
                )

            # Validate working directory
            is_valid, error_msg, work_dir = path_validator.validate_path(
                working_dir, check_exists=True
            )
            if not is_valid:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Working directory validation failed: {error_msg}",
                )

            # Create temporary script file
            script_extensions = {
                "bash": ".sh",
                "sh": ".sh",
                "python": ".py",
                "node": ".js",
                "javascript": ".js",
            }

            extension = script_extensions.get(script_type, ".sh")

            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=extension,
                delete=not save_script,
                encoding="utf-8",
                dir=tempfile.gettempdir(),  # Use system temp dir
            ) as script_file:

                # Add shebang if needed (Unix only)
                import platform

                if platform.system() != "Windows":
                    if script_type == "bash":
                        script_file.write("#!/bin/bash\nset -e\n\n")
                    elif script_type == "python":
                        script_file.write("#!/usr/bin/env python3\n\n")
                    elif script_type in ["node", "javascript"]:
                        script_file.write("#!/usr/bin/env node\n\n")

                script_file.write(script_content)
                script_file.flush()

                # Make script executable (Unix only)
                if platform.system() != "Windows":
                    os.chmod(script_file.name, 0o700)  # User read/write/execute only

                # Prepare execution command
                import shutil

                if script_type == "bash":
                    if platform.system() == "Windows":
                        # Use cmd or find bash on Windows
                        bash_path = shutil.which("bash") or shutil.which("git-bash")
                        if bash_path:
                            # Use shell=True to handle paths with spaces on Windows
                            cmd = [bash_path, script_file.name]
                        else:
                            # Fallback to cmd reading the script
                            cmd = [
                                shutil.which("cmd") or "cmd.exe",
                                "/c",
                                f"type {script_file.name} | cmd",
                            ]
                    else:
                        cmd = [shutil.which("bash") or "bash", script_file.name]
                elif script_type == "python":
                    python_cmd = (
                        shutil.which("python3") or shutil.which("python") or "python"
                    )
                    cmd = [python_cmd, script_file.name]
                elif script_type in ["node", "javascript"]:
                    node_cmd = shutil.which("node") or "node"
                    cmd = [node_cmd, script_file.name]
                else:
                    if platform.system() == "Windows":
                        cmd = [shutil.which("cmd") or "cmd.exe", "/c", script_file.name]
                    else:
                        cmd = [shutil.which("sh") or "sh", script_file.name]

                # Execute script using appropriate method for platform
                if (
                    platform.system() == "Windows"
                    and script_type == "bash"
                    and len(cmd) >= 2
                    and work_dir is not None
                ):
                    # On Windows with bash, execute directly to avoid quoting issues
                    result = await self._execute_script_directly(
                        cmd, work_dir, timeout, env_vars
                    )
                else:
                    # Use BashTool for other cases
                    bash_tool = BashTool()
                    command_str = self._build_cross_platform_command(cmd)
                    result = await bash_tool.execute(
                        command=command_str,
                        working_dir=str(work_dir),
                        timeout=timeout,
                        env_vars=env_vars,
                        safe_mode=False,  # Scripts are created by us
                        show_command=True,
                    )

                # Add script info to metadata
                if result.metadata:
                    result.metadata.update(
                        {
                            "script_type": script_type,
                            "script_path": (
                                script_file.name if save_script else "temporary"
                            ),
                            "script_size": len(script_content),
                        }
                    )

                if save_script:
                    result.output = f"Script saved to: {script_file.name}\n\n" + (
                        result.output or ""
                    )

                return result

        except Exception as e:
            return ToolResult(
                success=False, output="", error=f"Script execution failed: {str(e)}"
            )

    async def _execute_script_directly(
        self, cmd: List[str], work_dir: Path, timeout: int, env_vars: dict
    ) -> ToolResult:
        """Execute script directly without going through cmd.exe on Windows."""
        import asyncio
        import time

        start_time = time.time()

        try:
            # Prepare environment
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)

            # Execute directly using asyncio.create_subprocess_exec
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(work_dir),
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout if timeout > 0 else None
                )

                stdout_str = stdout.decode("utf-8", errors="replace") if stdout else ""
                stderr_str = stderr.decode("utf-8", errors="replace") if stderr else ""

                execution_time = time.time() - start_time

                # Format output similar to BashTool
                output_lines = [f"$ {' '.join(cmd)}", ""]
                if stdout_str:
                    output_lines.append(stdout_str.rstrip())

                success = process.returncode == 0

                return ToolResult(
                    success=success,
                    output="\n".join(output_lines).rstrip() if success else stdout_str,
                    error=stderr_str if not success else "",
                    metadata={
                        "command": " ".join(cmd),
                        "working_dir": str(work_dir),
                        "return_code": process.returncode,
                        "execution_time": execution_time,
                    },
                )

            except asyncio.TimeoutError:
                process.kill()
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Script timed out after {timeout} seconds",
                    metadata={"command": " ".join(cmd), "return_code": -15},
                )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Script execution failed: {str(e)}",
                metadata={"command": " ".join(cmd)},
            )

    def _build_cross_platform_command(self, cmd: List[str]) -> str:
        """Build a command string that works on both Windows and Unix."""
        import platform

        if platform.system() == "Windows":
            # On Windows, use double quotes for paths with spaces
            quoted_args = []
            for arg in cmd:
                if " " in arg and not (arg.startswith('"') and arg.endswith('"')):
                    quoted_args.append(f'"{arg}"')
                else:
                    quoted_args.append(arg)
            return " ".join(quoted_args)
        else:
            # On Unix, use shlex.quote for proper escaping
            return " ".join(shlex.quote(arg) for arg in cmd)
