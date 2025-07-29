"""
Simple Bash tool for maxs agent.

Execute shell commands safely with timeout and error handling.
Perfect for system administration, file operations, and automation.
"""

from pathlib import Path
import shlex
import subprocess

from strands import tool


@tool
def bash(command: str, timeout: int = 30, shell: bool = True) -> dict:
    """
    Execute a bash/shell command and return the output.

    Args:
        command: The shell command to execute
        timeout: Timeout in seconds (default: 30)
        shell: Whether to use shell mode (default: True)

    Returns:
        Dictionary with command output and status
    """
    try:
        # Execute the command
        if shell:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path.cwd(),
            )
        else:
            # Split command for non-shell mode
            cmd_parts = shlex.split(command)
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path.cwd(),
            )

        # Format output
        output_lines = []

        if result.stdout:
            output_lines.append(f"📤 Output:\n{result.stdout}")

        if result.stderr:
            output_lines.append(f"⚠️ Error output:\n{result.stderr}")

        if result.returncode != 0:
            output_lines.append(f"❌ Exit code: {result.returncode}")
        else:
            output_lines.append(f"✅ Command completed successfully (exit code: 0)")

        return {
            "status": "success" if result.returncode == 0 else "error",
            "content": [{"text": "\n\n".join(output_lines)}],
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "content": [{"text": f"⏰ Command timed out after {timeout} seconds"}],
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "content": [
                {
                    "text": f"❌ Command not found: {command.split()[0] if command.split() else command}"
                }
            ],
        }
    except Exception as e:
        return {
            "status": "error",
            "content": [{"text": f"❌ Error executing command: {str(e)}"}],
        }
