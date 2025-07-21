from pathlib import Path
import os
from google.genai import types

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Read file contents, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to read from, relative to the working directory.",
            ),
        },
        required=["file_path"],
    ),
)


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
