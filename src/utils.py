import os
import sys
from dotenv import load_dotenv


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def extract_number(filename):
    return int(filename.split("-")[1].split(".")[0])

load_dotenv(dotenv_path=resource_path("../.env"))


OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
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
