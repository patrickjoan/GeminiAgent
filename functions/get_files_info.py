from pathlib import Path
import os


def get_files_info(working_directory, directory=None) -> str:
    try:
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
    except Exception as e:
        return f"Error: {e}"


def get_file_content(working_directory, file_path) -> str:
    try:
        working_dir_abs_path = os.path.abspath(working_directory)
        file_path = os.path.join(working_dir_abs_path, file_path)

        if not file_path.startswith(working_dir_abs_path):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        if not Path(file_path).is_file():
            return f'Error: File not found or is not a regular file: "{file_path}"'

        file_content = ""
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                file_content = file.read()
            except UnicodeDecodeError:
                return f'Error: Cannot read "{file_path}" due to encoding issues'

        if len(file_content) > 10000:
            file_content = file_content[:10000] + f'[...File "{file_path}"'
        return file_content
    except Exception as e:
        return f"Error: {e}"
