# drive_upload.py

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
import requests

from .constants import CREDS_JSON, TOKEN_FILE

SCOPES = ['https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/userinfo.profile',
          "https://www.googleapis.com/auth/spreadsheets"]

def get_user_profile(creds):
    """Retrieve the user's profile information including their name."""
    profile_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    headers = {'Authorization': f'Bearer {creds.token}'}
    response = requests.get(profile_info_url, headers=headers)
    
    if response.status_code == 200:
        user_info = response.json()
        user_name = user_info.get('name', 'Unknown')
        return user_name
    else:
        return 'Unknown'

def authenticate_google_drive():
    """Authenticate and return the Google Drive service instance."""
    creds = None

    while True:
        # Load token from file if it exists
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        # Check if the credentials are valid
        if creds and creds.valid:
            # Get the current user email from the creds
            current_user = get_user_profile(creds)
            print(f"Current logged-in user: {current_user}")
            
            # Ask the user if they want to use the current account or log in with a different one
            choice = input("Do you want to use the current account? (y/n): ").strip().lower()
            
            if choice != 'n':
                return creds  # Return the current credentials if the user chooses "current"
            else:
                print("Logging in with a different account...")
        
        # If the credentials are expired or the user chooses a different account, log in again
        if not creds or not creds.valid or choice == 'n':
            if creds and creds.expired and creds.refresh_token:
                # Try to refresh the credentials
                creds.refresh(Request())
            else:
                # Run OAuth flow to get new credentials
                flow = InstalledAppFlow.from_client_config(CREDS_JSON, SCOPES)
                creds = flow.run_local_server()

            # Save the new credentials to the token file
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)

        # Check if the creds are valid before breaking the loop
        if creds and creds.valid:
            break

    return creds

def upload_to_drive(service, file_path, folder_id):
    """Upload a file to Google Drive."""
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = uploaded_file.get('id')
    return file_id


def delete_file_from_drive(service, file_id):
    """Delete a file from Google Drive by its file ID."""
    service.files().delete(fileId=file_id).execute()
    print(f"Deleted file with ID {file_id} from Google Drive")


def convert_excel_to_google_sheet(service, file_id):
    """Convert an uploaded Excel file to a Google Sheet."""
    file_metadata = {
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    converted_file = service.files().copy(fileId=file_id, body=file_metadata, fields='id, webViewLink').execute()
    print(f"Excel file converted to Google Sheet with file ID {converted_file.get('id')}")
    return converted_file.get('id'), converted_file.get('webViewLink')