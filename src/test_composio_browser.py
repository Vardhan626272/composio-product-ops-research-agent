import os
from dotenv import load_dotenv
from composio import ComposioToolSet, Action

load_dotenv()

def test_composio_retrieval():
    """
    Attempted to use Composio's Browser tool for initial web scraping.
    Status: Disabled in the final pipeline because the sandbox API key 
    returned an HTTP 403 (Execution disabled by administrator). 
    Moved to local Playwright fallback (see web_research.py).
    """
    try:
        print("Initializing Composio ToolSet...")
        toolset = ComposioToolSet(api_key=os.getenv("COMPOSIO_API_KEY"))
        
        # Test the browser action
        response = toolset.execute_action(
            action=Action.BROWSER_GOTO,
            params={"url": "https://developer.salesforce.com"}
        )
        print("Response:", response)
        
    except Exception as e:
        print(f"Composio SDK Error (Expected 403): {e}")

if __name__ == "__main__":
    test_composio_retrieval()
