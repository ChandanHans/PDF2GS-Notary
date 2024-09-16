# annuaire_data.py

from functools import lru_cache
import pickle
import gspread
from google.oauth2 import service_account
from unidecode import unidecode
import pandas as pd
from src.constants import *
from src.utils import *

def get_uploaded_pdfs(name, drive_service, folder_id=None):
    """
    Retrieve the list of PDF file names from Google Drive that contain the given name.
    
    Parameters:
    name (str): The name to search for in the file names.
    drive_service (Resource): The Google Drive service object.
    folder_id (str): Optional, the ID of the folder to search in. If None, searches all files.

    Returns:
    List[str]: A list of matching PDF file names.
    """
    query = f"mimeType = 'application/pdf' and trashed = false and name contains '{name}'"
    
    if folder_id:
        query += f" and '{folder_id}' in parents"
    
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    # Return a list of file names
    return [file['name'] for file in files]

@lru_cache(maxsize=None)
def get_annuaire_data():
    with open(TOKEN_FILE, 'rb') as token:
        credentials = pickle.load(token)
    gc = gspread.authorize(credentials)
    annuraie_sheet = gc.open_by_key(ANNUAIRE_SHEET_KEY)
    annuraie_worksheet = annuraie_sheet.get_worksheet_by_id(0)
    
    sheet_data = annuraie_worksheet.get_values()
    header = sheet_data[0]
    rows = sheet_data[1:]
    result = []
    df = pd.DataFrame(rows, columns=header)
    
    for _, row in df.iterrows():
        full_name = unidecode(row["First Name"] + row["Last Name"]).replace(" ", "").replace("-", "").lower()
        result.append((full_name, row["Phone"], str(row["Email"]).strip()))
    
    return result