import os
from urllib.parse import uses_relative
from dotenv import load_dotenv
from google import genai
from google.genai import types
from sys import argv
from functions.get_files_info import available_functions

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
user_prompt = str(argv[1])

verbose = False
if "--verbose" in argv:
    verbose = True

if len(user_prompt) == 0:
    print("Prompt content cannot be empty. Please provide a valid prompt.")
    exit(1)


def main():
    print("Starting the Gemini API client...")
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
    )
    if response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'function_call') and part.function_call:
                print(
                    f"Calling function: {part.function_call.name}({part.function_call.args})"
                )
            elif hasattr(part, 'text') and part.text:
                print(part.text)
    if verbose:
        print(f"User prompt: {user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")


if __name__ == "__main__":
    main()
