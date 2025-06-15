import os
from urllib.parse import uses_relative
from dotenv import load_dotenv
from google import genai
from google.genai import types
from sys import argv

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
        model="gemini-2.0-flash-001", contents=messages
    )
    print(response.text)
    if verbose:
        print(f"User prompt: {user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")


if __name__ == "__main__":
    main()
