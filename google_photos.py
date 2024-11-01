from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient import discovery
import os
import pickle


# Scopes required to access the Google Photos Library API
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']

CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", ".secrets/client_secret.json")
AUTH_PORT = int(os.getenv("GOOGLE_AUTH_PORT", "8080"))
TOKEN_PICKLE_FILE = os.getenv("GOOGLE_TOKEN_PICKLE_FILE", ".secrets/token.pickle")


def authenticate():
    creds = None
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise ValueError("Invalid credentials. Please run google_photos_init.py to authenticate.")

    return creds


def search_photos(service, search_term=None, start_date=None, end_date=None):
    """Search photos in Google Photos library based on search term or date range."""
    search_body = {
        "pageSize": 50,
        "filters": {}
    }

    # Add date filters if specified
    if start_date or end_date:
        date_filters = {}
        if start_date:
            date_filters['startDate'] = start_date
        if end_date:
            date_filters['endDate'] = end_date
        search_body["filters"] = {"dateFilter": {"ranges": [date_filters]}}

    # Add search term if specified
    if search_term:
        search_body["filters"]["contentFilter"] = {"includedContentCategories": [search_term]}

    # Execute the search
    results = service.mediaItems().search(body=search_body).execute()
    items = results.get('mediaItems', [])

    if not items:
        print('No media items found.')
    else:
        for item in items:
            print(f"Filename: {item['filename']}, URL: {item['baseUrl']}")

def main():
    creds = authenticate()
    photos_api = discovery.build("photoslibrary", "v1", credentials=creds, static_discovery=False)

    search_photos(photos_api, search_term='food', start_date={'year': 2024, 'month': 7, 'day': 1}, end_date={'year': 2024, 'month': 8, 'day': 10})


if __name__ == '__main__':
    main()
