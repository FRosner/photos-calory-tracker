# Google Photos Calory Tracker

## Description

Just some pet project to track my calories based on pictures from my Google Photos.

## Setup

* Configure your app on the [Google API Console](https://developers.google.com/photos/overview/configure-your-app) to use the Google Photos Library API. Make sure to add the `/auth/photoslibrary.readonly` scope.
* Create credentials for a Web Application. Add `https://localhost:8080/` as an authorized redirect URI.
* Download the `credentials.json` file and place it under `.secrets` in this project. By default, the script will load `client_secret.json`. You can override this by setting the `GOOGLE_CREDENTIALS_FILE` environment variable.
* Go to [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent) and add your email as a test user.
* Run `poetry run python google_photos_init.py` and allow the app to access your Google Photos. If successful, you should see the following message in your Browser: "The authentication flow has completed. You may close this window."
* Now, there's a `token.pickle` file in the `.secrets` folder. This file is used to authenticate the app in the future.
* Create a new API Key for the [OpenAI Platform](https://platform.openai.com/) and store it (or pass it) via the `OPENAI_API_KEY` environment variable.

## Usage

To analyze all your food photos from yesterday, run:

```bash
poetry run python main.py
```

## Validation

To run validation against the validation dataset, run:

```bash
poetry run python validate.py
```
