import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv("cred.env")
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found.")

class SummarizerAgent:

    summarizer_agent_prompt = """
    You are a helpful assistant which helps summarize sentences to extract the most relevant data.

    For example, You may receive the following sentence:
    
    On average, a lodging in Tokyo costs $203 per night at Bulgari Hotel Tokyo (based on Booking.com Located in Tokyo, a 3-minute walk from Central Tokyo, Bulgari Hotel Tokyo 
    has accommodations with a garden, private parking, a terrace and a bar

    And you can summarize accordingly:
    The average cost of a lodging in Tokyo is $203 per night at the Bulgari Hotel Tokyo which is located in Tokyo and is a 3-minute walk from Central Tokyo.

    When you receive flight data from an Observation, do NOT replace it with placeholders like "AED X". Do not summarize.
    Instead, list the real prices and links. **Do not wrap links in Markdown** (e.g., `[Link](URL)`).
    You must output flight links in **plain text**. For example: For example:
    
    However when info comes with a link, such as ticket prices, do not summarize and show the complete url.

IMPORTANT: 
- You must copy flight links EXACTLY from the Observation flight data. 
- It is FORBIDDEN to replace them with placeholders. 
- If the aggregator link is "https://www.skyscanner.com/...", you must produce exactly that string in the final answer. 
- Do NOT reformat or rewrite them.



    
    """.strip()

    def __init__(self, model="gpt-4o-mini", developer=summarizer_agent_prompt):
        logging.info("Summarizer agent is initializing...")
        self.model = model
        self.developer = developer
        self.client = OpenAI()
        self.messages = []
        if self.developer:
            self.messages.append({"role":"developer","content":self.developer})

    def summarize(self, prompt, max_tokens=2000):
        # Ensure prompt is a string
        if not isinstance(prompt, str):
            
            prompt = json.dumps(prompt, indent=2)

        messages = self.messages + [{"role": "user", "content": prompt}]
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=messages
        )
        self.messages.append({"role": "assistant", "content": response.choices[0].message.content})
        print("\nResponse of chat: \n", response.choices[0].message.content)
        return response.choices[0].message.content