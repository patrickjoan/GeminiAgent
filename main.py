import os
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

When you call a function, you will receive a response that may contain either a result or an error message. If the function call is successful, return the result. If there is an error, return the error message.
"""

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
user_prompt = str(argv[1])
verbose = "--verbose" in argv

if len(user_prompt) == 0:
    print("Prompt content cannot be empty. Please provide a valid prompt.")
    exit(1)


def call_function(function_call_part, verbose=False):
    """Execute a function call and return the result as Content."""
    print_func = lambda msg: print(f"Calling function: {function_call_part.name}({function_call_part.args})") if verbose else print(f" - Calling function: {function_call_part.name}")
    print_func("")
    
    function_name = function_call_part.name
    
    if function_name not in function_map:
        return create_tool_response(function_name, {"error": f"Unknown function: {function_name}"})

    args = dict(function_call_part.args)
    args["working_directory"] = "./calculator"

    try:
        function_result = function_map[function_name](**args)
        return create_tool_response(function_name, {"result": function_result})
    except Exception as e:
        return create_tool_response(function_name, {"error": f"Function execution failed: {str(e)}"})


def create_tool_response(function_name, response_data):
    """Create a tool response Content object."""
    return types.Content(
        role="tool",
        parts=[types.Part.from_function_response(name=function_name, response=response_data)]
    )


def validate_function_response(function_call_result):
    """Validate that function response has expected structure."""
    checks = [
        (hasattr(function_call_result, "parts") and len(function_call_result.parts) > 0, "missing parts"),
        (hasattr(function_call_result.parts[0], "function_response"), "missing function_response"),
        (hasattr(function_call_result.parts[0].function_response, "response"), "missing response")
    ]
    
    for condition, error_msg in checks:
        if not condition:
            raise Exception(f"Function call result {error_msg}")


def handle_function_call(part, verbose):
    """Handle a single function call."""
    function_call_result = call_function(part.function_call, verbose)
    validate_function_response(function_call_result)
    
    response_data = function_call_result.parts[0].function_response.response
    
    if isinstance(response_data, dict):
        if "result" in response_data:
            print(response_data["result"])
            if verbose:
                print("-> Function completed successfully")
        elif "error" in response_data:
            print(f"Error: {response_data['error']}")
            if verbose:
                print("-> Function failed with error")
    elif verbose:
        print(f"-> {response_data}")
    
    return function_call_result


def process_response_parts(candidate, verbose):
    """Process all parts of a response, handling both function calls and text."""
    function_called = False
    has_text = False
    final_response = None
    function_results = []
    
    if hasattr(candidate.content, "parts") and candidate.content.parts:
        for part in candidate.content.parts:
            if hasattr(part, "function_call") and part.function_call:
                function_called = True
                function_result = handle_function_call(part, verbose)
                function_results.append(function_result)
            elif hasattr(part, "text") and part.text:
                final_response = part.text
                print(part.text)
                has_text = True
    
    return function_called, has_text, final_response, function_results


def main():
    print("Starting the Gemini API client...")
    messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]
    
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
                    tools=[available_functions], 
                    system_instruction=system_prompt
                ),
            )
            
            if not response.candidates:
                print("Error: No candidates in response")
                break
                
            candidate = response.candidates[0]
            messages.append(candidate.content)
            
            function_called, has_text, final_response, function_results = process_response_parts(candidate, verbose)
            
            messages.extend(function_results)
            
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
        if 'response' in locals() and hasattr(response, "usage_metadata"):
            usage = response.usage_metadata
            print(f"Prompt tokens: {getattr(usage, 'prompt_token_count', 'N/A')}")
            print(f"Response tokens: {getattr(usage, 'candidates_token_count', 'N/A')}")


if __name__ == "__main__":
    main()
