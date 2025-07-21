from pathlib import Path
import subprocess
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs target python file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write to, relative to the working directory. If the file does not exist, it will be created.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                ),
                description="Optional arguments to pass to the Python script.",
            ),
        },
    ),
)


def run_python_file(working_directory, file_path, args=[]):
    if args is None:
        args = []
    try:
        working_dir = Path(working_directory).resolve()
        target_file = Path(working_dir, file_path).resolve()

        try:
            target_file.relative_to(working_dir)
        except ValueError:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not target_file.exists():
            return f'Error: File "{file_path}" not found.'

        if target_file.suffix != ".py":
            return f'Error: "{file_path}" is not a Python file.'

        completed_process = subprocess.run(
            ["python3", str(target_file)] + args,
            cwd=str(working_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if completed_process.returncode != 0:
            return f"Error: Python file execution failed with return code {completed_process.returncode}"
        if completed_process.stdout == "" and completed_process.stderr == "":
            return "No output produced"

        process_output = f"STDOUT: {completed_process.stdout.strip()}\nSTDERR: {completed_process.stderr.strip()}"

        return process_output
    except Exception as e:
        return f"Error: executing Python file: {e}"
