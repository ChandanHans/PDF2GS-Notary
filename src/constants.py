import json
import os
from dotenv import load_dotenv

from .utils import resource_path


load_dotenv(dotenv_path=resource_path(".env"))


GPT_KEY = os.environ["GPT_KEY"]
CREDS_JSON = json.loads(os.environ["CREDS_JSON"])
ANNUAIRE_SHEET_KEY = "1NBWDbmuXHKr6yWsEvxJhio4uaUPKol6_dJvtgKJCDhc"
FOLDER_ID1 = '16r80-Mq5jDo6Lj9svu0hD7ULYMyyUnHp'
FOLDER_ID2 = '13wqi6NK5E_gvXgnTyry-WaQLh6C6Mf97'
IMAGE_SHEET_ID = '1e4GzXCftJYFRbh3xKWnvRK8zE-FjOUut7FinhFj-2ug'
INPUT_FOLDER = "./Input"
OUTPUT_FOLDER = "./Output"
IMAGE_FOLDER = "./images"
COMPLETED_FOLDER = "./Completed"
TOKEN_FILE = 'token.pickle'