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

