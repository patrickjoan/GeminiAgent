# GeminiAgent

GeminiAgent is a command-line AI coding assistant powered by Google's Gemini API. It can list files, read and write file contents, and execute Python scripts within a secure, sandboxed `./calculator` directory.
Made as part of the boot.dev AI agent course

## Features

- List files and directories
- Read file contents
- Write or overwrite files
- Run Python scripts with optional arguments
- All operations are restricted to the `./calculator` working directory for safety

## Usage

1. Install dependencies:
uv pip install -r requirements.txt

2. Set your Gemini API key in a `.env` file:
GEMINI_API_KEY=your_api_key_here

3. Run the agent with a prompt:
uv run main.py "read the contents of main.py" uv run main.py "run tests.py" --verbose

## How it works

- The agent interprets your prompt and decides which tool/function to use.
- It performs the requested operation and prints the result.
- All file paths are relative to `./calculator` and access outside is blocked.
