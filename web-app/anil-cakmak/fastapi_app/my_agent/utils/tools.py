import asyncio
import os
from tavily import TavilyClient
from dotenv import load_dotenv
from typing import Dict, List
from pydantic import BaseModel

load_dotenv()

tavily = TavilyClient(os.getenv("TAVILY_API_KEY"))

class Queries(BaseModel):
    queries: List[str]


async def search_single_query(query: str) -> Dict:
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(
        None,
        lambda: tavily.search(
            query=query,
            search_depth="basic",
            max_results=2,
            include_answer=True
        )
    )
    return response


async def search_multiple_queries(queries: List[str]) -> Dict[str, str]:
    tasks = [search_single_query(query) for query in queries]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    extracted_results = {}
    for query, result in zip(queries, results):
        if isinstance(result, dict) and "answer" in result:
            extracted_results[query] = result["answer"]
        else:
            extracted_results[query] = f"Error: {result}"
    
    return extracted_results


def run_search_multiple_queries(queries: List[str]) -> Dict[str, str]:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(search_multiple_queries(queries))