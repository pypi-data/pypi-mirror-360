"""
Simple file operations tool for maxs agent.

Basic file reading, writing, and manipulation - the essentials.
"""

import shutil
from pathlib import Path

from strands import tool


@tool
def read_file(file_path: str, max_lines: int = 100) -> dict:
    """
    Read contents of a text file.

    Args:
        file_path: Path to the file to read
        max_lines: Maximum number of lines to read (default: 100)

    Returns:
        Dictionary with file contents
    """
    try:
        path = Path(file_path)

        if not path.exists():
            return {
                "status": "error",
                "content": [{"text": f"❌ File not found: {file_path}"}],
            }

        if not path.is_file():
            return {
                "status": "error",
                "content": [{"text": f"❌ Not a file: {file_path}"}],
            }

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) > max_lines:
            content = "".join(lines[:max_lines])
            truncated_msg = (
                f"\n\n📏 Truncated to {max_lines} lines (total: {len(lines)} lines)"
            )
        else:
            content = "".join(lines)
            truncated_msg = ""

        return {
            "status": "success",
            "content": [{"text": f"📄 {file_path}:\n{content}{truncated_msg}"}],
        }

    except UnicodeDecodeError:
        return {
            "status": "error",
            "content": [{"text": f"❌ Cannot read binary file: {file_path}"}],
        }
    except Exception as e:
        return {
            "status": "error",
            "content": [{"text": f"❌ Error reading file: {str(e)}"}],
        }


@tool
def write_file(file_path: str, content: str, append: bool = False) -> dict:
    """
    Write content to a file.

    Args:
        file_path: Path to the file to write
        content: Content to write
        append: Whether to append (default: False, overwrites)

    Returns:
        Dictionary with operation result
    """
    try:
        path = Path(file_path)

        # Create directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        mode = "a" if append else "w"
        with open(path, mode, encoding="utf-8") as f:
            f.write(content)

        action = "appended to" if append else "written to"
        size = path.stat().st_size

        return {
            "status": "success",
            "content": [{"text": f"✅ Content {action} {file_path} ({size} bytes)"}],
        }

    except Exception as e:
        return {
            "status": "error",
            "content": [{"text": f"❌ Error writing file: {str(e)}"}],
        }


@tool
def copy_file(source: str, destination: str) -> dict:
    """
    Copy a file from source to destination.

    Args:
        source: Source file path
        destination: Destination file path

    Returns:
        Dictionary with operation result
    """
    try:
        src_path = Path(source)
        dst_path = Path(destination)

        if not src_path.exists():
            return {
                "status": "error",
                "content": [{"text": f"❌ Source file not found: {source}"}],
            }

        # Create destination directory
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(src_path, dst_path)

        return {
            "status": "success",
            "content": [{"text": f"✅ Copied {source} → {destination}"}],
        }

    except Exception as e:
        return {
            "status": "error",
            "content": [{"text": f"❌ Error copying file: {str(e)}"}],
        }


@tool
def file_info(file_path: str) -> dict:
    """
    Get information about a file or directory.

    Args:
        file_path: Path to examine

    Returns:
        Dictionary with file information
    """
    try:
        path = Path(file_path)

        if not path.exists():
            return {
                "status": "error",
                "content": [{"text": f"❌ Path not found: {file_path}"}],
            }

        stat = path.stat()

        info_lines = [
            f"📋 File Info: {file_path}",
            f"Type: {'Directory' if path.is_dir() else 'File'}",
            f"Size: {stat.st_size:,} bytes",
            f"Modified: {stat.st_mtime}",
            f"Permissions: {oct(stat.st_mode)[-3:]}",
        ]

        if path.is_file():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    lines = sum(1 for _ in f)
                info_lines.append(f"Lines: {lines}")
            except:
                info_lines.append("Lines: (binary file)")

        return {"status": "success", "content": [{"text": "\n".join(info_lines)}]}

    except Exception as e:
        return {
            "status": "error",
            "content": [{"text": f"❌ Error getting file info: {str(e)}"}],
        }
