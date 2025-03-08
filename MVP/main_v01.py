# main_v01.py

import re
import logging
from planner_v01 import PlannerAgent
from summarizer_v01 import SummarizerAgent
from tools_v01 import SearchWeb, TicketSearch, TourSearch

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Register all known actions (tools)
known_actions = {
    "web_search": SearchWeb,
    "ticket_search": TicketSearch,
    "tour_search": TourSearch
}

def grab_actions(response):
    """
    Looks for lines like:
    Action: ticket_search: <details> 
    in the LLM's response. 
    If not found, returns (None, None).
    """
    pattern = r"^(Action):\s(\w+):\s(.*?)(?=\.\s|$)"
    match = re.search(pattern, response, re.MULTILINE)
    if match:
        tool = match.group(2)
        details = match.group(3)
        return tool, details
    return None, None

def query(max_turns=10):
    """
    Orchestrates the conversation with the LLM. 
    The LLM may request 'ticket_search', 'web_search', or 'tour_search' 
    in multiple steps. We gather the data, feed them back as Observations, 
    and let the LLM continue until it returns a final answer (no new action).
    """

    logging.info("Starting the conversation...")

    planner = PlannerAgent()
    summarizer = SummarizerAgent()

    # Example user request
    prompt_template = """
    I want you to build an itinerary for me for a trip from {origin} to {destination} 
    starting from {start_month} {start_day} to {end_month} {end_day}.
    Also, please include tours for each city, flight tickets, and best hotel deals. You must include tours and links
    """

    origin = 'chile'
    destination = 'brazil'
    start_month = 'march'
    start_day   = '1'
    end_month   = 'march'
    end_day     = '23'

    # Convert textual months to numeric
    month_map = {
        "january": "01", "february": "02", "march": "03", "april": "04",
        "may": "05", "june": "06", "july": "07", "august": "08",
        "september": "09", "october": "10", "november": "11", "december": "12"
    }
    start_month_num = month_map.get(start_month.lower(), "01")
    end_month_num   = month_map.get(end_month.lower(),   "01")

    start_date = f"2025-{start_month_num}-{start_day.zfill(2)}"
    end_date   = f"2025-{end_month_num}-{end_day.zfill(2)}"

    user_prompt = prompt_template.format(
        origin=origin,
        destination=destination,
        start_month=start_month,
        start_day=start_day,
        end_month=end_month,
        end_day=end_day
    )

    i = 0
    next_prompt = user_prompt

    while i < max_turns:
        # 1) Send the prompt to LLM
        response = planner.plan(next_prompt)
        
        # 2) Attempt to parse an action
        tool, details = grab_actions(response)

        # If the LLM doesn't produce a recognized action,
        # we treat this as the final answer from the LLM.
        if not tool:
            logging.info("No recognized action found => returning final answer.")
            return response

        if tool not in known_actions:
            logging.warning(f"Unknown tool requested: {tool}")
            return response

        logging.info(f"--- Running tool '{tool}' with details: {details} ---")
        action_instance = known_actions[tool]()

        # 3) Based on which tool, do the step, build an Observation, let LLM continue
        if tool == "ticket_search":
            aggregator_data = action_instance.ticket_search(
                origin, destination, start_date, end_date
            )

            # Build flight text
            flight_text = "Flight Options:\n"
            valid_flights = [f for f in aggregator_data if f["price"] is not None]
            if not valid_flights:
                flight_text += "No flight options found.\n"
            else:
                for idx, flight in enumerate(valid_flights[:5], start=1):
                    flight_text += (
                        f"{idx}) {flight['origin']} -> {flight['destination']} on {flight['date']} "
                        f"Price={flight['price']} {flight['currency']}, Link={flight['link']}\n"
                    )

            # Feed flight data back to LLM as new prompt
            next_prompt = f"""
Observation: {flight_text}

Please incorporate these flight options exactly (no placeholder links).
"""

        elif tool == "web_search":
            # Summarize the web search (hotels etc.)
            raw_results = action_instance.search(details)
            summary = summarizer.summarize(raw_results)
            next_prompt = f"Observation: {summary}"

        elif tool == "tour_search":
            # The LLM presumably gave us itinerary text or city info in 'details'
            # We pass it to tour search
            tours_result = action_instance.search(details)

            next_prompt = f"""
Observation: {tours_result}

Please incorporate these tour options exactly (no placeholder links).
"""

        else:
            logging.warning(f"No handler for {tool}.")
            return response

        i += 1

    # If we exhausted the loop, just return the last response from LLM
    logging.info("Reached max_turns => returning last LLM response.")
    return response

if __name__ == "__main__":
    final_answer = query()
    print("\n--- FINAL RESPONSE ---\n")
    print(final_answer)
