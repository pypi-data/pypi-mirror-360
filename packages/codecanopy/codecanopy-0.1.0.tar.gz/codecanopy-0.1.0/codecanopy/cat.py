"""Cat command implementation."""

import os
from pathlib import Path
from typing import List, Optional

from .config import Config
from .utils import collect_files, format_header, get_file_size, is_text_file


class CatGenerator:
    """Generate concatenated file contents."""

    def __init__(self, config: Config):
        self.config = config

    def generate(
        self,
        patterns: List[str],
        exclude_patterns: List[str] = None,
        header_format: str = None,
        show_headers: bool = True,
        max_file_size: str = None,
        base_path: Path = None,
    ) -> str:
        """Generate concatenated file contents."""

        if base_path is None:
            base_path = Path.cwd()

        # Validate inputs
        if not patterns:
            return "No file patterns specified."

        header_format = header_format or self.config.get(
            "header_format", "=== {path} ==="
        )
        max_size_str = max_file_size or self.config.get("max_file_size", "")

        try:
            max_size_bytes = self.config.parse_size(max_size_str)
        except (ValueError, TypeError):
            max_size_bytes = float("inf")

        # Collect files
        try:
            files = collect_files(patterns, exclude_patterns, base_path)
        except Exception as e:
            return f"Error collecting files: {e}"

        if not files:
            return "No files found matching the specified patterns."

        output_lines = []
        processed_count = 0

        for file_path in files:
            try:
                # Check file size
                file_size = get_file_size(file_path)
                if file_size > max_size_bytes:
                    if show_headers:
                        header = format_header(header_format, file_path, base_path)
                        output_lines.append(header)
                    output_lines.append(
                        f"[File too large: {self._format_size(file_size)}, skipped]"
                    )
                    output_lines.append("")
                    continue

                # Check if file is text
                if not is_text_file(file_path):
                    if show_headers:
                        header = format_header(header_format, file_path, base_path)
                        output_lines.append(header)
                    output_lines.append("[Binary file, skipped]")
                    output_lines.append("")
                    continue

                # Add header
                if show_headers:
                    header = format_header(header_format, file_path, base_path)
                    output_lines.append(header)

                # Add file content
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        # Remove trailing whitespace but preserve intentional empty lines
                        content = content.rstrip()
                        output_lines.append(content)
                        processed_count += 1
                except (IOError, OSError, UnicodeDecodeError) as e:
                    output_lines.append(f"[Error reading file: {e}]")

                # Add separator between files (but not after the last file)
                output_lines.append("")

            except Exception as e:
                output_lines.append(f"[Error processing {file_path}: {e}]")
                output_lines.append("")

        if processed_count == 0:
            return "No files could be processed (all were binary, too large, or had errors)."

        # Remove the last empty line if present
        if output_lines and output_lines[-1] == "":
            output_lines.pop()

        return "\n".join(output_lines)

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
