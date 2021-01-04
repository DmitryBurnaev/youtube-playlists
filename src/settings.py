import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DEBUG = os.getenv("APP_DEBUG", "") in ("1", "True")

ENVIRONMENT = os.getenv("ENVIRONMENT", "develop")

APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = os.getenv("APP_PORT", "8000")

