import os
from urllib.parse import uses_relative
from dotenv import load_dotenv
from google import genai
from google.genai import types
from sys import argv
from functions.function_call import available_functions, function_map

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

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


def call_function(function_call_part, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    function_name = function_call_part.name
    
    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    
    args = dict(function_call_part.args)
    args["working_directory"] = "./calculator"
    
    try:
        function_result = function_map[function_name](**args)
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": function_result},
                )
            ],
        )
    except Exception as e:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Function execution failed: {str(e)}"},
                )
            ],
        )


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
            if hasattr(part, "function_call") and part.function_call:
                function_call_result = call_function(part.function_call, verbose)
                
                # Check if the response has the expected structure
                if not hasattr(function_call_result, 'parts') or len(function_call_result.parts) == 0:
                    raise Exception("Function call result missing parts")
                
                if not hasattr(function_call_result.parts[0], 'function_response'):
                    raise Exception("Function call result missing function_response")
                
                if not hasattr(function_call_result.parts[0].function_response, 'response'):
                    raise Exception("Function call result missing response")
                
                response_data = function_call_result.parts[0].function_response.response
                if "result" in response_data:
                    print(response_data["result"])
                elif "error" in response_data:
                    print(f"Error: {response_data['error']}")
                
                if verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")
                    
            elif hasattr(part, "text") and part.text:
                print(part.text)
                
    if verbose:
        print(f"User prompt: {user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")


if __name__ == "__main__":
    main()
