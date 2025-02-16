import os
import logging
from dotenv import load_dotenv
from tavily import TavilyClient
import datetime
import re

load_dotenv("cred.env")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY not found.")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class TicketSearchTwoStep:
    
    def __init__(self):
        self.client = TavilyClient(TAVILY_API_KEY)

    def date_range(self, start_date, end_date):
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        delta = datetime.timedelta(days=1)
        current = start
        while current <= end:
            yield current.strftime("%Y-%m-%d")
            current += delta

    def fetch_aggregator_data(self, origin, destination, start_date, end_date):
        """
        STEP 1:
        Fetch aggregator text data from Tavily's 'results' field.
        Return a list of entries, each with "date" + aggregator "results".
        """
        all_data = []
        for date in self.date_range(start_date, end_date):
            search_input = (
                f"Flights from {origin} to {destination} departing on {date} "
                f"and returning on {date}"
            )
            logging.info(f"Fetching aggregator data for {date}: '{search_input}'")
            response = self.client.search(search_input)
            
            data_for_date = {
                "date": date,
                "results": response.get("results", [])  # aggregator items
            }
            all_data.append(data_for_date)
        
        return all_data

    def parse_aggregator_data(self, aggregator_data):
        """
        STEP 2:
        Take aggregator info from 'fetch_aggregator_data' and do your best
        to parse out flight info, including the link (URL), airline, price, etc.
        """
        parsed_flights = []

        # Example naive regex for something like "AED 1234" or "AED1,234"
        # Adjust if you see different currency or formats in the aggregator text
        price_regex = re.compile(r"(AED|USD|\$)\s?(\d+(,\d+)*(\.\d+)?)", re.IGNORECASE)

        for day_entry in aggregator_data:
            date = day_entry["date"]
            results = day_entry["results"]  # a list of aggregator items with "title", "url", "content", etc.

            for item in results:
                content = item.get("content", "")
                link = item.get("url", "No link provided")

                # Attempt to find a numeric price in the aggregator text
                match_price = price_regex.search(content)
                if match_price:
                    # Extract the raw numeric substring
                    raw_price_str = match_price.group(2).replace(",", "")
                    try:
                        numeric_price = float(raw_price_str)
                    except ValueError:
                        numeric_price = None
                else:
                    numeric_price = None

                # Some placeholder logic for airline, times, etc.
                airline = "Unknown"
                departure_airport = "Unknown"
                arrival_airport   = "Unknown"
                departure_time    = None
                arrival_time      = None

                # Build a flight dict, including the link
                flight_info = {
                    "date": date,
                    "airline": airline,
                    "departure_airport": departure_airport,
                    "arrival_airport": arrival_airport,
                    "departure_time": departure_time,
                    "arrival_time": arrival_time,
                    "price": numeric_price,
                    "link": link
                }
                parsed_flights.append(flight_info)

        return parsed_flights


if __name__ == "__main__":
    # Instantiate the two-step tool
    two_step = TicketSearchTwoStep()

    # Define parameters
    origin = "Abu Dhabi"
    destination = "Tokyo"
    start_date = "2025-03-01"
    end_date   = "2025-03-02"

    # ----------------------------------------
    # STEP 1: Fetch aggregator data from Tavily
    # ----------------------------------------
    aggregator_data = two_step.fetch_aggregator_data(origin, destination, start_date, end_date)

    # ----------------------------------------
    # STEP 2: Parse aggregator data
    # ----------------------------------------
    parsed_flights = two_step.parse_aggregator_data(aggregator_data)

    # Filter those with a valid price
    flights_with_price = [f for f in parsed_flights if f["price"] is not None]

    if not flights_with_price:
        print("No priced flights found from aggregator data.")
    else:
        # Possibly find the cheapest
        cheapest = min(flights_with_price, key=lambda f: f["price"])
        print(f"Found {len(flights_with_price)} flights with a price.")
        print(f"Cheapest price is {cheapest['price']} - Link: {cheapest['link']}\n")

        # Print them all
        for i, flight in enumerate(flights_with_price, start=1):
            print(f"Flight {i}: Date={flight['date']}, Price={flight['price']}, Link={flight['link']}")
            # If you want more detail:
            # print(f"  Airline: {flight['airline']}, Dep: {flight['departure_airport']}, Arr: {flight['arrival_airport']}")
