from planner_agent import PlannerAgent
from summarizer_agent import SummarizerAgent
from tools import SearchWeb
import re
import gradio as gr

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
        print("\nTool and details extracted from response:\n")
        print(f"\nTool: {tool}, Details: {details}\n")

    return tool, details

def query(origin, destination, start_month, start_day, end_month, end_day, max_turns=6):
    
    # Initialize agents and tools
    planner = PlannerAgent()
    summarizer = SummarizerAgent()

    # Define the user prompt
    prompt_template = """
    I want you to build an itinerary for me for a trip from {origin} to {destination} starting 
    from {start_month} {start_day} to {end_month} {end_day}.
    """

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
        response = planner.plan(next_prompt)
        next_prompt = response
        i += 1
        if "Action" in next_prompt:
            tool, details = grab_actions(response)
            if tool not in known_actions:
                print(f"Unknown tool: {tool}")
                break
            print("\n--- running {} {} ---\n".format(tool, details))
            action = known_actions[tool]()
            search_resp = action.search(details)
            print("\n--- summarizing results ---\n")
            summary = summarizer.summarize(search_resp)
            # print("--- Observation: {} ---".format(summary))
            next_prompt = f"Observation: {summary}"
        else:
            return response.strip("Answer:")

def main():
    iface = gr.Interface(
        fn=query,
        inputs=[
            gr.Textbox(label="Origin"),
            gr.Textbox(label="Destination"),
            gr.Textbox(label="Start Month"),
            gr.Textbox(label="Start Day"),
            gr.Textbox(label="End Month"),
            gr.Textbox(label="End Day")
        ],
        outputs="markdown",
        title="AI Travel Companion",
        description="Enter your travel details to get a personalized itinerary."
    )
    iface.launch()

if __name__ == "__main__":
    main()