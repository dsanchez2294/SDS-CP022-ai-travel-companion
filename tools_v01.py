import os
import logging
from dotenv import load_dotenv
from tavily import TavilyClient
import datetime

load_dotenv("cred.env")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY not found.")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class SearchWeb:
    
    DOMAINS = [
        'https://www.expedia.ae/',
        'https://www.skyscanner.ae/',
        'https://www.etihad.com/en-ae/',
        'https://www.booking.com/'
    ]

    def __init__(self):
        logging.info("Web search tool is being called...")
        self.client = TavilyClient(TAVILY_API_KEY)

    def search(self, search_input, include_domains=DOMAINS):
        response = self.client.search(search_input, include_domains=include_domains)
        response_list = [resp["content"] for resp in response["results"]]
        responses = " ".join(response_list)
        return responses

class TicketSearch:
    
    def __init__(self, api_key):
        self.client = TavilyClient(api_key)

    def date_range(self, start_date, end_date):
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        delta = datetime.timedelta(days=1)
        current = start
        while current <= end:
            yield current.strftime("%Y-%m-%d")
            current += delta

    def get_flight_data(self, origin, destination, start_date, end_date):
        flights = []
        for date in self.date_range(start_date, end_date):
            search_input = f"Flights from {origin} to {destination} departing on {date} and returning on {date}"
            response = self.client.search(search_input)
            if response:
                for flight in response.get('best_flights', []):
                    for segment in flight.get('flights', []):
                        flight_info = {
                            'departure_airport': segment['departure_airport']['name'],
                            'arrival_airport': segment['arrival_airport']['name'],
                            'departure_time': segment['departure_airport']['time'],
                            'arrival_time': segment['arrival_airport']['time'],
                            'airline': segment['airline'],
                            'price': flight['price']
                        }
                        flights.append(flight_info)
            else:
                logging.error("Error: No response from Tavily API")
        return flights