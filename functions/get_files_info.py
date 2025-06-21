from pathlib import Path
import os


def get_files_info(working_directory, directory=None) -> str:
    working_dir_abs_path = os.path.abspath(working_directory)
    target_dir = working_dir_abs_path

    if directory:
        target_dir = os.path.join(working_dir_abs_path, directory)
    if not target_dir.startswith(working_dir_abs_path):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    if not Path(target_dir).is_dir():
        return f'Error: "{directory}" is not a directory'
    try:
        dir_elements = os.listdir(target_dir)
        result = [
            f"- {os.path.basename(element)}: file_size={os.path.getsize(os.path.join(target_dir, element))} bytes, is_dir={os.path.isdir(os.path.join(target_dir, element))}"
            for element in dir_elements
        ]
        return "\n".join(result)
    except Exception as e:
        return f"Error listing files: {e}"
