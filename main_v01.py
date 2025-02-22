# main_v01.py

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
    return None, None

def query(max_turns=6):
    
    planner = PlannerAgent()
    summarizer = SummarizerAgent()

    prompt_template = """
    I want you to build an itinerary for me for a trip from {origin} to {destination} starting 
    from {start_month} {start_day} to {end_month} {end_day}.
    """

    # Hardcoded example
    origin = 'chile'
    destination = 'brazil'
    start_month = 'march'
    start_day = '1'
    end_month = 'march'
    end_day = '23'

    # Convert months
    month_map = {
        "january": "01", "february": "02", "march": "03", "april": "04", "may": "05",
        "june": "06", "july": "07", "august": "08", "september": "09", "october": "10",
        "november": "11", "december": "12"
    }   

    start_month_num = month_map.get(start_month.lower(), "01")
    end_month_num = month_map.get(end_month.lower(), "01")

    start_date = f"2025-{start_month_num}-{start_day.zfill(2)}"
    end_date   = f"2025-{end_month_num}-{end_day.zfill(2)}"

    prompt = prompt_template.format(
        origin=origin,
        destination=destination,
        start_month=start_month,
        start_day=start_day,
        end_month=end_month,
        end_day=end_day
    )
    
    i = 0
    next_prompt = prompt

    while i < max_turns:
        # 1) Call the planner
        response = planner.plan(next_prompt)
        
        # 2) Attempt to extract an action + details
        tool, details = grab_actions(response)
        if not tool:
            # No more actions
            return response

        if tool not in known_actions:
            print(f"Unknown tool: {tool}")
            return response

        print(f"--- running {tool} with details: {details} ---")
        action = known_actions[tool]()

        if tool == "ticket_search":
        # Step C: aggregator flights
            ticket_tool = TicketSearch()
            aggregator_data = ticket_tool.ticket_search(origin, destination, start_date, end_date)

            # Build flight_text with real aggregator links
            flight_text = "Flight Options:\n"
            valid_flights = [f for f in aggregator_data if f["price"] is not None]
            if not valid_flights:
                flight_text += "No flight options found.\n"
            else:
                for idx, f in enumerate(valid_flights[:5], start=1):
                    flight_text += (
                        f"{idx}) {f['origin']} -> {f['destination']} on {f['date']} "
                        f"Price={f['price']} {f['currency']}, Link={f['link']}\n"
                    )
            
            # Step D: "Pause" the LLM. We now do a second call with the aggregator data
            resume_prompt = f"""
    Observation: {flight_text}

    Now please produce the final itinerary. 
    IMPORTANT:
    - You must replicate these aggregator flight links EXACTLY, no rewriting or placeholders.
    """
            # Step E: Second LLM call to produce final itinerary
            final_response = planner.plan(resume_prompt)
            return final_response
        
        elif tool == "web_search":
            # Possibly handle web search first if that's the LLM's action
            # ...
            return response
        else:
            # Unknown or no tool
            return response

if __name__ == "__main__":
    final_response = query()
    print("\n--- FINAL RESPONSE ---\n")
    print(final_response)