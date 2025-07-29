import os
from dotenv import load_dotenv

load_dotenv()


def get_optional_headers():
    if os.getenv("COMPOSER_API_KEY") is None or os.getenv("COMPOSER_SECRET_KEY") is None:
        return {}
    else:
        return {
            "x-api-key-id": os.getenv("COMPOSER_API_KEY"),
            "Authorization": f"Bearer {os.getenv('COMPOSER_SECRET_KEY')}"
        }

def get_required_headers():
    if os.getenv("COMPOSER_API_KEY") is None or os.getenv("COMPOSER_SECRET_KEY") is None:
        raise ValueError("COMPOSER_API_KEY and COMPOSER_SECRET_KEY must be set")
    else:
        return {
            "x-api-key-id": os.getenv("COMPOSER_API_KEY"),
            "Authorization": f"Bearer {os.getenv('COMPOSER_SECRET_KEY')}"
        }
