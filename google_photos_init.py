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


def main():
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=AUTH_PORT, access_type='offline', include_granted_scopes='true')
    with open(TOKEN_PICKLE_FILE, 'wb') as token:
        pickle.dump(creds, token)


if __name__ == '__main__':
    main()
