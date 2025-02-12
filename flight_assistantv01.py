# %%
import requests


# Replace with your API details
from dotenv import load_dotenv
load_dotenv()


# Load environment variables from cred.env file
load_dotenv("cred.env")


# %%
def get_flight_data(origin, destination, start_date, end_date):
    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": start_date,
        "return_date": end_date,
        "currency": "USD",
        "hl": "es",
        "api_key": SERPAPI_KEY
    }   
    response = requests.get(SERPAPI_URL, params=params)
    if response.status_code == 200:
        return response.json()  # Adjust for your API's response format
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

# %%
# Example usage
origin = "JFK"
destination = "LHR"
start_date = "2025-02-01"
end_date = "2025-02-28"

# %%
flight_data = get_flight_data(origin, destination, start_date, end_date)

# %%
print(flight_data)

# %%
# Extract relevant flight details and structure them into a list of dictionaries
flights_for_db = []

for flight in flight_data['best_flights']:
    for segment in flight['flights']:
        flight_info = {
            'departure_airport': segment['departure_airport']['name'],
            'arrival_airport': segment['arrival_airport']['name'],
            'departure_time': segment['departure_airport']['time'],
            'arrival_time': segment['arrival_airport']['time'],
            'airline': segment['airline'],
            'price': flight['price']
        }
        flights_for_db.append(flight_info)

# Now flights_for_db contains the structured flight information
print(flights_for_db)


