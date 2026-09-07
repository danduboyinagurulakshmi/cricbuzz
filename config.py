import os

import streamlit as st
from dotenv import load_dotenv


load_dotenv()


def _get_setting(name):
	value = os.getenv(name)
	if value:
		return value

	try:
		return st.secrets.get(name)
	except Exception:
		return None


API_BASE_URL = _get_setting("CRICKET_API_BASE_URL")
API_KEY = _get_setting("CRICKET_API_KEY")
API_HOST = _get_setting("CRICKET_API_HOST")