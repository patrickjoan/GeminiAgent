import os
from pathlib import Path


def write_file(working_directory: str, file_path: str, content: str) -> str:
    try:
        working_dir = Path(working_directory).resolve()
        target_file = Path(working_dir, file_path).resolve()

        try:
            target_file.relative_to(working_dir)
        except ValueError:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        target_file.write_text(content)

        return (
            f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        )
    except Exception as e:
        return f"Error: {e}"
