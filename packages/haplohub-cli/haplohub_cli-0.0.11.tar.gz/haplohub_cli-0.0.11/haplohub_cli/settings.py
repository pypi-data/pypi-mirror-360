from os import environ
from posixpath import expanduser, join

from dotenv import load_dotenv

load_dotenv()

# File paths
CONFIG_DIR = expanduser("~/.haplohub")
CONFIG_FILE = join(CONFIG_DIR, "config.json")
CREDENTIALS_FILE = join(CONFIG_DIR, "credentials.json")

# Authentication
REDIRECT_PORT = 8088

AUTH0_REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}/"
AUTH0_DOMAIN = environ.get("AUTH0_DOMAIN", "dev-42a7qv136prmsazj.us.auth0.com")
AUTH0_CLIENT_ID = environ.get("AUTH0_CLIENT_ID", "TRi894X7yV3e8EOpNVrDdvQbRvYnjibH")
AUTH0_AUDIENCE = environ.get("AUTH0_AUDIENCE", "https://haplohub.com/api/")

# API
API_URL = environ.get("API_URL", "http://localhost:8000")

environ["DOCKER_CONFIG"] = join(CONFIG_DIR, "docker")
