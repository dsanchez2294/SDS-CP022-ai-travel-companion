###################################################################
# tools_v01.py
###################################################################
import os
import logging
import datetime
import re
from dotenv import load_dotenv
from tavily import TavilyClient

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

    def parse_aggregator_results(self, date_str, results):
        """
        Parse aggregator 'results' to extract flight price (if any) plus currency and the aggregator link.
        We'll look for something like "AED 5755", "$1234", or "USD 999" using a whitelist regex,
        then store both the numeric amount and currency in a flight dictionary.
        """
        flights_found = []

        # Whitelist for recognized currencies: AED, USD, GBP, EUR, SAR, or literal '$'
        price_regex = re.compile(
            r"(?:\b(AED|USD|GBP|EUR|SAR)\b|\$)\s?(\d+(,\d+)*(\.\d+)?)",
            re.IGNORECASE
        )

        for item in results:
            content = item.get("content", "")
            link = item.get("url", "No link provided")

            # Attempt to find a currency + numeric price
            match_price = price_regex.search(content)
            if match_price:
                raw_currency = match_price.group(1)  # could be None if '$' matched
                if raw_currency is not None:
                    # Convert e.g. "usd" -> "USD"
                    currency_symbol = raw_currency.strip().upper()
                else:
                    # The match was '$'
                    currency_symbol = "$"

                raw_price_str = match_price.group(2).replace(",", "")
                try:
                    price_val = float(raw_price_str)
                except ValueError:
                    price_val = None
            else:
                currency_symbol = None
                price_val = None

            # Construct the flight dict
            flight_info = {
                "date": date_str,
                "departure_airport": "Unknown",
                "arrival_airport": "Unknown",
                "departure_time": None,
                "arrival_time": None,
                "airline": "Unknown",
                "price": price_val,
                "currency": currency_symbol,
                "link": link,
            }
            flights_found.append(flight_info)

        return flights_found

    def ticket_search(self, origin, destination, start_date, end_date):
        """
        Main function to search Tavily for each date, trying 'best_flights' first
        and falling back to aggregator results if best_flights is empty.
        Returns a list of flight dicts, each with 'price', 'currency', 'link', etc.
        """
        flights = []
        
        for date in self.date_range(start_date, end_date):
            search_input = (
                f"Flights from {origin} to {destination} "
                f"departing on {date} and returning on {date}"
            )
            logging.info(f"Performing flight search for {date}: {search_input}")

            response = self.client.search(search_input)
            if not response:
                logging.warning(f"No response for {date}, skipping this day.")
                continue

            best_flights = response.get('best_flights', [])
            if best_flights:
                logging.info(f"Found structured 'best_flights' data for {date}")
                # If Tavily returns structured flight info, parse it.
                # We don't know the currency here, so set currency="N/A (best_flights)"
                for flight in best_flights:
                    for segment in flight.get('flights', []):
                        flight_info = {
                            'date': date,
                            'departure_airport': segment['departure_airport']['name'],
                            'arrival_airport': segment['arrival_airport']['name'],
                            'departure_time': segment['departure_airport']['time'],
                            'arrival_time': segment['arrival_airport']['time'],
                            'airline': segment['airline'],
                            'price': flight['price'],
                            'currency': "N/A (best_flights data)",
                            'link': "No link (best_flights data)",
                        }
                        flights.append(flight_info)
            else:
                logging.info(f"No 'best_flights' found for {date}; parsing aggregator results.")
                aggregator_items = response.get("results", [])
                aggregator_flights = self.parse_aggregator_results(date, aggregator_items)
                flights.extend(aggregator_flights)

        return flights
