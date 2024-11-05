import os
import time
import requests
import platform
import subprocess
import pytesseract
from openai import OpenAI
from bs4 import BeautifulSoup
from unidecode import unidecode
from googleapiclient.http import MediaFileUpload

from .annuaire_data import get_annuaire_data
from .constants import *
from .utils import *

# image_processing.py


def clean_name_for_comparison(name: str):
    """Clean the name by removing spaces, commas, and dashes."""
    return name.replace(" ", "").replace(",", "").replace("-", "").lower()


def upload_image_and_append_sheet(
    name, image_path, drive_service, sheets_service, existing_images=None
):
    """
    Upload the image to Google Drive and append its name and link to a Google Sheet.

    If the image already exists in the sheet, skip upload and append.
    """
    # Clean the name for comparison
    cleaned_name = clean_name_for_comparison(name)

    # Check if the image already exists in the sheet
    if existing_images is None:
        existing_images = []  # Ensure there's an empty list if no data is passed
    for image in existing_images:
        if cleaned_name in clean_name_for_comparison(image[0]):
            print(f"Image '{name}.png' already exists in the sheet. Skipping upload.")
            return image[1]

    # Upload the image to the folder
    file_name = f"Acte de décès - {name}.png"
    file_metadata = {"name": file_name, "parents": [FOLDER_ID1]}
    media = MediaFileUpload(image_path, mimetype="image/png")
    request = drive_service.files().create(body=file_metadata, media_body=media, fields="id, webViewLink")
    uploaded_file = execute_with_retry(request)
    # Get the file ID and web link
    file_link = uploaded_file.get("webViewLink")

    # Append the image name and link to the Google Sheet
    row_data = [file_name, file_link]
    request = sheets_service.spreadsheets().values().append(
        spreadsheetId=IMAGE_SHEET_ID,
        range="Sheet1!A:B",
        valueInputOption="RAW",
        body={"values": [row_data]},
    )
    execute_with_retry(request)
    return file_link


def get_existing_image_names(sheets_service, sheet_id):
    """
    Retrieve and cache the existing image names from the Google Sheet.
    This function is called once to avoid multiple requests to the sheet.
    """
    request = sheets_service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="Sheet1!A:B", 
        )
    result = execute_with_retry(request)
    return result.get("values", [])


openai_client = OpenAI(api_key=GPT_KEY)


def get_image_result(image_path):
    text = pytesseract.image_to_string(image_path, lang="fra")
    prompt = (
        "Text:\n"
        + text
        + """


1. Filter unnecessary characters like (*, #, ~, etc.)
2. case sensitive so Don't change any case because I Identify fname and lname with case.
3. If you think this is not the full text from a death certificate then ""
4. Ensure the following:
    - If any of the fields are not present, leave them as an empty string ("").
    - Return the result in the exact JSON format.

Please format the output as a JSON object, following this structure exactly:
{
    "Dead person full name": "" (You can get it right at the beginning),
    "Acte de notorieti": "" (date only) (format dd/mm/yyyy),
    "Certificate notary name": "" (Name of the notary mentioned after "Acte de notorieti") (omit the title "Maitre" and only include the name).
}
""")
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
        response_format={"type": "json_object"},
        max_tokens=300,
    )
    result = eval(response.choices[0].message.content)
    return result


def get_contact(name: str):
    annuaire_data = get_annuaire_data()
    for row in annuaire_data:
        if row[0] == unidecode(name).replace(" ", "").replace("-", "").lower():
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


def process_image(image, drive_service, sheets_service, existing_images_names):
    result = None
    try:
        t = time.time()
        notary = don = None
        image_path = f"{IMAGE_FOLDER}/{image}"
        image_result: dict[str, str] = get_image_result(image_path)
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

        file_link = upload_image_and_append_sheet(
            name, image_path, drive_service, sheets_service, existing_images_names
        )
        result = [name, don, notary, phone, email, "à envoyer", file_link]
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
