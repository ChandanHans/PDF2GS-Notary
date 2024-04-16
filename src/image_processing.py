import json
import time
import base64
import requests
import pytesseract
from openai import OpenAI,Completion
from bs4 import BeautifulSoup
from functools import lru_cache

from .utils import *

if os.path.exists('Tesseract-OCR/tesseract.exe'):           
    tesseract_path = 'Tesseract-OCR/tesseract.exe'
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

client = OpenAI(api_key = OPENAI_API_KEY)

def get_image_result(image_path):
    text = pytesseract.image_to_string(image_path, lang="fra")
    prompt = text + """


    Please filter unnecessary characters like (*,#)
    if not found then ""
    json
    {
        "person full name": "" (You can get it right at the beginning),
        "declarant name": "",
        "Acte de notorieti": (date only),
        "certificate notary name": (after Acte de notorieti) (only name, don't include mr. or mrs.),
        "address": "",
    }
    """
    response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
        ],
        }
    ],
    response_format={ "type": "json_object" },
    max_tokens=300,
    )
    cost = (response.usage.prompt_tokens/1000) * 0.0005 + (response.usage.completion_tokens/1000) * 0.0015
    result = eval(response.choices[0].message.content)
        
    return result, cost

@lru_cache(maxsize=None)
def get_contact(name):
    try:
        url = f'https://www.notaires.fr/en/directory/notaries?name={name}'
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        phone = email = website = "Not Found"
        
        notary_page_element = soup.find('a', class_='arrow-link')
        if notary_page_element:
            notary_page_href = notary_page_element['href']
            notary_page_link = "https://www.notaires.fr" + notary_page_href
            
            response = requests.get(notary_page_link)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if response:            
                phone_element = soup.find('div', class_='office-sheet__phone field--telephone')
                if phone_element:
                    phone = phone_element.text
                    
                email_button = soup.find('a', class_='btn-sheet btn-size--size-m btn-sheet--mail')
                if email_button:
                    email = email_button["href"]
                
                website_element = soup.find('div', class_='office-sheet__url field--link')
                if website_element:
                    website = website_element.text
                        
        return phone, email, website
    except requests.RequestException:
        print()
        raise Exception("No Network Connection")


def process_image(image):
    result = ["","","","","","","","","","",None]
    cost = 0
    try:
        t = time.time()
        notary = don = address = None
        image_path = f"{IMAGE_FOLDER}/{image}"
        image_result, cost = get_image_result(image_path)
        name, declarant, don, notary, address = image_result.values()
        if notary:
            while True:
                try:
                    phone, email, website = get_contact(notary)
                except Exception as e:
                    print()
                    print(e)
                    input("\n\nPress Enter To Continue :")
                    time.sleep(1)
        else:
            phone = email = website = ""
            notary = "Not Found"
                
        
        print(f"     {image} in {int(time.time()-t)} sec",end="\r")
        result = [name, "-", "-", declarant, don, notary, address, phone, email, website,None]
    except Exception as e:
        print(e)
        
    return result, cost
