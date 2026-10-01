from dotenv import load_dotenv
from google import genai
import os


# Load variables from .env
load_dotenv()


# Get API key
api_key = os.getenv("GEMINI_API_KEY")


# Check API key
if not api_key:
    print("API key not found!")
    exit()


# Create Gemini client
client = genai.Client(
    api_key=api_key
)


# Send a simple question
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="Explain what a UAV is in two simple sentences."
)


# Display response
print("\nGemini Response:")
print(response.text)