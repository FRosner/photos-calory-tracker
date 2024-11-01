from datetime import datetime, timedelta

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
DATE_STRING = os.getenv("GOOGLE_PHOTOS_DATE")  # yyyy-mm-dd
SEARCH_TERM = os.getenv("GOOGLE_PHOTOS_SEARCH_TERM", "food")


def parse_date_string(date_string):
    if date_string:
        return datetime.strptime(date_string, "%Y-%m-%d")
    else:
        return datetime.now() - timedelta(days=1)


def google_authenticate():
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


def google_search_photos(service, search_term=None, date_filter=None):
    """
    Search photos in Google Photos library based on search term and date.

    Date filter is of the form (https://developers.google.com/photos/library/reference/rest/v1/mediaItems/search#date):

    {
      "year": integer,
      "month": integer,
      "day": integer
    }

    Unfortunately, this API is getting removed on March 31, 2025. After that,
    apps can only access Photos that they have created or that the user picks.
    See https://developers.google.com/photos/support/updates.
    """
    filters = {}
    if date_filter:
        filters["dateFilter"] = {"dates": [date_filter]}
    if search_term:
        filters["contentFilter"] = {"includedContentCategories": [search_term]}

    search_body = {
        "pageSize": 50,
        "filters": filters,
    }

    results = service.mediaItems().search(body=search_body).execute()
    return results.get('mediaItems', [])


def main():
    creds = google_authenticate()
    photos_api = discovery.build("photoslibrary", "v1", credentials=creds, static_discovery=False)

    date = parse_date_string(DATE_STRING)
    date_filter = {'year': date.year, 'month': date.month, 'day': date.day}

    print(f"Searching photos matching {SEARCH_TERM} on {date_filter}")
    photos = google_search_photos(photos_api, search_term=SEARCH_TERM, date_filter=date_filter)
    if not photos:
        print('No media items found.')
    else:
        for item in photos:
            print(f"Filename: {item['filename']}")


if __name__ == '__main__':
    main()
