import json
import os
import sys
from dotenv import load_dotenv


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(
        sys, "_MEIPASS", os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    )
    return os.path.join(base_path, relative_path)


def extract_number(filename: str):
    return int(filename.split("-")[1].split(".")[0])


load_dotenv(dotenv_path=resource_path(".env"))


GPT_KEY = os.environ["GPT_KEY"]
CREDS_JSON = json.loads(os.environ["CREDS_JSON"])
ANNUAIRE_SHEET_KEY = "1NBWDbmuXHKr6yWsEvxJhio4uaUPKol6_dJvtgKJCDhc"
INPUT_FOLDER = "./Input"
OUTPUT_FOLDER = "./Output"
IMAGE_FOLDER = "./images"
COMPLETED_FOLDER = "./Completed"


if not os.path.exists(INPUT_FOLDER):
    os.makedirs(INPUT_FOLDER)
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)
if not os.path.exists(COMPLETED_FOLDER):
    os.makedirs(COMPLETED_FOLDER)
