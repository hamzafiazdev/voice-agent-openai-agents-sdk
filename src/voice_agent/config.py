import os

from dotenv import load_dotenv

load_dotenv()


def get_google_api_key() -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        return api_key

    raise RuntimeError(
        "Missing GOOGLE_API_KEY. Create a .env file in the project root and add "
        "GOOGLE_API_KEY=AIzaSyDHXCqfiCsOyytefws46sQI_dVqz7_ZWTc."
    )
