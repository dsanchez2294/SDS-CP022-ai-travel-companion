import openai
from dotenv import load_dotenv
import os

# Load environment variables from cred.env
load_dotenv("cred.env")

# Retrieve the API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in cred.env")

# Set the API key for the openai package
openai.api_key = api_key

# Attempt to list available engines as a simple test of the API key
try:
    engines = openai.Engine.list()
    print("API key is working. Available engines:")
    for engine in engines.data:
        print(engine.id)
except Exception as e:
    print("An error occurred:", e)
