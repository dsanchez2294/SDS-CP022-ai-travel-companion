from my_agent.agent import graph
from typing import Generator

def chat(user_input: str, thread: str) -> Generator[str, None, None]:

    if not user_input.strip():
        yield "Error: Empty input"
        return
        
    try:
        config = {"configurable": {"thread_id": thread}}

        for event in graph.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            config
        ):
            for value in event.values():
                if "messages" in value:
                    yield value['messages'][-1].content
    
    except Exception as e:
        yield f"Chat Error: {e} \n\n Please try again or start a new session."
        return