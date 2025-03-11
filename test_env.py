import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key
api_key = os.getenv("FMP_API_KEY")

print("=" * 50)
print("Environment Variable Test")
print("=" * 50)

if api_key:
    print(f"✅ FMP_API_KEY is set: {api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}")
else:
    print("❌ FMP_API_KEY is not set in the environment")

print("\nTest complete.")
print("=" * 50) 