import os
from dotenv import load_dotenv
from google import genai
from sys import argv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
prompt_content = str(argv[1])

if len(prompt_content) == 0:
    print("Prompt content cannot be empty. Please provide a valid prompt.")
    exit(1)


def main():
    print("Starting the Gemini API client...")
    response = client.models.generate_content(
        model="gemini-2.0-flash-001", contents=prompt_content
    )
    print(response.text)
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")


if __name__ == "__main__":
    main()
