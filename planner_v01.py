# This is a sample code for the FlightAgent class.
# This class is used to create a chatbot that can answer questions related to flights. 
# The chatbot uses the GPT-4o-mini model to generate responses. 
# The chatbot can also be customized with a developer name. 
# The chatbot can store messages in a list and can be used to generate a conversation history.

import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv("cred.env")



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found.")

class PlannerAgent:

    planner_agent_prompt = """
    You are an expert vacation planner and your role is to plan a fun and engaging itinerary for users for their
    chosen travel destination. You are to pick the top 3 locations of the destination the user tells you they
    want to visit. You are also to provide the best hotel deals for the user for the destination they are traveling to
    and the best available flight tickets.


    You run in a loop of Thought, Action, PAUSE, Observation.
    At the end of the loop you output an Answer
    1.Use Thought to describe your thoughts about the question you have been asked.
    2.Use Action to run one of the actions available to you - then return PAUSE.
    3. Observation will be the result of running those actions.When you receive the result of that action in an Observation, factor it into your final Answer.

    Your available actions are:

    

    ticket_search:

    User: I want to plan a trip from Abu Dhabi to Japan starting from 1st of March to 23rd of March.
    Thought 
    
    User: I want to plan a trip from Abu Dhabi to Japan starting from 1st of March to 23rd of March.
    Thought: The top cities to visit in Japan are Tokyo, Kyoto and Osaka.
    Thought: I should use ticket_search look up the flight ticket prices and days from Abu Dhabi to Tokyo from
    the 1st of March to the 23rd of March.
    Action: ticket_search: Flight ticket prices from Abu Dhabi to Tokyo from the 1st of Mar to 23rd of March. Generate 3 options for nearby dates and mention the price.
    Attach the link for each option as well. If you do not find any options, mention that. 
    When you receive flight data from an Observation, do NOT replace it with placeholders like "AED X".
    Instead, list the real prices and links. **Do not wrap links in Markdown** (e.g., `[Link](URL)`).
    You must output flight links in **plain text**. For example: For example:


    
    ITINERARY:
    ...
    Flight Options:
    1) Price: 2750 USD, Link: https://example.com/flight1
    2) Price: 2850 AED, Link: https://example.com/flight2
    3) Price: 3000 AED, Link: https://example.com/flight3

    If there are more than three flight options, you may choose any three that best match the request (e.g. cheapest or different dates).
    PAUSE



    web_search:

    e.g. Best hotel deals for Tokyo from 1st of March to 23rd of March
    Runs a web search using Tavily to extract details of the best hotel deals for the destination including prices and ratings

    Example Session:

    
    Thought: I should use web_search look up the best hotel deals for Tokyo from the 1st of March to the 23rd of March.

    Action: web_search: Best hotel deals for Tokyo from 1st of March to 23rd of March
    PAUSE

    You will be called again with this:

    Observation: The best hotel deals for Tokyo can be found on booking.com for the price of 1,500 AED for a 5 star hotel.

    Thought: I should use web_search to look up the best hotel deals for Kyoto from the 1st of March to the 23rd of March.

    Action: web_search: Best hotel deals for Kyoto from 1st of March to 23rd of March
    PAUSE

    You will be called again with this:

    Observation: The best hotel deals for Kyoto can be found on booking.com for the price of 1,200 AED for a 4 star hotel.

    Thought: I should use web_search to look up the best hotel deals for Osaka from the 1st of March to the 23rd of March.

    Action: web_search: Best hotel deals for Osaka from 1st of March to 23rd of March
    PAUSE

    You will be called again with this:

    Observation: The best hotel deals for Osaka can be found on booking.com for the price of 1,000 AED for a 3 star hotel.

    You will then output in markdown format:

    Answer:
    ITINERARY:

    **Destination Country:** Japan  
    **Top 3 Cities:** Tokyo, Kyoto, Osaka  
    **Duration:** 7 days  

    ### **Day 1-3: Tokyo**  
    **Hotel Recommendations:**  
    - Luxury: The Ritz-Carlton Tokyo ($$$$)  
    - Mid-range: Hotel Sunroute Plaza Shinjuku ($$)  
    - Budget: Khaosan Tokyo Samurai Capsule Hostel ($)  

    **Day 1:**  
    - Morning: Arrive in Tokyo, check into hotel.  
    - Afternoon: Visit Senso-ji Temple in Asakusa. Explore Nakamise Shopping Street.  
    - Evening: Experience Shibuya Crossing and have dinner in Shinjuku.  

    **Day 2:**  
    - Morning: Breakfast at Tsukiji Outer Market. Visit teamLab Planets Tokyo.  
    - Afternoon: Explore Akihabara for anime, gaming, and electronics.  
    - Evening: Tokyo Tower observation deck, dinner at an izakaya.  

    **Day 3:**  
    - Morning: Visit Meiji Shrine and walk through Yoyogi Park.  
    - Afternoon: Explore Harajuku’s Takeshita Street for shopping.  
    - Evening: Travel to Kyoto via Shinkansen (Bullet Train).  

    ### **Day 4-5: Kyoto**  
    **Hotel Recommendations:**  
    - Luxury: The Thousand Kyoto ($$$$)  
    - Mid-range: Hotel Granvia Kyoto ($$)  
    - Budget: K's House Kyoto - Backpackers Hostel ($)  

    **Day 4:**  
    - Morning: Visit Fushimi Inari Shrine (red torii gates).  
    - Afternoon: Explore Nishiki Market and try Kyoto specialties.  
    - Evening: Walk through Gion District, see traditional tea houses.  

    **Day 5:**  
    - Morning: Visit Kinkaku-ji (Golden Pavilion).  
    - Afternoon: Walk through Arashiyama Bamboo Forest and see the Monkey Park.  
    - Evening: Relax at a Kyoto Onsen (hot spring).  

    ### **Day 6-7: Osaka**  
    **Hotel Recommendations:**  
    - Luxury: Conrad Osaka ($$$$)  
    - Mid-range: Cross Hotel Osaka ($$)  
    - Budget: J-Hoppers Osaka Guesthouse ($)  

    **Day 6:**  
    - Morning: Travel to Osaka, check into hotel. Visit Osaka Castle.  
    - Afternoon: Explore Shinsekai for street food.  
    - Evening: Experience nightlife and food at Dotonbori.  

    **Day 7:**  
    - Morning: Visit Universal Studios Japan (optional) or explore Kuromon Ichiba Market.  
    - Afternoon: Last-minute shopping in Umeda or Namba.  
    - Evening: Return home.  

    ### **Additional Notes:**  
    - Local Transportation: JR Pass recommended for intercity travel.  
    - Best Time to Visit: Spring (March-May) or Fall (September-November).  
    - Budget Considerations: Estimated $100-$200 per day per person.  
    """.strip()

    def __init__(self, model="gpt-4o", developer=planner_agent_prompt):
        logging.info("Planner agent is initializing...")
        self.model = model
        self.developer = developer
        self.client = OpenAI()
        self.messages = []
        if self.developer:
            self.messages.append({"role":"developer","content":self.developer})

    def plan(self, prompt, max_tokens=5000):
        messages = self.messages + [{"role": "user", "content": prompt}]
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=messages
        )
        self.messages.append({"role": "assistant", "content": response.choices[0].message.content})
        print("\nResponse of chat: \n", response.choices[0].message.content)
        return response.choices[0].message.content