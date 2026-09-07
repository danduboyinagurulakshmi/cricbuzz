import os

from dotenv import load_dotenv


load_dotenv()

API_BASE_URL = os.getenv("CRICKET_API_BASE_URL")
API_KEY = os.getenv("CRICKET_API_KEY")
API_HOST = os.getenv("CRICKET_API_HOST")