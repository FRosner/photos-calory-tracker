import base64
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from googleapiclient import discovery
import os
import pickle
import openai
import requests
import yaml
from openai import OpenAI
from pydantic import BaseModel


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


def encode_image(image):
    return base64.b64encode(image).decode('utf-8')


class FoodAnalysis(BaseModel):
    readable_name: str
    protein_g: int
    fat_g: int
    carbohydrate_g: int
    fibre_g: int
    total_mass_g: int
    total_kcal: int
    total_health_score: int
    processing_degree: str
    components: list[str]


class FoodAnalysisResponse(BaseModel):
    foods: list[FoodAnalysis]


def analyze_images(images):
    client = OpenAI()

    image_messages = []
    for image in images:
        encoded_image = encode_image(image)
        image_messages.append({
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded_image}"
                    }
                }
            ]
        })

    try:
        response = client.beta.chat.completions.parse(
            messages=[
                {
                    "role": "system",
                    "content": "You are a nutrition and health expert. You are helping a user understand the nutritional value of their food to help them eat healthier. "
                               "For each image, estimate the protein, fat, fibre, and carbohydrate content in grams, the total mass in grams, the total calories, "
                               "the total health score (1-10, 10 being super healthy, 1 being heart-attack-unhealthy), the processing degree ('low', 'medium', 'high'), "
                               "and the components that are in the dish. If you are unsure, please provide an estimate. Only refuse the query if the image does not contain any food."
                               "Please also provide a readable name of the dish. If this looks like a well-known dish, you can use that name. Otherwise,"
                               " you can describe it in a few words that are helpful to understand the dish."
                },
                *image_messages,
            ],
            model="gpt-4o-mini",
            response_format=FoodAnalysisResponse,
        )

        food_analysis = response.choices[0].message
        if food_analysis.parsed:
            return food_analysis.parsed
        elif food_analysis.refusal:
            print(food_analysis.refusal)
            return None
    except Exception as e:
        if type(e) == openai.LengthFinishReasonError:
            print("Too many tokens: ", e)
            return None
        else:
            print(e)
            return None


def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to download image. Status code: {response.status_code}")


def main():
    creds = google_authenticate()
    photos_api = discovery.build("photoslibrary", "v1", credentials=creds, static_discovery=False)

    date = parse_date_string(DATE_STRING)
    date_filter = {'year': date.year, 'month': date.month, 'day': date.day}

    print(f"Searching photos matching '{SEARCH_TERM}' on '{date_filter}'")
    photos = google_search_photos(photos_api, search_term=SEARCH_TERM, date_filter=date_filter)
    if not photos:
        print('No media items found.')
    else:
        images = []
        for image in photos:
            image_url = image['baseUrl']
            print(f"Downloading {image['filename']} ({image.get('mediaMetadata', {}).get('creationTime')})")
            images.append(download_image(image_url))
        analysis = analyze_images(images)
        if analysis:
            print(yaml.dump(analysis.dict()))



if __name__ == '__main__':
    main()
