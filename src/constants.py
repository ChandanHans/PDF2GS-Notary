import json
import os
from dotenv import load_dotenv

from .utils import resource_path


load_dotenv(dotenv_path=resource_path(".env"))


GPT_KEY = os.environ["GPT_KEY"]
CREDS_JSON = json.loads(os.environ["CREDS_JSON"])
ANNUAIRE_SHEET_KEY = "1NBWDbmuXHKr6yWsEvxJhio4uaUPKol6_dJvtgKJCDhc"
INPUT_FOLDER = "./Input"
OUTPUT_FOLDER = "./Output"
IMAGE_FOLDER = "./images"
COMPLETED_FOLDER = "./Completed"