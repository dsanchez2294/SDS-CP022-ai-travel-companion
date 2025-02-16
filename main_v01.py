from planner_v01 import PlannerAgent
from summarizer_v01 import SummarizerAgent
from tools_v01 import SearchWeb
from tools_v01 import TicketSearch
import re

known_actions = {
    "web_search": SearchWeb,
    "ticket_search": TicketSearch
}

def grab_actions(response):
    pattern = r"^(Action):\s(\w+):\s(.*?)(?=\.\s|$)"
    match = re.search(pattern, response, re.MULTILINE)
    if match:
        tool = match.group(2)
        details = match.group(3)
        return tool, details

# If no match, return None, None
    return None, None


def query(max_turns=6):
    
    # Initialize agents and tools
    planner = PlannerAgent()
    summarizer = SummarizerAgent()

    # Define the user prompt
    prompt_template = """
    I want you to build an itinerary for me for a trip from {origin} to {destination} starting 
    from {start_month} {start_day} to {end_month} {end_day}.
    """

    # origin = input("Enter where you are travelling from: ")
    # destination = input("Enter your destination: ")
    # start_month = input("Enter the month you would like to depart for your trip: ")
    # start_day = input("Enter the day you would like to depart for your trip: ")
    # end_month = input("Enter the month you would like to return: ")
    # end_day = input("Enter the day you would like to return: ")

    origin = 'abu dhabi'
    destination = 'japan'
    start_month = 'march'
    start_day = '1'
    end_month = 'march'
    end_day = '23'

    # Convert the months so Ticket Search can understand them
    month_map = {
        "january": "01", "february": "02", "march": "03", "april": "04", "may": "05",
        "june": "06", "july": "07", "august": "08", "september": "09", "october": "10",
        "november": "11", "december": "12"
        }   

    start_month_num = month_map.get(start_month.lower(), "01")
    end_month_num = month_map.get(end_month.lower(), "01")

    start_date = f"2025-{start_month_num}-{start_day.zfill(2)}"
    end_date   = f"2025-{end_month_num}-{end_day.zfill(2)}"



    # Run the planner agent
    prompt = prompt_template.format(
        origin=origin,
        destination=destination,
        start_month=start_month,
        start_day=start_day,
        end_month=end_month,
        end_day=end_day)
    
    i = 0
    next_prompt = prompt

    while i < max_turns:
        # 1) Call the planner
        response = planner.plan(next_prompt)
        
        # 2) Attempt to extract an action + details
        tool, details = grab_actions(response)
        
        # 3) Invoque the ticket searcher or other tool

        if not tool:
            return response

        # 3) Check if it's a known tool
        if tool not in known_actions:
            print(f"Unknown tool: {tool}")
            return response

        # 4) Instantiate the relevant tool
        print(f"--- running {tool} with details: {details} ---")
        action = known_actions[tool]()

        if tool == "ticket_search":
            # Directly call .ticket_search() with the known variables
            search_resp = action.ticket_search(origin, destination, start_date, end_date)

        elif tool == "web_search":
            # For web_search, pass the entire details string
            search_resp = action.search(details)

        else:
            # No implementation for other tools
            print(f"No handler for tool: {tool}")
            return response

        # 5) Summarize the tool's output
        print("--- summarizing results ---")
        summary = summarizer.summarize(search_resp)

        # 6) Provide the observation back to the planner
        next_prompt = f"Observation: {summary}"
        i += 1

    # If we exceed max_turns without returning, just return the last response
    return response

if __name__ == "__main__":
    final_response = query()
    print("\n--- FINAL RESPONSE ---\n")
    print(final_response)