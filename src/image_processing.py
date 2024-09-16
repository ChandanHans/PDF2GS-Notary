import subprocess
import time
import requests
import platform
import pytesseract
from openai import OpenAI
from bs4 import BeautifulSoup
from functools import lru_cache
from unidecode import unidecode

from .annuaire_data import get_annuaire_data
from .constants import *
from .utils import *

# image_processing.py

import os
import time
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from .drive_upload import upload_to_drive
from .constants import IMAGE_FOLDER, SHEET_ID, FOLDER_ID1


def clean_name_for_comparison(name):
    """Clean the name by removing spaces, commas, and dashes."""
    return name.replace(" ", "").replace(",", "").replace("-", "").lower()

def upload_image_and_append_sheet(name, image_path, drive_service, sheets_service, existing_entries=None):
    """
    Upload the image to Google Drive and append its name and link to a Google Sheet.
    
    If the image already exists in the sheet, skip upload and append.
    """
    # Clean the name for comparison
    cleaned_name = clean_name_for_comparison(name)
    
    # Check if the image already exists in the sheet
    if existing_entries is None:
        existing_entries = []  # Ensure there's an empty list if no data is passed
    if any(cleaned_name in clean_name_for_comparison(entry[0]) for entry in existing_entries):
        print(f"Image '{name}.png' already exists in the sheet. Skipping upload.")
        return

    # Upload the image to the folder
    file_metadata = {
        'name': f"Acte de décès - {name}.png",
        'parents': [FOLDER_ID1]
    }
    media = MediaFileUpload(image_path, mimetype='image/png')
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()

    # Get the file ID and web link
    file_link = uploaded_file.get('webViewLink')

    # Append the image name and link to the Google Sheet
    row_data = [[f"Acte de décès - {name}.png", file_link]]
    sheets_service.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range="Sheet1!A:B",
        valueInputOption="RAW",
        body={"values": row_data}
    ).execute()



def get_existing_image_names(sheets_service, sheet_id):
    """
    Retrieve and cache the existing image names from the Google Sheet.
    This function is called once to avoid multiple requests to the sheet.
    """
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range='Sheet1!A:A'  # Assuming the image names are in column A
    ).execute()
    return result.get('values', [])

openai_client = OpenAI(api_key=GPT_KEY)


def get_image_result(image_path):
    text = pytesseract.image_to_string(image_path, lang="fra")
    prompt = (
        text
        + """


    Please filter unnecessary characters like (*,#)
    if not found then ""
    json
    {
        "dead person full name": "" (You can get it right at the beginning),
        "Acte de notorieti": (date only) (dd/mm/yyyy),
        "certificate notary name": (after Acte de notorieti) (don't include Maitre) (only name)
    }
    """
    )
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                ],
            }
        ],
        response_format={"type": "json_object"},
        max_tokens=300,
    )
    result = eval(response.choices[0].message.content)
    return result

def get_contact_from_sheet(name: str):
    annuaire_data = get_annuaire_data()
    for row in annuaire_data:
        if row[0] == unidecode(name).replace(" ","").replace("-", "").lower():
            return row[1], row[2]
    return None, None

def get_contact_from_web(name: str):
    url = f"https://www.notaires.fr/en/directory/notaries?name={name}"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    phone = email = None

    notary_page_element = soup.find("a", class_="arrow-link")
    if notary_page_element:
        notary_page_href = notary_page_element["href"]
        notary_page_link = "https://www.notaires.fr" + notary_page_href

        response = requests.get(notary_page_link)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        if response:
            phone_element = soup.find(
                "div", class_="office-sheet__phone field--telephone"
            )
            if phone_element:
                phone = phone_element.text

            email_button = soup.find(
                "a", class_="btn-sheet btn-size--size-m btn-sheet--mail"
            )
            if email_button:
                email = email_button["href"]

                
    return phone, email
        
@lru_cache(maxsize=None)
def get_contact(name):
    try:
        phone,email = get_contact_from_sheet(name)
        # if not email:
        #     phone,email = get_contact_from_web(name)
        return phone, email
    except requests.RequestException as e:
        print()
        print(e)
        raise Exception("No Network Connection")

def process_image(image, drive_service, sheets_service, existing_images_names):
    result = None
    try:
        t = time.time()
        notary = don = None
        image_path = f"{IMAGE_FOLDER}/{image}"
        image_result : dict[str,str] = get_image_result(image_path)
        name, don, notary = image_result.values()
        if notary:
            while True:
                try:
                    phone, email = get_contact(notary)
                    break
                except Exception as e:
                    print()
                    print(e)
                    input("\n\nPress Enter To Continue :")
                    time.sleep(1)
        else:
            phone = email = notary = None

        print(f"     {image} in {int(time.time()-t)} sec", end="\r")
        
        upload_image_and_append_sheet(name, image_path, drive_service, sheets_service, existing_images_names)
        result = [
            name,
            don,
            notary,
            phone,
            email,
            None,
        ]
    except Exception as e:
        print(e)

    return result


def check_for_tesseract():
    os_name = platform.system()
    if os_name == "Windows":
        if os.path.exists("C:/Program Files/Tesseract-OCR"):
            tesseract_path = "C:/Program Files/Tesseract-OCR/tesseract.exe"
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            if "fra" in pytesseract.get_languages():
                return
        else:
            pass
        print("!! tesseract is not installed !!")
        print(
            "Download and install tesseract : https://github.com/UB-Mannheim/tesseract/wiki"
        )
        print("Select French language during installation")
        input()
        sys.exit()
    else:
        try:
            result = subprocess.run(
                ["tesseract", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode == 0:
                if "fra" in pytesseract.get_languages():
                    return
        except FileNotFoundError:
            pass
        print("!! tesseract-fra is not installed !!")
        print('Install tesseract-fra with this command : "brew install tesseract-fra"')
        input()
        sys.exit()
