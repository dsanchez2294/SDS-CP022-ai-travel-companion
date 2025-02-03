import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY not found.")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found.")

MODEL = "gpt-4o-mini"

messages = [
    "role":"assistant","content":"You are a helpful assistant and your roles is to advice users on flight tickets and hotel bookings."
]

while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit', 'quit']:
        break

    messages.append({"role": "user", "content": user_input})

    client = OpenAI()
    completion = client.chat.completions.create(
        model=MODEL,
        messages=messages
    )

    ai_response = completion.choices[0].message.content
    messages.append({"role": "assistant", "content": ai_response})
    print("AI: ", ai_response)