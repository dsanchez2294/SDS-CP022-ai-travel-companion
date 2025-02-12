from tools_v01 import TicketSearch
import os
from dotenv import load_dotenv

load_dotenv("cred.env")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY not found.")


# Initialize the TicketSearch class with your API key
ticket_search = TicketSearch(api_key=TAVILY_API_KEY)

# Define test parameters
origin = "JFK"
destination = "LHR"
start_date = "2025-02-01"
end_date = "2025-02-03"

# Perform the flight search
flights = ticket_search.get_flight_data(origin, destination, start_date, end_date)

# Print the results
print(flights)