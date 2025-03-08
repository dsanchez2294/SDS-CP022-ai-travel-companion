# check_ticket_search.py

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
    level=logging.DEBUG,  # Set to DEBUG so you can see the logs
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class TicketSearchTwoStep:
    
    def __init__(self):
        logging.debug("Initializing TicketSearchTwoStep with TAVILY_API_KEY: %s", TAVILY_API_KEY)
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
        all_data = []
        for date in self.date_range(start_date, end_date):
            search_input = (
                f"Flights from {origin} to {destination} departing on {date} "
                f"and returning on {date}"
            )
            logging.info(f"Fetching aggregator data for {date}: '{search_input}'")
            response = self.client.search(search_input)

            aggregator_items = response.get("results", [])
            logging.debug("[DEBUG fetch_aggregator_data] For date=%s, aggregator items found: %d", date, len(aggregator_items))

            data_for_date = {
                "date": date,
                "results": aggregator_items
            }
            all_data.append(data_for_date)
        
        return all_data

    def parse_aggregator_data(self, aggregator_data):
        """
        STEP 2:
        1) We match either "USD" or "$" + numeric,
        2) Then check the snippet around that match to skip if it's not referencing an actual flight/fare
           or if it explicitly says discount/baggage/fee, etc.
        """
        parsed_flights = []

        # Regex for "USD" or literal "$"
        price_regex = re.compile(r"(?:USD|\$)\s?(\d+(,\d+)*(\.\d+)?)", re.IGNORECASE)

        # We'll skip if snippet mentions these words (i.e. it's probably a fee)
        skip_keywords = ["discount", "service fee", "baggage", "seat fee"]
        # We'll keep if snippet mentions these words (i.e. real flight)
        # You can do keep OR skip logic. We'll do both: skip if "discount" etc., keep if "flight"/"fare".
        must_have_keywords = ["flight", "fare"]

        for day_entry in aggregator_data:
            date = day_entry["date"]
            results = day_entry["results"]

            logging.debug("[DEBUG parse_aggregator_data] Processing day_entry for date=%s, items=%d", date, len(results))

            for item_idx, item in enumerate(results):
                content = item.get("content", "")
                link = item.get("url", "No link provided")

                logging.debug("[DEBUG parse_aggregator_data] date=%s, item_idx=%d, link=%s\ncontent=%r",
                              date, item_idx, link, content[:500])  # show the first 500 chars

                match_price = price_regex.search(content)
                if match_price:
                    entire_match = match_price.group(0)  # e.g. "$8", "USD 1139"
                    raw_price_str = match_price.group(1).replace(",", "")
                    try:
                        numeric_price = float(raw_price_str)
                    except ValueError:
                        numeric_price = None

                    # Distinguish "USD" vs "$"
                    if "USD" in entire_match.upper():
                        currency_symbol = "USD"
                    else:
                        currency_symbol = "$"

                    # Let's extract a snippet around the matched text to see context
                    start_i = max(0, match_price.start() - 80)
                    end_i = min(len(content), match_price.end() + 80)
                    snippet = content[start_i:end_i].lower()

                    # Check skip keywords
                    if any(kw in snippet for kw in skip_keywords):
                        logging.debug("Skipping match because snippet includes skip_keyword. snippet=%r", snippet)
                        numeric_price = None
                        currency_symbol = None
                    else:
                        # If you want to *require* mention of "flight" or "fare," do:
                        if not any(kw in snippet for kw in must_have_keywords):
                            logging.debug("Skipping match because snippet doesn't mention flight/fare. snippet=%r", snippet)
                            numeric_price = None
                            currency_symbol = None

                    # Print debug if it survived
                    if numeric_price is not None:
                        logging.debug(
                            "[DEBUG parse_aggregator_data] Matched price substring=%r => %r %s, link=%s",
                            entire_match, numeric_price, currency_symbol, link
                        )
                else:
                    numeric_price = None
                    currency_symbol = None

                flight_info = {
                    "date": date,
                    "airline": "Unknown",
                    "departure_airport": "Unknown",
                    "arrival_airport": "Unknown",
                    "departure_time": None,
                    "arrival_time": None,
                    "price": numeric_price,
                    "currency": currency_symbol,
                    "link": link
                }
                parsed_flights.append(flight_info)

        return parsed_flights


if __name__ == "__main__":
    two_step = TicketSearchTwoStep()

    origin = "Chile"
    destination = "Brazil"
    start_date = "2025-03-01"
    end_date   = "2025-03-02"

    aggregator_data = two_step.fetch_aggregator_data(origin, destination, start_date, end_date)
    parsed_flights = two_step.parse_aggregator_data(aggregator_data)

    flights_with_price = [f for f in parsed_flights if f["price"] is not None]

    if not flights_with_price:
        print("No priced flights found from aggregator data.")
    else:
        cheapest = min(flights_with_price, key=lambda f: f["price"])
        print(f"Found {len(flights_with_price)} flights with a price.")
        print(f"Cheapest price is {cheapest['price']} {cheapest['currency']} - Link: {cheapest['link']}\n")

        for i, flight in enumerate(flights_with_price, start=1):
            print(f"Flight {i}: Date={flight['date']}, Price={flight['price']} {flight['currency']}, Link={flight['link']}")
