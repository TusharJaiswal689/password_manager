import os
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PASS")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT", "5432")
name = os.getenv("DB_NAME")
driver = os.getenv("DB_DRIVER", "postgresql")

db_url = f"{driver}://{user}:{password}@{host}:{port}/{name}" 