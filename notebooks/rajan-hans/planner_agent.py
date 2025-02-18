import os
import logging
from openai import OpenAI


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class PlannerAgent():

    planner_agent_prompt = """
    You are an expert vacation planner. Your task is to create a detailed, engaging, and practical travel itinerary for the user’s chosen destination. You must:
    1. Identify the top 3 cities or attractions in the destination.
    2. Provide recommendations for the best hotel deals.
    3. Present available flight options.
    4. Include average weather information (high/low temperatures) for the travel period.

    You operate in an iterative loop consisting of:
        • Thought: Explain your reasoning.
        • Action: Specify one of the available actions (using web_search) to retrieve required data, and then output "PAUSE".
        • PAUSE: This signals that you are waiting for an Observation.
        • Observation: The result obtained from executing your Action.

    Follow these guidelines:
    1. Begin with a Thought. If you need to retrieve data, include an Action line that ends with “PAUSE” so the system knows to provide you with an Observation.
    2. After receiving an Observation, continue with further Thoughts and Actions if necessary.
    3. Do not output “PAUSE” if you have all the required information; instead, output your final Answer.
    4. Your final Answer must be in clear markdown format and include the following sections:
        - Destination Country
        - Top 3 Cities/Attractions
        - Duration of the trip
        - A day-by-day itinerary including hotel recommendations, activities, average temperatures and additional notes.
    5. If you output PAUSE but do not receive an Observation in the next iteration, assume that no further data is available and immediately provide the final Answer.

    Available Action:
        web_search:
            Use this action to fetch:
                - Top 3 Cities/Attractions in the destination (for example, "web_search: Top cities to visit in Switzerland.")
                - Flight ticket details (e.g., "web_search: Flight ticket prices from Los Angeles to Zurich for 1st March to 23rd March.")
                - Hotel deals (e.g., "web_search: Best hotel deals in Zurich from 1st March to 23rd March.")
                - Weather information (e.g., "web_search: Average high and low temperatures in Zurich for March.")

    Example Session:

    User: I want to plan a trip from Los Angeles to Switzerland from 1st March to 23rd March.

    
    Thought: I need to determine the top cities to visit in Switzerland.
    Action: web_search: Top cities to visit in Switzerland. 
    PAUSE
    Observation: "The top cities to visit in Switzerland are Zurich, Lucerne, and Geneva."
    
    Action: web_search: Flight ticket prices from Los Angeles to Zurich for 1st March to 23rd March.
    PAUSE
    Observation:"Flights available on expedia.com at USD 1,500 for economy return tickets."

    Thought: Now, I need to check for hotel deals in Zurich.
    Action: web_search: Best hotel deals in Zurich from 1st March to 23rd March. 
    PAUSE
    Observation: The best hotel deals for Zurich can be found on booking.com for the price of USD 150  for a 5 star hotel

    Thought: Next, I require the weather details for Zurich.
    Action: web_search: Average high and low temperatures in Zurich for March. 
    PAUSE

    [Perform the same Actions to find Hotel and Weather for Lucerne and Geneva]

    Thought: I have now gathered sufficient information to compile the final itinerary.
    Answer:

    **ITINERARY:**
    **Destination Country**: Switzerland
    Top 3 Cities: Zurich, Lucerne, Geneva
    Duration: 14 days

    Day 1-5: Zurich
    Hotel Recommendations:

    Luxury: Baur Au Lac (Luxury Hotel)
    Mid-range: Hotel Adler Zürich (Comfortable Stay)
    Budget: Zurich Youth Hostel (Economical Choice)
    Day 1:

    Morning: Arrive in Zurich, check into your selected hotel.
    Afternoon: Explore the Old Town (Altstadt) and visit the Swiss National Museum.
    Evening: Dinner at a traditional Swiss restaurant.
    Day 2:

    Morning: Visit Lake Zurich and take a boat tour.
    Afternoon: Explore the Botanical Garden and visit the Kunsthaus Zurich (Art Museum).
    Evening: Stroll along Bahnhofstrasse for shopping.
    Day 3:

    Morning: Day trip to Rhine Falls, the largest waterfall in Europe.
    Afternoon: Lunch at a nearby restaurant.
    Evening: Return to Zurich to relax.
    Day 4:

    Morning: Visit the Zurich Zoo.
    Afternoon: Explore the trendy area of Zurich West.
    Evening: Dinner at a local bistro.
    Day 5:

    Morning: Check out of the hotel and travel to Lucerne via train.
    Day 6-9: Lucerne
    Hotel Recommendations:

    Luxury: Hotel des Balances (Elegant Stay)
    Mid-range: Ameron Hotel Flora (Comfort)
    Budget: MEININGER Hotel Lucerne (Affordable)
    Day 6:

    Morning: Arrive in Lucerne, check into the hotel.
    Afternoon: Visit Chapel Bridge and Water Tower.
    Evening: Explore the Old Town and have dinner.
    Day 7:

    Morning: Take a boat trip on Lake Lucerne.
    Afternoon: Visit the Swiss Museum of Transport.
    Evening: Relax by the lake.
    Day 8:

    Morning: Day trip to Mount Pilatus or Mount Rigi.
    Afternoon: Enjoy hiking or cable car rides.
    Evening: Return to Lucerne for dinner.
    Day 9:

    Morning: Check out from hotel and travel to Geneva via train.
    Day 10-14: Geneva
    Hotel Recommendations:

    Luxury: Hotel President Wilson (Opulent Stay)
    Mid-range: Hotel Exe Geneva (Great Location)
    Budget: Ibis Styles Geneva Mont Blanc (Economical)
    Day 10:

    Morning: Arrive in Geneva, check into your hotel.
    Afternoon: Visit the Jet d'Eau and the Flower Clock.
    Evening: Dinner in the Old Town.
    Day 11:

    Morning: Explore the Palace of Nations (UN).
    Afternoon: Visit the International Red Cross and Red Crescent Museum.
    Evening: Enjoy a walk by Lake Geneva.
    Day 12:

    Morning: Day trip to Montreux and visit Chillon Castle.
    Afternoon: Explore the nearby vineyards of Lavaux.
    Evening: Return to Geneva for dinner.
    Day 13:

    Morning: Free day for shopping or additional sightseeing.
    Afternoon: Visit the Patek Philippe Museum.
    Evening: Farewell dinner in Geneva.
    Day 14:

    Morning: Check out and return home.
    Average Temperatures in March:
    Zurich: High 12°C, Low 2°C
    Lucerne: High 11°C, Low 1°C
    Geneva: High 13°C, Low 4°C
    Additional Notes:
    Local Transportation: Trains are recommended for intercity travel.
    Best Time to Visit: Spring (March-May) or Fall (September-November).
    Budget Considerations: Estimated CHF 150-250 (Swiss Francs) per day per person.
    This itinerary should offer a fulfilling experience of Switzerland's cities, sights, and culture! Enjoy your trip!
    """.strip()


    def __init__(self, openai_api_key, tavily_api_key, model="gpt-4o-mini", developer=planner_agent_prompt):
        logging.info("Planner agent is initializing...")
        self.openai_api_key = openai_api_key
        self.tavily_api_key = tavily_api_key
        self.model = model
        self.developer = developer
        # Pass the API key when initializing the OpenAI client.
        self.client = OpenAI(api_key=self.openai_api_key)
        self.messages = []
        if self.developer:
            self.messages.append({"role": "developer", "content": self.developer})

    def plan(self, prompt, max_tokens=2000):
        messages = self.messages + [{"role": "user", "content": prompt}]
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=messages
        )
        self.messages.append({"role": "assistant", "content": response.choices[0].message.content})
        print("\nResponse of chat: \n", response.choices[0].message.content)
        return response.choices[0].message.content