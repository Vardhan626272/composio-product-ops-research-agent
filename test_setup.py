import os
from dotenv import load_dotenv
from composio import Composio

load_dotenv()

api_key = os.getenv("COMPOSIO_API_KEY")

if not api_key:
    raise RuntimeError("COMPOSIO_API_KEY is missing")

composio = Composio(api_key=api_key)

toolkits = composio.toolkits.list()

print("Composio connection successful.")
print("Available toolkits returned:", len(toolkits.items))