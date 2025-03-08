# test_ticket_search.py

import os
import logging
from dotenv import load_dotenv
from tools_v01 import TicketSearch

load_dotenv("cred.env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def main():
    origin = "chile"
    destination = "brazil"
    start_date = "2025-03-01"
    end_date = "2025-03-23"
    
    ts = TicketSearch()
    flights = ts.ticket_search(origin, destination, start_date, end_date)
    
    if not flights:
        print("No flights found.")
    else:
        print("Final Flight Options:")
        for idx, flight in enumerate(flights, start=1):
            # Format departure and arrival airport (they may be 'Unknown' if not available)
            dep_airport = flight['departure_airport']
            arr_airport = flight['arrival_airport']
            price_info = f"{flight['price']} {flight['currency']}" if flight['price'] is not None else "N/A"
            print(f"{idx}) {flight['origin']} -> {flight['destination']} on {flight['date']} | "
                  f"Dep: {dep_airport} -> Arr: {arr_airport} | "
                  f"Price: {price_info} | Link: {flight['link']}")

if __name__ == "__main__":
    main()
