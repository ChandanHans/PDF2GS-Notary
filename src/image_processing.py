from functools import lru_cache
import json
import time
from PIL import Image
from bs4 import BeautifulSoup
import requests
import google.generativeai as genai

from .utils import *

genai.configure(api_key = API_KEY)
model = genai.GenerativeModel('gemini-pro-vision')

def get_image_result(image_path):
    img = Image.open(image_path)
    prompt="""
    return a json
    if not found then ""
    {
        "person_full_name": ""
        "declarant_name": ""
        "certificate_notary_name": "" (only name. don't include mr. or mrs.)
        "date_of_notary": "" (use french date only)
        "address": ""
    }
    """

    response = model.generate_content([prompt,img], stream=True)
    response.resolve()
    try:
        result = dict(json.loads("{"+ response.text.split("{")[1].split("}")[0]+"}"))
    except:
        print(response.text)
        return {}
    return result

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
    try:
        t = time.time()
        notary = don = address = None
        image_path = f"{IMAGE_FOLDER}/{image}"
        result = get_image_result(image_path)
        name, declarant, notary, don, address = result.values()
        if notary:
            while True:
                try:
                    phone, email, website = get_contact(notary)
                    break
                except Exception as e:
                    print()
                    print(e)
                    input("\n\nPress Enter To Continue :")
                    time.sleep(5)
        else:
            phone = email = website = ""
            notary = "Not Found"
                
        
        print(f"     {image} in {int(time.time()-t)} sec",end="\r")
        return [name, "-", "-", declarant, don, notary, address, phone, email, website,None]
    except Exception as e:
        print(e)
        return ["","","","","","","","","","",None]