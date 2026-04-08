from langchain_core.tools import tool
from ddgs import DDGS

@tool
def web_search_tool(query: str) -> str:
    """
    Use this tool to search the internet for the latest information via DuckDuckGo.
    Very useful for finding the latest technical solutions, error documentation, or
    RAG theories that may not be found in local databases.

    Args:
    query: Search keywords.
    Returns:
    A string containing a summary of the search results (title, link, and snippet).
    """
    try:
        results = DDGS().text(query, max_results=3)
        
        if not results:
            return "No relevant search results found."
        
        formatted_results = []
        for i, res in enumerate(results, 1):
            formatted_results.append(
                f"[{i+1}] Title: {res['title']}\n"
                f"Link: {res['href']}\n"
                f"Snippet: {res['body']}\n"
            )
        
        return "\n".join(formatted_results)
    
    except Exception as e:
        return f"Error during web search: {str(e)}"

AVAILABLE_TOOLS = {
    "web_search_tool": web_search_tool,
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "web_search_tool",
            "description": "Use this tool to search for documentation, the latest technical solutions, or RAG best practices on the internet via DuckDuckGo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Technical search keywords (examples: 'best RAG chunking strategy', 'how to fix hallucination').",
                    }
                },
                "required": ["query"],
            },
        },
    }
]