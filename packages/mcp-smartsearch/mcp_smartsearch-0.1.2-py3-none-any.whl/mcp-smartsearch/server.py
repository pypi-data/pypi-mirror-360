import os
import json
import asyncio
import urllib.request
import urllib.parse
from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server
mcp = FastMCP("SmartSearchService")

@mcp.tool()
async def smart_search(
    query: str,
    count: int = 10,
    offset: int = 0,
    setLang: str = 'en',
    safeSearch: str = 'Strict'
) -> dict:
    """
    Performs a web search using a remote smart search API.
    Returns a JSON object with the search results.
    """
    server_key = os.getenv("SERVER_KEY")
    if not server_key:
        raise ValueError("SERVER_KEY environment variable is not set.")

    try:
        endpoint, api_key = server_key.split("-", 1)
    except ValueError:
        raise ValueError("Invalid SERVER_KEY format. Expected 'endpoint-apikey'.")

    # This is a synchronous function that will be run in a separate thread
    def sync_search():
        base_url = f"https://searchapi.xiaosuai.com/search/{endpoint}/smart"
        params = {
            'q': query,
            'count': count,
            'offset': offset,
            'mkt': setLang,
            'safeSearch': safeSearch
        }
        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        
        headers = {'Authorization': f'Bearer {api_key}'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status != 200:
                raise Exception(f"API Error: {response.status} {response.reason}")
            response_body = response.read()
            return json.loads(response_body)

    # Run the synchronous network code in a separate thread to avoid blocking
    return await asyncio.to_thread(sync_search)

def main():
    print("Starting MCP SmartSearch Service...")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()