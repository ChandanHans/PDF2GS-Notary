from functools import lru_cache
import gspread
from google.oauth2 import service_account
from unidecode import unidecode
import pandas as pd

from .utils import *





def get_annuaire_sheet_data():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = service_account.Credentials.from_service_account_info(
        CREDS_JSON, scopes=scopes
    )
    gc = gspread.authorize(credentials)
    annuraie_sheet = gc.open_by_key(ANNUAIRE_SHEET_KEY)
    annuraie_worksheet = annuraie_sheet.get_worksheet_by_id(0)
    
    return annuraie_worksheet.get_values()
    
    
@lru_cache(maxsize=None)
def get_annuaire_data():
    sheet_data = get_annuaire_sheet_data()
    header = sheet_data[1]
    rows = sheet_data[2:]
    result = []
    df = pd.DataFrame(rows, columns=header)
    for _, row in df.iterrows():
        full_name = unidecode(row["First Name"]+row["Last Name"]).replace(" ","").lower()
        result.append((full_name,row["Phone"],str(row["Email"]).strip()))
    return result