import os
from anthropic import Anthropic

# Get API key from environment
api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"API Key loaded: {api_key[:10]}..." if api_key else "No API key")

# Try to create client
try:
    client = Anthropic(api_key=api_key)
    print("✓ Client created successfully")
    print(f"Client type: {type(client)}")
except Exception as e:
    print(f"✗ Error creating client: {e}")
