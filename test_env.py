# test_env.py
import os
from dotenv import load_dotenv

load_dotenv()
telegram_token = os.getenv('TELEGRAM_TOKEN')
print(f"TELEGRAM_TOKEN = {telegram_token}")