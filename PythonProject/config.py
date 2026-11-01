from pathlib import Path
from dotenv import dotenv_values

# Locate the .env file in the project folder
env_file = Path(__file__).resolve().parent / ".env"

# Load variables from .env
values = dotenv_values(env_file)

# Read the API key using its variable name
apikey = values.get("GEMINI_API_KEY")

# Validate the API key
if not apikey or not apikey.strip():
    raise ValueError(
        f"Gemini API key missing or empty. Check: {env_file}"
    )

apikey = apikey.strip()
