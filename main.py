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

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons. The working directory is set to "./calculator".
You can only access files and directories within the working directory. If a file or directory is outside the working directory, you should return an error message indicating that it cannot be accessed.

When you call a function, you will receive a response that may contain either a result or an error message. If the function call is successful, return the result. If there is an error, return the error message.:
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
    
    max_iterations = 20
    final_response = None
    
    for iteration in range(max_iterations):
        try:
            if verbose:
                print(f"Iteration {iteration + 1}/{max_iterations}")
            
            response = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions], system_instruction=system_prompt
                ),
            )
            
            if not response.candidates:
                print("Error: No candidates in response")
                break
                
            candidate = response.candidates[0]
            messages.append(candidate.content)
            
            function_called = False
            if hasattr(candidate.content, "parts") and candidate.content.parts:
                for part in candidate.content.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        function_called = True
                        function_call_result = call_function(part.function_call, verbose)
                        
                        if (
                            not hasattr(function_call_result, "parts")
                            or len(function_call_result.parts) == 0
                        ):
                            raise Exception("Function call result missing parts")

                        if not hasattr(function_call_result.parts[0], "function_response"):
                            raise Exception("Function call result missing function_response")

                        if not hasattr(
                            function_call_result.parts[0].function_response, "response"
                        ):
                            raise Exception("Function call result missing response")
                        
                        response_data = function_call_result.parts[0].function_response.response
                        if isinstance(response_data, dict) and "result" in response_data:
                            print(response_data["result"])
                            if verbose:
                                print(f"-> Function completed successfully")
                        elif isinstance(response_data, dict) and "error" in response_data:
                            print(f"Error: {response_data['error']}")
                            if verbose:
                                print(f"-> Function failed with error")
                        elif verbose:
                            print(f"-> {response_data}")
                        
                        messages.append(function_call_result)
            
            # Check for text responses
            has_text = False
            if hasattr(candidate.content, "parts") and candidate.content.parts:
                for part in candidate.content.parts:
                    if hasattr(part, "text") and part.text:
                        final_response = part.text
                        print(part.text)
                        has_text = True
                        
            # Exit conditions
            if has_text and not function_called:
                if verbose:
                    print(f"-> Conversation completed after {iteration + 1} iterations")
                break
            
            if not function_called and not has_text:
                print("Error: No function calls or text in response")
                break
                
        except Exception as e:
            print(f"Error during iteration {iteration + 1}: {e}")
            break
    else:
        print(f"Warning: Reached maximum iterations ({max_iterations}). Conversation may be incomplete.")
        if final_response:
            print(f"Last response: {final_response}")
        else:
            print("No final text response received.")
    
    if verbose:
        print(f"User prompt: {user_prompt}")
        print(f"Completed {iteration + 1}/{max_iterations} iterations")
        if 'response' in locals():
            usage_metadata = getattr(response, "usage_metadata", None)
            if usage_metadata:
                print(f"Prompt tokens: {getattr(usage_metadata, 'prompt_token_count', 'N/A')}")
                print(f"Response tokens: {getattr(usage_metadata, 'candidates_token_count', 'N/A')}")


if __name__ == "__main__":
    main()
