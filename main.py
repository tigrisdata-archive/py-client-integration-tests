import os

from dotenv import load_dotenv
from tigrisdb.types import ClientConfig

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(ROOT_DIR, ".env.dev"))
tigris_conf: ClientConfig = ClientConfig(
    server_url=os.environ.get("TIGRIS_SERVER_URL"),
    project_name=os.environ.get("TIGRIS_PROJECT"),
    client_id=os.environ.get("TIGRIS_CLIENT_ID"),
    client_secret=os.environ.get("TIGRIS_CLIENT_SECRET")
)
