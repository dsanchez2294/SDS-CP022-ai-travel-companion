from planner_v01 import PlannerAgent
from summarizer_v01 import SummarizerAgent
from tools_v01 import SearchWeb
import re

known_actions = {
    "web_search": SearchWeb
}

def grab_actions(response):
    # using regex to grab the action, the tool to use and the details of the tool input
    pattern = r"^(Action):\s(\w+):\s(.*?)(?=\.\s|$)"
    match = re.search(pattern, response, re.MULTILINE)
    if match:
        tool = match.group(2)
        details = match.group(3)

    return tool, details

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
        
        # 3) Advance iteration
        i += 1
        next_prompt = response  # default next prompt
        
        # 4) If we found a tool name:
        if tool:
            # Check if it's known
            if tool not in known_actions:
                print(f"Unknown tool: {tool}")
                break
            
            print(f"--- running {tool} {details} ---")
            
            # Instantiate and run the tool
            action = known_actions[tool]()
            search_resp = action.search(details)

            print("--- summarizing results ---")
            summary = summarizer.summarize(search_resp)
            
            # Provide the observation back to the planner
            next_prompt = f"Observation: {summary}"
        
        # If no tool was found, we exit the loop (the user is done)
        else:
            return response

if __name__ == "__main__":
    query()