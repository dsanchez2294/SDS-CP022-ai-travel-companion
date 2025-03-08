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
        'https://www.booking.com/',
        'https://www.latam.com/',
        'https://www.despegar.com/',
        'https://www.tripadvisor.com/'
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

    def parse_aggregator_results(self, date_str, results, origin, destination):
        """
        Parse aggregator 'results' to extract flight prices. We'll skip lines referencing 
        'discount', 'fee', 'baggage', etc. and require 'flight' or 'fare' in the snippet.
        For aggregator flights, departure_airport and arrival_airport remain 'Unknown'.
        """
        flights_found = []

        # Matches "USD 123" or "$123"
        price_regex = re.compile(r"(?:USD|\$)\s?(\d+(,\d+)*(\.\d+)?)", re.IGNORECASE)

        skip_keywords = ["discount", "fee", "baggage", "seat fee"]
        must_have_keywords = ["flight", "fare"]

        for item in results:
            content = item.get("content", "")
            link = item.get("url", "No link provided")

            match = price_regex.search(content)
            if match:
                entire_match = match.group(0)
                raw_price_str = match.group(1).replace(",", "")

                try:
                    price_val = float(raw_price_str)
                except ValueError:
                    price_val = None

                # If "USD" in entire_match, currency = "USD", else "$"
                if "USD" in entire_match.upper():
                    currency_symbol = "USD"
                else:
                    currency_symbol = "$"

                # Check snippet around the match for skip/require keywords
                snippet_start = max(0, match.start() - 80)
                snippet_end   = min(len(content), match.end() + 80)
                snippet_text  = content[snippet_start:snippet_end].lower()

                if price_val is not None:
                    # Skip if snippet has skip_keyword or doesn't contain must_have_keyword
                    if any(kw in snippet_text for kw in skip_keywords):
                        price_val = None
                        currency_symbol = None
                    else:
                        if not any(kw in snippet_text for kw in must_have_keywords):
                            price_val = None
                            currency_symbol = None
            else:
                price_val = None
                currency_symbol = None

            flight_info = {
                "origin": origin,
                "destination": destination,
                "date": date_str,
                "departure_airport": "Unknown",
                "arrival_airport": "Unknown",
                "departure_time": None,
                "arrival_time": None,
                "airline": "Unknown",
                "price": price_val,
                "currency": currency_symbol,
                "link": link
            }
            flights_found.append(flight_info)

        return flights_found

    def ticket_search(self, origin, destination, start_date, end_date):
        """
        Main function:
          1) For each date, we either parse best_flights or aggregator items.
          2) We store origin, destination, plus aggregator/best_flights data.
          3) After collecting flights for all days, we keep only the cheapest 5 aggregator flights overall
             plus any best_flights flights (unlimited, if you want).
        """
        all_flights = []
        
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
                for flight in best_flights:
                    for segment in flight.get('flights', []):
                        flight_info = {
                            "origin": origin,
                            "destination": destination,
                            "date": date,
                            "departure_airport": segment['departure_airport']['name'],
                            "arrival_airport": segment['arrival_airport']['name'],
                            "departure_time": segment['departure_airport']['time'],
                            "arrival_time": segment['arrival_airport']['time'],
                            "airline": segment['airline'],
                            "price": flight['price'],
                            "currency": "N/A (best_flights data)",
                            "link": "No link (best_flights data)",
                        }
                        all_flights.append(flight_info)
            else:
                logging.info(f"No 'best_flights' found for {date}; parsing aggregator results.")
                aggregator_items = response.get("results", [])
                aggregator_flights = self.parse_aggregator_results(date, aggregator_items, origin, destination)
                all_flights.extend(aggregator_flights)

        # Filter out flights with no price
        valid_flights = [f for f in all_flights if f["price"] is not None]

        # Separate aggregator flights vs best_flights
        aggregator_sub = [f for f in valid_flights if f["currency"] != "N/A (best_flights data)"]
        best_sub       = [f for f in valid_flights if f["currency"] == "N/A (best_flights data)"]

        # Sort aggregator flights by ascending price
        aggregator_sub.sort(key=lambda x: x["price"])

        # Keep only the cheapest 5 aggregator flights overall
        aggregator_sub = aggregator_sub[:5]

        # Combine aggregator flights + best_flights
        final_flights = aggregator_sub + best_sub
        return final_flights


class TourSearch:
    """
    This new tool searches for tours for the places mentioned in the itinerary.
    For simplicity, it just runs a web search using Tavily for each city found in the itinerary
    and tries to retrieve tours or booking links.
    """
    def __init__(self):
        logging.info("TourSearch tool is being called...")
        self.client = TavilyClient(TAVILY_API_KEY)

    def search(self, itinerary_text):
        """
        Takes the final itinerary or partial itinerary as input (a text)
        and extracts city names or key keywords. Then queries the Tavily client 
        (like a web search) to find tours for those places, returning a textual result 
        with links to book.

        Real logic would parse the itinerary carefully. For demo, we do naive city extraction 
        or just search "Tours in <city>".
        """
        # Example: find lines like "Day 1-3: Tokyo" or something similar
        # We'll do a naive approach:
        city_regex = re.compile(r"(Rio de Janeiro|São Paulo|Salvador|Tokyo|Kyoto|Osaka)", re.IGNORECASE)
        found_cities = city_regex.findall(itinerary_text)
        if not found_cities:
            return "No city found in itinerary text. Cannot find tours."

        # For each city, we do a naive search for "Tours in <city>"
        results_text = "Recommended Tours:\n"
        for city in set(found_cities):
            query = f"Tours in {city}"
            logging.info(f"Searching tours for city={city} => {query}")
            resp = self.client.search(query)
            # For demonstration, we just merge all aggregator content:
            aggregator_items = resp.get("results", [])
            if not aggregator_items:
                results_text += f"No tours found for {city}.\n"
                continue
            # Otherwise, let's just list the top 2 aggregator links
            for idx, item in enumerate(aggregator_items[:2], start=1):
                link = item.get("url", "No link provided")
                snippet = item.get("content", "")[:100]  # partial snippet
                results_text += f"{city} Tour Option {idx}: Link={link}, Info snippet={snippet}\n"

        return results_text